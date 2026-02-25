"""
Tests for preprocessing (cleaning and feature engineering).
Validates cleaning, price_bucket creation, and database insert.
"""

from pathlib import Path

import pandas as pd
import pytest

from backend.preprocessing.cleaner import DataCleaner
from backend.preprocessing.feature_engineering import FeatureEngineer
from backend.database.db_manager import DatabaseManager
from backend.config import PRICE_BUCKET_LABELS


class TestDataCleaner:
    """Test suite for DataCleaner."""

    def test_clean_removes_nulls_in_critical_columns(
        self, sample_raw_dataframe_with_nulls: pd.DataFrame
    ) -> None:
        """Cleaning should handle or remove rows with null critical data."""
        # Map to expected column names
        df = sample_raw_dataframe_with_nulls.rename(
            columns={
                "cuisines": "cuisine",
                "rate": "rating",
                "approx_cost(for_two)": "cost",
            }
        )
        df = df[["name", "cuisine", "location", "rating", "cost", "votes"]]

        cleaner = DataCleaner()
        result = cleaner.clean(df)

        # Should have valid rows (at least name or location non-empty)
        assert len(result) >= 1
        assert "rating" in result.columns
        assert result["rating"].notna().all()

    def test_clean_normalizes_cuisines(self, sample_raw_dataframe: pd.DataFrame) -> None:
        """Cuisines should be normalized to list format."""
        df = sample_raw_dataframe.rename(
            columns={
                "cuisines": "cuisine",
                "rate": "rating",
                "approx_cost(for_two)": "cost",
            }
        )
        df = df[["name", "cuisine", "location", "rating", "cost", "votes"]]

        cleaner = DataCleaner()
        result = cleaner.clean(df)

        assert "cuisine_list" in result.columns
        assert all(isinstance(x, list) for x in result["cuisine_list"])
        # First row: "Italian, Pizza" -> ["italian", "pizza"]
        first_cuisines = result["cuisine_list"].iloc[0]
        assert "italian" in first_cuisines
        assert "pizza" in first_cuisines

    def test_clean_parses_rating_formats(self) -> None:
        """Rating parsing handles '4.2/5', float, 'NEW', etc."""
        df = pd.DataFrame(
            {
                "name": ["A", "B", "C"],
                "cuisine": ["Italian", "Indian", "Cafe"],
                "location": ["X", "Y", "Z"],
                "rating": ["4.2/5", 4.5, "NEW"],
                "cost": [500, 800, 400],
            }
        )
        cleaner = DataCleaner()
        result = cleaner.clean(df)
        assert result["rating"].iloc[0] == 4.2
        assert result["rating"].iloc[1] == 4.5
        assert result["rating"].iloc[2] == 0.0  # NEW -> default

    def test_clean_removes_duplicates(self, sample_raw_dataframe: pd.DataFrame) -> None:
        """Duplicate rows should be removed."""
        df = sample_raw_dataframe.rename(
            columns={
                "cuisines": "cuisine",
                "rate": "rating",
                "approx_cost(for_two)": "cost",
            }
        )
        df = df[["name", "cuisine", "location", "rating", "cost", "votes"]]
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)  # Add duplicate

        cleaner = DataCleaner()
        result = cleaner.clean(df)
        assert len(result) == 5  # Duplicate removed


class TestFeatureEngineer:
    """Test suite for FeatureEngineer."""

    def test_price_bucket_created_correctly(self) -> None:
        """price_bucket should be low/medium/high based on cost."""
        df = pd.DataFrame(
            {
                "name": ["A", "B", "C"],
                "cuisine": ["Italian", "Indian", "Cafe"],
                "cuisine_list": [["italian"], ["indian"], ["cafe"]],
                "location": ["X", "Y", "Z"],
                "rating": [4.0, 4.5, 3.5],
                "cost": [400, 1000, 2000],  # low, medium, high
            }
        )
        engineer = FeatureEngineer(
            low_max=500,
            medium_max=1500,
        )
        result = engineer.transform(df)

        assert "price_bucket" in result.columns
        assert result["price_bucket"].iloc[0] == "low"
        assert result["price_bucket"].iloc[1] == "medium"
        assert result["price_bucket"].iloc[2] == "high"

    def test_normalized_rating_created(self) -> None:
        """normalized_rating should be 0-1 scale."""
        df = pd.DataFrame(
            {
                "name": ["A"],
                "cuisine": ["Italian"],
                "cuisine_list": [["italian"]],
                "location": ["X"],
                "rating": [4.0],
                "cost": [500],
            }
        )
        engineer = FeatureEngineer()
        result = engineer.transform(df)
        assert "normalized_rating" in result.columns
        assert result["normalized_rating"].iloc[0] == pytest.approx(0.8)  # 4/5

    def test_cuisine_list_exists(self) -> None:
        """cuisine_list column should exist after transform."""
        df = pd.DataFrame(
            {
                "name": ["A"],
                "cuisine": ["Italian, Pizza"],
                "location": ["X"],
                "rating": [4.0],
                "cost": [500],
            }
        )
        engineer = FeatureEngineer()
        result = engineer.transform(df)
        assert "cuisine_list" in result.columns


class TestDatabaseManager:
    """Test suite for DatabaseManager."""

    def test_data_inserted_into_sqlite(
        self, temp_db_path: Path, sample_raw_dataframe: pd.DataFrame
    ) -> None:
        """Processed data should be inserted into SQLite."""
        df = sample_raw_dataframe.rename(
            columns={
                "cuisines": "cuisine",
                "rate": "rating",
                "approx_cost(for_two)": "cost",
            }
        )
        cleaner = DataCleaner()
        engineer = FeatureEngineer()
        df_clean = cleaner.clean(df)
        df_processed = engineer.transform(df_clean)

        db = DatabaseManager(db_path=temp_db_path)
        db.create_table()
        rows = db.insert_dataframe(df_processed)
        db.close()

        assert rows > 0

    def test_row_count_after_insert(
        self, temp_db_path: Path, sample_raw_dataframe: pd.DataFrame
    ) -> None:
        """Row count in database should match inserted rows."""
        df = sample_raw_dataframe.rename(
            columns={
                "cuisines": "cuisine",
                "rate": "rating",
                "approx_cost(for_two)": "cost",
            }
        )
        cleaner = DataCleaner()
        engineer = FeatureEngineer()
        df_clean = cleaner.clean(df)
        df_processed = engineer.transform(df_clean)

        db = DatabaseManager(db_path=temp_db_path)
        db.create_table()
        rows_inserted = db.insert_dataframe(df_processed)
        count = db.get_row_count()
        db.close()

        assert count == rows_inserted
        assert count > 0
