"""
Graph Module

This module handles knowledge graph, citations, and discovery functionality.
It provides graph-based relationship analysis, citation network extraction,
and literature-based discovery (LBD) capabilities.

Public Interface:
- graph_router: Main graph endpoints
- citations_router: Citation network endpoints
- discovery_router: LBD and hypothesis discovery endpoints
- GraphService: Core graph operations
- AdvancedGraphService: Advanced graph intelligence
- GraphEmbeddingsService: Graph embedding generation
- CitationService: Citation extraction and analysis
- LBDService: Literature-based discovery

Events Emitted:
- citation.extracted: When citations are extracted from a resource
- graph.updated: When the knowledge graph is updated
- hypothesis.discovered: When LBD discovers new hypotheses

Events Subscribed:
- resource.created: Extract citations and add to graph
- resource.deleted: Remove from graph and update relationships
"""

__version__ = "1.0.0"
__domain__ = "graph"

# Import routers
from app.modules.graph.router import router as graph_router
from app.modules.graph.citations_router import router as citations_router
from app.modules.graph.discovery_router import router as discovery_router

# Import services
from app.modules.graph.service import (
    GraphService,
    find_hybrid_neighbors,
    generate_global_overview,
    cosine_similarity,
    compute_hybrid_weight,
)
from app.modules.graph.advanced_service import GraphService as AdvancedGraphService
from app.modules.graph.embeddings import GraphEmbeddingsService
from app.modules.graph.citations import CitationService
from app.modules.graph.discovery import LBDService

# Import schemas
from app.modules.graph.schema import (
    # Graph schemas
    GraphNode,
    GraphEdge,
    GraphEdgeDetails,
    KnowledgeGraph,
    # Citation schemas
    CitationBase,
    CitationCreate,
    CitationResponse,
    CitationWithResource,
    ResourceCitationsResponse,
    CitationGraphResponse,
    CitationExtractionRequest,
    CitationExtractionResponse,
    CitationResolutionResponse,
    ImportanceComputationResponse,
    # Discovery schemas
    OpenDiscoveryHypothesis,
    OpenDiscoveryResponse,
    ClosedDiscoveryRequest,
    ClosedDiscoveryPath,
    ClosedDiscoveryResponse,
    NeighborResponse,
    NeighborsResponse,
    HypothesisValidation,
    HypothesisResponse,
    HypothesesListResponse,
)

# Import models
from app.modules.graph.model import (
    Citation,
    GraphEdge as GraphEdgeModel,
    GraphEmbedding,
    DiscoveryHypothesis,
)

# Import event handlers
from app.modules.graph.handlers import register_handlers

__all__ = [
    # Version and metadata
    "__version__",
    "__domain__",
    
    # Routers
    "graph_router",
    "citations_router",
    "discovery_router",
    
    # Services
    "GraphService",
    "AdvancedGraphService",
    "GraphEmbeddingsService",
    "CitationService",
    "LBDService",
    
    # Service functions
    "find_hybrid_neighbors",
    "generate_global_overview",
    "cosine_similarity",
    "compute_hybrid_weight",
    
    # Schemas - Graph
    "GraphNode",
    "GraphEdge",
    "GraphEdgeDetails",
    "KnowledgeGraph",
    
    # Schemas - Citations
    "CitationBase",
    "CitationCreate",
    "CitationResponse",
    "CitationWithResource",
    "ResourceCitationsResponse",
    "CitationGraphResponse",
    "CitationExtractionRequest",
    "CitationExtractionResponse",
    "CitationResolutionResponse",
    "ImportanceComputationResponse",
    
    # Schemas - Discovery
    "OpenDiscoveryHypothesis",
    "OpenDiscoveryResponse",
    "ClosedDiscoveryRequest",
    "ClosedDiscoveryPath",
    "ClosedDiscoveryResponse",
    "NeighborResponse",
    "NeighborsResponse",
    "HypothesisValidation",
    "HypothesisResponse",
    "HypothesesListResponse",
    
    # Models
    "Citation",
    "GraphEdgeModel",
    "GraphEmbedding",
    "DiscoveryHypothesis",
    
    # Event handlers
    "register_handlers",
]
