"""
Search Event Handlers

Emits search-related events for analytics and monitoring.

Events Emitted:
- search.executed: When a search query is executed
"""

import logging
from typing import Dict, Any

from app.shared.event_bus import event_bus, EventPriority

logger = logging.getLogger(__name__)


def emit_search_executed(
    query: str,
    search_type: str,
    result_count: int,
    execution_time: float,
    user_id: str = None,
    filters: Dict[str, Any] = None
):
    """
    Emit search.executed event.
    
    This should be called by the search service after executing a search query.
    
    Args:
        query: Search query text
        search_type: Type of search (fulltext, semantic, hybrid, three_way_hybrid)
        result_count: Number of results returned
        execution_time: Query execution time in seconds
        user_id: Optional user ID who executed the search
        filters: Optional filters applied to the search
    """
    try:
        payload = {
            'query': query,
            'search_type': search_type,
            'result_count': result_count,
            'execution_time': execution_time
        }
        
        if user_id:
            payload['user_id'] = user_id
        
        if filters:
            payload['filters'] = filters
        
        event_bus.emit(
            'search.executed',
            payload,
            priority=EventPriority.LOW
        )
        logger.debug(f"Emitted search.executed event for query: {query[:50]}...")
    except Exception as e:
        logger.error(f"Error emitting search.executed event: {str(e)}", exc_info=True)


def register_handlers():
    """
    Register all event handlers for the search module.
    
    This function should be called during application startup.
    Currently, search module only emits events and doesn't subscribe to any.
    """
    logger.info("Search module event handlers registered")
