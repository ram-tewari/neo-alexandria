"""
Recommendations Event Handlers

Handles events from other modules to update user profiles and generate recommendations.

Events Subscribed:
- annotation.created: Update user profile based on annotation activity
- collection.resource_added: Update user profile based on collection activity

Events Emitted:
- recommendation.generated: When new recommendations are generated
- user.profile_updated: When user profile is updated
- interaction.recorded: When user interaction is recorded
"""

import logging
from typing import Dict, Any
from uuid import UUID


from app.shared.event_bus import event_bus
from app.shared.database import get_sync_db

logger = logging.getLogger(__name__)


def handle_annotation_created(payload: Dict[str, Any]):
    """
    Handle annotation.created event to update user profile.
    
    When a user creates an annotation, we:
    1. Record it as an interaction
    2. Update user profile preferences
    3. Emit user.profile_updated event
    
    Args:
        payload: Event payload containing annotation details
            - annotation_id: UUID of the annotation
            - user_id: UUID of the user
            - resource_id: UUID of the resource
            - text: Annotation text
    """
    try:
        from .user_profile import UserProfileService
        
        user_id = UUID(payload.get('user_id'))
        resource_id = UUID(payload.get('resource_id'))
        
        # Get database session
        db = next(get_sync_db())
        
        try:
            # Track interaction
            profile_service = UserProfileService(db)
            interaction = profile_service.track_interaction(
                user_id=user_id,
                resource_id=resource_id,
                interaction_type='annotation',
                dwell_time=None,
                scroll_depth=None,
                session_id=None,
                rating=None
            )
            
            # Emit interaction recorded event
            event_bus.emit('interaction.recorded', {
                'interaction_id': str(interaction.id),
                'user_id': str(user_id),
                'resource_id': str(resource_id),
                'interaction_type': 'annotation',
                'interaction_strength': interaction.interaction_strength,
                'timestamp': interaction.created_at.isoformat()
            })
            
            # Emit profile updated event
            event_bus.emit('user.profile_updated', {
                'user_id': str(user_id),
                'update_type': 'annotation_activity',
                'timestamp': interaction.created_at.isoformat()
            })
            
            logger.info(f"Updated user profile for annotation: user={user_id}, resource={resource_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error handling annotation.created event: {str(e)}", exc_info=True)


def handle_collection_resource_added(payload: Dict[str, Any]):
    """
    Handle collection.resource_added event to update user profile.
    
    When a user adds a resource to a collection, we:
    1. Record it as an interaction
    2. Update user profile preferences
    3. Emit user.profile_updated event
    
    Args:
        payload: Event payload containing collection details
            - collection_id: UUID of the collection
            - user_id: UUID of the user
            - resource_id: UUID of the resource
    """
    try:
        from .user_profile import UserProfileService
        
        user_id = UUID(payload.get('user_id'))
        resource_id = UUID(payload.get('resource_id'))
        
        # Get database session
        db = next(get_sync_db())
        
        try:
            # Track interaction
            profile_service = UserProfileService(db)
            interaction = profile_service.track_interaction(
                user_id=user_id,
                resource_id=resource_id,
                interaction_type='collection_add',
                dwell_time=None,
                scroll_depth=None,
                session_id=None,
                rating=None
            )
            
            # Emit interaction recorded event
            event_bus.emit('interaction.recorded', {
                'interaction_id': str(interaction.id),
                'user_id': str(user_id),
                'resource_id': str(resource_id),
                'interaction_type': 'collection_add',
                'interaction_strength': interaction.interaction_strength,
                'timestamp': interaction.created_at.isoformat()
            })
            
            # Emit profile updated event
            event_bus.emit('user.profile_updated', {
                'user_id': str(user_id),
                'update_type': 'collection_activity',
                'timestamp': interaction.created_at.isoformat()
            })
            
            logger.info(f"Updated user profile for collection add: user={user_id}, resource={resource_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error handling collection.resource_added event: {str(e)}", exc_info=True)


def register_handlers():
    """
    Register all event handlers for the recommendations module.
    
    This function should be called during application startup to
    subscribe to events from other modules.
    """
    # Subscribe to annotation events
    event_bus.subscribe('annotation.created', handle_annotation_created)
    
    # Subscribe to collection events
    event_bus.subscribe('collection.resource_added', handle_collection_resource_added)
    
    logger.info("Recommendations module event handlers registered")

