"""
Collections Event Handlers

Handles events from other modules and emits collection-related events.

Events Subscribed:
- resource.deleted: Remove resource from all collections when deleted

Events Emitted:
- collection.resource_added: When a resource is added to a collection
- collection.resource_removed: When a resource is removed from a collection
"""

import logging
from uuid import UUID

from app.shared.event_bus import event_bus, EventPriority
from app.shared.database import get_sync_db

logger = logging.getLogger(__name__)


def handle_resource_deleted(event):
    """
    Handle resource.deleted event to remove resource from collections.
    
    When a resource is deleted, we:
    1. Find all collections containing that resource
    2. Remove the resource from each collection
    3. Emit collection.resource_removed events
    
    Args:
        event: Event object containing resource deletion details
            - resource_id: UUID of the deleted resource
    """
    try:
        payload = event.data
        resource_id = UUID(payload.get('resource_id'))
        
        # Get database session
        db = next(get_sync_db())
        
        try:
            from .model import CollectionResource
            from sqlalchemy import select
            
            # Find all collection associations for this resource
            stmt = select(CollectionResource).where(CollectionResource.resource_id == resource_id)
            result = db.execute(stmt)
            associations = result.scalars().all()
            
            # Delete each association and emit events
            for association in associations:
                collection_id = str(association.collection_id)
                
                # Delete association
                db.delete(association)
                
                # Emit collection.resource_removed event
                event_bus.emit(
                    'collection.resource_removed',
                    {
                        'collection_id': collection_id,
                        'resource_id': str(resource_id),
                        'reason': 'resource_deleted'
                    },
                    priority=EventPriority.NORMAL
                )
            
            db.commit()
            
            logger.info(f"Removed resource {resource_id} from {len(associations)} collections")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error handling resource.deleted event: {str(e)}", exc_info=True)


def emit_collection_resource_added(collection_id: str, resource_id: str, user_id: str):
    """
    Emit collection.resource_added event.
    
    This should be called by the collection service after adding a resource to a collection.
    
    Args:
        collection_id: UUID of the collection
        resource_id: UUID of the resource added
        user_id: User ID who added the resource
    """
    try:
        event_bus.emit(
            'collection.resource_added',
            {
                'collection_id': collection_id,
                'resource_id': resource_id,
                'user_id': user_id
            },
            priority=EventPriority.NORMAL
        )
        logger.debug(f"Emitted collection.resource_added event for collection {collection_id}")
    except Exception as e:
        logger.error(f"Error emitting collection.resource_added event: {str(e)}", exc_info=True)


def emit_collection_resource_removed(collection_id: str, resource_id: str, user_id: str = None, reason: str = 'user_removed'):
    """
    Emit collection.resource_removed event.
    
    This should be called by the collection service after removing a resource from a collection.
    
    Args:
        collection_id: UUID of the collection
        resource_id: UUID of the resource removed
        user_id: Optional user ID who removed the resource
        reason: Reason for removal (user_removed, resource_deleted, etc.)
    """
    try:
        payload = {
            'collection_id': collection_id,
            'resource_id': resource_id,
            'reason': reason
        }
        if user_id:
            payload['user_id'] = user_id
            
        event_bus.emit(
            'collection.resource_removed',
            payload,
            priority=EventPriority.NORMAL
        )
        logger.debug(f"Emitted collection.resource_removed event for collection {collection_id}")
    except Exception as e:
        logger.error(f"Error emitting collection.resource_removed event: {str(e)}", exc_info=True)


def register_handlers():
    """
    Register all event handlers for the collections module.
    
    This function should be called during application startup to
    subscribe to events from other modules.
    """
    # Subscribe to resource events
    event_bus.on('resource.deleted', handle_resource_deleted, async_handler=False)
    
    logger.info("Collections module event handlers registered")
