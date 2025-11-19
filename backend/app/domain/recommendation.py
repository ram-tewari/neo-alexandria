"""
Recommendation domain objects for Neo Alexandria.

This module contains domain objects for recommendation systems,
replacing primitive obsession with rich value objects that encapsulate
validation and business logic for recommendation scoring and ranking.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from backend.app.domain import (
    ValueObject,
    validate_non_empty,
    validate_range,
    validate_non_negative,
)


@dataclass
class RecommendationScore(ValueObject):
    """
    Recommendation score with confidence and ranking metadata.
    
    Represents the scoring information for a recommendation, including
    the relevance score, confidence in the recommendation, and ranking
    position. This encapsulates the quality metrics of a recommendation.
    
    Attributes:
        score: Relevance score (0.0-1.0, higher is better)
        confidence: Confidence in the recommendation (0.0-1.0)
        rank: Ranking position (1-based, lower is better)
    """
    score: float
    confidence: float
    rank: int
    
    def validate(self) -> None:
        """
        Validate recommendation score attributes.
        
        Raises:
            ValueError: If score or confidence not in [0.0, 1.0] or rank not positive
        """
        validate_range(self.score, 0.0, 1.0, "score")
        validate_range(self.confidence, 0.0, 1.0, "confidence")
        
        if self.rank < 1:
            raise ValueError(f"rank must be positive (1-based), got {self.rank}")
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """
        Check if recommendation has high confidence.
        
        Args:
            threshold: Confidence threshold (default: 0.8)
            
        Returns:
            True if confidence >= threshold
        """
        return self.confidence >= threshold
    
    def is_low_confidence(self, threshold: float = 0.5) -> bool:
        """
        Check if recommendation has low confidence.
        
        Args:
            threshold: Confidence threshold (default: 0.5)
            
        Returns:
            True if confidence < threshold
        """
        return self.confidence < threshold
    
    def is_high_score(self, threshold: float = 0.7) -> bool:
        """
        Check if recommendation has high relevance score.
        
        Args:
            threshold: Score threshold (default: 0.7)
            
        Returns:
            True if score >= threshold
        """
        return self.score >= threshold
    
    def is_top_ranked(self, top_k: int = 5) -> bool:
        """
        Check if recommendation is in top K positions.
        
        Args:
            top_k: Number of top positions to consider (default: 5)
            
        Returns:
            True if rank <= top_k
        """
        return self.rank <= top_k
    
    def combined_quality(self) -> float:
        """
        Calculate combined quality metric from score and confidence.
        
        Returns weighted average of score and confidence, giving
        more weight to the score (70%) than confidence (30%).
        
        Returns:
            Combined quality score between 0.0 and 1.0
        """
        return 0.7 * self.score + 0.3 * self.confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert recommendation score to dictionary for API compatibility.
        
        Returns:
            Dictionary representation with all attributes
        """
        return {
            'score': self.score,
            'confidence': self.confidence,
            'rank': self.rank,
            'combined_quality': self.combined_quality()
        }


