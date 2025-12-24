"""
Neo Alexandria 2.0 - Hybrid Search Methods (Phase 4)

This module provides the core hybrid search implementation for Neo Alexandria 2.0.
It combines traditional FTS5 keyword search with AI-powered vector semantic search
using weighted fusion algorithms for optimal search results.

Related files:
- app/services/search_service.py: Main search service that orchestrates hybrid search
- app/services/ai_core.py: Provides vector embedding generation
- app/schemas/search.py: Search query and result schemas
- app/database/models.py: Resource model with embedding storage

Features:
- Weighted fusion of keyword and semantic search (0.0-1.0 weight range)
- Three search modes: pure keyword (0.0), pure semantic (1.0), balanced hybrid (0.5)
- Score normalization using min-max scaling for fair combination
- Cosine similarity calculation with numpy acceleration
- Graceful fallback when vector search dependencies unavailable
- Efficient brute force similarity suitable for Phase 4 scale
- Comprehensive error handling and edge case management
"""

from __future__ import annotations
from typing import List, Dict, Tuple

from sqlalchemy import func, or_, asc, desc
from sqlalchemy.orm import Session

from ..database.models import Resource
from ..modules.search.schema import SearchQuery, Facets
from ..services.ai_core import generate_embedding

# Import numpy with fallback for vector operations
try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


