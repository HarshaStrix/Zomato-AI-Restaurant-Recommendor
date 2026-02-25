"""
Parses LLM response into structured explanations and summary.
"""

import json
import logging
import re
from typing import Any, Optional

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class ResponseParser:
    """Parse LLM JSON response into explanations and summary."""

    def parse(self, raw_response: str) -> dict[str, Any]:
        """
        Parse raw LLM response into structured format.

        Expected shape:
        {
          "explanations": [{"restaurant_name": "...", "explanation": "..."}],
          "summary": "..."
        }

        Args:
            raw_response: Raw string from LLM.

        Returns:
            Dict with "explanations" (list) and "summary" (str).
            On parse failure, returns fallback structure.
        """
        if not raw_response or not raw_response.strip():
            return {"explanations": [], "summary": "No explanation generated."}

        # Try to extract JSON from response (handle markdown code blocks)
        text = raw_response.strip()
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            try:
                data = json.loads(json_match.group())
                explanations = data.get("explanations", [])
                if not isinstance(explanations, list):
                    explanations = []
                summary = data.get("summary", "")
                if not isinstance(summary, str):
                    summary = str(summary)
                return {"explanations": explanations, "summary": summary}
            except json.JSONDecodeError as e:
                logger.warning("JSON parse error: %s", e)

        # Fallback: treat whole response as summary
        return {"explanations": [], "summary": text[:500]}

    def get_explanation_by_name(
        self, parsed: dict[str, Any], restaurant_name: str
    ) -> Optional[str]:
        """Get explanation text for a restaurant by name (fuzzy match)."""
        explanations = parsed.get("explanations", [])
        name_lower = restaurant_name.lower().strip()
        for item in explanations:
            if not isinstance(item, dict):
                continue
            rn = (item.get("restaurant_name") or "").lower().strip()
            if rn == name_lower or name_lower in rn or rn in name_lower:
                return item.get("explanation")
        return None
