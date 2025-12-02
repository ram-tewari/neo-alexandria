"""
Neo Alexandria 2.0 - Collection Data Models and Validation

This module defines Pydantic schemas for collection data validation and serialization.
It provides comprehensive models for collection creation, updates, and responses with
proper validation rules and field constraints.

Related files:
- model.py: SQLAlchemy models that these schemas represent
- router.py: API endpoints that use these schemas
- service.py: Business logic that validates with these schemas

Schemas:
- CollectionBase: Common fields for all collection operations
- CollectionCreate: Schema for creating new collections
- CollectionUpdate: Schema for updating existing collections
- CollectionResponse: Schema for API responses
- CollectionResourcesUpdate: Schema for batch add/remove resources
"""

import uuid
from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class CollectionBase(BaseModel):
    """Base collection schema with common fields."""
    
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    visibility: Optional[Literal["private", "shared", "public"]] = None
    parent_id: Optional[uuid.UUID] = None


class CollectionCreate(CollectionBase):
    """Schema for creating a new collection."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Collection name")
    owner_id: str = Field(..., min_length=1, max_length=255, description="Owner user ID")
    visibility: Literal["private", "shared", "public"] = Field(default="private", description="Collection visibility")


class CollectionUpdate(CollectionBase):
    """Schema for updating an existing collection.
    
    All fields are optional for partial updates.
    """
    pass


class ResourceSummary(BaseModel):
    """Lightweight resource summary for collection responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    creator: Optional[str] = None
    type: Optional[str] = None
    quality_score: float
    created_at: datetime


class CollectionRead(CollectionBase):
    """Schema for reading a collection (includes all fields)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    owner_id: str
    visibility: Literal["private", "shared", "public"]
    parent_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    # Resource count (computed)
    resource_count: int = 0


class CollectionWithResources(CollectionRead):
    """Schema for collection with populated resources."""
    
    resources: List[ResourceSummary] = Field(default_factory=list)


class CollectionResourcesUpdate(BaseModel):
    """Schema for batch add/remove resources from collection."""
    
    add_resource_ids: List[uuid.UUID] = Field(default_factory=list, description="Resource IDs to add")
    remove_resource_ids: List[uuid.UUID] = Field(default_factory=list, description="Resource IDs to remove")


class CollectionRecommendation(BaseModel):
    """Schema for collection-based recommendations."""
    
    resource_id: uuid.UUID
    title: str
    description: Optional[str] = None
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity to collection")
    reason: str = Field(..., description="Explanation for recommendation")


class CollectionRecommendationsResponse(BaseModel):
    """Schema for collection recommendations response."""
    
    collection_id: uuid.UUID
    collection_name: str
    recommendations: List[CollectionRecommendation]
    total: int
