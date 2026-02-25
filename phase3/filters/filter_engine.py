"""
Filter engine orchestrating all modular filters.
"""

import logging
from typing import Optional

import pandas as pd

from phase3.config import LOG_FORMAT, LOG_LEVEL
from phase3.filters.location_filter import LocationFilter
from phase3.filters.price_filter import PriceFilter
from phase3.filters.rating_filter import RatingFilter
from phase3.filters.cuisine_filter import CuisineFilter

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class FilterEngine:
    """Orchestrates modular filters for restaurant data."""

    def __init__(
        self,
        location_filter: Optional[LocationFilter] = None,
        price_filter: Optional[PriceFilter] = None,
        rating_filter: Optional[RatingFilter] = None,
        cuisine_filter: Optional[CuisineFilter] = None,
    ) -> None:
        """Initialize filter engine with filter components."""
        self.location_filter = location_filter or LocationFilter()
        self.price_filter = price_filter or PriceFilter()
        self.rating_filter = rating_filter or RatingFilter()
        self.cuisine_filter = cuisine_filter or CuisineFilter()

    def filter(
        self,
        df: pd.DataFrame,
        location: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_rating: Optional[float] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        cost_min: Optional[float] = None,
        cost_max: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Apply all filters in sequence.

        Args:
            df: Restaurant DataFrame.
            location: Location filter.
            cuisine: Cuisine filter.
            min_rating: Minimum rating filter.
            price_min: Minimum price range (1-4).
            price_max: Maximum price range (1-4).
            cost_min: Minimum cost in ₹.
            cost_max: Maximum cost in ₹.

        Returns:
            Filtered DataFrame.
        """
        filtered = df.copy()
        initial_count = len(filtered)

        filtered = self.location_filter.apply(filtered, location)
        filtered = self.cuisine_filter.apply(filtered, cuisine)
        filtered = self.rating_filter.apply(filtered, min_rating)
        filtered = self.price_filter.apply(
            filtered,
            price_min=price_min,
            price_max=price_max,
            cost_min=cost_min,
            cost_max=cost_max,
        )

        logger.info(
            "Filtered %d restaurants down to %d (location=%s, cuisine=%s, "
            "min_rating=%s, price=%s-%s, cost=%s-%s)",
            initial_count,
            len(filtered),
            location,
            cuisine,
            min_rating,
            price_min,
            price_max,
            cost_min,
            cost_max,
        )

        return filtered
