"""
Fixtures for Phase 8 Classification integration tests.

Provides fixtures specific to classification integration testing.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock

from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
from backend.app.services.ml_classification_service import MLClassificationService


@pytest.fixture
def classification_test_resource(db_session):
    """
    Create a test resource for classification integration testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        Resource ready for classification
    """
    from backend.app.database.models import Resource
    
    resource = Resource(
        id=uuid4(),
        title="Machine Learning and Artificial Intelligence",
        description="A comprehensive guide to ML and AI techniques",
        source="https://example.com/ml-ai",
        type="article",
        language="en",
        embedding=[0.1] * 768,  # Simple embedding for testing
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
def sample_classification_predictions() -> list:
    """
    Create sample classification predictions for testing.
    
    Returns:
        List of ClassificationPrediction objects
    """
    return [
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


@pytest.fixture
def classification_result_with_predictions(sample_classification_predictions) -> ClassificationResult:
    """
    Create a ClassificationResult with predictions for testing.
    
    Args:
        sample_classification_predictions: Predictions fixture
        
    Returns:
        ClassificationResult domain object
    """
    return ClassificationResult(
        predictions=sample_classification_predictions,
        model_version="test-model-v1.0",
        inference_time_ms=45.2,
        resource_id=str(uuid4())
    )


@pytest.fixture
def mock_ml_classification_service_with_domain_objects(classification_result_with_predictions):
    """
    Create a mock MLClassificationService that returns domain objects.
    
    Args:
        classification_result_with_predictions: ClassificationResult fixture
        
    Returns:
        Mock MLClassificationService
    """
    mock_service = Mock(spec=MLClassificationService)
    
    # Configure mock to return ClassificationResult domain objects
    mock_service.predict.return_value = classification_result_with_predictions
    mock_service.classify_resource.return_value = classification_result_with_predictions
    mock_service.classify_batch.return_value = [classification_result_with_predictions]
    mock_service.get_model_version.return_value = "test-model-v1.0"
    
    return mock_service


@pytest.fixture
def classification_batch_resources(db_session):
    """
    Create multiple resources for batch classification testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        List of resources
    """
    from backend.app.database.models import Resource
    
    resources = []
    titles = [
        "Introduction to Machine Learning",
        "Deep Learning with Neural Networks",
        "Natural Language Processing Basics"
    ]
    
    for i, title in enumerate(titles):
        resource = Resource(
            id=uuid4(),
            title=title,
            description=f"Test resource {i+1} for batch classification",
            source=f"https://example.com/resource{i+1}",
            type="article",
            language="en",
            embedding=[0.1 * (i+1)] * 768,
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
