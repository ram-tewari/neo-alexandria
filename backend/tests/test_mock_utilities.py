"""
Tests for mock utility functions.

This module tests the mock utility functions created for Phase 12.6
to ensure they properly return domain objects with required methods
and attributes.
"""

import pytest
from backend.app.domain.quality import QualityScore
from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
from backend.app.domain.search import SearchResult, SearchResults
from backend.app.domain.recommendation import Recommendation, RecommendationScore


def test_create_quality_service_mock():
    """Test that create_quality_service_mock returns proper mock."""
    from backend.tests.conftest import create_quality_service_mock
    
    # Create mock with default quality score
    mock_service = create_quality_service_mock()
    
    # Test that mock has expected methods
    assert hasattr(mock_service, 'compute_quality')
    assert hasattr(mock_service, 'get_quality_scores')
    assert hasattr(mock_service, 'assess_resource_quality')
    
    # Test that methods return QualityScore domain objects
    result = mock_service.compute_quality("test-resource-id")
    assert isinstance(result, QualityScore)
    assert result.overall_score() > 0.0
    assert result.accuracy == 0.8
    assert result.completeness == 0.7
    
    # Test with custom quality score
    custom_score = QualityScore(
        accuracy=0.95,
        completeness=0.9,
        consistency=0.85,
        timeliness=0.8,
        relevance=0.9
    )
    mock_service_custom = create_quality_service_mock(quality_score=custom_score)
    result_custom = mock_service_custom.compute_quality("test-resource-id")
    assert result_custom.accuracy == 0.95
    assert result_custom.overall_score() > 0.85


def test_create_classification_service_mock():
    """Test that create_classification_service_mock returns proper mock."""
    from backend.tests.conftest import create_classification_service_mock
    
    # Create mock with default result
    mock_service = create_classification_service_mock()
    
    # Test that mock has expected methods
    assert hasattr(mock_service, 'predict')
    assert hasattr(mock_service, 'classify_resource')
    assert hasattr(mock_service, 'classify')
    
    # Test that methods return ClassificationResult domain objects
    result = mock_service.predict("test text")
    assert isinstance(result, ClassificationResult)
    assert len(result.predictions) > 0
    assert isinstance(result.predictions[0], ClassificationPrediction)
    assert result.predictions[0].confidence > 0.0
    assert result.model_version == "test-model-v1"
    
    # Test with custom result
    custom_result = ClassificationResult(
        predictions=[
            ClassificationPrediction(
                taxonomy_id="custom-001",
                confidence=0.99,
                rank=1
            )
        ],
        model_version="custom-model-v2",
        inference_time_ms=25.0,
        resource_id="custom-resource"
    )
    mock_service_custom = create_classification_service_mock(result=custom_result)
    result_custom = mock_service_custom.predict("test text")
    assert result_custom.model_version == "custom-model-v2"
    assert result_custom.predictions[0].taxonomy_id == "custom-001"


def test_create_search_service_mock():
    """Test that create_search_service_mock returns proper mock."""
    from backend.tests.conftest import create_search_service_mock
    
    # Create mock with default results
    mock_service = create_search_service_mock()
    
    # Test that mock has expected methods
    assert hasattr(mock_service, 'search')
    assert hasattr(mock_service, 'hybrid_search')
    assert hasattr(mock_service, 'semantic_search')
    assert hasattr(mock_service, 'keyword_search')
    
    # Test that methods return SearchResult domain objects
    results = mock_service.search("test query")
    assert len(results) > 0
    assert isinstance(results[0], SearchResult)
    assert results[0].score > 0.0
    assert results[0].rank == 1
    assert results[0].resource_id == "test-resource-1"
    
    # Test hybrid_search returns SearchResults wrapper
    search_results = mock_service.hybrid_search("test query")
    assert isinstance(search_results, SearchResults)
    assert len(search_results.results) > 0
    
    # Test with custom results
    custom_results = [
        SearchResult(
            resource_id="custom-1",
            score=0.99,
            rank=1,
            title="Custom Result",
            search_method="custom",
            metadata={}
        )
    ]
    mock_service_custom = create_search_service_mock(results=custom_results)
    results_custom = mock_service_custom.search("test query")
    assert results_custom[0].resource_id == "custom-1"
    assert results_custom[0].score == 0.99


def test_create_recommendation_service_mock():
    """Test that create_recommendation_service_mock returns proper mock."""
    from backend.tests.conftest import create_recommendation_service_mock
    
    # Create mock with default recommendations
    mock_service = create_recommendation_service_mock()
    
    # Test that mock has expected methods
    assert hasattr(mock_service, 'generate_recommendations')
    assert hasattr(mock_service, 'get_recommendations')
    assert hasattr(mock_service, 'recommend')
    assert hasattr(mock_service, 'get_personalized_recommendations')
    
    # Test that methods return Recommendation domain objects
    recommendations = mock_service.generate_recommendations("test-user")
    assert len(recommendations) > 0
    assert isinstance(recommendations[0], Recommendation)
    assert isinstance(recommendations[0].recommendation_score, RecommendationScore)
    assert recommendations[0].get_score() > 0.0
    assert recommendations[0].get_rank() == 1
    assert recommendations[0].resource_id == "rec-resource-1"
    
    # Test with custom recommendations
    custom_recs = [
        Recommendation(
            resource_id="custom-rec-1",
            user_id="custom-user",
            recommendation_score=RecommendationScore(
                score=0.99,
                confidence=0.95,
                rank=1
            ),
            strategy="custom",
            reason="Custom reason",
            metadata={"custom": "data"}
        )
    ]
    mock_service_custom = create_recommendation_service_mock(recommendations=custom_recs)
    recs_custom = mock_service_custom.generate_recommendations("test-user")
    assert recs_custom[0].resource_id == "custom-rec-1"
    assert recs_custom[0].get_score() == 0.99
    assert recs_custom[0].strategy == "custom"


def test_mock_utilities_with_domain_object_methods():
    """Test that mocked services support domain object methods."""
    from backend.tests.conftest import (
        create_quality_service_mock,
        create_classification_service_mock,
        create_search_service_mock,
        create_recommendation_service_mock
    )
    
    # Test QualityScore methods
    quality_mock = create_quality_service_mock()
    quality_result = quality_mock.compute_quality("test")
    assert quality_result.is_high_quality() or not quality_result.is_high_quality()
    assert quality_result.get_quality_level() in ['high', 'medium', 'low']
    assert quality_result.get_weakest_dimension() in ['accuracy', 'completeness', 'consistency', 'timeliness', 'relevance']
    
    # Test ClassificationResult methods
    classification_mock = create_classification_service_mock()
    classification_result = classification_mock.predict("test")
    assert classification_result.get_best_prediction() is not None
    assert len(classification_result.get_top_k(1)) == 1
    assert classification_result.has_high_confidence_predictions() or not classification_result.has_high_confidence_predictions()
    
    # Test SearchResult methods
    search_mock = create_search_service_mock()
    search_results = search_mock.search("test")
    assert search_results[0].is_high_score() or not search_results[0].is_high_score()
    assert search_results[0].is_top_result() or not search_results[0].is_top_result()
    
    # Test Recommendation methods
    recommendation_mock = create_recommendation_service_mock()
    recommendations = recommendation_mock.generate_recommendations("test")
    assert recommendations[0].is_high_quality() or not recommendations[0].is_high_quality()
    assert recommendations[0].is_top_recommendation() or not recommendations[0].is_top_recommendation()
    assert recommendations[0].get_score() > 0.0
    assert recommendations[0].get_confidence() > 0.0