def fallback_search(db: Session, query: SearchQuery, advanced_search_service) -> Tuple[List[Resource], int, Facets, Dict[str, str]]:
    """Fallback to original FTS/keyword search logic."""
    # Temporarily disable hybrid search to use original logic
    original_weight = query.hybrid_weight
    query.hybrid_weight = None
    
    try:
        # Import here to avoid circular imports
        from ..services.search_service import _detect_fts5, _fts_index_ready, _apply_structured_filters, _compute_facets
        
        use_fts = bool(query.text) and _detect_fts5(db) and _fts_index_ready(db)
        base = db.query(Resource)

        if use_fts and query.text:
            parsed_match = advanced_search_service.parse_search_query(query.text)
            items, total, facets, bm25_scores, snippets = advanced_search_service.fts_search(
                db, parsed_match, query.filters, limit=query.limit, offset=query.offset
            )
            ranked_items = advanced_search_service.rank_results(items, bm25_scores, query.filters)
            return ranked_items, total, facets, snippets
        else:
            # Use existing fallback keyword logic
            q = base
            if query.text:
                # Simplified keyword matching
                like = f"%{query.text.lower()}%"
                q = q.filter(or_(func.lower(Resource.title).like(like), func.lower(Resource.description).like(like)))

            filtered = _apply_structured_filters(q, query.filters)
            total = filtered.count()

            # Sorting
            sort_map = {
                "relevance": Resource.updated_at,
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

            snippets: Dict[str, str] = {}
            if query.text:
                for it in items:
                    snippets[str(it.id)] = advanced_search_service.generate_snippets(
                        (it.description or it.title or ""), query.text
                    )

            return items, total, facets, snippets
    finally:
        # Restore original weight
        query.hybrid_weight = original_weight


def pure_vector_search(db: Session, query: SearchQuery, advanced_search_service) -> Tuple[List[Resource], int, Facets, Dict[str, str]]:
    """Pure semantic vector search."""
    from ..services.search_service import _apply_structured_filters, _compute_facets
    
    # Generate query embedding
    query_embedding = generate_embedding(query.text)
    if not query_embedding:
        # Fallback to keyword search if embedding generation fails
        return fallback_search(db, query, advanced_search_service)
    
    # Get all resources with non-empty embeddings and apply filters
    base_query = db.query(Resource).filter(Resource.embedding.isnot(None))
    filtered_query = _apply_structured_filters(base_query, query.filters)
    
    # Get all candidates for similarity calculation
    candidates = filtered_query.all()
    if not candidates:
        from ..schemas.search import Facets
        empty_facets = Facets()
        return [], 0, empty_facets, {}
    
    # Calculate similarities
    scored_results = []
    for resource in candidates:
        try:
            embedding = resource.embedding
            if embedding and len(embedding) > 0:
                similarity = cosine_similarity(query_embedding, embedding)
                scored_results.append((resource, similarity))
        except Exception:
            continue
    
    # Sort by similarity score
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    # Apply pagination
    total = len(scored_results)
    start_idx = query.offset
    end_idx = start_idx + query.limit
    page_results = scored_results[start_idx:end_idx]
    
    items = [item[0] for item in page_results]
    
    # Compute facets from full filtered set
    facets = _compute_facets(db, filtered_query)
    
    # Generate snippets
    snippets: Dict[str, str] = {}
    for resource in items:
        snippets[str(resource.id)] = advanced_search_service.generate_snippets(
            (resource.description or resource.title or ""), query.text
        )
    
    return items, total, facets, snippets


def fusion_search(db: Session, query: SearchQuery, hybrid_weight: float, advanced_search_service) -> Tuple[List[Resource], int, Facets, Dict[str, str]]:
    """Hybrid search combining FTS and vector similarity with weighted fusion."""
    from ..services.search_service import _detect_fts5, _fts_index_ready, _apply_structured_filters, _compute_facets
    
    # Get FTS results
    fts_results = {}
    fts_snippets = {}
    use_fts = _detect_fts5(db) and _fts_index_ready(db)
    
    if use_fts:
        try:
            parsed_match = advanced_search_service.parse_search_query(query.text)
            # Get larger set for fusion (no pagination yet)
            fts_items, fts_total, fts_facets, fts_bm25_scores, fts_snips = advanced_search_service.fts_search(
                db, parsed_match, query.filters, limit=1000, offset=0
            )
            # Convert BM25 scores to similarity scores (0-1 range, higher is better)
            for item in fts_items:
                bm25_score = fts_bm25_scores.get(str(item.id), 1.0)
                # Normalize BM25: lower is better -> higher is better, scale to 0-1
                similarity = 1.0 / (1.0 + float(bm25_score))
                fts_results[item.id] = (item, similarity)
            fts_snippets = fts_snips
        except Exception:
            pass
    
    # Get vector results
    vector_results = {}
    query_embedding = generate_embedding(query.text)
    if query_embedding:
        try:
            base_query = db.query(Resource).filter(Resource.embedding.isnot(None))
            filtered_query = _apply_structured_filters(base_query, query.filters)
            candidates = filtered_query.all()
            
            for resource in candidates:
                try:
                    embedding = resource.embedding
                    if embedding and len(embedding) > 0:
                        similarity = cosine_similarity(query_embedding, embedding)
                        vector_results[resource.id] = (resource, similarity)
                except Exception:
                    continue
        except Exception:
            pass
    
    # Combine results
    all_resource_ids = set(fts_results.keys()) | set(vector_results.keys())
    if not all_resource_ids:
        from ..schemas.search import Facets
        empty_facets = Facets()
        return [], 0, empty_facets, {}
    
    # Get all FTS scores and vector scores for normalization
    fts_scores = [score for _, score in fts_results.values()]
    vector_scores = [score for _, score in vector_results.values()]
    
    # Normalize scores to 0-1 range
    norm_fts_scores = normalize_scores(fts_scores) if fts_scores else []
    norm_vector_scores = normalize_scores(vector_scores) if vector_scores else []
    
    # Create score mappings
    fts_score_map = {}
    vector_score_map = {}
    
    if norm_fts_scores:
        fts_items = list(fts_results.values())
        for i, (resource, _) in enumerate(fts_items):
            fts_score_map[resource.id] = norm_fts_scores[i]
    
    if norm_vector_scores:
        vector_items = list(vector_results.values())
        for i, (resource, _) in enumerate(vector_items):
            vector_score_map[resource.id] = norm_vector_scores[i]
    
    # Fuse scores
    fusion_results = []
    for resource_id in all_resource_ids:
        fts_score = fts_score_map.get(resource_id, 0.0)
        vector_score = vector_score_map.get(resource_id, 0.0)
        
        # Weighted combination
        final_score = (1.0 - hybrid_weight) * fts_score + hybrid_weight * vector_score
        
        # Get resource object
        resource = None
        if resource_id in fts_results:
            resource = fts_results[resource_id][0]
        elif resource_id in vector_results:
            resource = vector_results[resource_id][0]
        
        if resource:
            fusion_results.append((resource, final_score))
    
    # Sort by final score
    fusion_results.sort(key=lambda x: x[1], reverse=True)
    
    # Apply pagination
    total = len(fusion_results)
    start_idx = query.offset
    end_idx = start_idx + query.limit
    page_results = fusion_results[start_idx:end_idx]
    
    items = [item[0] for item in page_results]
    
    # Compute facets from combined resource set
    all_resources = [item[0] for item in fusion_results]
    resource_ids = [r.id for r in all_resources]
    base_for_facets = db.query(Resource).filter(Resource.id.in_(resource_ids))
    facets = _compute_facets(db, base_for_facets)
    
    # Use FTS snippets if available, otherwise generate new ones
    snippets: Dict[str, str] = {}
    for resource in items:
        resource_id_str = str(resource.id)
        if resource_id_str in fts_snippets:
            snippets[resource_id_str] = fts_snippets[resource_id_str]
        else:
            snippets[resource_id_str] = advanced_search_service.generate_snippets(
                (resource.description or resource.title or ""), query.text
            )
    
    return items, total, facets, snippets


def normalize_scores(scores: List[float]) -> List[float]:
    """Normalize scores to 0-1 range using min-max scaling."""
    if not scores:
        return []
    
    if len(scores) == 1:
        return [1.0]
    
    min_score = min(scores)
    max_score = max(scores)
    
    if min_score == max_score:
        return [1.0] * len(scores)
    
    return [(score - min_score) / (max_score - min_score) for score in scores]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors using numpy."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    if np is None:
        # Fallback implementation without numpy
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    else:
        # Use numpy for efficiency
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norms = np.linalg.norm(v1) * np.linalg.norm(v2)
            
            if norms == 0:
                return 0.0
            
            return float(dot_product / norms)
        except Exception:
            return 0.0
