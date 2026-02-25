"""
Recommendation API routes.
"""

import logging
import time
import uuid
from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException

from phase2.api.schemas.request import RecommendationRequest
from phase2.api.schemas.response import (
    RecommendationResponse,
    RestaurantRecommendation,
    RecommendationSummary,
)
from phase2.config import DEFAULT_RECOMMENDATION_LIMIT, LOG_FORMAT, LOG_LEVEL
from phase2.services.recommendation_service import RecommendationService
from phase2.services.database_service import DatabaseService
from phase4.query_parser import parse_natural_language_query

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommend", tags=["recommendations"])

# Price tier -> (cost_min, cost_max) in ₹ for two
PRICE_TIER_COST = {
    "budget": (None, 500.0),        # <=500
    "mid": (501.0, 1500.0),         # >500 to <=1500
    "premium": (1501.0, None),      # >1500
}


def _dataframe_to_recommendations(df: pd.DataFrame) -> list[RestaurantRecommendation]:
    """Convert DataFrame to list of RestaurantRecommendation objects."""
    recommendations = []
    bucket_to_range = {"low": 1, "medium": 2, "high": 3}

    for _, row in df.iterrows():
        price_range = None
        if "price_range" in row and pd.notna(row.get("price_range")):
            price_range = int(row["price_range"])
        elif "price_bucket" in row:
            price_range = bucket_to_range.get(row["price_bucket"], None)

        cost_val = None
        if "cost" in row and pd.notna(row.get("cost")):
            try:
                cost_val = float(row["cost"])
            except (TypeError, ValueError):
                pass

        rec = RestaurantRecommendation(
            restaurant_id=int(row.get("id", 0)),
            name=str(row.get("name", "")),
            location=str(row.get("location", "")),
            cuisine=str(row.get("cuisine", "")),
            rating=float(row.get("rating", 0.0)),
            price_range=price_range,
            cost=cost_val,
            review_count=int(row.get("votes", 0)) if pd.notna(row.get("votes")) else None,
            score=float(row.get("score", 0.0)),
            explanation=str(row.get("explanation", "")) if pd.notna(row.get("explanation")) else None,
        )
        recommendations.append(rec)
    return recommendations


@router.get("/options")
async def get_options():
    """
    Get dropdown options from Phase 1 data: unique locations and cuisines.
    """
    try:
        db = DatabaseService()
        df = db.get_all_restaurants()
        if len(df) == 0:
            return {
                "locations": [],
                "cuisines": [],
                "price_ranges": [1, 2, 3, 4],
                "price_tiers": [
                    {"value": "budget", "label": "Budget friendly (≤ ₹500)"},
                    {"value": "mid", "label": "Mid-range (₹500–₹1500)"},
                    {"value": "premium", "label": "Premium (> ₹1500)"},
                ],
            }

        locations = sorted(df["location"].dropna().astype(str).str.strip().unique().tolist())
        locations = [x for x in locations if x]

        # Cuisines: from cuisine_list (pipe-separated) and cuisine
        cuisines_set = set()
        if "cuisine_list" in df.columns:
            for v in df["cuisine_list"].dropna():
                s = str(v).strip()
                if s:
                    for part in s.replace("|", ",").split(","):
                        p = part.strip().lower()
                        if p:
                            cuisines_set.add(p.title())
        if "cuisine" in df.columns:
            for v in df["cuisine"].dropna().astype(str):
                for part in str(v).replace("|", ",").split(","):
                    p = part.strip()
                    if p:
                        cuisines_set.add(p.strip().title())
        cuisines = sorted(cuisines_set)

        return {
            "locations": locations,
            "cuisines": cuisines,
            "price_ranges": [1, 2, 3, 4],
            "price_tiers": [
                {"value": "budget", "label": "Budget friendly (≤ ₹500)"},
                {"value": "mid", "label": "Mid-range (₹500–₹1500)"},
                {"value": "premium", "label": "Premium (> ₹1500)"},
            ],
        }
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Database not available. Run Phase 1 pipeline first.")
    except Exception as e:
        logger.exception("Options error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Get restaurant recommendations based on user preferences.

    Args:
        request: Recommendation request with filters.

    Returns:
        RecommendationResponse with top restaurants.
    """
    start_time = time.time()
    query_id = str(uuid.uuid4())

    try:
        logger.info("Processing recommendation request: %s", query_id)

        location = (request.location.place.strip() if request.location else "") or ""
        cuisine = (request.cuisine.strip() or None) if request.cuisine else None
        min_rating = request.minimum_rating
        limit = request.limit or DEFAULT_RECOMMENDATION_LIMIT
        user_coords = request.location.coordinates if request.location else None

        # Price: prefer price_tier (cost-based), else price_range (1-4)
        cost_min, cost_max = None, None
        price_min = request.price_range.min if request.price_range else None
        price_max = request.price_range.max if request.price_range else None
        if request.price_tier and request.price_tier in PRICE_TIER_COST:
            cost_min, cost_max = PRICE_TIER_COST[request.price_tier]
            price_min = price_max = None  # cost filter takes precedence
        elif request.price_range:
            pass  # keep price_min, price_max

        # Natural language query: LLM extracts filters; merge with form (form overrides)
        if request.natural_language_query and request.natural_language_query.strip():
            extracted = parse_natural_language_query(request.natural_language_query.strip())
            if extracted.get("location") and not location:
                location = extracted["location"]
            if extracted.get("cuisine") and not cuisine:
                cuisine = extracted["cuisine"]
            if extracted.get("min_rating") is not None and min_rating is None:
                min_rating = extracted["min_rating"]
            if extracted.get("cost_min") is not None and cost_min is None:
                cost_min = extracted["cost_min"]
            if extracted.get("cost_max") is not None and cost_max is None:
                cost_max = extracted["cost_max"]

        # If still no location, default to Bangalore so the engine can return results
        if not location:
            location = "Bangalore"

        service = RecommendationService()
        recommendations_df, total_found, llm_result = service.get_recommendations(
            location=location,
            cuisine=cuisine,
            min_rating=min_rating,
            price_min=price_min,
            price_max=price_max,
            cost_min=cost_min,
            cost_max=cost_max,
            user_coords=user_coords,
            limit=limit,
            include_explanations=True,
        )

        # Convert to response format
        recommendations = _dataframe_to_recommendations(recommendations_df)

        # AI summary from Phase 4
        ai_explanation = None
        cache_hit = False
        if llm_result:
            ai_explanation = llm_result.get("summary") or None
            cache_hit = llm_result.get("from_cache", False)

        processing_time = int((time.time() - start_time) * 1000)

        response = RecommendationResponse(
            success=True,
            data={
                "recommendations": [rec.model_dump() for rec in recommendations],
                "summary": RecommendationSummary(
                    total_found=total_found,
                    returned=len(recommendations),
                    ai_explanation=ai_explanation,
                ).model_dump(),
            },
            metadata={
                "query_id": query_id,
                "processing_time_ms": processing_time,
                "cache_hit": cache_hit,
            },
        )

        logger.info(
            "Request %s completed: %d recommendations in %dms",
            query_id,
            len(recommendations),
            processing_time,
        )

        return response

    except FileNotFoundError as e:
        logger.error("Database error: %s", e)
        raise HTTPException(
            status_code=503,
            detail="Database not available. Please ensure Phase 1 pipeline has been run.",
        )
    except Exception as e:
        logger.exception("Error processing recommendation request: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )
