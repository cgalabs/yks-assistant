import base64
import json
from schemas_contracts.models import ExtractV1
from contract_guard import run_with_contract_guard
from ingest import generate_request_id
from config import MEASURE_API_KEY, EXTRACT_API_KEY, EXTRACT_MODEL_ID
from .hakem.standardizer import standardize
from .hakem.osym_similarity import osym_similarity_score

# ------------------------------------------------------------------------
# PROMPTS
# ------------------------------------------------------------------------

MEASURE_SYSTEM_PROMPT = """
Sen uzman bir soru analiz sistemisin. Görevin, verilen bir test sorusu görselini (TYT/AYT/YKS tarzı) analiz etmek ve içerikleri yapılandırılmış JSON formatında çıkarmaktır.

HEDEF JSON FORMATI:
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
  "figures_desc": "Varsa şekil/grafik/tablo açıklaması. Yoksa null veya \"\".",
  "extraction_notes": "Varsa ek notlar.",
  "extraction_confidence": 0.95
}

KURALLAR:
1. "question_text": Soru metnini eksiksiz çıkar. Soru numarasını (1., 2. vb) metnin başına ekleme.
2. "choices": Şık harflerini (A, B...) value kısmına dahil etme. Sadece metni al.
3. "figures_desc": Şekil, grafik veya tablo varsa detaylı betimle (görme engelli biri için anlatır gibi). Şekil yoksa boş bırak.
4. "extraction_confidence": 0.0 ile 1.0 arasında bir güven skoru ver.
5. Sadece ve sadece geçerli JSON döndür. Markdown bloğu (```json) içine alma.
"""

# ------------------------------------------------------------------------
# PIPELINE STEPS
# ------------------------------------------------------------------------

async def extract_step(image_bytes: bytes, request_id: str) -> ExtractV1:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    
    return await run_with_contract_guard(
        prompt=MEASURE_SYSTEM_PROMPT,
        api_key=EXTRACT_API_KEY,
        image_b64=image_b64,
        output_model=ExtractV1,
        pipeline_name="measure",
        model_name="qwen_vl_235b",
        request_id=request_id,
        model=EXTRACT_MODEL_ID
    )

# ------------------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------------------

async def measure_pipeline(image_bytes: bytes) -> dict:
    """
    Orchestrates the Measurement Pipeline.
    1. VLM Extraction (Image -> JSON)
    2. Standardization (JSON -> Standardized)
    3. Similarity Scoring (Standardized -> Score)
    """
    req_id = generate_request_id()
    
    try:
        # 1. Extract
        extract_result = await extract_step(image_bytes, req_id)
        extract_dict = extract_result.model_dump()
        
        # Ensure schema field is present as expected by hakem
        extract_dict["schema"] = "extract_v1"
        if not extract_dict.get("id"):
             extract_dict["id"] = req_id

        # 2. Standardize (Hakem Logic)
        try:
            standardized_data = standardize(extract_dict)
        except Exception as e:
            print(f"[ERROR] Standardization failed: {e}")
            raise ValueError(f"Standardizasyon hatası: {e}")

        # 3. Calculate Similarity (Hakem Logic)
        try:
            score_result = osym_similarity_score(standardized_data)
        except Exception as e:
            print(f"[ERROR] Scoring failed: {e}")
            raise ValueError(f"Skorlama hatası: {e}")
        
        # 4. Format Response
        return {
            "req_id": req_id,
            "status": "success",
            "extraction": extract_dict,
            "standardized": standardized_data,
            "result": score_result
        }
        
    except Exception as e:
        print(f"[ERROR] Measure Pipeline failed: {e}")
        return {
            "req_id": req_id,
            "status": "error",
            "message": f"Ölçüm sırasında bir hata oluştu: {str(e)}"
        }
