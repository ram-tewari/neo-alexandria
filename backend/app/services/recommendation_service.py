"""
Recommendation service using Strategy pattern.

This module provides the main interface for generating recommendations
using the Strategy pattern. It replaces conditional logic with polymorphic
strategies, following Fowler's "Replace Conditional with Polymorphism" technique.

The service delegates to concrete strategy implementations based on the
requested strategy type, eliminating repeated switch statements.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from backend.app.services.recommendation_strategies import (
    RecommendationStrategyFactory
)
from backend.app.domain.recommendation import Recommendation

logger = logging.getLogger(__name__)


def get_graph_based_recommendations(
    db: Session,
    resource_id: UUID,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get recommendations based on graph structure.
    
    Uses graph-based strategy to find recommendations through
    citation network relationships.
    
    Args:
        db: Database session
        resource_id: Source resource ID (converted to user_id for compatibility)
        limit: Maximum number of recommendations
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        # Create graph-based strategy
        strategy = RecommendationStrategyFactory.create('graph', db)
        
        # Generate recommendations (use resource_id as user_id for compatibility)
        recommendations = strategy.generate(
            user_id=str(resource_id),
            limit=limit
        )
        
        # Convert to dict format for backward compatibility
        return [rec.to_dict() for rec in recommendations]
        
    except Exception as e:
        logger.error(f"Error generating graph-based recommendations: {e}")
        return []


def generate_recommendations_with_graph_fusion(
    db: Session,
    resource_id: UUID,
    limit: int = 10,
    graph_weight: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Generate recommendations using graph fusion.
    
    Uses hybrid strategy with custom weights to incorporate
    graph-based recommendations.
    
    Args:
        db: Database session
        resource_id: Source resource ID (converted to user_id for compatibility)
        limit: Maximum number of recommendations
        graph_weight: Weight for graph-based strategy (0.0-1.0)
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        from backend.app.services.recommendation_strategies import (
            CollaborativeFilteringStrategy,
            ContentBasedStrategy,
            GraphBasedStrategy,
            HybridStrategy
        )
        
        # Create strategies with custom weights
        strategies = [
            CollaborativeFilteringStrategy(db),
            ContentBasedStrategy(db),
            GraphBasedStrategy(db)
        ]
        
        # Calculate weights (graph_weight for graph, rest split between others)
        remaining_weight = 1.0 - graph_weight
        weights = [
            remaining_weight * 0.6,  # Collaborative
            remaining_weight * 0.4,  # Content
            graph_weight             # Graph
        ]
        
        # Create hybrid strategy with custom weights
        hybrid_strategy = HybridStrategy(db, strategies, weights)
        
        # Generate recommendations
        recommendations = hybrid_strategy.generate(
            user_id=str(resource_id),
            limit=limit
        )
        
        # Convert to dict format for backward compatibility
        return [rec.to_dict() for rec in recommendations]
        
    except Exception as e:
        logger.error(f"Error generating graph fusion recommendations: {e}")
        return []


def generate_recommendations(
    db: Session,
    resource_id: Optional[UUID] = None,
    limit: int = 10,
    strategy: str = "hybrid",
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Generate recommendations using specified strategy.
    
    This is the main entry point for recommendation generation.
    Uses the Strategy pattern to delegate to appropriate strategy
    implementation, eliminating conditional logic.
    
    Args:
        db: Database session
        resource_id: Optional resource ID (for backward compatibility)
        limit: Maximum number of recommendations
        strategy: Strategy type ('collaborative', 'content', 'graph', 'hybrid')
        user_id: Optional user ID (takes precedence over resource_id)
        
    Returns:
        List of recommendation dictionaries
        
    Raises:
        ValueError: If strategy type is invalid
    """
    try:
        # Determine user_id (prefer explicit user_id, fallback to resource_id)
        effective_user_id = user_id or (str(resource_id) if resource_id else None)
        
        if not effective_user_id:
            logger.warning("No user_id or resource_id provided for recommendations")
            return []
        
        # Create strategy using factory (eliminates conditional logic)
        recommendation_strategy = RecommendationStrategyFactory.create(
            strategy_type=strategy,
            db=db
        )
        
        logger.info(
            f"Generating recommendations using {strategy} strategy "
            f"for user {effective_user_id}"
        )
        
        # Generate recommendations using polymorphic strategy
        recommendations = recommendation_strategy.generate(
            user_id=effective_user_id,
            limit=limit
        )
        
        # Convert to dict format for backward compatibility
        result = [rec.to_dict() for rec in recommendations]
        
        logger.info(f"Generated {len(result)} recommendations")
        return result
        
    except ValueError as e:
        # Invalid strategy type
        logger.error(f"Invalid strategy type '{strategy}': {e}")
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return []



