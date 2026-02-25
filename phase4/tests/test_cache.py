"""Tests for LLMCache (no API key required)."""

import pytest

from phase4.cache.llm_cache import LLMCache


class TestLLMCache:
    def test_set_and_get(self):
        cache = LLMCache(ttl_seconds=60, enabled=True)
        cache.set("Bangalore", "Italian", "2-3", [1, 2], {"explanations": [], "summary": "Cached"})
        out = cache.get("Bangalore", "Italian", "2-3", [1, 2])
        assert out is not None
        assert out["summary"] == "Cached"

    def test_different_key_misses(self):
        cache = LLMCache(ttl_seconds=60, enabled=True)
        cache.set("Bangalore", "Italian", "2-3", [1, 2], {"explanations": [], "summary": "x"})
        assert cache.get("Mumbai", "Italian", "2-3", [1, 2]) is None
        assert cache.get("Bangalore", "Indian", "2-3", [1, 2]) is None

    def test_disabled_returns_none(self):
        cache = LLMCache(enabled=False)
        cache.set("Bangalore", None, "", [1], {"summary": "x"})
        assert cache.get("Bangalore", None, "", [1]) is None
