"""
Neo Alexandria 2.0 - Annotation Schemas (Phase 7.5)

This module defines Pydantic schemas for annotation-related API requests and responses.

Related files:
- app/database/models.py: Annotation model
- app/routers/annotations.py: Annotation API endpoints
- app/services/annotation_service.py: Annotation business logic
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class AnnotationCreate(BaseModel):
    """Schema for creating a new annotation."""
    start_offset: int = Field(..., ge=0, description="Start character offset (zero-indexed, non-negative)")
    end_offset: int = Field(..., ge=0, description="End character offset (zero-indexed, non-negative)")
    highlighted_text: str = Field(..., min_length=1, description="Selected text content")
    note: Optional[str] = Field(None, max_length=10000, description="User note or commentary (max 10,000 chars)")
    tags: Optional[List[str]] = Field(None, max_items=20, description="Tags for organization (max 20)")
    color: Optional[str] = Field("#FFFF00", pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code (default: yellow)")
    collection_ids: Optional[List[str]] = Field(None, description="Associated collection UUIDs")
    
    @field_validator('end_offset')
    @classmethod
    def validate_offsets(cls, end_offset: int, info) -> int:
        """Validate that start_offset < end_offset."""
        start_offset = info.data.get('start_offset')
        if start_offset is not None and start_offset >= end_offset:
            raise ValueError('start_offset must be less than end_offset')
        return end_offset
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, tags: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tag length and content."""
        if tags:
            for tag in tags:
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
                if not tag.strip():
                    raise ValueError('Tags cannot be empty or whitespace only')
        return tags


class AnnotationUpdate(BaseModel):
    """Schema for updating an existing annotation."""
    note: Optional[str] = Field(None, max_length=10000, description="User note or commentary")
    tags: Optional[List[str]] = Field(None, max_items=20, description="Tags for organization")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")
    is_shared: Optional[bool] = Field(None, description="Whether annotation is publicly visible")
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, tags: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tag length and content."""
        if tags:
            for tag in tags:
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
                if not tag.strip():
                    raise ValueError('Tags cannot be empty or whitespace only')
        return tags


class AnnotationResponse(BaseModel):
    """Schema for annotation API responses."""
    id: str = Field(..., description="Annotation UUID")
    resource_id: str = Field(..., description="Resource UUID")
    user_id: str = Field(..., description="Owner user ID")
    start_offset: int = Field(..., description="Start character offset")
    end_offset: int = Field(..., description="End character offset")
    highlighted_text: str = Field(..., description="Selected text content")
    note: Optional[str] = Field(None, description="User note or commentary")
    tags: Optional[List[str]] = Field(None, description="Tags for organization")
    color: str = Field(..., description="Hex color code")
    context_before: Optional[str] = Field(None, description="50 characters before highlight")
    context_after: Optional[str] = Field(None, description="50 characters after highlight")
    is_shared: bool = Field(..., description="Whether annotation is publicly visible")
    collection_ids: Optional[List[str]] = Field(None, description="Associated collection UUIDs")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    resource_title: Optional[str] = Field(None, description="Resource title (for list views)")
    
    class Config:
        from_attributes = True


class AnnotationListResponse(BaseModel):
    """Response for annotation list endpoints."""
    items: List[AnnotationResponse] = Field(default_factory=list)
    total: int = Field(..., description="Total count of annotations")
    page: Optional[int] = Field(None, description="Current page number")
    limit: Optional[int] = Field(None, description="Items per page")


class AnnotationSearchResult(AnnotationResponse):
    """Annotation search result with relevance score."""
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Semantic similarity score")


class AnnotationSearchResponse(BaseModel):
    """Response for annotation search endpoints."""
    items: List[AnnotationSearchResult] = Field(default_factory=list)
    total: int = Field(..., description="Total count of matching annotations")
    query: str = Field(..., description="Search query")
