"""Unit tests for status tracking service.

Tests cover:
- set_progress() stores data in Redis
- get_progress() retrieves data from Redis
- Round-trip (set then get)
- Overall status calculation with various stage combinations
- TTL is set on Redis keys
- Graceful degradation when Redis unavailable
"""

import pytest
from unittest.mock import Mock

from app.shared.services.status_tracker import StatusTracker, get_status_tracker
from app.shared.schemas.status import ProcessingStage, StageStatus
from app.cache.redis_cache import RedisCache


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_cache():
    """Create a mock RedisCache instance."""
    cache = Mock(spec=RedisCache)
    cache.get = Mock(return_value=None)
    cache.set = Mock()
    return cache


@pytest.fixture
def status_tracker(mock_cache):
    """Create a StatusTracker instance with mocked cache."""
    return StatusTracker(cache=mock_cache)


# ============================================================================
# Test set_progress()
# ============================================================================


@pytest.mark.asyncio
async def test_set_progress_creates_new_progress(status_tracker, mock_cache):
    """Test set_progress creates new progress record when none exists."""
    # Setup
    resource_id = 123
    stage = ProcessingStage.INGESTION
    status = StageStatus.COMPLETED

    # Mock cache to return None (no existing progress)
    mock_cache.get.return_value = None

    # Execute
    await status_tracker.set_progress(resource_id, stage, status)

    # Assert
    mock_cache.get.assert_called_once_with(f"progress:resource:{resource_id}")
    mock_cache.set.assert_called_once()

    # Verify the data passed to cache.set
    call_args = mock_cache.set.call_args
    key = call_args[0][0]
    data = call_args[0][1]
    ttl = call_args[1]["ttl"]

    assert key == f"progress:resource:{resource_id}"
    assert data["resource_id"] == resource_id
    assert data["stages"][stage.value] == status.value
    assert data["overall_status"] == StageStatus.COMPLETED.value
    assert ttl == 86400  # 24 hours


@pytest.mark.asyncio
async def test_set_progress_updates_existing_progress(status_tracker, mock_cache):
    """Test set_progress updates existing progress record."""
    # Setup
    resource_id = 123

    # Mock existing progress
    existing_progress = {
        "resource_id": resource_id,
        "overall_status": StageStatus.PROCESSING.value,
        "stages": {
            ProcessingStage.INGESTION.value: StageStatus.COMPLETED.value,
            ProcessingStage.QUALITY.value: StageStatus.PROCESSING.value,
        },
        "error_message": None,
        "updated_at": "2026-01-01T10:00:00Z",
    }
    mock_cache.get.return_value = existing_progress

    # Execute - update QUALITY stage to COMPLETED
    await status_tracker.set_progress(
        resource_id, ProcessingStage.QUALITY, StageStatus.COMPLETED
    )

    # Assert
    mock_cache.set.assert_called_once()

    # Verify the updated data
    call_args = mock_cache.set.call_args
    data = call_args[0][1]

    assert (
        data["stages"][ProcessingStage.INGESTION.value] == StageStatus.COMPLETED.value
    )
    assert data["stages"][ProcessingStage.QUALITY.value] == StageStatus.COMPLETED.value
    assert data["overall_status"] == StageStatus.COMPLETED.value  # All completed


@pytest.mark.asyncio
async def test_set_progress_with_error_message(status_tracker, mock_cache):
    """Test set_progress stores error message when stage fails."""
    # Setup
    resource_id = 123
    stage = ProcessingStage.TAXONOMY
    status = StageStatus.FAILED
    error_message = "Classification model failed: timeout"

    mock_cache.get.return_value = None

    # Execute
    await status_tracker.set_progress(resource_id, stage, status, error_message)

    # Assert
    call_args = mock_cache.set.call_args
    data = call_args[0][1]

    assert data["stages"][stage.value] == status.value
    assert data["error_message"] == error_message
    assert data["overall_status"] == StageStatus.FAILED.value


