"""
Neo Alexandria 2.0 - Advanced Search Service (Phase 4)

This module provides the advanced search service for Neo Alexandria 2.0, integrating
traditional FTS5 keyword search with Phase 4's vector semantic search capabilities.
It orchestrates hybrid search operations and provides comprehensive search functionality.

Related files:
- app/services/hybrid_search_methods.py: Core hybrid search implementation
- app/services/ai_core.py: Vector embedding generation
- app/routers/search.py: Search API endpoints
- app/schemas/search.py: Search query and result schemas
- app/config/settings.py: Search configuration settings

Features:
- FTS5 full-text search with SQLite contentless virtual tables
- PostgreSQL full-text search with tsvector and tsquery
- Phase 4 hybrid search with vector similarity and weighted fusion
- Advanced filtering, pagination, and sorting capabilities
- Faceted search with counts for classification, type, language, and subjects
- Search result snippets with highlighted matching text
- Graceful fallback to LIKE search when FTS5 unavailable
- Automatic detection of search capabilities and method routing
- Comprehensive error handling and performance optimization
- Database-agnostic full-text search abstraction (Phase 13)
"""

from __future__ import annotations

import logging
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

from sqlalchemy import text, func, or_, asc, desc, String, cast
from sqlalchemy.orm import Session

from backend.app.database.models import Resource
from backend.app.schemas.search import Facets, FacetBucket, SearchFilters
from backend.app.schemas.search import SearchQuery as SearchQuerySchema
from backend.app.domain.search import SearchQuery as DomainSearchQuery
from backend.app.config.settings import get_settings
from backend.app.services.ai_core import generate_embedding
from backend.app.cache.redis_cache import cache
from backend.app.database.base import get_database_type

# Setup logging
logger = logging.getLogger(__name__)

# Import numpy with fallback for vector operations
try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


# ============================================================================
# Full-Text Search Strategy Pattern (Phase 13)
# ============================================================================

class FullTextSearchStrategy(ABC):
    """
    Abstract base class for full-text search strategies.
    
    Provides a common interface for different database-specific full-text
    search implementations (SQLite FTS5, PostgreSQL tsvector, etc.).
    """
    
    def __init__(self, db: Session):
        """
        Initialize the search strategy.
        
        Args:
            db: Database session
        """
        self.db = db
    
    @abstractmethod
    def search(
        self,
        query: str,
        filters: SearchFilters | None = None,
        limit: int = 25,
        offset: int = 0
    ) -> Tuple[List[Resource], int, Dict[str, float], Dict[str, str]]:
        """
        Execute full-text search.
        
        Args:
            query: Search query text
            filters: Optional structured filters
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            Tuple of:
            - resources: List of Resource objects
            - total: Total count of matching resources
            - scores: Dict mapping resource_id to relevance score
            - snippets: Dict mapping resource_id to snippet text
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this search strategy is available.
        
        Returns:
            True if the search method is available, False otherwise
        """
        pass


class SQLiteFTS5Strategy(FullTextSearchStrategy):
    """
    SQLite FTS5 full-text search strategy.
    
    Uses SQLite's FTS5 virtual tables for full-text search with BM25 ranking.
    """
    
    def is_available(self) -> bool:
        """Check if FTS5 is available and index is ready."""
        return _detect_fts5(self.db) and _fts_index_ready(self.db)
    
    def search(
        self,
        query: str,
        filters: SearchFilters | None = None,
        limit: int = 25,
        offset: int = 0
    ) -> Tuple[List[Resource], int, Dict[str, float], Dict[str, str]]:
        """
        Execute FTS5 full-text search.
        
        Args:
            query: Search query text
            filters: Optional structured filters
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            Tuple of (resources, total, scores, snippets)
        """
        if not self.is_available():
            logger.warning("FTS5 not available, returning empty results")
            return [], 0, {}, {}
        
        # Parse query into FTS5 MATCH syntax
        from backend.app.services.search_service import AdvancedSearchService
        parsed_query = AdvancedSearchService.parse_search_query(query)
        
        # Execute FTS5 search
        items, total, _, bm25_scores, snippets = AdvancedSearchService.fts_search(
            self.db, parsed_query, filters, limit=limit, offset=offset
        )
        
        return items, total, bm25_scores, snippets


