"""Tests for scoring module."""

import pandas as pd
import pytest

from phase3.scoring.score_calculator import ScoreCalculator
from phase3.scoring.weight_config import WeightConfig


class TestWeightConfig:
    """Tests for WeightConfig."""

    def test_get_weights_returns_dict(self) -> None:
        config = WeightConfig(weights={"rating": 0.5, "price_match": 0.5})
        w = config.get_weights()
        assert w["rating"] == 0.5
        assert w["price_match"] == 0.5

    def test_get_weights_defaults(self) -> None:
        config = WeightConfig()
        w = config.get_weights()
        assert "rating" in w
        assert "price_match" in w
        assert sum(w.values()) > 0


class TestScoreCalculator:
    """Tests for ScoreCalculator."""

    def test_calculate_scores_adds_score_column(
        self, sample_restaurants_df: pd.DataFrame
    ) -> None:
        calc = ScoreCalculator()
        result = calc.calculate_scores(sample_restaurants_df)
        assert "score" in result.columns
        assert all(result["score"] >= 0)
        assert all(result["score"] <= 1.5)  # Max possible ~1.0 + buffer

    def test_calculate_scores_with_cuisine_preference(
        self, sample_restaurants_df: pd.DataFrame
    ) -> None:
        calc = ScoreCalculator()
        result = calc.calculate_scores(
            sample_restaurants_df, user_cuisine="Italian"
        )
        italian_scores = result[result["cuisine"].str.lower().str.contains("italian")]["score"]
        assert len(italian_scores) > 0
        assert italian_scores.mean() >= 0

    def test_empty_dataframe(self) -> None:
        calc = ScoreCalculator()
        result = calc.calculate_scores(pd.DataFrame())
        assert len(result) == 0
