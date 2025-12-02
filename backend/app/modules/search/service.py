"""
Search Module Service

Unified search service consolidating all search functionality.

This service provides a single interface for:
- Full-text search (FTS5, PostgreSQL tsvector)
- Dense vector semantic search
- Sparse vector learned keyword search
- Hybrid search with RRF fusion
- ColBERT reranking
- Query-adaptive weighting

Architecture:
- Delegates to existing services for implementation
- Provides unified interface for module consumers
- Handles strategy selection and orchestration
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

# Import existing services (delayed import for AdvancedSearchService to avoid circular dependency)
from backend.app.services.hybrid_search_methods import (
    fallback_search,
    pure_vector_search,
    fusion_search,
    cosine_similarity,
    normalize_scores
)
from backend.app.services.reciprocal_rank_fusion_service import ReciprocalRankFusionService
from backend.app.services.reranking_service import RerankingService
from backend.app.services.sparse_embedding_service import SparseEmbeddingService

logger = logging.getLogger(__name__)


def _get_advanced_search_service():
    """Lazy import to avoid circular dependency."""
    from backend.app.services.search_service import AdvancedSearchService
    return AdvancedSearchService



class SearchService:
    """
    Unified search service providing all search functionality.
    
    This service consolidates multiple search methods into a single interface:
    - Full-text search (FTS5, PostgreSQL)
    - Dense vector semantic search
    - Sparse vector learned keyword search
    - Hybrid search with RRF fusion
    - ColBERT reranking
    
    The service delegates to existing implementations while providing
    a clean, modular interface for the Search module.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the search service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    # ========================================================================
    # Main Search Methods
    # ========================================================================
    
    def search(self, query: Any) -> Tuple[List[Any], int, Any, Dict[str, str]]:
        """
        Execute search using the appropriate method based on query parameters.
        
        Args:
            query: SearchQuery object with search parameters
            
        Returns:
            Tuple of (resources, total, facets, snippets)
        """
        AdvancedSearchService = _get_advanced_search_service()
        return AdvancedSearchService.search(self.db, query)
    
    def hybrid_search(
        self,
        query: Any,
        hybrid_weight: float = 0.5
    ) -> Tuple[List[Any], int, Any, Dict[str, str]]:
        """
        Execute hybrid search combining FTS and vector similarity.
        
        Args:
            query: SearchQuery object
            hybrid_weight: Weight for fusion (0.0=keyword, 1.0=semantic)
            
        Returns:
            Tuple of (resources, total, facets, snippets)
        """
        AdvancedSearchService = _get_advanced_search_service()
        return AdvancedSearchService.hybrid_search(self.db, query, hybrid_weight)
    
    def three_way_hybrid_search(
        self,
        query: Any,
        enable_reranking: bool = True,
        adaptive_weighting: bool = True
    ) -> Tuple[List[Any], int, Any, Dict[str, str], Dict[str, Any]]:
        """
        Execute three-way hybrid search with RRF fusion and optional reranking.
        
        Combines FTS5, dense vectors, and sparse vectors using Reciprocal Rank
        Fusion with query-adaptive weighting and optional ColBERT reranking.
        
        Args:
            query: SearchQuery object
            enable_reranking: Whether to apply ColBERT reranking
            adaptive_weighting: Whether to use query-adaptive RRF weights
            
        Returns:
            Tuple of (resources, total, facets, snippets, metadata)
        """
        AdvancedSearchService = _get_advanced_search_service()
        return AdvancedSearchService.search_three_way_hybrid(
            self.db,
            query,
            enable_reranking=enable_reranking,
            adaptive_weighting=adaptive_weighting
        )
    
    # ========================================================================
    # Component Services (for direct access if needed)
    # ========================================================================
    
    def get_rrf_service(self, k: int = 60) -> ReciprocalRankFusionService:
        """Get RRF service for result fusion."""
        return ReciprocalRankFusionService(k=k)
    
    def get_reranking_service(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ) -> RerankingService:
        """Get reranking service for ColBERT reranking."""
        return RerankingService(self.db, model_name=model_name)
    
    def get_sparse_embedding_service(
        self,
        model_name: str = "BAAI/bge-m3"
    ) -> SparseEmbeddingService:
        """Get sparse embedding service."""
        return SparseEmbeddingService(self.db, model_name=model_name)
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    @staticmethod
    def parse_search_query(text: str) -> str:
        """
        Parse input text into FTS5 MATCH syntax.
        
        Args:
            text: Raw search query text
            
        Returns:
            Parsed query string for FTS5
        """
        AdvancedSearchService = _get_advanced_search_service()
        return AdvancedSearchService.parse_search_query(text)
    
    @staticmethod
    def generate_snippets(text: str, query: str) -> str:
        """
        Generate highlighted snippet from text.
        
        Args:
            text: Source text
            query: Search query for highlighting
            
        Returns:
            Snippet with highlighted matches
        """
        AdvancedSearchService = _get_advanced_search_service()
        return AdvancedSearchService.generate_snippets(text, query)
    
    @staticmethod
    def analyze_query(query: str) -> Dict[str, Any]:
        """
        Analyze query characteristics for adaptive weighting.
        
        Args:
            query: Search query text
            
        Returns:
            Dictionary with query characteristics
        """
        AdvancedSearchService = _get_advanced_search_service()
        return AdvancedSearchService._analyze_query(query)


# ============================================================================
# Strategy Classes (for internal use)
# ============================================================================

class FTSSearchStrategy:
    """Strategy for FTS5 keyword search."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search(
        self,
        query: str,
        limit: int = 100
    ) -> List[Tuple[str, float]]:
        """Execute FTS5 search and return (resource_id, score) tuples."""
        # Delegate to AdvancedSearchService
        AdvancedSearchService = _get_advanced_search_service()
        parsed_query = AdvancedSearchService.parse_search_query(query)
        items, _, scores, _ = AdvancedSearchService.fts_search(
            self.db, parsed_query, None, limit=limit, offset=0
        )
        return [(str(item.id), scores.get(str(item.id), 1.0)) for item in items]


class VectorSearchStrategy:
    """Strategy for dense vector semantic search."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search(
        self,
        query: str,
        limit: int = 100
    ) -> List[Tuple[str, float]]:
        """Execute dense vector search and return (resource_id, score) tuples."""
        # Use pure_vector_search from hybrid_search_methods
        from backend.app.modules.search.schema import SearchQuery
        AdvancedSearchService = _get_advanced_search_service()
        search_query = SearchQuery(text=query, limit=limit, offset=0)
        items, _, _, _ = pure_vector_search(self.db, search_query, AdvancedSearchService)
        # Return with similarity scores (would need to compute)
        return [(str(item.id), 1.0) for item in items]


class HybridSearchStrategy:
    """Strategy for hybrid search combining multiple methods."""
    
    def __init__(self, db: Session):
        self.db = db
        self.rrf_service = ReciprocalRankFusionService(k=60)
    
    def search(
        self,
        query: str,
        enable_reranking: bool = True,
        adaptive_weighting: bool = True,
        limit: int = 20
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Execute hybrid search with RRF fusion.
        
        Returns:
            Tuple of (resources, metadata)
        """
        from backend.app.schemas.search import SearchQuery
        search_query = SearchQuery(text=query, limit=limit, offset=0)
        
        AdvancedSearchService = _get_advanced_search_service()
        resources, total, facets, snippets, metadata = AdvancedSearchService.search_three_way_hybrid(
            self.db,
            search_query,
            enable_reranking=enable_reranking,
            adaptive_weighting=adaptive_weighting
        )
        
        return resources, metadata