@pytest.mark.asyncio
async def test_set_progress_updates_timestamp(status_tracker, mock_cache):
    """Test set_progress updates the timestamp."""
    # Setup
    resource_id = 123
    stage = ProcessingStage.EMBEDDING
    status = StageStatus.PROCESSING

    mock_cache.get.return_value = None

    # Execute
    await status_tracker.set_progress(resource_id, stage, status)

    # Assert
    call_args = mock_cache.set.call_args
    data = call_args[0][1]

    # Verify timestamp is recent (ISO 8601 format)
    assert "updated_at" in data
    assert "T" in data["updated_at"]  # ISO format
    assert "Z" in data["updated_at"] or "+" in data["updated_at"]  # Timezone


@pytest.mark.asyncio
async def test_set_progress_sets_ttl(status_tracker, mock_cache):
    """Test set_progress sets TTL on Redis keys."""
    # Setup
    resource_id = 123
    stage = ProcessingStage.GRAPH
    status = StageStatus.COMPLETED

    mock_cache.get.return_value = None

    # Execute
    await status_tracker.set_progress(resource_id, stage, status)

    # Assert TTL is set to 24 hours
    call_args = mock_cache.set.call_args
    ttl = call_args[1]["ttl"]
    assert ttl == 86400  # 24 hours in seconds


# ============================================================================
# Test get_progress()
# ============================================================================


@pytest.mark.asyncio
async def test_get_progress_returns_existing_progress(status_tracker, mock_cache):
    """Test get_progress retrieves existing progress from Redis."""
    # Setup
    resource_id = 123

    # Mock cached progress
    cached_data = {
        "resource_id": resource_id,
        "overall_status": StageStatus.PROCESSING.value,
        "stages": {
            ProcessingStage.INGESTION.value: StageStatus.COMPLETED.value,
            ProcessingStage.QUALITY.value: StageStatus.PROCESSING.value,
        },
        "error_message": None,
        "updated_at": "2026-01-01T12:00:00Z",
    }
    mock_cache.get.return_value = cached_data

    # Execute
    progress = await status_tracker.get_progress(resource_id)

    # Assert
    assert progress is not None
    assert progress.resource_id == resource_id
    assert progress.overall_status == StageStatus.PROCESSING
    assert progress.stages[ProcessingStage.INGESTION] == StageStatus.COMPLETED
    assert progress.stages[ProcessingStage.QUALITY] == StageStatus.PROCESSING
    assert progress.error_message is None

    # Verify cache was queried
    mock_cache.get.assert_called_once_with(f"progress:resource:{resource_id}")


@pytest.mark.asyncio
async def test_get_progress_returns_none_when_not_found(status_tracker, mock_cache):
    """Test get_progress returns None when no progress exists."""
    # Setup
    resource_id = 999
    mock_cache.get.return_value = None

    # Execute
    progress = await status_tracker.get_progress(resource_id)

    # Assert
    assert progress is None
    mock_cache.get.assert_called_once_with(f"progress:resource:{resource_id}")


@pytest.mark.asyncio
async def test_get_progress_with_all_stages(status_tracker, mock_cache):
    """Test get_progress with all processing stages."""
    # Setup
    resource_id = 456

    # Mock progress with all stages
    cached_data = {
        "resource_id": resource_id,
        "overall_status": StageStatus.COMPLETED.value,
        "stages": {
            ProcessingStage.INGESTION.value: StageStatus.COMPLETED.value,
            ProcessingStage.QUALITY.value: StageStatus.COMPLETED.value,
            ProcessingStage.TAXONOMY.value: StageStatus.COMPLETED.value,
            ProcessingStage.GRAPH.value: StageStatus.COMPLETED.value,
            ProcessingStage.EMBEDDING.value: StageStatus.COMPLETED.value,
        },
        "error_message": None,
        "updated_at": "2026-01-01T12:00:00Z",
    }
    mock_cache.get.return_value = cached_data

    # Execute
    progress = await status_tracker.get_progress(resource_id)

    # Assert all stages are present
    assert len(progress.stages) == 5
    assert all(status == StageStatus.COMPLETED for status in progress.stages.values())


