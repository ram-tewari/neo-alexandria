"""
Graph Module Event Handlers

Event handlers for graph-related operations.
Handles resource lifecycle events to maintain graph consistency.
"""

import logging
from typing import Dict, Any

from app.shared.event_bus import event_bus, EventPriority
from app.events.event_types import SystemEvent

logger = logging.getLogger(__name__)


async def handle_resource_created(payload: Dict[str, Any]) -> None:
    """
    Handle resource.created event.
    
    Extracts citations from the resource and adds it to the knowledge graph.
    
    Args:
        payload: Event payload containing resource_id and resource data
    """
    resource_id = payload.get("resource_id")
    
    if not resource_id:
        logger.warning("resource.created event missing resource_id")
        return
    
    try:
        # Import here to avoid circular dependencies
        from app.modules.graph.citations import CitationService
        from app.shared.database import get_db
        
        # Get database session
        db = next(get_db())
        
        try:
            # Extract citations from the resource
            citation_service = CitationService(db)
            citations = citation_service.extract_citations(resource_id)
            
            if citations:
                logger.info(f"Extracted {len(citations)} citations from resource {resource_id}")
                
                # Emit citation.extracted event
                event_bus.emit(
                    SystemEvent.CITATIONS_EXTRACTED.value,
                    {
                        "resource_id": resource_id,
                        "citation_count": len(citations),
                        "citations": [c["target_url"] for c in citations]
                    },
                    priority=EventPriority.NORMAL
                )
            
            # Emit graph.updated event
            event_bus.emit(
                "graph.updated",
                {
                    "resource_id": resource_id,
                    "action": "resource_added",
                    "citation_count": len(citations)
                },
                priority=EventPriority.LOW
            )
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error handling resource.created for {resource_id}: {e}")


async def handle_resource_deleted(payload: Dict[str, Any]) -> None:
    """
    Handle resource.deleted event.
    
    Removes the resource from the knowledge graph and updates relationships.
    Citations are automatically cascade-deleted by database constraints.
    
    Args:
        payload: Event payload containing resource_id
    """
    resource_id = payload.get("resource_id")
    
    if not resource_id:
        logger.warning("resource.deleted event missing resource_id")
        return
    
    try:
        logger.info(f"Resource {resource_id} deleted, citations cascade-deleted by database")
        
        # Emit graph.updated event
        event_bus.emit(
            "graph.updated",
            {
                "resource_id": resource_id,
                "action": "resource_removed"
            },
            priority=EventPriority.LOW
        )
        
    except Exception as e:
        logger.error(f"Error handling resource.deleted for {resource_id}: {e}")


def register_handlers() -> None:
    """Register all graph module event handlers."""
    event_bus.subscribe("resource.created", handle_resource_created)
    event_bus.subscribe("resource.deleted", handle_resource_deleted)
    
    logger.info("Graph module event handlers registered")
