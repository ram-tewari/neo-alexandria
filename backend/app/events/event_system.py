"""Core event system implementation.

Provides EventPriority enum, Event dataclass, and EventEmitter singleton for
publisher-subscriber pattern with support for both sync and async handlers.
"""

import asyncio
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels for task queue prioritization."""
    
    CRITICAL = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25


@dataclass
class Event:
    """Represents a system event with metadata.
    
    Attributes:
        name: Event type identifier (e.g., "resource.updated")
        data: Event payload containing relevant information
        timestamp: When the event occurred
        priority: Processing priority level
        correlation_id: Optional ID for tracking event chains
    """
    
    name: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))


class EventEmitter:
    """Singleton event dispatcher with support for sync and async handlers.
    
    Provides methods to register listeners, unregister listeners, and emit events.
    Implements error isolation so handler failures don't affect other handlers.
    Maintains event history for debugging and audit trails.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize event emitter (only once due to singleton)."""
        if not EventEmitter._initialized:
            self._listeners: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            self._event_history: deque = deque(maxlen=1000)
            EventEmitter._initialized = True
            logger.info("EventEmitter initialized")
    
    def on(
        self,
        event_name: str,
        handler: Callable,
        async_handler: bool = False
    ) -> None:
        """Register an event listener.
        
        Args:
            event_name: Name of the event to listen for
            handler: Callback function to execute when event is emitted
            async_handler: Whether the handler is an async function
        """
        handler_info = {
            "handler": handler,
            "async": async_handler
        }
        
        # Avoid duplicate registrations
        if handler_info not in self._listeners[event_name]:
            self._listeners[event_name].append(handler_info)
            logger.debug(
                f"Registered {'async' if async_handler else 'sync'} handler "
                f"for event '{event_name}'"
            )
    
    def off(self, event_name: str, handler: Callable) -> None:
        """Unregister an event listener.
        
        Args:
            event_name: Name of the event
            handler: Handler function to remove
        """
        self._listeners[event_name] = [
            h for h in self._listeners[event_name]
            if h["handler"] != handler
        ]
        logger.debug(f"Unregistered handler for event '{event_name}'")
    
    def emit(
        self,
        event_name: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL
    ) -> Event:
        """Emit an event and execute all registered handlers.
        
        Implements error isolation - handler failures don't affect other handlers.
        
        Args:
            event_name: Name of the event to emit
            data: Event payload
            priority: Event priority level
            
        Returns:
            The emitted Event object
        """
        event = Event(
            name=event_name,
            data=data,
            priority=priority
        )
        
        # Store in history
        self._event_history.append(event)
        
        logger.debug(
            f"Emitting event '{event_name}' with priority {priority.name} "
            f"(correlation_id: {event.correlation_id})"
        )
        
        # Execute all handlers with error isolation
        handlers = self._listeners.get(event_name, [])
        
        for handler_info in handlers:
            handler = handler_info["handler"]
            is_async = handler_info["async"]
            
            try:
                if is_async:
                    # Schedule async handler
                    asyncio.create_task(handler(event))
                else:
                    # Execute sync handler
                    handler(event)
                    
            except Exception as e:
                # Log error but continue with other handlers
                logger.error(
                    f"Handler error for event '{event_name}': {e}",
                    exc_info=True,
                    extra={
                        "event_name": event_name,
                        "correlation_id": event.correlation_id,
                        "handler": handler.__name__
                    }
                )
        
        return event
    
    def get_listeners(self, event_name: str) -> List[Callable]:
        """Get all registered listeners for an event.
        
        Args:
            event_name: Name of the event
            
        Returns:
            List of handler functions
        """
        return [h["handler"] for h in self._listeners.get(event_name, [])]
    
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries with serializable data
        """
        events = list(self._event_history)[-limit:]
        
        return [
            {
                "name": event.name,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
                "priority": event.priority.name,
                "correlation_id": event.correlation_id
            }
            for event in events
        ]
    
    def clear_listeners(self, event_name: Optional[str] = None) -> None:
        """Clear listeners for testing purposes.
        
        Args:
            event_name: Specific event to clear, or None to clear all
        """
        if event_name:
            self._listeners[event_name] = []
        else:
            self._listeners.clear()
        logger.debug(f"Cleared listeners for: {event_name or 'all events'}")
    
    def clear_history(self) -> None:
        """Clear event history for testing purposes."""
        self._event_history.clear()
        logger.debug("Cleared event history")


# Global singleton instance
event_emitter = EventEmitter()