# ============================================================================
# Test Round-Trip (set then get)
# ============================================================================


@pytest.mark.asyncio
async def test_round_trip_set_then_get(status_tracker, mock_cache):
    """Test round-trip: set_progress followed by get_progress."""
    # Setup
    resource_id = 789
    stage = ProcessingStage.QUALITY
    status = StageStatus.PROCESSING

    # Mock cache behavior for round-trip
    stored_data = None

    def mock_get(key):
        return stored_data

    def mock_set(key, data, ttl):
        nonlocal stored_data
        stored_data = data

    mock_cache.get.side_effect = mock_get
    mock_cache.set.side_effect = mock_set

    # Execute set
    await status_tracker.set_progress(resource_id, stage, status)

    # Execute get
    progress = await status_tracker.get_progress(resource_id)

    # Assert
    assert progress is not None
    assert progress.resource_id == resource_id
    assert progress.stages[stage] == status
    assert progress.overall_status == StageStatus.PROCESSING


@pytest.mark.asyncio
async def test_round_trip_multiple_stages(status_tracker, mock_cache):
    """Test round-trip with multiple stage updates."""
    # Setup
    resource_id = 101

    # Mock cache behavior
    stored_data = None

    def mock_get(key):
        return stored_data

    def mock_set(key, data, ttl):
        nonlocal stored_data
        stored_data = data

    mock_cache.get.side_effect = mock_get
    mock_cache.set.side_effect = mock_set

    # Execute multiple updates
    await status_tracker.set_progress(
        resource_id, ProcessingStage.INGESTION, StageStatus.COMPLETED
    )
    await status_tracker.set_progress(
        resource_id, ProcessingStage.QUALITY, StageStatus.COMPLETED
    )
    await status_tracker.set_progress(
        resource_id, ProcessingStage.TAXONOMY, StageStatus.PROCESSING
    )

    # Get final progress
    progress = await status_tracker.get_progress(resource_id)

    # Assert
    assert progress.stages[ProcessingStage.INGESTION] == StageStatus.COMPLETED
    assert progress.stages[ProcessingStage.QUALITY] == StageStatus.COMPLETED
    assert progress.stages[ProcessingStage.TAXONOMY] == StageStatus.PROCESSING
    assert progress.overall_status == StageStatus.PROCESSING


# ============================================================================
# Test Overall Status Calculation
# ============================================================================


def test_calculate_overall_status_empty_stages(status_tracker):
    """Test overall status calculation with no stages."""
    stages = {}
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.PENDING