@dataclass
class Recommendation(ValueObject):
    """
    Recommendation value object with resource and scoring information.
    
    Represents a single recommendation for a user, including the
    recommended resource, scoring information, and optional metadata
    about why this recommendation was made.
    
    Attributes:
        resource_id: Unique identifier of the recommended resource
        user_id: Unique identifier of the user receiving the recommendation
        recommendation_score: Scoring information for this recommendation
        strategy: Strategy used to generate this recommendation
        reason: Optional explanation for why this was recommended
        metadata: Additional metadata about the recommendation
    """
    resource_id: str
    user_id: str
    recommendation_score: RecommendationScore
    strategy: str = "unknown"
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize metadata dict if None and validate."""
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        super().__post_init__()
    
    def validate(self) -> None:
        """
        Validate recommendation attributes.
        
        Raises:
            ValueError: If resource_id or user_id is empty
        """
        validate_non_empty(self.resource_id, "resource_id")
        validate_non_empty(self.user_id, "user_id")
        
        # Validate the recommendation score
        self.recommendation_score.validate()
    
    def get_score(self) -> float:
        """
        Get the relevance score.
        
        Returns:
            Relevance score from recommendation_score
        """
        return self.recommendation_score.score
    
    def get_confidence(self) -> float:
        """
        Get the confidence score.
        
        Returns:
            Confidence from recommendation_score
        """
        return self.recommendation_score.confidence
    
    def get_rank(self) -> int:
        """
        Get the ranking position.
        
        Returns:
            Rank from recommendation_score
        """
        return self.recommendation_score.rank
    
    def is_high_quality(
        self,
        score_threshold: float = 0.7,
        confidence_threshold: float = 0.8
    ) -> bool:
        """
        Check if recommendation meets high quality criteria.
        
        A recommendation is high quality if both score and confidence
        meet their respective thresholds.
        
        Args:
            score_threshold: Minimum score (default: 0.7)
            confidence_threshold: Minimum confidence (default: 0.8)
            
        Returns:
            True if both thresholds are met
        """
        return (
            self.recommendation_score.is_high_score(score_threshold) and
            self.recommendation_score.is_high_confidence(confidence_threshold)
        )
    
    def is_top_recommendation(self, top_k: int = 5) -> bool:
        """
        Check if this is a top-ranked recommendation.
        
        Args:
            top_k: Number of top positions to consider (default: 5)
            
        Returns:
            True if rank <= top_k
        """
        return self.recommendation_score.is_top_ranked(top_k)
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """
        Check if recommendation has high confidence.
        
        Convenience method that delegates to recommendation_score.
        
        Args:
            threshold: Confidence threshold (default: 0.8)
            
        Returns:
            True if confidence >= threshold
        """
        return self.recommendation_score.is_high_confidence(threshold)
    
    def is_high_score(self, threshold: float = 0.7) -> bool:
        """
        Check if recommendation has high relevance score.
        
        Convenience method that delegates to recommendation_score.
        
        Args:
            threshold: Score threshold (default: 0.7)
            
        Returns:
            True if score >= threshold
        """
        return self.recommendation_score.is_high_score(threshold)
    
    def is_top_ranked(self, top_k: int = 5) -> bool:
        """
        Check if recommendation is in top K positions.
        
        Convenience method that delegates to recommendation_score.
        
        Args:
            top_k: Number of top positions to consider (default: 5)
            
        Returns:
            True if rank <= top_k
        """
        return self.recommendation_score.is_top_ranked(top_k)
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value by key.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    def has_metadata(self, key: str) -> bool:
        """
        Check if metadata contains a key.
        
        Args:
            key: Metadata key to check
            
        Returns:
            True if key exists in metadata
        """
        return key in self.metadata
    
    def __lt__(self, other: 'Recommendation') -> bool:
        """
        Compare recommendations for sorting (lower rank is better).
        
        Args:
            other: Another recommendation to compare with
            
        Returns:
            True if this recommendation has lower rank (better)
        """
        if not isinstance(other, Recommendation):
            return NotImplemented
        return self.get_rank() < other.get_rank()
    
    def __le__(self, other: 'Recommendation') -> bool:
        """
        Compare recommendations for sorting (lower or equal rank).
        
        Args:
            other: Another recommendation to compare with
            
        Returns:
            True if this recommendation has lower or equal rank
        """
        if not isinstance(other, Recommendation):
            return NotImplemented
        return self.get_rank() <= other.get_rank()
    
    def __gt__(self, other: 'Recommendation') -> bool:
        """
        Compare recommendations for sorting (higher rank is worse).
        
        Args:
            other: Another recommendation to compare with
            
        Returns:
            True if this recommendation has higher rank (worse)
        """
        if not isinstance(other, Recommendation):
            return NotImplemented
        return self.get_rank() > other.get_rank()
    
    def __ge__(self, other: 'Recommendation') -> bool:
        """
        Compare recommendations for sorting (higher or equal rank).
        
        Args:
            other: Another recommendation to compare with
            
        Returns:
            True if this recommendation has higher or equal rank
        """
        if not isinstance(other, Recommendation):
            return NotImplemented
        return self.get_rank() >= other.get_rank()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get attribute value by key (dict-like interface for backward compatibility).
        
        Args:
            key: Attribute name
            default: Default value if key not found
            
        Returns:
            Attribute value or default value
        """
        # Map common dict keys to domain object attributes
        key_mapping = {
            'score': 'get_score',
            'confidence': 'get_confidence',
            'rank': 'get_rank',
        }
        
        if key in key_mapping:
            method_name = key_mapping[key]
            return getattr(self, method_name)()
        
        return getattr(self, key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get attribute value by key (dict-like interface).
        
        Args:
            key: Attribute name
            
        Returns:
            Attribute value
            
        Raises:
            KeyError: If key is not a valid attribute
        """
        # Map common dict keys to domain object attributes
        key_mapping = {
            'score': 'get_score',
            'confidence': 'get_confidence',
            'rank': 'get_rank',
        }
        
        if key in key_mapping:
            method_name = key_mapping[key]
            return getattr(self, method_name)()
        
        if hasattr(self, key):
            return getattr(self, key)
        
        raise KeyError(f"'{key}' is not a valid recommendation attribute")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert recommendation to dictionary for API compatibility.
        
        Returns:
            Dictionary representation with all attributes
        """
        return {
            'resource_id': self.resource_id,
            'user_id': self.user_id,
            'score': self.get_score(),
            'confidence': self.get_confidence(),
            'rank': self.get_rank(),
            'strategy': self.strategy,
            'reason': self.reason,
            'metadata': self.metadata,
            'quality_metrics': {
                'is_high_quality': self.is_high_quality(),
                'is_top_recommendation': self.is_top_recommendation(),
                'combined_quality': self.recommendation_score.combined_quality()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recommendation':
        """
        Create recommendation from dictionary.
        
        Args:
            data: Dictionary with recommendation data
            
        Returns:
            New Recommendation instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Handle both nested and flat score structures
        if 'recommendation_score' in data:
            score_data = data['recommendation_score']
            rec_score = RecommendationScore(
                score=score_data['score'],
                confidence=score_data['confidence'],
                rank=score_data['rank']
            )
        else:
            # Flat structure with score, confidence, rank at top level
            rec_score = RecommendationScore(
                score=data['score'],
                confidence=data['confidence'],
                rank=data['rank']
            )
        
        return cls(
            resource_id=data['resource_id'],
            user_id=data['user_id'],
            recommendation_score=rec_score,
            strategy=data.get('strategy', 'unknown'),
            reason=data.get('reason'),
            metadata=data.get('metadata')
        )