def generate_user_profile_vector(db: Session, user_id: str) -> List[float]:
    """
    Generate user profile vector from interaction history.
    
    Uses content-based strategy's internal method to build
    user profile from interactions.
    
    Args:
        db: Database session
        user_id: User identifier
        
    Returns:
        User profile vector (768-dimensional)
    """
    try:
        from backend.app.services.recommendation_strategies import ContentBasedStrategy
        from backend.app.database.models import UserInteraction
        
        # Get user interactions
        interactions = db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).all()
        
        if not interactions:
            return [0.0] * 768
        
        # Use content-based strategy to build profile
        strategy = ContentBasedStrategy(db)
        profile = strategy._build_user_profile(interactions)
        
        return profile if profile else [0.0] * 768
        
    except Exception as e:
        logger.error(f"Error generating user profile vector: {e}")
        return [0.0] * 768


def recommend_based_on_annotations(
    db: Session,
    user_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Generate recommendations based on user annotations.
    
    Uses content-based strategy which considers user interactions
    including annotations.
    
    Args:
        db: Database session
        user_id: User identifier
        limit: Maximum number of recommendations
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        # Use content-based strategy (considers all interactions including annotations)
        strategy = RecommendationStrategyFactory.create('content', db)
        
        recommendations = strategy.generate(
            user_id=user_id,
            limit=limit
        )
        
        # Convert to dict format
        return [rec.to_dict() for rec in recommendations]
        
    except Exception as e:
        logger.error(f"Error generating annotation-based recommendations: {e}")
        return []



def get_top_subjects(db: Session, limit: int = 10) -> List[str]:
    """
    Get top subjects by resource count.
    
    Analyzes the resource database to find the most common subjects,
    useful for generating seed keywords for recommendations.
    
    Args:
        db: Database session
        limit: Maximum number of subjects to return
        
    Returns:
        List of top subject strings sorted by frequency
    """
    try:
        from backend.app.database.models import Resource
        
        # Query resources and extract subjects
        resources = db.query(Resource).filter(
            Resource.subject.isnot(None)
        ).all()
        
        # Count subject occurrences
        subject_counts = {}
        for resource in resources:
            if resource.subject:
                subjects = (
                    resource.subject
                    if isinstance(resource.subject, list)
                    else []
                )
                for subject in subjects:
                    subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        # Sort by count and return top subjects
        sorted_subjects = sorted(
            subject_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [subject for subject, count in sorted_subjects[:limit]]
        
    except Exception as e:
        logger.error(f"Error getting top subjects: {e}")
        return []



def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Helper function for backward compatibility. Delegates to
    ContentBasedStrategy implementation.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity (-1.0 to 1.0)
    """
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
    """
    Convert subject list to vector representation.
    
    Placeholder for subject-to-vector conversion.
    In a full implementation, this would use embeddings.
    
    Args:
        subjects: List of subject strings
        
    Returns:
        Vector representation (768-dimensional)
    """
    # TODO: Implement proper subject embedding
    return [0.0] * 768


def _to_numpy_vector(data: Any) -> List[float]:
    """
    Convert data to numpy-compatible vector.
    
    Helper function to normalize various data types to
    a consistent vector format.
    
    Args:
        data: Input data (numpy array, list, or other)
        
    Returns:
        List of floats representing the vector
    """
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
    except Exception:
        pass
    
    return []
