"""
Taxonomy Event Handlers

Event handlers for taxonomy module.
Handles resource.created events to trigger auto-classification.
"""

from typing import Dict, Any
from app.shared.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)


async def handle_resource_created(payload: Dict[str, Any]) -> None:
    """
    Handle resource.created event to auto-classify resources.
    
    Args:
        payload: Event payload containing resource_id and resource data
    """
    resource_id = payload.get("resource_id")
    logger.info(f"Taxonomy: Handling resource.created for resource {resource_id}")
    
    # TODO: Implement auto-classification logic
    # 1. Get resource content
    # 2. Run ML classification
    # 3. Assign to taxonomy nodes
    # 4. Emit resource.classified event
    
    # Emit event
    await event_bus.emit(
        "resource.classified",
        {
            "resource_id": resource_id,
            "classifications": [],
            "confidence_scores": {},
        }
    )


def register_handlers() -> None:
    """Register all taxonomy event handlers"""
    event_bus.subscribe("resource.created", handle_resource_created)
    logger.info("Taxonomy event handlers registered")
