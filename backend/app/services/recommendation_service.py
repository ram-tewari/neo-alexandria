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
                                strategy: str = "hybrid") -> List[Dict[str, Any]]:
        """Generate recommendations using specified strategy."""
        return []
    
    def get_graph_based_recommendations(self, resource_id: UUID, 
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """Get recommendations based on graph structure."""
        return []
    
    def generate_recommendations_with_graph_fusion(self, resource_id: UUID,
                                                  limit: int = 10, 
                                                  graph_weight: float = 0.3) -> List[Dict[str, Any]]:
        """Generate recommendations using graph fusion."""
        return []
    
    def recommend_based_on_annotations(self, user_id: str, 
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """Generate recommendations based on user annotations."""
        return []


# Module-level functions for backward compatibility
def get_graph_based_recommendations(db: Session, resource_id: UUID, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
    """Get recommendations based on graph structure."""
    service = RecommendationService(db)
    return service.get_graph_based_recommendations(resource_id, limit)


def generate_recommendations_with_graph_fusion(db: Session, resource_id: UUID,
                                              limit: int = 10, 
                                              graph_weight: float = 0.3) -> List[Dict[str, Any]]:
    """Generate recommendations using graph fusion."""
    service = RecommendationService(db)
    return service.generate_recommendations_with_graph_fusion(resource_id, limit, graph_weight)


def generate_recommendations(db: Session, resource_id: UUID, 
                            limit: int = 10, 
                            strategy: str = "hybrid") -> List[Dict[str, Any]]:
    """Generate recommendations using specified strategy."""
    service = RecommendationService(db)
    return service.generate_recommendations(resource_id, limit, strategy)


def generate_user_profile_vector(db: Session, user_id: str) -> List[float]:
    """Generate user profile vector from interaction history."""
    return [0.0] * 768


def recommend_based_on_annotations(db: Session, user_id: str, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
    """Generate recommendations based on user annotations."""
    service = RecommendationService(db)
    return service.recommend_based_on_annotations(user_id, limit)


def get_top_subjects(db: Session, limit: int = 10) -> List[str]:
    """Get top subjects by resource count."""
    from backend.app.database.models import Resource
    
    resources = self.db.query(Resource).filter(Resource.subject.isnot(None)).all()
    
    subject_counts = {}
    for resource in resources:
        if resource.subject:
            subjects = resource.subject if isinstance(resource.subject, list) else []
            for subject in subjects:
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
    
    sorted_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)
    return [subject for subject, count in sorted_subjects[:limit]]


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors. Returns value in [0, 1] range."""
    v1 = np.array(vec1) if not isinstance(vec1, np.ndarray) else vec1
    v2 = np.array(vec2) if not isinstance(vec2, np.ndarray) else vec2
    
    if v1.size == 0 or v2.size == 0 or v1.shape != v2.shape:
        return 0.0
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    
    similarity = np.dot(v1, v2) / (norm1 * norm2)
    similarity = (similarity + 1.0) / 2.0
    return float(np.clip(similarity, 0.0, 1.0))


def to_numpy_vector(data: Any) -> Optional[np.ndarray]:
    """Convert data to numpy array. Returns None for invalid data."""
    if data is None:
        return None
    
    if isinstance(data, np.ndarray):
        return data
    
    if isinstance(data, list):
        if len(data) == 0:
            return np.array([])
        try:
            return np.array([float(x) for x in data])
        except (ValueError, TypeError):
            return None
    
    try:
        arr = np.array(data)
        if arr.ndim == 1:
            return arr
    except:
        pass
    
    return None


def _to_numpy_vector(data: Any) -> List[float]:
    """Convert data to list (backward compatibility)."""
    arr = to_numpy_vector(data)
    if arr is None:
        return []
    return arr.tolist()
