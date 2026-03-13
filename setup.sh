#!/bin/bash
set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ███████╗████████╗██╗   ██╗██████╗ ██╗ ██████╗      █████╗ ██╗"
echo "  ██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗    ██╔══██╗██║"
echo "  ███████╗   ██║   ██║   ██║██║  ██║██║██║   ██║    ███████║██║"
echo "  ╚════██║   ██║   ██║   ██║██║  ██║██║██║   ██║    ██╔══██║██║"
echo "  ███████║   ██║   ╚██████╔╝██████╔╝██║╚██████╔╝    ██║  ██║██║"
echo -e "  ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝     ╚═╝  ╚═╝╚═╝${NC}"
echo ""
echo -e "${GREEN}🎬 StudioAvatarAI — Professional AI Avatar Generator${NC}"
echo "======================================================"
echo ""

echo -e "${YELLOW}📁 Creating directory structure...${NC}"
mkdir -p data/{avatars,backgrounds,inputs,frames,audio,outputs} models
for d in data/{avatars,backgrounds,inputs,frames,audio,outputs} models; do
  touch "$d/.gitkeep"
done
echo -e "${GREEN}✓ Directories ready${NC}"
echo ""

echo -e "${YELLOW}🐍 Setting up Python backend...${NC}"
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"
cd ..
echo ""

echo -e "${YELLOW}⚛️  Setting up React frontend...${NC}"
cd frontend
npm install --legacy-peer-deps
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
cd ..
echo ""

echo -e "${GREEN}======================================================"
echo "✅ SETUP COMPLETE!"
echo "======================================================"
echo ""
echo "  Terminal 1 — Backend:"
echo "    cd backend && source .venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  Terminal 2 — Frontend:"
echo "    cd frontend && npm start"
echo -e "${NC}"