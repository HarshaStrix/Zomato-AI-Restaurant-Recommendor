"""Tests for DefaultExplanationGenerator (no API key required)."""

import pytest

from phase4.fallback.default_generator import DefaultExplanationGenerator


class TestDefaultExplanationGenerator:
    def test_generate_for_restaurant(self):
        gen = DefaultExplanationGenerator()
        text = gen.generate_for_restaurant("Bella Italia", rating=4.5, cuisine="Italian")
        assert "Bella Italia" in text
        assert "4.5" in text
        assert "Italian" in text

    def test_generate_summary(self):
        gen = DefaultExplanationGenerator()
        text = gen.generate_summary(location="Bangalore", cuisine="Italian", count=3)
        assert "Bangalore" in text
        assert "Italian" in text
        assert "3" in text

    def test_generate_all(self, sample_restaurants):
        gen = DefaultExplanationGenerator()
        out = gen.generate_all(sample_restaurants, location="Bangalore", cuisine="Italian")
        assert "explanations" in out
        assert "summary" in out
        assert len(out["explanations"]) == 2
        assert out["explanations"][0]["restaurant_name"] == "Bella Italia"
        assert out["explanations"][0]["explanation"]
