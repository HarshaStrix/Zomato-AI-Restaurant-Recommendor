"""
Response schemas for recommendation API.
"""

from typing import Optional

from pydantic import BaseModel, Field


class RestaurantRecommendation(BaseModel):
    """Individual restaurant recommendation. All prices in Indian Rupees (₹)."""

    restaurant_id: int = Field(..., description="Unique restaurant ID")
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Restaurant location")
    cuisine: str = Field(..., description="Cuisine type")
    rating: float = Field(..., description="Average rating (0-5)")
    price_range: Optional[int] = Field(None, description="Price range (1-4)")
    cost: Optional[float] = Field(None, description="Cost for two in ₹ (Indian Rupees)")
    review_count: Optional[int] = Field(None, description="Number of reviews/votes")
    score: float = Field(..., description="Recommendation score (0-1)")
    explanation: Optional[str] = Field(
        None, description="Explanation (will be added in Phase 4 with LLM)"
    )


class RecommendationSummary(BaseModel):
    """Summary of recommendations."""

    total_found: int = Field(..., description="Total restaurants found")
    returned: int = Field(..., description="Number of recommendations returned")
    ai_explanation: Optional[str] = Field(
        None, description="AI-generated summary (will be added in Phase 4)"
    )


class RecommendationResponse(BaseModel):
    """Response schema for restaurant recommendations."""

    success: bool = Field(True, description="Request success status")
    data: dict = Field(
        ...,
        description="Response data containing recommendations and summary",
    )
    metadata: Optional[dict] = Field(
        None, description="Additional metadata (processing time, cache hit, etc.)"
    )

    model_config = {"json_schema_extra": {"example": {
        "success": True,
        "data": {
            "recommendations": [
                {
                    "restaurant_id": 1,
                    "name": "Restaurant A",
                    "location": "Bangalore",
                    "cuisine": "Italian",
                    "rating": 4.5,
                    "price_range": 2,
                    "review_count": 500,
                    "score": 0.85,
                    "explanation": None
                }
            ],
            "summary": {
                "total_found": 10,
                "returned": 5,
                "ai_explanation": None
            }
        },
        "metadata": {
            "query_id": "uuid-here",
            "processing_time_ms": 45
        }
    }}}
