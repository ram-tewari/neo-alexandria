"""
Fixtures for workflow integration tests.

Provides fixtures for testing end-to-end workflows with domain objects.
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
def workflow_test_resource(db_session):
    """
    Create a test resource for workflow integration testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        Resource for workflow testing
    """
    from backend.app.database.models import Resource
    
    quality_score = QualityScore(
        accuracy=0.8,
        completeness=0.75,
        consistency=0.7,
        timeliness=0.85,
        relevance=0.8
    )
    
    resource = Resource(
        id=uuid4(),
        title="Workflow Test Resource",
        description="A resource for testing end-to-end workflows",
        subject=["AI", "Machine Learning"],
        source="https://example.com/workflow-test",
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
    
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    
    yield resource
    
    # Cleanup
    db_session.delete(resource)
    db_session.commit()


@pytest.fixture
def mock_workflow_services():
    """
    Create mock services for workflow testing that return domain objects.
    
    Returns:
        Dict of mock services
    """
    # Quality Service Mock
    quality_score = QualityScore(
        accuracy=0.85,
        completeness=0.8,
        consistency=0.8,
        timeliness=0.75,
        relevance=0.85
    )
    mock_quality_service = Mock()
    mock_quality_service.compute_quality.return_value = quality_score
    mock_quality_service.assess_resource_quality.return_value = quality_score
    mock_quality_service.detect_quality_outliers.return_value = 5
    mock_quality_service.monitor_quality_degradation.return_value = []
    
    # Classification Service Mock
    classification_result = ClassificationResult(
        predictions=[
            ClassificationPrediction("006.31", 0.85, 1),
            ClassificationPrediction("006.3", 0.72, 2)
        ],
        model_version="test-model-v1.0",
        inference_time_ms=45.2,
        resource_id=str(uuid4())
    )
    mock_classification_service = Mock()
    mock_classification_service.predict.return_value = classification_result
    mock_classification_service.classify_resource.return_value = classification_result
    
    # Search Service Mock
    search_result = SearchResult(
        resource_id=str(uuid4()),
        title="Test Result",
        score=0.92,
        rank=1,
        search_method="hybrid",
        metadata={"query": "test query"}
    )
    mock_search_service = Mock()
    mock_search_service.search.return_value = [search_result]
    mock_search_service.hybrid_search.return_value = [search_result]
    
    # Recommendation Service Mock
    from backend.app.domain.recommendation import RecommendationScore
    
    recommendation_score = RecommendationScore(
        score=0.88,
        confidence=0.82,
        rank=1
    )
    
    recommendation = Recommendation(
        resource_id=str(uuid4()),
        user_id=str(uuid4()),
        recommendation_score=recommendation_score,
        strategy="hybrid",
        reason="Test recommendation",
        metadata={"quality_score": 0.9}
    )
    mock_recommendation_service = Mock()
    mock_recommendation_service.get_recommendations.return_value = [recommendation]
    mock_recommendation_service.generate_recommendation.return_value = recommendation
    
    return {
        "quality_service": mock_quality_service,
        "classification_service": mock_classification_service,
        "search_service": mock_search_service,
        "recommendation_service": mock_recommendation_service
    }


@pytest.fixture
def workflow_test_resources_batch(db_session):
    """
    Create multiple resources for batch workflow testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        List of resources
    """
    from backend.app.database.models import Resource
    
    resources = []
    
    for i in range(5):
        quality_score = QualityScore(
            accuracy=0.7 + (i * 0.05),
            completeness=0.65 + (i * 0.05),
            consistency=0.68 + (i * 0.05),
            timeliness=0.75 + (i * 0.05),
            relevance=0.72 + (i * 0.05)
        )
        
        resource = Resource(
            id=uuid4(),
            title=f"Batch Workflow Resource {i+1}",
            description=f"Resource {i+1} for batch workflow testing",
            source=f"https://example.com/batch-{i+1}",
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
            ingestion_status="completed"
        )
        db_session.add(resource)
        resources.append(resource)
    
    db_session.commit()
    
    for resource in resources:
        db_session.refresh(resource)
    
    yield resources
    
    # Cleanup
    for resource in resources:
        db_session.delete(resource)
    db_session.commit()
