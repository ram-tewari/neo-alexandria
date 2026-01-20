"""
Collections Module - Public Interface

This module provides collection management functionality including:
- Collection CRUD operations
- Resource membership management
- Collection-level embeddings and recommendations
- Hierarchical collection organization

Public API:
- collections_router: FastAPI router for collection endpoints
- CollectionService: Business logic for collection operations
- Schema classes: Pydantic models for validation

Version: 1.0.0
Domain: Collections
"""

__version__ = "1.0.0"
__domain__ = "collections"

# Import public components
# NOTE: Router and service imports are deferred to avoid model conflicts during migration
# from .router import router as collections_router
# from .service import CollectionService
from .schema import (
    CollectionCreate,
    CollectionUpdate,
    CollectionRead,
    CollectionWithResources,
    CollectionResourcesUpdate,
    CollectionRecommendation,
    CollectionRecommendationsResponse,
    ResourceSummary,
)


# Lazy imports to avoid model conflicts
def __getattr__(name):
    """Lazy import to avoid model conflicts during migration phase."""
    if name == "collections_router":
        from .router import router

        return router
    elif name == "CollectionService":
        from .service import CollectionService

        return CollectionService
    elif name == "register_handlers":
        from .handlers import register_handlers

        return register_handlers
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Public exports
__all__ = [
    # Router
    "collections_router",
    # Service
    "CollectionService",
    # Schemas
    "CollectionCreate",
    "CollectionUpdate",
    "CollectionRead",
    "CollectionWithResources",
    "CollectionResourcesUpdate",
    "CollectionRecommendation",
    "CollectionRecommendationsResponse",
    "ResourceSummary",
    # Event handlers
    "register_handlers",
]
