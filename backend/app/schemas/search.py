"""
DEPRECATED: This module has been moved to backend.app.modules.search.schema

This compatibility shim re-exports from the new location to maintain backward compatibility
during the migration to modular architecture.

Please update your imports to:
    from backend.app.modules.search import (
        SearchQuery,
        SearchResults,
        SearchFilters,
        Facets,
        FacetBucket,
        ThreeWayHybridResults,
        MethodContributions,
        ComparisonResults,
        ComparisonMethodResults,
        EvaluationRequest,
        EvaluationResults,
        EvaluationMetrics,
        BatchSparseEmbeddingRequest,
        BatchSparseEmbeddingResponse
    )
"""

import warnings

warnings.warn(
    "backend.app.schemas.search is deprecated. "
    "Use backend.app.modules.search schema classes instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
from backend.app.modules.search import (
    SearchQuery,
    SearchResults,
    SearchFilters,
    Facets,
    FacetBucket,
    ThreeWayHybridResults,
    MethodContributions,
    ComparisonResults,
    ComparisonMethodResults,
    EvaluationRequest,
    EvaluationResults,
    EvaluationMetrics,
    BatchSparseEmbeddingRequest,
    BatchSparseEmbeddingResponse
)

__all__ = [
    "SearchQuery",
    "SearchResults",
    "SearchFilters",
    "Facets",
    "FacetBucket",
    "ThreeWayHybridResults",
    "MethodContributions",
    "ComparisonResults",
    "ComparisonMethodResults",
    "EvaluationRequest",
    "EvaluationResults",
    "EvaluationMetrics",
    "BatchSparseEmbeddingRequest",
    "BatchSparseEmbeddingResponse"
]
