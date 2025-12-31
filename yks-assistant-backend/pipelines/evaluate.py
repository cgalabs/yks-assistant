from schemas_contracts.models import EvalV1
from contract_guard import run_with_contract_guard
from ingest import generate_request_id
import json
from config import EVALUATE_API_KEY

# ------------------------------------------------------------------------
# PROMPTS
# ------------------------------------------------------------------------

EVAL_SYSTEM_PROMPT = """
You are an independent Evaluator (Judge) for TYT/AYT Math questions.
Evaluate the given question and solution.
Return ONLY valid JSON matching this schema:
{
  "scores": {
    "osym_similarity": 0.0 to 1.0,
    "difficulty": 0.0 to 1.0,
    "kazanim_fit": 0.0 to 1.0 (optional)
  },
  "short_justifications": ["reason 1", "reason 2"]
}
"""

# ------------------------------------------------------------------------
# PIPELINE STEPS
# ------------------------------------------------------------------------

async def evaluate_pipeline(data_to_eval: dict) -> dict:
    req_id = generate_request_id()
    
    data_str = json.dumps(data_to_eval, ensure_ascii=False, indent=2)
    prompt = f"{EVAL_SYSTEM_PROMPT}\n\nContent to Evaluate:\n{data_str}"
    
    try:
        eval_result = await run_with_contract_guard(
            prompt=prompt,
            api_key=EVALUATE_API_KEY,
            output_model=EvalV1,
            pipeline_name="evaluate",
            model_name="evaluator_v1",
            request_id=req_id
        )
        
        return {
            "req_id": req_id,
            "status": "success",
            "data": eval_result.model_dump()
        }
        
    except Exception as e:
        print(f"[ERROR] Evaluate pipeline failed: {e}")
        return {
            "req_id": req_id,
            "status": "error",
            "message": "Değerlendirme yapılamadı."
        }
