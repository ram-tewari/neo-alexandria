"""
Neo Alexandria 2.0 - Graph Schemas for Phase 5

Pydantic models for the hybrid knowledge graph system that represents
relationships between resources based on vector similarity, shared subjects,
and classification codes.

Related files:
- app/services/graph_service.py: Business logic using these schemas
- app/routers/graph.py: API endpoints returning these schemas
- app/config/settings.py: Graph configuration settings
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """
    A node in the knowledge graph representing a resource.
    
    Attributes:
        id: Unique resource identifier
        title: Human-readable title of the resource
        type: Resource type (e.g., "article", "book", "webpage")
        classification_code: UDC-inspired classification code if assigned
    """
    
    id: UUID = Field(..., description="Unique resource identifier")
    title: str = Field(..., description="Human-readable title of the resource")
    type: Optional[str] = Field(None, description="Resource type (e.g., 'article', 'book', 'webpage')")
    classification_code: Optional[str] = Field(None, description="UDC-inspired classification code if assigned")


class GraphEdgeDetails(BaseModel):
    """
    Detailed information about why two nodes are connected.
    
    Provides transparency for the UI to explain connection reasoning,
    showing the specific factors that contributed to the edge weight.
    
    Attributes:
        connection_type: Type of connection (e.g., "semantic", "topical", "classification")
        vector_similarity: Cosine similarity score between embeddings (if applicable)
        shared_subjects: List of canonical subjects shared between the resources
    """
    
    connection_type: str = Field(..., description="Type of connection (e.g., 'semantic', 'topical', 'classification')")
    vector_similarity: Optional[float] = Field(None, description="Cosine similarity score between embeddings (0.0-1.0)")
    shared_subjects: List[str] = Field(default_factory=list, description="List of canonical subjects shared between resources")


class GraphEdge(BaseModel):
    """
    A weighted edge between two nodes in the knowledge graph.
    
    Represents the hybrid-scored relationship between two resources,
    combining vector similarity, subject overlap, and classification matching.
    
    Attributes:
        source: Source node UUID
        target: Target node UUID  
        weight: Combined hybrid weight score (0.0-1.0)
        details: Detailed information about the connection
    """
    
    source: UUID = Field(..., description="Source node UUID")
    target: UUID = Field(..., description="Target node UUID")
    weight: float = Field(..., ge=0.0, le=1.0, description="Combined hybrid weight score (0.0-1.0)")
    details: GraphEdgeDetails = Field(..., description="Detailed information about the connection")


class KnowledgeGraph(BaseModel):
    """
    A complete knowledge graph containing nodes and their relationships.
    
    Used for both the mind-map view (neighbors of a specific resource)
    and the global overview (strongest connections across the library).
    
    Attributes:
        nodes: List of graph nodes (resources)
        edges: List of weighted edges between nodes
    """
    
    nodes: List[GraphNode] = Field(default_factory=list, description="List of graph nodes (resources)")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of weighted edges between nodes")
    
    class Config:
        """Pydantic configuration for proper JSON serialization"""
        json_encoders = {
            UUID: str
        }
