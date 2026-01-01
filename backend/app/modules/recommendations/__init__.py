"""
Recommendations Module

This module provides hybrid recommendation functionality combining:
- Content-based filtering using embeddings
- Collaborative filtering using user interactions
- Neural Collaborative Filtering (NCF) for deep learning recommendations
- User profile management and preference learning

Public Interface:
- recommendations_router: FastAPI router for recommendation endpoints
- RecommendationService: Main recommendation orchestration service
- UserProfileService: User profile and preference management
- Strategy classes: ContentBasedStrategy, CollaborativeStrategy, HybridStrategy
"""

__version__ = "1.0.0"
__domain__ = "recommendations"

# Import public interface components
from .router import recommendations_router
from .service import get_graph_based_recommendations
from .user_profile import UserProfileService
from .hybrid_service import HybridRecommendationService
from .strategies import RecommendationStrategyFactory
# Import models from database to avoid duplicate table definitions
from ...database.models import UserProfile, UserInteraction, RecommendationFeedback
from .schema import (
    RecommendedResource,
    RecommendationResponse,
    InteractionRequest,
    InteractionResponse,
    ProfileUpdateRequest,
    ProfileResponse,
    RecommendationItem,
    RecommendationsResponse,
    FeedbackRequest,
    FeedbackResponse,
)
from .handlers import register_handlers

__all__ = [
    # Router
    "recommendations_router",
    
    # Services
    "get_graph_based_recommendations",
    "UserProfileService",
    "HybridRecommendationService",
    "RecommendationStrategyFactory",
    
    # Models
    "UserProfile",
    "UserInteraction",
    "RecommendationFeedback",
    
    # Schemas
    "RecommendedResource",
    "RecommendationResponse",
    "InteractionRequest",
    "InteractionResponse",
    "ProfileUpdateRequest",
    "ProfileResponse",
    "RecommendationItem",
    "RecommendationsResponse",
    "FeedbackRequest",
    "FeedbackResponse",
    
    # Event handlers
    "register_handlers",
]
