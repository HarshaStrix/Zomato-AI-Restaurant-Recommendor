"""
Location filter for restaurant recommendations.
"""

from typing import Optional

import pandas as pd


class LocationFilter:
    """Filters restaurants by location (case-insensitive partial match)."""

    def apply(self, df: pd.DataFrame, location: Optional[str] = None) -> pd.DataFrame:
        """
        Apply location filter.

        Args:
            df: Restaurant DataFrame.
            location: Location name (case-insensitive partial match).

        Returns:
            Filtered DataFrame.
        """
        if not location or location.strip() == "":
            return df

        location_lower = location.strip().lower()
        mask = df["location"].fillna("").str.lower().str.contains(location_lower, na=False)
        return df[mask].copy()
