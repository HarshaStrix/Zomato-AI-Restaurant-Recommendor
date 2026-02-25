"""
Recommendation service: Phase 2 DB + Phase 3 engine + Phase 4 LLM.
"""

import logging
from typing import Any, Optional

import pandas as pd

from phase2.config import DEFAULT_RECOMMENDATION_LIMIT, LOG_FORMAT, LOG_LEVEL
from phase2.services.database_service import DatabaseService
from phase3.recommendation_engine import RecommendationEngine
from phase4.llm_service import LLMService

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class RecommendationService:
    """Orchestrates Phase 3 recommendation engine and Phase 4 LLM explanations."""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        recommendation_engine: Optional[RecommendationEngine] = None,
        llm_service: Optional[LLMService] = None,
    ) -> None:
        self.db_service = db_service or DatabaseService()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()
        self.llm_service = llm_service or LLMService()

    def get_recommendations(
        self,
        location: str,
        cuisine: Optional[str] = None,
        min_rating: Optional[float] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        cost_min: Optional[float] = None,
        cost_max: Optional[float] = None,
        user_coords: Optional[dict] = None,
        limit: int = DEFAULT_RECOMMENDATION_LIMIT,
        include_explanations: bool = True,
    ) -> tuple[pd.DataFrame, int, Optional[dict[str, Any]]]:
        """
        Get restaurant recommendations (Phase 3 engine) with optional LLM explanations (Phase 4).

        cost_min/cost_max: filter by cost in ₹ (for two). When set, used instead of price_min/price_max.

        Returns:
            (recommendations_df, total_found, llm_result with summary/from_cache/from_fallback)
        """
        logger.info(
            "Getting recommendations: location=%s, cuisine=%s, min_rating=%s, "
            "price=%s-%s, cost=%s-%s, limit=%d",
            location,
            cuisine,
            min_rating,
            price_min,
            price_max,
            cost_min,
            cost_max,
            limit,
        )

        restaurants_df = self.db_service.get_all_restaurants()
        if len(restaurants_df) == 0:
            logger.warning("No restaurants found in database")
            return pd.DataFrame(), 0, None

        # Phase 3: filter, score, rank (removes duplicates via engine)
        ranked, total_found = self.recommendation_engine.get_recommendations(
            restaurants_df,
            location=location,
            cuisine=cuisine,
            min_rating=min_rating,
            price_min=price_min,
            price_max=price_max,
            cost_min=cost_min,
            cost_max=cost_max,
            user_coords=user_coords,
            limit=limit,
        )

        # Deduplicate by (name, location) before LLM
        ranked = ranked.drop_duplicates(subset=["name", "location"], keep="first").head(limit)

        llm_result = None
        if include_explanations:
            price_range_str = ""
            if cost_min is not None or cost_max is not None:
                price_range_str = f"₹{cost_min or 0}-{cost_max or '∞'}"
            elif price_min is not None or price_max is not None:
                price_range_str = f"₹ tier {price_min or 1}-{price_max or 4}"
            
            rest_list = ranked.to_dict("records")
            llm_result = self.llm_service.generate_explanations(
                rest_list,
                location=location,
                cuisine=cuisine,
                price_range=price_range_str,
                min_rating=min_rating,
            )
            
            if len(ranked) > 0:
                # Attach explanation to each row
                enriched = self.llm_service.attach_explanations_to_restaurants(rest_list, llm_result)
                ranked = pd.DataFrame(enriched)

        return ranked, total_found, llm_result
