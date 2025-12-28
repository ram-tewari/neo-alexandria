"""
Monitoring Event Handlers

Handles events for metrics aggregation and monitoring.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ...shared.event_bus import event_bus

logger = logging.getLogger(__name__)


# In-memory metrics storage (for demonstration - use Prometheus in production)
_event_metrics = {
    "total_events": 0,
    "events_by_type": {},
    "events_by_module": {},
    "last_event_time": None
}


def handle_all_events(event_name: str, payload: Dict[str, Any]) -> None:
    """
    Handle all events for metrics aggregation.
    
    This handler subscribes to all events and aggregates metrics
    for monitoring purposes.
    
    Args:
        event_name: Name of the event
        payload: Event payload
    """
    try:
        # Update total event count
        _event_metrics["total_events"] += 1
        
        # Update event type count
        if event_name not in _event_metrics["events_by_type"]:
            _event_metrics["events_by_type"][event_name] = 0
        _event_metrics["events_by_type"][event_name] += 1
        
        # Extract module from event name (e.g., "resource.created" -> "resource")
        module = event_name.split(".")[0] if "." in event_name else "unknown"
        if module not in _event_metrics["events_by_module"]:
            _event_metrics["events_by_module"][module] = 0
        _event_metrics["events_by_module"][module] += 1
        
        # Update last event time
        _event_metrics["last_event_time"] = datetime.utcnow().isoformat()
        
        logger.debug(f"Monitoring: Recorded event {event_name}")
        
    except Exception as e:
        logger.error(f"Error handling event for monitoring: {str(e)}", exc_info=True)


def handle_quality_outlier_detected(payload: Dict[str, Any]) -> None:
    """
    Handle quality outlier detection events.
    
    Emits monitoring alert when quality outliers are detected.
    
    Args:
        payload: Event payload with resource_id and quality_score
    """
    try:
        resource_id = payload.get("resource_id")
        quality_score = payload.get("quality_score", 0.0)
        
        logger.warning(
            f"Quality outlier detected for resource {resource_id}: "
            f"score={quality_score}"
        )
        
        # Emit monitoring alert
        event_bus.emit(
            "monitoring.alert_triggered",
            {
                "alert_type": "quality_outlier",
                "resource_id": resource_id,
                "quality_score": quality_score,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error handling quality outlier event: {str(e)}", exc_info=True)


def handle_quality_degradation_detected(payload: Dict[str, Any]) -> None:
    """
    Handle quality degradation detection events.
    
    Emits monitoring alert when quality degradation is detected.
    
    Args:
        payload: Event payload with resource_id and degradation details
    """
    try:
        resource_id = payload.get("resource_id")
        previous_score = payload.get("previous_score", 0.0)
        current_score = payload.get("current_score", 0.0)
        
        logger.warning(
            f"Quality degradation detected for resource {resource_id}: "
            f"{previous_score} -> {current_score}"
        )
        
        # Emit monitoring alert
        event_bus.emit(
            "monitoring.alert_triggered",
            {
                "alert_type": "quality_degradation",
                "resource_id": resource_id,
                "previous_score": previous_score,
                "current_score": current_score,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error handling quality degradation event: {str(e)}", exc_info=True)


def handle_system_error(payload: Dict[str, Any]) -> None:
    """
    Handle system error events.
    
    Emits monitoring alert for system errors.
    
    Args:
        payload: Event payload with error details
    """
    try:
        error_type = payload.get("error_type", "unknown")
        error_message = payload.get("error_message", "")
        component = payload.get("component", "unknown")
        
        logger.error(
            f"System error in {component}: {error_type} - {error_message}"
        )
        
        # Emit monitoring alert
        event_bus.emit(
            "monitoring.alert_triggered",
            {
                "alert_type": "system_error",
                "error_type": error_type,
                "error_message": error_message,
                "component": component,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error handling system error event: {str(e)}", exc_info=True)


def get_event_metrics() -> Dict[str, Any]:
    """
    Get aggregated event metrics.
    
    Returns:
        Dictionary with event metrics
    """
    return _event_metrics.copy()


def register_handlers() -> None:
    """
    Register all monitoring event handlers.
    
    Subscribes to all events for metrics aggregation and specific
    events for alert generation.
    """
    # Subscribe to all events for metrics aggregation
    # Note: This is a wildcard subscription - the event bus should support this
    # For now, we'll subscribe to specific event patterns
    
    # Resource events
    event_bus.subscribe("resource.created", handle_all_events)
    event_bus.subscribe("resource.updated", handle_all_events)
    event_bus.subscribe("resource.deleted", handle_all_events)
    
    # Collection events
    event_bus.subscribe("collection.created", handle_all_events)
    event_bus.subscribe("collection.updated", handle_all_events)
    event_bus.subscribe("collection.deleted", handle_all_events)
    event_bus.subscribe("collection.resource_added", handle_all_events)
    event_bus.subscribe("collection.resource_removed", handle_all_events)
    
    # Search events
    event_bus.subscribe("search.executed", handle_all_events)
    event_bus.subscribe("search.results_returned", handle_all_events)
    
    # Annotation events
    event_bus.subscribe("annotation.created", handle_all_events)
    event_bus.subscribe("annotation.updated", handle_all_events)
    event_bus.subscribe("annotation.deleted", handle_all_events)
    
    # Quality events
    event_bus.subscribe("quality.computed", handle_all_events)
    event_bus.subscribe("quality.outlier_detected", handle_all_events)
    event_bus.subscribe("quality.outlier_detected", handle_quality_outlier_detected)
    event_bus.subscribe("quality.degradation_detected", handle_all_events)
    event_bus.subscribe("quality.degradation_detected", handle_quality_degradation_detected)
    
    # Taxonomy events
    event_bus.subscribe("resource.classified", handle_all_events)
    event_bus.subscribe("taxonomy.node_created", handle_all_events)
    event_bus.subscribe("taxonomy.model_trained", handle_all_events)
    
    # Graph events
    event_bus.subscribe("citation.extracted", handle_all_events)
    event_bus.subscribe("graph.updated", handle_all_events)
    event_bus.subscribe("hypothesis.discovered", handle_all_events)
    
    # Recommendation events
    event_bus.subscribe("recommendation.generated", handle_all_events)
    event_bus.subscribe("user.profile_updated", handle_all_events)
    event_bus.subscribe("interaction.recorded", handle_all_events)
    
    # Curation events
    event_bus.subscribe("curation.reviewed", handle_all_events)
    event_bus.subscribe("curation.approved", handle_all_events)
    event_bus.subscribe("curation.rejected", handle_all_events)
    
    # Scholarly events
    event_bus.subscribe("metadata.extracted", handle_all_events)
    event_bus.subscribe("equations.parsed", handle_all_events)
    event_bus.subscribe("tables.extracted", handle_all_events)
    
    # System error events
    event_bus.subscribe("system.error", handle_all_events)
    event_bus.subscribe("system.error", handle_system_error)
    
    logger.info("Monitoring event handlers registered")
