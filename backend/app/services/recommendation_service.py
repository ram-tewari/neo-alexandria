"""
Recommendation service for Phase 5 and Phase 10.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from uuid import UUID
import numpy as np


class RecommendationService:
    """Service for generating recommendations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_recommendations(self, resource_id: UUID, 
                                limit: int = 10, 
                                strategy: str = "hybrid",
                                min_quality: Optional[float] = None) -> List[Dict[str, Any]]:
        """Generate recommendations using specified strategy."""
        return []
    
    def get_graph_based_recommendations(self, resource_id: UUID, 
                                       limit: int = 10,
                                       min_quality: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get recommendations based on graph structure."""
        return get_graph_based_recommendations(self.db, resource_id, limit, min_quality=min_quality)
    
    def generate_recommendations_with_graph_fusion(self, resource_id: UUID,
                                                  limit: int = 10,
                                                  min_quality: Optional[float] = None) -> List[Dict[str, Any]]:
        """Generate recommendations using graph fusion."""
        return generate_recommendations_with_graph_fusion(self.db, resource_id, limit, min_quality=min_quality)
    
    def recommend_based_on_annotations(self, user_id: str, 
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """Generate recommendations based on user annotations."""
        return []


# Module-level functions for backward compatibility
def get_graph_based_recommendations(db: Session, resource_id: UUID, 
                                   limit: int = 10,
                                   min_plausibility: float = 0.0,
                                   min_quality: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Get recommendations based on graph structure.
    
    Combines 2-hop graph neighbors and LBD hypotheses to generate recommendations.
    
    Args:
        db: Database session
        resource_id: Resource ID to generate recommendations for
        limit: Maximum number of recommendations to return
        min_plausibility: Minimum plausibility score for hypotheses
        min_quality: Optional minimum quality threshold to filter recommendations
        
    Returns:
        List of recommendation dictionaries with graph-based scores
    """
    from backend.app.services.graph_service import GraphService
    from backend.app.services.lbd_service import LBDService
    
    recommendations = []
    seen_ids = set()
    
    # Get 2-hop neighbors from graph
    graph_service = GraphService(db)
    neighbors = graph_service.get_neighbors_multihop(
        resource_id=str(resource_id),
        hops=2,
        limit=limit * 2
    )
    
    for neighbor in neighbors:
        neighbor_id = neighbor.get('resource_id')
        if neighbor_id and neighbor_id not in seen_ids:
            seen_ids.add(neighbor_id)
            recommendations.append({
                'resource_id': neighbor_id,
                'id': neighbor_id,
                'score': neighbor.get('score', 0.5),
                'path_strength': neighbor.get('path_strength', 0.5),
                'distance': neighbor.get('distance', 2),
                'hops': neighbor.get('hops', 2)
            })
    
    # Get LBD hypotheses
    lbd_service = LBDService(db)
    hypotheses = lbd_service.open_discovery(
        start_resource_id=str(resource_id),
        limit=limit,
        min_plausibility=min_plausibility
    )
    
    for hypothesis in hypotheses:
        c_resource_id = hypothesis.get('c_resource_id')
        plausibility = hypothesis.get('plausibility_score', 0.0)
        
        if c_resource_id and c_resource_id not in seen_ids and plausibility >= min_plausibility:
            seen_ids.add(c_resource_id)
            recommendations.append({
                'resource_id': c_resource_id,
                'id': c_resource_id,
                'score': plausibility,
                'plausibility_score': plausibility,
                'hypothesis': True
            })
    
    # Apply quality boosting and filtering
    from backend.app.database.models import Resource
    filtered_recommendations = []
    for rec in recommendations:
        res_id = rec.get('resource_id')
        if res_id:
            candidate_resource = db.query(Resource).filter(Resource.id == res_id).first()
            if candidate_resource:
                # Exclude quality outliers
                if candidate_resource.is_quality_outlier:
                    continue
                # Apply quality threshold if specified
                if min_quality is not None and candidate_resource.quality_overall is not None:
                    if candidate_resource.quality_overall < min_quality:
                        continue
                
                # Apply quality boosting
                if candidate_resource.quality_overall is not None:
                    quality_boost = 1.2 if candidate_resource.quality_overall > 0.8 else 1.0
                    # Incorporate quality weighting into final score
                    rec['score'] = rec['score'] * quality_boost * (0.7 + 0.3 * candidate_resource.quality_overall)
                    rec['quality_boost'] = quality_boost
            
            filtered_recommendations.append(rec)
    
    # Sort by score (descending)
    filtered_recommendations.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    return filtered_recommendations[:limit]


def generate_recommendations_with_graph_fusion(db: Session, resource_id: UUID,
                                              limit: int = 10,
                                              content_weight: float = 0.7,
                                              graph_weight: float = None,
                                              min_quality: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Generate recommendations using graph fusion with fixed weights.
    
    Note: content_weight and graph_weight parameters are accepted for backward
    compatibility but are ignored. The function uses fixed fusion weights:
    70% content-based, 30% graph-based.
    
    Args:
        db: Database session
        resource_id: Resource ID to generate recommendations for
        limit: Maximum number of recommendations to return
        content_weight: Ignored (kept for backward compatibility)
        graph_weight: Ignored (kept for backward compatibility)
        min_quality: Optional minimum quality threshold to filter recommendations
        
    Returns:
        List of recommendation dictionaries with fused scores
    """
    from backend.app.services.graph_service import GraphService
    from backend.app.services.lbd_service import LBDService
    from backend.app.database.models import Resource
    
    # Fixed fusion weights (70% content, 30% graph)
    CONTENT_WEIGHT = 0.7
    GRAPH_WEIGHT = 0.3
    
    # Get content-based recommendations (using embeddings)
    content_recs = []
    source_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if source_resource and source_resource.embedding:
        # Get similar resources by embedding
        candidates = db.query(Resource).filter(
            Resource.id != resource_id,
            Resource.embedding.isnot(None)
        ).limit(limit * 2).all()
        
        for candidate in candidates:
            if candidate.embedding:
                similarity = cosine_similarity(source_resource.embedding, candidate.embedding)
                if similarity > 0:
                    content_recs.append({
                        'resource_id': str(candidate.id),
                        'id': str(candidate.id),
                        'score': similarity,
                        'similarity': similarity,
                        'resource': {
                            'id': str(candidate.id),
                            'title': candidate.title,
                            'type': candidate.type
                        }
                    })
    
    # Get graph-based recommendations
    graph_service = GraphService(db)
    graph_neighbors = graph_service.get_neighbors_multihop(
        resource_id=str(resource_id),
        hops=2,
        limit=limit * 2
    )
    
    graph_recs = []
    for neighbor in graph_neighbors:
        graph_recs.append({
            'resource_id': neighbor.get('resource_id'),
            'id': neighbor.get('resource_id'),
            'score': neighbor.get('score', 0.5),
            'path_strength': neighbor.get('path_strength', 0.5)
        })
    
    # Get LBD hypotheses
    lbd_service = LBDService(db)
    hypotheses = lbd_service.open_discovery(
        start_resource_id=str(resource_id),
        limit=limit
    )
    
    for hypothesis in hypotheses:
        c_resource_id = hypothesis.get('c_resource_id')
        if c_resource_id:
            graph_recs.append({
                'resource_id': c_resource_id,
                'id': c_resource_id,
                'score': hypothesis.get('plausibility_score', 0.5),
                'plausibility_score': hypothesis.get('plausibility_score', 0.5)
            })
    
    # Fuse recommendations
    fused_scores = {}
    
    # Add content-based scores
    for rec in content_recs:
        res_id = rec.get('resource_id') or rec.get('id')
        if res_id:
            fused_scores[res_id] = {
                'resource_id': res_id,
                'id': res_id,
                'content_score': rec.get('score', 0),
                'graph_score': 0,
                'resource': rec.get('resource')
            }
    
    # Add graph-based scores
    for rec in graph_recs:
        res_id = rec.get('resource_id') or rec.get('id')
        if res_id:
            if res_id not in fused_scores:
                fused_scores[res_id] = {
                    'resource_id': res_id,
                    'id': res_id,
                    'content_score': 0,
                    'graph_score': rec.get('score', 0)
                }
            else:
                fused_scores[res_id]['graph_score'] = max(
                    fused_scores[res_id]['graph_score'],
                    rec.get('score', 0)
                )
    
    # Calculate fused scores with quality boosting
    fused_recs = []
    for res_id, scores in fused_scores.items():
        fused_score = (
            CONTENT_WEIGHT * scores['content_score'] +
            GRAPH_WEIGHT * scores['graph_score']
        )
        
        # Apply quality boost for high-quality resources
        quality_boost = 1.0
        candidate_resource = db.query(Resource).filter(Resource.id == res_id).first()
        if candidate_resource and candidate_resource.quality_overall is not None:
            if candidate_resource.quality_overall > 0.8:
                quality_boost = 1.2
            # Incorporate quality weighting into final score
            fused_score = fused_score * quality_boost * (0.7 + 0.3 * candidate_resource.quality_overall)
        
        rec = {
            'resource_id': res_id,
            'id': res_id,
            'score': fused_score,
            'similarity': fused_score,
            'content_score': scores['content_score'],
            'graph_score': scores['graph_score'],
            'quality_boost': quality_boost
        }
        
        if scores.get('resource'):
            rec['resource'] = scores['resource']
        
        fused_recs.append(rec)
    
    # Filter out quality outliers and apply quality threshold
    filtered_recs = []
    for rec in fused_recs:
        res_id = rec.get('resource_id')
        if res_id:
            candidate_resource = db.query(Resource).filter(Resource.id == res_id).first()
            if candidate_resource:
                # Exclude quality outliers
                if candidate_resource.is_quality_outlier:
                    continue
                # Apply quality threshold if specified
                if min_quality is not None and candidate_resource.quality_overall is not None:
                    if candidate_resource.quality_overall < min_quality:
                        continue
            filtered_recs.append(rec)
    
    # Sort by fused score
    filtered_recs.sort(key=lambda x: x['score'], reverse=True)
    
    return filtered_recs[:limit]


def generate_recommendations(db: Session, resource_id: UUID, 
                            limit: int = 10, 
                            strategy: str = "hybrid",
                            min_quality: Optional[float] = None) -> List[Dict[str, Any]]:
    """Generate recommendations using specified strategy."""
    service = RecommendationService(db)
    return service.generate_recommendations(resource_id, limit, strategy, min_quality)


def generate_user_profile_vector(db: Session, user_id: Optional[str] = None, 
                                min_quality: Optional[float] = None) -> np.ndarray:
    """
    Generate user profile vector by averaging embeddings from user's resources.
    
    Args:
        db: Database session
        user_id: Optional user ID (currently unused, for future user-specific profiles)
        min_quality: Optional minimum quality threshold to filter resources
    
    Returns:
        numpy array of averaged embeddings, or empty array if no valid embeddings found
    """
    from backend.app.database.models import Resource
    
    # Query all resources with embeddings, excluding quality outliers
    query = db.query(Resource).filter(
        Resource.embedding.isnot(None),
        Resource.is_quality_outlier == False
    )
    
    # Apply quality threshold if specified
    if min_quality is not None:
        query = query.filter(Resource.quality_overall >= min_quality)
    
    resources = query.all()
    
    if not resources:
        return np.array([])
    
    # Collect valid embeddings
    valid_embeddings = []
    for resource in resources:
        if resource.embedding and len(resource.embedding) > 0:
            try:
                # Convert to numpy array
                emb = np.array(resource.embedding, dtype=np.float32)
                if emb.size > 0 and not np.all(emb == 0):
                    valid_embeddings.append(emb)
            except (ValueError, TypeError):
                continue
    
    if not valid_embeddings:
        return np.array([])
    
    # Average all embeddings
    avg_embedding = np.mean(valid_embeddings, axis=0)
    return avg_embedding


def recommend_based_on_annotations(db: Session, user_id: str, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
    """Generate recommendations based on user annotations."""
    service = RecommendationService(db)
    return service.recommend_based_on_annotations(user_id, limit)


def get_top_subjects(db: Session, limit: int = 5) -> List[str]:
    """
    Get top subjects by usage count from authority subjects.
    
    Args:
        db: Database session
        limit: Maximum number of subjects to return (default 5)
    
    Returns:
        List of subject strings ordered by usage count (highest first)
    """
    from backend.app.database.models import AuthoritySubject
    
    # Query authority subjects ordered by usage count
    subjects = db.query(AuthoritySubject).order_by(
        AuthoritySubject.usage_count.desc()
    ).limit(limit).all()
    
    return [subject.canonical_form for subject in subjects]


def cosine_similarity(vec1, vec2) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        vec1: First vector (list, numpy array, or array-like)
        vec2: Second vector (list, numpy array, or array-like)
    
    Returns:
        Cosine similarity in [-1, 1] range, or 0.0 for zero/invalid vectors
    """
    # Convert to numpy arrays
    v1 = np.array(vec1) if not isinstance(vec1, np.ndarray) else vec1
    v2 = np.array(vec2) if not isinstance(vec2, np.ndarray) else vec2
    
    # Handle empty or mismatched shapes
    if v1.size == 0 or v2.size == 0 or v1.shape != v2.shape:
        return 0.0
    
    # Calculate norms
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    # Handle zero vectors
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = np.dot(v1, v2) / (norm1 * norm2)
    
    # Clamp to [-1, 1] range to handle floating point errors
    return float(np.clip(similarity, -1.0, 1.0))


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors. Returns value in [0, 1] range.
    Negative similarities are clamped to 0.0.
    """
    similarity = cosine_similarity(vec1, vec2)
    # Clamp negative values to 0, keep positive values as-is
    return max(0.0, similarity)


def to_numpy_vector(data: Any) -> Optional[np.ndarray]:
    """
    Convert data to numpy array. Returns None for invalid data.
    
    Args:
        data: Input data (list, numpy array, or array-like)
    
    Returns:
        numpy array for valid input, None for None/empty/invalid inputs
    """
    if data is None:
        return None
    
    if isinstance(data, np.ndarray):
        if data.size == 0:
            return None
        return data
    
    if isinstance(data, list):
        if len(data) == 0:
            return None
        try:
            arr = np.array([float(x) for x in data], dtype=np.float32)
            return arr
        except (ValueError, TypeError):
            return None
    
    try:
        arr = np.array(data, dtype=np.float32)
        if arr.ndim == 1 and arr.size > 0:
            return arr
    except (ValueError, TypeError):
        pass
    
    return None


def _to_numpy_vector(data: Any) -> np.ndarray:
    """
    Convert data to numpy array (backward compatibility).
    Returns empty array for None or invalid data.
    
    Args:
        data: Input data (list, numpy array, or array-like)
    
    Returns:
        numpy array (empty array for invalid input)
    """
    arr = to_numpy_vector(data)
    if arr is None:
        return np.array([])
    return arr
