"""
Stub implementation of recommendation service for Phase 10 tests.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID


def get_graph_based_recommendations(db: Session, resource_id: UUID, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
    """Get recommendations based on graph structure."""
    return []


def generate_recommendations_with_graph_fusion(db: Session, resource_id: UUID,
                                              limit: int = 10, 
                                              graph_weight: float = 0.3) -> List[Dict[str, Any]]:
    """Generate recommendations using graph fusion."""
    return []



def generate_recommendations(db: Session, resource_id: UUID, 
                            limit: int = 10, 
                            strategy: str = "hybrid") -> List[Dict[str, Any]]:
    """Generate recommendations using specified strategy."""
    return []



def generate_user_profile_vector(db: Session, user_id: str) -> List[float]:
    """Generate user profile vector from interaction history."""
    return [0.0] * 768  # Return zero vector as stub


def recommend_based_on_annotations(db: Session, user_id: str, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
    """Generate recommendations based on user annotations."""
    return []



def get_top_subjects(db: Session, limit: int = 10) -> List[str]:
    """Get top subjects by resource count."""
    from backend.app.database.models import Resource
    from sqlalchemy import func
    import json
    
    # Query resources and extract subjects
    resources = db.query(Resource).filter(Resource.subject.isnot(None)).all()
    
    # Count subject occurrences
    subject_counts = {}
    for resource in resources:
        if resource.subject:
            subjects = resource.subject if isinstance(resource.subject, list) else []
            for subject in subjects:
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
    
    # Sort by count and return top subjects
    sorted_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)
    return [subject for subject, count in sorted_subjects[:limit]]



def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import numpy as np
    
    # Convert to numpy arrays if needed
    v1 = np.array(vec1) if not isinstance(vec1, np.ndarray) else vec1
    v2 = np.array(vec2) if not isinstance(vec2, np.ndarray) else vec2
    
    # Check for empty or mismatched vectors
    if v1.size == 0 or v2.size == 0 or v1.shape != v2.shape:
        return 0.0
    
    # Compute norms
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    # Handle zero vectors
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    
    # Compute cosine similarity
    similarity = np.dot(v1, v2) / (norm1 * norm2)
    
    # Clamp to [-1, 1] to handle numerical errors
    return float(np.clip(similarity, -1.0, 1.0))


def _convert_subjects_to_vector(subjects: List[str]) -> List[float]:
    """Convert subject list to vector representation."""
    return [0.0] * 768  # Return zero vector as stub



def _to_numpy_vector(data: Any) -> List[float]:
    """Convert data to numpy-compatible vector."""
    import numpy as np
    
    if data is None:
        return []
    
    if isinstance(data, np.ndarray):
        return data.tolist()
    
    if isinstance(data, list):
        if len(data) == 0:
            return []
        # Check if it's already a valid vector
        try:
            return [float(x) for x in data]
        except (ValueError, TypeError):
            return []
    
    # Try to convert other types
    try:
        arr = np.array(data)
        if arr.ndim == 1:
            return arr.tolist()
    except:
        pass
    
    return []
