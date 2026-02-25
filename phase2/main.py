"""
Phase 2: Backend REST API Entry Point.
Run with: python phase2/main.py
"""

import uvicorn

from phase2.api.main import app
from phase2.config import HOST, PORT

if __name__ == "__main__":
    print(f"Starting Restaurant Recommendation API on http://{HOST}:{PORT}")
    print(f"API Documentation: http://{HOST}:{PORT}/docs")
    uvicorn.run(app, host=HOST, port=PORT)
