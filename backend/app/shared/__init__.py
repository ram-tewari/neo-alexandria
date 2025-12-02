"""
Shared Kernel - Common components used across all modules.

The shared kernel contains only database, event bus, and base model components.
It has no dependencies on any application modules, ensuring one-way dependency flow.

Components:
- database: Database engine, session factory, and Base
- event_bus: Event emitter and subscription system
- base_model: SQLAlchemy Base and common mixins
"""

__all__ = ["database", "event_bus", "base_model"]
