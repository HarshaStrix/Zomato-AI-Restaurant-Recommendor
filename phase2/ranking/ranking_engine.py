"""
Ranking engine for scoring and ranking restaurants.
"""

import logging
from typing import Optional

import pandas as pd

from phase2.config import RANKING_WEIGHTS, LOG_FORMAT, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class RankingEngine:
    """Scores and ranks restaurants based on multiple factors."""

    def __init__(self, weights: Optional[dict[str, float]] = None) -> None:
        """
        Initialize ranking engine.

        Args:
            weights: Custom ranking weights. Defaults to config weights.
        """
        self.weights = weights or RANKING_WEIGHTS

    def _calculate_rating_score(self, rating: float) -> float:
        """Calculate normalized rating score (0-1)."""
        return (rating / 5.0) * self.weights["rating"]

    def _calculate_price_match_score(
        self, price_bucket: str, price_min: Optional[int], price_max: Optional[int]
    ) -> float:
        """Calculate price match score."""
        bucket_map = {"low": 1, "medium": 2, "high": 3}
        price_numeric = bucket_map.get(price_bucket, 2)

        if price_min is None and price_max is None:
            return self.weights["price_match"] * 0.5  # Neutral score

        if price_min is not None and price_max is not None:
            if price_min <= price_numeric <= price_max:
                return self.weights["price_match"]  # Full score
            elif price_numeric < price_min:
                return self.weights["price_match"] * 0.5  # Bonus for cheaper
            else:
                return self.weights["price_match"] * 0.25  # Penalty for expensive

        if price_min is not None:
            if price_numeric >= price_min:
                return self.weights["price_match"]
            else:
                return self.weights["price_match"] * 0.5

        if price_max is not None:
            if price_numeric <= price_max:
                return self.weights["price_match"]
            else:
                return self.weights["price_match"] * 0.25

        return 0.0

    def _calculate_cuisine_match_score(
        self, cuisine: str, cuisine_list: str, user_cuisine: Optional[str]
    ) -> float:
        """Calculate cuisine match score."""
        if not user_cuisine:
            return 0.0

        user_cuisine_lower = user_cuisine.lower()
        cuisine_lower = str(cuisine).lower()
        cuisine_list_lower = str(cuisine_list).lower()

        if user_cuisine_lower in cuisine_lower or user_cuisine_lower in cuisine_list_lower:
            return self.weights["cuisine_match"]  # Exact match
        # Partial match (e.g., "italian" in "italian, pizza")
        if any(
            user_cuisine_lower in item.strip()
            for item in cuisine_list_lower.split("|")
            if item.strip()
        ):
            return self.weights["cuisine_match"] * 0.5

        return 0.0

    def _calculate_popularity_score(self, votes: Optional[int]) -> float:
        """Calculate popularity score based on review count."""
        if votes is None or votes == 0:
            return 0.0

        # Normalize: cap at 1000 reviews for scoring
        normalized = min(votes / 1000.0, 1.0)
        return normalized * self.weights["popularity"]

    def _calculate_proximity_score(
        self, user_coords: Optional[dict], restaurant_coords: Optional[dict]
    ) -> float:
        """Calculate proximity score (placeholder - requires coordinates)."""
        if not user_coords or not restaurant_coords:
            return self.weights["proximity"] * 0.5  # Default for same city

        # Placeholder: would calculate distance here
        # For now, return default score
        return self.weights["proximity"] * 0.5

    def score_and_rank(
        self,
        df: pd.DataFrame,
        user_cuisine: Optional[str] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        user_coords: Optional[dict] = None,
        limit: int = 5,
    ) -> pd.DataFrame:
        """
        Score and rank restaurants.

        Args:
            df: Filtered restaurant DataFrame.
            user_cuisine: User's preferred cuisine.
            price_min: Minimum price range.
            price_max: Maximum price range.
            user_coords: User coordinates (optional).
            limit: Number of top results to return.

        Returns:
            DataFrame with scores and rankings.
        """
        if len(df) == 0:
            return df

        scored = df.copy()

        # Calculate component scores
        scored["rating_score"] = scored["rating"].apply(self._calculate_rating_score)
        scored["price_score"] = scored["price_bucket"].apply(
            lambda x: self._calculate_price_match_score(x, price_min, price_max)
        )
        scored["cuisine_score"] = scored.apply(
            lambda row: self._calculate_cuisine_match_score(
                row.get("cuisine", ""),
                row.get("cuisine_list", ""),
                user_cuisine,
            ),
            axis=1,
        )
        scored["popularity_score"] = scored.get("votes", pd.Series([0])).apply(
            self._calculate_popularity_score
        )
        scored["proximity_score"] = scored.apply(
            lambda row: self._calculate_proximity_score(
                user_coords, row.get("coordinates")
            ),
            axis=1,
        )

        # Calculate total score
        scored["score"] = (
            scored["rating_score"]
            + scored["price_score"]
            + scored["cuisine_score"]
            + scored["popularity_score"]
            + scored["proximity_score"]
        )

        # Sort by score (descending) and handle ties
        scored = scored.sort_values(
            by=["score", "rating", "votes"], ascending=[False, False, False]
        )

        # Return top N
        result = scored.head(limit).copy()

        # Clean up intermediate columns
        result = result.drop(
            columns=[
                "rating_score",
                "price_score",
                "cuisine_score",
                "popularity_score",
                "proximity_score",
            ],
            errors="ignore",
        )

        logger.info("Ranked and selected top %d restaurants", len(result))
        return result
