import base64
import json
from schemas_contracts.models import ExtractV1, SolveV1
from contract_guard import run_with_contract_guard
from ingest import generate_request_id
from config import SOLVE_API_KEY, TOGETHER_API_KEY, EXTRACT_API_KEY, EXTRACT_MODEL_ID

# ------------------------------------------------------------------------
# PROMPTS
# ------------------------------------------------------------------------

VLM_SYSTEM_PROMPT = """
You are a VLM Extractor. Your job is to extract the question, choices, and relevant details from the image into a structured JSON format.
Return ONLY valid JSON matching this exact structure:
{
  "schema": "extract_v1",
  "id": "q_001",
  "question_text": "...",
  "choices": {
    "A": "...",
    "B": "...",
    "C": "...",
    "D": "...",
    "E": "..."
  },
  "figures_desc": "Varsa şekil / grafik / tablo açıklaması",
  "topic_hint": "opsiyonel",
  "constraints": ["opsiyonel"]
}
"""

SOLVER_SYSTEM_PROMPT = """
You are a master Math/Science Solver for TYT/AYT exams.
Given a structured question JSON, solve it step-by-step.

CRITICAL RULES:
1. MAXIMUM 15 STEPS. If the solution is longer, summarize.
2. Be concise and direct. Do not repeat steps.
3. If you find yourself in a loop, STOP and choose the most logical answer immediately.

Return ONLY valid JSON matching this schema:
{
  "steps": ["step 1", "step 2", ...],
  "final_answer": "A" (or B, C, D, E),
  "reasoning_checks": ["check 1", ...],
  "common_traps": ["trap 1", ...],
  "confidence": 0.95
}
"""

# ------------------------------------------------------------------------
# PIPELINE STEPS
# ------------------------------------------------------------------------

async def extract_step(image_bytes: bytes, request_id: str) -> ExtractV1:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    
    return await run_with_contract_guard(
        prompt=VLM_SYSTEM_PROMPT,
        api_key=EXTRACT_API_KEY,
        image_b64=image_b64,
        output_model=ExtractV1,
        pipeline_name="solve",
        model_name="qwen3_thinking_v1",
        request_id=request_id,
        model=EXTRACT_MODEL_ID
    )

async def solve_step(extract_data: ExtractV1, request_id: str) -> SolveV1:
    # Serialize extraction result to text for the solver
    problem_str = json.dumps(extract_data.model_dump(), ensure_ascii=False, indent=2)
    prompt = f"{SOLVER_SYSTEM_PROMPT}\n\nProblem Data:\n{problem_str}"
    
    return await run_with_contract_guard(
        prompt=prompt,
        api_key=TOGETHER_API_KEY, # Using Together API Key
        output_model=SolveV1,
        pipeline_name="solve",
        model_name="together_solver_v1",
        request_id=request_id,
        use_together=True # Routing to Together AI
    )

# ------------------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------------------

async def solve_pipeline(image_bytes: bytes) -> dict:
    req_id = generate_request_id()
    
    try:
        # 1. Extract
        extract_result = await extract_step(image_bytes, req_id)
        
        # 2. Solve
        solve_result = await solve_step(extract_result, req_id)
        
        # 3. Format Response (UI Ready)
        return {
            "req_id": req_id,
            "status": "success",
            "extracted": extract_result.model_dump(),
            "solution": solve_result.model_dump()
        }
        
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}")
        return {
            "req_id": req_id,
            "status": "error",
            "message": "Soruyu çözerken bir sorun oluştu. Lütfen tekrar deneyin."
        }
