"""
In-memory cache for LLM responses (MVP).
Redis can be added later for production.
"""

import hashlib
import json
import logging
import time
from typing import Any, Optional

from phase4.config import LLM_CACHE_ENABLED, LLM_CACHE_TTL_SECONDS

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class LLMCache:
    """In-memory TTL cache for LLM explanation responses."""

    def __init__(
        self,
        ttl_seconds: int = LLM_CACHE_TTL_SECONDS,
        enabled: bool = LLM_CACHE_ENABLED,
    ) -> None:
        self.ttl = ttl_seconds
        self.enabled = enabled
        self._store: dict[str, tuple[Any, float]] = {}

    def _make_key(self, location: str, cuisine: Optional[str], price_range: str, restaurant_ids: list[Any]) -> str:
        """Generate cache key from query context."""
        payload = f"{location}|{cuisine or ''}|{price_range}|{sorted(restaurant_ids)}"
        return hashlib.md5(payload.encode()).hexdigest()

    def get(
        self,
        location: str,
        cuisine: Optional[str],
        price_range: str,
        restaurant_ids: list[Any],
    ) -> Optional[dict[str, Any]]:
        """Get cached response if present and not expired."""
        if not self.enabled:
            return None
        key = self._make_key(location, cuisine, price_range, restaurant_ids)
        if key not in self._store:
            return None
        data, expires = self._store[key]
        if time.time() > expires:
            del self._store[key]
            return None
        return data

    def set(
        self,
        location: str,
        cuisine: Optional[str],
        price_range: str,
        restaurant_ids: list[Any],
        value: dict[str, Any],
    ) -> None:
        """Store response in cache."""
        if not self.enabled:
            return
        key = self._make_key(location, cuisine, price_range, restaurant_ids)
        self._store[key] = (value, time.time() + self.ttl)
        logger.debug("LLM cache set: key=%s", key[:8])
