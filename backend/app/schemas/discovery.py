"""
Neo Alexandria 2.0 - Discovery Schemas for Phase 10

Pydantic models for Literature-Based Discovery (LBD) API endpoints,
implementing the ABC paradigm for hypothesis generation.

Related files:
- app/services/lbd_service.py: Business logic using these schemas
- app/routers/discovery.py: API endpoints returning these schemas
- app/database/models.py: DiscoveryHypothesis database model
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ResourceSummary(BaseModel):
    """
    Summary information about a resource in discovery results.
    
    Attributes:
        id: Unique resource identifier
        title: Human-readable title
        type: Resource type (e.g., "article", "book")
        publication_year: Year of publication if available
        quality_overall: Overall quality score from Phase 9 (0.0-1.0)
    """
    
    id: str = Field(..., description="Unique resource identifier")
    title: str = Field(..., description="Human-readable title")
    type: Optional[str] = Field(None, description="Resource type (e.g., 'article', 'book')")
    publication_year: Optional[int] = Field(None, description="Year of publication")
    quality_overall: Optional[float] = Field(None, description="Overall quality score (0.0-1.0)")


class PathInfo(BaseModel):
    """
    Information about a specific path in the graph.
    
    Attributes:
        b_id: Intermediate resource UUID
        weight_ab: Edge weight from A to B
        weight_bc: Edge weight from B to C
        path_strength: Product of edge weights
        path: List of resource UUIDs in path
    """
    
    b_id: str = Field(..., description="Intermediate resource UUID")
    weight_ab: float = Field(..., description="Edge weight from A to B")
    weight_bc: float = Field(..., description="Edge weight from B to C")
    path_strength: float = Field(..., description="Product of edge weights")
    path: List[str] = Field(..., description="List of resource UUIDs in path")


class OpenDiscoveryHypothesis(BaseModel):
    """
    A hypothesis discovered through open discovery (A→B→C pattern).
    
    Represents a potential connection between the starting resource A
    and a discovered resource C through intermediate resources B.
    
    Attributes:
        c_resource: Target resource discovered
        b_resources: List of intermediate resources connecting A to C
        plausibility_score: Combined plausibility score (0.0-1.0)
        path_strength: Product of edge weights along best path
        common_neighbors: Count of shared neighbors between A and C
        semantic_similarity: Cosine similarity of embeddings (0.0-1.0)
        path_length: Number of hops in path
        paths: Detailed information about all paths to C
    """
    
    c_resource: ResourceSummary = Field(..., description="Target resource discovered")
    b_resources: List[ResourceSummary] = Field(..., description="Intermediate resources connecting A to C")
    plausibility_score: float = Field(..., ge=0.0, le=1.0, description="Combined plausibility score")
    path_strength: float = Field(..., description="Product of edge weights along best path")
    common_neighbors: int = Field(..., description="Count of shared neighbors between A and C")
    semantic_similarity: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity of embeddings")
    path_length: int = Field(..., description="Number of hops in path")
    paths: Optional[List[PathInfo]] = Field(None, description="Detailed information about all paths")


class OpenDiscoveryResponse(BaseModel):
    """
    Response for open discovery endpoint.
    
    Attributes:
        hypotheses: List of discovered hypotheses ranked by plausibility
        total_count: Total number of hypotheses found
    """
    
    hypotheses: List[OpenDiscoveryHypothesis] = Field(..., description="List of discovered hypotheses")
    total_count: int = Field(..., description="Total number of hypotheses found")


class ClosedDiscoveryRequest(BaseModel):
    """
    Request body for closed discovery endpoint.
    
    Attributes:
        a_resource_id: Starting resource UUID
        c_resource_id: Target resource UUID
        max_hops: Maximum number of hops to search (default 3)
    """
    
    a_resource_id: str = Field(..., description="Starting resource UUID")
    c_resource_id: str = Field(..., description="Target resource UUID")
    max_hops: int = Field(3, ge=2, le=4, description="Maximum number of hops to search")


class ClosedDiscoveryPath(BaseModel):
    """
    A path connecting two resources in closed discovery.
    
    Attributes:
        b_resources: List of intermediate resources in path
        path: List of resource UUIDs in path
        path_length: Number of hops in path
        plausibility_score: Combined plausibility score with hop penalty
        path_strength: Product of edge weights
        common_neighbors: Count of shared neighbors between A and C
        semantic_similarity: Cosine similarity of embeddings
        is_direct: True if direct A→C edge exists
        weights: List of edge weights in path
    """
    
    b_resources: List[ResourceSummary] = Field(..., description="Intermediate resources in path")
    path: List[str] = Field(..., description="List of resource UUIDs in path")
    path_length: int = Field(..., description="Number of hops in path")
    plausibility_score: float = Field(..., ge=0.0, le=1.0, description="Combined plausibility score")
    path_strength: float = Field(..., description="Product of edge weights")
    common_neighbors: int = Field(..., description="Count of shared neighbors")
    semantic_similarity: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity")
    is_direct: bool = Field(..., description="True if direct A→C edge exists")
    weights: Optional[List[float]] = Field(None, description="List of edge weights in path")


class ClosedDiscoveryResponse(BaseModel):
    """
    Response for closed discovery endpoint.
    
    Attributes:
        paths: List of paths connecting A and C, ranked by plausibility
        total_count: Total number of paths found
    """
    
    paths: List[ClosedDiscoveryPath] = Field(..., description="List of paths connecting A and C")
    total_count: int = Field(..., description="Total number of paths found")


class NeighborResponse(BaseModel):
    """
    A multi-hop neighbor with path information.
    
    Attributes:
        resource_id: Target resource UUID
        title: Resource title
        type: Resource type
        distance: Number of hops (1 or 2)
        path: List of resource UUIDs in path
        path_strength: Product of edge weights along path
        edge_types: List of edge types used in path
        score: Combined ranking score
        intermediate: Intermediate resource UUID (for 2-hop paths)
        quality: Resource quality score
        novelty: Novelty score based on node degree
    """
    
    resource_id: str = Field(..., description="Target resource UUID")
    title: str = Field(..., description="Resource title")
    type: Optional[str] = Field(None, description="Resource type")
    distance: int = Field(..., description="Number of hops")
    path: List[str] = Field(..., description="List of resource UUIDs in path")
    path_strength: float = Field(..., description="Product of edge weights")
    edge_types: List[str] = Field(..., description="List of edge types used")
    score: float = Field(..., description="Combined ranking score")
    intermediate: Optional[str] = Field(None, description="Intermediate resource UUID for 2-hop")
    quality: float = Field(..., description="Resource quality score")
    novelty: float = Field(..., description="Novelty score")


class NeighborsResponse(BaseModel):
    """
    Response for multi-hop neighbors endpoint.
    
    Attributes:
        neighbors: List of neighbors with path information
        total_count: Total number of neighbors found
    """
    
    neighbors: List[NeighborResponse] = Field(..., description="List of neighbors")
    total_count: int = Field(..., description="Total number of neighbors found")


class HypothesisValidation(BaseModel):
    """
    Request body for hypothesis validation endpoint.
    
    Attributes:
        is_valid: Whether the hypothesis is valid
        notes: Optional validation notes
    """
    
    is_valid: bool = Field(..., description="Whether the hypothesis is valid")
    notes: Optional[str] = Field(None, description="Optional validation notes")


class HypothesisResponse(BaseModel):
    """
    A stored discovery hypothesis.
    
    Attributes:
        id: Hypothesis UUID
        a_resource: Starting resource
        c_resource: Target resource
        b_resources: Intermediate resources
        hypothesis_type: Type of hypothesis ("open" or "closed")
        plausibility_score: Combined plausibility score
        path_strength: Product of edge weights
        path_length: Number of hops
        common_neighbors: Count of shared neighbors
        discovered_at: Timestamp of discovery
        is_validated: Validation status (None if not validated)
        validation_notes: Optional validation notes
    """
    
    id: str = Field(..., description="Hypothesis UUID")
    a_resource: ResourceSummary = Field(..., description="Starting resource")
    c_resource: ResourceSummary = Field(..., description="Target resource")
    b_resources: List[ResourceSummary] = Field(..., description="Intermediate resources")
    hypothesis_type: str = Field(..., description="Type of hypothesis")
    plausibility_score: float = Field(..., description="Combined plausibility score")
    path_strength: float = Field(..., description="Product of edge weights")
    path_length: int = Field(..., description="Number of hops")
    common_neighbors: int = Field(..., description="Count of shared neighbors")
    discovered_at: str = Field(..., description="Timestamp of discovery")
    is_validated: Optional[bool] = Field(None, description="Validation status")
    validation_notes: Optional[str] = Field(None, description="Validation notes")


class HypothesesListResponse(BaseModel):
    """
    Response for hypotheses list endpoint.
    
    Attributes:
        hypotheses: List of stored hypotheses
        total_count: Total number of hypotheses matching filters
        skip: Number of items skipped (pagination)
        limit: Maximum items per page
    """
    
    hypotheses: List[HypothesisResponse] = Field(..., description="List of hypotheses")
    total_count: int = Field(..., description="Total count matching filters")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
