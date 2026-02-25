"""
Pytest fixtures for Phase 1 tests.
Provides mock data to avoid network calls during testing.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_raw_dataframe() -> pd.DataFrame:
    """Sample DataFrame simulating raw Zomato dataset structure."""
    return pd.DataFrame(
        {
            "name": [
                "Restaurant A",
                "Restaurant B",
                "Cafe C",
                "Diner D",
                "Eatery E",
            ],
            "cuisines": [
                "Italian, Pizza",
                "Indian, North Indian",
                "Cafe, Continental",
                "American, Burger",
                "Chinese",
            ],
            "location": ["Bangalore", "Mumbai", "Delhi", "Chennai", "Bangalore"],
            "rate": ["4.2/5", "4.5/5", "NEW", "3.8/5", "4.0/5"],
            "approx_cost(for_two)": [800, 1500, 400, 2500, 600],
            "votes": [100, 250, 50, 400, 80],
        }
    )


@pytest.fixture
def sample_raw_dataframe_with_nulls() -> pd.DataFrame:
    """Sample DataFrame with nulls for cleaning tests."""
    return pd.DataFrame(
        {
            "name": ["Restaurant A", "", "Cafe C"],
            "cuisines": ["Italian", None, "Cafe"],
            "location": ["Bangalore", "Mumbai", ""],
            "rate": ["4.2/5", None, "3.5/5"],
            "approx_cost(for_two)": [800, None, 400],
            "votes": [100, 50, 0],
        }
    )


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Temporary directory for test data."""
    raw_dir = tmp_path / "data" / "raw"
    processed_dir = tmp_path / "data" / "processed"
    raw_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Temporary database path."""
    db_dir = tmp_path / "data" / "processed"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "test_restaurants.db"
