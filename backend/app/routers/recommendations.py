"""
Neo Alexandria 2.0 - Recommendations API Router

This module provides REST API endpoints for Phase 11 hybrid recommendation engine.

Endpoints:
- GET /api/recommendations: Get personalized recommendations
- POST /api/interactions: Track user-resource interactions
- GET /api/profile: Get user profile settings
- PUT /api/profile: Update user profile settings
- POST /api/recommendations/feedback: Submit recommendation feedback
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from ..database.base import get_sync_db
from ..database.models import User, RecommendationFeedback
from ..services.hybrid_recommendation_service import HybridRecommendationService
from ..services.user_profile_service import UserProfileService
from ..utils.performance_monitoring import metrics


router = APIRouter(prefix="/api", tags=["recommendations-phase11"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class InteractionRequest(BaseModel):
    """Request schema for tracking user interactions."""
    resource_id: str = Field(..., description="Resource UUID")
    interaction_type: str = Field(..., description="Type of interaction: view, annotation, collection_add, export, rating")
    dwell_time: Optional[int] = Field(None, description="Time spent on resource in seconds")
    scroll_depth: Optional[float] = Field(None, ge=0.0, le=1.0, description="Scroll depth (0.0-1.0)")
    session_id: Optional[str] = Field(None, description="Session identifier")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5 stars)")
    
    @validator('interaction_type')
    def validate_interaction_type(cls, v):
        allowed_types = ["view", "annotation", "collection_add", "export", "rating"]
        if v not in allowed_types:
            raise ValueError(f"interaction_type must be one of {allowed_types}")
        return v


class InteractionResponse(BaseModel):
    """Response schema for interaction tracking."""
    interaction_id: str
    user_id: str
    resource_id: str
    interaction_type: str
    interaction_strength: float
    is_positive: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    """Request schema for updating user profile."""
    diversity_preference: Optional[float] = Field(None, ge=0.0, le=1.0, description="Diversity preference (0.0-1.0)")
    novelty_preference: Optional[float] = Field(None, ge=0.0, le=1.0, description="Novelty preference (0.0-1.0)")
    recency_bias: Optional[float] = Field(None, ge=0.0, le=1.0, description="Recency bias (0.0-1.0)")
    excluded_sources: Optional[List[str]] = Field(None, description="List of excluded source domains")
    research_domains: Optional[List[str]] = Field(None, description="List of research domains")
    active_domain: Optional[str] = Field(None, description="Currently active research domain")


class ProfileResponse(BaseModel):
    """Response schema for user profile."""
    user_id: str
    diversity_preference: float
    novelty_preference: float
    recency_bias: float
    research_domains: Optional[List[str]]
    active_domain: Optional[str]
    excluded_sources: Optional[List[str]]
    total_interactions: int
    last_active_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RecommendationScores(BaseModel):
    """Breakdown of recommendation scores."""
    collaborative: float
    content: float
    graph: float
    quality: float
    recency: float


class RecommendationItem(BaseModel):
    """Individual recommendation item."""
    resource_id: str
    title: str
    score: float
    strategy: str
    scores: RecommendationScores
    rank: int
    novelty_score: float
    view_count: int


class RecommendationMetadata(BaseModel):
    """Metadata about the recommendation process."""
    total: int
    strategy: str
    is_cold_start: Optional[bool] = None
    interaction_count: Optional[int] = None
    diversity_applied: bool
    novelty_applied: bool
    gini_coefficient: Optional[float] = None
    diversity_preference: Optional[float] = None
    novelty_preference: Optional[float] = None


class RecommendationsResponse(BaseModel):
    """Response schema for recommendations."""
    recommendations: List[RecommendationItem]
    metadata: RecommendationMetadata


class FeedbackRequest(BaseModel):
    """Request schema for recommendation feedback."""
    resource_id: str = Field(..., description="Resource UUID")
    was_clicked: bool = Field(..., description="Whether the recommendation was clicked")
    was_useful: Optional[bool] = Field(None, description="Whether the recommendation was useful (explicit feedback)")
    feedback_notes: Optional[str] = Field(None, description="Optional feedback notes")


class FeedbackResponse(BaseModel):
    """Response schema for recommendation feedback."""
    feedback_id: str
    user_id: str
    resource_id: str
    was_clicked: bool
    was_useful: Optional[bool]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Helper Functions
# ============================================================================

def _get_current_user_id(db: Session) -> UUID:
    """
    Get current authenticated user ID.
    
    For now, returns a test user. In production, this would extract
    user ID from JWT token or session.
    """
    # TODO: Replace with actual authentication
    # For now, get or create a test user
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        test_user = User(
            email="test@example.com",
            username="testuser"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
    return test_user.id


def _get_hybrid_recommendation_service(db: Session) -> HybridRecommendationService:
    """Helper to create HybridRecommendationService instance."""
    return HybridRecommendationService(db)


def _get_user_profile_service(db: Session) -> UserProfileService:
    """Helper to create UserProfileService instance."""
    return UserProfileService(db)


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    limit: int = Query(20, ge=1, le=100, description="Number of recommendations to return"),
    strategy: str = Query("hybrid", description="Strategy: collaborative, content, graph, or hybrid"),
    diversity: Optional[float] = Query(None, ge=0.0, le=1.0, description="Override diversity preference"),
    min_quality: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum quality threshold"),
    db: Session = Depends(get_sync_db),
):
    """
    Get personalized recommendations for the authenticated user.
    
    Args:
        limit: Number of recommendations (1-100, default 20)
        strategy: Recommendation strategy (collaborative, content, graph, hybrid)
        diversity: Override user's diversity preference (0.0-1.0)
        min_quality: Minimum quality threshold (0.0-1.0)
        db: Database session
        
    Returns:
        RecommendationsResponse with recommendations and metadata
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)
        
        # Validate strategy
        allowed_strategies = ["collaborative", "content", "graph", "hybrid"]
        if strategy not in allowed_strategies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid strategy. Must be one of {allowed_strategies}"
            )
        
        # Build filters
        filters = {}
        if min_quality is not None:
            filters['min_quality'] = min_quality
            filters['exclude_outliers'] = True
        
        # Override diversity preference if provided
        if diversity is not None:
            profile_service = _get_user_profile_service(db)
            profile = profile_service.get_or_create_profile(user_id)
            profile.diversity_preference = diversity
            db.commit()
        
        # Generate recommendations
        recommendation_service = _get_hybrid_recommendation_service(db)
        result = recommendation_service.generate_recommendations(
            user_id=user_id,
            limit=limit,
            strategy=strategy,
            filters=filters if filters else None
        )
        
        # Convert to response format
        recommendations = []
        for rec in result['recommendations']:
            recommendations.append(RecommendationItem(
                resource_id=rec['resource_id'],
                title=rec['title'],
                score=rec['score'],
                strategy=rec['strategy'],
                scores=RecommendationScores(**rec['scores']),
                rank=rec['rank'],
                novelty_score=rec['novelty_score'],
                view_count=rec['view_count']
            ))
        
        metadata = RecommendationMetadata(**result['metadata'])
        
        return RecommendationsResponse(
            recommendations=recommendations,
            metadata=metadata
        )
    
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ValueError in get_recommendations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_recommendations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def track_interaction(
    request: InteractionRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Track a user-resource interaction.
    
    Args:
        request: InteractionRequest with interaction details
        db: Database session
        
    Returns:
        InteractionResponse with interaction details
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)
        
        # Parse resource_id
        try:
            resource_id = UUID(request.resource_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resource_id format"
            )
        
        # Track interaction
        profile_service = _get_user_profile_service(db)
        interaction = profile_service.track_interaction(
            user_id=user_id,
            resource_id=resource_id,
            interaction_type=request.interaction_type,
            dwell_time=request.dwell_time,
            scroll_depth=request.scroll_depth,
            session_id=request.session_id,
            rating=request.rating
        )
        
        return InteractionResponse(
            interaction_id=str(interaction.id),
            user_id=str(interaction.user_id),
            resource_id=str(interaction.resource_id),
            interaction_type=interaction.interaction_type,
            interaction_strength=interaction.interaction_strength,
            is_positive=bool(interaction.is_positive),
            created_at=interaction.created_at
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking interaction: {str(e)}"
        )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    db: Session = Depends(get_sync_db),
):
    """
    Get user profile settings.
    
    Args:
        db: Database session
        
    Returns:
        ProfileResponse with user profile settings
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)
        
        # Get profile
        profile_service = _get_user_profile_service(db)
        profile = profile_service.get_or_create_profile(user_id)
        
        # Parse JSON fields
        import json
        research_domains = None
        if profile.research_domains:
            try:
                research_domains = json.loads(profile.research_domains)
            except json.JSONDecodeError:
                research_domains = None
        
        excluded_sources = None
        if profile.excluded_sources:
            try:
                excluded_sources = json.loads(profile.excluded_sources)
            except json.JSONDecodeError:
                excluded_sources = None
        
        return ProfileResponse(
            user_id=str(profile.user_id),
            diversity_preference=profile.diversity_preference,
            novelty_preference=profile.novelty_preference,
            recency_bias=profile.recency_bias,
            research_domains=research_domains,
            active_domain=profile.active_domain,
            excluded_sources=excluded_sources,
            total_interactions=profile.total_interactions,
            last_active_at=profile.last_active_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}"
        )


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Update user profile settings.
    
    Args:
        request: ProfileUpdateRequest with updated settings
        db: Database session
        
    Returns:
        ProfileResponse with updated profile settings
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)
        
        # Update profile
        profile_service = _get_user_profile_service(db)
        profile = profile_service.update_profile_settings(
            user_id=user_id,
            diversity_preference=request.diversity_preference,
            novelty_preference=request.novelty_preference,
            recency_bias=request.recency_bias,
            excluded_sources=request.excluded_sources,
            research_domains=request.research_domains,
            active_domain=request.active_domain
        )
        
        # Parse JSON fields
        import json
        research_domains = None
        if profile.research_domains:
            try:
                research_domains = json.loads(profile.research_domains)
            except json.JSONDecodeError:
                research_domains = None
        
        excluded_sources = None
        if profile.excluded_sources:
            try:
                excluded_sources = json.loads(profile.excluded_sources)
            except json.JSONDecodeError:
                excluded_sources = None
        
        return ProfileResponse(
            user_id=str(profile.user_id),
            diversity_preference=profile.diversity_preference,
            novelty_preference=profile.novelty_preference,
            recency_bias=profile.recency_bias,
            research_domains=research_domains,
            active_domain=profile.active_domain,
            excluded_sources=excluded_sources,
            total_interactions=profile.total_interactions,
            last_active_at=profile.last_active_at
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )


@router.post("/recommendations/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Submit feedback for a recommendation.
    
    Args:
        request: FeedbackRequest with feedback details
        db: Database session
        
    Returns:
        FeedbackResponse with feedback details
    """
    try:
        # Get current user
        user_id = _get_current_user_id(db)
        
        # Parse resource_id
        try:
            resource_id = UUID(request.resource_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resource_id format"
            )
        
        # Create feedback record
        feedback = RecommendationFeedback(
            user_id=user_id,
            resource_id=resource_id,
            recommendation_strategy="hybrid",  # Default, could be tracked from recommendation context
            recommendation_score=0.0,  # Would be populated from recommendation context
            rank_position=0,  # Would be populated from recommendation context
            was_clicked=1 if request.was_clicked else 0,
            was_useful=1 if request.was_useful else 0 if request.was_useful is not None else None,
            feedback_notes=request.feedback_notes,
            feedback_at=datetime.utcnow() if request.was_useful is not None or request.feedback_notes else None
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return FeedbackResponse(
            feedback_id=str(feedback.id),
            user_id=str(feedback.user_id),
            resource_id=str(feedback.resource_id),
            was_clicked=bool(feedback.was_clicked),
            was_useful=bool(feedback.was_useful) if feedback.was_useful is not None else None,
            created_at=feedback.created_at
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/recommendations/metrics")
async def get_performance_metrics():
    """
    Get performance metrics for the recommendation system.
    
    Returns:
        Dictionary with performance metrics including:
        - Cache hit rate
        - Method execution times
        - Slow query count
        - Recommendation generation metrics
    """
    try:
        summary = metrics.get_summary()
        return {
            "status": "success",
            "metrics": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metrics: {str(e)}"
        )
