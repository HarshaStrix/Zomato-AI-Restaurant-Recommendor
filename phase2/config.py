"""
Configuration for Phase 2: Backend REST API.
"""

import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Phase 1 database path
PHASE1_DB_PATH = PROJECT_ROOT / "phase1" / "data" / "processed" / "restaurants.db"

# -----------------------------------------------------------------------------
# API Configuration
# -----------------------------------------------------------------------------
API_TITLE = "Zomato AI Restaurant Recommender API"
API_VERSION = "v1"
API_PREFIX = "/api/v1"

# Default recommendation limit
DEFAULT_RECOMMENDATION_LIMIT = 5
MAX_RECOMMENDATION_LIMIT = 50

# -----------------------------------------------------------------------------
# Ranking Weights
# -----------------------------------------------------------------------------
RANKING_WEIGHTS = {
    "rating": 0.5,           # Increased from 0.4
    "price_match": 0.2,
    "cuisine_match": 0.15,   # Decreased from 0.2
    "popularity": 0.1,       # Decreased from 0.15
    "proximity": 0.05,
}

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# -----------------------------------------------------------------------------
# Server Configuration
# -----------------------------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
