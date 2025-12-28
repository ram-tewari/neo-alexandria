"""
Authority Module Schemas

Pydantic schemas for authority control API requests and responses.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SubjectSuggestionResponse(BaseModel):
    """Response model for subject suggestions."""
    suggestions: List[str] = Field(description="List of suggested subject strings")


class ClassificationTreeNode(BaseModel):
    """Classification tree node model."""
    code: str = Field(description="Classification code (e.g., '000', '400')")
    name: str = Field(description="Human-readable name of the classification")
    description: Optional[str] = Field(None, description="Detailed description of the classification")
    keywords: List[str] = Field(default_factory=list, description="Keywords associated with this classification")
    children: List[ClassificationTreeNode] = Field(default_factory=list, description="Child classification nodes")


class ClassificationTreeResponse(BaseModel):
    """Response model for classification tree."""
    tree: List[ClassificationTreeNode] = Field(description="Top-level classification nodes")


# Enable forward references for recursive model
ClassificationTreeNode.model_rebuild()
