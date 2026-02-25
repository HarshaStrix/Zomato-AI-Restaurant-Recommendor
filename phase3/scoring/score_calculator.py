"""
Score calculator for multi-factor restaurant scoring.
"""

import logging
from typing import Optional

import pandas as pd

from phase3.config import MAX_RATING, POPULARITY_CAP, PRICE_BUCKET_MAP
from phase3.scoring.weight_config import WeightConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ScoreCalculator:
    """Calculates composite scores for restaurants."""

    def __init__(self, weight_config: Optional[WeightConfig] = None) -> None:
        """Initialize with weight configuration."""
        self.weight_config = weight_config or WeightConfig()
        self.weights = self.weight_config.get_weights()

    def _rating_score(self, rating: float) -> float:
        """Rating score: (rating / 5.0) * weight."""
        return (rating / MAX_RATING) * self.weights.get("rating", 0.4)

    def _price_match_score(
        self,
        price_bucket: str,
        price_min: Optional[int],
        price_max: Optional[int],
    ) -> float:
        """Price match score based on alignment with user preference."""
        weight = self.weights.get("price_match", 0.2)
        price_numeric = PRICE_BUCKET_MAP.get(price_bucket, 2)

        if price_min is None and price_max is None:
            return weight * 0.5

        if price_min is not None and price_max is not None:
            if price_min <= price_numeric <= price_max:
                return weight
            elif price_numeric < price_min:
                return weight * 0.5
            else:
                return weight * 0.25

        if price_min is not None:
            return weight if price_numeric >= price_min else weight * 0.5
        if price_max is not None:
            return weight if price_numeric <= price_max else weight * 0.25

        return 0.0

    def _cuisine_match_score(
        self,
        cuisine: str,
        cuisine_list: str,
        user_cuisine: Optional[str],
    ) -> float:
        """Cuisine match score."""
        if not user_cuisine:
            return 0.0

        weight = self.weights.get("cuisine_match", 0.2)
        user_lower = user_cuisine.lower()
        cuisine_lower = str(cuisine).lower()
        list_lower = str(cuisine_list).lower()

        if user_lower in cuisine_lower or user_lower in list_lower:
            return weight
        if any(user_lower in item.strip() for item in list_lower.split("|") if item.strip()):
            return weight * 0.5

        return 0.0

    def _popularity_score(self, votes: Optional[int]) -> float:
        """Popularity score: normalized review count."""
        weight = self.weights.get("popularity", 0.15)
        if votes is None or votes == 0:
            return 0.0
        normalized = min(votes / POPULARITY_CAP, 1.0)
        return normalized * weight

    def _proximity_score(
        self,
        user_coords: Optional[dict],
        restaurant_coords: Optional[dict],
    ) -> float:
        """Proximity score (placeholder)."""
        weight = self.weights.get("proximity", 0.05)
        if not user_coords or not restaurant_coords:
            return weight * 0.5
        return weight * 0.5

    def calculate_scores(
        self,
        df: pd.DataFrame,
        user_cuisine: Optional[str] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        user_coords: Optional[dict] = None,
    ) -> pd.DataFrame:
        """
        Calculate all component scores and total score.

        Args:
            df: Restaurant DataFrame.
            user_cuisine: User's preferred cuisine.
            price_min: Minimum price range.
            price_max: Maximum price range.
            user_coords: User coordinates.

        Returns:
            DataFrame with score columns added.
        """
        if len(df) == 0:
            return df

        scored = df.copy()
        scored["rating_score"] = scored["rating"].apply(self._rating_score)
        scored["price_score"] = scored["price_bucket"].apply(
            lambda x: self._price_match_score(x, price_min, price_max)
        )
        scored["cuisine_score"] = scored.apply(
            lambda row: self._cuisine_match_score(
                row.get("cuisine", ""),
                row.get("cuisine_list", ""),
                user_cuisine,
            ),
            axis=1,
        )
        scored["popularity_score"] = scored.get("votes", pd.Series([0])).apply(
            self._popularity_score
        )
        scored["proximity_score"] = scored.apply(
            lambda row: self._proximity_score(user_coords, row.get("coordinates")),
            axis=1,
        )
        scored["score"] = (
            scored["rating_score"]
            + scored["price_score"]
            + scored["cuisine_score"]
            + scored["popularity_score"]
            + scored["proximity_score"]
        )

        return scored
