"""
Tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from phase2.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Test client fixture."""
    return TestClient(app)


class TestRecommendationAPI:
    """Test suite for recommendation API endpoints."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns 200 (HTML or JSON)."""
        response = client.get("/")
        assert response.status_code == 200
        content = response.text
        # Serves frontend HTML when index.html exists, else JSON
        if content.strip().startswith("{"):
            assert "message" in response.json()
        else:
            assert "html" in content.lower() or "<!DOCTYPE" in content or "<!doctype" in content

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_recommend_endpoint_basic(self, client: TestClient) -> None:
        """Test basic recommendation request."""
        request_data = {
            "location": {"place": "Bangalore"},
            "limit": 5,
        }
        response = client.post("/api/v1/recommend", json=request_data)
        # May return 503 if Phase 1 DB not found, or 200 if found
        assert response.status_code in [200, 503]

    def test_recommend_endpoint_with_filters(self, client: TestClient) -> None:
        """Test recommendation request with filters."""
        request_data = {
            "location": {"place": "Bangalore"},
            "cuisine": "Italian",
            "minimum_rating": 4.0,
            "price_range": {"min": 2, "max": 3},
            "limit": 5,
        }
        response = client.post("/api/v1/recommend", json=request_data)
        assert response.status_code in [200, 503]

    def test_recommend_endpoint_validation_error(self, client: TestClient) -> None:
        """Test validation error handling for invalid payload."""
        # Invalid: empty place when location provided (min_length=1)
        request_data = {"location": {"place": ""}, "limit": 5}
        response = client.post("/api/v1/recommend", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_recommend_endpoint_invalid_rating(self, client: TestClient) -> None:
        """Test invalid rating validation."""
        request_data = {
            "location": {"place": "Bangalore"},
            "minimum_rating": 10.0,  # Invalid: > 5.0
        }
        response = client.post("/api/v1/recommend", json=request_data)
        assert response.status_code == 422

    def test_recommend_endpoint_invalid_price_range(self, client: TestClient) -> None:
        """Test invalid price range validation."""
        request_data = {
            "location": {"place": "Bangalore"},
            "price_range": {"min": 3, "max": 2},  # Invalid: min > max
        }
        response = client.post("/api/v1/recommend", json=request_data)
        assert response.status_code == 422
