"""
Recommendations Database Models

This module re-exports Recommendation models from the central database.models module.
All model definitions are in app/database/models.py to avoid circular imports.

Related files:
- schema.py: Pydantic schemas for validation
- service.py: Business logic for recommendation operations
- ../../database/models.py: Actual model definitions
"""

# Re-export models from central database.models
from ...database.models import UserProfile, UserInteraction, RecommendationFeedback

__all__ = ["UserProfile", "UserInteraction", "RecommendationFeedback"]
