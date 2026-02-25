"""
Configuration for Phase 4: LLM Integration Layer (Groq).
"""

import os
from pathlib import Path
from typing import Optional

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# -----------------------------------------------------------------------------
# Groq API
# -----------------------------------------------------------------------------
# Set GROQ_API_KEY in environment or .env; never commit the key.
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Fast model on Groq
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "600"))
GROQ_TIMEOUT_SECONDS = int(os.getenv("GROQ_TIMEOUT", "15"))

# -----------------------------------------------------------------------------
# Retry
# -----------------------------------------------------------------------------
GROQ_MAX_RETRIES = 3
GROQ_RETRY_BACKOFF_FACTOR = 2.0  # Exponential backoff

# -----------------------------------------------------------------------------
# Cache (in-memory for MVP; Redis can be added later)
# -----------------------------------------------------------------------------
LLM_CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours
LLM_CACHE_ENABLED = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
