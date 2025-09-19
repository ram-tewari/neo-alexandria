"""
Neo Alexandria 2.0 - Resource Data Models and Validation

This module defines Pydantic schemas for resource data validation and serialization.
It provides comprehensive models for resource creation, updates, and responses with
proper validation rules and field constraints.

Related files:
- app/database/models.py: SQLAlchemy models that these schemas represent
- app/routers/resources.py: API endpoints that use these schemas
- app/services/resource_service.py: Business logic that validates with these schemas

Schemas:
- ResourceBase: Common fields for all resource operations
- ResourceCreate: Schema for creating new resources
- ResourceUpdate: Schema for updating existing resources
- ResourceResponse: Schema for API responses
- ResourceListResponse: Schema for paginated resource lists
"""

import uuid
from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


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
    quality_score: Optional[float] = None


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
    quality_score: float  # Always present
    # Expose computed URL; map from source when present
    url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Ingestion workflow fields
    ingestion_status: Literal["pending", "processing", "completed", "failed"]
    ingestion_error: Optional[str] = None
    ingestion_started_at: Optional[datetime] = None
    ingestion_completed_at: Optional[datetime] = None


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
