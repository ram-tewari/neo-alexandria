"""
Neo Alexandria 2.0 - Collection Models

This module re-exports Collection models from the central database.models module.
All model definitions are in app/database/models.py to avoid circular imports.
"""

# Re-export models from central database.models
from ...database.models import Collection, CollectionResource

__all__ = ["Collection", "CollectionResource"]
