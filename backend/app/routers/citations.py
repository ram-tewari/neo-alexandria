"""
Neo Alexandria 2.0 - Citation API Endpoints (Phase 6)

This module provides REST API endpoints for citation management and graph visualization.

Related files:
- app/services/citation_service.py: Citation business logic
- app/schemas/citation.py: Request/response schemas
- app/database/models.py: Citation and Resource models
"""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.base import get_sync_db
from backend.app.services.citation_service import CitationService
from backend.app.schemas.citation import (
    CitationWithResource,
    ResourceCitationsResponse,
    CitationGraphResponse,
    CitationExtractionResponse,
    CitationResolutionResponse,
    ImportanceComputationResponse,
    GraphNode,
    GraphEdge,
)

router = APIRouter(prefix="/citations", tags=["citations"])


@router.get("/resources/{resource_id}/citations", response_model=ResourceCitationsResponse)
async def get_resource_citations(
    resource_id: str,
    direction: str = Query("both", regex="^(outbound|inbound|both)$"),
    db: Session = Depends(get_sync_db)
):
    """
    Retrieve citations for a specific resource.
    
    Args:
        resource_id: UUID of the resource
        direction: Citation direction - "outbound" (this resource cites), 
                  "inbound" (cites this resource), or "both"
        db: Database session
        
    Returns:
        ResourceCitationsResponse with outbound and inbound citations
    """
    service = CitationService(db)
    
    try:
        citations = service.get_citations_for_resource(resource_id, direction)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Separate outbound and inbound
    outbound = []
    inbound = []
    
    for citation in citations:
        # Build citation response
        citation_dict = {
            "id": str(citation.id),
            "source_resource_id": str(citation.source_resource_id),
            "target_url": citation.target_url,
            "citation_type": citation.citation_type,
            "context_snippet": citation.context_snippet,
            "position": citation.position,
            "target_resource_id": str(citation.target_resource_id) if citation.target_resource_id else None,
            "importance_score": citation.importance_score,
            "created_at": citation.created_at,
            "updated_at": citation.updated_at,
            "target_resource": None
        }
        
        # Add target resource info if available
        if citation.target_resource_id:
            from backend.app.database.models import Resource
            from sqlalchemy import select
            
            result = db.execute(
                select(Resource).filter(Resource.id == citation.target_resource_id)
            )
            target_resource = result.scalar_one_or_none()
            
            if target_resource:
                citation_dict["target_resource"] = {
                    "id": str(target_resource.id),
                    "title": target_resource.title,
                    "source": target_resource.source
                }
        
        # Categorize by direction
        if str(citation.source_resource_id) == resource_id:
            outbound.append(CitationWithResource(**citation_dict))
        else:
            inbound.append(CitationWithResource(**citation_dict))
    
    return ResourceCitationsResponse(
        resource_id=resource_id,
        outbound=outbound,
        inbound=inbound,
        counts={
            "outbound": len(outbound),
            "inbound": len(inbound),
            "total": len(citations)
        }
    )


