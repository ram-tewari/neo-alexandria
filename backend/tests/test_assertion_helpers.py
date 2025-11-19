"""
Tests for assertion helper functions.

This module tests the assertion helpers to ensure they work correctly
with both domain objects and dict representations.
"""

import pytest
from backend.tests.conftest import (
    assert_quality_score,
    assert_classification_result,
    assert_search_result,
    assert_recommendation
)


class TestAssertQualityScore:
    """Test assert_quality_score helper function."""
    
    def test_with_domain_object(self, quality_score_factory):
        """Test assertion with QualityScore domain object."""
        score = quality_score_factory(accuracy=0.9, completeness=0.8)
        
        # Should not raise
        assert_quality_score(score, min_overall=0.7)
        assert_quality_score(score, expected_level='high')
        assert_quality_score(score, expected_dimensions={'accuracy': 0.9})
    
    def test_with_dict(self):
        """Test assertion with dict representation."""
        score_dict = {
            'accuracy': 0.9,
            'completeness': 0.8,
            'consistency': 0.75,
            'timeliness': 0.85,
            'relevance': 0.8,
            'overall_score': 0.82
        }
        
        # Should not raise
        assert_quality_score(score_dict, min_overall=0.7)
        assert_quality_score(score_dict, expected_dimensions={'accuracy': 0.9})
    
    def test_overall_score_assertion(self, quality_score_factory):
        """Test overall score assertions."""
        score = quality_score_factory(accuracy=0.8, completeness=0.7)
        
        # Test exact match
        expected = score.overall_score()
        assert_quality_score(score, expected_overall=expected)
        
        # Test range
        assert_quality_score(score, min_overall=0.7, max_overall=0.9)
    
    def test_quality_level_assertion(self, quality_score_factory):
        """Test quality level assertions."""
        high_score = quality_score_factory(accuracy=0.9, completeness=0.9)
        assert_quality_score(high_score, expected_level='high')
        
        # Create a truly low score (all dimensions below 0.5)
        low_score = quality_score_factory(
            accuracy=0.2, completeness=0.2, consistency=0.2,
            timeliness=0.2, relevance=0.2
        )
        assert_quality_score(low_score, expected_level='low')
    
    def test_dimension_assertion(self, quality_score_factory):
        """Test individual dimension assertions."""
        score = quality_score_factory(accuracy=0.95, completeness=0.85)
        
        assert_quality_score(
            score,
            expected_dimensions={
                'accuracy': 0.95,
                'completeness': 0.85
            }
        )
    
    def test_assertion_failure(self, quality_score_factory):
        """Test that assertions fail when they should."""
        score = quality_score_factory(accuracy=0.5, completeness=0.5)
        
        with pytest.raises(AssertionError):
            assert_quality_score(score, min_overall=0.9)
        
        with pytest.raises(AssertionError):
            assert_quality_score(score, expected_level='high')


class TestAssertClassificationResult:
    """Test assert_classification_result helper function."""
    
    def test_with_domain_object(self, classification_result_factory):
        """Test assertion with ClassificationResult domain object."""
        from backend.app.domain.classification import ClassificationPrediction
        
        result = classification_result_factory(
            predictions=[
                ClassificationPrediction("004", 0.9, 1),
                ClassificationPrediction("006", 0.75, 2)
            ]
        )
        
        # Should not raise
        assert_classification_result(result, min_confidence=0.7)
        assert_classification_result(result, expected_count=2)
        assert_classification_result(result, check_high_confidence=True)
    
    def test_with_dict(self):
        """Test assertion with dict representation."""
        result_dict = {
            'predictions': [
                {'taxonomy_id': '004', 'confidence': 0.9, 'rank': 1},
                {'taxonomy_id': '006', 'confidence': 0.75, 'rank': 2}
            ],
            'model_version': 'test-v1',
            'inference_time_ms': 50.0
        }
        
        # Should not raise
        assert_classification_result(result_dict, min_confidence=0.7)
        assert_classification_result(result_dict, expected_count=2)
    
    def test_confidence_assertions(self, classification_result_factory):
        """Test confidence range assertions."""
        from backend.app.domain.classification import ClassificationPrediction
        
        result = classification_result_factory(
            predictions=[
                ClassificationPrediction("004", 0.9, 1),
                ClassificationPrediction("006", 0.85, 2)
            ]
        )
        
        assert_classification_result(result, min_confidence=0.8, max_confidence=1.0)
    
    def test_taxonomy_id_assertion(self, classification_result_factory):
        """Test taxonomy ID assertions."""
        from backend.app.domain.classification import ClassificationPrediction
        
        result = classification_result_factory(
            predictions=[
                ClassificationPrediction("004", 0.9, 1),
                ClassificationPrediction("006", 0.75, 2)
            ]
        )
        
        assert_classification_result(
            result,
            expected_taxonomy_ids=["004", "006"]
        )
    
    def test_high_confidence_check(self, classification_result_factory):
        """Test high confidence check."""
        from backend.app.domain.classification import ClassificationPrediction
        
        result = classification_result_factory(
            predictions=[
                ClassificationPrediction("004", 0.9, 1)
            ]
        )
        
        assert_classification_result(
            result,
            check_high_confidence=True,
            high_confidence_threshold=0.8
        )


