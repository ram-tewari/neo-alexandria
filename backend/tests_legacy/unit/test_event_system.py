"""Unit tests for the event system.

Tests event emission, handler execution, error isolation, event history,
and async handler support.
"""

import asyncio
import pytest
from datetime import datetime

from backend.app.events import EventPriority, EventEmitter, SystemEvent
from backend.app.events.hooks import Event


@pytest.fixture
def emitter():
    """Create a fresh EventEmitter instance for each test."""
    emitter = EventEmitter()
    emitter.clear_listeners()
    emitter.clear_history()
    yield emitter
    emitter.clear_listeners()
    emitter.clear_history()


class TestEventPriority:
    """Test EventPriority enum."""

    def test_priority_values(self):
        """Test that priority levels have correct numeric values."""
        assert EventPriority.CRITICAL.value == 100
        assert EventPriority.HIGH.value == 75
        assert EventPriority.NORMAL.value == 50
        assert EventPriority.LOW.value == 25


class TestEvent:
    """Test Event dataclass."""

    def test_event_creation(self):
        """Test creating an event with required fields."""
        event = Event(name="test.event", data={"key": "value"})

        assert event.name == "test.event"
        assert event.data == {"key": "value"}
        assert isinstance(event.timestamp, datetime)
        assert event.priority == EventPriority.NORMAL
        assert event.correlation_id is not None

    def test_event_with_priority(self):
        """Test creating an event with custom priority."""
        event = Event(name="test.event", data={}, priority=EventPriority.HIGH)

        assert event.priority == EventPriority.HIGH

    def test_event_with_correlation_id(self):
        """Test creating an event with custom correlation ID."""
        event = Event(name="test.event", data={}, correlation_id="custom-id-123")

        assert event.correlation_id == "custom-id-123"


class TestEventEmitter:
    """Test EventEmitter singleton and core functionality."""

    def test_singleton_pattern(self):
        """Test that EventEmitter is a singleton."""
        emitter1 = EventEmitter()
        emitter2 = EventEmitter()

        assert emitter1 is emitter2

    def test_register_handler(self, emitter):
        """Test registering an event handler."""
        handler_called = False

        def handler(event):
            nonlocal handler_called
            handler_called = True

        emitter.on("test.event", handler)
        emitter.emit("test.event", {})

        assert handler_called

    def test_unregister_handler(self, emitter):
        """Test unregistering an event handler."""
        handler_called = False

        def handler(event):
            nonlocal handler_called
            handler_called = True

        emitter.on("test.event", handler)
        emitter.off("test.event", handler)
        emitter.emit("test.event", {})

        assert not handler_called

    def test_multiple_handlers(self, emitter):
        """Test multiple handlers for the same event."""
        handler1_called = False
        handler2_called = False

        def handler1(event):
            nonlocal handler1_called
            handler1_called = True

        def handler2(event):
            nonlocal handler2_called
            handler2_called = True

        emitter.on("test.event", handler1)
        emitter.on("test.event", handler2)
        emitter.emit("test.event", {})

        assert handler1_called
        assert handler2_called

    def test_handler_receives_event(self, emitter):
        """Test that handlers receive the event object."""
        received_event = None

        def handler(event):
            nonlocal received_event
            received_event = event

        emitter.on("test.event", handler)
        emitted_event = emitter.emit("test.event", {"key": "value"})

        assert received_event is not None
        assert received_event.name == "test.event"
        assert received_event.data == {"key": "value"}
        assert received_event.correlation_id == emitted_event.correlation_id

    def test_handler_error_isolation(self, emitter):
        """Test that handler errors don't affect other handlers."""
        handler1_called = False
        handler2_called = False

        def handler1(event):
            nonlocal handler1_called
            handler1_called = True
            raise Exception("Handler 1 error")

        def handler2(event):
            nonlocal handler2_called
            handler2_called = True

        emitter.on("test.event", handler1)
        emitter.on("test.event", handler2)
        emitter.emit("test.event", {})

        # Both handlers should be called despite handler1 raising an error
        assert handler1_called
        assert handler2_called

    def test_get_listeners(self, emitter):
        """Test retrieving registered listeners."""

        def handler1(event):
            pass

        def handler2(event):
            pass

        emitter.on("test.event", handler1)
        emitter.on("test.event", handler2)

        listeners = emitter.get_listeners("test.event")

        assert len(listeners) == 2
        assert handler1 in listeners
        assert handler2 in listeners

    def test_no_duplicate_registrations(self, emitter):
        """Test that the same handler isn't registered twice."""
        call_count = 0

        def handler(event):
            nonlocal call_count
            call_count += 1

        emitter.on("test.event", handler)
        emitter.on("test.event", handler)  # Register again
        emitter.emit("test.event", {})

        # Handler should only be called once
        assert call_count == 1


