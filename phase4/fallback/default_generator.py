"""
Default/template-based explanations when LLM is unavailable or fails.
"""

from typing import Any, Optional


class DefaultExplanationGenerator:
    """Generates simple template-based explanations without LLM."""

    def generate_for_restaurant(
        self,
        name: str,
        rating: Optional[float] = None,
        cuisine: Optional[str] = None,
        price_bucket: Optional[str] = None,
    ) -> str:
        """Generate a short default explanation for one restaurant."""
        parts = [f"{name} is a recommended choice."]
        if rating is not None:
            parts.append(f"It has a {rating}-star rating.")
        if cuisine:
            parts.append(f"The cuisine is {cuisine}.")
        if price_bucket:
            parts.append(f"Price range: {price_bucket}.")
        return " ".join(parts)

    def generate_summary(
        self,
        location: Optional[str] = None,
        cuisine: Optional[str] = None,
        count: int = 0,
    ) -> str:
        """Generate a default overall summary."""
        parts = ["Here are your restaurant recommendations."]
        if location:
            parts.append(f"They are in {location}.")
        if cuisine:
            parts.append(f"They match your preference for {cuisine} cuisine.")
        if count:
            parts.append(f"We found {count} options for you.")
        return " ".join(parts)

    def generate_all(
        self,
        restaurants: list[dict[str, Any]],
        location: Optional[str] = None,
        cuisine: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate default explanations and summary for all restaurants.

        Returns:
            {"explanations": [{"restaurant_name": "...", "explanation": "..."}], "summary": "..."}
        """
        explanations = []
        for r in restaurants:
            name = r.get("name", "Restaurant")
            explanations.append({
                "restaurant_name": name,
                "explanation": self.generate_for_restaurant(
                    name,
                    r.get("rating"),
                    r.get("cuisine"),
                    r.get("price_bucket"),
                ),
            })
        summary = self.generate_summary(location, cuisine, len(restaurants))
        return {"explanations": explanations, "summary": summary}
