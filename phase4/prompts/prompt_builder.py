"""
Builds prompts from context (user preferences + restaurants).
"""

from typing import Any, Optional

from phase4.prompts.templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class PromptBuilder:
    """Builds system and user prompts for the LLM."""

    def __init__(
        self,
        system_prompt: str = SYSTEM_PROMPT,
        user_template: str = USER_PROMPT_TEMPLATE,
    ) -> None:
        self.system_prompt = system_prompt
        self.user_template = user_template

    def build_restaurant_list(self, restaurants: list[dict[str, Any]]) -> str:
        """Format restaurant list for prompt (cost in ₹ when available)."""
        lines = []
        for r in restaurants:
            name = r.get("name", "Unknown")
            rating = r.get("rating", "")
            cuisine = r.get("cuisine", "")
            cost = r.get("cost")
            price_bucket = r.get("price_bucket", r.get("price_range", ""))
            price_str = f"₹{cost}" if cost is not None else str(price_bucket)
            votes = r.get("votes", "")
            line = f"- {name} (rating: {rating}, cuisine: {cuisine}, cost for two: {price_str}, reviews: {votes})"
            lines.append(line)
        return "\n".join(lines) if lines else "No restaurants."

    def build(
        self,
        location: str,
        cuisine: Optional[str],
        price_range: str,
        restaurants: list[dict[str, Any]],
        min_rating: Optional[float] = None,
    ) -> tuple[str, str]:
        """
        Build system and user prompts.

        Args:
            location: User location.
            cuisine: User cuisine preference.
            price_range: User price range (e.g. "₹500-1500" or "2-3").
            restaurants: List of restaurant dicts with name, rating, cuisine, etc.
            min_rating: User minimum rating filter (0-5).

        Returns:
            (system_prompt, user_prompt)
        """
        restaurant_list = self.build_restaurant_list(restaurants)
        min_rating_str = f"{min_rating}" if min_rating is not None else "Any"
        user_prompt = self.user_template.format(
            location=location or "Not specified",
            cuisine=cuisine or "Any",
            price_range=price_range or "Any",
            min_rating=min_rating_str,
            restaurant_list=restaurant_list,
        )
        return self.system_prompt, user_prompt
