"""
Test that integration test fixtures properly create domain objects.

This test verifies that the new integration test fixtures in conftest.py
correctly create and return domain objects for use in integration tests.
"""

import pytest
from backend.app.domain.quality import QualityScore
from backend.app.domain.classification import (
    ClassificationResult,
    ClassificationPrediction,
)
from backend.app.domain.search import SearchResult
from backend.app.domain.recommendation import Recommendation


def test_sample_quality_score_fixture(sample_quality_score):
    """Test that sample_quality_score fixture creates a QualityScore domain object."""
    assert isinstance(sample_quality_score, QualityScore)
    assert sample_quality_score.accuracy == 0.8
    assert sample_quality_score.completeness == 0.75
    assert sample_quality_score.overall_score() > 0.0


def test_high_quality_score_fixture(high_quality_score):
    """Test that high_quality_score fixture creates a high-quality QualityScore."""
    assert isinstance(high_quality_score, QualityScore)
    assert high_quality_score.overall_score() > 0.8
    assert high_quality_score.get_quality_level() in ["high", "excellent"]


def test_low_quality_score_fixture(low_quality_score):
    """Test that low_quality_score fixture creates a low-quality QualityScore."""
    assert isinstance(low_quality_score, QualityScore)
    assert low_quality_score.overall_score() < 0.6
    assert low_quality_score.get_quality_level() in ["low", "poor"]


def test_sample_classification_result_fixture(sample_classification_result):
    """Test that sample_classification_result fixture creates a ClassificationResult."""
    assert isinstance(sample_classification_result, ClassificationResult)
    assert len(sample_classification_result.predictions) > 0
    assert all(
        isinstance(p, ClassificationPrediction)
        for p in sample_classification_result.predictions
    )
    assert sample_classification_result.model_version == "test-model-v1.0"


def test_sample_search_result_fixture(sample_search_result):
    """Test that sample_search_result fixture creates a SearchResult."""
    assert isinstance(sample_search_result, SearchResult)
    assert sample_search_result.score > 0.0
    assert sample_search_result.rank > 0
    assert sample_search_result.title == "Machine Learning Fundamentals"


def test_sample_recommendation_fixture(sample_recommendation):
    """Test that sample_recommendation fixture creates a Recommendation."""
    assert isinstance(sample_recommendation, Recommendation)
    assert sample_recommendation.recommendation_score.score > 0.0
    assert sample_recommendation.recommendation_score.confidence > 0.0
    assert sample_recommendation.strategy == "hybrid"
    assert sample_recommendation.reason is not None


def test_mock_quality_service_fixture(mock_quality_service_with_domain_objects):
    """Test that mock quality service returns domain objects."""
    mock_service = mock_quality_service_with_domain_objects

    result = mock_service.compute_quality("test-resource-id")
    assert isinstance(result, QualityScore)

    result = mock_service.assess_resource_quality("test-resource-id")
    assert isinstance(result, QualityScore)


def test_mock_classification_service_fixture(
    mock_classification_service_with_domain_objects,
):
    """Test that mock classification service returns domain objects."""
    mock_service = mock_classification_service_with_domain_objects

    result = mock_service.predict("test-resource-id")
    assert isinstance(result, ClassificationResult)

    result = mock_service.classify_resource("test-resource-id")
    assert isinstance(result, ClassificationResult)


def test_mock_search_service_fixture(mock_search_service_with_domain_objects):
    """Test that mock search service returns domain objects."""
    mock_service = mock_search_service_with_domain_objects

    results = mock_service.search("test query")
    assert isinstance(results, list)
    assert all(isinstance(r, SearchResult) for r in results)

    results = mock_service.hybrid_search("test query")
    assert isinstance(results, list)
    assert all(isinstance(r, SearchResult) for r in results)


def test_mock_recommendation_service_fixture(
    mock_recommendation_service_with_domain_objects,
):
    """Test that mock recommendation service returns domain objects."""
    mock_service = mock_recommendation_service_with_domain_objects

    results = mock_service.get_recommendations("test-user-id")
    assert isinstance(results, list)
    assert all(isinstance(r, Recommendation) for r in results)

    result = mock_service.generate_recommendation("test-user-id", "test-resource-id")
    assert isinstance(result, Recommendation)


def test_integration_test_resources_fixture(integration_test_resources):
    """Test that integration_test_resources fixture creates resources with domain objects."""
    data = integration_test_resources

    assert "resources" in data
    assert "resource_ids" in data
    assert "high_quality" in data
    assert "medium_quality" in data
    assert "low_quality" in data

    assert len(data["resources"]) == 3
    assert len(data["resource_ids"]) == 3

    # Verify quality scores are properly set
    high_quality = data["high_quality"]
    assert high_quality.quality_overall > 0.8

    medium_quality = data["medium_quality"]
    assert 0.6 < medium_quality.quality_overall < 0.8

    low_quality = data["low_quality"]
    assert low_quality.quality_overall < 0.6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
