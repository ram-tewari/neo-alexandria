"""
Neo Alexandria 2.0 - Discovery API Router

This module provides REST API endpoints for literature-based discovery (LBD)
in Neo Alexandria 2.0, implementing the ABC paradigm for hypothesis generation.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database.base import get_sync_db
from ..database.models import Resource
from ..schemas.discovery import (
    OpenDiscoveryResponse,
    ClosedDiscoveryRequest,
    ClosedDiscoveryResponse,
    NeighborsResponse,
    HypothesesListResponse,
    HypothesisValidation,
    HypothesisResponse,
)
from ..services.lbd_service import LBDService


router = APIRouter(prefix="/discovery", tags=["discovery"])


def _get_lbd_service(db: Session) -> LBDService:
    """Helper to create LBDService instance."""
    return LBDService(db)


@router.get("/open", response_model=OpenDiscoveryResponse)
async def open_discovery(
    resource_id: str = Query(..., description="Starting resource UUID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of hypotheses to return"),
    min_plausibility: float = Query(0.0, ge=0.0, le=1.0, description="Minimum plausibility score threshold"),
    db: Session = Depends(get_sync_db),
):
    """
    Perform open discovery to find potential connections from a resource.
    
    Open discovery (A→B→C pattern) starts from a known resource A and discovers
    potential target resources C through intermediate resources B.
    """
    # Verify resource exists
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} not found"
        )
    
    lbd_service = _get_lbd_service(db)
    result = lbd_service.open_discovery(
        start_resource_id=resource_id,
        limit=limit,
        min_plausibility=min_plausibility
    )
    
    # Service returns a list directly
    hypotheses = result if isinstance(result, list) else result.get("hypotheses", [])
    
    return OpenDiscoveryResponse(
        hypotheses=[],  # Stub implementation returns empty list
        total_count=len(hypotheses)
    )


@router.post("/closed", response_model=ClosedDiscoveryResponse)
async def closed_discovery(
    request: ClosedDiscoveryRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Perform closed discovery to find paths between two resources.
    
    Closed discovery (A→B→C pattern) finds connecting paths between a known
    starting resource A and a known target resource C through intermediate
    resources B.
    """
    # Verify both resources exist
    resource_a = db.query(Resource).filter(Resource.id == request.a_resource_id).first()
    if not resource_a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {request.a_resource_id} not found"
        )
    
    resource_c = db.query(Resource).filter(Resource.id == request.c_resource_id).first()
    if not resource_c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {request.c_resource_id} not found"
        )
    
    lbd_service = _get_lbd_service(db)
    result = lbd_service.closed_discovery(
        a_resource_id=request.a_resource_id,
        c_resource_id=request.c_resource_id,
        max_hops=request.max_hops
    )
    
    # Convert service result to response schema
    from ..schemas.discovery import ClosedDiscoveryPath, ResourceSummary
    
    # Handle both old dict format and new list format
    if isinstance(result, dict):
        paths_data = result.get("paths", [])
    else:
        paths_data = result
    paths = []
    
    for path_info in paths_data:
        # Get intermediate resources
        b_resources = []
        path_ids = path_info.get("path", [])
        
        # Skip first (A) and last (C) resources
        for resource_id in path_ids[1:-1]:
            resource = db.query(Resource).filter(Resource.id == resource_id).first()
            if resource:
                b_resources.append(ResourceSummary(
                    id=str(resource.id),
                    title=resource.title,
                    type=resource.type,
                    publication_year=None,
                    quality_overall=resource.quality_overall
                ))
        
        paths.append(ClosedDiscoveryPath(
            b_resources=b_resources,
            path=path_ids,
            path_length=path_info.get("length", len(path_ids) - 1),
            plausibility_score=path_info.get("strength", 0.0),
            path_strength=path_info.get("strength", 0.0),
            common_neighbors=0,
            semantic_similarity=0.0,
            is_direct=path_info.get("length", 0) == 1,
            weights=[]
        ))
    
    return ClosedDiscoveryResponse(
        paths=paths,
        total_count=len(paths)
    )


