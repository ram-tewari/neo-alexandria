"""
Recommendations Schemas

Pydantic models for recommendation requests and responses.

This module consolidates schemas from:
- schemas/recommendation.py (Phase 5.5 basic schemas)
- Additional schemas defined in routers/recommendations.py (Phase 11)
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


# ============================================================================
# Basic Recommendation Schemas (Phase 5.5)
# ============================================================================

class RecommendedResource(BaseModel):
    """Individual recommendation item with metadata."""
    url: str
    title: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    reasoning: List[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    """Container for multiple recommendations."""
    items: List[RecommendedResource] = Field(default_factory=list)


# ============================================================================
# Hybrid Recommendation Schemas (Phase 11)
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
    """Individual recommendation item with detailed scoring."""
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
    """Response schema for hybrid recommendations."""
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