@router.get("/graph/citations", response_model=CitationGraphResponse)
async def get_citation_network(
    resource_ids: List[str] = Query([], description="Filter to specific resources"),
    min_importance: float = Query(0.0, ge=0.0, le=1.0, description="Minimum importance score"),
    depth: int = Query(1, ge=1, le=2, description="Graph depth"),
    db: Session = Depends(get_sync_db)
):
    """
    Get citation network for visualization.
    
    Args:
        resource_ids: Optional list of resource IDs to focus on
        min_importance: Minimum importance score threshold
        depth: Graph traversal depth (1 or 2)
        db: Database session
        
    Returns:
        CitationGraphResponse with nodes and edges
    """
    service = CitationService(db)
    
    if resource_ids:
        # Build graph for specific resources
        all_nodes = {}
        all_edges = []
        
        for resource_id in resource_ids:
            try:
                graph = service.get_citation_graph(resource_id, depth=depth)
                
                # Merge nodes
                for node in graph["nodes"]:
                    all_nodes[node["id"]] = node
                
                # Merge edges
                all_edges.extend(graph["edges"])
            except ValueError:
                continue
        
        # Filter by importance if specified
        if min_importance > 0.0:
            from backend.app.database.models import Citation
            from sqlalchemy import select
            
            # Get citations with sufficient importance
            result = db.execute(
                select(Citation).filter(
                    Citation.importance_score >= min_importance
                )
            )
            important_citations = result.scalars().all()
            important_pairs = {
                (str(c.source_resource_id), str(c.target_resource_id))
                for c in important_citations
            }
            
            # Filter edges
            all_edges = [
                edge for edge in all_edges
                if (edge["source"], edge["target"]) in important_pairs
            ]
        
        # Convert to response format
        nodes = [GraphNode(**node) for node in all_nodes.values()]
        edges = [GraphEdge(**edge) for edge in all_edges]
        
        return CitationGraphResponse(nodes=nodes, edges=edges)
    
    else:
        # Return global overview (limited)
        from backend.app.database.models import Citation
        from sqlalchemy import select
        
        query = select(Citation).filter(Citation.target_resource_id.isnot(None))
        
        if min_importance > 0.0:
            query = query.filter(Citation.importance_score >= min_importance)
        
        query = query.limit(100)  # Limit for performance
        
        result = db.execute(query)
        citations = result.scalars().all()
        
        # Build nodes and edges
        nodes_dict = {}
        edges = []
        
        for citation in citations:
            # Add source node
            if str(citation.source_resource_id) not in nodes_dict:
                from backend.app.database.models import Resource
                
                resource_result = db.execute(
                    select(Resource).filter(Resource.id == citation.source_resource_id)
                )
                resource = resource_result.scalar_one_or_none()
                
                if resource:
                    nodes_dict[str(citation.source_resource_id)] = GraphNode(
                        id=str(resource.id),
                        title=resource.title,
                        type="source"
                    )
            
            # Add target node
            if str(citation.target_resource_id) not in nodes_dict:
                from backend.app.database.models import Resource
                
                resource_result = db.execute(
                    select(Resource).filter(Resource.id == citation.target_resource_id)
                )
                resource = resource_result.scalar_one_or_none()
                
                if resource:
                    nodes_dict[str(citation.target_resource_id)] = GraphNode(
                        id=str(resource.id),
                        title=resource.title,
                        type="cited"
                    )
            
            # Add edge
            edges.append(GraphEdge(
                source=str(citation.source_resource_id),
                target=str(citation.target_resource_id),
                type=citation.citation_type
            ))
        
        return CitationGraphResponse(
            nodes=list(nodes_dict.values()),
            edges=edges
        )


@router.post("/resources/{resource_id}/citations/extract", response_model=CitationExtractionResponse)
async def trigger_citation_extraction(
    resource_id: str,
    db: Session = Depends(get_sync_db)
):
    """
    Manually trigger citation extraction for a resource.
    
    This is typically done automatically during ingestion, but can be
    triggered manually for debugging or re-extraction.
    
    Args:
        resource_id: UUID of the resource
        db: Database session
        
    Returns:
        CitationExtractionResponse with task status
    """
    from ..tasks.celery_tasks import extract_citations_task
    
    service = CitationService(db)
    
    # Verify resource exists
    from backend.app.database.models import Resource
    from sqlalchemy import select
    
    try:
        import uuid
        resource_uuid = uuid.UUID(resource_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid resource ID format")
    
    result = db.execute(
        select(Resource).filter(Resource.id == resource_uuid)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Queue extraction task
    extract_citations_task.apply_async(args=[resource_id], priority=5)
    
    return CitationExtractionResponse(
        status="queued",
        resource_id=resource_id,
        message="Citation extraction queued for processing"
    )


@router.post("/citations/resolve", response_model=CitationResolutionResponse)
async def resolve_citations(
    db: Session = Depends(get_sync_db)
):
    """
    Manually trigger internal citation resolution.
    
    This matches unresolved citation URLs to existing resources in the database.
    Typically runs automatically after new resource ingestion.
    
    Args:
        db: Database session
        
    Returns:
        CitationResolutionResponse with task status
    """
    from ..tasks.celery_tasks import resolve_citations_task
    
    service = CitationService(db)
    
    # Queue resolution task
    resolve_citations_task.apply_async(priority=5)
    
    return CitationResolutionResponse(
        status="queued"
    )


@router.post("/citations/importance/compute", response_model=ImportanceComputationResponse)
async def compute_importance_scores(
    db: Session = Depends(get_sync_db)
):
    """
    Recompute PageRank importance scores for all citations.
    
    This is a computationally expensive operation that should be run
    periodically (e.g., daily) rather than on every request.
    
    Args:
        db: Database session
        
    Returns:
        ImportanceComputationResponse with task status
    """
    from ..tasks.celery_tasks import compute_citation_importance_task
    
    service = CitationService(db)
    
    # Queue computation task
    compute_citation_importance_task.apply_async(priority=3)
    
    return ImportanceComputationResponse(
        status="queued"
    )