class PostgreSQLFullTextStrategy(FullTextSearchStrategy):
    """
    PostgreSQL full-text search strategy.
    
    Uses PostgreSQL's tsvector and tsquery for full-text search with
    ts_rank ranking.
    """
    
    def is_available(self) -> bool:
        """Check if PostgreSQL full-text search is available."""
        try:
            db_type = get_database_type(self.db.bind.url.render_as_string(hide_password=True))
            if db_type != "postgresql":
                return False
            
            # Check if search_vector column exists
            result = self.db.execute(
                text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'resources' 
                    AND column_name = 'search_vector'
                """)
            ).fetchone()
            
            return result is not None
        except Exception as e:
            logger.debug(f"PostgreSQL FTS availability check failed: {e}")
            return False
    
    def search(
        self,
        query: str,
        filters: SearchFilters | None = None,
        limit: int = 25,
        offset: int = 0
    ) -> Tuple[List[Resource], int, Dict[str, float], Dict[str, str]]:
        """
        Execute PostgreSQL full-text search.
        
        Args:
            query: Search query text
            filters: Optional structured filters
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            Tuple of (resources, total, scores, snippets)
        """
        if not self.is_available():
            logger.warning("PostgreSQL FTS not available, returning empty results")
            return [], 0, {}, {}
        
        try:
            # Convert query to tsquery format
            # Simple approach: split on spaces and join with &
            query_terms = query.strip().split()
            tsquery_str = " & ".join(query_terms)
            
            # Build base query with full-text search
            sql_query = text("""
                SELECT 
                    id,
                    ts_rank(search_vector, to_tsquery('english', :query)) as rank,
                    ts_headline('english', 
                        COALESCE(description, title), 
                        to_tsquery('english', :query),
                        'MaxWords=20, MinWords=10, MaxFragments=1'
                    ) as snippet
                FROM resources
                WHERE search_vector @@ to_tsquery('english', :query)
                ORDER BY rank DESC
                LIMIT :limit OFFSET :offset
            """)
            
            # Execute search
            results = self.db.execute(
                sql_query,
                {"query": tsquery_str, "limit": limit, "offset": offset}
            ).fetchall()
            
            # Get total count
            count_query = text("""
                SELECT COUNT(*) 
                FROM resources 
                WHERE search_vector @@ to_tsquery('english', :query)
            """)
            total = self.db.execute(count_query, {"query": tsquery_str}).scalar() or 0
            
            # Extract resource IDs, scores, and snippets
            resource_ids = [str(row[0]) for row in results]
            scores = {str(row[0]): float(row[1]) for row in results}
            snippets = {str(row[0]): str(row[2]) for row in results}
            
            # Fetch full Resource objects
            if resource_ids:
                resources_query = self.db.query(Resource).filter(
                    Resource.id.in_(resource_ids)
                )
                
                # Apply structured filters
                resources_query = _apply_structured_filters(resources_query, filters)
                
                # Preserve ranking order
                resources = resources_query.all()
                resource_map = {str(r.id): r for r in resources}
                ordered_resources = [
                    resource_map[rid] for rid in resource_ids if rid in resource_map
                ]
            else:
                ordered_resources = []
            
            return ordered_resources, int(total), scores, snippets
            
        except Exception as e:
            logger.error(f"PostgreSQL FTS search failed: {e}", exc_info=True)
            return [], 0, {}, {}

# Import Phase 8 services for three-way hybrid search
try:
    from backend.app.services.sparse_embedding_service import SparseEmbeddingService
    from backend.app.services.reciprocal_rank_fusion_service import ReciprocalRankFusionService
    from backend.app.services.reranking_service import RerankingService
except ImportError:  # pragma: no cover
    SparseEmbeddingService = None
    ReciprocalRankFusionService = None
    RerankingService = None


@dataclass
class _FtsSupport:
    checked: bool = False
    available: bool = False


_fts_support = _FtsSupport()


@dataclass
class RetrievalCandidates:
    """Intermediate data structure for retrieval phase results.
    
    Encapsulates the results from all three retrieval methods before fusion.
    This enables independent testing and modification of the retrieval phase.
    
    Attributes:
        fts5_results: Results from FTS5 keyword search
        dense_results: Results from dense vector search
        sparse_results: Results from sparse vector search
        retrieval_time_ms: Total time taken for retrieval phase
        method_times_ms: Individual times for each method
    """
    fts5_results: List[Tuple[str, float]]
    dense_results: List[Tuple[str, float]]
    sparse_results: List[Tuple[str, float]]
    retrieval_time_ms: float
    method_times_ms: Dict[str, float]
    
    def get_all_candidate_ids(self) -> set[str]:
        """Get all unique candidate IDs across all methods.
        
        Returns:
            Set of unique resource IDs
        """
        all_ids = set()
        all_ids.update(rid for rid, _ in self.fts5_results)
        all_ids.update(rid for rid, _ in self.dense_results)
        all_ids.update(rid for rid, _ in self.sparse_results)
        return all_ids
    
    def get_method_counts(self) -> Dict[str, int]:
        """Get count of results from each method.
        
        Returns:
            Dictionary with counts for each method
        """
        return {
            'fts5': len(self.fts5_results),
            'dense': len(self.dense_results),
            'sparse': len(self.sparse_results)
        }


@dataclass
class FusedCandidates:
    """Intermediate data structure for fusion phase results.
    
    Encapsulates the results after RRF fusion but before reranking.
    This enables independent testing and modification of the fusion phase.
    
    Attributes:
        fused_results: Ranked list of (resource_id, score) after RRF fusion
        weights_used: RRF weights applied to each method
        fusion_time_ms: Time taken for fusion phase
        method_contributions: Count of results contributed by each method
    """
    fused_results: List[Tuple[str, float]]
    weights_used: List[float]
    fusion_time_ms: float
    method_contributions: Dict[str, int]
    
    def get_top_k(self, k: int) -> List[Tuple[str, float]]:
        """Get top k results.
        
        Args:
            k: Number of top results to return
            
        Returns:
            List of top k (resource_id, score) tuples
        """
        return self.fused_results[:k]
    
    def get_candidate_ids(self) -> List[str]:
        """Get ordered list of candidate IDs.
        
        Returns:
            List of resource IDs in ranked order
        """
        return [rid for rid, _ in self.fused_results]


class HybridSearchQuery:
    """Encapsulates three-way hybrid search pipeline.
    
    This class combines FTS5 keyword search, dense vector search, and sparse
    vector search using Reciprocal Rank Fusion (RRF) with optional reranking.
    
    Attributes:
        db: Database session
        query: Domain SearchQuery object with query text and configuration
        enable_reranking: Whether to apply ColBERT reranking
        adaptive_weighting: Whether to use query-adaptive RRF weights
    """
    
    def __init__(
        self,
        db: Session,
        query: DomainSearchQuery,
        enable_reranking: bool = True,
        adaptive_weighting: bool = True
    ):
        """Initialize hybrid search query.
        
        Args:
            db: Database session
            query: Domain SearchQuery object with query text and configuration
            enable_reranking: Whether to apply ColBERT reranking (default: True)
            adaptive_weighting: Whether to use query-adaptive RRF weights (default: True)
        """
        self.db = db
        self.query = query
        self.enable_reranking = enable_reranking
        self.adaptive_weighting = adaptive_weighting
        
        # Diagnostic information
        self._diagnostics: Dict[str, Any] = {
            'query_analysis': {},
            'retrieval_times': {},
            'method_results': {},
            'fusion_time': 0.0,
            'reranking_time': 0.0,
            'total_time': 0.0
        }
    
    def execute(self) -> Tuple[List[Resource], int, Facets, Dict[str, str], Dict[str, Any]]:
        """Execute the hybrid search pipeline.
        
        Returns:
            Tuple of:
            - resources: List of Resource objects
            - total: Total count of unique matching resources
            - facets: Faceted search results
            - snippets: Dict mapping resource_id to snippet text
            - metadata: Dict with latency_ms, method_contributions, weights_used
        """
        import time
        
        start_time = time.time()
        
        # Ensure tables exist
        self._ensure_tables_exist()
        
        # Check if Phase 8 services are available
        if not self._check_services_available():
            return self._fallback_to_two_way_hybrid(start_time)
        
        # 1. Query Analysis
        query_analysis = self._analyze_query()
        self._diagnostics['query_analysis'] = query_analysis
        logger.debug(f"Query analysis: {query_analysis}")
        
        # PHASE 1: Candidate Retrieval
        # Execute all three retrieval methods and collect results
        retrieval_candidates = self._execute_retrieval_phase()
        
        # PHASE 2: Fusion
        # Fuse candidates using RRF with adaptive weighting
        fused_candidates = self._execute_fusion_phase(retrieval_candidates)
        
        # PHASE 3: Reranking (optional)
        # Apply ColBERT reranking to improve ranking quality
        final_results = self._execute_reranking_phase(fused_candidates)
        
        # 6. Fetch Resources
        resources = self._fetch_paginated_resources(final_results)
        
        # Total count is the number of unique documents in fused results
        total = len(final_results)
        
        # 7. Compute Facets
        facets = self._compute_facets(final_results)
        
        # 8. Generate Snippets
        snippets = self._generate_snippets(resources)
        
        # 9. Compute Metadata
        total_time = (time.time() - start_time) * 1000
        self._diagnostics['total_time'] = total_time
        
        metadata = {
            'latency_ms': total_time,
            'method_contributions': fused_candidates.method_contributions,
            'weights_used': fused_candidates.weights_used,
            'reranking_enabled': self.enable_reranking,
            'adaptive_weighting': self.adaptive_weighting
        }
        
        # Log slow queries
        if total_time > 500:
            logger.warning(
                f"Slow query detected: {total_time:.1f}ms for query '{self.query.query_text[:50]}...'"
            )
        
        logger.info(
            f"Three-way hybrid search completed in {total_time:.1f}ms: "
            f"{len(resources)} results returned, {total} total matches"
        )
        
        return resources, total, facets, snippets, metadata
    
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information about the search execution.
        
        Returns:
            Dictionary with diagnostic information including:
            - query_analysis: Query characteristics
            - retrieval_times: Time taken for each retrieval method
            - method_results: Number of results from each method
            - fusion_time: Time taken for RRF fusion
            - reranking_time: Time taken for reranking (if enabled)
            - total_time: Total execution time
        """
        return self._diagnostics.copy()
    
    def _convert_to_schema_filters(self) -> SearchFilters | None:
        """Convert domain SearchQuery to schema SearchFilters for compatibility.
        
        Returns:
            SearchFilters object or None
        """
        # For now, return None as the domain SearchQuery doesn't have filters
        # This will be enhanced when filters are added to the domain object
        return None
    
    def _ensure_tables_exist(self) -> None:
        """Ensure database tables exist."""
        from backend.app.database.base import Base
        try:
            Base.metadata.create_all(bind=self.db.get_bind())
        except Exception:
            pass
    
    def _check_services_available(self) -> bool:
        """Check if Phase 8 services are available.
        
        Returns:
            True if all required services are available, False otherwise
        """
        return (
            ReciprocalRankFusionService is not None and
            SparseEmbeddingService is not None and
            (not self.enable_reranking or RerankingService is not None)
        )
    
    def _fallback_to_two_way_hybrid(self, start_time: float) -> Tuple[List[Resource], int, Facets, Dict[str, str], Dict[str, Any]]:
        """Fallback to two-way hybrid search when Phase 8 services unavailable.
        
        Args:
            start_time: Start time for timing calculation
            
        Returns:
            Search results tuple
        """
        import time
        
        logger.warning(
            "Phase 8 services not fully available, falling back to two-way hybrid search"
        )
        
        # Convert domain SearchQuery to schema SearchQuery for compatibility
        schema_query = SearchQuerySchema(
            text=self.query.query_text,
            limit=self.query.limit,
            offset=0,
            hybrid_weight=0.5
        )
        
        results = AdvancedSearchService.hybrid_search(
            self.db, schema_query, 0.5
        )
        
        # Unpack and add empty metadata
        if len(results) == 4:
            resources, total, facets, snippets = results
        else:
            resources, total, facets = results
            snippets = {}
        
        metadata = {
            'latency_ms': (time.time() - start_time) * 1000,
            'method_contributions': {'fts5': 0, 'dense': 0, 'sparse': 0},
            'weights_used': [0.5, 0.5, 0.0],
            'reranking_enabled': self.enable_reranking,
            'adaptive_weighting': self.adaptive_weighting
        }
        return resources, total, facets, snippets, metadata
    
    def _analyze_query(self) -> Dict[str, Any]:
        """Analyze query characteristics.
        
        Returns:
            Dictionary with query analysis results
        """
        return AdvancedSearchService._analyze_query(self.query.query_text or "")
    
    def _execute_retrieval_phase(self) -> RetrievalCandidates:
        """Execute Phase 1: Candidate Retrieval.
        
        Executes all three retrieval methods in parallel and collects results
        into an intermediate data structure. This phase is independent of fusion
        and reranking, enabling separate testing and optimization.
        
        Returns:
            RetrievalCandidates with results from all three methods
        """
        import time
        
        retrieval_start = time.time()
        method_times: Dict[str, float] = {}
        
        # Execute three retrieval methods
        fts5_start = time.time()
        fts5_results = self._search_fts5()
        method_times['fts5'] = (time.time() - fts5_start) * 1000
        
        dense_start = time.time()
        dense_results = self._search_dense()
        method_times['dense'] = (time.time() - dense_start) * 1000
        
        sparse_start = time.time()
        sparse_results = self._search_sparse()
        method_times['sparse'] = (time.time() - sparse_start) * 1000
        
        retrieval_time = (time.time() - retrieval_start) * 1000
        
        # Create intermediate data structure
        candidates = RetrievalCandidates(
            fts5_results=fts5_results,
            dense_results=dense_results,
            sparse_results=sparse_results,
            retrieval_time_ms=retrieval_time,
            method_times_ms=method_times
        )
        
        # Update diagnostics
        self._diagnostics['retrieval_times'] = method_times
        self._diagnostics['retrieval_times']['total'] = retrieval_time
        self._diagnostics['method_results'] = candidates.get_method_counts()
        
        logger.debug(
            f"Retrieval phase completed in {retrieval_time:.1f}ms: "
            f"FTS5={len(fts5_results)}, Dense={len(dense_results)}, Sparse={len(sparse_results)}"
        )
        
        return candidates
    
    def _execute_fusion_phase(self, candidates: RetrievalCandidates) -> FusedCandidates:
        """Execute Phase 2: Fusion.
        
        Fuses results from all three retrieval methods using Reciprocal Rank Fusion
        with optional adaptive weighting. This phase is independent of retrieval
        and reranking, enabling separate testing and optimization.
        
        Args:
            candidates: RetrievalCandidates from retrieval phase
            
        Returns:
            FusedCandidates with merged and ranked results
        """
        import time
        
        fusion_start = time.time()
        
        # Compute adaptive weights based on query characteristics
        weights = self._compute_weights()
        
        # Apply RRF fusion
        rrf_service = ReciprocalRankFusionService(k=60)
        result_lists = [
            candidates.fts5_results,
            candidates.dense_results,
            candidates.sparse_results
        ]
        fused_results = rrf_service.fuse_results(result_lists, weights)
        
        # Compute method contributions
        method_contributions = self._compute_method_contributions(
            candidates.fts5_results,
            candidates.dense_results,
            candidates.sparse_results
        )
        
        fusion_time = (time.time() - fusion_start) * 1000
        
        # Create intermediate data structure
        fused = FusedCandidates(
            fused_results=fused_results,
            weights_used=weights,
            fusion_time_ms=fusion_time,
            method_contributions=method_contributions
        )
        
        # Update diagnostics
        self._diagnostics['fusion_time'] = fusion_time
        
        logger.debug(
            f"Fusion phase completed in {fusion_time:.1f}ms: "
            f"{len(fused_results)} unique documents, "
            f"weights=[{weights[0]:.3f}, {weights[1]:.3f}, {weights[2]:.3f}]"
        )
        
        return fused
    
    def _execute_reranking_phase(self, fused: FusedCandidates) -> List[Tuple[str, float]]:
        """Execute Phase 3: Reranking (optional).
        
        Applies ColBERT reranking to improve ranking quality. This phase is
        independent of retrieval and fusion, enabling separate testing and
        can be disabled for faster results.
        
        Args:
            fused: FusedCandidates from fusion phase
            
        Returns:
            Final ranked list of (resource_id, score) tuples
        """
        import time
        
        # If reranking is disabled, return fused results as-is
        if not self.enable_reranking or not fused.fused_results:
            logger.debug("Reranking phase skipped")
            return fused.fused_results
        
        reranking_start = time.time()
        
        try:
            reranking_service = RerankingService(self.db)
            
            # Take top 100 candidates for reranking
            candidates = fused.get_top_k(100)
            candidate_ids = [rid for rid, _ in candidates]
            
            reranked_results = reranking_service.rerank(
                self.query.query_text or "",
                candidate_ids,
                top_k=100,
                timeout=1.0  # 1 second timeout
            )
            
            if reranked_results:
                # Combine reranked top 100 with remaining fused results
                final_results = reranked_results + fused.fused_results[100:]
                reranking_time = (time.time() - reranking_start) * 1000
                self._diagnostics['reranking_time'] = reranking_time
                logger.debug(f"Reranking phase completed in {reranking_time:.1f}ms")
                return final_results
            else:
                logger.warning("Reranking returned no results, using fusion results")
                return fused.fused_results
        
        except Exception as e:
            logger.error(f"Reranking phase failed: {e}", exc_info=True)
            return fused.fused_results
    

    
    def _search_fts5(self) -> List[Tuple[str, float]]:
        """Execute full-text search using appropriate strategy.
        
        Uses database-specific full-text search strategy:
        - SQLite: FTS5 virtual tables
        - PostgreSQL: tsvector and tsquery
        
        Returns:
            List of (resource_id, score) tuples
        """
        import time
        
        start = time.time()
        results = []
        
        try:
            if not self.query.query_text:
                return results
            
            # Select appropriate full-text search strategy
            strategy = self._get_fts_strategy()
            
            if strategy and strategy.is_available():
                # Convert domain SearchQuery to schema SearchFilters for compatibility
                filters = self._convert_to_schema_filters()
                
                # Execute search using strategy
                items, _, scores, _ = strategy.search(
                    self.query.query_text,
                    filters=filters,
                    limit=100,
                    offset=0
                )
                
                results = [(str(item.id), scores.get(str(item.id), 1.0)) for item in items]
                logger.debug(f"Full-text search returned {len(results)} results using {strategy.__class__.__name__}")
            else:
                logger.debug("No full-text search strategy available")
        except Exception as e:
            logger.error(f"Full-text search failed: {e}", exc_info=True)
        
        self._diagnostics['retrieval_times']['fts5'] = (time.time() - start) * 1000
        return results
    
    def _get_fts_strategy(self) -> FullTextSearchStrategy | None:
        """
        Get appropriate full-text search strategy for current database.
        
        Returns:
            FullTextSearchStrategy instance or None if no strategy available
        """
        try:
            db_type = get_database_type(self.db.bind.url.render_as_string(hide_password=True))
            
            if db_type == "postgresql":
                return PostgreSQLFullTextStrategy(self.db)
            elif db_type == "sqlite":
                return SQLiteFTS5Strategy(self.db)
            else:
                logger.warning(f"Unsupported database type for FTS: {db_type}")
                return None
        except Exception as e:
            logger.error(f"Failed to determine FTS strategy: {e}", exc_info=True)
            return None
    
    def _search_dense(self) -> List[Tuple[str, float]]:
        """Execute dense vector search.
        
        Returns:
            List of (resource_id, score) tuples
        """
        import time
        import json
        
        start = time.time()
        results = []
        
        try:
            if self.query.query_text and np is not None:
                # Check if we have embeddings
                has_embeddings = self.db.query(Resource).filter(
                    Resource.embedding.isnot(None),
                    func.json_array_length(Resource.embedding) > 0
                ).first() is not None
                
                if has_embeddings:
                    # Generate query embedding
                    query_embedding = generate_embedding(self.query.query_text)
                    
                    if query_embedding:
                        # Get all resources with embeddings
                        resources_with_embeddings = self.db.query(Resource).filter(
                            Resource.embedding.isnot(None),
                            func.json_array_length(Resource.embedding) > 0
                        ).all()
                        
                        # Compute cosine similarities
                        query_vec = np.array(query_embedding)
                        query_norm = np.linalg.norm(query_vec)
                        
                        similarities = []
                        for resource in resources_with_embeddings:
                            try:
                                resource_vec = np.array(json.loads(resource.embedding))
                                resource_norm = np.linalg.norm(resource_vec)
                                
                                if query_norm > 0 and resource_norm > 0:
                                    similarity = np.dot(query_vec, resource_vec) / (query_norm * resource_norm)
                                    similarities.append((str(resource.id), float(similarity)))
                            except Exception:
                                continue
                        
                        # Sort by similarity and take top 100
                        similarities.sort(key=lambda x: x[1], reverse=True)
                        results = similarities[:100]
                        logger.debug(f"Dense vector search returned {len(results)} results")
        except Exception as e:
            logger.error(f"Dense vector search failed: {e}", exc_info=True)
        
        self._diagnostics['retrieval_times']['dense'] = (time.time() - start) * 1000
        return results
    
    def _search_sparse(self) -> List[Tuple[str, float]]:
        """Execute sparse vector search.
        
        Returns:
            List of (resource_id, score) tuples
        """
        import time
        
        start = time.time()
        results = []
        
        try:
            if self.query.query_text:
                results = AdvancedSearchService._search_sparse(self.db, self.query.query_text, limit=100)
                logger.debug(f"Sparse vector search returned {len(results)} results")
        except Exception as e:
            logger.error(f"Sparse vector search failed: {e}", exc_info=True)
        
        self._diagnostics['retrieval_times']['sparse'] = (time.time() - start) * 1000
        return results
    
    def _compute_weights(self) -> List[float]:
        """Compute RRF weights based on query characteristics.
        
        Returns:
            List of three weights for [fts5, dense, sparse]
        """
        rrf_service = ReciprocalRankFusionService(k=60)
        
        if self.adaptive_weighting and self.query.query_text:
            weights = rrf_service.adaptive_weights(self.query.query_text)
        else:
            # Equal weights
            weights = [1.0 / 3, 1.0 / 3, 1.0 / 3]
        
        logger.debug(f"Using RRF weights: FTS5={weights[0]:.3f}, Dense={weights[1]:.3f}, Sparse={weights[2]:.3f}")
        return weights
    

    
    def _compute_method_contributions(
        self,
        fts5_results: List[Tuple[str, float]],
        dense_results: List[Tuple[str, float]],
        sparse_results: List[Tuple[str, float]]
    ) -> Dict[str, int]:
        """Compute how many results each method contributed.
        
        Args:
            fts5_results: FTS5 search results
            dense_results: Dense vector search results
            sparse_results: Sparse vector search results
            
        Returns:
            Dictionary with counts for each method
        """
        fts5_ids = {rid for rid, _ in fts5_results}
        dense_ids = {rid for rid, _ in dense_results}
        sparse_ids = {rid for rid, _ in sparse_results}
        
        return {
            'fts5': len(fts5_ids),
            'dense': len(dense_ids),
            'sparse': len(sparse_ids)
        }
    

    
    def _fetch_paginated_resources(self, fused_results: List[Tuple[str, float]]) -> List[Resource]:
        """Fetch resources with pagination applied.
        
        Args:
            fused_results: Fused and ranked results
            
        Returns:
            List of Resource objects
        """
        # Apply pagination to fused results
        # Note: offset and pagination will be handled by the caller
        # For now, take the first 'limit' results
        paginated_ids = [rid for rid, _ in fused_results[:self.query.limit]]
        
        return AdvancedSearchService._fetch_resources_ordered(
            self.db,
            paginated_ids,
            None  # No filters for now
        )
    
    def _compute_facets(self, fused_results: List[Tuple[str, float]]) -> Facets:
        """Compute facets from fused results.
        
        Args:
            fused_results: Fused and ranked results
            
        Returns:
            Facets object
        """
        # Use all fused result IDs for facet computation
        all_fused_ids = [rid for rid, _ in fused_results]
        facet_query = self.db.query(Resource).filter(Resource.id.in_(all_fused_ids))
        # No filters for now
        return _compute_facets(self.db, facet_query)
    
    def _generate_snippets(self, resources: List[Resource]) -> Dict[str, str]:
        """Generate snippets for resources.
        
        Args:
            resources: List of Resource objects
            
        Returns:
            Dictionary mapping resource_id to snippet text
        """
        snippets: Dict[str, str] = {}
        if self.query.query_text:
            for resource in resources:
                snippets[str(resource.id)] = AdvancedSearchService.generate_snippets(
                    (resource.description or resource.title or ""),
                    self.query.query_text
                )
        return snippets


def _detect_fts5(db: Session) -> bool:
    global _fts_support
    if _fts_support.checked:
        return _fts_support.available
    try:
        conn = db.connection()
        if conn.dialect.name != "sqlite":
            _fts_support = _FtsSupport(True, False)
            return False
        # Probe FTS5 via PRAGMA or temp table create
        try:
            rows = conn.exec_driver_sql("PRAGMA compile_options;").fetchall()
            if any("FTS5" in r[0] for r in rows):
                _fts_support = _FtsSupport(True, True)
                return True
        except Exception:
            pass
        try:
            conn.exec_driver_sql("CREATE VIRTUAL TABLE IF NOT EXISTS temp.__fts_probe USING fts5(x);")
            conn.exec_driver_sql("DROP TABLE IF EXISTS temp.__fts_probe;")
            _fts_support = _FtsSupport(True, True)
            return True
        except Exception:
            _fts_support = _FtsSupport(True, False)
            return False
    except Exception:
        _fts_support = _FtsSupport(True, False)
        return False


def _fts_index_ready(db: Session) -> bool:
    """Return True only if the FTS index tables exist."""
    try:
        conn = db.connection()
        if conn.dialect.name != "sqlite":
            return False
        rows = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name IN ('resources_fts','resources_fts_doc');"
        ).fetchall()
        names = {r[0] for r in rows}
        return {"resources_fts", "resources_fts_doc"}.issubset(names)
    except Exception:
        return False


