"""
Tests for RecommendationService.
"""

import pytest

from phase2.services.recommendation_service import RecommendationService


class TestRecommendationService:
    """Test suite for RecommendationService."""

    def test_get_recommendations_basic(self, db_service) -> None:
        """Test basic recommendation retrieval."""
        service = RecommendationService(db_service=db_service)
        recommendations, total, _ = service.get_recommendations(
            location="Bangalore", limit=5
        )
        assert total >= 0
        assert len(recommendations) <= 5

    def test_get_recommendations_with_filters(self, db_service) -> None:
        """Test recommendations with filters."""
        service = RecommendationService(db_service=db_service)
        recommendations, total, _ = service.get_recommendations(
            location="Bangalore",
            cuisine="Italian",
            min_rating=4.0,
            limit=5,
        )
        assert total >= 0
        if len(recommendations) > 0:
            assert all("italian" in str(c).lower() for c in recommendations["cuisine"])

    def test_get_recommendations_limit(self, db_service) -> None:
        """Test recommendation limit."""
        service = RecommendationService(db_service=db_service)
        recommendations, _, _ = service.get_recommendations(
            location="Bangalore", limit=2
        )
        assert len(recommendations) <= 2

    def test_no_results(self, db_service) -> None:
        """Test handling when no restaurants match."""
        service = RecommendationService(db_service=db_service)
        recommendations, total, _ = service.get_recommendations(
            location="NonexistentCity", limit=5
        )
        assert total == 0
        assert len(recommendations) == 0
