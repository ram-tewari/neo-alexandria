"""
Domain objects package for Neo Alexandria.

This package contains domain objects that encapsulate business logic
and replace primitive obsession throughout the codebase.
"""

from .base import (
    BaseDomainObject,
    ValueObject,
    DomainEntity,
    validate_range,
    validate_positive,
    validate_non_empty,
    validate_non_negative,
)

from .classification import (
    ClassificationPrediction,
    ClassificationResult,
)

from .search import (
    SearchQuery,
    SearchResult,
    SearchResults,
)

from .quality import (
    QualityScore,
)

from .recommendation import (
    Recommendation,
    RecommendationScore,
)

__all__ = [
    "BaseDomainObject",
    "ValueObject",
    "DomainEntity",
    "validate_range",
    "validate_positive",
    "validate_non_empty",
    "validate_non_negative",
    "ClassificationPrediction",
    "ClassificationResult",
    "SearchQuery",
    "SearchResult",
    "SearchResults",
    "QualityScore",
    "Recommendation",
    "RecommendationScore",
]
