#!/bin/bash

# Renkler
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 YKS Asistan Başlatılıyor...${NC}"

# Backend Başlat
echo -e "${GREEN}📦 Backend başlatılıyor (Port 8000)...${NC}"
cd yks-assistant-backend
# Arka planda çalıştırve çıktıyı loga yaz veya ekrana bas
# python3 -m uvicorn main:app --reload --port 8000 &
source venv/bin/activate
# Kullanıcının görebilmesi için screen veya yeni tab açmak zor, 
# bu yüzden arka plana atıp PID'leri tutuyoruz.
python3 -m uvicorn main:app --reload --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Frontend Başlat
echo -e "${GREEN}💻 Frontend başlatılıyor (Port 3000)...${NC}"
cd yks-assistant-frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "${BLUE}✅ Servisler çalışıyor!${NC}"
echo -e "👉 Frontend: http://localhost:3000"
echo -e "👉 Backend:  http://localhost:8000/docs"
echo ""
echo "Logları izlemek için: tail -f backend.log frontend.log"
echo "Çıkış yapmak için CTRL+C'ye basın."

# Uygulamayı açık tut
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
