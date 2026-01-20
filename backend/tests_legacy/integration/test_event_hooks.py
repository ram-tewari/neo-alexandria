"""
Integration tests for event hooks.

Tests verify that event hooks correctly queue Celery tasks in response to
system events. These tests focus on the hook behavior, not the task execution.

Test Strategy:
- Use Celery's eager mode to capture task calls without executing them
- Verify that correct tasks are queued with correct parameters
- Verify priority and countdown values
- Test event-to-task flow for core consistency hooks
"""

import pytest
from unittest.mock import patch

from backend.app.events import event_emitter, EventPriority
from backend.app.events.event_types import SystemEvent
from backend.app.events.hooks import (
    Event,
    on_content_changed_regenerate_embedding,
    on_metadata_changed_recompute_quality,
    on_resource_updated_sync_search_index,
    on_resource_updated_invalidate_caches,
    register_all_hooks,
)


class TestEmbeddingRegenerationHook:
    """Test hook 5.1: Embedding regeneration on content change."""

    @patch("app.tasks.celery_tasks.regenerate_embedding_task")
    def test_content_change_triggers_embedding_regeneration(self, mock_task):
        """Test that content change event queues embedding regeneration task."""
        # Arrange
        resource_id = "test-resource-123"
        event = Event(
            name=SystemEvent.RESOURCE_CONTENT_CHANGED,
            data={"resource_id": resource_id},
            priority=EventPriority.HIGH,
        )

        # Act
        on_content_changed_regenerate_embedding(event)

        # Assert
        mock_task.apply_async.assert_called_once_with(
            args=[resource_id],
            priority=7,  # HIGH priority
            countdown=5,  # 5-second debounce
        )

    @patch("app.tasks.celery_tasks.regenerate_embedding_task")
    def test_missing_resource_id_logs_warning(self, mock_task, caplog):
        """Test that missing resource_id is handled gracefully."""
        # Arrange
        event = Event(
            name=SystemEvent.RESOURCE_CONTENT_CHANGED,
            data={},  # Missing resource_id
            priority=EventPriority.HIGH,
        )

        # Act
        on_content_changed_regenerate_embedding(event)

        # Assert
        mock_task.apply_async.assert_not_called()
        assert "missing resource_id" in caplog.text.lower()


class TestQualityRecomputationHook:
    """Test hook 5.2: Quality recomputation on metadata change."""

    @patch("app.tasks.celery_tasks.recompute_quality_task")
    def test_metadata_change_triggers_quality_recomputation(self, mock_task):
        """Test that metadata change event queues quality recomputation task."""
        # Arrange
        resource_id = "test-resource-456"
        event = Event(
            name=SystemEvent.RESOURCE_METADATA_CHANGED,
            data={"resource_id": resource_id},
            priority=EventPriority.NORMAL,
        )

        # Act
        on_metadata_changed_recompute_quality(event)

        # Assert
        mock_task.apply_async.assert_called_once_with(
            args=[resource_id],
            priority=5,  # MEDIUM priority
            countdown=10,  # 10-second debounce
        )

    @patch("app.tasks.celery_tasks.recompute_quality_task")
    def test_missing_resource_id_logs_warning(self, mock_task, caplog):
        """Test that missing resource_id is handled gracefully."""
        # Arrange
        event = Event(
            name=SystemEvent.RESOURCE_METADATA_CHANGED,
            data={},
            priority=EventPriority.NORMAL,
        )

        # Act
        on_metadata_changed_recompute_quality(event)

        # Assert
        mock_task.apply_async.assert_not_called()
        assert "missing resource_id" in caplog.text.lower()


class TestSearchIndexSyncHook:
    """Test hook 5.3: Search index sync on resource update."""

    @patch("app.tasks.celery_tasks.update_search_index_task")
    def test_resource_update_triggers_search_index_sync(self, mock_task):
        """Test that resource update event queues search index update task."""
        # Arrange
        resource_id = "test-resource-789"
        event = Event(
            name=SystemEvent.RESOURCE_UPDATED,
            data={"resource_id": resource_id},
            priority=EventPriority.CRITICAL,
        )

        # Act
        on_resource_updated_sync_search_index(event)

        # Assert
        mock_task.apply_async.assert_called_once_with(
            args=[resource_id],
            priority=9,  # URGENT priority
            countdown=1,  # 1-second minimal delay
        )

    @patch("app.tasks.celery_tasks.update_search_index_task")
    def test_urgent_priority_for_search_index(self, mock_task):
        """Test that search index updates use URGENT priority."""
        # Arrange
        event = Event(
            name=SystemEvent.RESOURCE_UPDATED,
            data={"resource_id": "test-123"},
            priority=EventPriority.NORMAL,
        )

        # Act
        on_resource_updated_sync_search_index(event)

        # Assert
        call_kwargs = mock_task.apply_async.call_args[1]
        assert call_kwargs["priority"] == 9  # URGENT


