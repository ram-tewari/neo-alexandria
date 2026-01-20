"""
Search Module Models

This module re-exports Search models from the central database.models module.
All model definitions are in app/database/models.py to avoid circular imports.
"""

# Re-export models from central database.models
from ...database.models import SyntheticQuestion

__all__ = ["SyntheticQuestion"]
