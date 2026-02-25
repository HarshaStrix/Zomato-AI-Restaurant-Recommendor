"""Tests for ResponseParser (no API key required)."""

import pytest

from phase4.parsers.response_parser import ResponseParser


class TestResponseParser:
    def test_parse_valid_json(self):
        parser = ResponseParser()
        raw = '{"explanations": [{"restaurant_name": "A", "explanation": "Great food."}], "summary": "Summary here."}'
        out = parser.parse(raw)
        assert out["summary"] == "Summary here."
        assert len(out["explanations"]) == 1
        assert out["explanations"][0]["restaurant_name"] == "A"
        assert out["explanations"][0]["explanation"] == "Great food."

    def test_parse_json_inside_markdown(self):
        parser = ResponseParser()
        raw = '```json\n{"explanations": [], "summary": "Done."}\n```'
        out = parser.parse(raw)
        assert out["summary"] == "Done."
        assert out["explanations"] == []

    def test_parse_empty_returns_fallback(self):
        parser = ResponseParser()
        out = parser.parse("")
        assert "summary" in out
        assert "explanations" in out
        assert out["explanations"] == []

    def test_get_explanation_by_name(self):
        parser = ResponseParser()
        parsed = {
            "explanations": [
                {"restaurant_name": "Bella Italia", "explanation": "Best Italian."},
            ],
            "summary": "Ok",
        }
        assert parser.get_explanation_by_name(parsed, "Bella Italia") == "Best Italian."
        assert parser.get_explanation_by_name(parsed, "Unknown") is None
