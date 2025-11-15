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
from typing import List, Optional, Set, Tuple
from uuid import UUID

# Import numpy with fallback for vector operations
try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None
from sqlalchemy import func, or_
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



# Phase 10: Multi-layer Graph Construction
class GraphService:
    """Service for Phase 10 multi-layer graph construction and neighbor discovery."""
    
    def __init__(self, db: Session):
        self.db = db
        self._graph_cache = None
        self._cache_timestamp = None
    
    def build_multilayer_graph(self, refresh_cache: bool = False):
        """
        Build multi-layer graph with citation, coauthorship, subject, and temporal edges.
        
        Returns a NetworkX MultiGraph object.
        """
        try:
            import networkx as nx
        except ImportError:
            # Return a simple dict-based graph structure if networkx not available
            return {"nodes": [], "edges": []}
        
        # Check cache
        if not refresh_cache and self._graph_cache is not None:
            return self._graph_cache
        
        G = nx.MultiGraph()
        
        # Add all resources as nodes
        from backend.app.database.models import Resource, Citation, GraphEdge, ResourceTaxonomy
        resources = self.db.query(Resource).all()
        
        for resource in resources:
            G.add_node(str(resource.id), 
                      title=resource.title,
                      type=resource.type)
        
        # Add citation edges from Citation table
        citations = self.db.query(Citation).filter(
            Citation.target_resource_id.isnot(None)
        ).all()
        
        for citation in citations:
            G.add_edge(
                str(citation.source_resource_id),
                str(citation.target_resource_id),
                edge_type="citation",
                weight=1.0,
                key="citation"
            )
            
            # Also persist to GraphEdge table if not exists
            existing_edge = self.db.query(GraphEdge).filter(
                GraphEdge.source_resource_id == citation.source_resource_id,
                GraphEdge.target_resource_id == citation.target_resource_id,
                GraphEdge.edge_type == "citation"
            ).first()
            
            if not existing_edge:
                graph_edge = GraphEdge(
                    source_resource_id=citation.source_resource_id,
                    target_resource_id=citation.target_resource_id,
                    edge_type="citation",
                    weight=1.0
                )
                self.db.add(graph_edge)
        
        # Commit citation edges
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        # Create co-authorship edges
        self.create_coauthorship_edges()
        
        # Create subject similarity edges
        self.create_subject_similarity_edges_from_taxonomy()
        
        # Create temporal edges
        self.create_temporal_edges()
        
        # Commit any new edges
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        # Add edges from GraphEdge table
        graph_edges = self.db.query(GraphEdge).all()
        for edge in graph_edges:
            import json
            # Parse metadata if present
            metadata = {}
            if edge.edge_metadata:
                try:
                    metadata = json.loads(edge.edge_metadata) if isinstance(edge.edge_metadata, str) else edge.edge_metadata
                except (json.JSONDecodeError, TypeError):
                    pass
            
            G.add_edge(
                str(edge.source_resource_id),
                str(edge.target_resource_id),
                edge_type=edge.edge_type,
                weight=edge.weight,
                metadata=metadata,
                key=edge.edge_type
            )
        
        # Cache the graph
        self._graph_cache = G
        from datetime import datetime, timezone
        self._cache_timestamp = datetime.now(timezone.utc)
        
        return G
    
    def get_neighbors_multihop(self, resource_id: str, hops: int = 1,
                              edge_types: Optional[List[str]] = None,
                              min_weight: float = 0.0,
                              limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get multi-hop neighbors with filtering and ranking.
        
        Args:
            resource_id: Source resource ID
            hops: Number of hops (1 or 2)
            edge_types: Filter by edge types (e.g., ['citation', 'coauthorship'])
            min_weight: Minimum edge weight threshold
            limit: Maximum number of neighbors to return
            
        Returns:
            List of neighbor dictionaries with paths and scores
        """
        from backend.app.database.models import Resource
        
        G = self.build_multilayer_graph()
        
        if not G.has_node(resource_id):
            return []
        
        neighbors = []
        
        if hops == 1:
            # Get direct neighbors
            for neighbor in G.neighbors(resource_id):
                # Get all edges between source and neighbor
                edge_data = G.get_edge_data(resource_id, neighbor)
                
                for key, data in edge_data.items():
                    edge_type = data.get('edge_type', 'unknown')
                    weight = data.get('weight', 1.0)
                    
                    # Apply filters
                    if edge_types and edge_type not in edge_types:
                        continue
                    if weight < min_weight:
                        continue
                    
                    # Get neighbor resource for quality score
                    neighbor_resource = self.db.query(Resource).filter(
                        Resource.id == neighbor
                    ).first()
                    
                    quality = neighbor_resource.quality_overall if neighbor_resource and neighbor_resource.quality_overall else 0.5
                    novelty = 0.5  # Default novelty score
                    
                    # Calculate combined score
                    path_strength = weight
                    score = 0.5 * path_strength + 0.3 * quality + 0.2 * novelty
                    
                    neighbors.append({
                        'resource_id': neighbor,
                        'hops': 1,
                        'distance': 1,
                        'path': [resource_id, neighbor],
                        'edge_types': [edge_type],
                        'total_weight': weight,
                        'path_strength': path_strength,
                        'quality': quality,
                        'novelty': novelty,
                        'score': score,
                        'edge_type': edge_type,
                        'weight': weight,
                        'intermediate': None
                    })
        
        elif hops == 2:
            # Get 2-hop neighbors
            visited = {resource_id}
            
            for neighbor1 in G.neighbors(resource_id):
                if neighbor1 in visited:
                    continue
                    
                # Get edge data for first hop
                edge_data_1 = G.get_edge_data(resource_id, neighbor1)
                
                for key1, data1 in edge_data_1.items():
                    edge_type_1 = data1.get('edge_type', 'unknown')
                    weight_1 = data1.get('weight', 1.0)
                    
                    if edge_types and edge_type_1 not in edge_types:
                        continue
                    if weight_1 < min_weight:
                        continue
                    
                    # Explore second hop
                    for neighbor2 in G.neighbors(neighbor1):
                        if neighbor2 == resource_id or neighbor2 in visited:
                            continue
                        
                        edge_data_2 = G.get_edge_data(neighbor1, neighbor2)
                        
                        for key2, data2 in edge_data_2.items():
                            edge_type_2 = data2.get('edge_type', 'unknown')
                            weight_2 = data2.get('weight', 1.0)
                            
                            if edge_types and edge_type_2 not in edge_types:
                                continue
                            if weight_2 < min_weight:
                                continue
                            
                            total_weight = weight_1 * weight_2
                            path_strength = total_weight
                            
                            # Get neighbor resource for quality score
                            neighbor_resource = self.db.query(Resource).filter(
                                Resource.id == neighbor2
                            ).first()
                            
                            quality = neighbor_resource.quality_overall if neighbor_resource and neighbor_resource.quality_overall else 0.5
                            novelty = 0.5  # Default novelty score
                            
                            # Calculate combined score
                            score = 0.5 * path_strength + 0.3 * quality + 0.2 * novelty
                            
                            neighbors.append({
                                'resource_id': neighbor2,
                                'hops': 2,
                                'distance': 2,
                                'path': [resource_id, neighbor1, neighbor2],
                                'edge_types': [edge_type_1, edge_type_2],
                                'total_weight': total_weight,
                                'path_strength': path_strength,
                                'quality': quality,
                                'novelty': novelty,
                                'score': score,
                                'intermediate': neighbor1,
                                'intermediate_nodes': [neighbor1]
                            })
        
        # Sort by score descending (not just total_weight)
        neighbors.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Apply limit
        if limit:
            neighbors = neighbors[:limit]
        
        return neighbors

    
    def create_coauthorship_edges(self):
        """Create co-authorship edges for resources sharing authors."""
        from backend.app.database.models import Resource, GraphEdge
        import json
        
        # Get all resources with authors
        resources = self.db.query(Resource).filter(
            Resource.authors.isnot(None)
        ).all()
        
        # Build resource to authors mapping
        resource_authors = {}
        for resource in resources:
            if resource.authors:
                try:
                    authors_list = json.loads(resource.authors) if isinstance(resource.authors, str) else resource.authors
                    author_names = []
                    for author_obj in authors_list:
                        author_name = author_obj.get('name') if isinstance(author_obj, dict) else str(author_obj)
                        author_names.append(author_name)
                    resource_authors[resource.id] = set(author_names)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Create edges between resources sharing authors
        edges_created = 0
        resource_ids = list(resource_authors.keys())
        
        for i, res_id_1 in enumerate(resource_ids):
            for res_id_2 in resource_ids[i+1:]:
                # Calculate shared authors
                shared_authors = resource_authors[res_id_1].intersection(resource_authors[res_id_2])
                
                if len(shared_authors) > 0:
                    # Check if edge already exists
                    existing = self.db.query(GraphEdge).filter(
                        GraphEdge.source_resource_id == res_id_1,
                        GraphEdge.target_resource_id == res_id_2,
                        GraphEdge.edge_type == "co_authorship"
                    ).first()
                    
                    if not existing:
                        # Weight inversely proportional to number of shared authors
                        weight = 1.0 / len(shared_authors)
                        edge = GraphEdge(
                            source_resource_id=res_id_1,
                            target_resource_id=res_id_2,
                            edge_type="co_authorship",
                            weight=weight
                        )
                        self.db.add(edge)
                        edges_created += 1
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        return edges_created
    
    def create_subject_similarity_edges(self, min_shared_subjects: int = 1):
        """Create subject similarity edges for resources sharing subjects."""
        from backend.app.database.models import Resource, GraphEdge
        
        # Get all resources with subjects
        resources = self.db.query(Resource).filter(
            Resource.subject.isnot(None)
        ).all()
        
        edges_created = 0
        for i, res1 in enumerate(resources):
            if not res1.subject or len(res1.subject) == 0:
                continue
                
            for res2 in resources[i+1:]:
                if not res2.subject or len(res2.subject) == 0:
                    continue
                
                # Calculate shared subjects
                shared = set(res1.subject).intersection(set(res2.subject))
                if len(shared) >= min_shared_subjects:
                    # Check if edge already exists
                    existing = self.db.query(GraphEdge).filter(
                        GraphEdge.source_resource_id == res1.id,
                        GraphEdge.target_resource_id == res2.id,
                        GraphEdge.edge_type == "subject"
                    ).first()
                    
                    if not existing:
                        # Weight based on number of shared subjects
                        weight = min(1.0, len(shared) * 0.3)
                        edge = GraphEdge(
                            source_resource_id=res1.id,
                            target_resource_id=res2.id,
                            edge_type="subject",
                            weight=weight
                        )
                        self.db.add(edge)
                        edges_created += 1
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        return edges_created
    
    def create_subject_similarity_edges_from_taxonomy(self):
        """Create subject similarity edges from ResourceTaxonomy associations."""
        from backend.app.database.models import Resource, GraphEdge, ResourceTaxonomy
        
        # Get all resource-taxonomy associations
        associations = self.db.query(ResourceTaxonomy).all()
        
        # Build taxonomy to resources mapping
        taxonomy_resources = {}
        for assoc in associations:
            if assoc.taxonomy_node_id not in taxonomy_resources:
                taxonomy_resources[assoc.taxonomy_node_id] = []
            taxonomy_resources[assoc.taxonomy_node_id].append(assoc.resource_id)
        
        # Create edges between resources sharing taxonomy nodes
        edges_created = 0
        for taxonomy_id, resource_ids in taxonomy_resources.items():
            if len(resource_ids) < 2:
                continue
            
            # Create edges between all pairs
            for i, res_id_1 in enumerate(resource_ids):
                for res_id_2 in resource_ids[i+1:]:
                    # Check if edge already exists
                    existing = self.db.query(GraphEdge).filter(
                        GraphEdge.source_resource_id == res_id_1,
                        GraphEdge.target_resource_id == res_id_2,
                        GraphEdge.edge_type == "subject_similarity"
                    ).first()
                    
                    if not existing:
                        # Fixed weight for subject similarity
                        weight = 0.5
                        edge = GraphEdge(
                            source_resource_id=res_id_1,
                            target_resource_id=res_id_2,
                            edge_type="subject_similarity",
                            weight=weight
                        )
                        self.db.add(edge)
                        edges_created += 1
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        return edges_created
    
    def create_temporal_edges(self, max_year_diff: int = 0):
        """Create temporal edges for resources published close in time."""
        from backend.app.database.models import Resource, GraphEdge
        import json
        
        # Get all resources with publication years
        resources = self.db.query(Resource).filter(
            Resource.publication_year.isnot(None)
        ).order_by(Resource.publication_year).all()
        
        edges_created = 0
        for i, res1 in enumerate(resources):
            for res2 in resources[i+1:]:
                year_diff = abs(res1.publication_year - res2.publication_year)
                
                if year_diff <= max_year_diff:
                    # Check if edge already exists
                    existing = self.db.query(GraphEdge).filter(
                        GraphEdge.source_resource_id == res1.id,
                        GraphEdge.target_resource_id == res2.id,
                        GraphEdge.edge_type == "temporal"
                    ).first()
                    
                    if not existing:
                        # Fixed weight for temporal edges (same year)
                        weight = 0.3
                        # Store metadata as JSON string
                        edge_metadata = json.dumps({"year": res1.publication_year})
                        edge = GraphEdge(
                            source_resource_id=res1.id,
                            target_resource_id=res2.id,
                            edge_type="temporal",
                            weight=weight,
                            edge_metadata=edge_metadata
                        )
                        self.db.add(edge)
                        edges_created += 1
                else:
                    # Resources are sorted by year, so we can break
                    break
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        return edges_created
