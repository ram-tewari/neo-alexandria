"""
DEPRECATED: This module has been moved to backend.app.modules.collections.schema

This compatibility shim re-exports from the new location to maintain backward compatibility
during the migration to modular architecture.

Please update your imports to:
    from backend.app.modules.collections import (
        CollectionCreate,
        CollectionUpdate,
        CollectionRead,
        CollectionWithResources,
        CollectionResourcesUpdate,
        CollectionRecommendation,
        CollectionRecommendationsResponse,
        ResourceSummary
    )
"""

import warnings

warnings.warn(
    "backend.app.schemas.collection is deprecated. "
    "Use backend.app.modules.collections schema classes instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
from backend.app.modules.collections import (
    CollectionCreate,
    CollectionUpdate,
    CollectionRead,
    CollectionWithResources,
    CollectionResourcesUpdate,
    CollectionRecommendation,
    CollectionRecommendationsResponse,
    ResourceSummary
)

__all__ = [
    "CollectionCreate",
    "CollectionUpdate",
    "CollectionRead",
    "CollectionWithResources",
    "CollectionResourcesUpdate",
    "CollectionRecommendation",
    "CollectionRecommendationsResponse",
    "ResourceSummary"
]
