"""
Tests for RankingEngine.
"""

import pandas as pd
import pytest

from phase2.ranking.ranking_engine import RankingEngine


class TestRankingEngine:
    """Test suite for RankingEngine."""

    def test_score_and_rank(self, sample_restaurants_dataframe: pd.DataFrame) -> None:
        """Test scoring and ranking."""
        engine = RankingEngine()
        ranked = engine.score_and_rank(sample_restaurants_dataframe, limit=3)
        assert len(ranked) == 3
        assert "score" in ranked.columns
        # Should be sorted by score descending
        scores = ranked["score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_ranking_with_cuisine_preference(
        self, sample_restaurants_dataframe: pd.DataFrame
    ) -> None:
        """Test ranking prioritizes preferred cuisine."""
        engine = RankingEngine()
        ranked = engine.score_and_rank(
            sample_restaurants_dataframe, user_cuisine="Italian", limit=5
        )
        # Italian restaurants should rank higher
        top_cuisines = ranked.head(2)["cuisine"].tolist()
        assert "Italian" in top_cuisines

    def test_ranking_with_price_preference(
        self, sample_restaurants_dataframe: pd.DataFrame
    ) -> None:
        """Test ranking considers price preference."""
        engine = RankingEngine()
        ranked = engine.score_and_rank(
            sample_restaurants_dataframe, price_min=2, price_max=2, limit=5
        )
        # Medium price restaurants should rank higher
        assert len(ranked) > 0

    def test_empty_dataframe(self) -> None:
        """Test handling of empty DataFrame."""
        engine = RankingEngine()
        empty_df = pd.DataFrame()
        result = engine.score_and_rank(empty_df)
        assert len(result) == 0
