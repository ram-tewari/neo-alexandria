"""
Tests for recommendation domain objects.

This module tests the Recommendation and RecommendationScore domain objects,
verifying validation, business logic, and API compatibility.
"""

import pytest
from backend.app.domain.recommendation import (
    Recommendation,
    RecommendationScore,
)


class TestRecommendationScore:
    """Tests for RecommendationScore value object."""
    
    def test_create_valid_score(self):
        """Test creating a valid recommendation score."""
        score = RecommendationScore(
            score=0.85,
            confidence=0.9,
            rank=1
        )
        
        assert score.score == 0.85
        assert score.confidence == 0.9
        assert score.rank == 1
    
    def test_score_validation_too_low(self):
        """Test that score below 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="score must be between 0.0 and 1.0"):
            RecommendationScore(
                score=-0.1,
                confidence=0.9,
                rank=1
            )
    
    def test_score_validation_too_high(self):
        """Test that score above 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="score must be between 0.0 and 1.0"):
            RecommendationScore(
                score=1.5,
                confidence=0.9,
                rank=1
            )
    
    def test_confidence_validation_too_low(self):
        """Test that confidence below 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            RecommendationScore(
                score=0.85,
                confidence=-0.1,
                rank=1
            )
    
    def test_confidence_validation_too_high(self):
        """Test that confidence above 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            RecommendationScore(
                score=0.85,
                confidence=1.5,
                rank=1
            )
    
    def test_rank_validation_zero(self):
        """Test that rank of 0 raises ValueError."""
        with pytest.raises(ValueError, match="rank must be positive"):
            RecommendationScore(
                score=0.85,
                confidence=0.9,
                rank=0
            )
    
    def test_rank_validation_negative(self):
        """Test that negative rank raises ValueError."""
        with pytest.raises(ValueError, match="rank must be positive"):
            RecommendationScore(
                score=0.85,
                confidence=0.9,
                rank=-1
            )
    
    def test_boundary_values(self):
        """Test that boundary values (0.0 and 1.0) are valid."""
        score = RecommendationScore(
            score=0.0,
            confidence=1.0,
            rank=1
        )
        
        assert score.score == 0.0
        assert score.confidence == 1.0
    
    def test_is_high_confidence_default_threshold(self):
        """Test is_high_confidence with default threshold (0.8)."""
        high_conf = RecommendationScore(0.85, 0.85, 1)
        low_conf = RecommendationScore(0.85, 0.75, 2)
        
        assert high_conf.is_high_confidence() is True
        assert low_conf.is_high_confidence() is False
    
    def test_is_low_confidence_default_threshold(self):
        """Test is_low_confidence with default threshold (0.5)."""
        low_conf = RecommendationScore(0.85, 0.45, 1)
        high_conf = RecommendationScore(0.85, 0.55, 2)
        
        assert low_conf.is_low_confidence() is True
        assert high_conf.is_low_confidence() is False
    
    def test_is_high_score_default_threshold(self):
        """Test is_high_score with default threshold (0.7)."""
        high_score = RecommendationScore(0.75, 0.9, 1)
        low_score = RecommendationScore(0.65, 0.9, 2)
        
        assert high_score.is_high_score() is True
        assert low_score.is_high_score() is False
    
    def test_is_top_ranked_default(self):
        """Test is_top_ranked with default top_k (5)."""
        top_rec = RecommendationScore(0.85, 0.9, 3)
        not_top_rec = RecommendationScore(0.85, 0.9, 6)
        
        assert top_rec.is_top_ranked() is True
        assert not_top_rec.is_top_ranked() is False
    
    def test_combined_quality(self):
        """Test combined_quality calculation."""
        score = RecommendationScore(0.8, 0.9, 1)
        
        # Expected: 0.7 * 0.8 + 0.3 * 0.9 = 0.56 + 0.27 = 0.83
        expected = 0.83
        assert abs(score.combined_quality() - expected) < 0.001


