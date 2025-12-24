"""
Collections Module - Event Handlers

Event handlers for cross-module communication.
Handles events from other modules that affect collections.

Events:
- resource.deleted: Recompute embeddings for affected collections
"""

import logging
from typing import Dict, Any
import uuid

from ...shared.event_bus import event_bus
from ...shared.database import get_sync_db
from .service import CollectionService

logger = logging.getLogger(__name__)


def handle_resource_deleted(payload: Dict[str, Any]) -> None:
    """
    Handle resource deletion event.
    
    When a resource is deleted, we need to:
    1. Find all collections containing that resource
    2. Recompute their embeddings (since a member was removed)
    
    Args:
        payload: Event payload containing:
            - resource_id: UUID of deleted resource
    """
    try:
        resource_id = payload.get("resource_id")
        
        if not resource_id:
            logger.warning("resource.deleted event missing resource_id")
            return
        
        # Convert to UUID if string
        if isinstance(resource_id, str):
            resource_id = uuid.UUID(resource_id)
        
        logger.info(f"Handling resource.deleted event for resource {resource_id}")
        
        # Get database session
        db_gen = get_sync_db()
        db = next(db_gen)
        
        try:
            # Create service instance
            service = CollectionService(db)
            
            # Find collections containing this resource
            collections = service.find_collections_with_resource(resource_id)
            
            if not collections:
                logger.debug(f"No collections contain resource {resource_id}")
                return
            
            logger.info(f"Found {len(collections)} collections containing resource {resource_id}")
            
            # Recompute embeddings for each affected collection
            for collection in collections:
                try:
                    logger.debug(f"Recomputing embedding for collection {collection.id} ({collection.name})")
                    service.compute_collection_embedding(collection.id)
                except Exception as e:
                    logger.error(
                        f"Failed to recompute embedding for collection {collection.id}: {e}",
                        exc_info=True
                    )
            
            logger.info(f"Successfully updated {len(collections)} collections after resource deletion")
            
        finally:
            # Close database session
            try:
                next(db_gen)
            except StopIteration:
                pass
    
    except Exception as e:
        logger.error(
            f"Error handling resource.deleted event: {e}",
            exc_info=True,
            extra={"payload": payload}
        )


def register_handlers() -> None:
    """
    Register all event handlers for the Collections module.
    
    This should be called during application startup to ensure
    the module responds to relevant events from other modules.
    """
    logger.info("Registering Collections module event handlers")
    
    # Subscribe to resource.deleted event
    event_bus.subscribe("resource.deleted", handle_resource_deleted)
    
    logger.info("Collections module event handlers registered successfully")
