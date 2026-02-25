"""
Feature Engineering for Zomato restaurant data.
Creates derived features for recommendation and filtering.
"""

import logging
from typing import Optional

import pandas as pd

from phase1.config import (
    MAX_RATING,
    PRICE_BUCKET_LABELS,
    PRICE_BUCKET_LOW_MAX,
    PRICE_BUCKET_MEDIUM_MAX,
    LOG_FORMAT,
    LOG_LEVEL,
)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Creates derived features for restaurant data."""

    def __init__(
        self,
        low_max: float = PRICE_BUCKET_LOW_MAX,
        medium_max: float = PRICE_BUCKET_MEDIUM_MAX,
        max_rating: float = MAX_RATING,
    ) -> None:
        """
        Initialize the feature engineer.

        Args:
            low_max: Maximum cost for 'low' price bucket.
            medium_max: Maximum cost for 'medium' price bucket.
            max_rating: Maximum rating (for normalization).
        """
        self.low_max = low_max
        self.medium_max = medium_max
        self.max_rating = max_rating

    def _create_price_bucket(self, cost: Optional[float]) -> str:
        """
        Assign price bucket based on cost.

        Args:
            cost: Approximate cost for two.

        Returns:
            One of 'low', 'medium', 'high'.
        """
        if cost is None or (isinstance(cost, float) and pd.isna(cost)):
            return PRICE_BUCKET_LABELS[1]  # default to medium
        try:
            c = float(cost)
            if c <= self.low_max:
                return PRICE_BUCKET_LABELS[0]
            if c <= self.medium_max:
                return PRICE_BUCKET_LABELS[1]
            return PRICE_BUCKET_LABELS[2]
        except (TypeError, ValueError):
            return PRICE_BUCKET_LABELS[1]

    def _create_normalized_rating(self, rating: Optional[float]) -> float:
        """
        Normalize rating to 0-1 scale.

        Args:
            rating: Raw rating (typically 0-5).

        Returns:
            Normalized rating between 0 and 1.
        """
        if rating is None or (isinstance(rating, float) and pd.isna(rating)):
            return 0.0
        try:
            r = float(rating)
            return round(r / self.max_rating, 4)
        except (TypeError, ValueError):
            return 0.0

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply feature engineering to the DataFrame.

        Args:
            df: Cleaned DataFrame from DataCleaner.

        Returns:
            DataFrame with engineered features.
        """
        logger.info("Starting feature engineering on %d rows", len(df))
        df = df.copy()

        # Ensure cuisine_list exists
        if "cuisine_list" not in df.columns:
            df["cuisine_list"] = df.get("cuisine", pd.Series()).apply(
                lambda x: [str(x).strip().lower()] if x and str(x).strip() else []
            )

        # Create price_bucket
        df["price_bucket"] = df.get("cost", pd.Series()).apply(
            self._create_price_bucket
        )
        logger.info("Created price_bucket column")

        # Create normalized_rating
        df["normalized_rating"] = df.get("rating", pd.Series()).apply(
            self._create_normalized_rating
        )
        logger.info("Created normalized_rating column")

        # Ensure correct data types
        type_mapping = {
            "name": str,
            "location": str,
            "cuisine": str,
            "rating": float,
            "cost": float,
            "price_bucket": str,
            "normalized_rating": float,
        }
        for col, dtype in type_mapping.items():
            if col in df.columns:
                if dtype == str:
                    df[col] = df[col].fillna("").astype(str)
                elif dtype == float:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                else:
                    df[col] = df[col].astype(dtype)

        # votes as int if present
        if "votes" in df.columns:
            df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)

        logger.info("Feature engineering complete")
        return df
