"""
Test fixture factories for domain objects.

This test file verifies that all domain object fixture factories
work correctly and produce valid domain objects.
"""

import pytest
from backend.app.domain.quality import QualityScore
from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
from backend.app.domain.search import SearchResult
from backend.app.domain.recommendation import Recommendation, RecommendationScore


def test_quality_score_factory_default(quality_score_factory):
    """Test quality_score_factory with default values."""
    score = quality_score_factory()
    
    assert isinstance(score, QualityScore)
    assert score.accuracy == 0.8
    assert score.completeness == 0.7
    assert score.consistency == 0.75
    assert score.timeliness == 0.9
    assert score.relevance == 0.85
    assert 0.0 <= score.overall_score() <= 1.0


def test_quality_score_factory_custom(quality_score_factory):
    """Test quality_score_factory with custom values."""
    score = quality_score_factory(
        accuracy=0.95,
        completeness=0.85,
        consistency=0.9,
        timeliness=0.8,
        relevance=0.92
    )
    
    assert isinstance(score, QualityScore)
    assert score.accuracy == 0.95
    assert score.completeness == 0.85
    assert score.consistency == 0.9
    assert score.timeliness == 0.8
    assert score.relevance == 0.92
    assert score.is_high_quality()


def test_classification_result_factory_default(classification_result_factory):
    """Test classification_result_factory with default values."""
    result = classification_result_factory()
    
    assert isinstance(result, ClassificationResult)
    assert len(result.predictions) == 1
    assert isinstance(result.predictions[0], ClassificationPrediction)
    assert result.predictions[0].taxonomy_id == "004"
    assert result.predictions[0].confidence == 0.9
    assert result.predictions[0].rank == 1
    assert result.model_version == "test-model-v1"
    assert result.inference_time_ms == 50.0


def test_classification_result_factory_custom(classification_result_factory):
    """Test classification_result_factory with custom predictions."""
    predictions = [
        ClassificationPrediction(taxonomy_id="cat1", confidence=0.95, rank=1),
        ClassificationPrediction(taxonomy_id="cat2", confidence=0.75, rank=2),
        ClassificationPrediction(taxonomy_id="cat3", confidence=0.6, rank=3)
    ]
    
    result = classification_result_factory(
        predictions=predictions,
        model_version="custom-model-v2",
        inference_time_ms=75.5,
        resource_id="res-123"
    )
    
    assert isinstance(result, ClassificationResult)
    assert len(result.predictions) == 3
    assert result.model_version == "custom-model-v2"
    assert result.inference_time_ms == 75.5
    assert result.resource_id == "res-123"
    assert result.get_best_prediction().taxonomy_id == "cat1"


def test_search_result_factory_default(search_result_factory):
    """Test search_result_factory with default values."""
    result = search_result_factory()
    
    assert isinstance(result, SearchResult)
    assert result.resource_id == "test-resource-id"
    assert result.score == 0.85
    assert result.rank == 1
    assert result.title == "Test Resource Title"
    assert result.search_method == "hybrid"
    assert result.metadata == {}


def test_search_result_factory_custom(search_result_factory):
    """Test search_result_factory with custom values."""
    metadata = {"source": "fts5", "match_type": "exact"}
    
    result = search_result_factory(
        resource_id="custom-res-456",
        score=0.95,
        rank=2,
        title="Custom Title",
        search_method="fts5",
        metadata=metadata
    )
    
    assert isinstance(result, SearchResult)
    assert result.resource_id == "custom-res-456"
    assert result.score == 0.95
    assert result.rank == 2
    assert result.title == "Custom Title"
    assert result.search_method == "fts5"
    assert result.metadata == metadata
    assert result.is_high_score()


def test_recommendation_factory_default(recommendation_factory):
    """Test recommendation_factory with default values."""
    rec = recommendation_factory()
    
    assert isinstance(rec, Recommendation)
    assert rec.resource_id == "test-resource-id"
    assert rec.user_id == "test-user-id"
    assert rec.get_score() == 0.85
    assert rec.get_confidence() == 0.9
    assert rec.get_rank() == 1
    assert rec.strategy == "content-based"
    assert rec.reason is None
    assert rec.metadata == {}


def test_recommendation_factory_custom(recommendation_factory):
    """Test recommendation_factory with custom values."""
    metadata = {"similarity": 0.92, "category_match": True}
    
    rec = recommendation_factory(
        resource_id="rec-res-789",
        user_id="user-123",
        score=0.92,
        confidence=0.88,
        rank=3,
        strategy="collaborative",
        reason="Based on similar users' preferences",
        metadata=metadata
    )
    
    assert isinstance(rec, Recommendation)
    assert rec.resource_id == "rec-res-789"
    assert rec.user_id == "user-123"
    assert rec.get_score() == 0.92
    assert rec.get_confidence() == 0.88
    assert rec.get_rank() == 3
    assert rec.strategy == "collaborative"
    assert rec.reason == "Based on similar users' preferences"
    assert rec.metadata == metadata
    assert rec.is_high_quality()


def test_all_factories_produce_valid_domain_objects(
    quality_score_factory,
    classification_result_factory,
    search_result_factory,
    recommendation_factory
):
    """Test that all factories produce valid domain objects that pass validation."""
    # Create instances with defaults
    quality_score = quality_score_factory()
    classification_result = classification_result_factory()
    search_result = search_result_factory()
    recommendation = recommendation_factory()
    
    # All should validate without errors
    quality_score.validate()
    classification_result.validate()
    search_result.validate()
    recommendation.validate()
    
    # All should be able to convert to dict
    assert isinstance(quality_score.to_dict(), dict)
    assert isinstance(classification_result.to_dict(), dict)
    assert isinstance(search_result.to_dict(), dict)
    assert isinstance(recommendation.to_dict(), dict)
