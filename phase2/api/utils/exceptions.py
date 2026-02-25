"""
Custom exceptions for API.
"""


class RecommendationError(Exception):
    """Base exception for recommendation errors."""

    pass


class DatabaseError(RecommendationError):
    """Database-related errors."""

    pass


class ValidationError(RecommendationError):
    """Validation errors."""

    pass
