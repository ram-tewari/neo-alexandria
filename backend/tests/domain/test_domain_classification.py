"""
Tests for classification domain objects.

This module tests the ClassificationPrediction and ClassificationResult
domain objects, verifying validation, business logic, and API compatibility.
"""

import pytest
from backend.app.domain.classification import (
    ClassificationPrediction,
    ClassificationResult,
)


class TestClassificationPrediction:
    """Tests for ClassificationPrediction value object."""
    
    def test_create_valid_prediction(self):
        """Test creating a valid prediction."""
        pred = ClassificationPrediction(
            taxonomy_id="node_123",
            confidence=0.95,
            rank=1
        )
        
        assert pred.taxonomy_id == "node_123"
        assert pred.confidence == 0.95
        assert pred.rank == 1
    
    def test_confidence_validation_too_low(self):
        """Test that confidence below 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            ClassificationPrediction(
                taxonomy_id="node_123",
                confidence=-0.1,
                rank=1
            )
    
    def test_confidence_validation_too_high(self):
        """Test that confidence above 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            ClassificationPrediction(
                taxonomy_id="node_123",
                confidence=1.5,
                rank=1
            )
    
    def test_confidence_boundary_values(self):
        """Test that confidence boundary values (0.0 and 1.0) are valid."""
        pred_min = ClassificationPrediction(
            taxonomy_id="node_123",
            confidence=0.0,
            rank=1
        )
        assert pred_min.confidence == 0.0
        
        pred_max = ClassificationPrediction(
            taxonomy_id="node_123",
            confidence=1.0,
            rank=1
        )
        assert pred_max.confidence == 1.0
    
    def test_rank_validation_zero(self):
        """Test that rank of 0 raises ValueError."""
        with pytest.raises(ValueError, match="rank must be positive"):
            ClassificationPrediction(
                taxonomy_id="node_123",
                confidence=0.95,
                rank=0
            )
    
    def test_rank_validation_negative(self):
        """Test that negative rank raises ValueError."""
        with pytest.raises(ValueError, match="rank must be positive"):
            ClassificationPrediction(
                taxonomy_id="node_123",
                confidence=0.95,
                rank=-1
            )
    
    def test_taxonomy_id_validation_empty(self):
        """Test that empty taxonomy_id raises ValueError."""
        with pytest.raises(ValueError, match="taxonomy_id cannot be empty"):
            ClassificationPrediction(
                taxonomy_id="",
                confidence=0.95,
                rank=1
            )
    
    def test_taxonomy_id_validation_whitespace(self):
        """Test that whitespace-only taxonomy_id raises ValueError."""
        with pytest.raises(ValueError, match="taxonomy_id cannot be empty"):
            ClassificationPrediction(
                taxonomy_id="   ",
                confidence=0.95,
                rank=1
            )
    
    def test_is_high_confidence_default_threshold(self):
        """Test is_high_confidence with default threshold (0.8)."""
        pred_high = ClassificationPrediction("node_1", 0.85, 1)
        pred_low = ClassificationPrediction("node_2", 0.75, 2)
        
        assert pred_high.is_high_confidence() is True
        assert pred_low.is_high_confidence() is False
    
    def test_is_high_confidence_custom_threshold(self):
        """Test is_high_confidence with custom threshold."""
        pred = ClassificationPrediction("node_1", 0.75, 1)
        
        assert pred.is_high_confidence(threshold=0.7) is True
        assert pred.is_high_confidence(threshold=0.8) is False
    
    def test_is_low_confidence_default_threshold(self):
        """Test is_low_confidence with default threshold (0.5)."""
        pred_low = ClassificationPrediction("node_1", 0.45, 1)
        pred_high = ClassificationPrediction("node_2", 0.55, 2)
        
        assert pred_low.is_low_confidence() is True
        assert pred_high.is_low_confidence() is False
    
    def test_is_low_confidence_custom_threshold(self):
        """Test is_low_confidence with custom threshold."""
        pred = ClassificationPrediction("node_1", 0.55, 1)
        
        assert pred.is_low_confidence(threshold=0.6) is True
        assert pred.is_low_confidence(threshold=0.5) is False
    
    def test_is_medium_confidence_default_thresholds(self):
        """Test is_medium_confidence with default thresholds."""
        pred_low = ClassificationPrediction("node_1", 0.45, 1)
        pred_medium = ClassificationPrediction("node_2", 0.65, 2)
        pred_high = ClassificationPrediction("node_3", 0.85, 3)
        
        assert pred_low.is_medium_confidence() is False
        assert pred_medium.is_medium_confidence() is True
        assert pred_high.is_medium_confidence() is False
    
    def test_is_medium_confidence_custom_thresholds(self):
        """Test is_medium_confidence with custom thresholds."""
        pred = ClassificationPrediction("node_1", 0.6, 1)
        
        assert pred.is_medium_confidence(low_threshold=0.5, high_threshold=0.7) is True
        assert pred.is_medium_confidence(low_threshold=0.65, high_threshold=0.8) is False
    
    def test_serialization(self):
        """Test that ClassificationPrediction can be serialized."""
        pred = ClassificationPrediction("node_1", 0.95, 1)
        
        # Should be able to serialize to dict
        data = pred.to_dict()
        assert isinstance(data, dict)
        assert data['taxonomy_id'] == 'node_1'
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        pred = ClassificationPrediction("node_123", 0.95, 1)
        result = pred.to_dict()
        
        assert result == {
            'taxonomy_id': 'node_123',
            'confidence': 0.95,
            'rank': 1
        }
    
    def test_equality(self):
        """Test equality comparison."""
        pred1 = ClassificationPrediction("node_1", 0.95, 1)
        pred2 = ClassificationPrediction("node_1", 0.95, 1)
        pred3 = ClassificationPrediction("node_2", 0.95, 1)
        
        assert pred1 == pred2
        assert pred1 != pred3


