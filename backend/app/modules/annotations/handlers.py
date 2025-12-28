"""
Annotations Event Handlers - Event-driven integration.

This module handles events related to annotations and subscribes to
events from other modules.

Events Emitted:
- annotation.created: When a new annotation is created
- annotation.updated: When an annotation is modified
- annotation.deleted: When an annotation is removed

Events Subscribed:
- resource.deleted: Cascade delete annotations for deleted resource
"""

import logging
from typing import Dict, Any
from sqlalchemy import delete

from ...shared.event_bus import event_bus
from ...shared.database import get_sync_db
from .model import Annotation

logger = logging.getLogger(__name__)


def handle_resource_deleted(payload: Dict[str, Any]) -> None:
    """
    Handle resource.deleted event by cascade deleting associated annotations.
    
    When a resource is deleted, all annotations on that resource should be
    automatically deleted to maintain referential integrity.
    
    Args:
        payload: Event payload containing:
            - resource_id: UUID of the deleted resource
    """
    resource_id = payload.get("resource_id")
    
    if not resource_id:
        logger.warning("resource.deleted event missing resource_id")
        return
    
    try:
        # Get database session
        db = next(get_sync_db())
        
        # Delete all annotations for this resource
        stmt = delete(Annotation).where(Annotation.resource_id == resource_id)
        result = db.execute(stmt)
        db.commit()
        
        deleted_count = result.rowcount
        if deleted_count > 0:
            logger.info(f"Cascade deleted {deleted_count} annotations for resource {resource_id}")
            
            # Emit annotation.deleted events for each deleted annotation
            # Note: In a production system, we might want to fetch the annotation IDs
            # before deletion to emit individual events
            event_bus.emit(
                "annotation.deleted",
                {
                    "resource_id": str(resource_id),
                    "count": deleted_count,
                    "reason": "resource_deleted"
                }
            )
    except Exception as e:
        logger.error(f"Failed to cascade delete annotations for resource {resource_id}: {e}")
        # Don't raise - event handlers should be resilient
    finally:
        db.close()


def emit_annotation_created(annotation_id: str, resource_id: str, user_id: str) -> None:
    """
    Emit annotation.created event.
    
    Args:
        annotation_id: UUID of the created annotation
        resource_id: UUID of the resource
        user_id: User ID of the annotation owner
    """
    event_bus.emit(
        "annotation.created",
        {
            "annotation_id": annotation_id,
            "resource_id": resource_id,
            "user_id": user_id
        }
    )


def emit_annotation_updated(annotation_id: str, resource_id: str, user_id: str, changed_fields: list) -> None:
    """
    Emit annotation.updated event.
    
    Args:
        annotation_id: UUID of the updated annotation
        resource_id: UUID of the resource
        user_id: User ID of the annotation owner
        changed_fields: List of field names that were changed
    """
    event_bus.emit(
        "annotation.updated",
        {
            "annotation_id": annotation_id,
            "resource_id": resource_id,
            "user_id": user_id,
            "changed_fields": changed_fields
        }
    )


def emit_annotation_deleted(annotation_id: str, resource_id: str, user_id: str) -> None:
    """
    Emit annotation.deleted event.
    
    Args:
        annotation_id: UUID of the deleted annotation
        resource_id: UUID of the resource
        user_id: User ID of the annotation owner
    """
    event_bus.emit(
        "annotation.deleted",
        {
            "annotation_id": annotation_id,
            "resource_id": resource_id,
            "user_id": user_id
        }
    )


def register_handlers() -> None:
    """
    Register all event handlers for the annotations module.
    
    This function should be called during application startup to subscribe
    to events from other modules.
    """
    # Subscribe to resource.deleted event
    event_bus.subscribe("resource.deleted", handle_resource_deleted)
    
    logger.info("Annotations module event handlers registered")

