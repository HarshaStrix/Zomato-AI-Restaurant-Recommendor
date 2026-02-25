"""
Ranker for sorting and limiting restaurant results.
Handles tie-breaking and edge cases.
"""

import logging
from typing import Optional

import pandas as pd

from phase3.config import TIE_BREAK_COLUMNS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Ranker:
    """Ranks restaurants by score with tie-breaking."""

    def __init__(self, tie_break_columns: Optional[list[str]] = None) -> None:
        """
        Initialize ranker.

        Args:
            tie_break_columns: Columns for tie-breaking (secondary sort).
        """
        self.tie_break_columns = tie_break_columns or TIE_BREAK_COLUMNS

    def rank(
        self,
        df: pd.DataFrame,
        limit: int = 5,
        ascending: bool = False,
    ) -> pd.DataFrame:
        """
        Sort by score and return top N results with tie-breaking.

        Args:
            df: DataFrame with 'score' column.
            limit: Maximum number of results.
            ascending: Sort order for score.

        Returns:
            Top N ranked DataFrame.
        """
        if len(df) == 0:
            return df

        if "score" not in df.columns:
            logger.warning("No 'score' column found, returning unsorted")
            return df.head(limit)

        df = df.copy()

        # Build sort columns
        sort_cols = ["score"]
        for col in self.tie_break_columns:
            if col in df.columns and col != "score":
                sort_cols.append(col)

        # Fill NaN for tie-break columns
        for col in sort_cols[1:]:
            if col in df.columns:
                if df[col].dtype in ["object", "string"]:
                    df[col] = df[col].fillna("")
                else:
                    df[col] = df[col].fillna(0)

        # Sort: score desc, then rating desc, votes desc, name asc (deterministic)
        asc_flags = []
        for col in sort_cols:
            asc_flags.append(True if col == "name" else (ascending if col == "score" else False))

        df = df.sort_values(by=sort_cols, ascending=asc_flags)

        result = df.head(limit).copy()

        # Drop intermediate score columns if present
        drop_cols = ["rating_score", "price_score", "cuisine_score", "popularity_score", "proximity_score"]
        result = result.drop(columns=[c for c in drop_cols if c in result.columns], errors="ignore")

        logger.info("Ranked and selected top %d of %d restaurants", len(result), len(df))
        return result