def _apply_structured_filters(q, filters) -> Any:
    if not filters:
        return q

    if filters.classification_code:
        q = q.filter(Resource.classification_code.in_(filters.classification_code))
    if filters.type:
        q = q.filter(Resource.type.in_(filters.type))
    if filters.language:
        q = q.filter(Resource.language.in_(filters.language))
    if filters.read_status:
        q = q.filter(Resource.read_status.in_(filters.read_status))
    if filters.min_quality is not None:
        q = q.filter(Resource.quality_score >= float(filters.min_quality))
    if filters.created_from:
        q = q.filter(Resource.created_at >= filters.created_from)
    if filters.created_to:
        q = q.filter(Resource.created_at <= filters.created_to)
    if filters.updated_from:
        q = q.filter(Resource.updated_at >= filters.updated_from)
    if filters.updated_to:
        q = q.filter(Resource.updated_at <= filters.updated_to)

    # Subject matching (portable) using JSON serialization fallback
    if filters.subject_any:
        ser = func.lower(cast(Resource.subject, String))
        ors = [ser.like(f"%{term.lower()}%") for term in filters.subject_any]
        if ors:
            q = q.filter(or_(*ors))
    if filters.subject_all:
        ser_all = func.lower(cast(Resource.subject, String))
        for term in filters.subject_all:
            q = q.filter(ser_all.like(f"%{term.lower()}%"))
    return q


