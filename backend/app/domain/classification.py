"""
Classification domain objects for Neo Alexandria.

This module contains domain objects for ML-based classification,
replacing primitive obsession with rich value objects that encapsulate
validation and business logic.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from backend.app.domain import ValueObject, validate_range, validate_positive


@dataclass
class ClassificationPrediction(ValueObject):
    """
    Single classification prediction with validation.
    
    Represents a single taxonomy category prediction with confidence score
    and ranking. This is a value object - immutable and defined by its attributes.
    
    Attributes:
        taxonomy_id: Unique identifier for the taxonomy category
        confidence: Confidence score between 0.0 and 1.0
        rank: Ranking position (1-based, lower is better)
    """
    taxonomy_id: str
    confidence: float
    rank: int
    
    def validate(self) -> None:
        """
        Validate prediction attributes.
        
        Raises:
            ValueError: If confidence is not in [0.0, 1.0] or rank is not positive
        """
        validate_range(self.confidence, 0.0, 1.0, "confidence")
        validate_positive(self.rank, "rank")
        
        if not self.taxonomy_id or not self.taxonomy_id.strip():
            raise ValueError("taxonomy_id cannot be empty")
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """
        Check if prediction has high confidence.
        
        Args:
            threshold: Confidence threshold (default: 0.8)
            
        Returns:
            True if confidence >= threshold
        """
        return self.confidence >= threshold
    
    def is_low_confidence(self, threshold: float = 0.5) -> bool:
        """
        Check if prediction has low confidence.
        
        Args:
            threshold: Confidence threshold (default: 0.5)
            
        Returns:
            True if confidence < threshold
        """
        return self.confidence < threshold
    
    def is_medium_confidence(
        self,
        low_threshold: float = 0.5,
        high_threshold: float = 0.8
    ) -> bool:
        """
        Check if prediction has medium confidence.
        
        Args:
            low_threshold: Lower bound (default: 0.5)
            high_threshold: Upper bound (default: 0.8)
            
        Returns:
            True if low_threshold <= confidence < high_threshold
        """
        return low_threshold <= self.confidence < high_threshold
    
    def is_top_prediction(self, top_k: int = 1) -> bool:
        """
        Check if this prediction is in the top K positions.
        
        Args:
            top_k: Number of top positions to consider (default: 1)
            
        Returns:
            True if rank <= top_k
        """
        return self.rank <= top_k
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert classification prediction to dictionary for API compatibility.
        
        Returns:
            Dictionary representation with all attributes
        """
        return {
            'taxonomy_id': self.taxonomy_id,
            'confidence': self.confidence,
            'rank': self.rank
        }


