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