class TestCacheInvalidationHook:
    """Test hook 5.5: Cache invalidation on resource update."""

    @patch("app.tasks.celery_tasks.invalidate_cache_task")
    def test_resource_update_triggers_cache_invalidation(self, mock_task):
        """Test that resource update event queues cache invalidation task."""
        # Arrange
        resource_id = "test-resource-abc"
        event = Event(
            name=SystemEvent.RESOURCE_UPDATED,
            data={"resource_id": resource_id},
            priority=EventPriority.CRITICAL,
        )

        # Act
        on_resource_updated_invalidate_caches(event)

        # Assert
        mock_task.apply_async.assert_called_once()

        # Verify cache keys
        call_args = mock_task.apply_async.call_args
        cache_keys = call_args[1]["args"][0]

        assert f"embedding:{resource_id}" in cache_keys
        assert f"quality:{resource_id}" in cache_keys
        assert f"resource:{resource_id}" in cache_keys
        assert "search_query:*" in cache_keys

        # Verify priority and countdown
        assert call_args[1]["priority"] == 9  # URGENT
        assert call_args[1]["countdown"] == 0  # Immediate

    @patch("app.tasks.celery_tasks.invalidate_cache_task")
    def test_cache_invalidation_includes_pattern_keys(self, mock_task):
        """Test that cache invalidation includes wildcard patterns."""
        # Arrange
        event = Event(
            name=SystemEvent.RESOURCE_UPDATED,
            data={"resource_id": "test-123"},
            priority=EventPriority.CRITICAL,
        )

        # Act
        on_resource_updated_invalidate_caches(event)

        # Assert
        call_args = mock_task.apply_async.call_args
        cache_keys = call_args[1]["args"][0]

        # Should include pattern for search query invalidation
        assert any("*" in key for key in cache_keys)


class TestHookRegistration:
    """Test hook registration function."""

    def test_register_all_hooks_registers_correct_count(self, caplog):
        """Test that register_all_hooks registers all 8 hooks."""
        # Arrange
        event_emitter.clear_listeners()  # Clear any existing listeners

        # Act
        register_all_hooks()

        # Assert
        assert "8 event hooks" in caplog.text

    def test_hooks_registered_for_correct_events(self):
        """Test that hooks are registered for the correct event types."""
        # Arrange
        event_emitter.clear_listeners()

        # Act
        register_all_hooks()

        # Assert - verify key events have listeners
        assert (
            len(event_emitter.get_listeners(SystemEvent.RESOURCE_CONTENT_CHANGED)) > 0
        )
        assert (
            len(event_emitter.get_listeners(SystemEvent.RESOURCE_METADATA_CHANGED)) > 0
        )
        assert (
            len(event_emitter.get_listeners(SystemEvent.RESOURCE_UPDATED)) >= 2
        )  # Search + cache
        assert len(event_emitter.get_listeners(SystemEvent.CITATIONS_EXTRACTED)) > 0
        assert (
            len(event_emitter.get_listeners(SystemEvent.USER_INTERACTION_TRACKED)) > 0
        )
        assert len(event_emitter.get_listeners(SystemEvent.RESOURCE_CREATED)) > 0
        assert len(event_emitter.get_listeners(SystemEvent.AUTHORS_EXTRACTED)) > 0


class TestEndToEndEventFlow:
    """Test end-to-end event emission to task queuing."""

    @patch("app.tasks.celery_tasks.regenerate_embedding_task")
    @patch("app.tasks.celery_tasks.update_search_index_task")
    @patch("app.tasks.celery_tasks.invalidate_cache_task")
    def test_resource_update_triggers_multiple_hooks(
        self, mock_cache_task, mock_search_task, mock_embedding_task
    ):
        """Test that resource update triggers both search and cache hooks."""
        # Arrange
        event_emitter.clear_listeners()
        register_all_hooks()

        resource_id = "test-resource-xyz"

        # Act - emit resource updated event
        event_emitter.emit(
            SystemEvent.RESOURCE_UPDATED,
            {"resource_id": resource_id},
            EventPriority.CRITICAL,
        )

        # Assert - both search index and cache invalidation should be queued
        mock_search_task.apply_async.assert_called_once()
        mock_cache_task.apply_async.assert_called_once()

        # Embedding should NOT be triggered by resource.updated
        mock_embedding_task.apply_async.assert_not_called()

    @patch("app.tasks.celery_tasks.regenerate_embedding_task")
    @patch("app.tasks.celery_tasks.recompute_quality_task")
    def test_content_and_metadata_changes_trigger_different_hooks(
        self, mock_quality_task, mock_embedding_task
    ):
        """Test that content and metadata changes trigger different hooks."""
        # Arrange
        event_emitter.clear_listeners()
        register_all_hooks()

        resource_id = "test-resource-123"

        # Act - emit content changed event
        event_emitter.emit(
            SystemEvent.RESOURCE_CONTENT_CHANGED,
            {"resource_id": resource_id},
            EventPriority.HIGH,
        )

        # Assert - only embedding should be triggered
        mock_embedding_task.apply_async.assert_called_once()
        mock_quality_task.apply_async.assert_not_called()

        # Reset mocks
        mock_embedding_task.reset_mock()
        mock_quality_task.reset_mock()

        # Act - emit metadata changed event
        event_emitter.emit(
            SystemEvent.RESOURCE_METADATA_CHANGED,
            {"resource_id": resource_id},
            EventPriority.NORMAL,
        )

        # Assert - only quality should be triggered
        mock_quality_task.apply_async.assert_called_once()
        mock_embedding_task.apply_async.assert_not_called()


class TestHookErrorHandling:
    """Test error handling in hooks."""

    @patch("app.tasks.celery_tasks.regenerate_embedding_task")
    def test_hook_error_is_logged_but_not_raised(self, mock_task, caplog):
        """Test that hook errors are logged but don't crash the system."""
        # Arrange
        mock_task.apply_async.side_effect = Exception("Task queue error")

        event = Event(
            name=SystemEvent.RESOURCE_CONTENT_CHANGED,
            data={"resource_id": "test-123"},
            priority=EventPriority.HIGH,
        )

        # Act - should not raise exception
        on_content_changed_regenerate_embedding(event)

        # Assert - error should be logged
        assert "error" in caplog.text.lower()
        assert "test-123" in caplog.text


# Cleanup after tests
@pytest.fixture(autouse=True)
def cleanup_event_emitter():
    """Clean up event emitter after each test."""
    yield
    event_emitter.clear_listeners()
    event_emitter.clear_history()
