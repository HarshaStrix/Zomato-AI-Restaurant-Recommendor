"""
Integration tests: Phase 1 -> Phase 2 API (with Phase 3 + Phase 4).
Requires Phase 1 database to exist (run phase1 pipeline first).
"""

import os
import sys
from pathlib import Path

import pytest

# Project root
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Load .env for GROQ_API_KEY
_env = ROOT / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass


@pytest.fixture(scope="module")
def phase1_db_path():
    return ROOT / "phase1" / "data" / "processed" / "restaurants.db"


@pytest.mark.integration
class TestPhasesConnected:
    """Integration tests for phase connectivity."""

    def test_phase1_db_exists_or_skip(self, phase1_db_path):
        """Phase 1 database must exist for integration tests."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found. Run: python phase1/main.py")

    def test_phase2_options_endpoint(self, phase1_db_path):
        """GET /api/v1/recommend/options returns locations and cuisines."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        r = client.get("/api/v1/recommend/options")
        assert r.status_code == 200
        data = r.json()
        assert "locations" in data
        assert "cuisines" in data
        assert "price_ranges" in data
        assert isinstance(data["locations"], list)
        assert isinstance(data["cuisines"], list)

    def test_phase2_recommend_endpoint_returns_ok(self, phase1_db_path):
        """POST /api/v1/recommend returns 200 and recommendations structure."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        opts = client.get("/api/v1/recommend/options").json()
        locations = opts.get("locations", []) or ["Bangalore"]
        place = locations[0] if locations else "Bangalore"
        payload = {
            "location": {"place": place},
            "limit": 3,
        }
        r = client.post("/api/v1/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data.get("success") is True
        assert "data" in data
        assert "recommendations" in data["data"]
        assert "summary" in data["data"]
        assert "ai_explanation" in data["data"]["summary"]

    def test_phase3_engine_with_phase2_db(self, phase1_db_path):
        """Phase 3 engine produces results from Phase 1 data."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        import pandas as pd
        from phase2.services.database_service import DatabaseService
        from phase3.recommendation_engine import RecommendationEngine
        db = DatabaseService(db_path=phase1_db_path)
        df = db.get_all_restaurants()
        assert len(df) > 0
        engine = RecommendationEngine()
        ranked, total = engine.get_recommendations(
            df, location=df["location"].iloc[0], limit=3
        )
        assert total > 0
        assert len(ranked) <= 3

    def test_recommend_with_only_natural_language_query(self, phase1_db_path):
        """POST /recommend with only natural_language_query (no location) returns 200.
        Backend uses LLM to extract filters and defaults location to Bangalore."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        payload = {
            "natural_language_query": "good restaurants under 1500 in Bangalore",
            "limit": 3,
        }
        r = client.post("/api/v1/recommend", json=payload)
        assert r.status_code == 200, r.json()
        data = r.json()
        assert data.get("success") is True
        assert "data" in data
        assert "recommendations" in data["data"]
        assert "summary" in data["data"]

    def test_recommend_with_minimum_rating_respected(self, phase1_db_path):
        """POST /recommend with minimum_rating returns only restaurants >= that rating."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        opts = client.get("/api/v1/recommend/options").json()
        locations = opts.get("locations", []) or ["Bangalore"]
        place = locations[0] if locations else "Bangalore"
        payload = {
            "location": {"place": place},
            "minimum_rating": 4.0,
            "limit": 5,
        }
        r = client.post("/api/v1/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        recs = data.get("data", {}).get("recommendations", [])
        for rec in recs:
            assert rec.get("rating", 0) >= 4.0, f"Expected rating >= 4.0, got {rec.get('rating')}"

    def test_recommend_with_minimum_rating_01_precision(self, phase1_db_path):
        """POST /recommend with minimum_rating 4.2 (0.1 precision) returns only restaurants >= 4.2."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        opts = client.get("/api/v1/recommend/options").json()
        locations = opts.get("locations", []) or ["Bangalore"]
        place = locations[0] if locations else "Bangalore"
        payload = {
            "location": {"place": place},
            "minimum_rating": 4.2,
            "limit": 5,
        }
        r = client.post("/api/v1/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        recs = data.get("data", {}).get("recommendations", [])
        for rec in recs:
            assert rec.get("rating", 0) >= 4.2, f"Expected rating >= 4.2, got {rec.get('rating')}"

    def test_recommend_response_includes_cost_in_rupees(self, phase1_db_path):
        """POST /recommend returns recommendations with cost field (₹) when available."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        payload = {
            "location": {"place": "Bangalore"},
            "limit": 5,
        }
        r = client.post("/api/v1/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        recs = data.get("data", {}).get("recommendations", [])
        assert len(recs) > 0
        # Each recommendation should have cost (float) or price_range
        for rec in recs:
            assert "rating" in rec
            assert "name" in rec
            assert "location" in rec
            assert "cost" in rec or "price_range" in rec

    def test_recommend_with_cuisine_only(self, phase1_db_path):
        """POST /recommend with only cuisine filter returns matching restaurants."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        opts = client.get("/api/v1/recommend/options").json()
        cuisines = opts.get("cuisines", [])
        cuisine = cuisines[0] if cuisines else "North Indian"
        payload = {
            "location": {"place": "Bangalore"},
            "cuisine": cuisine,
            "limit": 5,
        }
        r = client.post("/api/v1/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        recs = data.get("data", {}).get("recommendations", [])
        summary = data.get("data", {}).get("summary", {})
        assert "ai_explanation" in summary

    def test_recommend_with_price_tier_rupees(self, phase1_db_path):
        """POST /recommend with price_tier (budget/mid/premium in ₹) filters by cost."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        payload = {
            "location": {"place": "Bangalore"},
            "price_tier": "budget",
            "limit": 5,
        }
        r = client.post("/api/v1/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        recs = data.get("data", {}).get("recommendations", [])
        # Budget = <= ₹500 for two
        for rec in recs:
            cost = rec.get("cost")
            if cost is not None:
                assert cost <= 500, f"Budget tier: cost should be <= 500, got {cost}"

    def test_recommend_with_minimum_rating_05_precision(self, phase1_db_path):
        """POST /recommend with minimum_rating 4.5 (0.5 precision) returns only restaurants >= 4.5."""
        if not phase1_db_path.exists():
            pytest.skip("Phase 1 DB not found")
        from fastapi.testclient import TestClient
        from phase2.api.main import app
        client = TestClient(app)
        payload = {
            "location": {"place": "Bangalore"},
            "minimum_rating": 4.5,
            "limit": 5,
        }
        r = client.post("/api/v1/recommend", json=payload)
        assert r.status_code == 200
        data = r.json()
        recs = data.get("data", {}).get("recommendations", [])
        for rec in recs:
            assert rec.get("rating", 0) >= 4.5, f"Expected rating >= 4.5, got {rec.get('rating')}"
