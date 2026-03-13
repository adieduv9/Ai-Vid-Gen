#!/bin/bash
cd /workspaces/Ai-Vid-Gen/backend
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
