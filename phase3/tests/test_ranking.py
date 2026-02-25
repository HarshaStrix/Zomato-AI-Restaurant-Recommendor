"""Tests for ranking module."""

import pandas as pd
import pytest

from phase3.ranking.ranker import Ranker
from phase3.scoring.score_calculator import ScoreCalculator


class TestRanker:
    """Tests for Ranker."""

    def test_rank_returns_top_n(self, sample_restaurants_df: pd.DataFrame) -> None:
        calc = ScoreCalculator()
        scored = calc.calculate_scores(sample_restaurants_df)
        ranker = Ranker()
        result = ranker.rank(scored, limit=3)
        assert len(result) == 3
        assert "score" in result.columns

    def test_rank_sorted_by_score_desc(self, sample_restaurants_df: pd.DataFrame) -> None:
        calc = ScoreCalculator()
        scored = calc.calculate_scores(sample_restaurants_df)
        ranker = Ranker()
        result = ranker.rank(scored, limit=5)
        scores = result["score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_rank_empty_dataframe(self) -> None:
        ranker = Ranker()
        result = ranker.rank(pd.DataFrame(), limit=5)
        assert len(result) == 0

    def test_rank_tie_breaking(self, sample_restaurants_df: pd.DataFrame) -> None:
        # Create two rows with same score
        df = sample_restaurants_df.head(2).copy()
        df.loc[df.index[0], "rating"] = 4.5
        df.loc[df.index[1], "rating"] = 4.5
        df["score"] = [0.8, 0.8]
        ranker = Ranker()
        result = ranker.rank(df, limit=2)
        assert len(result) == 2
