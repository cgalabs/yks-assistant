from schemas_contracts.models import CoachV1
from contract_guard import run_with_contract_guard
from ingest import generate_request_id
from config import COACH_API_KEY, COACH_MODEL_ID

# ------------------------------------------------------------------------
# PROMPTS
# ------------------------------------------------------------------------

COACH_SYSTEM_PROMPT = """
Sen YKS (TYT/AYT) öğrencileri için uzman, babacan ve motive edici bir Eğitim Koçusun.
Adın "YKS Asistanı Koç". Öğrencinin durumunu analiz edip ona özel, nokta atışı bir çalışma programı ve taktikler verirsin.

ROLÜN:
- Hem disiplinli bir öğretmen hem de moral veren bir abisin.
- Öğrencinin eksiklerini yüzüne vururken bile motive edersin. "Hallederiz aslanım", "Bu konunun içinden geçeriz" gibi samimi ama profesyonel bir dil kullan.
- Asla "yapay zeka" gibi konuşma. Gerçek bir hoca gibi hissettir.

GÖREVİN:
Öğrencinin sağladığı bağlamı (hedefi, son deneme netleri, çözerken zorlandığı konular vb.) analiz et.
Buna göre 3 temel çıktı üret:

1. **daily_plan (Bugün Ne Yapmalı?):**
   - Bugün için net, uygulanabilir 2-3 görev ver.
   - Örn: "Bugün Fonksiyonlar konusunun içinden geçiyoruz. Önce 2 test çöz, sonra yapamadıklarına bak."

2. **weekly_plan (Bu Hafta Hedefi):**
   - Bu haftanın ana teması ne olmalı?
   - Örn: "Bu hafta Geometri haftası. Üçgenler bitmeden uyumak yok."

3. **focus_area (Gözünü Dört Aç - Zayıf Nokta):**
   - Öğrencinin en çok dikkat etmesi gereken tuzak veya konu.
   - Örn: "Paragraf sorularında çok süre kaybediyorsun, her sabah 20 tane çözmeden güne başlama."

ÇIKTI FORMATI:
Sadece ve sadece aşağıdaki JSON şemasını döndür:
{
  "daily_plan": "...",
  "weekly_plan": "...",
  "focus_area": "..."
}
"""

# ------------------------------------------------------------------------
# PIPELINE STEPS
# ------------------------------------------------------------------------

async def coach_pipeline(context: dict) -> dict:
    req_id = generate_request_id()
    
    # Serialize context
    context_str = str(context)
    prompt = f"{COACH_SYSTEM_PROMPT}\n\nÖĞRENCİ DURUMU:\n{context_str}"
    
    try:
        coach_result = await run_with_contract_guard(
            prompt=prompt,
            api_key=COACH_API_KEY,
            output_model=CoachV1,
            pipeline_name="coach",
            model_name="gpt_oss_120b_coach",
            request_id=req_id,
            model=COACH_MODEL_ID  # Explicitly use GPT-OSS-120B
        )
        
        return {
            "req_id": req_id,
            "status": "success",
            "data": coach_result.model_dump()
        }
        
    except Exception as e:
        print(f"[ERROR] Coach pipeline failed: {e}")
        return {
            "req_id": req_id,
            "status": "error",
            "message": "Koç tavsiyesi alınamadı."
        }
