import sys
import os

# Force-add backend dir to path for ALL child processes
os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run directly - no subprocess, no spawn
import main
import uvicorn

uvicorn.run(main.app, host="0.0.0.0", port=8000)