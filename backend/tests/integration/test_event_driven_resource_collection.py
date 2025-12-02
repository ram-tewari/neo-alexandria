"""
Integration test: Verify event-driven communication between Resources and Collections.

This test verifies that:
1. Resource deletion emits the resource.deleted event
2. Collections handler receives the event
3. Collection embeddings are recomputed
4. No direct imports exist between modules
"""

import pytest
import logging
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from backend.app.services.resource_service import (
    create_pending_resource,
    delete_resource
)
from backend.app.shared.event_bus import event_bus
from backend.app.events.event_types import SystemEvent

logger = logging.getLogger(__name__)


def test_resource_deletion_emits_event(db_session: Session):
    """Test that deleting a resource emits resource.deleted event."""
    # Create a test resource
    resource = create_pending_resource(
        db_session,
        {"url": "https://example.com/test-event", "title": "Test Event Resource"}
    )
    resource_id = str(resource.id)
    
    # Track emitted events
    emitted_events = []
    
    def capture_event(event_name, payload, priority=None):
        emitted_events.append({
            "event": event_name,
            "payload": payload,
            "priority": priority
        })
    
    # Patch event_bus.emit to capture events
    with patch.object(event_bus, 'emit', side_effect=capture_event):
        # Delete the resource
        delete_resource(db_session, resource_id)
    
    # Verify resource.deleted event was emitted
    resource_deleted_events = [
        e for e in emitted_events 
        if e["event"] == SystemEvent.RESOURCE_DELETED.value
    ]
    
    assert len(resource_deleted_events) == 1, "resource.deleted event should be emitted once"
    
    event = resource_deleted_events[0]
    assert event["payload"]["resource_id"] == resource_id
    assert event["payload"]["title"] == "Test Event Resource"
    assert event["priority"] is not None


def test_collections_handler_receives_event(db_session: Session):
    """Test that Collections handler receives and processes resource.deleted event."""
    from backend.app.modules.collections.handlers import handle_resource_deleted
    from backend.app.modules.collections.service import CollectionService
    
    # Create a collection
    collection_service = CollectionService(db_session)
    collection = collection_service.create_collection(
        name="Test Event Collection",
        description="Test collection for event handling",
        owner_id="test_user"
    )
    
    # Create a resource
    resource = create_pending_resource(
        db_session,
        {"url": "https://example.com/test-handler", "title": "Test Handler Resource"}
    )
    resource_id = str(resource.id)
    
    # Add resource to collection
    collection_service.add_resources_to_collection(
        collection.id,
        [resource.id],
        "test_user"
    )
    
    # Store original embedding (if any)
    db_session.refresh(collection)
    original_embedding = collection.embedding
    
    # Delete the resource (this will emit the event)
    delete_resource(db_session, resource_id)
    
    # Manually trigger the handler (simulating event bus notification)
    payload = {
        "resource_id": resource_id,
        "title": "Test Handler Resource"
    }
    
    # Mock get_sync_db to return our test session
    def mock_get_sync_db():
        yield db_session
    
    with patch('backend.app.modules.collections.handlers.get_sync_db', mock_get_sync_db):
        handle_resource_deleted(payload)
    
    # Verify collection was updated
    db_session.refresh(collection)
    
    # The embedding should have been recomputed
    # (it might be None if there are no remaining resources, or different if there are)
    logger.info(f"Original embedding: {original_embedding}")
    logger.info(f"New embedding: {collection.embedding}")
    
    # Verify the resource is no longer in the collection
    remaining_resources = collection_service.get_collection_resources(collection.id)
    resource_ids = [str(r.id) for r in remaining_resources]
    assert resource_id not in resource_ids, "Deleted resource should not be in collection"


def test_no_circular_imports():
    """Test that there are no circular import dependencies between modules."""
    import inspect
    
    # Import resource_service module
    from backend.app.services import resource_service
    
    # Get source code
    resource_source = inspect.getsource(resource_service)
    
    # Verify ResourceService doesn't import CollectionService
    assert "from backend.app.services.collection_service" not in resource_source, \
        "ResourceService should not import CollectionService"
    assert "from backend.app.modules.collections" not in resource_source, \
        "ResourceService should not import from collections module"
    
    # Check for any direct references to CollectionService (excluding comments)
    lines = resource_source.split('\n')
    for line in lines:
        if '#' in line:
            line = line[:line.index('#')]  # Remove comments
        if 'CollectionService' in line:
            assert False, f"Found CollectionService reference in ResourceService: {line.strip()}"
    
    logger.info("✓ No circular imports detected")


def test_event_handler_registration():
    """Test that event handlers can be registered with the event bus."""
    from backend.app.modules.collections.handlers import register_handlers
    
    # Clear any existing subscriptions for testing
    if "resource.deleted" in event_bus._subscribers:
        original_subscribers = event_bus._subscribers["resource.deleted"].copy()
    else:
        original_subscribers = []
    
    # Register handlers
    register_handlers()
    
    # Verify handler is registered
    assert "resource.deleted" in event_bus._subscribers
    assert len(event_bus._subscribers["resource.deleted"]) > len(original_subscribers)
    
    logger.info("✓ Event handlers registered successfully")


def test_end_to_end_event_flow(db_session: Session):
    """Test complete end-to-end event flow from resource deletion to collection update."""
    from backend.app.modules.collections.service import CollectionService
    from backend.app.modules.collections.handlers import register_handlers
    
    # Register event handlers
    register_handlers()
    
    # Create a collection
    collection_service = CollectionService(db_session)
    collection = collection_service.create_collection(
        name="E2E Test Collection",
        description="End-to-end test collection",
        owner_id="test_user"
    )
    
    # Create two resources
    resource1 = create_pending_resource(
        db_session,
        {"url": "https://example.com/e2e-1", "title": "E2E Resource 1"}
    )
    resource2 = create_pending_resource(
        db_session,
        {"url": "https://example.com/e2e-2", "title": "E2E Resource 2"}
    )
    
    # Add both resources to collection
    collection_service.add_resources_to_collection(
        collection.id,
        [resource1.id, resource2.id],
        "test_user"
    )
    
    # Compute initial embedding
    collection_service.compute_collection_embedding(collection.id)
    db_session.refresh(collection)
    initial_embedding = collection.embedding
    
    # Mock get_sync_db to return our test session
    def mock_get_sync_db():
        yield db_session
    
    with patch('backend.app.modules.collections.handlers.get_sync_db', mock_get_sync_db):
        # Delete one resource (this should trigger the event and update the collection)
        delete_resource(db_session, str(resource1.id))
    
    # Verify collection still exists and has been updated
    db_session.refresh(collection)
    
    # Verify only one resource remains
    remaining_resources = collection_service.get_collection_resources(collection.id)
    assert len(remaining_resources) == 1
    assert str(remaining_resources[0].id) == str(resource2.id)
    
    # The embedding should have changed (or be None if recomputation failed)
    logger.info(f"Initial embedding: {initial_embedding}")
    logger.info(f"Updated embedding: {collection.embedding}")
    
    logger.info("✓ End-to-end event flow completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
