"""
Test that all domain objects have the expected attributes and methods.

This test verifies that domain objects don't have AttributeError issues
by checking that all commonly used methods and attributes exist and work correctly.
"""

import pytest
from backend.app.domain.quality import QualityScore
from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
from backend.app.domain.search import SearchResult, SearchResults, SearchQuery
from backend.app.domain.recommendation import Recommendation, RecommendationScore


class TestQualityScoreAttributes:
    """Test QualityScore has all expected attributes and methods."""
    
    def test_quality_score_attributes(self):
        """Test QualityScore has all dimension attributes."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.75,
            consistency=0.7,
            timeliness=0.85,
            relevance=0.8
        )
        
        # Test attributes exist
        assert hasattr(score, 'accuracy')
        assert hasattr(score, 'completeness')
        assert hasattr(score, 'consistency')
        assert hasattr(score, 'timeliness')
        assert hasattr(score, 'relevance')
        
        # Test attribute access
        assert score.accuracy == 0.8
        assert score.completeness == 0.75
        assert score.consistency == 0.7
        assert score.timeliness == 0.85
        assert score.relevance == 0.8
    
    def test_quality_score_methods(self):
        """Test QualityScore has all expected methods."""
        score = QualityScore(0.8, 0.75, 0.7, 0.85, 0.8)
        
        # Test methods exist
        assert hasattr(score, 'overall_score')
        assert hasattr(score, 'is_high_quality')
        assert hasattr(score, 'is_low_quality')
        assert hasattr(score, 'is_medium_quality')
        assert hasattr(score, 'get_quality_level')
        assert hasattr(score, 'get_weakest_dimension')
        assert hasattr(score, 'get_strongest_dimension')
        assert hasattr(score, 'to_dict')
        assert hasattr(score, 'validate')
        
        # Test methods work
        assert isinstance(score.overall_score(), float)
        assert isinstance(score.is_high_quality(), bool)
        assert isinstance(score.get_quality_level(), str)
        assert isinstance(score.get_weakest_dimension(), str)
        assert isinstance(score.to_dict(), dict)
    
    def test_quality_score_from_dict(self):
        """Test QualityScore.from_dict class method."""
        data = {
            'accuracy': 0.8,
            'completeness': 0.75,
            'consistency': 0.7,
            'timeliness': 0.85,
            'relevance': 0.8
        }
        
        score = QualityScore.from_dict(data)
        assert isinstance(score, QualityScore)
        assert score.accuracy == 0.8


class TestClassificationResultAttributes:
    """Test ClassificationResult has all expected attributes and methods."""
    
    def test_classification_result_attributes(self):
        """Test ClassificationResult has all expected attributes."""
        predictions = [
            ClassificationPrediction("cat1", 0.9, 1),
            ClassificationPrediction("cat2", 0.7, 2)
        ]
        
        result = ClassificationResult(
            predictions=predictions,
            model_version="v1.0",
            inference_time_ms=50.0,
            resource_id="test-id"
        )
        
        # Test attributes exist
        assert hasattr(result, 'predictions')
        assert hasattr(result, 'model_version')
        assert hasattr(result, 'inference_time_ms')
        assert hasattr(result, 'resource_id')
        
        # Test attribute access
        assert len(result.predictions) == 2
        assert result.model_version == "v1.0"
        assert result.inference_time_ms == 50.0
    
    def test_classification_result_methods(self):
        """Test ClassificationResult has all expected methods."""
        predictions = [ClassificationPrediction("cat1", 0.9, 1)]
        result = ClassificationResult(predictions, "v1.0", 50.0, "test-id")
        
        # Test methods exist
        assert hasattr(result, 'get_top_prediction')
        assert hasattr(result, 'get_predictions_above_threshold')
        assert hasattr(result, 'has_high_confidence_prediction')
        assert hasattr(result, 'to_dict')
        assert hasattr(result, 'validate')
        
        # Test methods work
        assert isinstance(result.get_top_prediction(), ClassificationPrediction)
        assert isinstance(result.get_predictions_above_threshold(0.5), list)
        assert isinstance(result.has_high_confidence_prediction(), bool)
        assert isinstance(result.to_dict(), dict)


class TestSearchResultAttributes:
    """Test SearchResult has all expected attributes and methods."""
    
    def test_search_result_attributes(self):
        """Test SearchResult has all expected attributes."""
        result = SearchResult(
            resource_id="res-123",
            score=0.95,
            rank=1,
            title="Test Result",
            search_method="hybrid"
        )
        
        # Test attributes exist
        assert hasattr(result, 'resource_id')
        assert hasattr(result, 'score')
        assert hasattr(result, 'rank')
        assert hasattr(result, 'title')
        assert hasattr(result, 'search_method')
        assert hasattr(result, 'metadata')
        
        # Test attribute access
        assert result.resource_id == "res-123"
        assert result.score == 0.95
        assert result.rank == 1
    
    def test_search_result_methods(self):
        """Test SearchResult has all expected methods."""
        result = SearchResult("res-123", 0.95, 1, "Test", "hybrid")
        
        # Test methods exist
        assert hasattr(result, 'is_high_score')
        assert hasattr(result, 'is_low_score')
        assert hasattr(result, 'is_top_result')
        assert hasattr(result, 'get_metadata_value')
        assert hasattr(result, 'has_metadata')
        assert hasattr(result, 'to_dict')
        assert hasattr(result, 'validate')
        
        # Test methods work
        assert isinstance(result.is_high_score(), bool)
        assert isinstance(result.is_top_result(), bool)
        assert isinstance(result.to_dict(), dict)


class TestRecommendationAttributes:
    """Test Recommendation has all expected attributes and methods."""
    
    def test_recommendation_attributes(self):
        """Test Recommendation has all expected attributes."""
        rec_score = RecommendationScore(score=0.88, confidence=0.82, rank=1)
        rec = Recommendation(
            resource_id="res-123",
            user_id="user-456",
            recommendation_score=rec_score,
            strategy="hybrid"
        )
        
        # Test attributes exist
        assert hasattr(rec, 'resource_id')
        assert hasattr(rec, 'user_id')
        assert hasattr(rec, 'recommendation_score')
        assert hasattr(rec, 'strategy')
        assert hasattr(rec, 'reason')
        assert hasattr(rec, 'metadata')
        
        # Test attribute access
        assert rec.resource_id == "res-123"
        assert rec.user_id == "user-456"
        assert isinstance(rec.recommendation_score, RecommendationScore)
    
    def test_recommendation_methods(self):
        """Test Recommendation has all expected methods."""
        rec_score = RecommendationScore(0.88, 0.82, 1)
        rec = Recommendation("res-123", "user-456", rec_score, "hybrid")
        
        # Test methods exist
        assert hasattr(rec, 'get_score')
        assert hasattr(rec, 'get_confidence')
        assert hasattr(rec, 'get_rank')
        assert hasattr(rec, 'is_high_confidence')
        assert hasattr(rec, 'is_high_score')
        assert hasattr(rec, 'is_top_ranked')
        assert hasattr(rec, 'to_dict')
        assert hasattr(rec, 'validate')
        
        # Test methods work
        assert isinstance(rec.get_score(), float)
        assert isinstance(rec.get_confidence(), float)
        assert isinstance(rec.get_rank(), int)
        assert isinstance(rec.is_high_confidence(), bool)
        assert isinstance(rec.to_dict(), dict)
    
    def test_recommendation_score_attributes(self):
        """Test RecommendationScore has all expected attributes."""
        score = RecommendationScore(score=0.88, confidence=0.82, rank=1)
        
        # Test attributes exist
        assert hasattr(score, 'score')
        assert hasattr(score, 'confidence')
        assert hasattr(score, 'rank')
        
        # Test attribute access
        assert score.score == 0.88
        assert score.confidence == 0.82
        assert score.rank == 1
    
    def test_recommendation_score_methods(self):
        """Test RecommendationScore has all expected methods."""
        score = RecommendationScore(0.88, 0.82, 1)
        
        # Test methods exist
        assert hasattr(score, 'is_high_confidence')
        assert hasattr(score, 'is_low_confidence')
        assert hasattr(score, 'is_high_score')
        assert hasattr(score, 'is_top_ranked')
        assert hasattr(score, 'combined_quality')
        assert hasattr(score, 'validate')
        
        # Test methods work
        assert isinstance(score.is_high_confidence(), bool)
        assert isinstance(score.is_high_score(), bool)
        assert isinstance(score.combined_quality(), float)


class TestClassificationPredictionAttributes:
    """Test ClassificationPrediction has all expected attributes and methods."""
    
    def test_classification_prediction_attributes(self):
        """Test ClassificationPrediction has all expected attributes."""
        pred = ClassificationPrediction(
            taxonomy_id="cat1",
            confidence=0.9,
            rank=1
        )
        
        # Test attributes exist
        assert hasattr(pred, 'taxonomy_id')
        assert hasattr(pred, 'confidence')
        assert hasattr(pred, 'rank')
        
        # Test attribute access
        assert pred.taxonomy_id == "cat1"
        assert pred.confidence == 0.9
        assert pred.rank == 1
    
    def test_classification_prediction_methods(self):
        """Test ClassificationPrediction has all expected methods."""
        pred = ClassificationPrediction("cat1", 0.9, 1)
        
        # Test methods exist
        assert hasattr(pred, 'is_high_confidence')
        assert hasattr(pred, 'is_low_confidence')
        assert hasattr(pred, 'is_top_prediction')
        assert hasattr(pred, 'to_dict')
        assert hasattr(pred, 'validate')
        
        # Test methods work
        assert isinstance(pred.is_high_confidence(), bool)
        assert isinstance(pred.is_top_prediction(), bool)
        assert isinstance(pred.to_dict(), dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
