"""
Database service for querying restaurant data from Phase 1 SQLite database.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd

from phase2.config import PHASE1_DB_PATH, LOG_FORMAT, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for querying restaurant database."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize database service.

        Args:
            db_path: Path to SQLite database. Defaults to Phase 1 database.
        """
        self.db_path = Path(db_path) if db_path else PHASE1_DB_PATH
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found at {self.db_path}. "
                "Please run Phase 1 pipeline first."
            )

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_restaurants(self) -> pd.DataFrame:
        """
        Get all restaurants from database.

        Returns:
            DataFrame with all restaurants.
        """
        conn = self._get_connection()
        try:
            df = pd.read_sql_query("SELECT * FROM restaurants", conn)
            logger.info("Loaded %d restaurants from database", len(df))
            return df
        finally:
            conn.close()

    def get_restaurants_by_location(
        self, location: str, limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get restaurants filtered by location.

        Args:
            location: Location name (case-insensitive partial match).
            limit: Optional limit on results.

        Returns:
            DataFrame with filtered restaurants.
        """
        conn = self._get_connection()
        try:
            query = "SELECT * FROM restaurants WHERE LOWER(location) LIKE ?"
            params = [f"%{location.lower()}%"]
            if limit:
                query += f" LIMIT {limit}"
            df = pd.read_sql_query(query, conn, params=params)
            logger.info("Found %d restaurants in location '%s'", len(df), location)
            return df
        finally:
            conn.close()

    def get_restaurants_by_criteria(
        self,
        location: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_rating: Optional[float] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get restaurants filtered by multiple criteria.

        Args:
            location: Location filter (case-insensitive partial match).
            cuisine: Cuisine filter (case-insensitive partial match).
            min_rating: Minimum rating filter.
            price_min: Minimum price range (1-4).
            price_max: Maximum price range (1-4).

        Returns:
            DataFrame with filtered restaurants.
        """
        conn = self._get_connection()
        try:
            conditions = []
            params = []

            if location:
                conditions.append("LOWER(location) LIKE ?")
                params.append(f"%{location.lower()}%")

            if cuisine:
                conditions.append(
                    "(LOWER(cuisine) LIKE ? OR LOWER(cuisine_list) LIKE ?)"
                )
                params.extend([f"%{cuisine.lower()}%", f"%{cuisine.lower()}%"])

            if min_rating is not None:
                conditions.append("rating >= ?")
                params.append(min_rating)

            if price_min is not None:
                conditions.append("price_bucket IN (?, ?, ?)")
                # Map price range 1-4 to buckets
                buckets = []
                if price_min <= 1:
                    buckets.extend(["low", "medium", "high"])
                elif price_min == 2:
                    buckets.extend(["medium", "high"])
                elif price_min == 3:
                    buckets.extend(["high"])
                params.extend(buckets)

            if price_max is not None:
                # Refine price filter if both min and max provided
                if price_min is None:
                    conditions.append("price_bucket IN (?, ?, ?)")
                    buckets = []
                    if price_max >= 4:
                        buckets.extend(["low", "medium", "high"])
                    elif price_max == 3:
                        buckets.extend(["low", "medium"])
                    elif price_max == 2:
                        buckets.extend(["low"])
                    params.extend(buckets)

            query = "SELECT * FROM restaurants"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            df = pd.read_sql_query(query, conn, params=params)
            logger.info(
                "Found %d restaurants matching criteria (location=%s, cuisine=%s, "
                "min_rating=%s, price=%s-%s)",
                len(df),
                location,
                cuisine,
                min_rating,
                price_min,
                price_max,
            )
            return df
        finally:
            conn.close()
