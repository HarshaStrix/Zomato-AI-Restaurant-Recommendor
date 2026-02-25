"""
Request schemas for recommendation API.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class LocationInput(BaseModel):
    """Location input schema."""

    place: str = Field(..., description="City or location name", min_length=1)
    coordinates: Optional[dict[str, float]] = Field(
        None,
        description="Optional GPS coordinates with 'latitude' and 'longitude'",
    )

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v):
        """Validate coordinates if provided."""
        if v is not None:
            if "latitude" not in v or "longitude" not in v:
                raise ValueError("Coordinates must include 'latitude' and 'longitude'")
            if not (-90 <= v["latitude"] <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= v["longitude"] <= 180):
                raise ValueError("Longitude must be between -180 and 180")
        return v


class PriceRangeInput(BaseModel):
    """Price range input schema."""

    min: Optional[int] = Field(None, ge=1, le=4, description="Minimum price range (1-4)")
    max: Optional[int] = Field(None, ge=1, le=4, description="Maximum price range (1-4)")

    @field_validator("max")
    @classmethod
    def validate_range(cls, v, info):
        """Ensure max >= min if both provided."""
        if v is not None and "min" in info.data and info.data["min"] is not None:
            if v < info.data["min"]:
                raise ValueError("max must be >= min")
        return v


# Price tier by cost for two (₹): budget <=500, mid 500-1500, premium >1500
PriceTier = Literal["budget", "mid", "premium"]


class RecommendationRequest(BaseModel):
    """Request schema for restaurant recommendations.
    Location is optional when natural_language_query is provided (LLM can extract it).
    """

    location: Optional[LocationInput] = Field(
        None, description="Location preferences (optional if natural_language_query is provided)"
    )
    price_range: Optional[PriceRangeInput] = Field(
        None, description="Optional price range filter (1-4)"
    )
    price_tier: Optional[PriceTier] = Field(
        None,
        description="Price tier: budget (<=500), mid (500-1500), premium (>1500)",
    )
    minimum_rating: Optional[float] = Field(
        None, ge=0.0, le=5.0, description="Minimum rating filter (0-5)"
    )
    cuisine: Optional[str] = Field(
        None, min_length=1, description="Preferred cuisine type"
    )
    limit: Optional[int] = Field(
        None, ge=1, le=50, description="Number of recommendations (default: 5)"
    )
    natural_language_query: Optional[str] = Field(
        None,
        max_length=500,
        description="Free-text search (e.g. romantic place for dinner under ₹1500); LLM extracts filters.",
    )

    model_config = {"json_schema_extra": {"example": {
        "location": {"place": "Bangalore"},
        "price_tier": "mid",
        "minimum_rating": 4.0,
        "cuisine": "Italian",
        "natural_language_query": "romantic place for dinner under 1500",
        "limit": 5
    }}}