def _compute_facets(db: Session, base_query) -> Facets:
    # Materialize filtered IDs to avoid duplicating filter logic in counts
    subq = base_query.with_entities(Resource.id).subquery()

    # Simple helpers to run grouped counts
    def buckets(col) -> List[FacetBucket]:
        rows = (
            db.query(col.label("key"), func.count().label("count"))
            .select_from(Resource)
            .filter(Resource.id.in_(db.query(subq.c.id)))
            .group_by(col)
            .order_by(func.count().desc(), col.asc())
            .all()
        )
        return [FacetBucket(key=(k if k is not None else ""), count=c) for k, c in rows if k is not None]

    # Subjects: portable aggregation in Python (guards malformed JSON)
    terms: Dict[str, int] = {}
    for (arr_json,) in db.query(Resource.subject).filter(Resource.id.in_(db.query(subq.c.id))).all():
        try:
            for term in (arr_json or []):
                if isinstance(term, str):
                    terms[term] = terms.get(term, 0) + 1
        except Exception:
            continue
    top = sorted(terms.items(), key=lambda kv: (-kv[1], kv[0]))[:15]
    subject_buckets = [FacetBucket(key=k, count=c) for k, c in top]

    return Facets(
        classification_code=buckets(Resource.classification_code),
        type=buckets(Resource.type),
        language=buckets(Resource.language),
        read_status=buckets(Resource.read_status),
        subject=subject_buckets,
    )


