"""
Shared Kernel - Common components used across all modules.

The shared kernel contains database, event bus, base model, and cross-cutting concerns.
It has no dependencies on any application modules, ensuring one-way dependency flow.

Components:
- database: Database engine, session factory, and Base
- event_bus: Event emitter and subscription system
- base_model: SQLAlchemy Base and common mixins
- embeddings: Embedding generation and caching service
- ai_core: AI operations (summarization, classification, entity extraction)
- cache: Redis caching with TTL and pattern invalidation
"""

__all__ = ["database", "event_bus", "base_model", "embeddings", "ai_core", "cache"]
