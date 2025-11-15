"""
Neo Alexandria 2.0 - Graph API Router for Phase 5

Provides REST endpoints for the hybrid knowledge graph system, enabling
mind-map neighbor exploration and global overview analysis.

Related files:
- app/services/graph_service.py: Core graph computation logic
- app/schemas/graph.py: Pydantic response models
- app/config/settings.py: Graph configuration settings
"""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.base import get_sync_db
from backend.app.schemas.graph import KnowledgeGraph
from backend.app.services.graph_service import (
    find_hybrid_neighbors,
    generate_global_overview,
)
from backend.app.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/graph", tags=["graph"])
settings = get_settings()


@router.get(
    "/resource/{resource_id}/neighbors",
    response_model=KnowledgeGraph,
    summary="Get hybrid neighbors for mind-map view",
    description=(
        "Returns a knowledge graph showing the most relevant neighbors for a given resource, "
        "ranked by hybrid scoring that combines vector similarity, shared subjects, and "
        "classification code matches. Suitable for mind-map visualization."
    ),
)
def get_resource_neighbors(
    resource_id: UUID,
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=20,
        description=f"Maximum number of neighbors to return (default: {settings.DEFAULT_GRAPH_NEIGHBORS})"
    ),
    db: Session = Depends(get_sync_db),
) -> KnowledgeGraph:
    """
    Get hybrid-scored neighbors for a specific resource.
    
    This endpoint provides the data needed for a mind-map visualization
    centered on the specified resource. The returned graph includes:
    - The source resource as a node
    - Its top-ranked neighbor resources as nodes  
    - Weighted edges explaining the relationships
    
    The hybrid scoring considers:
    - Vector similarity between embeddings (60% weight by default)
    - Shared canonical subjects (30% weight by default)
    - Classification code matches (10% weight by default)
    
    Args:
        resource_id: UUID of the resource to find neighbors for
        limit: Maximum number of neighbors to return
        db: Database session dependency
        
    Returns:
        KnowledgeGraph: Graph with source node and its neighbors
        
    Raises:
        HTTPException: If resource is not found or other errors occur
    """
    try:
        graph = find_hybrid_neighbors(db, resource_id, limit)
        
        # Check if source resource was found (empty graph means resource not found)
        if not graph.nodes:
            raise HTTPException(
                status_code=404,
                detail=f"Resource with ID {resource_id} not found"
            )
        
        logger.info(
            f"Generated neighbor graph for resource {resource_id}: "
            f"{len(graph.nodes)} nodes, {len(graph.edges)} edges"
        )
        
        return graph
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating neighbor graph for {resource_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating neighbor graph"
        )


@router.get(
    "/overview",
    response_model=KnowledgeGraph,
    summary="Get global overview of strongest connections",
    description=(
        "Returns a knowledge graph showing the strongest relationships across the entire library. "
        "Combines high vector similarity pairs and significant tag overlap pairs, ranked by "
        "hybrid scoring. Suitable for global overview visualization."
    ),
)
def get_global_overview(
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description=f"Maximum number of edges to return (default: {settings.GRAPH_OVERVIEW_MAX_EDGES})"
    ),
    vector_threshold: Optional[float] = Query(
        None,
        ge=0.0,
        le=1.0,
        description=f"Minimum vector similarity threshold for candidates (default: {settings.GRAPH_VECTOR_MIN_SIM_THRESHOLD})"
    ),
    db: Session = Depends(get_sync_db),
) -> KnowledgeGraph:
    """
    Get global overview of strongest connections across the library.
    
    This endpoint provides data for a global knowledge graph visualization
    showing the most significant relationships in the entire collection.
    
    The algorithm:
    1. Finds resource pairs with high vector similarity (above threshold)
    2. Finds resource pairs with significant tag overlap
    3. Scores all candidate pairs using hybrid weighting
    4. Returns the top-weighted edges and their involved nodes
    
    Args:
        limit: Maximum number of edges to include in the overview
        vector_threshold: Minimum cosine similarity for vector-based candidates
        db: Database session dependency
        
    Returns:
        KnowledgeGraph: Graph with strongest global connections
        
    Raises:
        HTTPException: If errors occur during graph generation
    """
    try:
        graph = generate_global_overview(db, limit, vector_threshold)
        
        logger.info(
            f"Generated global overview: "
            f"{len(graph.nodes)} nodes, {len(graph.edges)} edges, "
            f"limit={limit}, threshold={vector_threshold}"
        )
        
        return graph
        
    except Exception as e:
        logger.error(f"Error generating global overview: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating global overview"
        )


