"""
Cuisine filter for restaurant recommendations.
"""

from typing import Optional

import pandas as pd


class CuisineFilter:
    """Filters restaurants by cuisine type (case-insensitive partial match)."""

    def apply(self, df: pd.DataFrame, cuisine: Optional[str] = None) -> pd.DataFrame:
        """
        Apply cuisine filter.

        Args:
            df: Restaurant DataFrame with cuisine and/or cuisine_list columns.
            cuisine: Cuisine type (case-insensitive partial match).

        Returns:
            Filtered DataFrame.
        """
        if not cuisine or cuisine.strip() == "":
            return df

        cuisine_lower = cuisine.strip().lower()

        if "cuisine" in df.columns:
            cuisine_match = df["cuisine"].fillna("").str.lower().str.contains(cuisine_lower, na=False)
        else:
            cuisine_match = pd.Series([False] * len(df), index=df.index)

        if "cuisine_list" in df.columns:
            list_match = df["cuisine_list"].astype(str).str.lower().str.contains(cuisine_lower, na=False)
        else:
            list_match = pd.Series([False] * len(df), index=df.index)

        mask = cuisine_match | list_match
        return df[mask].copy()
