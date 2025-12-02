"""Event system for Neo Alexandria.

This module provides a publisher-subscriber pattern for decoupled component communication.
"""

from ..shared.event_bus import EventBus, EventPriority, event_bus, Event
from .event_types import SystemEvent

# Backward compatibility aliases
event_emitter = event_bus
EventEmitter = EventBus

__all__ = ["Event", "EventPriority", "EventEmitter", "event_emitter", "SystemEvent"]
