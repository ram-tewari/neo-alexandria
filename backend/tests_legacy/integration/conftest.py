"""
Shared fixtures for integration tests.

This module provides fixtures that create domain objects for integration testing,
ensuring tests work with the same domain objects used in production code.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock

from backend.app.domain.quality import QualityScore
from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
from backend.app.domain.search import SearchResult
from backend.app.domain.recommendation import Recommendation


@pytest.fixture
def db_session(test_db):
    """
    Create a database session for integration tests.
    
    This fixture provides a database session that can be used directly
    in integration tests. It ensures proper cleanup after each test.
    
    Args:
        test_db: Test database fixture from main conftest.py
        
    Returns:
        SQLAlchemy Session
        
    Yields:
        Database session for the test
    """
    db = test_db()
    yield db
    db.close()


@pytest.fixture
def sample_quality_score() -> QualityScore:
    """
    Create a sample QualityScore domain object for integration testing.
    
    Returns:
        QualityScore with typical values for testing
    """
    return QualityScore(
        accuracy=0.8,
        completeness=0.75,
        consistency=0.7,
        timeliness=0.85,
        relevance=0.8
    )


@pytest.fixture
def high_quality_score() -> QualityScore:
    """
    Create a high-quality QualityScore domain object.
    
    Returns:
        QualityScore with high values (>0.8)
    """
    return QualityScore(
        accuracy=0.9,
        completeness=0.85,
        consistency=0.88,
        timeliness=0.92,
        relevance=0.9
    )


@pytest.fixture
def low_quality_score() -> QualityScore:
    """
    Create a low-quality QualityScore domain object.
    
    Returns:
        QualityScore with low values (<0.6)
    """
    return QualityScore(
        accuracy=0.5,
        completeness=0.45,
        consistency=0.48,
        timeliness=0.52,
        relevance=0.5
    )


@pytest.fixture
def sample_classification_result() -> ClassificationResult:
    """
    Create a sample ClassificationResult domain object for integration testing.
    
    Returns:
        ClassificationResult with typical predictions
    """
    predictions = [
        ClassificationPrediction(
            taxonomy_id="006.31",
            confidence=0.85,
            rank=1
        ),
        ClassificationPrediction(
            taxonomy_id="006.3",
            confidence=0.72,
            rank=2
        ),
        ClassificationPrediction(
            taxonomy_id="004.6",
            confidence=0.65,
            rank=3
        )
    ]
    
    return ClassificationResult(
        predictions=predictions,
        model_version="test-model-v1.0",
        inference_time_ms=45.2,
        resource_id=str(uuid4())
    )


@pytest.fixture
def sample_search_result() -> SearchResult:
    """
    Create a sample SearchResult domain object for integration testing.
    
    Returns:
        SearchResult with typical search result
    """
    return SearchResult(
        resource_id=str(uuid4()),
        score=0.92,
        rank=1,
        title="Machine Learning Fundamentals",
        search_method="hybrid",
        metadata={
            "snippet": "Introduction to machine learning concepts...",
            "query": "machine learning"
        }
    )


@pytest.fixture
def sample_recommendation() -> Recommendation:
    """
    Create a sample Recommendation domain object for integration testing.
    
    Returns:
        Recommendation with typical values
    """
    from backend.app.domain.recommendation import RecommendationScore
    
    recommendation_score = RecommendationScore(
        score=0.88,
        confidence=0.82,
        rank=1
    )
    
    return Recommendation(
        resource_id=str(uuid4()),
        user_id=str(uuid4()),
        recommendation_score=recommendation_score,
        strategy="hybrid",
        reason="Recommended based on your interest in machine learning and recent reading history",
        metadata={
            "content_similarity": 0.85,
            "graph_score": 0.78,
            "quality_score": 0.9,
            "recency_boost": 0.05
        }
    )


@pytest.fixture
def mock_quality_service_with_domain_objects(sample_quality_score):
    """
    Create a mock QualityService that returns domain objects.
    
    Args:
        sample_quality_score: QualityScore fixture
        
    Returns:
        Mock QualityService configured to return QualityScore domain objects
    """
    mock_service = Mock()
    mock_service.compute_quality.return_value = sample_quality_score
    mock_service.assess_resource_quality.return_value = sample_quality_score
    mock_service.get_quality_score.return_value = sample_quality_score
    return mock_service


@pytest.fixture
def mock_classification_service_with_domain_objects(sample_classification_result):
    """
    Create a mock MLClassificationService that returns domain objects.
    
    Args:
        sample_classification_result: ClassificationResult fixture
        
    Returns:
        Mock MLClassificationService configured to return ClassificationResult domain objects
    """
    mock_service = Mock()
    mock_service.predict.return_value = sample_classification_result
    mock_service.classify_resource.return_value = sample_classification_result
    mock_service.classify_batch.return_value = [sample_classification_result]
    return mock_service


@pytest.fixture
def mock_search_service_with_domain_objects(sample_search_result):
    """
    Create a mock SearchService that returns domain objects.
    
    Args:
        sample_search_result: SearchResult fixture
        
    Returns:
        Mock SearchService configured to return SearchResult domain objects
    """
    mock_service = Mock()
    # SearchService typically returns a list of SearchResult objects
    mock_service.search.return_value = [sample_search_result]
    mock_service.hybrid_search.return_value = [sample_search_result]
    mock_service.semantic_search.return_value = [sample_search_result]
    return mock_service


@pytest.fixture
def mock_recommendation_service_with_domain_objects(sample_recommendation):
    """
    Create a mock RecommendationService that returns domain objects.
    
    Args:
        sample_recommendation: Recommendation fixture
        
    Returns:
        Mock RecommendationService configured to return Recommendation domain objects
    """
    mock_service = Mock()
    mock_service.get_recommendations.return_value = [sample_recommendation]
    mock_service.generate_recommendation.return_value = sample_recommendation
    return mock_service


@pytest.fixture
def integration_test_resources(test_db):
    """
    Create a set of resources with domain objects for integration testing.
    
    This fixture creates resources with proper quality scores, classifications,
    and other domain objects attached.
    
    Performance optimizations:
    - Minimal required fields only
    - Batch insert all resources at once
    - Single commit operation
    - Bulk delete for cleanup
    
    Args:
        test_db: Database session fixture
        
    Returns:
        Dict containing created resources and their IDs
    """
    from backend.app.database.models import Resource
    
    db = test_db()
    
    # Create resources with varying quality scores
    quality_scores = [
        QualityScore(0.9, 0.85, 0.88, 0.92, 0.9),  # High quality
        QualityScore(0.75, 0.7, 0.72, 0.78, 0.75),  # Medium quality
        QualityScore(0.5, 0.45, 0.48, 0.52, 0.5),   # Low quality
    ]
    
    resources = []
    for i, quality_score in enumerate(quality_scores):
        resource = Resource(
            title=f"Integration Test Resource {i+1}",
            description=f"Test resource for integration testing with quality level {i+1}",
            source=f"https://example.com/resource{i+1}",
            type="article",
            language="en",
            quality_score=quality_score.overall_score(),
            quality_overall=quality_score.overall_score(),
            quality_accuracy=quality_score.accuracy,
            quality_completeness=quality_score.completeness,
            quality_consistency=quality_score.consistency,
            quality_timeliness=quality_score.timeliness,
            quality_relevance=quality_score.relevance,
            quality_last_computed=datetime.now(timezone.utc),
            quality_computation_version="v2.0",
            ingestion_status="completed"
        )
        resources.append(resource)
    
    # Batch insert all resources at once (much faster)
    db.add_all(resources)
    db.commit()
    
    # Batch refresh to get IDs
    for resource in resources:
        db.refresh(resource)
    
    yield {
        "resources": resources,
        "resource_ids": [str(r.id) for r in resources],
        "high_quality": resources[0],
        "medium_quality": resources[1],
        "low_quality": resources[2]
    }
    
    # Cleanup with bulk delete (faster than individual deletes)
    try:
        db.query(Resource).filter(Resource.id.in_([r.id for r in resources])).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
