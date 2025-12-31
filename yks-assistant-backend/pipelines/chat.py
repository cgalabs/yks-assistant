from schemas_contracts.models import ChatV1
from contract_guard import run_with_contract_guard
from ingest import generate_request_id
from config import SOLVE_API_KEY # Reusing Solve API Key for general chat

CHAT_SYSTEM_PROMPT = """
You are YKS Assistant, an expert tutor for TYT/AYT exams.
Provide helpful, encouraging, and accurate responses to the student's questions.
The student might be asking about a specific problem they just solved or about their study program.
Always respond in Turkish.
Return ONLY valid JSON matching this schema:
{
  "response": "Your detailed response here"
}
"""

async def chat_pipeline(message: str, history: list, context: dict) -> dict:
    req_id = generate_request_id()
    
    # Construct conversation prompt
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    context_str = str(context)
    
    prompt = f"{CHAT_SYSTEM_PROMPT}\n\nContext:\n{context_str}\n\nHistory:\n{history_str}\n\nStudent: {message}"
    
    try:
        chat_result = await run_with_contract_guard(
            prompt=prompt,
            api_key=SOLVE_API_KEY,
            output_model=ChatV1,
            pipeline_name="chat",
            model_name="chat_v1",
            request_id=req_id
        )
        
        return {
            "req_id": req_id,
            "status": "success",
            "data": chat_result.model_dump()
        }
        
    except Exception as e:
        print(f"[ERROR] Chat pipeline failed: {e}")
        return {
            "req_id": req_id,
            "status": "error",
            "message": "Mesajınız iletilemedi. Lütfen tekrar deneyin."
        }
