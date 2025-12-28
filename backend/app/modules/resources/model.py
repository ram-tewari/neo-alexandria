"""
Resources Module - Database Models

This module re-exports Resource models from the central database.models module.
All model definitions are in app/database/models.py to avoid circular imports.
"""

# Re-export models from central database.models
from ...database.models import Resource

__all__ = ["Resource"]