class TestRecommendation:
    """Tests for Recommendation value object."""
    
    def test_create_valid_recommendation(self):
        """Test creating a valid recommendation."""
        rec_score = RecommendationScore(0.85, 0.9, 1)
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=rec_score,
            strategy="collaborative"
        )
        
        assert rec.resource_id == "resource_123"
        assert rec.user_id == "user_456"
        assert rec.recommendation_score == rec_score
        assert rec.strategy == "collaborative"
        assert rec.reason is None
        assert rec.metadata == {}
    
    def test_create_with_optional_fields(self):
        """Test creating recommendation with optional fields."""
        rec_score = RecommendationScore(0.85, 0.9, 1)
        metadata = {"source": "ncf_model"}
        
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=rec_score,
            strategy="collaborative",
            reason="Similar users liked this",
            metadata=metadata
        )
        
        assert rec.reason == "Similar users liked this"
        assert rec.metadata == {"source": "ncf_model"}
    
    def test_validation_empty_resource_id(self):
        """Test that empty resource_id raises ValueError."""
        rec_score = RecommendationScore(0.85, 0.9, 1)
        
        with pytest.raises(ValueError, match="resource_id cannot be empty"):
            Recommendation(
                resource_id="",
                user_id="user_456",
                recommendation_score=rec_score
            )
    
    def test_validation_empty_user_id(self):
        """Test that empty user_id raises ValueError."""
        rec_score = RecommendationScore(0.85, 0.9, 1)
        
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            Recommendation(
                resource_id="resource_123",
                user_id="",
                recommendation_score=rec_score
            )
    
    def test_get_score(self):
        """Test get_score returns score from recommendation_score."""
        rec_score = RecommendationScore(0.85, 0.9, 1)
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=rec_score
        )
        
        assert rec.get_score() == 0.85
    
    def test_get_confidence(self):
        """Test get_confidence returns confidence from recommendation_score."""
        rec_score = RecommendationScore(0.85, 0.9, 1)
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=rec_score
        )
        
        assert rec.get_confidence() == 0.9
    
    def test_get_rank(self):
        """Test get_rank returns rank from recommendation_score."""
        rec_score = RecommendationScore(0.85, 0.9, 3)
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=rec_score
        )
        
        assert rec.get_rank() == 3
    
    def test_is_high_quality_true(self):
        """Test is_high_quality returns True when both thresholds met."""
        rec_score = RecommendationScore(0.75, 0.85, 1)
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=rec_score
        )
        
        assert rec.is_high_quality() is True
    
    def test_is_high_quality_false_low_score(self):
        """Test is_high_quality returns False when score below threshold."""
        rec_score = RecommendationScore(0.65, 0.85, 1)
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=rec_score
        )
        
        assert rec.is_high_quality() is False
    
    def test_is_high_quality_false_low_confidence(self):
        """Test is_high_quality returns False when confidence below threshold."""
        rec_score = RecommendationScore(0.75, 0.75, 1)
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=rec_score
        )
        
        assert rec.is_high_quality() is False
    
    def test_is_top_recommendation(self):
        """Test is_top_recommendation checks rank."""
        top_rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.85, 0.9, 3)
        )
        
        not_top_rec = Recommendation(
            resource_id="resource_456",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.75, 0.8, 6)
        )
        
        assert top_rec.is_top_recommendation() is True
        assert not_top_rec.is_top_recommendation() is False
    
    def test_get_metadata_value(self):
        """Test get_metadata_value retrieves metadata."""
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.85, 0.9, 1),
            metadata={"source": "ncf_model", "version": "v1.0"}
        )
        
        assert rec.get_metadata_value("source") == "ncf_model"
        assert rec.get_metadata_value("version") == "v1.0"
        assert rec.get_metadata_value("missing", "default") == "default"
    
    def test_has_metadata(self):
        """Test has_metadata checks for key existence."""
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.85, 0.9, 1),
            metadata={"source": "ncf_model"}
        )
        
        assert rec.has_metadata("source") is True
        assert rec.has_metadata("missing") is False
    
    def test_comparison_operators(self):
        """Test comparison operators for sorting."""
        rec1 = Recommendation(
            resource_id="resource_1",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.85, 0.9, 1)
        )
        
        rec2 = Recommendation(
            resource_id="resource_2",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.75, 0.8, 2)
        )
        
        rec3 = Recommendation(
            resource_id="resource_3",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.65, 0.7, 3)
        )
        
        # Lower rank is better
        assert rec1 < rec2
        assert rec2 < rec3
        assert rec1 <= rec2
        assert rec2 > rec1
        assert rec3 > rec2
        assert rec2 >= rec1
    
    def test_sorting(self):
        """Test that recommendations can be sorted by rank."""
        rec1 = Recommendation(
            resource_id="resource_1",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.65, 0.7, 3)
        )
        
        rec2 = Recommendation(
            resource_id="resource_2",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.85, 0.9, 1)
        )
        
        rec3 = Recommendation(
            resource_id="resource_3",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.75, 0.8, 2)
        )
        
        recommendations = [rec1, rec2, rec3]
        sorted_recs = sorted(recommendations)
        
        assert sorted_recs[0].get_rank() == 1
        assert sorted_recs[1].get_rank() == 2
        assert sorted_recs[2].get_rank() == 3
    
    def test_to_dict_api_compatibility(self):
        """Test to_dict provides API-compatible format."""
        rec = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.85, 0.9, 1),
            strategy="collaborative",
            reason="Similar users liked this",
            metadata={"source": "ncf_model"}
        )
        
        data = rec.to_dict()
        
        assert data['resource_id'] == "resource_123"
        assert data['user_id'] == "user_456"
        assert data['score'] == 0.85
        assert data['confidence'] == 0.9
        assert data['rank'] == 1
        assert data['strategy'] == "collaborative"
        assert data['reason'] == "Similar users liked this"
        assert data['metadata'] == {"source": "ncf_model"}
        assert 'quality_metrics' in data
        assert 'is_high_quality' in data['quality_metrics']
        assert 'combined_quality' in data['quality_metrics']
    
    def test_from_dict_nested_structure(self):
        """Test from_dict with nested recommendation_score."""
        data = {
            'resource_id': 'resource_123',
            'user_id': 'user_456',
            'recommendation_score': {
                'score': 0.85,
                'confidence': 0.9,
                'rank': 1
            },
            'strategy': 'collaborative',
            'reason': 'Similar users liked this',
            'metadata': {'source': 'ncf_model'}
        }
        
        rec = Recommendation.from_dict(data)
        
        assert rec.resource_id == 'resource_123'
        assert rec.user_id == 'user_456'
        assert rec.get_score() == 0.85
        assert rec.get_confidence() == 0.9
        assert rec.get_rank() == 1
        assert rec.strategy == 'collaborative'
        assert rec.reason == 'Similar users liked this'
    
    def test_from_dict_flat_structure(self):
        """Test from_dict with flat structure (score at top level)."""
        data = {
            'resource_id': 'resource_123',
            'user_id': 'user_456',
            'score': 0.85,
            'confidence': 0.9,
            'rank': 1,
            'strategy': 'collaborative'
        }
        
        rec = Recommendation.from_dict(data)
        
        assert rec.resource_id == 'resource_123'
        assert rec.user_id == 'user_456'
        assert rec.get_score() == 0.85
        assert rec.get_confidence() == 0.9
        assert rec.get_rank() == 1
    
    def test_round_trip_serialization(self):
        """Test that to_dict/from_dict round-trip works correctly."""
        original = Recommendation(
            resource_id="resource_123",
            user_id="user_456",
            recommendation_score=RecommendationScore(0.85, 0.9, 1),
            strategy="collaborative",
            reason="Similar users liked this",
            metadata={"source": "ncf_model"}
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = Recommendation.from_dict(data)
        
        # Verify core attributes match
        assert restored.resource_id == original.resource_id
        assert restored.user_id == original.user_id
        assert restored.get_score() == original.get_score()
        assert restored.get_confidence() == original.get_confidence()
        assert restored.get_rank() == original.get_rank()
        assert restored.strategy == original.strategy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
