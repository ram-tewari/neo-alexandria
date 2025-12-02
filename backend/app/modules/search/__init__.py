"""
Search Module

This module provides comprehensive search functionality for Neo Alexandria 2.0,
including full-text search, semantic search, and hybrid search capabilities.

Public Interface:
- search_router: FastAPI router for search endpoints
- SearchService: Unified search service
- Search schemas: SearchQuery, SearchResults, etc.

Domain: Search and Information Retrieval
Version: 1.0.0
"""

__version__ = "1.0.0"
__domain__ = "search"

# Import public interface
from backend.app.modules.search.router import router as search_router
from backend.app.modules.search.service import SearchService
from backend.app.modules.search.schema import (
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
from backend.app.modules.search.handlers import register_handlers

# Public exports
__all__ = [
    # Router
    "search_router",
    
    # Service
    "SearchService",
    
    # Schemas
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
    "BatchSparseEmbeddingResponse",
    
    # Event handlers
    "register_handlers",
    
    # Metadata
    "__version__",
    "__domain__"
]
