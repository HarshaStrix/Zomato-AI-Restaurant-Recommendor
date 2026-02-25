"""
Pytest fixtures for Phase 2 tests.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest
import sqlite3

from phase2.services.database_service import DatabaseService


@pytest.fixture
def sample_restaurants_dataframe() -> pd.DataFrame:
    """Sample restaurants DataFrame."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": [
                "Restaurant A",
                "Restaurant B",
                "Cafe C",
                "Diner D",
                "Eatery E",
            ],
            "location": ["Bangalore", "Mumbai", "Bangalore", "Delhi", "Bangalore"],
            "cuisine": [
                "Italian",
                "Indian",
                "Cafe",
                "American",
                "Italian",
            ],
            "cuisine_list": [
                "italian|pizza",
                "indian|north indian",
                "cafe|continental",
                "american|burger",
                "italian|pasta",
            ],
            "rating": [4.5, 4.2, 3.8, 4.0, 4.7],
            "cost": [800, 1200, 400, 2000, 900],
            "price_bucket": ["medium", "medium", "low", "high", "medium"],
            "normalized_rating": [0.9, 0.84, 0.76, 0.8, 0.94],
            "votes": [500, 300, 100, 800, 600],
        }
    )


@pytest.fixture
def temp_db_path(tmp_path: Path, sample_restaurants_dataframe: pd.DataFrame) -> Path:
    """Create temporary database with sample data."""
    db_path = tmp_path / "test_restaurants.db"
    conn = sqlite3.connect(str(db_path))
    sample_restaurants_dataframe.to_sql("restaurants", conn, if_exists="replace", index=False)
    conn.close()
    return db_path


@pytest.fixture
def db_service(temp_db_path: Path) -> DatabaseService:
    """Database service with test database."""
    return DatabaseService(db_path=temp_db_path)
