"""
Price filter for restaurant recommendations.
Supports both bucket (1-4) and cost in rupees (cost_min/cost_max).
"""

from typing import Optional

import pandas as pd

from phase3.config import PRICE_BUCKET_MAP


class PriceFilter:
    """Filters restaurants by price range (1-4) and/or cost in rupees."""

    def apply(
        self,
        df: pd.DataFrame,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        cost_min: Optional[float] = None,
        cost_max: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Apply price filter. When cost_min/cost_max are set, filter by cost (₹);
        otherwise use price_bucket (1-4).

        Args:
            df: Restaurant DataFrame (price_bucket and/or cost column).
            price_min: Minimum price range (1-4).
            price_max: Maximum price range (1-4).
            cost_min: Minimum cost for two (rupees).
            cost_max: Maximum cost for two (rupees).

        Returns:
            Filtered DataFrame.
        """
        result = df.copy()

        # Cost-based filter (Budget <=500, Mid 500-1500, Premium >1500)
        if cost_min is not None or cost_max is not None:
            if "cost" in result.columns:
                cost = pd.to_numeric(result["cost"], errors="coerce")
                mask = pd.Series(True, index=result.index)
                if cost_min is not None:
                    mask = mask & (cost >= cost_min)
                if cost_max is not None:
                    mask = mask & (cost <= cost_max)
                result = result[mask]
            return result

        # Bucket-based filter (1-4)
        if price_min is None and price_max is None:
            return result
        if "price_bucket" not in result.columns:
            return result

        result["_price_numeric"] = result["price_bucket"].map(PRICE_BUCKET_MAP).fillna(2)
        if price_min is not None and price_max is not None:
            mask = (result["_price_numeric"] >= price_min) & (result["_price_numeric"] <= price_max)
        elif price_min is not None:
            mask = result["_price_numeric"] >= price_min
        else:
            mask = result["_price_numeric"] <= price_max
        result = result[mask].drop(columns=["_price_numeric"], errors="ignore")
        return result
