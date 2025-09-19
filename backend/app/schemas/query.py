"""
Neo Alexandria 2.0 - Query Parameter Schemas

This module defines Pydantic schemas for query parameters used across the API.
It provides validation and type safety for filtering, pagination, sorting, and
batch operations.

Related files:
- app/routers/resources.py: Uses these schemas for resource queries
- app/routers/curation.py: Uses these schemas for curation operations
- app/services/resource_service.py: Business logic that processes these queries

Schemas:
- ResourceFilters: Filtering parameters for resource queries
- ResourceSort: Sorting parameters for resource lists
- PaginationParams: Pagination parameters for list endpoints
- BatchUpdateRequest: Schema for batch update operations
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from .resource import ResourceUpdate


class PageParams(BaseModel):
    limit: int = Field(default=25, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SortParams(BaseModel):
    sort_by: Literal["created_at", "updated_at", "quality_score", "title"] = "created_at"
    sort_dir: Literal["asc", "desc"] = "desc"


class ResourceFilters(BaseModel):
    q: Optional[str] = None
    classification_code: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    read_status: Optional[Literal["unread", "in_progress", "completed", "archived"]] = None
    min_quality: Optional[float] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    updated_from: Optional[datetime] = None
    updated_to: Optional[datetime] = None
    subject_any: Optional[List[str]] = None
    subject_all: Optional[List[str]] = None

    @field_validator("subject_any", "subject_all")
    @classmethod
    def empty_to_none(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and len(v) == 0:
            return None
        return v


class BatchUpdateRequest(BaseModel):
    resource_ids: List[uuid.UUID] = Field(min_length=1)
    updates: ResourceUpdate


class BatchUpdateResult(BaseModel):
    updated_count: int
    failed_ids: List[uuid.UUID] = Field(default_factory=list)


class ReviewQueueParams(BaseModel):
    threshold: Optional[float] = None
    include_unread_only: bool = False
    limit: int = Field(default=25, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


