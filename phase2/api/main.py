"""
FastAPI application for Restaurant Recommendation API.
"""

import logging
from pathlib import Path

# Load .env from project root (for GROQ_API_KEY)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from phase2.api.routes.recommendations import router
from phase2.config import API_PREFIX, API_TITLE, API_VERSION, LOG_FORMAT, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="REST API for restaurant recommendations",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=API_PREFIX)

# Frontend: serve UI at /
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
INDEX_HTML = FRONTEND_DIR / "index.html"


@app.get("/")
async def serve_ui():
    """Serve the recommendation UI (Phase 1 dropdowns + recommendations)."""
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return {"message": "Restaurant Recommendation API", "version": API_VERSION, "docs": "/docs"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    from phase2.config import HOST, PORT

    logger.info("Starting server on %s:%d", HOST, PORT)
    uvicorn.run(app, host=HOST, port=PORT)
