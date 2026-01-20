"""
Monitoring Event Handlers

The monitoring module subscribes to all events for metrics aggregation
but doesn't emit its own events (except alerts, which are handled separately).

Events Subscribed:
- All events (for metrics tracking)
"""

import logging

logger = logging.getLogger(__name__)


def register_handlers():
    """
    Register all event handlers for the monitoring module.

    This function should be called during application startup.
    Currently, monitoring module tracks events through the event bus
    metrics system rather than individual handlers.
    """
    logger.info("Monitoring module event handlers registered")
