"""Tests for PromptBuilder (no API key required)."""

import pytest

from phase4.prompts.prompt_builder import PromptBuilder
from phase4.prompts.templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class TestPromptBuilder:
    def test_build_restaurant_list(self):
        builder = PromptBuilder()
        restaurants = [
            {"name": "A", "rating": 4.5, "cuisine": "Italian", "price_bucket": "medium", "votes": 100},
        ]
        text = builder.build_restaurant_list(restaurants)
        assert "A" in text
        assert "4.5" in text
        assert "Italian" in text

    def test_build_returns_system_and_user_prompt(self, sample_restaurants):
        builder = PromptBuilder()
        system, user = builder.build(
            location="Bangalore",
            cuisine="Italian",
            price_range="2-3",
            restaurants=sample_restaurants,
        )
        assert system == SYSTEM_PROMPT
        assert "Bangalore" in user
        assert "Italian" in user
        assert "2-3" in user
        assert "Bella Italia" in user
