"""
Curation Event Handlers

Emits curation-related events for review workflows.

Events Emitted:
- curation.reviewed: When a resource is reviewed
- curation.approved: When a resource is approved
"""

import logging

from app.shared.event_bus import event_bus, EventPriority

logger = logging.getLogger(__name__)


def emit_curation_reviewed(
    review_id: str,
    resource_id: str,
    reviewer_id: str,
    status: str,
    quality_rating: float = None
):
    """
    Emit curation.reviewed event.
    
    This should be called after a curator reviews a resource.
    
    Args:
        review_id: UUID of the review record
        resource_id: UUID of the reviewed resource
        reviewer_id: User ID of the reviewer
        status: Review status (pending, approved, rejected, needs_revision)
        quality_rating: Optional quality rating assigned by reviewer
    """
    try:
        payload = {
            'review_id': review_id,
            'resource_id': resource_id,
            'reviewer_id': reviewer_id,
            'status': status
        }
        
        if quality_rating is not None:
            payload['quality_rating'] = quality_rating
        
        event_bus.emit(
            'curation.reviewed',
            payload,
            priority=EventPriority.NORMAL
        )
        logger.debug(f"Emitted curation.reviewed event for resource {resource_id}")
    except Exception as e:
        logger.error(f"Error emitting curation.reviewed event: {str(e)}", exc_info=True)


def emit_curation_approved(
    review_id: str,
    resource_id: str,
    reviewer_id: str,
    approval_notes: str = None
):
    """
    Emit curation.approved event.
    
    This should be called when a resource is approved by a curator.
    
    Args:
        review_id: UUID of the review record
        resource_id: UUID of the approved resource
        reviewer_id: User ID of the reviewer who approved
        approval_notes: Optional notes about the approval
    """
    try:
        payload = {
            'review_id': review_id,
            'resource_id': resource_id,
            'reviewer_id': reviewer_id
        }
        
        if approval_notes:
            payload['approval_notes'] = approval_notes
        
        event_bus.emit(
            'curation.approved',
            payload,
            priority=EventPriority.NORMAL
        )
        logger.info(f"Emitted curation.approved event for resource {resource_id}")
    except Exception as e:
        logger.error(f"Error emitting curation.approved event: {str(e)}", exc_info=True)


def register_handlers():
    """
    Register all event handlers for the curation module.
    
    This function should be called during application startup.
    Currently, curation module only emits events and doesn't subscribe to any.
    """
    logger.info("Curation module event handlers registered")