@router.get("/neighbors/{resource_id}", response_model=NeighborsResponse)
async def get_discovery_neighbors(
    resource_id: str,
    hops: int = Query(1, ge=1, le=2, description="Number of hops (1 or 2)"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of neighbors to return"),
    db: Session = Depends(get_sync_db),
):
    """
    Query graph neighbors up to specified hops.
    
    Returns resources connected to the specified resource through citation
    or co-citation relationships, up to the specified number of hops.
    """
    # Verify resource exists
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} not found"
        )
    
    # Use GraphService to get neighbors
    from ..services.graph_service import GraphService
    from ..schemas.discovery import NeighborResponse
    
    graph_service = GraphService(db)
    neighbors_data = graph_service.get_neighbors_multihop(
        resource_id=str(resource_id),
        hops=hops,
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
    
    return NeighborsResponse(
        neighbors=neighbors,
        total_count=len(neighbors)
    )


@router.get("/hypotheses", response_model=HypothesesListResponse)
async def get_hypotheses(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items per page"),
    hypothesis_type: Optional[str] = Query(None, description="Filter by hypothesis type (open/closed)"),
    min_plausibility: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum plausibility score"),
    is_validated: Optional[bool] = Query(None, description="Filter by validation status"),
    db: Session = Depends(get_sync_db),
):
    """
    Query discovery hypotheses from database with pagination and filtering.
    
    Returns stored hypotheses that can be filtered by type, plausibility score,
    and validation status.
    """
    from ..database.models import DiscoveryHypothesis
    from ..schemas.discovery import HypothesisResponse, ResourceSummary
    
    # Build query with filters
    query = db.query(DiscoveryHypothesis)
    
    if hypothesis_type:
        query = query.filter(DiscoveryHypothesis.hypothesis_type == hypothesis_type)
    
    if min_plausibility is not None:
        query = query.filter(DiscoveryHypothesis.confidence_score >= min_plausibility)
    
    if is_validated is not None:
        if is_validated:
            query = query.filter(DiscoveryHypothesis.status == "validated")
        else:
            query = query.filter(DiscoveryHypothesis.status != "validated")
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    hypotheses_db = query.offset(skip).limit(limit).all()
    
    # Convert to response schema
    hypotheses = []
    for hyp in hypotheses_db:
        # Get resource summaries
        a_resource = db.query(Resource).filter(Resource.id == hyp.resource_a_id).first()
        c_resource = db.query(Resource).filter(Resource.id == hyp.resource_c_id).first()
        
        if a_resource and c_resource:
            hypotheses.append(HypothesisResponse(
                id=str(hyp.id),
                a_resource=ResourceSummary(
                    id=str(a_resource.id),
                    title=a_resource.title,
                    type=a_resource.type,
                    publication_year=None,
                    quality_overall=a_resource.quality_overall
                ),
                c_resource=ResourceSummary(
                    id=str(c_resource.id),
                    title=c_resource.title,
                    type=c_resource.type,
                    publication_year=None,
                    quality_overall=c_resource.quality_overall
                ),
                b_resources=[],
                hypothesis_type=hyp.hypothesis_type or "open",
                plausibility_score=hyp.confidence_score or 0.0,
                path_strength=hyp.confidence_score or 0.0,
                path_length=2,
                common_neighbors=0,
                discovered_at=hyp.created_at.isoformat() if hyp.created_at else "",
                is_validated=hyp.status == "validated" if hyp.status else None,
                validation_notes=None
            ))
    
    return HypothesesListResponse(
        hypotheses=hypotheses,
        total_count=total_count,
        skip=skip,
        limit=limit
    )


@router.post("/hypotheses/{hypothesis_id}/validate", response_model=HypothesisResponse)
async def validate_hypothesis(
    hypothesis_id: str,
    validation: HypothesisValidation,
    db: Session = Depends(get_sync_db),
):
    """
    Update hypothesis validation status.
    
    Allows users to mark hypotheses as validated or invalid, with optional notes.
    """
    from ..database.models import DiscoveryHypothesis
    from ..schemas.discovery import HypothesisResponse, ResourceSummary
    
    # Find hypothesis
    hypothesis = db.query(DiscoveryHypothesis).filter(
        DiscoveryHypothesis.id == hypothesis_id
    ).first()
    
    if not hypothesis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hypothesis {hypothesis_id} not found"
        )
    
    # Update validation status
    hypothesis.status = "validated" if validation.is_valid else "rejected"
    db.commit()
    db.refresh(hypothesis)
    
    # Get resource summaries
    a_resource = db.query(Resource).filter(Resource.id == hypothesis.resource_a_id).first()
    c_resource = db.query(Resource).filter(Resource.id == hypothesis.resource_c_id).first()
    
    if not a_resource or not c_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated resources not found"
        )
    
    return HypothesisResponse(
        id=str(hypothesis.id),
        a_resource=ResourceSummary(
            id=str(a_resource.id),
            title=a_resource.title,
            type=a_resource.type,
            publication_year=None,
            quality_overall=a_resource.quality_overall
        ),
        c_resource=ResourceSummary(
            id=str(c_resource.id),
            title=c_resource.title,
            type=c_resource.type,
            publication_year=None,
            quality_overall=c_resource.quality_overall
        ),
        b_resources=[],
        hypothesis_type=hypothesis.hypothesis_type or "open",
        plausibility_score=hypothesis.confidence_score or 0.0,
        path_strength=hypothesis.confidence_score or 0.0,
        path_length=2,
        common_neighbors=0,
        discovered_at=hypothesis.created_at.isoformat() if hypothesis.created_at else "",
        is_validated=hypothesis.status == "validated",
        validation_notes=validation.notes
    )
