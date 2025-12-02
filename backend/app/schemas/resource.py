"""
DEPRECATED: This module has been moved to backend.app.modules.resources.schema

This compatibility shim re-exports from the new location to maintain backward compatibility
during the migration to modular architecture.

Please update your imports to:
    from backend.app.modules.resources import (
        ResourceBase,
        ResourceCreate,
        ResourceUpdate,
        ResourceRead,
        ResourceInDB,
        ResourceStatus
    )
"""

import warnings

warnings.warn(
    "backend.app.schemas.resource is deprecated. "
    "Use backend.app.modules.resources schema classes instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
from backend.app.modules.resources import (
    ResourceBase,
    ResourceCreate,
    ResourceUpdate,
    ResourceRead,
    ResourceInDB,
    ResourceStatus
)

__all__ = [
    "ResourceBase",
    "ResourceCreate",
    "ResourceUpdate",
    "ResourceRead",
    "ResourceInDB",
    "ResourceStatus"
]
