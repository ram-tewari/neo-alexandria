"""
Neo Alexandria 2.0 - Cache Module

This module provides Redis-based caching with intelligent TTL management
and pattern-based invalidation for Phase 12.5 event-driven architecture.
"""

from .redis_cache import RedisCache, CacheStats, cache

__all__ = ["RedisCache", "CacheStats", "cache"]
