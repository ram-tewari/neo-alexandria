"""
Neo Alexandria 2.0 - Collection Schemas (Phase 7)

This module defines Pydantic schemas for collection-related API requests and responses.

Related files:
- app/database/models.py: Collection and CollectionResource models
- app/routers/collections.py: Collection API endpoints
- app/services/collection_service.py: Collection business logic
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CollectionBase(BaseModel):
    """Base schema for collection data."""
    name: str = Field(..., min_length=1, max_length=255, description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    visibility: str = Field(default="private", description="Access control: private, shared, or public")


class CollectionCreate(CollectionBase):
    """Schema for creating a new collection."""
    parent_id: Optional[str] = Field(None, description="Parent collection UUID for hierarchical organization")


class CollectionUpdate(BaseModel):
    """Schema for updating collection metadata."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    visibility: Optional[str] = Field(None, description="Access control: private, shared, or public")
    parent_id: Optional[str] = Field(None, description="Parent collection UUID")


class ResourceSummary(BaseModel):
    """Minimal resource information for collection responses."""
    id: str
    title: str
    quality_score: float
    classification_code: Optional[str] = None
    
    class Config:
        from_attributes = True


class CollectionResponse(CollectionBase):
    """Schema for collection API responses."""
    id: str = Field(..., description="Collection UUID")
    owner_id: str = Field(..., description="Owner user ID")
    parent_id: Optional[str] = Field(None, description="Parent collection UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    resource_count: int = Field(default=0, description="Number of resources in collection")
    
    class Config:
        from_attributes = True


class CollectionDetailResponse(CollectionResponse):
    """Detailed collection response with embedded resources."""
    resources: List[ResourceSummary] = Field(default_factory=list, description="Collection resources")
    subcollections: List[CollectionResponse] = Field(default_factory=list, description="Child collections")


class CollectionListResponse(BaseModel):
    """Response for collection list endpoint."""
    items: List[CollectionResponse] = Field(default_factory=list)
    total: int = Field(..., description="Total count of collections")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")


class ResourceMembershipRequest(BaseModel):
    """Request to add or remove resources from collection."""
    resource_ids: List[str] = Field(..., min_items=1, max_items=100, description="Resource UUIDs (max 100)")


class ResourceMembershipResponse(BaseModel):
    """Response for resource membership operations."""
    collection_id: str
    added_count: Optional[int] = None
    removed_count: Optional[int] = None
    total_resources: int


class RecommendationItem(BaseModel):
    """Recommended resource or collection."""
    id: str
    title: str
    type: str = Field(..., description="Type: resource or collection")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    description: Optional[str] = None
    quality_score: Optional[float] = None


class CollectionRecommendationsResponse(BaseModel):
    """Response for collection-based recommendations."""
    collection_id: str
    resource_recommendations: List[RecommendationItem] = Field(default_factory=list)
    collection_recommendations: List[RecommendationItem] = Field(default_factory=list)
