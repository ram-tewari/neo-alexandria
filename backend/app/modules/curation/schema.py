"""
Neo Alexandria 2.0 - Curation Module Schemas

This module defines Pydantic schemas for curation operations including
review queue management, batch operations, and quality analysis.

Related files:
- app/modules/curation/router.py: API endpoints using these schemas
- app/modules/curation/service.py: Business logic processing these schemas

Schemas:
- ReviewQueueParams: Parameters for review queue queries
- ReviewQueueResponse: Response containing review queue items
- BatchUpdateRequest: Request for batch updating resources
- BatchUpdateResult: Result of batch update operation
- QualityAnalysisResponse: Detailed quality analysis for a resource
- LowQualityResponse: Response containing low-quality resources
- BulkQualityCheckRequest: Request for bulk quality checking
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReviewQueueParams(BaseModel):
    """Parameters for review queue queries."""
    
    threshold: Optional[float] = None
    include_unread_only: bool = False
    limit: int = Field(default=25, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ReviewQueueResponse(BaseModel):
    """Response containing review queue items."""
    
    items: List[Dict[str, Any]]  # Generic resource data
    total: int


class BatchUpdateRequest(BaseModel):
    """Request for batch updating resources."""
    
    resource_ids: List[uuid.UUID] = Field(min_length=1)
    updates: Dict[str, Any]  # Generic update data


class BatchUpdateResult(BaseModel):
    """Result of batch update operation."""
    
    updated_count: int
    failed_ids: List[uuid.UUID] = Field(default_factory=list)


class QualityAnalysisResponse(BaseModel):
    """Detailed quality analysis for a resource."""
    
    resource_id: str
    metadata_completeness: float
    readability: dict
    source_credibility: float
    content_depth: float
    overall_quality: float
    quality_level: str
    suggestions: List[str]


class LowQualityResponse(BaseModel):
    """Response containing low-quality resources."""
    
    items: List[Dict[str, Any]]  # Generic resource data
    total: int


class BulkQualityCheckRequest(BaseModel):
    """Request for bulk quality checking."""
    
    resource_ids: List[str]


class BatchReviewRequest(BaseModel):
    """Request for batch review operations."""
    
    resource_ids: List[uuid.UUID] = Field(min_length=1)
    action: str = Field(pattern="^(approve|reject|flag)$")
    curator_id: str
    comment: Optional[str] = None


class BatchTagRequest(BaseModel):
    """Request for batch tagging operations."""
    
    resource_ids: List[uuid.UUID] = Field(min_length=1)
    tags: List[str] = Field(min_length=1)


class AssignCuratorRequest(BaseModel):
    """Request for curator assignment."""
    
    resource_ids: List[uuid.UUID] = Field(min_length=1)
    curator_id: str


class EnhancedReviewQueueParams(BaseModel):
    """Enhanced parameters for review queue queries."""
    
    threshold: Optional[float] = None
    status: Optional[str] = None  # pending, approved, rejected, assigned
    assigned_curator: Optional[str] = None
    min_quality: Optional[float] = None
    max_quality: Optional[float] = None
    include_unread_only: bool = False
    limit: int = Field(default=25, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