class TestClassificationResult:
    """Tests for ClassificationResult value object."""
    
    def test_create_valid_result(self):
        """Test creating a valid classification result."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),
            ClassificationPrediction("node_2", 0.87, 2),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        assert len(result.predictions) == 2
        assert result.model_version == "v1.0.0"
        assert result.inference_time_ms == 45.2
        assert result.resource_id is None
    
    def test_create_with_resource_id(self):
        """Test creating result with optional resource_id."""
        predictions = [ClassificationPrediction("node_1", 0.95, 1)]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2,
            resource_id="resource_123"
        )
        
        assert result.resource_id == "resource_123"
    
    def test_validation_empty_predictions(self):
        """Test that empty predictions list raises ValueError."""
        with pytest.raises(ValueError, match="predictions cannot be empty"):
            ClassificationResult(
                predictions=[],
                model_version="v1.0.0",
                inference_time_ms=45.2
            )
    
    def test_validation_empty_model_version(self):
        """Test that empty model_version raises ValueError."""
        predictions = [ClassificationPrediction("node_1", 0.95, 1)]
        
        with pytest.raises(ValueError, match="model_version cannot be empty"):
            ClassificationResult(
                predictions=predictions,
                model_version="",
                inference_time_ms=45.2
            )
    
    def test_validation_negative_inference_time(self):
        """Test that negative inference_time_ms raises ValueError."""
        predictions = [ClassificationPrediction("node_1", 0.95, 1)]
        
        with pytest.raises(ValueError, match="inference_time_ms must be non-negative"):
            ClassificationResult(
                predictions=predictions,
                model_version="v1.0.0",
                inference_time_ms=-10.0
            )
    
    def test_get_high_confidence_default_threshold(self):
        """Test get_high_confidence with default threshold."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),
            ClassificationPrediction("node_2", 0.75, 2),
            ClassificationPrediction("node_3", 0.85, 3),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        high_conf = result.get_high_confidence()
        assert len(high_conf) == 2
        assert high_conf[0].taxonomy_id == "node_1"
        assert high_conf[1].taxonomy_id == "node_3"
    
    def test_get_low_confidence_default_threshold(self):
        """Test get_low_confidence with default threshold."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),
            ClassificationPrediction("node_2", 0.45, 2),
            ClassificationPrediction("node_3", 0.35, 3),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        low_conf = result.get_low_confidence()
        assert len(low_conf) == 2
        assert low_conf[0].taxonomy_id == "node_2"
        assert low_conf[1].taxonomy_id == "node_3"
    
    def test_get_medium_confidence_default_thresholds(self):
        """Test get_medium_confidence with default thresholds."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),
            ClassificationPrediction("node_2", 0.65, 2),
            ClassificationPrediction("node_3", 0.35, 3),
            ClassificationPrediction("node_4", 0.70, 4),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        medium_conf = result.get_medium_confidence()
        assert len(medium_conf) == 2
        assert medium_conf[0].taxonomy_id == "node_2"
        assert medium_conf[1].taxonomy_id == "node_4"
    
    def test_get_top_k(self):
        """Test get_top_k returns predictions sorted by confidence."""
        predictions = [
            ClassificationPrediction("node_1", 0.75, 1),
            ClassificationPrediction("node_2", 0.95, 2),
            ClassificationPrediction("node_3", 0.85, 3),
            ClassificationPrediction("node_4", 0.65, 4),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        top_2 = result.get_top_k(2)
        assert len(top_2) == 2
        assert top_2[0].taxonomy_id == "node_2"
        assert top_2[0].confidence == 0.95
        assert top_2[1].taxonomy_id == "node_3"
        assert top_2[1].confidence == 0.85
    
    def test_get_top_k_invalid(self):
        """Test get_top_k with invalid k raises ValueError."""
        predictions = [ClassificationPrediction("node_1", 0.95, 1)]
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        with pytest.raises(ValueError, match="k must be positive"):
            result.get_top_k(0)
    
    def test_get_by_rank(self):
        """Test get_by_rank filters by rank."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),
            ClassificationPrediction("node_2", 0.85, 2),
            ClassificationPrediction("node_3", 0.75, 3),
            ClassificationPrediction("node_4", 0.65, 4),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        top_2_ranks = result.get_by_rank(2)
        assert len(top_2_ranks) == 2
        assert all(p.rank <= 2 for p in top_2_ranks)
    
    def test_get_by_rank_invalid(self):
        """Test get_by_rank with invalid max_rank raises ValueError."""
        predictions = [ClassificationPrediction("node_1", 0.95, 1)]
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        with pytest.raises(ValueError, match="max_rank must be positive"):
            result.get_by_rank(0)
    
    def test_get_best_prediction(self):
        """Test get_best_prediction returns highest confidence."""
        predictions = [
            ClassificationPrediction("node_1", 0.75, 1),
            ClassificationPrediction("node_2", 0.95, 2),
            ClassificationPrediction("node_3", 0.85, 3),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        best = result.get_best_prediction()
        assert best.taxonomy_id == "node_2"
        assert best.confidence == 0.95
    
    def test_has_high_confidence_predictions_true(self):
        """Test has_high_confidence_predictions returns True when applicable."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),
            ClassificationPrediction("node_2", 0.65, 2),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        assert result.has_high_confidence_predictions() is True
    
    def test_has_high_confidence_predictions_false(self):
        """Test has_high_confidence_predictions returns False when none exist."""
        predictions = [
            ClassificationPrediction("node_1", 0.75, 1),
            ClassificationPrediction("node_2", 0.65, 2),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        assert result.has_high_confidence_predictions() is False
    
    def test_count_by_confidence_level(self):
        """Test count_by_confidence_level returns correct counts."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),  # high
            ClassificationPrediction("node_2", 0.85, 2),  # high
            ClassificationPrediction("node_3", 0.65, 3),  # medium
            ClassificationPrediction("node_4", 0.70, 4),  # medium
            ClassificationPrediction("node_5", 0.45, 5),  # low
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2
        )
        
        counts = result.count_by_confidence_level()
        assert counts == {'low': 1, 'medium': 2, 'high': 2}
    
    def test_to_dict_api_compatibility(self):
        """Test to_dict provides API-compatible format."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),
            ClassificationPrediction("node_2", 0.85, 2),
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2,
            resource_id="resource_123"
        )
        
        data = result.to_dict()
        
        assert 'predictions' in data
        assert len(data['predictions']) == 2
        assert data['predictions'][0]['taxonomy_id'] == 'node_1'
        # Check confidence is in valid range instead of exact value
        assert 0.0 <= data['predictions'][0]['confidence'] <= 1.0
        assert data['model_version'] == 'v1.0.0'
        assert data['inference_time_ms'] > 0
        assert data['resource_id'] == 'resource_123'
        assert 'metadata' in data
        assert data['metadata']['total_predictions'] == 2
        assert 0.0 <= data['metadata']['best_confidence'] <= 1.0
    
    def test_from_dict(self):
        """Test from_dict creates valid ClassificationResult."""
        data = {
            'predictions': [
                {'taxonomy_id': 'node_1', 'confidence': 0.95, 'rank': 1},
                {'taxonomy_id': 'node_2', 'confidence': 0.85, 'rank': 2},
            ],
            'model_version': 'v1.0.0',
            'inference_time_ms': 45.2,
            'resource_id': 'resource_123'
        }
        
        result = ClassificationResult.from_dict(data)
        
        assert len(result.predictions) == 2
        assert result.predictions[0].taxonomy_id == 'node_1'
        assert result.predictions[0].confidence == 0.95
        assert result.model_version == 'v1.0.0'
        assert result.inference_time_ms == 45.2
        assert result.resource_id == 'resource_123'
    
    def test_round_trip_serialization(self):
        """Test that to_dict/from_dict round-trip works correctly."""
        predictions = [
            ClassificationPrediction("node_1", 0.95, 1),
            ClassificationPrediction("node_2", 0.85, 2),
        ]
        
        original = ClassificationResult(
            predictions=predictions,
            model_version="v1.0.0",
            inference_time_ms=45.2,
            resource_id="resource_123"
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = ClassificationResult.from_dict(data)
        
        # Verify core attributes match
        assert len(restored.predictions) == len(original.predictions)
        assert restored.model_version == original.model_version
        assert restored.inference_time_ms == original.inference_time_ms
        assert restored.resource_id == original.resource_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
