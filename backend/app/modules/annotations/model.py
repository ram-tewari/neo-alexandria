"""
Annotations Model - Database model for annotations.

This module re-exports Annotation models from the central database.models module.
All model definitions are in app/database/models.py to avoid circular imports.

Related files:
- schema.py: Pydantic schemas for validation
- service.py: Business logic for annotation operations
- ../../database/models.py: Actual model definitions
"""

# Re-export models from central database.models
from ...database.models import Annotation

__all__ = ["Annotation"]