@router.get(
    "/resources/{resource_id}/neighbors",
    summary="Get multi-hop neighbors for Phase 10 discovery",
    description=(
        "Returns resources connected to the specified resource through citation "
        "or co-citation relationships, up to the specified number of hops. "
        "This is a Phase 10 endpoint for graph intelligence features."
    ),
)
def get_multihop_neighbors(
    resource_id: str,
    hops: int = Query(1, ge=1, le=2, description="Number of hops (1 or 2)"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of neighbors to return"),
    edge_types: Optional[str] = Query(None, description="Comma-separated edge types to filter"),
    min_weight: float = Query(0.0, ge=0.0, le=1.0, description="Minimum edge weight"),
    db: Session = Depends(get_sync_db),
):
    """
    Get multi-hop neighbors for a resource using Phase 10 graph intelligence.
    
    This endpoint queries the multi-layer graph to find resources connected
    through citation, co-authorship, subject similarity, or temporal edges.
    
    Args:
        resource_id: UUID of the source resource
        hops: Number of hops to traverse (1 or 2)
        limit: Maximum number of neighbors to return
        edge_types: Optional comma-separated list of edge types to filter
        min_weight: Minimum edge weight threshold
        db: Database session dependency
        
    Returns:
        Dict with neighbors list and total count
        
    Raises:
        HTTPException: If resource is not found or other errors occur
    """
    from backend.app.database.models import Resource
    from backend.app.services.graph_service import GraphService
    from backend.app.schemas.discovery import NeighborResponse, NeighborsResponse
    
    # Verify resource exists
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=404,
            detail=f"Resource {resource_id} not found"
        )
    
    # Parse edge types filter
    edge_type_list = None
    if edge_types:
        edge_type_list = [t.strip() for t in edge_types.split(",")]
    
    # Get graph service and query neighbors
    graph_service = GraphService(db)
    
    try:
        neighbors_data = graph_service.get_neighbors_multihop(
            resource_id=str(resource_id),
            hops=hops,
            edge_types=edge_type_list,
            min_weight=min_weight,
            limit=limit
        )
        
        # Convert to response schema
        neighbors = []
        for neighbor_data in neighbors_data:
            neighbor_resource = db.query(Resource).filter(
                Resource.id == neighbor_data["resource_id"]
            ).first()
            
            if neighbor_resource:
                neighbors.append(NeighborResponse(
                    resource_id=neighbor_data["resource_id"],
                    title=neighbor_resource.title,
                    type=neighbor_resource.type,
                    distance=neighbor_data["distance"],
                    path=neighbor_data["path"],
                    path_strength=neighbor_data.get("path_strength", neighbor_data.get("total_weight", 1.0)),
                    edge_types=neighbor_data.get("edge_types", []),
                    score=neighbor_data.get("score", 1.0),
                    intermediate=neighbor_data.get("intermediate"),
                    quality=neighbor_data.get("quality", neighbor_resource.quality_overall or 0.0),
                    novelty=neighbor_data.get("novelty", 0.5)
                ))
        
        logger.info(
            f"Found {len(neighbors)} neighbors for resource {resource_id} "
            f"with {hops} hops"
        )
        
        return NeighborsResponse(
            neighbors=neighbors,
            total_count=len(neighbors)
        )
        
    except Exception as e:
        logger.error(f"Error finding neighbors for {resource_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while finding neighbors"
        )
