"""
Neo Alexandria 2.0 - Citation Schemas (Phase 6)

This module defines Pydantic schemas for citation-related API requests and responses.

Related files:
- app/database/models.py: Citation model
- app/routers/citations.py: Citation API endpoints
- app/services/citation_service.py: Citation business logic
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CitationBase(BaseModel):
    """Base schema for citation data."""
    source_resource_id: str = Field(..., description="UUID of the citing resource")
    target_url: str = Field(..., description="URL being cited")
    citation_type: str = Field(default="reference", description="Type of citation: reference, dataset, code, general")
    context_snippet: Optional[str] = Field(None, description="Text context around the citation")
    position: Optional[int] = Field(None, description="Position in the document")


class CitationCreate(CitationBase):
    """Schema for creating a new citation."""
    target_resource_id: Optional[str] = Field(None, description="UUID of the cited resource if internal")


class CitationResponse(CitationBase):
    """Schema for citation API responses."""
    id: str = Field(..., description="Citation UUID")
    target_resource_id: Optional[str] = Field(None, description="UUID of the cited resource if resolved")
    importance_score: Optional[float] = Field(None, description="PageRank importance score")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ResourceSummary(BaseModel):
    """Minimal resource information for citation responses."""
    id: str
    title: str
    source: Optional[str] = None
    
    class Config:
        from_attributes = True


class CitationWithResource(CitationResponse):
    """Citation response with embedded resource information."""
    target_resource: Optional[ResourceSummary] = None


class ResourceCitationsResponse(BaseModel):
    """Response for resource citations endpoint."""
    resource_id: str
    outbound: List[CitationWithResource] = Field(default_factory=list, description="Citations from this resource")
    inbound: List[CitationWithResource] = Field(default_factory=list, description="Citations to this resource")
    counts: dict = Field(default_factory=dict, description="Citation counts")


class GraphNode(BaseModel):
    """Node in citation graph."""
    id: str = Field(..., description="Resource UUID")
    title: str = Field(..., description="Resource title")
    type: str = Field(..., description="Node type: source, cited, citing")


class GraphEdge(BaseModel):
    """Edge in citation graph."""
    source: str = Field(..., description="Source resource UUID")
    target: str = Field(..., description="Target resource UUID")
    type: str = Field(..., description="Citation type")


class CitationGraphResponse(BaseModel):
    """Response for citation graph endpoint."""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class CitationExtractionRequest(BaseModel):
    """Request to trigger citation extraction."""
    resource_id: str = Field(..., description="UUID of resource to extract citations from")


class CitationExtractionResponse(BaseModel):
    """Response for citation extraction trigger."""
    status: str = Field(..., description="Task status: queued, processing, completed, failed")
    resource_id: str = Field(..., description="Resource UUID")
    message: Optional[str] = None


class CitationResolutionResponse(BaseModel):
    """Response for citation resolution."""
    status: str = Field(..., description="Task status")
    resolved_count: Optional[int] = Field(None, description="Number of citations resolved")


class ImportanceComputationResponse(BaseModel):
    """Response for importance score computation."""
    status: str = Field(..., description="Task status")
    computed_count: Optional[int] = Field(None, description="Number of scores computed")
