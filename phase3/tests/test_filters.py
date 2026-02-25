"""Tests for modular filters."""

import pandas as pd
import pytest

from phase3.filters.location_filter import LocationFilter
from phase3.filters.price_filter import PriceFilter
from phase3.filters.rating_filter import RatingFilter
from phase3.filters.cuisine_filter import CuisineFilter
from phase3.filters.filter_engine import FilterEngine


class TestLocationFilter:
    """Tests for LocationFilter."""

    def test_apply_filters_by_location(self, sample_restaurants_df: pd.DataFrame) -> None:
        f = LocationFilter()
        result = f.apply(sample_restaurants_df, "Bangalore")
        assert len(result) == 4
        assert all("bangalore" in loc.lower() for loc in result["location"])

    def test_apply_empty_location_returns_all(self, sample_restaurants_df: pd.DataFrame) -> None:
        f = LocationFilter()
        result = f.apply(sample_restaurants_df, None)
        assert len(result) == len(sample_restaurants_df)


class TestPriceFilter:
    """Tests for PriceFilter."""

    def test_apply_filters_by_price_range(self, sample_restaurants_df: pd.DataFrame) -> None:
        f = PriceFilter()
        result = f.apply(sample_restaurants_df, price_min=2, price_max=2)
        assert len(result) >= 2
        assert all(r in ["medium"] for r in result["price_bucket"])

    def test_apply_no_price_returns_all(self, sample_restaurants_df: pd.DataFrame) -> None:
        f = PriceFilter()
        result = f.apply(sample_restaurants_df, None, None)
        assert len(result) == len(sample_restaurants_df)


class TestRatingFilter:
    """Tests for RatingFilter."""

    def test_apply_filters_by_rating(self, sample_restaurants_df: pd.DataFrame) -> None:
        f = RatingFilter()
        result = f.apply(sample_restaurants_df, min_rating=4.0)
        assert len(result) == 5
        assert all(result["rating"] >= 4.0)

    def test_apply_no_rating_returns_all(self, sample_restaurants_df: pd.DataFrame) -> None:
        f = RatingFilter()
        result = f.apply(sample_restaurants_df, None)
        assert len(result) == len(sample_restaurants_df)


class TestCuisineFilter:
    """Tests for CuisineFilter."""

    def test_apply_filters_by_cuisine(self, sample_restaurants_df: pd.DataFrame) -> None:
        f = CuisineFilter()
        result = f.apply(sample_restaurants_df, "Italian")
        assert len(result) == 3

    def test_apply_no_cuisine_returns_all(self, sample_restaurants_df: pd.DataFrame) -> None:
        f = CuisineFilter()
        result = f.apply(sample_restaurants_df, None)
        assert len(result) == len(sample_restaurants_df)


class TestFilterEngine:
    """Tests for FilterEngine."""

    def test_filter_multiple_criteria(self, sample_restaurants_df: pd.DataFrame) -> None:
        engine = FilterEngine()
        result = engine.filter(
            sample_restaurants_df,
            location="Bangalore",
            cuisine="Italian",
            min_rating=4.0,
        )
        assert len(result) == 3  # Restaurant A, Eatery E, Bistro F
        assert all("italian" in str(c).lower() for c in result["cuisine"])
        assert all(result["rating"] >= 4.0)
