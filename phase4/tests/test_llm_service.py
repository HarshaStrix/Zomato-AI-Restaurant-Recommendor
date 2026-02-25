"""Tests for LLMService. Use fallback when GROQ_API_KEY not set."""

import pytest

from phase4.llm_service import LLMService


class TestLLMService:
    def test_generate_explanations_empty_restaurants(self):
        service = LLMService()
        out = service.generate_explanations([], "Bangalore", "Italian", "2-3")
        assert out["explanations"] == []
        assert "summary" in out
        assert out["from_fallback"] is True

    def test_generate_explanations_uses_fallback_when_no_client(self, sample_restaurants):
        # Without GROQ_API_KEY, client.is_available() is False -> fallback
        service = LLMService()
        out = service.generate_explanations(
            sample_restaurants,
            location="Bangalore",
            cuisine="Italian",
            price_range="2-3",
        )
        assert "explanations" in out
        assert "summary" in out
        assert len(out["explanations"]) == 2
        assert out["explanations"][0]["restaurant_name"] == "Bella Italia"
        assert out["explanations"][0]["explanation"]
        assert out["from_fallback"] is True or out["from_cache"] is True

    def test_attach_explanations_to_restaurants(self, sample_restaurants):
        service = LLMService()
        result = {
            "explanations": [
                {"restaurant_name": "Bella Italia", "explanation": "Great Italian food."},
                {"restaurant_name": "Spice Garden", "explanation": "Best Indian."},
            ],
            "summary": "Two options.",
        }
        attached = service.attach_explanations_to_restaurants(sample_restaurants, result)
        assert len(attached) == 2
        assert attached[0]["explanation"] == "Great Italian food."
        assert attached[1]["explanation"] == "Best Indian."
