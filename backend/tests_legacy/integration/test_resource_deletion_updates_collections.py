"""
Integration test: Verify resource deletion triggers collection embedding updates.

This test verifies that the event-driven architecture properly handles the
resource deletion → collection update flow without circular dependencies.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock

from backend.app.services.resource_service import delete_resource
from backend.app.events.event_system import event_emitter
from backend.app.events.event_types import SystemEvent


def test_resource_deletion_emits_event(db_session):
    """Test that deleting a resource emits RESOURCE_DELETED event."""
    from backend.app.services.resource_service import create_pending_resource

    # Create a test resource
    resource = create_pending_resource(
        db_session, {"url": "https://example.com/test", "title": "Test Resource"}
    )
    resource_id = resource.id

    # Mock the event emitter to track emissions
    with patch.object(event_emitter, "emit") as mock_emit:
        # Delete the resource
        delete_resource(db_session, resource_id)

        # Verify RESOURCE_DELETED event was emitted
        mock_emit.assert_any_call(
            SystemEvent.RESOURCE_DELETED,
            {"resource_id": str(resource_id), "title": "Test Resource"},
            priority=pytest.ANY,
        )


def test_resource_deleted_hook_queues_collection_update(db_session):
    """Test that RESOURCE_DELETED event triggers collection embedding update task."""
    from backend.app.events.hooks import on_resource_deleted_update_collections
    from backend.app.events.event_system import Event

    resource_id = str(uuid.uuid4())

    # Mock the Celery task
    with patch(
        "backend.app.events.hooks.update_collection_embeddings_task"
    ) as mock_task:
        # Create event
        event = Event(
            name=SystemEvent.RESOURCE_DELETED, data={"resource_id": resource_id}
        )

        # Trigger hook
        on_resource_deleted_update_collections(event)

        # Verify task was queued
        mock_task.apply_async.assert_called_once_with(
            args=[resource_id], priority=5, countdown=5
        )


def test_collection_embedding_update_task_execution(db_session):
    """Test that the collection embedding update task executes correctly."""
    from backend.app.tasks.celery_tasks import update_collection_embeddings_task
    from backend.app.services.collection_service import CollectionService
    from backend.app.services.resource_service import create_pending_resource

    # Create a collection
    collection_service = CollectionService(db_session)
    collection = collection_service.create_collection(
        name="Test Collection", description="Test", owner_id="test_user"
    )

    # Create and add a resource
    resource = create_pending_resource(
        db_session, {"url": "https://example.com/test", "title": "Test Resource"}
    )
    collection_service.add_resources_to_collection(
        collection.id, [resource.id], "test_user"
    )

    # Mock the task's self parameter
    mock_self = MagicMock()
    mock_self.request.retries = 0

    # Execute the task
    result = update_collection_embeddings_task(
        mock_self, str(resource.id), db=db_session
    )

    # Verify task completed successfully
    assert result["status"] == "success"
    assert result["resource_id"] == str(resource.id)
    assert result["collections_updated"] >= 0


def test_no_circular_dependency_in_imports():
    """Test that there are no circular import dependencies."""
    # This test will fail at import time if there's a circular dependency
    from backend.app.services import resource_service
    from backend.app.services import collection_service

    # Verify neither service directly imports the other
    import inspect

    resource_source = inspect.getsource(resource_service)
    assert "from backend.app.services.collection_service" not in resource_source
    assert "import CollectionService" not in resource_source

    collection_source = inspect.getsource(collection_service)
    assert "from backend.app.services.resource_service" not in collection_source
    assert "import ResourceService" not in collection_source
