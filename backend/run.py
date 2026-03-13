import sys
import os

# Must happen BEFORE uvicorn imports anything
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Also set it for child processes
os.environ["PYTHONPATH"] = backend_dir

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[backend_dir],
    )