class TestAssertSearchResult:
    """Test assert_search_result helper function."""
    
    def test_with_domain_object(self, search_result_factory):
        """Test assertion with SearchResult domain object."""
        result = search_result_factory(score=0.95, rank=1)
        
        # Should not raise
        assert_search_result(result, min_score=0.9)
        assert_search_result(result, max_rank=5)
        assert_search_result(result, check_high_score=True)
    
    def test_with_dict(self):
        """Test assertion with dict representation."""
        result_dict = {
            'resource_id': 'test-res-123',
            'score': 0.95,
            'rank': 1,
            'title': 'Test Resource',
            'search_method': 'hybrid'
        }
        
        # Should not raise
        assert_search_result(result_dict, min_score=0.9)
        assert_search_result(result_dict, expected_rank=1)
    
    def test_score_assertions(self, search_result_factory):
        """Test score range assertions."""
        result = search_result_factory(score=0.85)
        
        assert_search_result(result, min_score=0.8, max_score=0.9)
        assert_search_result(result, check_high_score=True, high_score_threshold=0.8)
    
    def test_rank_assertions(self, search_result_factory):
        """Test rank assertions."""
        result = search_result_factory(rank=3)
        
        assert_search_result(result, expected_rank=3)
        assert_search_result(result, max_rank=5)
    
    def test_metadata_assertions(self, search_result_factory):
        """Test metadata assertions."""
        result = search_result_factory(
            metadata={'source': 'test', 'type': 'article'}
        )
        
        assert_search_result(
            result,
            check_metadata={'source': 'test', 'type': 'article'}
        )


class TestAssertRecommendation:
    """Test assert_recommendation helper function."""
    
    def test_with_domain_object(self, recommendation_factory):
        """Test assertion with Recommendation domain object."""
        rec = recommendation_factory(score=0.9, confidence=0.85)
        
        # Should not raise
        assert_recommendation(rec, min_score=0.8)
        assert_recommendation(rec, min_confidence=0.8)
        assert_recommendation(rec, check_high_quality=True)
    
    def test_with_dict(self):
        """Test assertion with dict representation."""
        rec_dict = {
            'resource_id': 'test-res-123',
            'user_id': 'test-user-456',
            'score': 0.9,
            'confidence': 0.85,
            'rank': 1,
            'strategy': 'hybrid'
        }
        
        # Should not raise
        assert_recommendation(rec_dict, min_score=0.8)
        assert_recommendation(rec_dict, min_confidence=0.8)
    
    def test_with_nested_score_dict(self):
        """Test assertion with nested recommendation_score structure."""
        rec_dict = {
            'resource_id': 'test-res-123',
            'user_id': 'test-user-456',
            'recommendation_score': {
                'score': 0.9,
                'confidence': 0.85,
                'rank': 1
            },
            'strategy': 'hybrid'
        }
        
        # Should not raise
        assert_recommendation(rec_dict, min_score=0.8)
        assert_recommendation(rec_dict, min_confidence=0.8)
    
    def test_score_and_confidence_assertions(self, recommendation_factory):
        """Test score and confidence range assertions."""
        rec = recommendation_factory(score=0.85, confidence=0.9)
        
        assert_recommendation(rec, min_score=0.8, max_score=0.9)
        assert_recommendation(rec, min_confidence=0.85, max_confidence=0.95)
    
    def test_high_quality_check(self, recommendation_factory):
        """Test high quality check."""
        rec = recommendation_factory(score=0.9, confidence=0.85)
        
        assert_recommendation(
            rec,
            check_high_quality=True,
            score_threshold=0.7,
            confidence_threshold=0.8
        )
    
    def test_rank_assertions(self, recommendation_factory):
        """Test rank assertions."""
        rec = recommendation_factory(rank=2)
        
        assert_recommendation(rec, expected_rank=2)
        assert_recommendation(rec, max_rank=5)
    
    def test_metadata_assertions(self, recommendation_factory):
        """Test metadata assertions."""
        rec = recommendation_factory(
            metadata={'source': 'test', 'type': 'content-based'}
        )
        
        assert_recommendation(
            rec,
            check_metadata={'source': 'test', 'type': 'content-based'}
        )
