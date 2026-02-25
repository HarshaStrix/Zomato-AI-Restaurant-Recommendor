"""
Configuration for Phase 1: Data Ingestion & Preprocessing.
Centralizes constants and paths for easy maintenance.
"""

import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# -----------------------------------------------------------------------------
# Hugging Face Dataset
# -----------------------------------------------------------------------------
HUGGINGFACE_DATASET = "ManikaSaini/zomato-restaurant-recommendation"
HUGGINGFACE_SPLIT = "train"  # Primary split to use

# -----------------------------------------------------------------------------
# Column Mapping (Hugging Face dataset may use different column names)
# Maps our expected columns to potential dataset column names
# -----------------------------------------------------------------------------
COLUMN_MAPPING = {
    "name": ["name", "restaurant_name", "Restaurant Name"],
    "cuisine": ["cuisines", "cuisine", "Cuisines"],
    "location": [
        "location",
        "city",
        "City",
        "address",
        "Location",
        "listed_in(city)",
    ],
    "rating": ["rate", "rating", "Rating", "aggregate_rating"],
    "cost": [
        "approx_cost(for_two)",
        "approx_cost",
        "cost",
        "average_cost",
        "price_range",
    ],
    "votes": ["votes", "Votes", "review_count", "num_reviews"],
}

# Required columns that must exist after mapping
REQUIRED_COLUMNS = ["name", "cuisine", "location", "rating", "cost"]

# Output columns for processed data
OUTPUT_COLUMNS = [
    "name",
    "cuisine",
    "cuisine_list",
    "location",
    "rating",
    "cost",
    "price_bucket",
    "normalized_rating",
    "votes",
]

# -----------------------------------------------------------------------------
# Data Cleaning
# -----------------------------------------------------------------------------
MIN_RATING = 0.0
MAX_RATING = 5.0
DEFAULT_RATING = 0.0  # For rows with invalid/missing rating

# Cost/Price buckets (based on approx cost for two in INR)
PRICE_BUCKET_LOW_MAX = 500
PRICE_BUCKET_MEDIUM_MAX = 1500
PRICE_BUCKET_LABELS = ("low", "medium", "high")

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASE_PATH = PROCESSED_DATA_DIR / "restaurants.db"
DATABASE_TABLE = "restaurants"

# -----------------------------------------------------------------------------
# File Names
# -----------------------------------------------------------------------------
RAW_CSV_FILENAME = "zomato_raw.csv"
PROCESSED_CSV_FILENAME = "zomato_processed.csv"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
