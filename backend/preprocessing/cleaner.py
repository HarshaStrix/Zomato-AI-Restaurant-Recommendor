"""
Data Cleaner for Zomato restaurant data.
Handles missing values, normalization, and deduplication.
"""

import logging
import re
from typing import Optional

import pandas as pd

from backend.config import (
    DEFAULT_RATING,
    MAX_RATING,
    MIN_RATING,
    LOG_FORMAT,
    LOG_LEVEL,
)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans and normalizes restaurant data."""

    def __init__(
        self,
        default_rating: float = DEFAULT_RATING,
        min_rating: float = MIN_RATING,
        max_rating: float = MAX_RATING,
    ) -> None:
        """
        Initialize the data cleaner.

        Args:
            default_rating: Rating to use when value is missing/invalid.
            min_rating: Minimum valid rating.
            max_rating: Maximum valid rating.
        """
        self.default_rating = default_rating
        self.min_rating = min_rating
        self.max_rating = max_rating

    @staticmethod
    def _parse_rating(value: Optional[object]) -> Optional[float]:
        """
        Parse rating from various formats (e.g., '4.2/5', '4.2', 'NEW').

        Args:
            value: Raw rating value.

        Returns:
            Float rating or None if unparseable.
        """
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        if isinstance(value, (int, float)) and not pd.isna(value):
            try:
                v = float(value)
                if 0 <= v <= 5:
                    return round(v, 2)
            except (TypeError, ValueError):
                pass
            return None
        s = str(value).strip().upper()
        if s in ("NEW", "NA", "-", ""):
            return None
        # Match "4.2" or "4.2/5"
        match = re.search(r"([0-9]+\.?[0-9]*)\s*/?\s*5?", s)
        if match:
            try:
                v = float(match.group(1))
                if 0 <= v <= 5:
                    return round(v, 2)
            except ValueError:
                pass
        return None

    @staticmethod
    def _parse_cost(value: Optional[object]) -> Optional[float]:
        """
        Parse cost from string (e.g., '1,200' or '1200').

        Args:
            value: Raw cost value.

        Returns:
            Float cost or None if unparseable.
        """
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        if isinstance(value, (int, float)) and not pd.isna(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        s = str(value).strip().replace(",", "")
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def _normalize_cuisines(cuisine: Optional[object]) -> list[str]:
        """
        Normalize cuisine string to list of lowercase cuisine names.

        Args:
            cuisine: Raw cuisine value (string or list).

        Returns:
            List of normalized cuisine strings.
        """
        if cuisine is None or (isinstance(cuisine, float) and pd.isna(cuisine)):
            return []
        if isinstance(cuisine, list):
            return [
                str(c).strip().lower()
                for c in cuisine
                if c and str(c).strip()
            ]
        s = str(cuisine).strip()
        if not s:
            return []
        # Split by comma, &, or |
        parts = re.split(r"[,|&]", s)
        return [
            p.strip().lower()
            for p in parts
            if p.strip()
        ]

    @staticmethod
    def _normalize_location(loc: Optional[object]) -> str:
        """
        Normalize location name.

        Args:
            loc: Raw location value.

        Returns:
            Normalized location string.
        """
        if loc is None or (isinstance(loc, float) and pd.isna(loc)):
            return ""
        s = str(loc).strip()
        return " ".join(s.split()) if s else ""

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize the DataFrame.

        Args:
            df: Raw DataFrame from dataset loader.

        Returns:
            Cleaned DataFrame with normalized columns.
        """
        logger.info("Starting data cleaning on %d rows", len(df))
        df = df.copy()

        # Ensure required columns exist
        required = ["name", "cuisine", "location", "rating", "cost"]
        for col in required:
            if col not in df.columns:
                df[col] = None

        # Parse and clean rating
        if "rating" in df.columns:
            df["rating"] = df["rating"].apply(
                lambda x: self._parse_rating(x) or self.default_rating
            )
            df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
            df["rating"] = df["rating"].clip(
                lower=self.min_rating, upper=self.max_rating
            )
            df["rating"] = df["rating"].fillna(self.default_rating)
        logger.info("Cleaned rating column")

        # Parse and clean cost
        if "cost" in df.columns:
            df["cost"] = df["cost"].apply(self._parse_cost)
        logger.info("Cleaned cost column")

        # Normalize cuisines and create cuisine_list
        if "cuisine" in df.columns:
            df["cuisine_list"] = df["cuisine"].apply(self._normalize_cuisines)
            df["cuisine"] = df["cuisine_list"].apply(
                lambda x: ", ".join(x) if x else ""
            )
        logger.info("Cleaned cuisine column")

        # Normalize location
        if "location" in df.columns:
            df["location"] = df["location"].apply(self._normalize_location)
        logger.info("Cleaned location column")

        # Normalize name
        if "name" in df.columns:
            df["name"] = df["name"].fillna("").apply(
                lambda x: str(x).strip() if x is not None else ""
            )

        # Remove rows with critical missing data
        before_drop = len(df)
        df = df.dropna(subset=["name", "location"], how="all")
        # Keep rows that have at least name or location
        df = df[~((df["name"] == "") & (df["location"] == ""))]
        dropped = before_drop - len(df)
        if dropped > 0:
            logger.info("Dropped %d rows with missing name and location", dropped)

        # Remove duplicates
        before_dedup = len(df)
        df = df.drop_duplicates(
            subset=["name", "location", "cuisine"],
            keep="first",
        )
        deduped = before_dedup - len(df)
        if deduped > 0:
            logger.info("Removed %d duplicate rows", deduped)

        logger.info("Cleaning complete. %d rows remaining", len(df))
        return df
