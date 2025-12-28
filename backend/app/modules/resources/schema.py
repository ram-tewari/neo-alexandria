"""
Neo Alexandria 2.0 - Resource Data Models and Validation

This module defines Pydantic schemas for resource data validation and serialization.
It provides comprehensive models for resource creation, updates, and responses with
proper validation rules and field constraints.

Related files:
- model.py: SQLAlchemy models that these schemas represent
- router.py: API endpoints that use these schemas
- service.py: Business logic that validates with these schemas

Schemas:
- ResourceBase: Common fields for all resource operations
- ResourceCreate: Schema for creating new resources
- ResourceUpdate: Schema for updating existing resources
- ResourceResponse: Schema for API responses
- ResourceListResponse: Schema for paginated resource lists
"""

import uuid
from datetime import datetime
from typing import List, Optional, Literal, Union, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_serializer


# Query parameter schemas
class PageParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(default=25, ge=1, le=100, description="Items per page")


class SortOrder(str, Enum):
    """Sort order enum."""
    ASC = "asc"
    DESC = "desc"


class SortParams(BaseModel):
    """Sorting parameters."""
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")


class ResourceFilters(BaseModel):
    """Resource filtering parameters."""
    type: Optional[str] = Field(default=None, description="Filter by resource type")
    format: Optional[str] = Field(default=None, description="Filter by format")
    language: Optional[str] = Field(default=None, description="Filter by language")
    read_status: Optional[Literal["unread", "in_progress", "completed", "archived"]] = Field(
        default=None, description="Filter by read status"
    )
    min_quality: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum quality score")
    subject: Optional[str] = Field(default=None, description="Filter by subject")
    creator: Optional[str] = Field(default=None, description="Filter by creator")


class ResourceBase(BaseModel):
    """Base resource schema with common fields."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    publisher: Optional[str] = None
    contributor: Optional[str] = None
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    type: Optional[str] = None
    format: Optional[str] = None
    identifier: Optional[str] = None
    source: Optional[str] = None
    language: Optional[str] = None
    coverage: Optional[str] = None
    rights: Optional[str] = None
    subject: List[str] = Field(default_factory=list)
    relation: List[str] = Field(default_factory=list)
    classification_code: Optional[str] = None
    read_status: Optional[Literal["unread", "in_progress", "completed", "archived"]] = None
    quality_score: Optional[Union[float, Any]] = None


class ResourceCreate(ResourceBase):
    """Schema for creating a new resource."""
    
    title: str  # Required for creation


class ResourceUpdate(ResourceBase):
    """Schema for updating an existing resource.
    
    All fields are optional for partial updates.
    """
    pass


class ResourceRead(ResourceBase):
    """Schema for reading a resource (includes all fields)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    title: str  # Always present in read
    subject: List[str]  # Always present (default to empty list)
    relation: List[str]  # Always present (default to empty list)
    read_status: Literal["unread", "in_progress", "completed", "archived"]  # Always present
    quality_score: Union[float, Any]  # Can be float or QualityScore domain object
    # Expose computed URL; map from source when present
    url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Ingestion workflow fields
    ingestion_status: Literal["pending", "processing", "completed", "failed"]
    ingestion_error: Optional[str] = None
    ingestion_started_at: Optional[datetime] = None
    ingestion_completed_at: Optional[datetime] = None
    
    @field_serializer('quality_score')
    def serialize_quality_score(self, quality_score: Union[float, Any], _info) -> float:
        """Serialize quality_score to float for API responses.
        
        Handles both float values (from database) and QualityScore domain objects.
        """
        # If it's already a float, return it
        if isinstance(quality_score, (int, float)):
            return float(quality_score)
        
        # If it's a QualityScore domain object, get overall_score
        if hasattr(quality_score, 'overall_score'):
            return quality_score.overall_score()
        
        # If it has a to_dict method, extract overall_score from dict
        if hasattr(quality_score, 'to_dict'):
            return quality_score.to_dict().get('overall_score', 0.0)
        
        # Fallback to 0.0 if we can't determine the score
        return 0.0


class ResourceInDB(ResourceRead):
    """Schema representing resource as stored in database.
    
    Identical to ResourceRead but makes the distinction clear.
    """
    pass


class ResourceStatus(BaseModel):
    """Lightweight status payload for ingestion polling."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ingestion_status: Literal["pending", "processing", "completed", "failed"]
    ingestion_error: Optional[str] = None
    ingestion_started_at: Optional[datetime] = None
    ingestion_completed_at: Optional[datetime] = None
