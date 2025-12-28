"""
Resources Module - Database Models

This module re-exports Resource models from the central database.models module.
All model definitions are in app/database/models.py to avoid circular imports.

Related files:
- schema.py: Pydantic schemas for validation
- service.py: Business logic for resource operations
- ../../database/models.py: Actual model definitions
"""

# Re-export models from central database.models
from ...database.models import Resource, ResourceStatus

__all__ = ["Resource", "ResourceStatus"]
