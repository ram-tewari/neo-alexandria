"""
Domain objects package for Neo Alexandria.

This package contains domain objects that encapsulate business logic
and replace primitive obsession throughout the codebase.
"""

from backend.app.domain.base import (
    BaseDomainObject,
    ValueObject,
    DomainEntity,
    validate_range,
    validate_positive,
    validate_non_empty,
    validate_non_negative,
)

from backend.app.domain.classification import (
    ClassificationPrediction,
    ClassificationResult,
)

from backend.app.domain.search import (
    SearchQuery,
    SearchResult,
    SearchResults,
)

from backend.app.domain.quality import (
    QualityScore,
)

from backend.app.domain.recommendation import (
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
