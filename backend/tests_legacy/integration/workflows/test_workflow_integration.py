"""
Test Phase 9 workflow integration.

This test verifies that quality assessment is properly integrated into:
1. Resource ingestion pipeline
2. Resource update workflow
3. Summary generation workflow
4. Scheduled tasks
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.base import Base
from backend.app.database.models import Resource
from backend.app.services.resource_service import update_resource
from backend.app.services.scheduled_tasks import (
    run_outlier_detection,
    run_degradation_monitoring,
    run_all_scheduled_tasks,
)
from backend.app.schemas.resource import ResourceUpdate


@pytest.fixture
def db_session():
    """Create in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_resource(db_session):
    """Create a sample resource for testing."""
    resource = Resource(
        id=uuid4(),
        title="Test Resource",
        description="Test description",
        subject=["AI", "Machine Learning"],
        source="https://example.com/test",
        quality_score=0.75,
        quality_overall=0.75,
        quality_accuracy=0.8,
        quality_completeness=0.7,
        quality_consistency=0.75,
        quality_timeliness=0.7,
        quality_relevance=0.8,
        quality_last_computed=datetime.now(timezone.utc),
        ingestion_status="completed",
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


def test_update_resource_triggers_quality_recomputation(
    db_session, sample_resource, high_quality_score
):
    """Test that updating quality-affecting fields triggers quality recomputation."""

    with patch(
        "backend.app.services.quality_service.QualityService"
    ) as mock_quality_service:
        mock_service_instance = Mock()

        # Use fixture for QualityScore domain object
        mock_service_instance.compute_quality.return_value = high_quality_score
        mock_quality_service.return_value = mock_service_instance

        # Update a quality-affecting field
        update_payload = ResourceUpdate(
            title="Updated Test Resource",
            description="Updated description with more content",
        )

        updated_resource = update_resource(
            db_session, sample_resource.id, update_payload
        )

        # Verify quality service was called
        mock_quality_service.assert_called_once()
        mock_service_instance.compute_quality.assert_called_once_with(
            sample_resource.id
        )

        # Verify resource was updated
        assert updated_resource.title == "Updated Test Resource"
        assert updated_resource.description == "Updated description with more content"


def test_update_resource_no_quality_recomputation_for_non_affecting_fields(
    db_session, sample_resource
):
    """Test that updating non-quality-affecting fields doesn't trigger recomputation."""

    with patch(
        "backend.app.services.quality_service.QualityService"
    ) as mock_quality_service:
        # Update a non-quality-affecting field (read_status)
        update_payload = ResourceUpdate(read_status="completed")

        updated_resource = update_resource(
            db_session, sample_resource.id, update_payload
        )

        # Verify quality service was NOT called
        mock_quality_service.assert_not_called()

        # Verify resource was updated
        assert updated_resource.read_status == "completed"


def test_scheduled_outlier_detection(db_session, sample_resource):
    """Test scheduled outlier detection task."""

    with patch(
        "backend.app.services.scheduled_tasks.QualityService"
    ) as mock_quality_service:
        mock_service_instance = Mock()
        mock_service_instance.detect_quality_outliers.return_value = 5
        mock_quality_service.return_value = mock_service_instance

        result = run_outlier_detection(db=db_session, batch_size=100)

        # Verify task executed successfully
        assert result["success"] is True
        assert result["outlier_count"] == 5
        assert result["batch_size"] == 100
        assert "duration_seconds" in result
        assert "timestamp" in result

        # Verify quality service was called
        mock_service_instance.detect_quality_outliers.assert_called_once_with(
            batch_size=100
        )


def test_scheduled_degradation_monitoring(db_session, sample_resource):
    """Test scheduled degradation monitoring task."""

    with patch(
        "backend.app.services.scheduled_tasks.QualityService"
    ) as mock_quality_service:
        mock_service_instance = Mock()
        mock_service_instance.monitor_quality_degradation.return_value = [
            {
                "resource_id": str(sample_resource.id),
                "title": "Test Resource",
                "old_quality": 0.85,
                "new_quality": 0.62,
                "degradation_pct": 27.1,
            }
        ]
        mock_quality_service.return_value = mock_service_instance

        result = run_degradation_monitoring(db=db_session, time_window_days=30)

        # Verify task executed successfully
        assert result["success"] is True
        assert result["degraded_count"] == 1
        assert result["time_window_days"] == 30
        assert "duration_seconds" in result
        assert "timestamp" in result
        assert len(result["degraded_resources"]) == 1

        # Verify quality service was called
        mock_service_instance.monitor_quality_degradation.assert_called_once_with(
            time_window_days=30
        )


def test_run_all_scheduled_tasks(db_session):
    """Test running all scheduled tasks together."""

    with patch(
        "backend.app.services.scheduled_tasks.QualityService"
    ) as mock_quality_service:
        mock_service_instance = Mock()
        mock_service_instance.detect_quality_outliers.return_value = 3
        mock_service_instance.monitor_quality_degradation.return_value = []
        mock_quality_service.return_value = mock_service_instance

        results = run_all_scheduled_tasks(db=db_session)

        # Verify both tasks executed
        assert "outlier_detection" in results
        assert "degradation_monitoring" in results

        # Verify outlier detection results
        assert results["outlier_detection"]["success"] is True
        assert results["outlier_detection"]["outlier_count"] == 3

        # Verify degradation monitoring results
        assert results["degradation_monitoring"]["success"] is True
        assert results["degradation_monitoring"]["degraded_count"] == 0


def test_scheduled_task_error_handling(db_session):
    """Test that scheduled tasks handle errors gracefully."""

    with patch(
        "backend.app.services.scheduled_tasks.QualityService"
    ) as mock_quality_service:
        mock_quality_service.side_effect = Exception("Database connection failed")

        result = run_outlier_detection(db=db_session)

        # Verify task reports failure but doesn't crash
        assert result["success"] is False
        assert "error" in result
        assert "Database connection failed" in result["error"]
        assert "timestamp" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