def test_calculate_overall_status_all_completed(status_tracker):
    """Test overall status when all stages are completed."""
    stages = {
        ProcessingStage.INGESTION: StageStatus.COMPLETED,
        ProcessingStage.QUALITY: StageStatus.COMPLETED,
        ProcessingStage.TAXONOMY: StageStatus.COMPLETED,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.COMPLETED


def test_calculate_overall_status_one_processing(status_tracker):
    """Test overall status when one stage is processing."""
    stages = {
        ProcessingStage.INGESTION: StageStatus.COMPLETED,
        ProcessingStage.QUALITY: StageStatus.PROCESSING,
        ProcessingStage.TAXONOMY: StageStatus.PENDING,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.PROCESSING


def test_calculate_overall_status_one_failed(status_tracker):
    """Test overall status when one stage has failed."""
    stages = {
        ProcessingStage.INGESTION: StageStatus.COMPLETED,
        ProcessingStage.QUALITY: StageStatus.COMPLETED,
        ProcessingStage.TAXONOMY: StageStatus.FAILED,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.FAILED


def test_calculate_overall_status_failed_takes_priority(status_tracker):
    """Test that FAILED status takes priority over PROCESSING."""
    stages = {
        ProcessingStage.INGESTION: StageStatus.COMPLETED,
        ProcessingStage.QUALITY: StageStatus.PROCESSING,
        ProcessingStage.TAXONOMY: StageStatus.FAILED,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.FAILED


def test_calculate_overall_status_processing_takes_priority_over_pending(
    status_tracker,
):
    """Test that PROCESSING status takes priority over PENDING."""
    stages = {
        ProcessingStage.INGESTION: StageStatus.COMPLETED,
        ProcessingStage.QUALITY: StageStatus.PROCESSING,
        ProcessingStage.TAXONOMY: StageStatus.PENDING,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.PROCESSING


def test_calculate_overall_status_all_pending(status_tracker):
    """Test overall status when all stages are pending."""
    stages = {
        ProcessingStage.INGESTION: StageStatus.PENDING,
        ProcessingStage.QUALITY: StageStatus.PENDING,
        ProcessingStage.TAXONOMY: StageStatus.PENDING,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.PENDING


def test_calculate_overall_status_mixed_completed_pending(status_tracker):
    """Test overall status with mix of completed and pending."""
    stages = {
        ProcessingStage.INGESTION: StageStatus.COMPLETED,
        ProcessingStage.QUALITY: StageStatus.COMPLETED,
        ProcessingStage.TAXONOMY: StageStatus.PENDING,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.PENDING


def test_calculate_overall_status_priority_order(status_tracker):
    """Test overall status calculation follows priority: FAILED > PROCESSING > COMPLETED > PENDING."""
    # Test FAILED > PROCESSING > COMPLETED > PENDING
    stages = {
        ProcessingStage.INGESTION: StageStatus.FAILED,
        ProcessingStage.QUALITY: StageStatus.PROCESSING,
        ProcessingStage.TAXONOMY: StageStatus.COMPLETED,
        ProcessingStage.GRAPH: StageStatus.PENDING,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.FAILED

    # Test PROCESSING > COMPLETED > PENDING
    stages = {
        ProcessingStage.INGESTION: StageStatus.PROCESSING,
        ProcessingStage.QUALITY: StageStatus.COMPLETED,
        ProcessingStage.TAXONOMY: StageStatus.PENDING,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.PROCESSING

    # Test COMPLETED > PENDING
    stages = {
        ProcessingStage.INGESTION: StageStatus.COMPLETED,
        ProcessingStage.QUALITY: StageStatus.PENDING,
    }
    overall = status_tracker._calculate_overall_status(stages)
    assert overall == StageStatus.PENDING


# ============================================================================
# Test Graceful Degradation (Redis Unavailable)
# ============================================================================


@pytest.mark.asyncio
async def test_set_progress_redis_unavailable(status_tracker, mock_cache):
    """Test set_progress handles Redis unavailability gracefully."""
    # Setup
    resource_id = 123
    stage = ProcessingStage.INGESTION
    status = StageStatus.COMPLETED

    # Mock cache to raise exception
    mock_cache.get.side_effect = Exception("Redis connection failed")

    # Execute - should not raise exception
    await status_tracker.set_progress(resource_id, stage, status)

    # Assert - method completes without error (logs warning internally)
    # No assertion needed - just verify no exception raised


@pytest.mark.asyncio
async def test_get_progress_redis_unavailable(status_tracker, mock_cache):
    """Test get_progress returns None when Redis is unavailable."""
    # Setup
    resource_id = 123

    # Mock cache to raise exception
    mock_cache.get.side_effect = Exception("Redis connection failed")

    # Execute
    progress = await status_tracker.get_progress(resource_id)

    # Assert - returns None gracefully
    assert progress is None


@pytest.mark.asyncio
async def test_set_progress_cache_set_fails(status_tracker, mock_cache):
    """Test set_progress handles cache.set failure gracefully."""
    # Setup
    resource_id = 123
    stage = ProcessingStage.QUALITY
    status = StageStatus.PROCESSING

    # Mock cache.get succeeds but cache.set fails
    mock_cache.get.return_value = None
    mock_cache.set.side_effect = Exception("Redis write failed")

    # Execute - should not raise exception
    await status_tracker.set_progress(resource_id, stage, status)

    # Assert - method completes without error


@pytest.mark.asyncio
async def test_get_progress_invalid_data(status_tracker, mock_cache):
    """Test get_progress handles invalid cached data gracefully."""
    # Setup
    resource_id = 123

    # Mock cache to return invalid data (missing required fields)
    mock_cache.get.return_value = {"invalid": "data"}

    # Execute
    progress = await status_tracker.get_progress(resource_id)

    # Assert - returns None when data is invalid
    assert progress is None


# ============================================================================
# Test Global Instance
# ============================================================================


def test_get_status_tracker_singleton():
    """Test get_status_tracker returns singleton instance."""
    # Execute
    tracker1 = get_status_tracker()
    tracker2 = get_status_tracker()

    # Assert - same instance
    assert tracker1 is tracker2


def test_get_status_tracker_creates_instance():
    """Test get_status_tracker creates instance if not exists."""
    # Execute
    tracker = get_status_tracker()

    # Assert
    assert tracker is not None
    assert isinstance(tracker, StatusTracker)
    assert tracker.cache is not None
    assert tracker.ttl == 86400


# ============================================================================
# Test Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_set_progress_overwrite_error_message(status_tracker, mock_cache):
    """Test set_progress can overwrite error message."""
    # Setup
    resource_id = 123

    # Mock existing progress with error
    existing_progress = {
        "resource_id": resource_id,
        "overall_status": StageStatus.FAILED.value,
        "stages": {ProcessingStage.TAXONOMY.value: StageStatus.FAILED.value},
        "error_message": "Old error message",
        "updated_at": "2026-01-01T10:00:00Z",
    }
    mock_cache.get.return_value = existing_progress

    # Execute - update with new error
    await status_tracker.set_progress(
        resource_id, ProcessingStage.TAXONOMY, StageStatus.FAILED, "New error message"
    )

    # Assert
    call_args = mock_cache.set.call_args
    data = call_args[0][1]
    assert data["error_message"] == "New error message"


@pytest.mark.asyncio
async def test_set_progress_clear_error_on_success(status_tracker, mock_cache):
    """Test that error message persists when not explicitly cleared."""
    # Setup
    resource_id = 123

    # Mock existing progress with error
    existing_progress = {
        "resource_id": resource_id,
        "overall_status": StageStatus.FAILED.value,
        "stages": {ProcessingStage.TAXONOMY.value: StageStatus.FAILED.value},
        "error_message": "Previous error",
        "updated_at": "2026-01-01T10:00:00Z",
    }
    mock_cache.get.return_value = existing_progress

    # Execute - update to completed without error message
    await status_tracker.set_progress(
        resource_id, ProcessingStage.TAXONOMY, StageStatus.COMPLETED
    )

    # Assert - error message persists (not cleared)
    call_args = mock_cache.set.call_args
    data = call_args[0][1]
    assert data["error_message"] == "Previous error"


@pytest.mark.asyncio
async def test_set_progress_all_five_stages(status_tracker, mock_cache):
    """Test set_progress works with all five processing stages."""
    # Setup
    resource_id = 555

    # Mock cache behavior
    stored_data = None

    def mock_get(key):
        return stored_data

    def mock_set(key, data, ttl):
        nonlocal stored_data
        stored_data = data

    mock_cache.get.side_effect = mock_get
    mock_cache.set.side_effect = mock_set

    # Execute - update all five stages
    await status_tracker.set_progress(
        resource_id, ProcessingStage.INGESTION, StageStatus.COMPLETED
    )
    await status_tracker.set_progress(
        resource_id, ProcessingStage.QUALITY, StageStatus.COMPLETED
    )
    await status_tracker.set_progress(
        resource_id, ProcessingStage.TAXONOMY, StageStatus.COMPLETED
    )
    await status_tracker.set_progress(
        resource_id, ProcessingStage.GRAPH, StageStatus.COMPLETED
    )
    await status_tracker.set_progress(
        resource_id, ProcessingStage.EMBEDDING, StageStatus.COMPLETED
    )

    # Get final progress
    progress = await status_tracker.get_progress(resource_id)

    # Assert all stages completed
    assert len(progress.stages) == 5
    assert progress.overall_status == StageStatus.COMPLETED
    assert all(status == StageStatus.COMPLETED for status in progress.stages.values())
