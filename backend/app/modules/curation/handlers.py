"""
Neo Alexandria 2.0 - Curation Module Event Handlers

Event handlers for the Curation module to enable event-driven communication
with other modules.

Events Subscribed:
- quality.outlier_detected: Adds resources to review queue when quality outliers are detected

Events Emitted:
- curation.reviewed: When an item is reviewed by a curator
- curation.approved: When content is approved after review
- curation.rejected: When content is rejected during review
"""

import logging
from typing import Dict
from datetime import datetime, timezone

from ...shared.event_bus import event_bus, EventPriority
from ...shared.database import get_db
from ...database.models import Resource

logger = logging.getLogger(__name__)


async def handle_quality_outlier_detected(payload: Dict) -> None:
    """
    Handle quality.outlier_detected event by adding resource to review queue.
    
    The review queue is implicitly managed by the quality_score field on resources.
    This handler logs the outlier detection and can trigger additional workflows.
    
    Args:
        payload: Event payload containing resource_id, outlier_score, and reasons
    """
    resource_id = payload.get("resource_id")
    outlier_score = payload.get("outlier_score")
    reasons = payload.get("reasons", [])
    
    if not resource_id:
        logger.warning("quality.outlier_detected event missing resource_id")
        return
    
    try:
        # Get database session
        db = next(get_db())
        
        # Verify resource exists
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            logger.warning(f"Resource {resource_id} not found for outlier detection")
            return
        
        # Log the outlier detection
        logger.info(
            f"Quality outlier detected for resource {resource_id}: "
            f"score={outlier_score}, reasons={reasons}"
        )
        
        # The resource is automatically in the review queue due to its low quality_score
        # Additional workflow logic can be added here (e.g., notifications, assignments)
        
        # Emit curation.reviewed event to track that this item needs review
        event_bus.emit(
            "curation.reviewed",
            {
                "resource_id": str(resource_id),
                "reviewer_id": "system",  # System-initiated review
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "flagged",
                "outlier_score": outlier_score,
                "reasons": reasons
            },
            priority=EventPriority.LOW
        )
        
        logger.info(f"Added resource {resource_id} to review queue")
            
    except Exception as e:
        logger.error(f"Failed to handle quality.outlier_detected event for {resource_id}: {e}")
    finally:
        if 'db' in locals():
            db.close()


def emit_reviewed_event(resource_id: str, reviewer_id: str, action: str) -> None:
    """
    Emit curation.reviewed event.
    
    Args:
        resource_id: Resource UUID
        reviewer_id: Curator/user ID
        action: Action taken (approved, rejected, flagged)
    """
    event_bus.emit(
        "curation.reviewed",
        {
            "resource_id": resource_id,
            "reviewer_id": reviewer_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action
        },
        priority=EventPriority.NORMAL
    )


def emit_approved_event(
    resource_id: str, 
    reviewer_id: str, 
    previous_quality: float, 
    new_quality: float
) -> None:
    """
    Emit curation.approved event.
    
    Args:
        resource_id: Resource UUID
        reviewer_id: Curator/user ID
        previous_quality: Quality score before approval
        new_quality: Quality score after approval
    """
    event_bus.emit(
        "curation.approved",
        {
            "resource_id": resource_id,
            "reviewer_id": reviewer_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_quality": previous_quality,
            "new_quality": new_quality
        },
        priority=EventPriority.NORMAL
    )


def emit_rejected_event(resource_id: str, reviewer_id: str, reason: str) -> None:
    """
    Emit curation.rejected event.
    
    Args:
        resource_id: Resource UUID
        reviewer_id: Curator/user ID
        reason: Reason for rejection
    """
    event_bus.emit(
        "curation.rejected",
        {
            "resource_id": resource_id,
            "reviewer_id": reviewer_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason
        },
        priority=EventPriority.NORMAL
    )


def register_handlers() -> None:
    """
    Register all event handlers for the Curation module.
    
    This function should be called during application startup to subscribe
    to relevant events.
    """
    # Subscribe to quality.outlier_detected event
    event_bus.subscribe(
        "quality.outlier_detected",
        handle_quality_outlier_detected,
        priority=EventPriority.NORMAL
    )
    
    logger.info("Curation module event handlers registered")