@dataclass
class ClassificationResult(ValueObject):
    """
    Collection of predictions with metadata.
    
    Represents the complete result of a classification operation,
    including all predictions, model information, and performance metrics.
    
    Attributes:
        predictions: List of classification predictions
        model_version: Version identifier of the model used
        inference_time_ms: Time taken for inference in milliseconds
        resource_id: Optional ID of the resource being classified
    """
    predictions: List[ClassificationPrediction]
    model_version: str
    inference_time_ms: float
    resource_id: Optional[str] = None
    
    def validate(self) -> None:
        """
        Validate classification result.
        
        Raises:
            ValueError: If predictions is empty, model_version is empty,
                       or inference_time_ms is negative
        """
        if not self.predictions:
            raise ValueError("predictions cannot be empty")
        
        if not self.model_version or not self.model_version.strip():
            raise ValueError("model_version cannot be empty")
        
        if self.inference_time_ms < 0:
            raise ValueError(
                f"inference_time_ms must be non-negative, got {self.inference_time_ms}"
            )
        
        # Validate all predictions
        for pred in self.predictions:
            pred.validate()
    
    def get_high_confidence(self, threshold: float = 0.8) -> List[ClassificationPrediction]:
        """
        Get predictions with high confidence.
        
        Args:
            threshold: Confidence threshold (default: 0.8)
            
        Returns:
            List of predictions with confidence >= threshold
        """
        return [p for p in self.predictions if p.is_high_confidence(threshold)]
    
    def get_low_confidence(self, threshold: float = 0.5) -> List[ClassificationPrediction]:
        """
        Get predictions with low confidence.
        
        Args:
            threshold: Confidence threshold (default: 0.5)
            
        Returns:
            List of predictions with confidence < threshold
        """
        return [p for p in self.predictions if p.is_low_confidence(threshold)]
    
    def get_top_prediction(self) -> ClassificationPrediction:
        """
        Get the top-ranked prediction.
        
        Returns:
            The prediction with rank=1
            
        Raises:
            ValueError: If no predictions exist
        """
        if not self.predictions:
            raise ValueError("No predictions available")
        
        # Find prediction with rank 1
        for pred in self.predictions:
            if pred.rank == 1:
                return pred
        
        # If no rank 1, return first prediction
        return self.predictions[0]
    
    def get_predictions_above_threshold(self, threshold: float) -> List[ClassificationPrediction]:
        """
        Get predictions with confidence above threshold.
        
        Args:
            threshold: Confidence threshold
            
        Returns:
            List of predictions with confidence >= threshold
        """
        return [p for p in self.predictions if p.confidence >= threshold]
    
    def has_high_confidence_prediction(self, threshold: float = 0.8) -> bool:
        """
        Check if any prediction has high confidence.
        
        Args:
            threshold: Confidence threshold (default: 0.8)
            
        Returns:
            True if at least one prediction has confidence >= threshold
        """
        return any(p.is_high_confidence(threshold) for p in self.predictions)
    
    def get_medium_confidence(
        self,
        low_threshold: float = 0.5,
        high_threshold: float = 0.8
    ) -> List[ClassificationPrediction]:
        """
        Get predictions with medium confidence.
        
        Args:
            low_threshold: Lower bound (default: 0.5)
            high_threshold: Upper bound (default: 0.8)
            
        Returns:
            List of predictions with low_threshold <= confidence < high_threshold
        """
        return [
            p for p in self.predictions
            if p.is_medium_confidence(low_threshold, high_threshold)
        ]
    
    def get_top_k(self, k: int) -> List[ClassificationPrediction]:
        """
        Get top K predictions by confidence.
        
        Args:
            k: Number of top predictions to return
            
        Returns:
            List of top K predictions sorted by confidence (descending)
        """
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        return sorted(
            self.predictions,
            key=lambda p: p.confidence,
            reverse=True
        )[:k]
    
    def get_by_rank(self, max_rank: int) -> List[ClassificationPrediction]:
        """
        Get predictions up to a maximum rank.
        
        Args:
            max_rank: Maximum rank to include (inclusive)
            
        Returns:
            List of predictions with rank <= max_rank
        """
        if max_rank <= 0:
            raise ValueError(f"max_rank must be positive, got {max_rank}")
        
        return [p for p in self.predictions if p.rank <= max_rank]
    
    def get_best_prediction(self) -> ClassificationPrediction:
        """
        Get the prediction with highest confidence.
        
        Returns:
            Prediction with highest confidence score
            
        Raises:
            ValueError: If predictions list is empty
        """
        if not self.predictions:
            raise ValueError("Cannot get best prediction from empty list")
        
        return max(self.predictions, key=lambda p: p.confidence)
    
    def has_high_confidence_predictions(self, threshold: float = 0.8) -> bool:
        """
        Check if result has any high confidence predictions.
        
        Args:
            threshold: Confidence threshold (default: 0.8)
            
        Returns:
            True if at least one prediction has confidence >= threshold
        """
        return any(p.is_high_confidence(threshold) for p in self.predictions)
    
    def count_by_confidence_level(
        self,
        low_threshold: float = 0.5,
        high_threshold: float = 0.8
    ) -> Dict[str, int]:
        """
        Count predictions by confidence level.
        
        Args:
            low_threshold: Lower bound for medium confidence (default: 0.5)
            high_threshold: Lower bound for high confidence (default: 0.8)
            
        Returns:
            Dictionary with counts for 'low', 'medium', and 'high' confidence
        """
        return {
            'low': len(self.get_low_confidence(low_threshold)),
            'medium': len(self.get_medium_confidence(low_threshold, high_threshold)),
            'high': len(self.get_high_confidence(high_threshold))
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get attribute value by key (dict-like interface for backward compatibility).
        
        Args:
            key: Attribute name
            default: Default value if key not found
            
        Returns:
            Attribute value or default value
        """
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
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"'{key}' is not a valid classification result attribute")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert classification result to dictionary for API compatibility.
        
        Returns:
            Dictionary representation with all attributes
        """
        return {
            'predictions': [
                {
                    'taxonomy_id': p.taxonomy_id,
                    'confidence': p.confidence,
                    'rank': p.rank
                }
                for p in self.predictions
            ],
            'model_version': self.model_version,
            'inference_time_ms': self.inference_time_ms,
            'resource_id': self.resource_id,
            'metadata': {
                'total_predictions': len(self.predictions),
                'confidence_distribution': self.count_by_confidence_level(),
                'best_confidence': self.get_best_prediction().confidence
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassificationResult':
        """
        Create classification result from dictionary.
        
        Args:
            data: Dictionary with classification result data
            
        Returns:
            New ClassificationResult instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        predictions_data = data.get('predictions', [])
        predictions = [
            ClassificationPrediction(
                taxonomy_id=p['taxonomy_id'],
                confidence=p['confidence'],
                rank=p['rank']
            )
            for p in predictions_data
        ]
        
        return cls(
            predictions=predictions,
            model_version=data['model_version'],
            inference_time_ms=data['inference_time_ms'],
            resource_id=data.get('resource_id')
        )
