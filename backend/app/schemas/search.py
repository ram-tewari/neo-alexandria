"""
Neo Alexandria 2.0 - Search Schemas (Phase 4)

This module defines Pydantic schemas for search functionality in Neo Alexandria 2.0.
It includes schemas for search queries, filters, results, and facets, with Phase 4
extensions for hybrid search capabilities.

Related files:
- app/services/search_service.py: Uses these schemas for search operations
- app/services/hybrid_search_methods.py: Uses SearchQuery for hybrid search
- app/routers/search.py: API endpoints that validate using these schemas
- app/schemas/resource.py: ResourceRead schema used in search results

Features:
- SearchQuery schema with hybrid_weight parameter for Phase 4
- Comprehensive filtering options (classification, language, quality, etc.)
- Faceted search results with counts and buckets
- Pagination and sorting capabilities
- Input validation and type safety
- Backward compatibility with Phase 3 search functionality
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, field_validator

from .resource import ResourceRead


class FacetBucket(BaseModel):
    key: str
    count: int


class Facets(BaseModel):
    classification_code: List[FacetBucket] = Field(default_factory=list)
    type: List[FacetBucket] = Field(default_factory=list)
    language: List[FacetBucket] = Field(default_factory=list)
    read_status: List[FacetBucket] = Field(default_factory=list)
    subject: List[FacetBucket] = Field(default_factory=list)


class SearchFilters(BaseModel):
    classification_code: Optional[List[str]] = None
    type: Optional[List[str]] = None
    language: Optional[List[str]] = None
    read_status: Optional[List[Literal["unread", "in_progress", "completed", "archived"]]] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    updated_from: Optional[datetime] = None
    updated_to: Optional[datetime] = None
    subject_any: Optional[List[str]] = None
    subject_all: Optional[List[str]] = None
    min_quality: Optional[float] = None


class SearchQuery(BaseModel):
    text: Optional[str] = None
    filters: Optional[SearchFilters] = None
    limit: int = 25
    offset: int = 0
    sort_by: Literal["relevance", "updated_at", "created_at", "quality_score", "title"] = "relevance"
    sort_dir: Literal["asc", "desc"] = "desc"
    hybrid_weight: Optional[float] = None  # 0.0=keyword only, 1.0=semantic only, None=use default

    @field_validator("limit")
    @classmethod
    def _validate_limit(cls, v: int) -> int:
        if not (1 <= v <= 100):
            raise ValueError("limit must be between 1 and 100")
        return v

    @field_validator("offset")
    @classmethod
    def _validate_offset(cls, v: int) -> int:
        if v < 0:
            raise ValueError("offset must be >= 0")
        return v

    @field_validator("hybrid_weight")
    @classmethod
    def _validate_hybrid_weight(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("hybrid_weight must be between 0.0 and 1.0")
        return v


class SearchResults(BaseModel):
    total: int
    items: List[ResourceRead]
    facets: Facets
    snippets: dict[str, str] = Field(default_factory=dict)


