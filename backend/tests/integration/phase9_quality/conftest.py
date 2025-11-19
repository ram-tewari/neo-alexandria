"""
Fixtures for Phase 9 Quality integration tests.

Provides fixtures specific to quality assessment integration testing.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock

from backend.app.domain.quality import QualityScore
from backend.app.services.quality_service import QualityService


@pytest.fixture
def quality_service(db_session):
    """
    Create a QualityService instance for integration testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        QualityService instance
    """
    return QualityService(db=db_session)


@pytest.fixture
def quality_test_resource(db_session):
    """
    Create a test resource with quality scores for integration testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        Resource with quality scores
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
        title="Quality Test Resource",
        description="A resource for testing quality assessment",
        source="https://example.com/quality-test",
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
def quality_outlier_resource(db_session):
    """
    Create an outlier resource for quality testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        Resource with outlier quality scores
    """
    from backend.app.database.models import Resource
    
    # Create outlier with very low quality
    quality_score = QualityScore(
        accuracy=0.2,
        completeness=0.15,
        consistency=0.18,
        timeliness=0.22,
        relevance=0.2
    )
    
    resource = Resource(
        id=uuid4(),
        title="Outlier Resource",
        description="A resource with outlier quality scores",
        source="https://example.com/outlier",
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
def mock_quality_service_returning_domain_objects():
    """
    Create a mock QualityService that returns QualityScore domain objects.
    
    Returns:
        Mock QualityService
    """
    mock_service = Mock(spec=QualityService)
    
    # Configure mock to return QualityScore domain objects
    quality_score = QualityScore(
        accuracy=0.8,
        completeness=0.75,
        consistency=0.7,
        timeliness=0.85,
        relevance=0.8
    )
    
    mock_service.compute_quality.return_value = quality_score
    mock_service.assess_resource_quality.return_value = quality_score
    mock_service.get_quality_score.return_value = quality_score
    mock_service.detect_quality_outliers.return_value = 5
    mock_service.monitor_quality_degradation.return_value = []
    
    return mock_service
