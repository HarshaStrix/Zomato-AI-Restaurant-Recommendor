"""
Configuration for Phase 3: Recommendation & Ranking Engine.
"""

import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
WEIGHTS_CONFIG_PATH = BASE_DIR / "config" / "weights.yaml"

# -----------------------------------------------------------------------------
# Default Ranking Weights
# -----------------------------------------------------------------------------
DEFAULT_WEIGHTS = {
    "rating": 0.4,
    "price_match": 0.2,
    "cuisine_match": 0.2,
    "popularity": 0.15,
    "proximity": 0.05,
}

# -----------------------------------------------------------------------------
# Scoring Parameters
# -----------------------------------------------------------------------------
MAX_RATING = 5.0
POPULARITY_CAP = 1000  # Reviews cap for normalization
PRICE_BUCKET_MAP = {"low": 1, "medium": 2, "high": 3}

# -----------------------------------------------------------------------------
# Tie-breaking order (secondary sort columns)
# -----------------------------------------------------------------------------
TIE_BREAK_COLUMNS = ["rating", "votes", "name"]

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
