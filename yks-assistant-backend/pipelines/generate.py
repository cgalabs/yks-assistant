import json
from schemas_contracts.models import GenerateV1, SolveV1
from contract_guard import run_with_contract_guard
from ingest import generate_request_id
from pipelines.solve import solve_step, ExtractV1
from config import GENERATE_API_KEY, GENERATE_MODEL_ID
from logic.anchor_selector import get_random_anchors, format_anchors_for_prompt

# ------------------------------------------------------------------------
# PROMPTS
# ------------------------------------------------------------------------

GENERATOR_SYSTEM_PROMPT = """Sen YKS TYT Matematik sınavı için özgün sorular üreten uzman bir eğitim asistanısın.

Görevin:
1. Verilen örnek sorulara BENZER ama FARKLI yeni bir soru üretmek
2. Sorunun TYT seviyesine uygun olması
3. Şıkların mantıklı ve çeldirici olması
4. Çözümün adım adım ve anlaşılır olması

KURALLAR:
- Örnek soruları KOPYALAMA, sadece stilinden ve zorluğundan ilham al
- Şıklar A, B, C, D, E olmalı
- Sadece bir doğru cevap olmalı
- Matematiksel ifadeler için LaTeX kullan (\\frac{a}{b}, x^2, \\sqrt{x} vb.)

JSON formatında 'questions' listesi içinde cevap ver:
{
  "questions": [
    {
        "problem_text": "Soru metni",
        "answer_choices": {"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."},
        "solution": "Adım adım çözüm",
        "correct_answer": "A/B/C/D/E",
        "topic": "Konu adı"
    }
  ]
}"""

# ------------------------------------------------------------------------
# PIPELINE STEPS
# ------------------------------------------------------------------------

async def generate_step(topic: str, difficulty: str, request_id: str) -> GenerateV1:
    # 1. Get anchors
    anchors = get_random_anchors(topic, k=3)
    anchors_text = format_anchors_for_prompt(anchors)
    
    # 2. Build prompt
    prompt = f"{GENERATOR_SYSTEM_PROMPT}\n\nKonu: {topic}\n\nÖrnek Sorular:\n{anchors_text}\n\nŞimdi yukarıdaki örneklere benzer yeni ve özgün bir TYT matematik sorusu üret. JSON formatında cevap ver."
    
    return await run_with_contract_guard(
        prompt=prompt,
        api_key=GENERATE_API_KEY,
        output_model=GenerateV1,
        pipeline_name="generate",
        model_name="gpt_oss_120b",
        request_id=request_id,
        model=GENERATE_MODEL_ID
    )

async def validate_question(question_item, request_id: str) -> bool:
    """
    Validates a generated question by trying to solve it with the Solver.
    Returns True if Solver matches the Generator's answer.
    """
    try:
        # Mock an ExtractV1 object from the generated question
        mock_extract = ExtractV1(
            question_text=question_item.problem_text,
            choices=question_item.choices,
            language="tr"
        )
        
        # Call Solver
        solve_result = await solve_step(mock_extract, request_id)
        
        # Check agreement
        is_valid = solve_result.final_answer == question_item.correct_answer
        print(f"[VALIDATOR] req_id={request_id} expected={question_item.correct_answer} got={solve_result.final_answer} match={is_valid}")
        return is_valid
        
    except Exception as e:
        print(f"[VALIDATOR ERROR] {e}")
        return False

# ------------------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------------------

async def generate_pipeline(topic: str, difficulty: str) -> dict:
    req_id = generate_request_id()
    
    # Simple retry loop for generation/validation (max 1 retry per user spec)
    max_pipeline_retries = 1
    attempts = 0
    
    while attempts <= max_pipeline_retries:
        try:
            # 1. Generate
            gen_result = await generate_step(topic, difficulty, req_id)
            
            # 2. Validate (Check the first question as a heuristic)
            if not gen_result.questions:
                 attempts += 1
                 continue

            first_q = gen_result.questions[0]
            if await validate_question(first_q, req_id):
                 return {
                    "req_id": req_id,
                    "status": "success",
                    "data": gen_result.model_dump()
                }
            else:
                 print(f"[WARN] Validation failed for attempt {attempts}")
                 
        except Exception as e:
            print(f"[ERROR] Generate attempt {attempts} failed: {e}")
            
        attempts += 1
        
    return {
        "req_id": req_id,
        "status": "error",
        "message": "Soru üretilemedi veya doğrulama başarısız oldu."
    }
