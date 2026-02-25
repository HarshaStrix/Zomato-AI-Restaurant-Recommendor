"""
Filtering engine for applying user preference filters to restaurants.
"""

import logging
from typing import Optional

import pandas as pd

from phase2.config import LOG_FORMAT, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class FilterEngine:
    """Applies filters to restaurant data based on user preferences."""

    def filter(
        self,
        df: pd.DataFrame,
        location: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_rating: Optional[float] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Apply filters to restaurant DataFrame.

        Args:
            df: Restaurant DataFrame.
            location: Location filter (case-insensitive partial match).
            cuisine: Cuisine filter (case-insensitive partial match).
            min_rating: Minimum rating filter.
            price_min: Minimum price range (1-4).
            price_max: Maximum price range (1-4).

        Returns:
            Filtered DataFrame.
        """
        filtered = df.copy()
        initial_count = len(filtered)

        # Location filter
        if location:
            location_lower = location.lower()
            filtered = filtered[
                filtered["location"].str.lower().str.contains(location_lower, na=False)
            ]
            logger.debug("After location filter: %d rows", len(filtered))

        # Cuisine filter
        if cuisine:
            cuisine_lower = cuisine.lower()
            mask = (
                filtered["cuisine"].str.lower().str.contains(cuisine_lower, na=False)
                | filtered["cuisine_list"]
                .astype(str)
                .str.lower()
                .str.contains(cuisine_lower, na=False)
            )
            filtered = filtered[mask]
            logger.debug("After cuisine filter: %d rows", len(filtered))

        # Rating filter
        if min_rating is not None:
            filtered = filtered[filtered["rating"] >= min_rating]
            logger.debug("After rating filter: %d rows", len(filtered))

        # Price range filter
        if price_min is not None or price_max is not None:
            # Map price range to price_bucket
            bucket_map = {"low": 1, "medium": 2, "high": 3}
            filtered["price_range_numeric"] = filtered["price_bucket"].map(bucket_map)

            if price_min is not None and price_max is not None:
                filtered = filtered[
                    (filtered["price_range_numeric"] >= price_min)
                    & (filtered["price_range_numeric"] <= price_max)
                ]
            elif price_min is not None:
                filtered = filtered[filtered["price_range_numeric"] >= price_min]
            elif price_max is not None:
                filtered = filtered[filtered["price_range_numeric"] <= price_max]

            filtered = filtered.drop(columns=["price_range_numeric"], errors="ignore")
            logger.debug("After price filter: %d rows", len(filtered))

        logger.info(
            "Filtered %d restaurants down to %d (location=%s, cuisine=%s, "
            "min_rating=%s, price=%s-%s)",
            initial_count,
            len(filtered),
            location,
            cuisine,
            min_rating,
            price_min,
            price_max,
        )

        return filtered
