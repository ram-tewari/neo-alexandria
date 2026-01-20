"""
Taxonomy Schemas

Pydantic schemas for taxonomy and classification requests/responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    """Schema for creating a category."""

    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    allow_resources: bool = True


class CategoryResponse(BaseModel):
    """Schema for category response."""

    id: str
    name: str
    slug: str
    parent_id: Optional[str] = None
    level: int
    path: str
    description: Optional[str] = None
    allow_resources: bool


class ClassifyRequest(BaseModel):
    """Schema for classification request."""

    resource_id: str
    text: str


class UncertaintyResponse(BaseModel):
    """Schema for uncertain predictions response."""

    threshold: float
    count: int
    resource_ids: List[str]
