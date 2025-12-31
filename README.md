# YKS AI Asistan

# YKS AI Asistan

YKS (TYT/AYT) öğrencileri için geliştirilmiş, yapay zeka destekli soru çözme ve koçluk asistanı. 
**Not:** Modeller şu an için özellikle **TYT Matematik** üzerine özelleştirilmiştir.

## Kurulum

1. **Gereksinimleri Yükleyin**  
   Python backend için gerekli kütüphaneleri indirin:
   ```bash
   cd yks-assistant-backend
   pip install -r requirements.txt
   ```

2. **Ortam Değişkenleri (.env)**  
   `yks-assistant-backend` klasörü içinde `.env` dosyası oluşturun ve API anahtarlarınızı tanımlayın:
   ```env
   SOLVE_API_KEY=...
   GENERATE_API_KEY=...
   # (Diğer anahtarlar...)
   ```

## Çalıştırma

Tüm uygulamayı (Frontend + Backend) tek komutla başlatmak için:

```bash
bash start_app.sh
```

Manuel başlatmak isterseniz:
- **Backend:** `uvicorn main:app --reload` (Port 8000)
- **Frontend:** `npm run dev` (Port 3000)
