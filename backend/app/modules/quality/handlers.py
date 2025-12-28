"""
Quality Module - Event Handlers

This module implements event handlers for the Quality module.
It subscribes to resource events and emits quality-related events.

Events Subscribed:
- resource.created: Triggers initial quality computation
- resource.updated: Triggers quality recomputation

Events Emitted:
- quality.computed: When quality assessment is completed
- quality.outlier_detected: When a quality outlier is detected
- quality.degradation_detected: When quality degradation is detected
"""

import logging
from typing import Dict, Any

from app.shared.event_bus import event_bus
from app.shared.database import get_sync_db
from .service import QualityService

logger = logging.getLogger(__name__)


async def handle_resource_created(payload: Dict[str, Any]) -> None:
    """
    Handle resource.created event by computing initial quality assessment.
    
    Args:
        payload: Event payload containing:
            - resource_id: ID of the created resource
            - resource_data: Resource metadata
    """
    resource_id = payload.get("resource_id")
    if not resource_id:
        logger.warning("resource.created event missing resource_id")
        return
    
    try:
        # Get database session
        db = next(get_sync_db())
        
        # Create quality service
        quality_service = QualityService(db)
        
        # Compute initial quality scores
        logger.info(f"Computing initial quality for resource {resource_id}")
        quality_scores = quality_service.get_quality_scores(str(resource_id))
        
        if quality_scores:
            # Emit quality.computed event
            await event_bus.emit("quality.computed", {
                "resource_id": resource_id,
                "quality_overall": quality_scores.overall,
                "dimensions": {
                    "accuracy": quality_scores.accuracy,
                    "completeness": quality_scores.completeness,
                    "consistency": quality_scores.consistency,
                    "timeliness": quality_scores.timeliness,
                    "relevance": quality_scores.relevance,
                },
                "timestamp": payload.get("timestamp"),
            })
            
            # Check for outliers
            if quality_scores.overall < 0.3:  # Low quality threshold
                await event_bus.emit("quality.outlier_detected", {
                    "resource_id": resource_id,
                    "quality_score": quality_scores.overall,
                    "outlier_type": "low",
                    "threshold": 0.3,
                    "timestamp": payload.get("timestamp"),
                })
                logger.info(f"Quality outlier detected for resource {resource_id}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error computing quality for resource {resource_id}: {e}", exc_info=True)


async def handle_resource_updated(payload: Dict[str, Any]) -> None:
    """
    Handle resource.updated event by recomputing quality assessment.
    
    Args:
        payload: Event payload containing:
            - resource_id: ID of the updated resource
            - resource_data: Updated resource metadata
            - previous_quality: Previous quality score (optional)
    """
    resource_id = payload.get("resource_id")
    if not resource_id:
        logger.warning("resource.updated event missing resource_id")
        return
    
    try:
        # Get database session
        db = next(get_sync_db())
        
        # Create quality service
        quality_service = QualityService(db)
        
        # Get previous quality score
        previous_quality = payload.get("previous_quality")
        
        # Recompute quality scores
        logger.info(f"Recomputing quality for resource {resource_id}")
        quality_scores = quality_service.get_quality_scores(str(resource_id))
        
        if quality_scores:
            # Emit quality.computed event
            await event_bus.emit("quality.computed", {
                "resource_id": resource_id,
                "quality_overall": quality_scores.overall,
                "dimensions": {
                    "accuracy": quality_scores.accuracy,
                    "completeness": quality_scores.completeness,
                    "consistency": quality_scores.consistency,
                    "timeliness": quality_scores.timeliness,
                    "relevance": quality_scores.relevance,
                },
                "timestamp": payload.get("timestamp"),
            })
            
            # Check for quality degradation
            if previous_quality and quality_scores.overall < previous_quality:
                degradation_amount = previous_quality - quality_scores.overall
                if degradation_amount >= 0.2:  # 20% degradation threshold
                    await event_bus.emit("quality.degradation_detected", {
                        "resource_id": resource_id,
                        "previous_score": previous_quality,
                        "current_score": quality_scores.overall,
                        "degradation_amount": degradation_amount,
                        "timestamp": payload.get("timestamp"),
                    })
                    logger.warning(f"Quality degradation detected for resource {resource_id}: "
                                 f"{previous_quality:.2f} -> {quality_scores.overall:.2f}")
            
            # Check for outliers
            if quality_scores.overall < 0.3:  # Low quality threshold
                await event_bus.emit("quality.outlier_detected", {
                    "resource_id": resource_id,
                    "quality_score": quality_scores.overall,
                    "outlier_type": "low",
                    "threshold": 0.3,
                    "timestamp": payload.get("timestamp"),
                })
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error recomputing quality for resource {resource_id}: {e}", exc_info=True)


def register_handlers() -> None:
    """
    Register all event handlers for the Quality module.
    
    This function should be called during application startup to subscribe
    to relevant events.
    """
    event_bus.subscribe("resource.created", handle_resource_created)
    event_bus.subscribe("resource.updated", handle_resource_updated)
    
    logger.info("Quality module event handlers registered")
