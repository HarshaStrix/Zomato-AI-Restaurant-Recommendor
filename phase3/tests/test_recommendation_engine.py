"""Tests for RecommendationEngine."""

import pandas as pd
import pytest

from phase3.recommendation_engine import RecommendationEngine


class TestRecommendationEngine:
    """Tests for RecommendationEngine."""

    def test_get_recommendations_returns_top_5(
        self, sample_restaurants_df: pd.DataFrame
    ) -> None:
        engine = RecommendationEngine()
        recommendations, total = engine.get_recommendations(
            sample_restaurants_df,
            location="Bangalore",
            limit=5,
        )
        assert total == 4
        assert len(recommendations) <= 5
        assert "score" in recommendations.columns

    def test_get_recommendations_with_filters(
        self, sample_restaurants_df: pd.DataFrame
    ) -> None:
        engine = RecommendationEngine()
        recommendations, total = engine.get_recommendations(
            sample_restaurants_df,
            location="Bangalore",
            cuisine="Italian",
            min_rating=4.0,
            limit=5,
        )
        assert total == 3
        assert len(recommendations) <= 5
        if len(recommendations) > 0:
            assert all("italian" in str(c).lower() for c in recommendations["cuisine"])

    def test_get_recommendations_no_results(
        self, sample_restaurants_df: pd.DataFrame
    ) -> None:
        engine = RecommendationEngine()
        recommendations, total = engine.get_recommendations(
            sample_restaurants_df,
            location="NonexistentCity",
            limit=5,
        )
        assert total == 0
        assert len(recommendations) == 0

    def test_get_recommendations_respects_limit(
        self, sample_restaurants_df: pd.DataFrame
    ) -> None:
        engine = RecommendationEngine()
        recommendations, total = engine.get_recommendations(
            sample_restaurants_df,
            location="Bangalore",
            limit=2,
        )
        assert len(recommendations) <= 2
        assert total >= 2
