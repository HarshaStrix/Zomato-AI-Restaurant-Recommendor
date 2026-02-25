"""Pytest fixtures for Phase 4."""

import os
import pytest

# Skip integration tests (real Groq API) when GROQ_API_KEY is not set
GROQ_API_KEY_SET = bool(os.getenv("GROQ_API_KEY", "").strip())


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "groq_integration: mark test as requiring GROQ_API_KEY (deselect with -m 'not groq_integration')",
    )


@pytest.fixture
def sample_restaurants():
    return [
        {"id": 1, "name": "Bella Italia", "rating": 4.5, "cuisine": "Italian", "price_bucket": "medium", "votes": 500},
        {"id": 2, "name": "Spice Garden", "rating": 4.2, "cuisine": "Indian", "price_bucket": "medium", "votes": 300},
    ]
