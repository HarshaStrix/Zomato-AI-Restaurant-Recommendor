"""
Phase 3: Recommendation Engine - orchestrates filtering, scoring, and ranking.
"""

import logging
from typing import Optional

import pandas as pd

from phase3.config import LOG_FORMAT, LOG_LEVEL
from phase3.filters.filter_engine import FilterEngine
from phase3.scoring.score_calculator import ScoreCalculator
from phase3.ranking.ranker import Ranker

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Orchestrates the full recommendation pipeline:
    Filter -> Score -> Rank -> Top N
    """

    def __init__(
        self,
        filter_engine: Optional[FilterEngine] = None,
        score_calculator: Optional[ScoreCalculator] = None,
        ranker: Optional[Ranker] = None,
    ) -> None:
        """Initialize recommendation engine."""
        self.filter_engine = filter_engine or FilterEngine()
        self.score_calculator = score_calculator or ScoreCalculator()
        self.ranker = ranker or Ranker()

    def get_recommendations(
        self,
        df: pd.DataFrame,
        location: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_rating: Optional[float] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        cost_min: Optional[float] = None,
        cost_max: Optional[float] = None,
        user_coords: Optional[dict] = None,
        limit: int = 5,
    ) -> tuple[pd.DataFrame, int]:
        """
        Get top N restaurant recommendations.

        Args:
            df: Restaurant DataFrame.
            location: Location filter.
            cuisine: Cuisine filter.
            min_rating: Minimum rating filter.
            price_min: Minimum price range (1-4).
            price_max: Maximum price range (1-4).
            cost_min: Minimum cost in ₹.
            cost_max: Maximum cost in ₹.
            user_coords: User coordinates (for proximity scoring).
            limit: Number of recommendations to return.

        Returns:
            Tuple of (recommendations DataFrame, total filtered count).
        """
        logger.info(
            "Getting recommendations: location=%s, cuisine=%s, min_rating=%s, "
            "price=%s-%s, cost=%s-%s, limit=%d",
            location,
            cuisine,
            min_rating,
            price_min,
            price_max,
            cost_min,
            cost_max,
            limit,
        )

        # 1. Filter
        filtered = self.filter_engine.filter(
            df,
            location=location,
            cuisine=cuisine,
            min_rating=min_rating,
            price_min=price_min,
            price_max=price_max,
            cost_min=cost_min,
            cost_max=cost_max,
        )

        total_found = len(filtered)

        if total_found == 0:
            logger.info("No restaurants match the filters")
            return pd.DataFrame(), 0

        # 2. Score
        scored = self.score_calculator.calculate_scores(
            filtered,
            user_cuisine=cuisine,
            price_min=price_min,
            price_max=price_max,
            user_coords=user_coords,
        )

        # 3. Rank
        ranked = self.ranker.rank(scored, limit=limit)

        return ranked, total_found
