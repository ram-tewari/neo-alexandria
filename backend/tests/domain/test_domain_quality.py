"""
Tests for quality domain objects.

This module tests the QualityScore domain object, verifying validation,
business logic, and API compatibility.
"""

import pytest
from backend.app.domain.quality import QualityScore


class TestQualityScore:
    """Tests for QualityScore value object."""
    
    def test_create_valid_quality_score(self):
        """Test creating a valid quality score."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.6,
            relevance=0.75
        )
        
        assert score.accuracy == 0.8
        assert score.completeness == 0.7
        assert score.consistency == 0.9
        assert score.timeliness == 0.6
        assert score.relevance == 0.75
    
    def test_dimension_validation_too_low(self):
        """Test that dimension below 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="accuracy must be between 0.0 and 1.0"):
            QualityScore(
                accuracy=-0.1,
                completeness=0.7,
                consistency=0.9,
                timeliness=0.6,
                relevance=0.75
            )
    
    def test_dimension_validation_too_high(self):
        """Test that dimension above 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="completeness must be between 0.0 and 1.0"):
            QualityScore(
                accuracy=0.8,
                completeness=1.5,
                consistency=0.9,
                timeliness=0.6,
                relevance=0.75
            )
    
    def test_dimension_boundary_values(self):
        """Test that dimension boundary values (0.0 and 1.0) are valid."""
        score = QualityScore(
            accuracy=0.0,
            completeness=1.0,
            consistency=0.5,
            timeliness=0.0,
            relevance=1.0
        )
        
        assert score.accuracy == 0.0
        assert score.completeness == 1.0
    
    def test_overall_score_calculation(self):
        """Test overall score weighted calculation."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.6,
            consistency=0.7,
            timeliness=0.5,
            relevance=0.9
        )
        
        # Expected: 0.3*0.8 + 0.2*0.6 + 0.2*0.7 + 0.15*0.5 + 0.15*0.9
        # = 0.24 + 0.12 + 0.14 + 0.075 + 0.135 = 0.71
        expected = 0.71
        assert abs(score.overall_score() - expected) < 0.001
    
    def test_is_high_quality_default_threshold(self):
        """Test is_high_quality with default threshold (0.7)."""
        high_score = QualityScore(
            accuracy=0.9,
            completeness=0.8,
            consistency=0.8,
            timeliness=0.7,
            relevance=0.8
        )
        
        low_score = QualityScore(
            accuracy=0.6,
            completeness=0.5,
            consistency=0.6,
            timeliness=0.5,
            relevance=0.6
        )
        
        assert high_score.is_high_quality() is True
        assert low_score.is_high_quality() is False
    
    def test_is_high_quality_custom_threshold(self):
        """Test is_high_quality with custom threshold."""
        score = QualityScore(
            accuracy=0.7,
            completeness=0.6,
            consistency=0.7,
            timeliness=0.6,
            relevance=0.7
        )
        
        assert score.is_high_quality(threshold=0.6) is True
        assert score.is_high_quality(threshold=0.8) is False
    
    def test_is_low_quality_default_threshold(self):
        """Test is_low_quality with default threshold (0.5)."""
        low_score = QualityScore(
            accuracy=0.4,
            completeness=0.3,
            consistency=0.4,
            timeliness=0.3,
            relevance=0.4
        )
        
        high_score = QualityScore(
            accuracy=0.7,
            completeness=0.6,
            consistency=0.7,
            timeliness=0.6,
            relevance=0.7
        )
        
        assert low_score.is_low_quality() is True
        assert high_score.is_low_quality() is False
    
    def test_is_medium_quality_default_thresholds(self):
        """Test is_medium_quality with default thresholds."""
        low_score = QualityScore(
            accuracy=0.4,
            completeness=0.3,
            consistency=0.4,
            timeliness=0.3,
            relevance=0.4
        )
        
        medium_score = QualityScore(
            accuracy=0.6,
            completeness=0.6,
            consistency=0.6,
            timeliness=0.6,
            relevance=0.6
        )
        
        high_score = QualityScore(
            accuracy=0.9,
            completeness=0.8,
            consistency=0.8,
            timeliness=0.7,
            relevance=0.8
        )
        
        assert low_score.is_medium_quality() is False
        assert medium_score.is_medium_quality() is True
        assert high_score.is_medium_quality() is False
    
    def test_get_quality_level(self):
        """Test get_quality_level returns correct classification."""
        high_score = QualityScore(
            accuracy=0.9,
            completeness=0.8,
            consistency=0.8,
            timeliness=0.7,
            relevance=0.8
        )
        
        medium_score = QualityScore(
            accuracy=0.6,
            completeness=0.6,
            consistency=0.6,
            timeliness=0.6,
            relevance=0.6
        )
        
        low_score = QualityScore(
            accuracy=0.4,
            completeness=0.3,
            consistency=0.4,
            timeliness=0.3,
            relevance=0.4
        )
        
        assert high_score.get_quality_level() == 'high'
        assert medium_score.get_quality_level() == 'medium'
        assert low_score.get_quality_level() == 'low'
    
    def test_get_weakest_dimension(self):
        """Test get_weakest_dimension identifies lowest score."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.3,  # Weakest
            relevance=0.75
        )
        
        assert score.get_weakest_dimension() == 'timeliness'
    
    def test_get_strongest_dimension(self):
        """Test get_strongest_dimension identifies highest score."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.95,  # Strongest
            timeliness=0.6,
            relevance=0.75
        )
        
        assert score.get_strongest_dimension() == 'consistency'
    
    def test_get_dimension_scores(self):
        """Test get_dimension_scores returns all dimensions."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.6,
            relevance=0.75
        )
        
        dimensions = score.get_dimension_scores()
        
        assert dimensions == {
            'accuracy': 0.8,
            'completeness': 0.7,
            'consistency': 0.9,
            'timeliness': 0.6,
            'relevance': 0.75
        }
    
    def test_has_dimension_below_threshold_true(self):
        """Test has_dimension_below_threshold returns True when applicable."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.3,  # Below 0.5
            relevance=0.75
        )
        
        assert score.has_dimension_below_threshold(threshold=0.5) is True
    
    def test_has_dimension_below_threshold_false(self):
        """Test has_dimension_below_threshold returns False when none below."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.6,
            relevance=0.75
        )
        
        assert score.has_dimension_below_threshold(threshold=0.5) is False
    
    def test_count_dimensions_below_threshold(self):
        """Test count_dimensions_below_threshold returns correct count."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.4,  # Below 0.5
            consistency=0.9,
            timeliness=0.3,  # Below 0.5
            relevance=0.75
        )
        
        assert score.count_dimensions_below_threshold(threshold=0.5) == 2
    
    def test_to_dict_api_compatibility(self):
        """Test to_dict provides API-compatible format."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.6,
            relevance=0.75
        )
        
        data = score.to_dict()
        
        assert data['accuracy'] == 0.8
        assert data['completeness'] == 0.7
        assert data['consistency'] == 0.9
        assert data['timeliness'] == 0.6
        assert data['relevance'] == 0.75
        assert 'overall_score' in data
        assert 'quality_level' in data
        assert 'metadata' in data
        assert 'weakest_dimension' in data['metadata']
        assert 'strongest_dimension' in data['metadata']
    
    def test_from_dict(self):
        """Test from_dict creates valid QualityScore."""
        data = {
            'accuracy': 0.8,
            'completeness': 0.7,
            'consistency': 0.9,
            'timeliness': 0.6,
            'relevance': 0.75
        }
        
        score = QualityScore.from_dict(data)
        
        assert score.accuracy == 0.8
        assert score.completeness == 0.7
        assert score.consistency == 0.9
        assert score.timeliness == 0.6
        assert score.relevance == 0.75
    
    def test_round_trip_serialization(self):
        """Test that to_dict/from_dict round-trip works correctly."""
        original = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.6,
            relevance=0.75
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = QualityScore.from_dict(data)
        
        # Verify all dimensions match
        assert restored.accuracy == original.accuracy
        assert restored.completeness == original.completeness
        assert restored.consistency == original.consistency
        assert restored.timeliness == original.timeliness
        assert restored.relevance == original.relevance
    
    def test_equality(self):
        """Test equality comparison."""
        score1 = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.6,
            relevance=0.75
        )
        
        score2 = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.6,
            relevance=0.75
        )
        
        score3 = QualityScore(
            accuracy=0.9,
            completeness=0.7,
            consistency=0.9,
            timeliness=0.6,
            relevance=0.75
        )
        
        assert score1 == score2
        assert score1 != score3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
