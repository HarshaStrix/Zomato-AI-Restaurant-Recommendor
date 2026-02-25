"""Pytest fixtures for Phase 3."""

import pandas as pd
import pytest


@pytest.fixture
def sample_restaurants_df() -> pd.DataFrame:
    """Sample restaurants DataFrame."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "name": [
                "Restaurant A",
                "Restaurant B",
                "Cafe C",
                "Diner D",
                "Eatery E",
                "Bistro F",
            ],
            "location": [
                "Bangalore",
                "Mumbai",
                "Bangalore",
                "Delhi",
                "Bangalore",
                "Bangalore",
            ],
            "cuisine": [
                "Italian",
                "Indian",
                "Cafe",
                "American",
                "Italian",
                "Italian",
            ],
            "cuisine_list": [
                "italian|pizza",
                "indian|north indian",
                "cafe|continental",
                "american|burger",
                "italian|pasta",
                "italian|seafood",
            ],
            "rating": [4.5, 4.2, 3.8, 4.0, 4.7, 4.3],
            "cost": [800, 1200, 400, 2000, 900, 1100],
            "price_bucket": ["medium", "medium", "low", "high", "medium", "medium"],
            "normalized_rating": [0.9, 0.84, 0.76, 0.8, 0.94, 0.86],
            "votes": [500, 300, 100, 800, 600, 400],
        }
    )
