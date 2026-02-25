"""
Phase 4: LLM Service - generates recommendation explanations using Groq.
Orchestrates: cache check -> prompt build -> Groq call -> parse -> fallback on error.
"""

import logging
from typing import Any, Optional

from phase4.cache.llm_cache import LLMCache
from phase4.clients.groq_client import GroqClient
from phase4.config import GROQ_MAX_TOKENS, GROQ_TEMPERATURE, LOG_FORMAT, LOG_LEVEL
from phase4.fallback.default_generator import DefaultExplanationGenerator
from phase4.parsers.response_parser import ResponseParser
from phase4.prompts.prompt_builder import PromptBuilder

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class LLMService:
    """
    Generates restaurant recommendation explanations using Groq.
    Uses cache, fallback when API unavailable or on failure.
    """

    def __init__(
        self,
        client: Optional[GroqClient] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        parser: Optional[ResponseParser] = None,
        cache: Optional[LLMCache] = None,
        fallback: Optional[DefaultExplanationGenerator] = None,
    ) -> None:
        self.client = client or GroqClient()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.parser = parser or ResponseParser()
        self.cache = cache or LLMCache()
        self.fallback = fallback or DefaultExplanationGenerator()

    def generate_explanations(
        self,
        restaurants: list[dict[str, Any]],
        location: str,
        cuisine: Optional[str] = None,
        price_range: str = "",
        min_rating: Optional[float] = None,
    ) -> dict[str, Any]:
        """
        Generate explanations and summary for recommended restaurants.

        Args:
            restaurants: List of restaurant dicts (name, rating, cuisine, price_bucket, etc.).
            location: User location.
            cuisine: User cuisine preference.
            price_range: User price range string (e.g. "2-3").

        Returns:
            {
                "explanations": [{"restaurant_name": "...", "explanation": "..."}],
                "summary": "...",
                "from_cache": bool,
                "from_fallback": bool
            }
        """
        restaurant_ids = [r.get("id", r.get("name", i)) for i, r in enumerate(restaurants)]
        if not restaurants:
            return {
                "explanations": [],
                "summary": self.fallback.generate_summary(location, cuisine, 0),
                "from_cache": False,
                "from_fallback": True,
            }

        # Cache lookup (include min_rating in key for different filter combinations)
        cache_key_extra = f"r{min_rating}" if min_rating is not None else ""
        cached = self.cache.get(location, cuisine, price_range + cache_key_extra, restaurant_ids)
        if cached is not None:
            logger.info("LLM response served from cache")
            return {**cached, "from_cache": True, "from_fallback": False}

        # Try Groq
        if self.client.is_available():
            try:
                system_prompt, user_prompt = self.prompt_builder.build(
                    location, cuisine, price_range, restaurants, min_rating=min_rating
                )
                raw = self.client.complete(
                    system_prompt,
                    user_prompt,
                    temperature=GROQ_TEMPERATURE,
                    max_tokens=GROQ_MAX_TOKENS,
                )
                parsed = self.parser.parse(raw)
                result = {
                    "explanations": parsed.get("explanations", []),
                    "summary": parsed.get("summary", ""),
                    "from_cache": False,
                    "from_fallback": False,
                }
                self.cache.set(location, cuisine, price_range + cache_key_extra, restaurant_ids, result)
                return result
            except Exception as e:
                logger.warning("Groq call failed, using fallback: %s", e)

        # Fallback
        result = self.fallback.generate_all(restaurants, location, cuisine)
        result["from_cache"] = False
        result["from_fallback"] = True
        return result

    def attach_explanations_to_restaurants(
        self,
        restaurants: list[dict[str, Any]],
        result: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Add 'explanation' key to each restaurant from parsed result.
        """
        explanations = result.get("explanations", [])
        name_to_explanation = {e.get("restaurant_name", ""): e.get("explanation", "") for e in explanations if isinstance(e, dict)}

        out = []
        for r in restaurants:
            r = dict(r)
            name = r.get("name", "")
            r["explanation"] = name_to_explanation.get(name) or self.parser.get_explanation_by_name(
                {"explanations": explanations}, name
            ) or self.fallback.generate_for_restaurant(
                name, r.get("rating"), r.get("cuisine"), r.get("price_bucket")
            )
            out.append(r)
        return out