class AdvancedSearchService:
    @staticmethod
    def _get_fts_strategy_for_db(db: Session) -> FullTextSearchStrategy | None:
        """
        Get appropriate full-text search strategy for the database.
        
        Args:
            db: Database session
            
        Returns:
            FullTextSearchStrategy instance or None if no strategy available
        """
        try:
            db_type = get_database_type(db.bind.url.render_as_string(hide_password=True))
            
            if db_type == "postgresql":
                return PostgreSQLFullTextStrategy(db)
            elif db_type == "sqlite":
                return SQLiteFTS5Strategy(db)
            else:
                logger.warning(f"Unsupported database type for FTS: {db_type}")
                return None
        except Exception as e:
            logger.error(f"Failed to determine FTS strategy: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _generate_cache_key(query: SearchQuerySchema) -> str:
        """Generate cache key from search query.
        
        Args:
            query: SearchQuerySchema object
            
        Returns:
            Cache key string
        """
        # Create a dict representation of the query for hashing
        query_dict = {
            "text": query.text,
            "limit": query.limit,
            "offset": query.offset,
            "sort_by": query.sort_by,
            "sort_dir": query.sort_dir,
            "hybrid_weight": query.hybrid_weight,
            "filters": {
                "classification_code": query.filters.classification_code if query.filters else None,
                "type": query.filters.type if query.filters else None,
                "language": query.filters.language if query.filters else None,
                "subject_any": query.filters.subject_any if query.filters else None,
                "subject_all": query.filters.subject_all if query.filters else None,
                "min_quality": query.filters.min_quality if query.filters else None,
                "created_from": str(query.filters.created_from) if query.filters and query.filters.created_from else None,
                "created_to": str(query.filters.created_to) if query.filters and query.filters.created_to else None,
            }
        }
        
        # Generate hash from query dict
        query_json = json.dumps(query_dict, sort_keys=True)
        query_hash = hashlib.md5(query_json.encode()).hexdigest()
        
        return f"search_query:{query_hash}"
    
    @staticmethod
    def _cache_search_results(
        cache_key: str,
        resources: List[Resource],
        total: int,
        facets: Facets,
        snippets: Dict[str, str]
    ) -> None:
        """
        Cache search results for faster subsequent queries.
        
        Args:
            cache_key: Cache key for this query
            resources: List of Resource objects
            total: Total count of results
            facets: Facets object
            snippets: Snippets dictionary
        """
        try:
            # Extract resource IDs to cache (we'll fetch full objects from DB on cache hit)
            resource_ids = [str(r.id) for r in resources]
            
            # Convert facets to dict for caching
            facets_data = {
                "classification_code": [{"key": b.key, "count": b.count} for b in facets.classification_code],
                "type": [{"key": b.key, "count": b.count} for b in facets.type],
                "language": [{"key": b.key, "count": b.count} for b in facets.language],
                "read_status": [{"key": b.key, "count": b.count} for b in facets.read_status],
                "subject": [{"key": b.key, "count": b.count} for b in facets.subject],
            }
            
            # Create cache data
            cache_data = {
                "resource_ids": resource_ids,
                "total": total,
                "facets": facets_data,
                "snippets": snippets
            }
            
            # Cache for 5 minutes (300 seconds)
            cache.set(cache_key, cache_data, ttl=300)
            logger.debug(f"Cached search results for key: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to cache search results: {e}")
    
    @staticmethod
    def search(db: Session, query: SearchQuerySchema):
        # Try cache first
        cache_key = AdvancedSearchService._generate_cache_key(query)
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            logger.debug(f"Cache hit for search query: {query.text}")
            # Reconstruct result from cache
            # Note: We need to fetch resources from DB as we can't cache ORM objects
            resource_ids = cached_result.get("resource_ids", [])
            if resource_ids:
                resources = db.query(Resource).filter(Resource.id.in_(resource_ids)).all()
                # Maintain order from cache
                id_to_resource = {str(r.id): r for r in resources}
                ordered_resources = [id_to_resource[rid] for rid in resource_ids if rid in id_to_resource]
            else:
                ordered_resources = []
            
            total = cached_result.get("total", 0)
            facets_data = cached_result.get("facets", {})
            snippets = cached_result.get("snippets", {})
            
            # Reconstruct Facets object
            facets = Facets(
                classification_code=[FacetBucket(key=b["key"], count=b["count"]) for b in facets_data.get("classification_code", [])],
                type=[FacetBucket(key=b["key"], count=b["count"]) for b in facets_data.get("type", [])],
                language=[FacetBucket(key=b["key"], count=b["count"]) for b in facets_data.get("language", [])],
                read_status=[FacetBucket(key=b["key"], count=b["count"]) for b in facets_data.get("read_status", [])],
                subject=[FacetBucket(key=b["key"], count=b["count"]) for b in facets_data.get("subject", [])]
            )
            
            return ordered_resources, total, facets, snippets
        
        logger.debug(f"Cache miss for search query: {query.text}")
        
        # Ensure tables exist
        from backend.app.database.base import Base
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass
        
        # Phase 4: Hybrid search with vector embeddings
        settings = get_settings()
        hybrid_weight = query.hybrid_weight if query.hybrid_weight is not None else settings.DEFAULT_HYBRID_SEARCH_WEIGHT
        
        # Use hybrid search when text query is provided and numpy is available
        # But only if we have embeddings in the database
        if query.text and np is not None:
            # Check if we have any resources with embeddings
            has_embeddings = db.query(Resource).filter(
                Resource.embedding.isnot(None),
                func.json_array_length(Resource.embedding) > 0
            ).first() is not None
            
            if has_embeddings:
                return AdvancedSearchService.hybrid_search(db, query, hybrid_weight)
        
        # Determine if full-text search is available using strategy pattern
        fts_strategy = AdvancedSearchService._get_fts_strategy_for_db(db)
        use_fts = bool(query.text) and fts_strategy is not None and fts_strategy.is_available()

        base = db.query(Resource)

        if use_fts and query.text:
            # Use strategy pattern for database-agnostic full-text search
            items, total, bm25_scores, snippets = fts_strategy.search(
                query.text, query.filters, limit=query.limit, offset=query.offset
            )
            
            # Compute facets from results
            if items:
                facets_query = db.query(Resource).filter(Resource.id.in_([r.id for r in items]))
                facets = _compute_facets(db, facets_query)
            else:
                facets = Facets(
                    classification_code=[],
                    type=[],
                    language=[],
                    read_status=[],
                    subject=[]
                )

            # Apply ranking with BM25 + boosts
            ranked_items = AdvancedSearchService.rank_results(items, bm25_scores, query.filters)

            # Respect requested sorting if not relevance
            if query.sort_by != "relevance":
                sort_map = {
                    "updated_at": Resource.updated_at,
                    "created_at": Resource.created_at,
                    "quality_score": Resource.quality_score,
                    "title": Resource.title,
                }
                col = sort_map.get(query.sort_by, Resource.updated_at)
                order = asc(col) if query.sort_dir == "asc" else desc(col)
                ranked_items = (
                    _apply_structured_filters(db.query(Resource).filter(Resource.id.in_([r.id for r in ranked_items])), query.filters)
                    .order_by(order)
                    .limit(query.limit)
                    .offset(0)
                    .all()
                )

            # Attach snippets via return structure
            # Cache the results
            AdvancedSearchService._cache_search_results(cache_key, ranked_items, total, facets, snippets)
            # Return tuple extended with snippets mapping
            return ranked_items, total, facets, snippets

        # Fallback keyword search or when no text provided
        q = base
        if query.text:
            # Advanced fallback: support phrases, AND/OR/NOT, field scoping, and wildcards using LIKE
            import shlex

            def _make_condition(field: str | None, term: str):
                t = term.strip().strip('"')
                if not t:
                    return None
                # Handle wildcards properly
                if term.endswith("*"):
                    # For wildcards, match words starting with the prefix
                    like_pat = f"%{t.rstrip('*').lower()}%"
                else:
                    like_pat = f"%{t.lower()}%"
                
                title_col = func.lower(Resource.title)
                desc_col = func.lower(Resource.description)
                if field == "title":
                    return title_col.like(like_pat)
                if field == "description":
                    return desc_col.like(like_pat)
                return or_(title_col.like(like_pat), desc_col.like(like_pat))

            try:
                raw_tokens = shlex.split(query.text)
            except Exception:
                raw_tokens = query.text.split()

            conditions = []
            pending_op = None
            negate_next = False
            
            for tok in raw_tokens:
                up = tok.upper()
                if up in {"AND", "OR"}:
                    pending_op = up
                    continue
                if up == "NOT":
                    negate_next = True
                    continue
                
                field = None
                term = tok
                if ":" in tok:
                    f, t = tok.split(":", 1)
                    if f in {"title", "description"}:
                        field, term = f, t
                
                cond = _make_condition(field, term)
                if cond is None:
                    continue
                    
                if negate_next:
                    cond = ~cond
                    negate_next = False
                
                if pending_op == "OR":
                    if conditions:
                        # Combine with OR
                        conditions[-1] = or_(conditions[-1], cond)
                    else:
                        conditions.append(cond)
                else:
                    # Default to AND behavior
                    conditions.append(cond)
                pending_op = None

            if conditions:
                # Combine all conditions with AND
                final_condition = conditions[0]
                for cond in conditions[1:]:
                    final_condition = final_condition & cond
                q = q.filter(final_condition)
            else:
                # Fallback to simple LIKE on the whole text
                like = f"%{query.text.lower()}%"
                q = q.filter(or_(func.lower(Resource.title).like(like), func.lower(Resource.description).like(like)))

        filtered = _apply_structured_filters(q, query.filters)

        # Total before pagination
        total = filtered.count()

        # Sorting
        sort_map = {
            "relevance": Resource.updated_at,  # when no FTS, treat relevance as updated_at
            "updated_at": Resource.updated_at,
            "created_at": Resource.created_at,
            "quality_score": Resource.quality_score,
            "title": Resource.title,
        }
        col = sort_map.get(query.sort_by, Resource.updated_at)
        order = asc(col) if query.sort_dir == "asc" else desc(col)
        ordered = filtered.order_by(order)

        items = ordered.offset(query.offset).limit(query.limit).all()
        facets = _compute_facets(db, filtered)

        # Fallback snippets: simple extract around first match
        snippets: Dict[str, str] = {}
        if query.text:
            for it in items:
                snippets[str(it.id)] = AdvancedSearchService.generate_snippets(
                    (it.description or it.title or ""), query.text
                )

        # Cache the results
        AdvancedSearchService._cache_search_results(cache_key, items, total, facets, snippets)
        
        return items, total, facets, snippets

    @staticmethod
    def parse_search_query(text_in: str) -> str:
        """Parse input into FTS5 MATCH syntax.

        Supports:
        - Phrases with double quotes
        - Boolean operators AND/OR/NOT (case-insensitive)
        - Field scoping: title:term, description:term
        - Prefix wildcard: term*
        """
        if not text_in:
            return ""

        import shlex

        tokens: List[str] = []
        # shlex splits while respecting quotes
        try:
            raw_tokens = shlex.split(text_in)
        except Exception:
            raw_tokens = text_in.split()

        def is_operator(tok: str) -> bool:
            return tok.upper() in {"AND", "OR", "NOT"}

        for tok in raw_tokens:
            if is_operator(tok):
                tokens.append(tok.upper())
                continue
            field = None
            term = tok
            if ":" in tok:
                f, t = tok.split(":", 1)
                if f in {"title", "description"} and t:
                    field, term = f, t
            # Preserve phrase quotes if present already (from shlex)
            is_phrase = term.startswith("\"") and term.endswith("\"") and len(term) >= 2
            # Escape embedded quotes
            if not is_phrase and (" " in term):
                is_phrase = True
                term = f'"{term}"'
            # Normalize wildcard (allow trailing *)
            # Basic sanitization: remove dangerous characters
            safe = term
            # Allow *, ", : in controlled spots; strip others
            safe = safe.replace("'", "")
            if field:
                tokens.append(f"{field}:{safe}")
            else:
                tokens.append(safe)

        # Default implicit AND between terms
        # Join by space which FTS treats similar to AND; but we will insert explicit ANDs for clarity
        out: List[str] = []
        prev_was_term = False
        for tok in tokens:
            if tok in {"AND", "OR", "NOT"}:
                out.append(tok)
                prev_was_term = False if tok == "NOT" else False
            else:
                if prev_was_term:
                    out.append("AND")
                out.append(tok)
                prev_was_term = True
        return " ".join(out)

    @staticmethod
    def fts_search(
        db: Session,
        match_query: str,
        filters: SearchFilters | None,
        *,
        limit: int,
        offset: int,
    ) -> Tuple[List[Resource], int, Facets, Dict[str, float], Dict[str, str]]:
        """Execute FTS5 query and return items, total, facets, bm25 map, snippets map."""
        conn = db.connection()
        # Total count
        total_row = conn.execute(
            text(
                """
                SELECT COUNT(1)
                FROM resources_fts r
                WHERE r MATCH :q
                """
            ),
            {"q": match_query},
        ).scalar()
        total = int(total_row or 0)

        # All matched for facets and filtering
        all_rows = conn.execute(
            text(
                """
                SELECT d.resource_id
                FROM resources_fts r
                JOIN resources_fts_doc d ON d.rowid = r.rowid
                WHERE r MATCH :q
                """
            ),
            {"q": match_query},
        ).fetchall()
        all_ids = [r[0] for r in all_rows]

        # Apply structured filters to full set, then page
        full_filtered = db.query(Resource).filter(Resource.id.in_(all_ids))
        full_filtered = _apply_structured_filters(full_filtered, filters)

        # Page via bm25 order and join with mapping
        try:
            rows = conn.execute(
                text(
                    """
                    SELECT d.resource_id, bm25(r) AS bm
                    FROM resources_fts r
                    JOIN resources_fts_doc d ON d.rowid = r.rowid
                    WHERE r MATCH :q
                    ORDER BY bm ASC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"q": match_query, "limit": limit, "offset": offset},
            ).fetchall()
        except Exception:
            rows = conn.execute(
                text(
                    """
                    SELECT d.resource_id, 1.0 AS bm
                    FROM resources_fts r
                    JOIN resources_fts_doc d ON d.rowid = r.rowid
                    WHERE r MATCH :q
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"q": match_query, "limit": limit, "offset": offset},
            ).fetchall()

        page_ids = [row[0] for row in rows]
        bm25_map: Dict[str, float] = {row[0]: float(row[1]) for row in rows}

        # Fetch ORM items preserving pagination subset
        query_set = db.query(Resource).filter(Resource.id.in_(page_ids))
        query_set = _apply_structured_filters(query_set, filters)

        # Preserve bm25 order using CASE
        if page_ids:
            case_stmt = "CASE " + " ".join(
                f"WHEN id = '{rid}' THEN {i}" for i, rid in enumerate(page_ids)
            ) + " ELSE 1000000 END"
            query_set = query_set.order_by(text(case_stmt))
        items = query_set.all()

        # Compute facets from full_filtered
        facets = _compute_facets(db, full_filtered)

        # Snippets for page rows
        snippet_rows = conn.execute(
            text(
                """
                SELECT d.resource_id,
                       snippet(resources_fts, 1, '<mark>', '</mark>', '…', 12) as snip
                FROM resources_fts r
                JOIN resources_fts_doc d ON d.rowid = r.rowid
                WHERE r MATCH :q AND d.resource_id IN (:ids)
                """.replace(":ids", ",".join([f"'{pid}'" for pid in page_ids]) if page_ids else "''")
            ),
            {"q": match_query},
        ).fetchall()
        snippets: Dict[str, str] = {rid: (snip or "") for rid, snip in snippet_rows}

        # If snippet missing, fallback to description-based
        for it in items:
            if str(it.id) not in snippets:
                snippets[str(it.id)] = AdvancedSearchService.generate_snippets(
                    (it.description or it.title or ""), match_query
                )

        return items, total, facets, bm25_map, snippets

    @staticmethod
    def rank_results(items: List[Resource], bm25_map: Dict[str, float], filters: SearchFilters | None) -> List[Resource]:
        """Rank by weighted combination: BM25 (0.6), quality (0.2), recency (0.1), classification (0.1)."""
        now = datetime.now(timezone.utc)

        selected_codes = set(filters.classification_code) if (filters and filters.classification_code) else set()

        def score(it: Resource) -> float:
            bm_raw = bm25_map.get(str(it.id), bm25_map.get(it.id, 1.0))
            bm = 1.0 / (1.0 + float(bm_raw))  # normalize lower-is-better to 0..1
            quality = max(0.0, min(1.0, float(getattr(it, "quality_score", 0.0) or 0.0)))
            dt = getattr(it, "updated_at", None) or getattr(it, "created_at", None)
            if dt is None:
                rec = 0.0
            else:
                # days scale -> 0..1 with 365-day window
                try:
                    delta_days = max(0.0, (now - dt).total_seconds() / 86400.0)
                except Exception:
                    rec = 0.0
                else:
                    rec = max(0.0, 1.0 - min(1.0, delta_days / 365.0))
            cls = 0.0
            if selected_codes:
                if getattr(it, "classification_code", None) in selected_codes:
                    cls = 1.0
            return 0.6 * bm + 0.2 * quality + 0.1 * rec + 0.1 * cls

        return sorted(items, key=score, reverse=True)

    @staticmethod
    def generate_snippets(text: str, query: str) -> str:
        """Generate a simple highlighted snippet around the first match.

        Fallback when FTS5 snippet isn't available.
        """
        if not text:
            return ""
        if not query:
            return text[:200] + ("…" if len(text) > 200 else "")
        hay = text
        q = query.strip().strip('"')
        # crude: pick first non-operator token
        for token in q.split():
            up = token.upper()
            if up in {"AND", "OR", "NOT"}:
                continue
            t = token.strip('"')
            if not t:
                continue
            idx = hay.lower().find(t.lower().rstrip("*"))
            if idx >= 0:
                start = max(0, idx - 60)
                end = min(len(hay), idx + len(t) + 140)
                snippet = hay[start:end]
                # highlight all occurrences of the token in snippet
                try:
                    import re
                    pattern = re.compile(re.escape(t.rstrip("*")), re.IGNORECASE)
                    snippet = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", snippet)
                except Exception:
                    pass
                if start > 0:
                    snippet = "…" + snippet
                if end < len(hay):
                    snippet = snippet + "…"
                return snippet
        return text[:200] + ("…" if len(text) > 200 else "")

    @staticmethod
    def hybrid_search(db: Session, query: SearchQuerySchema, hybrid_weight: float) -> Tuple[List[Resource], int, Facets, Dict[str, str]]:
        """Execute hybrid search combining FTS5 and vector similarity.
        
        Args:
            db: Database session
            query: Search query with text and filters
            hybrid_weight: Weight for fusion (0.0=keyword only, 1.0=semantic only)
            
        Returns:
            Tuple of (resources, total_count, facets, snippets)
        """
        from backend.app.services.hybrid_search_methods import (
            fallback_search, pure_vector_search, fusion_search
        )
        
        if hybrid_weight == 0.0:
            # Pure keyword search - use existing FTS logic
            return fallback_search(db, query, AdvancedSearchService)
        elif hybrid_weight == 1.0:
            # Pure semantic search
            return pure_vector_search(db, query, AdvancedSearchService)
        else:
            # True hybrid search - combine both approaches
            return fusion_search(db, query, hybrid_weight, AdvancedSearchService)

    @staticmethod
    def search_with_annotations(
        db: Session,
        query: str,
        user_id: str,
        include_annotations: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Enhanced search that includes annotation matches.
        
        Algorithm:
        1. Perform standard resource search using existing search method
        2. If include_annotations is True:
           - Search user's annotations using AnnotationService
           - Build resource-annotation mapping
        3. Return dict with resources, annotations, and resource_annotation_matches
        
        Args:
            db: Database session
            query: Search query text
            user_id: User ID for annotation filtering
            include_annotations: Whether to include annotation search results
            limit: Maximum number of results per type
            offset: Offset for pagination
            
        Returns:
            Dictionary with keys:
            - resources: List of matching Resource objects
            - total: Total count of matching resources
            - annotations: List of matching Annotation objects (if include_annotations=True)
            - resource_annotation_matches: Dict mapping resource_id to list of annotation_ids
            - facets: Search facets
            - snippets: Search result snippets
        """
        # Build schema SearchQuery object for standard search
        search_query = SearchQuerySchema(
            text=query,
            filters=SearchFilters(),
            limit=limit,
            offset=offset,
            sort_by="relevance",
            sort_dir="desc"
        )
        
        # Perform standard resource search
        search_results = AdvancedSearchService.search(db, search_query)
        
        # Unpack results (handle both 3-tuple and 4-tuple returns)
        if len(search_results) == 4:
            resources, total, facets, snippets = search_results
        else:
            resources, total, facets = search_results
            snippets = {}
        
        # Initialize response
        response = {
            "resources": resources,
            "total": total,
            "facets": facets,
            "snippets": snippets,
            "annotations": [],
            "resource_annotation_matches": {}
        }
        
        if not include_annotations or not query:
            return response
        
        # Search user's annotations
        try:
            from backend.app.services.annotation_service import AnnotationService
            
            annotation_service = AnnotationService(db)
            annotations = annotation_service.search_annotations_fulltext(
                user_id=user_id,
                query=query,
                limit=limit
            )
            
            # Build resource-annotation mapping
            resource_annotation_map: Dict[str, List[str]] = {}
            for ann in annotations:
                resource_id_str = str(ann.resource_id)
                if resource_id_str not in resource_annotation_map:
                    resource_annotation_map[resource_id_str] = []
                resource_annotation_map[resource_id_str].append(str(ann.id))
            
            response["annotations"] = annotations
            response["resource_annotation_matches"] = resource_annotation_map
            
        except Exception as e:
            # Gracefully degrade if annotation search fails
            print(f"Warning: Annotation search failed: {e}")
        
        return response

    @staticmethod
    def _analyze_query(query: str) -> Dict[str, Any]:
        """Analyze query characteristics for adaptive weighting.
        
        Detects:
        - Query length (short: 1-3 words, long: >10 words)
        - Question queries (starts with who/what/when/where/why/how)
        - Technical queries (code patterns, math symbols)
        
        Args:
            query: Search query text
            
        Returns:
            Dictionary with query characteristics:
            - word_count: Number of words in query
            - is_short: True if 1-3 words
            - is_long: True if >10 words
            - is_question: True if starts with question word
            - is_technical: True if contains code/math patterns
        """
        import re
        
        query = (query or "").strip()
        if not query:
            return {
                'word_count': 0,
                'is_short': False,
                'is_long': False,
                'is_question': False,
                'is_technical': False
            }
        
        # Count words
        words = query.split()
        word_count = len(words)
        
        # Detect short/long queries
        is_short = word_count <= 3
        is_long = word_count > 10
        
        # Detect question queries
        question_words = ['who', 'what', 'when', 'where', 'why', 'how']
        is_question = any(query.lower().startswith(qw) for qw in question_words)
        
        # Detect technical queries (code or math)
        code_patterns = [
            r'\b(def|class|function|var|let|const|import|from|return)\b',
            r'[(){}\[\]]',
            r'[=<>!]+',
            r'\b\w+\.\w+\b',
            r'\b\w+\(\)',
        ]
        math_patterns = [
            r'[+\-*/^=]',
            r'\b(sum|integral|derivative|equation|formula)\b',
            r'[∫∑∏√∂∇]',
        ]
        
        is_technical = (
            any(re.search(pattern, query, re.IGNORECASE) for pattern in code_patterns) or
            any(re.search(pattern, query, re.IGNORECASE) for pattern in math_patterns)
        )
        
        return {
            'word_count': word_count,
            'is_short': is_short,
            'is_long': is_long,
            'is_question': is_question,
            'is_technical': is_technical
        }
    
    @staticmethod
    def _search_sparse(
        db: Session,
        query: str,
        limit: int = 100
    ) -> List[Tuple[str, float]]:
        """Execute sparse vector search.
        
        Args:
            db: Database session
            query: Search query text
            limit: Maximum number of results
            
        Returns:
            List of (resource_id, score) tuples sorted by score descending
        """
        # Check if sparse embedding service is available
        if SparseEmbeddingService is None:
            logger.warning("SparseEmbeddingService not available, returning empty results")
            return []
        
        try:
            # Initialize sparse embedding service
            sparse_service = SparseEmbeddingService(db)
            
            # Generate query sparse embedding
            query_sparse = sparse_service.generate_sparse_embedding(query)
            
            if not query_sparse:
                logger.debug("Failed to generate query sparse embedding")
                return []
            
            # Search using sparse vectors
            results = sparse_service.search_by_sparse_vector(
                query_sparse,
                limit=limit,
                min_score=0.0
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Sparse vector search failed: {e}", exc_info=True)
            return []
    
    @staticmethod
    def _fetch_resources_ordered(
        db: Session,
        resource_ids: List[str],
        filters: SearchFilters | None = None
    ) -> List[Resource]:
        """Fetch resources preserving the order specified in resource_ids.
        
        Args:
            db: Database session
            resource_ids: List of resource IDs in desired order
            filters: Optional structured filters to apply
            
        Returns:
            List of Resource objects in the same order as resource_ids
        """
        if not resource_ids:
            return []
        
        try:
            # Fetch resources
            query = db.query(Resource).filter(Resource.id.in_(resource_ids))
            
            # Apply structured filters
            query = _apply_structured_filters(query, filters)
            
            # Fetch all matching resources
            resources = query.all()
            
            # Build resource map
            resource_map = {str(r.id): r for r in resources}
            
            # Return in original order, skipping missing resources
            ordered_resources = []
            for rid in resource_ids:
                if rid in resource_map:
                    ordered_resources.append(resource_map[rid])
            
            return ordered_resources
        
        except Exception as e:
            logger.error(f"Failed to fetch ordered resources: {e}", exc_info=True)
            return []
    
    @staticmethod
    def search_three_way_hybrid(
        db: Session,
        query: DomainSearchQuery | SearchQuerySchema,
        enable_reranking: bool = True,
        adaptive_weighting: bool = True
    ) -> Tuple[List[Resource], int, Facets, Dict[str, str], Dict[str, Any]]:
        """Execute three-way hybrid search with RRF fusion and optional reranking.
        
        Combines three retrieval methods:
        1. FTS5 full-text search (keyword matching)
        2. Dense vector search (semantic similarity)
        3. Sparse vector search (learned keyword importance)
        
        Results are merged using Reciprocal Rank Fusion (RRF) with optional
        query-adaptive weighting, then optionally reranked using ColBERT.
        
        Args:
            db: Database session
            query: SearchQuerySchema or DomainSearchQuery object with query text and configuration
            enable_reranking: Whether to apply ColBERT reranking (default: True)
            adaptive_weighting: Whether to use query-adaptive RRF weights (default: True)
            
        Returns:
            Tuple of:
            - resources: List of Resource objects
            - total: Total count of unique matching resources
            - facets: Faceted search results
            - snippets: Dict mapping resource_id to snippet text
            - metadata: Dict with latency_ms, method_contributions, weights_used
        """
        # Convert schema SearchQuery to domain SearchQuery if needed
        from backend.app.domain.search import SearchQuery as DomainSearchQuery
        
        if not isinstance(query, DomainSearchQuery):
            # It's a schema SearchQuery, convert it
            domain_query = DomainSearchQuery(
                query_text=query.text or "",
                limit=query.limit,
                enable_reranking=enable_reranking,
                adaptive_weights=adaptive_weighting,
                search_method="three_way"
            )
        else:
            domain_query = query
        
        # Delegate to HybridSearchQuery class
        hybrid_query = HybridSearchQuery(
            db=db,
            query=domain_query,
            enable_reranking=enable_reranking,
            adaptive_weighting=adaptive_weighting
        )
        return hybrid_query.execute()
    
    @staticmethod
    def _convert_schema_to_domain_query(schema_query: SearchQuerySchema) -> DomainSearchQuery:
        """Convert schema SearchQuery to domain SearchQuery.
        
        Args:
            schema_query: Pydantic schema SearchQuery from API
            
        Returns:
            Domain SearchQuery object
        """
        return DomainSearchQuery(
            query_text=schema_query.text or "",
            limit=schema_query.limit,
            enable_reranking=True,  # Default value
            adaptive_weights=True,  # Default value
            search_method="hybrid"  # Default to hybrid search
        )
    
    @staticmethod
    def _search_sparse(
        db: Session,
        query: str,
        limit: int = 100
    ) -> List[Tuple[str, float]]:
        """Execute sparse vector search.
        
        Args:
            db: Database session
            query: Search query text
            limit: Maximum number of results
            
        Returns:
            List of (resource_id, score) tuples sorted by score descending
        """
        if not query or SparseEmbeddingService is None:
            return []
        
        try:
            # Initialize sparse embedding service
            sparse_service = SparseEmbeddingService(db)
            
            # Generate query sparse embedding
            query_sparse = sparse_service.generate_sparse_embedding(query)
            
            if not query_sparse:
                logger.debug("Failed to generate query sparse embedding")
                return []
            
            # Search using sparse vectors
            results = sparse_service.search_by_sparse_vector(
                query_sparse,
                limit=limit,
                min_score=0.0
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Sparse vector search failed: {e}", exc_info=True)
            return []
    
    @staticmethod
    def _fetch_resources_ordered(
        db: Session,
        resource_ids: List[str],
        filters: SearchFilters | None = None
    ) -> List[Resource]:
        """Fetch resources preserving the order of resource_ids.
        
        Args:
            db: Database session
            resource_ids: List of resource IDs in desired order
            filters: Optional structured filters to apply
            
        Returns:
            List of Resource objects in the same order as resource_ids
        """
        if not resource_ids:
            return []
        
        try:
            # Fetch resources
            query = db.query(Resource).filter(Resource.id.in_(resource_ids))
            
            # Apply structured filters
            query = _apply_structured_filters(query, filters)
            
            resources = query.all()
            
            # Create mapping for fast lookup
            resource_map = {str(r.id): r for r in resources}
            
            # Preserve order
            ordered_resources = []
            for rid in resource_ids:
                if rid in resource_map:
                    ordered_resources.append(resource_map[rid])
            
            return ordered_resources
        
        except Exception as e:
            logger.error(f"Failed to fetch ordered resources: {e}", exc_info=True)
            return []


