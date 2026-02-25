"""
Tests for FilterEngine.
"""

import pandas as pd
import pytest

from phase2.filters.filter_engine import FilterEngine


class TestFilterEngine:
    """Test suite for FilterEngine."""

    def test_filter_by_location(self, sample_restaurants_dataframe: pd.DataFrame) -> None:
        """Test location filtering."""
        engine = FilterEngine()
        filtered = engine.filter(sample_restaurants_dataframe, location="Bangalore")
        assert len(filtered) == 3
        assert all("bangalore" in loc.lower() for loc in filtered["location"])

    def test_filter_by_cuisine(self, sample_restaurants_dataframe: pd.DataFrame) -> None:
        """Test cuisine filtering."""
        engine = FilterEngine()
        filtered = engine.filter(sample_restaurants_dataframe, cuisine="Italian")
        assert len(filtered) == 2

    def test_filter_by_rating(self, sample_restaurants_dataframe: pd.DataFrame) -> None:
        """Test rating filtering."""
        engine = FilterEngine()
        filtered = engine.filter(sample_restaurants_dataframe, min_rating=4.0)
        assert len(filtered) == 4
        assert all(filtered["rating"] >= 4.0)

    def test_filter_by_price_range(
        self, sample_restaurants_dataframe: pd.DataFrame
    ) -> None:
        """Test price range filtering."""
        engine = FilterEngine()
        # Price range 1-2 (low to medium)
        filtered = engine.filter(
            sample_restaurants_dataframe, price_min=1, price_max=2
        )
        assert len(filtered) >= 2

    def test_filter_multiple_criteria(
        self, sample_restaurants_dataframe: pd.DataFrame
    ) -> None:
        """Test filtering with multiple criteria."""
        engine = FilterEngine()
        filtered = engine.filter(
            sample_restaurants_dataframe,
            location="Bangalore",
            cuisine="Italian",
            min_rating=4.0,
        )
        assert len(filtered) == 2  # Restaurant A and Eatery E both match
        assert all("italian" in str(c).lower() for c in filtered["cuisine"])
        assert all(filtered["rating"] >= 4.0)
        assert all("bangalore" in str(loc).lower() for loc in filtered["location"])
