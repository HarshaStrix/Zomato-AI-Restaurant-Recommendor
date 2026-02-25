"""
Database Manager for storing processed restaurant data in SQLite.
Creates tables, indexes, and handles insert operations.
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from phase1.config import (
    DATABASE_PATH,
    DATABASE_TABLE,
    LOG_FORMAT,
    LOG_LEVEL,
)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for restaurant data."""

    def __init__(self, db_path: Path = DATABASE_PATH) -> None:
        """
        Initialize the database manager.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self._connection = None

    def _get_connection(self):
        """Get or create database connection."""
        import sqlite3

        if self._connection is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def create_table(self, if_not_exists: bool = True) -> None:
        """
        Create the restaurants table and indexes.

        Args:
            if_not_exists: If True, use CREATE TABLE IF NOT EXISTS.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""

        cursor.execute(
            f"""
            CREATE TABLE {if_not_exists_clause}{DATABASE_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                cuisine TEXT,
                cuisine_list TEXT,
                rating REAL,
                cost REAL,
                price_bucket TEXT,
                normalized_rating REAL,
                votes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create indexes
        for idx_name, col in [
            ("idx_location", "location"),
            ("idx_cuisine", "cuisine"),
            ("idx_rating", "rating"),
        ]:
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} "
                f"ON {DATABASE_TABLE} ({col})"
            )

        conn.commit()
        logger.info("Created table %s with indexes", DATABASE_TABLE)

    def insert_dataframe(self, df: pd.DataFrame) -> int:
        """
        Insert DataFrame into the restaurants table.

        Args:
            df: Processed DataFrame with restaurant data.

        Returns:
            Number of rows inserted.
        """
        conn = self._get_connection()

        # Ensure cuisine_list is stored as string (pipe-separated)
        df_insert = df.copy()
        if "cuisine_list" in df_insert.columns:
            df_insert["cuisine_list"] = df_insert["cuisine_list"].apply(
                lambda x: "|".join(x) if isinstance(x, list) else str(x) if x else ""
            )
        else:
            df_insert["cuisine_list"] = ""

        # Select columns that exist in our schema
        schema_cols = [
            "name",
            "location",
            "cuisine",
            "cuisine_list",
            "rating",
            "cost",
            "price_bucket",
            "normalized_rating",
            "votes",
        ]
        available = [c for c in schema_cols if c in df_insert.columns]
        df_insert = df_insert[available]

        # Fill missing columns
        for col in schema_cols:
            if col not in df_insert.columns:
                if col == "votes":
                    df_insert[col] = 0
                else:
                    df_insert[col] = None

        df_insert = df_insert[schema_cols]
        df_insert = df_insert.where(pd.notna(df_insert), None)

        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {DATABASE_TABLE}")
        conn.commit()

        insert_sql = (
            f"INSERT INTO {DATABASE_TABLE} "
            f"({', '.join(schema_cols)}) "
            f"VALUES ({', '.join(['?' for _ in schema_cols])})"
        )

        rows = list(df_insert.itertuples(index=False, name=None))
        cursor.executemany(insert_sql, rows)
        conn.commit()

        count = cursor.rowcount
        if count == -1:
            count = len(rows)
        logger.info("Inserted %d rows into %s", len(rows), DATABASE_TABLE)
        return len(rows)

    def get_row_count(self) -> int:
        """
        Get the number of rows in the restaurants table.

        Returns:
            Row count.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {DATABASE_TABLE}")
        return cursor.fetchone()[0]

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Closed database connection")
