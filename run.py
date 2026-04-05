# run.py
import sys
import os

# Add project root to Python path (fixes Windows import issues)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=True
    )