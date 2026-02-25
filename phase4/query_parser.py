"""
Phase 4: Natural language query parser.
Uses Groq to extract structured filters from user text (e.g. "romantic place for dinner under ₹1500").
"""

import json
import logging
import re
from typing import Any, Optional

from phase4.config import GROQ_MAX_TOKENS, GROQ_TEMPERATURE, LOG_FORMAT, LOG_LEVEL
from phase4.clients.groq_client import GroqClient

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

QUERY_PARSE_SYSTEM = """You are a filter extractor for a restaurant recommendation system in Bangalore, India.
Given the user's message, extract structured filters. Return ONLY a valid JSON object, no other text.
Use this exact schema (use null for missing values):
{
  "location": "string or null (e.g. Bangalore, Koramangala)",
  "cuisine": "string or null (e.g. Italian, North Indian)",
  "cost_max": number or null (max budget in rupees for two people, e.g. 1500),
  "cost_min": number or null (min budget if mentioned),
  "min_rating": number or null (0-5 scale, e.g. 4.0)
}
Rules: Interpret "under ₹1500" as cost_max 1500. "Budget" or "cheap" -> cost_max 500. "Premium" or "splurge" -> cost_min 1500.
If only a city/area is mentioned, set location. Do not invent values; use null when unclear."""

QUERY_PARSE_USER = 'User message: "{query}"\n\nExtract filters as JSON:'


def parse_natural_language_query(
    query: str,
    client: Optional[GroqClient] = None,
) -> dict[str, Any]:
    """
    Parse natural language into structured filters using Groq.

    Args:
        query: User message (e.g. "I want a romantic place for dinner under ₹1500").
        client: Optional Groq client (for testing).

    Returns:
        Dict with keys: location, cuisine, cost_min, cost_max, min_rating (values may be None).
        On API failure or parse error, returns empty dict (all None).
    """
    query = (query or "").strip()
    if not query:
        return _empty_filters()

    groq = client or GroqClient()
    if not groq.is_available():
        logger.warning("Groq not available for query parsing")
        return _empty_filters()

    try:
        user_prompt = QUERY_PARSE_USER.format(query=query[:500])
        raw = groq.complete(
            QUERY_PARSE_SYSTEM,
            user_prompt,
            temperature=GROQ_TEMPERATURE,
            max_tokens=min(GROQ_MAX_TOKENS, 300),
        )
        return _parse_query_response(raw)
    except Exception as e:
        logger.warning("Query parse failed: %s", e)
        return _empty_filters()


def _empty_filters() -> dict[str, Any]:
    return {
        "location": None,
        "cuisine": None,
        "cost_min": None,
        "cost_max": None,
        "min_rating": None,
    }


def _parse_query_response(raw: str) -> dict[str, Any]:
    """Extract JSON from LLM response and normalize to filter dict."""
    out = _empty_filters()
    if not raw or not raw.strip():
        return out
    text = raw.strip()
    json_match = re.search(r"\{[\s\S]*\}", text)
    if not json_match:
        return out
    try:
        data = json.loads(json_match.group())
        if isinstance(data.get("location"), str) and data["location"].strip():
            out["location"] = data["location"].strip()
        if isinstance(data.get("cuisine"), str) and data["cuisine"].strip():
            out["cuisine"] = data["cuisine"].strip()
        cmin = data.get("cost_min")
        if cmin is not None:
            try:
                out["cost_min"] = float(cmin)
            except (TypeError, ValueError):
                pass
        cmax = data.get("cost_max")
        if cmax is not None:
            try:
                out["cost_max"] = float(cmax)
            except (TypeError, ValueError):
                pass
        rating = data.get("min_rating")
        if rating is not None:
            try:
                r = float(rating)
                if 0 <= r <= 5:
                    out["min_rating"] = r
            except (TypeError, ValueError):
                pass
        return out
    except json.JSONDecodeError as e:
        logger.warning("Query parse JSON error: %s", e)
        return out
