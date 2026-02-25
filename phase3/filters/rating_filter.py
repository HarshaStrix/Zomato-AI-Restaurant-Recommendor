"""
Rating filter for restaurant recommendations.
"""

from typing import Optional

import pandas as pd


class RatingFilter:
    """Filters restaurants by minimum rating."""

    def apply(self, df: pd.DataFrame, min_rating: Optional[float] = None) -> pd.DataFrame:
        """
        Apply minimum rating filter.

        Args:
            df: Restaurant DataFrame.
            min_rating: Minimum rating threshold (0-5).

        Returns:
            Filtered DataFrame.
        """
        if min_rating is None:
            return df

        if "rating" not in df.columns:
            return df

        df = df.copy()
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
        return df[df["rating"] >= min_rating].copy()
