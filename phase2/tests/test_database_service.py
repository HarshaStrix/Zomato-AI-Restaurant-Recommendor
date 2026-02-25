"""
Tests for DatabaseService.
"""

import pytest

from phase2.services.database_service import DatabaseService


class TestDatabaseService:
    """Test suite for DatabaseService."""

    def test_get_all_restaurants(self, db_service: DatabaseService) -> None:
        """Test retrieving all restaurants."""
        df = db_service.get_all_restaurants()
        assert len(df) == 5
        assert "name" in df.columns
        assert "location" in df.columns

    def test_get_restaurants_by_location(
        self, db_service: DatabaseService
    ) -> None:
        """Test filtering by location."""
        df = db_service.get_restaurants_by_location("Bangalore")
        assert len(df) == 3
        assert all("bangalore" in loc.lower() for loc in df["location"])

    def test_get_restaurants_by_criteria(
        self, db_service: DatabaseService
    ) -> None:
        """Test filtering by multiple criteria."""
        # Location + cuisine
        df = db_service.get_restaurants_by_criteria(
            location="Bangalore", cuisine="Italian"
        )
        assert len(df) == 2

        # Rating filter
        df = db_service.get_restaurants_by_criteria(min_rating=4.0)
        assert len(df) == 4
        assert all(df["rating"] >= 4.0)

    def test_database_not_found(self, tmp_path) -> None:
        """Test error when database doesn't exist."""
        db_path = tmp_path / "nonexistent.db"
        with pytest.raises(FileNotFoundError):
            DatabaseService(db_path=db_path)
