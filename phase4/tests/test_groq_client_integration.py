"""
Integration tests for GroqClient.
Run only when GROQ_API_KEY is set: pytest -m groq_integration
Skip by default: pytest -m "not groq_integration"
"""

import os
import pytest

pytestmark = pytest.mark.groq_integration


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY", "").strip(), reason="GROQ_API_KEY not set")
class TestGroqClientIntegration:
    """Real Groq API calls; require GROQ_API_KEY."""

    def test_is_available_when_key_set(self):
        from phase4.clients.groq_client import GroqClient

        client = GroqClient()
        assert client.is_available() is True

    def test_complete_returns_non_empty_string(self):
        from phase4.clients.groq_client import GroqClient

        client = GroqClient()
        if not client.is_available():
            pytest.skip("GROQ_API_KEY not set")
        response = client.complete(
            system_prompt="You are helpful. Reply in one short sentence.",
            user_prompt="What is 2+2? Say only the number.",
            max_tokens=10,
        )
        assert isinstance(response, str)
        assert len(response.strip()) > 0
