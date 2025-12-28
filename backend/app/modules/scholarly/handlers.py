"""
Neo Alexandria 2.0 - Scholarly Module Event Handlers

Event handlers for the Scholarly module to enable event-driven communication
with other modules.

Events Subscribed:
- resource.created: Triggers metadata extraction for new resources

Events Emitted:
- metadata.extracted: When metadata is successfully extracted
- equations.parsed: When equations are found and parsed
- tables.extracted: When tables are extracted
"""

import logging
from typing import Dict

from ...shared.event_bus import event_bus, EventPriority
from ...shared.database import get_db
from ...events.event_types import SystemEvent
from .extractor import MetadataExtractor

logger = logging.getLogger(__name__)


async def handle_resource_created(payload: Dict) -> None:
    """
    Handle resource.created event by extracting scholarly metadata.
    
    Args:
        payload: Event payload containing resource_id and resource details
    """
    resource_id = payload.get("resource_id")
    if not resource_id:
        logger.warning("resource.created event missing resource_id")
        return
    
    try:
        # Get database session
        db = next(get_db())
        
        # Extract metadata
        extractor = MetadataExtractor(db)
        metadata = extractor.extract_scholarly_metadata(resource_id)
        
        if metadata:
            # Emit metadata.extracted event
            event_bus.emit(
                "metadata.extracted",
                {
                    "resource_id": resource_id,
                    "metadata_fields": list(metadata.keys()),
                    "completeness_score": metadata.get("metadata_completeness_score", 0.0),
                    "extraction_confidence": metadata.get("extraction_confidence", 0.0)
                },
                priority=EventPriority.LOW
            )
            
            # Emit equations.parsed event if equations were found
            if metadata.get("equation_count", 0) > 0:
                event_bus.emit(
                    "equations.parsed",
                    {
                        "resource_id": resource_id,
                        "equation_count": metadata["equation_count"]
                    },
                    priority=EventPriority.LOW
                )
            
            # Emit tables.extracted event if tables were found
            if metadata.get("table_count", 0) > 0:
                event_bus.emit(
                    "tables.extracted",
                    {
                        "resource_id": resource_id,
                        "table_count": metadata["table_count"]
                    },
                    priority=EventPriority.LOW
                )
            
            logger.info(f"Successfully extracted metadata for resource {resource_id}")
        else:
            logger.warning(f"No metadata extracted for resource {resource_id}")
            
    except Exception as e:
        logger.error(f"Failed to handle resource.created event for {resource_id}: {e}")
    finally:
        if 'db' in locals():
            db.close()


def register_handlers() -> None:
    """
    Register all event handlers for the Scholarly module.
    
    This function should be called during application startup to subscribe
    to relevant events.
    """
    # Subscribe to resource.created event
    event_bus.subscribe(
        SystemEvent.RESOURCE_CREATED.value,
        handle_resource_created,
        priority=EventPriority.LOW
    )
    
    logger.info("Scholarly module event handlers registered")

