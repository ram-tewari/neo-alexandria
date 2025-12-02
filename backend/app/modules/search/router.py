"""
Search Module Router

API endpoints for search functionality including:
- Standard search with FTS5 and filters
- Three-way hybrid search with RRF fusion
- Search method comparison
- Search quality evaluation
- Batch sparse embedding generation
- Module health check
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)

from backend.app.shared.database import get_sync_db
from backend.app.shared.event_bus import event_bus
from backend.app.modules.search.schema import (
    SearchQuery, 
    SearchResults,
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
from backend.app.schemas.resource import ResourceRead
from backend.app.services.search_service import AdvancedSearchService
from backend.app.services.sparse_embedding_service import SparseEmbeddingService
from backend.app.database.models import Resource


router = APIRouter(prefix="", tags=["search"])


@router.post("/search", response_model=SearchResults, status_code=status.HTTP_200_OK)
def search_endpoint(payload: SearchQuery, db: Session = Depends(get_sync_db)):
    """
    Execute standard search with FTS5, filters, and pagination.
    
    Supports:
    - Full-text search with SQLite FTS5 or PostgreSQL tsvector
    - Structured filtering by classification, type, language, etc.
    - Pagination and sorting
    - Faceted search results
    - Search result snippets
    """
    try:
        result = AdvancedSearchService.search(db, payload)
        if len(result) == 4:
            items, total, facets, snippets = result
        else:
            items, total, facets = result
            snippets = {}
        items_read = [ResourceRead.model_validate(it) for it in items]
        return SearchResults(total=total, items=items_read, facets=facets, snippets=snippets)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed") from exc


@router.get("/search/three-way-hybrid", response_model=ThreeWayHybridResults, status_code=status.HTTP_200_OK)
def three_way_hybrid_search_endpoint(
    query: str = Query(..., description="Search query text"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    enable_reranking: bool = Query(True, description="Apply ColBERT reranking"),
    adaptive_weighting: bool = Query(True, description="Use query-adaptive RRF weights"),
    hybrid_weight: Optional[float] = Query(None, ge=0.0, le=1.0, description="Fusion weight (for compatibility)"),
    db: Session = Depends(get_sync_db)
):
    """
    Execute three-way hybrid search combining FTS5, dense vectors, and sparse vectors.
    
    This endpoint implements state-of-the-art search by:
    1. Executing three retrieval methods in parallel (FTS5, dense, sparse)
    2. Merging results using Reciprocal Rank Fusion (RRF)
    3. Applying query-adaptive weighting based on query characteristics
    4. Optionally reranking top results using ColBERT cross-encoder
    
    Returns results with detailed metadata including latency, method contributions,
    and the weights used for fusion.
    """
    try:
        search_query = SearchQuery(
            text=query,
            limit=limit,
            offset=offset,
            hybrid_weight=hybrid_weight
        )
        
        resources, total, facets, snippets, metadata = AdvancedSearchService.search_three_way_hybrid(
            db=db,
            query=search_query,
            enable_reranking=enable_reranking,
            adaptive_weighting=adaptive_weighting
        )
        
        items_read = [ResourceRead.model_validate(resource) for resource in resources]
        
        return ThreeWayHybridResults(
            total=total,
            items=items_read,
            facets=facets,
            snippets=snippets,
            latency_ms=metadata.get('latency_ms', 0.0),
            method_contributions=MethodContributions(**metadata.get('method_contributions', {})),
            weights_used=metadata.get('weights_used', [1.0/3, 1.0/3, 1.0/3])
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Three-way hybrid search failed"
        ) from exc


@router.get("/search/compare-methods", response_model=ComparisonResults, status_code=status.HTTP_200_OK)
def compare_search_methods_endpoint(
    query: str = Query(..., description="Search query text"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per method"),
    db: Session = Depends(get_sync_db)
):
    """
    Compare different search methods side-by-side for debugging and analysis.
    
    Executes all available search methods:
    - FTS5 only (keyword matching)
    - Dense only (semantic similarity)
    - Sparse only (learned keyword importance)
    - Two-way hybrid (FTS5 + dense)
    - Three-way hybrid (FTS5 + dense + sparse with RRF)
    - Three-way with reranking (+ ColBERT reranking)
    
    Returns results from each method with latency metrics for performance comparison.
    """
    methods_results = {}
    base_query = SearchQuery(text=query, limit=limit, offset=0)
    
    # 1. FTS5 Only
    try:
        start = time.time()
        fts5_query = SearchQuery(text=query, limit=limit, offset=0, hybrid_weight=0.0)
        result = AdvancedSearchService.search(db, fts5_query)
        latency = (time.time() - start) * 1000
        
        if len(result) == 4:
            items, total, _, _ = result
        else:
            items, total, _ = result
        
        items_read = [ResourceRead.model_validate(it) for it in items]
        methods_results['fts5_only'] = ComparisonMethodResults(
            results=items_read,
            latency_ms=latency,
            total=total
        )
    except Exception:
        methods_results['fts5_only'] = ComparisonMethodResults(
            results=[],
            latency_ms=0.0,
            total=0
        )
    
    # 2. Dense Only
    try:
        start = time.time()
        dense_query = SearchQuery(text=query, limit=limit, offset=0, hybrid_weight=1.0)
        result = AdvancedSearchService.search(db, dense_query)
        latency = (time.time() - start) * 1000
        
        if len(result) == 4:
            items, total, _, _ = result
        else:
            items, total, _ = result
        
        items_read = [ResourceRead.model_validate(it) for it in items]
        methods_results['dense_only'] = ComparisonMethodResults(
            results=items_read,
            latency_ms=latency,
            total=total
        )
    except Exception:
        methods_results['dense_only'] = ComparisonMethodResults(
            results=[],
            latency_ms=0.0,
            total=0
        )
    
    # 3. Sparse Only
    try:
        start = time.time()
        sparse_service = SparseEmbeddingService(db)
        query_sparse = sparse_service.generate_sparse_embedding(query)
        
        if query_sparse:
            sparse_results = sparse_service.search_by_sparse_vector(query_sparse, limit=limit)
            latency = (time.time() - start) * 1000
            
            resource_ids = [rid for rid, _ in sparse_results]
            resources = db.query(Resource).filter(
                Resource.id.in_(resource_ids)
            ).all()
            
            id_to_resource = {str(r.id): r for r in resources}
            ordered_resources = [id_to_resource[rid] for rid in resource_ids if rid in id_to_resource]
            
            items_read = [ResourceRead.model_validate(r) for r in ordered_resources]
            methods_results['sparse_only'] = ComparisonMethodResults(
                results=items_read,
                latency_ms=latency,
                total=len(sparse_results)
            )
        else:
            methods_results['sparse_only'] = ComparisonMethodResults(
                results=[],
                latency_ms=0.0,
                total=0
            )
    except Exception:
        methods_results['sparse_only'] = ComparisonMethodResults(
            results=[],
            latency_ms=0.0,
            total=0
        )
    
    # 4. Two-Way Hybrid
    try:
        start = time.time()
        result = AdvancedSearchService.hybrid_search(db, base_query, hybrid_weight=0.5)
        latency = (time.time() - start) * 1000
        
        if len(result) == 4:
            items, total, _, _ = result
        else:
            items, total, _ = result
        
        items_read = [ResourceRead.model_validate(it) for it in items]
        methods_results['two_way_hybrid'] = ComparisonMethodResults(
            results=items_read,
            latency_ms=latency,
            total=total
        )
    except Exception:
        methods_results['two_way_hybrid'] = ComparisonMethodResults(
            results=[],
            latency_ms=0.0,
            total=0
        )
    
    # 5. Three-Way Hybrid
    try:
        start = time.time()
        resources, total, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
            db=db,
            query=base_query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        latency = (time.time() - start) * 1000
        
        items_read = [ResourceRead.model_validate(r) for r in resources]
        methods_results['three_way_hybrid'] = ComparisonMethodResults(
            results=items_read,
            latency_ms=latency,
            total=total
        )
    except Exception:
        methods_results['three_way_hybrid'] = ComparisonMethodResults(
            results=[],
            latency_ms=0.0,
            total=0
        )
    
    # 6. Three-Way with Reranking
    try:
        start = time.time()
        resources, total, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
            db=db,
            query=base_query,
            enable_reranking=True,
            adaptive_weighting=True
        )
        latency = (time.time() - start) * 1000
        
        items_read = [ResourceRead.model_validate(r) for r in resources]
        methods_results['three_way_reranked'] = ComparisonMethodResults(
            results=items_read,
            latency_ms=latency,
            total=total
        )
    except Exception:
        methods_results['three_way_reranked'] = ComparisonMethodResults(
            results=[],
            latency_ms=0.0,
            total=0
        )
    
    return ComparisonResults(
        query=query,
        methods=methods_results
    )


@router.post("/search/evaluate", response_model=EvaluationResults, status_code=status.HTTP_200_OK)
def evaluate_search_endpoint(
    payload: EvaluationRequest,
    db: Session = Depends(get_sync_db)
):
    """
    Evaluate search quality using information retrieval metrics.
    
    Accepts a query and relevance judgments (ground truth) and computes:
    - nDCG@20: Normalized Discounted Cumulative Gain
    - Recall@20: Proportion of relevant documents retrieved
    - Precision@20: Proportion of retrieved documents that are relevant
    - MRR: Mean Reciprocal Rank (position of first relevant result)
    
    Relevance scale:
    - 0: Not relevant
    - 1: Marginally relevant
    - 2: Relevant
    - 3: Highly relevant
    
    Optionally compares against a baseline (two-way hybrid) to measure improvement.
    """
    try:
        from backend.app.services.search_metrics_service import SearchMetricsService
        
        search_query = SearchQuery(text=payload.query, limit=100, offset=0)
        resources, _, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
            db=db,
            query=search_query,
            enable_reranking=True,
            adaptive_weighting=True
        )
        
        ranked_results = [str(r.id) for r in resources]
        metrics_service = SearchMetricsService()
        
        ndcg = metrics_service.compute_ndcg(
            ranked_results=ranked_results,
            relevance_judgments=payload.relevance_judgments,
            k=20
        )
        
        relevant_docs = [doc_id for doc_id, rel in payload.relevance_judgments.items() if rel > 0]
        
        recall = metrics_service.compute_recall_at_k(
            ranked_results=ranked_results,
            relevant_docs=relevant_docs,
            k=20
        )
        
        precision = metrics_service.compute_precision_at_k(
            ranked_results=ranked_results,
            relevant_docs=relevant_docs,
            k=20
        )
        
        mrr = metrics_service.compute_mean_reciprocal_rank(
            ranked_results=ranked_results,
            relevant_docs=relevant_docs
        )
        
        metrics = EvaluationMetrics(
            ndcg_at_20=ndcg,
            recall_at_20=recall,
            precision_at_20=precision,
            mrr=mrr
        )
        
        baseline_comparison = None
        try:
            baseline_resources, _, _, _ = AdvancedSearchService.hybrid_search(
                db=db,
                query=search_query,
                hybrid_weight=0.5
            )
            
            baseline_ranked = [str(r.id) for r in baseline_resources]
            baseline_ndcg = metrics_service.compute_ndcg(
                ranked_results=baseline_ranked,
                relevance_judgments=payload.relevance_judgments,
                k=20
            )
            
            improvement = (ndcg - baseline_ndcg) / baseline_ndcg if baseline_ndcg > 0 else 0.0
            
            baseline_comparison = {
                'two_way_ndcg': baseline_ndcg,
                'improvement': improvement
            }
        except Exception:
            pass
        
        return EvaluationResults(
            query=payload.query,
            metrics=metrics,
            baseline_comparison=baseline_comparison
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search evaluation failed"
        ) from exc


@router.post("/admin/sparse-embeddings/generate", response_model=BatchSparseEmbeddingResponse, status_code=status.HTTP_200_OK)
def batch_generate_sparse_embeddings_endpoint(
    payload: BatchSparseEmbeddingRequest,
    db: Session = Depends(get_sync_db)
):
    """
    Queue batch generation of sparse embeddings for existing resources.
    
    This endpoint initiates a background task to generate sparse embeddings for:
    - Specific resources (if resource_ids provided)
    - All resources without sparse embeddings (if resource_ids is None)
    
    The batch processing:
    - Uses configurable batch size (32 for GPU, 8 for CPU)
    - Commits every 100 resources for reliability
    - Logs progress updates
    - Can be resumed if interrupted
    
    Returns a job ID and estimated duration for tracking progress.
    """
    try:
        import uuid
        
        sparse_service = SparseEmbeddingService(db)
        
        if payload.resource_ids:
            resources_query = db.query(Resource).filter(
                Resource.id.in_(payload.resource_ids)
            )
            resources_to_process = resources_query.count()
        else:
            resources_query = db.query(Resource).filter(
                or_(
                    Resource.sparse_embedding.is_(None),
                    Resource.sparse_embedding == ''
                )
            )
            resources_to_process = resources_query.count()
        
        job_id = str(uuid.uuid4())
        estimated_duration_minutes = max(1, resources_to_process // 60)
        
        try:
            if payload.resource_ids:
                sparse_service.batch_update_sparse_embeddings(
                    resource_ids=payload.resource_ids,
                    batch_size=payload.batch_size or 32
                )
            else:
                sparse_service.batch_update_sparse_embeddings(
                    resource_ids=None,
                    batch_size=payload.batch_size or 32
                )
            
            status_msg = "completed"
        except Exception as e:
            logger.error(f"Batch sparse embedding generation failed: {e}", exc_info=True)
            status_msg = "failed"
        
        return BatchSparseEmbeddingResponse(
            status=status_msg,
            job_id=job_id,
            estimated_duration_minutes=estimated_duration_minutes,
            resources_to_process=resources_to_process
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch sparse embedding generation failed"
        ) from exc


@router.get("/search/health", response_model=Dict[str, Any])
async def health_check(db: Session = Depends(get_sync_db)) -> Dict[str, Any]:
    """
    Health check endpoint for Search module.
    
    Verifies:
    - Database connectivity
    - Search service availability
    - Module version and status
    
    Returns:
        Dictionary with health status including:
        - status: "healthy" or "unhealthy"
        - module: Module name and version
        - database: Database connection status
        - services: Search service availability
        - timestamp: When the check was performed
    """
    try:
        # Check database connectivity
        try:
            db.execute("SELECT 1")
            db_healthy = True
            db_message = "Database connection healthy"
        except Exception as e:
            db_healthy = False
            db_message = f"Database connection failed: {str(e)}"
        
        # Check search service availability
        try:
            from backend.app.services.search_service import AdvancedSearchService
            search_available = True
            search_message = "Search service available"
        except Exception as e:
            search_available = False
            search_message = f"Search service unavailable: {str(e)}"
        
        # Determine overall status
        overall_healthy = db_healthy and search_available
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "module": {
                "name": "search",
                "version": "1.0.0",
                "domain": "search"
            },
            "database": {
                "healthy": db_healthy,
                "message": db_message
            },
            "services": {
                "search_service": {
                    "available": search_available,
                    "message": search_message
                }
            },
            "event_handlers": {
                "registered": False,
                "count": 0,
                "events": []
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
