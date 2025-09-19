"""
Neo Alexandria 2.0 - Hybrid Knowledge Graph Service for Phase 5

Implements hybrid graph scoring that fuses vector similarity, shared canonical
subjects, and classification code matches to build a knowledge graph suitable
for mind map visualization and global overview analysis.

Related files:
- app/schemas/graph.py: Pydantic models for graph data structures
- app/config/settings.py: Graph configuration and weights
- app/database/models.py: Resource model with embeddings and metadata
- app/routers/graph.py: API endpoints using this service
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

# Import numpy with fallback for vector operations
try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings
from backend.app.database import models as db_models
from backend.app.schemas.graph import (
    GraphEdge,
    GraphEdgeDetails,
    GraphNode,
    KnowledgeGraph,
)

logger = logging.getLogger(__name__)
settings = get_settings()


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors using NumPy.
    
    Formula: cos(θ) = (a · b) / (||a|| * ||b||)
    
    Args:
        vec_a: First vector as list of floats
        vec_b: Second vector as list of floats
        
    Returns:
        float: Cosine similarity in range [-1, 1], or 0.0 for zero vectors
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    
    if np is None:
        # Fallback to manual computation if numpy is not available
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        similarity = dot_product / (norm_a * norm_b)
        return max(-1.0, min(1.0, similarity))
        
    try:
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        
        # Check for zero vectors
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        # Compute cosine similarity
        dot_product = np.dot(a, b)
        similarity = dot_product / (norm_a * norm_b)
        
        # Ensure result is in valid range due to floating point precision
        return float(np.clip(similarity, -1.0, 1.0))
        
    except Exception as e:
        logger.warning(f"Error computing cosine similarity: {e}")
        return 0.0


def compute_tag_overlap_score(subjects_a: List[str], subjects_b: List[str]) -> Tuple[float, List[str]]:
    """
    Compute shared canonical subjects score using diminishing returns heuristic.
    
    Score formula: min(1.0, 0.5 + (num_shared - 1) * 0.1)
    This gives:
    - 1 shared subject: 0.5
    - 2 shared subjects: 0.6  
    - 3 shared subjects: 0.7
    - 6+ shared subjects: 1.0 (capped)
    
    Args:
        subjects_a: List of canonical subjects for first resource
        subjects_b: List of canonical subjects for second resource
        
    Returns:
        Tuple of (score, shared_subjects_list)
    """
    if not subjects_a or not subjects_b:
        return 0.0, []
        
    # Convert to sets for intersection, preserving case sensitivity
    set_a = set(subjects_a)
    set_b = set(subjects_b)
    shared = set_a.intersection(set_b)
    
    if not shared:
        return 0.0, []
        
    num_shared = len(shared)
    score = min(1.0, 0.5 + (num_shared - 1) * 0.1)
    shared_list = sorted(list(shared))  # Sort for consistent output
    
    return score, shared_list


def compute_classification_match_score(code_a: Optional[str], code_b: Optional[str]) -> float:
    """
    Compute binary classification code match score.
    
    Args:
        code_a: Classification code for first resource
        code_b: Classification code for second resource
        
    Returns:
        float: 1.0 if codes match and are not None, else 0.0
    """
    if code_a is None or code_b is None:
        return 0.0
    return 1.0 if code_a == code_b else 0.0


def compute_hybrid_weight(
    vector_score: float,
    tag_score: float, 
    classification_score: float,
    vector_weight: float = None,
    tag_weight: float = None,
    classification_weight: float = None,
) -> float:
    """
    Compute hybrid weight by fusing vector, tag, and classification scores.
    
    Normalizes vector score to [0,1] range by clamping negative values to 0,
    then combines all scores using weighted sum.
    
    Args:
        vector_score: Cosine similarity score in [-1, 1]
        tag_score: Tag overlap score in [0, 1]
        classification_score: Classification match score in {0, 1}
        vector_weight: Weight for vector component (uses settings default if None)
        tag_weight: Weight for tag component (uses settings default if None)
        classification_weight: Weight for classification component (uses settings default if None)
        
    Returns:
        float: Combined hybrid weight in [0, 1]
    """
    # Use settings defaults if weights not provided
    if vector_weight is None:
        vector_weight = settings.GRAPH_WEIGHT_VECTOR
    if tag_weight is None:
        tag_weight = settings.GRAPH_WEIGHT_TAGS
    if classification_weight is None:
        classification_weight = settings.GRAPH_WEIGHT_CLASSIFICATION
    
    # Normalize vector score to [0, 1] range by clamping negative values
    normalized_vector_score = max(0.0, vector_score)
    
    # Compute weighted sum
    hybrid_weight = (
        vector_weight * normalized_vector_score +
        tag_weight * tag_score +
        classification_weight * classification_score
    )
    
    # Ensure result is in [0, 1] range
    return max(0.0, min(1.0, hybrid_weight))


def find_hybrid_neighbors(
    db: Session,
    source_resource_id: UUID,
    limit: Optional[int] = None,
) -> KnowledgeGraph:
    """
    Find hybrid-scored neighbors for a given resource.
    
    Gathers candidates from vector similarity, shared subjects, and classification
    matches, then scores and ranks them using the hybrid weighting scheme.
    
    Args:
        db: Database session
        source_resource_id: UUID of the source resource
        limit: Maximum number of neighbors to return (uses setting default if None)
        
    Returns:
        KnowledgeGraph: Graph with source node and its top neighbors
    """
    if limit is None:
        limit = settings.DEFAULT_GRAPH_NEIGHBORS
        
    # Load source resource
    source_resource = db.query(db_models.Resource).filter(
        db_models.Resource.id == source_resource_id
    ).first()
    
    if not source_resource:
        return KnowledgeGraph(nodes=[], edges=[])
    
    # Gather candidates from multiple sources
    candidate_ids: Set[UUID] = set()
    
    # 1. Vector similarity candidates (top 2*limit)
    if source_resource.embedding:
        vector_candidates = db.query(db_models.Resource).filter(
            db_models.Resource.id != source_resource_id,
            db_models.Resource.embedding.isnot(None),
            func.json_array_length(db_models.Resource.embedding) > 0
        ).limit(limit * 2).all()
        
        for candidate in vector_candidates:
            if candidate.embedding:
                candidate_ids.add(candidate.id)
    
    # 2. Shared subject candidates
    if source_resource.subject:
        # Build query to find resources with overlapping subjects
        subject_conditions = []
        for subject in source_resource.subject:
            # Use JSON containment for efficient querying
            subject_conditions.append(
                func.lower(func.cast(db_models.Resource.subject, db_models.String)).like(f"%{subject.lower()}%")
            )
        
        if subject_conditions:
            shared_subject_candidates = db.query(db_models.Resource).filter(
                db_models.Resource.id != source_resource_id,
                or_(*subject_conditions)
            ).all()
            
            for candidate in shared_subject_candidates:
                candidate_ids.add(candidate.id)
    
    # 3. Classification match candidates
    if source_resource.classification_code:
        classification_candidates = db.query(db_models.Resource).filter(
            db_models.Resource.id != source_resource_id,
            db_models.Resource.classification_code == source_resource.classification_code
        ).all()
        
        for candidate in classification_candidates:
            candidate_ids.add(candidate.id)
    
    # Load all candidates
    if not candidate_ids:
        # Return graph with just the source node
        source_node = GraphNode(
            id=source_resource.id,
            title=source_resource.title,
            type=source_resource.type,
            classification_code=source_resource.classification_code,
        )
        return KnowledgeGraph(nodes=[source_node], edges=[])
    
    candidates = db.query(db_models.Resource).filter(
        db_models.Resource.id.in_(candidate_ids)
    ).all()
    
    # Score all candidates
    scored_candidates: List[Tuple[db_models.Resource, float, GraphEdgeDetails]] = []
    
    for candidate in candidates:
        # Vector similarity score
        vector_score = 0.0
        if source_resource.embedding and candidate.embedding:
            vector_score = cosine_similarity(source_resource.embedding, candidate.embedding)
        
        # Tag overlap score
        tag_score, shared_subjects = compute_tag_overlap_score(
            source_resource.subject or [], candidate.subject or []
        )
        
        # Classification match score
        classification_score = compute_classification_match_score(
            source_resource.classification_code, candidate.classification_code
        )
        
        # Compute hybrid weight
        hybrid_weight = compute_hybrid_weight(vector_score, tag_score, classification_score)
        
        # Determine primary connection type
        if classification_score > 0:
            connection_type = "classification"
        elif tag_score > 0:
            connection_type = "topical"
        else:
            connection_type = "semantic"
        
        # Create edge details
        edge_details = GraphEdgeDetails(
            connection_type=connection_type,
            vector_similarity=vector_score if vector_score > 0 else None,
            shared_subjects=shared_subjects,
        )
        
        scored_candidates.append((candidate, hybrid_weight, edge_details))
    
    # Sort by hybrid weight (descending) and take top limit
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    top_candidates = scored_candidates[:limit]
    
    # Build knowledge graph
    nodes = [
        GraphNode(
            id=source_resource.id,
            title=source_resource.title,
            type=source_resource.type,
            classification_code=source_resource.classification_code,
        )
    ]
    
    edges = []
    
    for candidate, weight, details in top_candidates:
        # Add candidate node
        candidate_node = GraphNode(
            id=candidate.id,
            title=candidate.title,
            type=candidate.type,
            classification_code=candidate.classification_code,
        )
        nodes.append(candidate_node)
        
        # Add edge
        edge = GraphEdge(
            source=source_resource.id,
            target=candidate.id,
            weight=weight,
            details=details,
        )
        edges.append(edge)
    
    return KnowledgeGraph(nodes=nodes, edges=edges)


def generate_global_overview(
    db: Session,
    limit: Optional[int] = None,
    vector_threshold: Optional[float] = None,
) -> KnowledgeGraph:
    """
    Generate global overview of strongest connections across the library.
    
    Finds the most significant relationships by combining high vector similarity
    pairs and high tag overlap pairs, then selecting the top hybrid-weighted edges.
    
    Args:
        db: Database session
        limit: Maximum number of edges to return (uses setting default if None)
        vector_threshold: Minimum vector similarity for candidate pairs
        
    Returns:
        KnowledgeGraph: Graph with strongest global connections
    """
    if limit is None:
        limit = settings.GRAPH_OVERVIEW_MAX_EDGES
    if vector_threshold is None:
        vector_threshold = settings.GRAPH_VECTOR_MIN_SIM_THRESHOLD
    
    # Load all resources with embeddings and subjects
    resources = db.query(db_models.Resource).filter(
        or_(
            db_models.Resource.embedding.isnot(None),
            func.json_array_length(db_models.Resource.subject) > 0
        )
    ).all()
    
    if len(resources) < 2:
        return KnowledgeGraph(nodes=[], edges=[])
    
    # Track candidate pairs to avoid duplicates
    candidate_pairs: Set[Tuple[UUID, UUID]] = set()
    
    # Find high vector similarity pairs
    for i, res_a in enumerate(resources):
        if not res_a.embedding:
            continue
            
        for j, res_b in enumerate(resources[i+1:], i+1):
            if not res_b.embedding:
                continue
                
            vector_sim = cosine_similarity(res_a.embedding, res_b.embedding)
            if vector_sim >= vector_threshold:
                # Ensure consistent ordering (smaller UUID first)
                pair = (res_a.id, res_b.id) if res_a.id < res_b.id else (res_b.id, res_a.id)
                candidate_pairs.add(pair)
    
    # Find high tag overlap pairs (top M by shared tag count)
    tag_pairs: List[Tuple[Tuple[UUID, UUID], int]] = []
    
    for i, res_a in enumerate(resources):
        if not res_a.subject:
            continue
            
        for j, res_b in enumerate(resources[i+1:], i+1):
            if not res_b.subject:
                continue
                
            _, shared_subjects = compute_tag_overlap_score(res_a.subject, res_b.subject)
            if shared_subjects:
                # Ensure consistent ordering (smaller UUID first)
                pair = (res_a.id, res_b.id) if res_a.id < res_b.id else (res_b.id, res_a.id)
                tag_pairs.append((pair, len(shared_subjects)))
    
    # Sort tag pairs by shared count and take top M
    tag_pairs.sort(key=lambda x: x[1], reverse=True)
    top_tag_pairs = tag_pairs[:limit]
    
    for pair, _ in top_tag_pairs:
        candidate_pairs.add(pair)
    
    # Score all candidate pairs
    resources_by_id = {res.id: res for res in resources}
    scored_pairs: List[Tuple[Tuple[UUID, UUID], float, GraphEdgeDetails]] = []
    
    for pair in candidate_pairs:
        res_a_id, res_b_id = pair
        res_a = resources_by_id.get(res_a_id)
        res_b = resources_by_id.get(res_b_id)
        
        if not res_a or not res_b:
            continue
        
        # Vector similarity score
        vector_score = 0.0
        if res_a.embedding and res_b.embedding:
            vector_score = cosine_similarity(res_a.embedding, res_b.embedding)
        
        # Tag overlap score
        tag_score, shared_subjects = compute_tag_overlap_score(
            res_a.subject or [], res_b.subject or []
        )
        
        # Classification match score
        classification_score = compute_classification_match_score(
            res_a.classification_code, res_b.classification_code
        )
        
        # Compute hybrid weight
        hybrid_weight = compute_hybrid_weight(vector_score, tag_score, classification_score)
        
        # Skip pairs with very low weights
        if hybrid_weight < 0.1:
            continue
        
        # Determine primary connection type
        if classification_score > 0:
            connection_type = "classification"
        elif tag_score > 0:
            connection_type = "topical"
        else:
            connection_type = "semantic"
        
        # Create edge details
        edge_details = GraphEdgeDetails(
            connection_type=connection_type,
            vector_similarity=vector_score if vector_score > 0 else None,
            shared_subjects=shared_subjects,
        )
        
        scored_pairs.append((pair, hybrid_weight, edge_details))
    
    # Sort by hybrid weight and take top limit
    scored_pairs.sort(key=lambda x: x[1], reverse=True)
    top_pairs = scored_pairs[:limit]
    
    # Build knowledge graph
    involved_node_ids = set()
    edges = []
    
    for pair, weight, details in top_pairs:
        source_id, target_id = pair
        involved_node_ids.add(source_id)
        involved_node_ids.add(target_id)
        
        edge = GraphEdge(
            source=source_id,
            target=target_id,
            weight=weight,
            details=details,
        )
        edges.append(edge)
    
    # Create nodes for all involved resources
    nodes = []
    for res_id in involved_node_ids:
        res = resources_by_id.get(res_id)
        if res:
            node = GraphNode(
                id=res.id,
                title=res.title,
                type=res.type,
                classification_code=res.classification_code,
            )
            nodes.append(node)
    
    return KnowledgeGraph(nodes=nodes, edges=edges)
