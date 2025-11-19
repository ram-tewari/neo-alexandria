"""
Quality domain objects for Neo Alexandria.

This module contains domain objects for quality assessment,
replacing primitive obsession with rich value objects that encapsulate
validation and business logic for multi-dimensional quality scoring.
"""

from dataclasses import dataclass
from typing import Dict, Any
from backend.app.domain import ValueObject, validate_range


# Quality dimension weights for overall score calculation
ACCURACY_WEIGHT = 0.3
COMPLETENESS_WEIGHT = 0.2
CONSISTENCY_WEIGHT = 0.2
TIMELINESS_WEIGHT = 0.15
RELEVANCE_WEIGHT = 0.15

# Quality thresholds
HIGH_QUALITY_THRESHOLD = 0.7
MEDIUM_QUALITY_THRESHOLD = 0.5


@dataclass
class QualityScore(ValueObject):
    """
    Multi-dimensional quality score value object.
    
    Represents quality assessment across five dimensions: accuracy,
    completeness, consistency, timeliness, and relevance. Each dimension
    is scored between 0.0 and 1.0, with higher values indicating better quality.
    
    This replaces primitive dict representations of quality scores with
    a rich domain object that encapsulates validation and calculation logic.
    
    Attributes:
        accuracy: Accuracy dimension score (0.0-1.0)
        completeness: Completeness dimension score (0.0-1.0)
        consistency: Consistency dimension score (0.0-1.0)
        timeliness: Timeliness dimension score (0.0-1.0)
        relevance: Relevance dimension score (0.0-1.0)
    """
    accuracy: float
    completeness: float
    consistency: float
    timeliness: float
    relevance: float
    
    def validate(self) -> None:
        """
        Validate all quality dimension scores.
        
        Each dimension must be between 0.0 and 1.0 inclusive.
        
        Raises:
            ValueError: If any dimension is outside the valid range
        """
        validate_range(self.accuracy, 0.0, 1.0, "accuracy")
        validate_range(self.completeness, 0.0, 1.0, "completeness")
        validate_range(self.consistency, 0.0, 1.0, "consistency")
        validate_range(self.timeliness, 0.0, 1.0, "timeliness")
        validate_range(self.relevance, 0.0, 1.0, "relevance")
    
    def overall_score(self) -> float:
        """
        Compute weighted overall quality score.
        
        The overall score is calculated as a weighted average of all
        five dimensions using predefined weights:
        - Accuracy: 30%
        - Completeness: 20%
        - Consistency: 20%
        - Timeliness: 15%
        - Relevance: 15%
        
        Returns:
            Overall quality score between 0.0 and 1.0
        """
        return (
            ACCURACY_WEIGHT * self.accuracy +
            COMPLETENESS_WEIGHT * self.completeness +
            CONSISTENCY_WEIGHT * self.consistency +
            TIMELINESS_WEIGHT * self.timeliness +
            RELEVANCE_WEIGHT * self.relevance
        )
    
    def is_high_quality(self, threshold: float = HIGH_QUALITY_THRESHOLD) -> bool:
        """
        Check if overall quality meets high quality threshold.
        
        Args:
            threshold: Quality threshold (default: 0.7)
            
        Returns:
            True if overall_score() >= threshold
        """
        return self.overall_score() >= threshold
    
    def is_low_quality(self, threshold: float = MEDIUM_QUALITY_THRESHOLD) -> bool:
        """
        Check if overall quality is below medium threshold.
        
        Args:
            threshold: Quality threshold (default: 0.5)
            
        Returns:
            True if overall_score() < threshold
        """
        return self.overall_score() < threshold
    
    def is_medium_quality(
        self,
        low_threshold: float = MEDIUM_QUALITY_THRESHOLD,
        high_threshold: float = HIGH_QUALITY_THRESHOLD
    ) -> bool:
        """
        Check if overall quality is in medium range.
        
        Args:
            low_threshold: Lower bound (default: 0.5)
            high_threshold: Upper bound (default: 0.7)
            
        Returns:
            True if low_threshold <= overall_score() < high_threshold
        """
        score = self.overall_score()
        return low_threshold <= score < high_threshold
    
    def get_quality_level(self) -> str:
        """
        Get quality level as string classification.
        
        Returns:
            'high', 'medium', or 'low' based on overall score
        """
        if self.is_high_quality():
            return 'high'
        elif self.is_low_quality():
            return 'low'
        else:
            return 'medium'
    
    def get_weakest_dimension(self) -> str:
        """
        Identify the dimension with the lowest score.
        
        Returns:
            Name of the dimension with the lowest score
        """
        dimensions = {
            'accuracy': self.accuracy,
            'completeness': self.completeness,
            'consistency': self.consistency,
            'timeliness': self.timeliness,
            'relevance': self.relevance
        }
        return min(dimensions, key=dimensions.get)
    
    def get_strongest_dimension(self) -> str:
        """
        Identify the dimension with the highest score.
        
        Returns:
            Name of the dimension with the highest score
        """
        dimensions = {
            'accuracy': self.accuracy,
            'completeness': self.completeness,
            'consistency': self.consistency,
            'timeliness': self.timeliness,
            'relevance': self.relevance
        }
        return max(dimensions, key=dimensions.get)
    
    def get_dimension_scores(self) -> Dict[str, float]:
        """
        Get all dimension scores as a dictionary.
        
        Returns:
            Dictionary mapping dimension names to scores
        """
        return {
            'accuracy': self.accuracy,
            'completeness': self.completeness,
            'consistency': self.consistency,
            'timeliness': self.timeliness,
            'relevance': self.relevance
        }
    
    def has_dimension_below_threshold(self, threshold: float = 0.5) -> bool:
        """
        Check if any dimension is below the specified threshold.
        
        Args:
            threshold: Minimum acceptable score (default: 0.5)
            
        Returns:
            True if at least one dimension is below threshold
        """
        return any(
            score < threshold
            for score in self.get_dimension_scores().values()
        )
    
    def count_dimensions_below_threshold(self, threshold: float = 0.5) -> int:
        """
        Count how many dimensions are below the specified threshold.
        
        Args:
            threshold: Minimum acceptable score (default: 0.5)
            
        Returns:
            Number of dimensions with score < threshold
        """
        return sum(
            1 for score in self.get_dimension_scores().values()
            if score < threshold
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert quality score to dictionary for API compatibility.
        
        Returns:
            Dictionary representation with all dimensions and metadata
        """
        return {
            'accuracy': self.accuracy,
            'completeness': self.completeness,
            'consistency': self.consistency,
            'timeliness': self.timeliness,
            'relevance': self.relevance,
            'overall_score': self.overall_score(),
            'quality_level': self.get_quality_level(),
            'metadata': {
                'weakest_dimension': self.get_weakest_dimension(),
                'strongest_dimension': self.get_strongest_dimension(),
                'dimensions_below_threshold': self.count_dimensions_below_threshold()
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get dimension score by key (dict-like interface for backward compatibility).
        
        Args:
            key: Dimension name or 'overall_score'
            default: Default value if key not found
            
        Returns:
            Dimension score or default value
        """
        if key == 'overall_score':
            return self.overall_score()
        return getattr(self, key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get dimension score by key (dict-like interface).
        
        Args:
            key: Dimension name or 'overall_score'
            
        Returns:
            Dimension score
            
        Raises:
            KeyError: If key is not a valid dimension
        """
        if key == 'overall_score':
            return self.overall_score()
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"'{key}' is not a valid quality dimension")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityScore':
        """
        Create quality score from dictionary.
        
        Args:
            data: Dictionary with quality score data
            
        Returns:
            New QualityScore instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        return cls(
            accuracy=data['accuracy'],
            completeness=data['completeness'],
            consistency=data['consistency'],
            timeliness=data['timeliness'],
            relevance=data['relevance']
        )