class TestEventHistory:
    """Test event history tracking."""

    def test_event_history_storage(self, emitter):
        """Test that events are stored in history."""
        emitter.emit("test.event1", {"data": 1})
        emitter.emit("test.event2", {"data": 2})

        history = emitter.get_event_history()

        assert len(history) == 2
        assert history[0]["name"] == "test.event1"
        assert history[1]["name"] == "test.event2"

    def test_event_history_limit(self, emitter):
        """Test that event history respects the limit parameter."""
        for i in range(10):
            emitter.emit(f"test.event{i}", {"index": i})

        history = emitter.get_event_history(limit=5)

        assert len(history) == 5
        # Should return the last 5 events
        assert history[0]["data"]["index"] == 5
        assert history[4]["data"]["index"] == 9

    def test_event_history_max_size(self, emitter):
        """Test that event history maintains max size of 1000."""
        # This test would be slow with 1000+ events, so we'll just verify
        # the deque is configured correctly
        assert emitter._event_history.maxlen == 1000

    def test_event_history_serialization(self, emitter):
        """Test that event history is properly serialized."""
        emitter.emit("test.event", {"key": "value"}, priority=EventPriority.HIGH)

        history = emitter.get_event_history()
        event_dict = history[0]

        assert "name" in event_dict
        assert "data" in event_dict
        assert "timestamp" in event_dict
        assert "priority" in event_dict
        assert "correlation_id" in event_dict
        assert event_dict["priority"] == "HIGH"
        assert isinstance(event_dict["timestamp"], str)  # ISO format


class TestAsyncHandlers:
    """Test async handler support."""

    def test_async_handler_registration(self, emitter):
        """Test registering an async handler."""
        handler_called = False

        async def async_handler(event):
            nonlocal handler_called
            handler_called = True
            await asyncio.sleep(0.01)  # Simulate async work

        emitter.on("test.event", async_handler, async_handler=True)
        emitter.emit("test.event", {})

        # Give async handler time to execute by running event loop
        import time

        time.sleep(0.1)

        # Note: In production, async handlers are scheduled with asyncio.create_task
        # which requires an active event loop. This test verifies registration works.
        listeners = emitter.get_listeners("test.event")
        assert async_handler in listeners

    def test_mixed_sync_async_handlers(self, emitter):
        """Test mixing sync and async handlers."""
        sync_called = False

        def sync_handler(event):
            nonlocal sync_called
            sync_called = True

        async def async_handler(event):
            await asyncio.sleep(0.01)

        emitter.on("test.event", sync_handler, async_handler=False)
        emitter.on("test.event", async_handler, async_handler=True)
        emitter.emit("test.event", {})

        # Sync handler should be called immediately
        assert sync_called

        # Verify both handlers are registered
        listeners = emitter.get_listeners("test.event")
        assert len(listeners) == 2
        assert sync_handler in listeners
        assert async_handler in listeners


class TestSystemEvents:
    """Test SystemEvent enum."""

    def test_resource_events_defined(self):
        """Test that resource lifecycle events are defined."""
        assert SystemEvent.RESOURCE_CREATED == "resource.created"
        assert SystemEvent.RESOURCE_UPDATED == "resource.updated"
        assert SystemEvent.RESOURCE_DELETED == "resource.deleted"
        assert SystemEvent.RESOURCE_CONTENT_CHANGED == "resource.content_changed"
        assert SystemEvent.RESOURCE_METADATA_CHANGED == "resource.metadata_changed"

    def test_processing_events_defined(self):
        """Test that processing events are defined."""
        assert SystemEvent.INGESTION_STARTED == "ingestion.started"
        assert SystemEvent.INGESTION_COMPLETED == "ingestion.completed"
        assert SystemEvent.EMBEDDING_GENERATED == "embedding.generated"
        assert SystemEvent.QUALITY_COMPUTED == "quality.computed"
        assert SystemEvent.CLASSIFICATION_COMPLETED == "classification.completed"

    def test_search_events_defined(self):
        """Test that search events are defined."""
        assert SystemEvent.SEARCH_EXECUTED == "search.executed"
        assert SystemEvent.SEARCH_INDEX_UPDATED == "search.index_updated"

    def test_graph_events_defined(self):
        """Test that graph events are defined."""
        assert SystemEvent.GRAPH_EDGE_ADDED == "graph.edge_added"
        assert SystemEvent.CITATIONS_EXTRACTED == "citations.extracted"

    def test_cache_events_defined(self):
        """Test that cache events are defined."""
        assert SystemEvent.CACHE_HIT == "cache.hit"
        assert SystemEvent.CACHE_MISS == "cache.miss"
        assert SystemEvent.CACHE_INVALIDATED == "cache.invalidated"

    def test_user_events_defined(self):
        """Test that user events are defined."""
        assert SystemEvent.USER_INTERACTION_TRACKED == "user.interaction_tracked"
        assert SystemEvent.USER_PROFILE_UPDATED == "user.profile_updated"

    def test_system_events_defined(self):
        """Test that system events are defined."""
        assert SystemEvent.BACKGROUND_TASK_STARTED == "background_task.started"
        assert SystemEvent.BACKGROUND_TASK_COMPLETED == "background_task.completed"
        assert SystemEvent.SYSTEM_STARTUP == "system.startup"
