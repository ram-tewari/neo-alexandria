"""
Domain objects package for Neo Alexandria.

This package contains domain objects that encapsulate business logic
and replace primitive obsession throughout the codebase.
"""

from ..domain.base import (
    BaseDomainObject,
    ValueObject,
    DomainEntity,
    validate_range,
    validate_positive,
    validate_non_empty,
    validate_non_negative,
)

from ..domain.classification import (
    ClassificationPrediction,
    ClassificationResult,
)

from ..domain.search import (
    SearchQuery,
    SearchResult,
    SearchResults,
)

from ..domain.quality import (
    QualityScore,
)

from ..domain.recommendation import (
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
