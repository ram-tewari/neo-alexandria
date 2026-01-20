"""
Neo Alexandria 2.0 - Discovery API Router for Phase 10

Provides REST endpoints for Literature-Based Discovery (LBD) implementing
the ABC paradigm for hypothesis generation and multi-hop neighbor discovery.

Related files:
- app.modules.graph.discovery: Core LBD logic
- app.modules.graph.service: Multi-layer graph and neighbor discovery
- app.modules.graph.schema: Pydantic request/response models
- app.modules.graph.model: DiscoveryHypothesis model

Features:
- Open discovery: Find related concepts from starting point
- Closed discovery: Connect two known concepts through intermediates
- Multi-hop neighbor queries with filtering
- Hypothesis listing and validation
- Edge weight updates based on validation feedback
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.modules.graph.model import DiscoveryHypothesis, GraphEdge
from app.database.models import Resource
from app.modules.graph.schema import (
    OpenDiscoveryResponse,
    OpenDiscoveryHypothesis,
    ClosedDiscoveryRequest,
    ClosedDiscoveryResponse,
    ClosedDiscoveryPath,
    NeighborsResponse,
    NeighborResponse,
    HypothesesListResponse,
    HypothesisResponse,
    HypothesisValidation,
    ResourceSummary,
)
from app.modules.graph.discovery import LBDService
from app.modules.graph.service import GraphService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get(
    "/open",
    response_model=OpenDiscoveryResponse,
    summary="Open discovery from starting resource",
    description=(
        "Discover related concepts C from starting point A through intermediate resources B. "
        "Uses the ABC paradigm to find potential connections that don't have direct edges. "
        "Returns hypotheses ranked by plausibility score combining path strength, "
        "common neighbors, and semantic similarity."
    ),
)
def open_discovery_endpoint(
    resource_id: str = Query(..., description="UUID of starting resource A"),
    limit: int = Query(20, ge=1, le=100, description="Maximum hypotheses to return"),
    min_plausibility: float = Query(
        0.5, ge=0.0, le=1.0, description="Minimum plausibility threshold"
    ),
    db: Session = Depends(get_db),
) -> OpenDiscoveryResponse:
    """Open discovery from starting resource."""
    try:
        lbd_service = LBDService(db)
        hypotheses = lbd_service.open_discovery(
            a_resource_id=resource_id, limit=limit, min_plausibility=min_plausibility
        )

        hypothesis_responses = [
            OpenDiscoveryHypothesis(
                c_resource=ResourceSummary(**h["c_resource"]),
                b_resources=[ResourceSummary(**b) for b in h["b_resources"]],
                plausibility_score=h["plausibility_score"],
                path_strength=h["path_strength"],
                common_neighbors=h["common_neighbors"],
                semantic_similarity=h["semantic_similarity"],
                path_length=h["path_length"],
                paths=h.get("paths"),
            )
            for h in hypotheses
        ]

        logger.info(
            f"Open discovery for resource {resource_id}: {len(hypothesis_responses)} hypotheses found"
        )

        return OpenDiscoveryResponse(
            hypotheses=hypothesis_responses, total_count=len(hypothesis_responses)
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server configuration error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error in open discovery for {resource_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during open discovery",
        )


@router.post(
    "/closed",
    response_model=ClosedDiscoveryResponse,
    summary="Closed discovery connecting two resources",
    description=(
        "Find connecting paths between two known concepts A and C through "
        "intermediate resources B. Returns all paths ranked by plausibility, "
        "with hop penalties applied for longer paths."
    ),
)
def closed_discovery_endpoint(
    request: ClosedDiscoveryRequest,
    db: Session = Depends(get_db),
) -> ClosedDiscoveryResponse:
    """Closed discovery connecting two resources."""
    try:
        lbd_service = LBDService(db)
        paths = lbd_service.closed_discovery(
            a_resource_id=request.a_resource_id,
            c_resource_id=request.c_resource_id,
            max_hops=request.max_hops,
        )

        path_responses = [
            ClosedDiscoveryPath(
                b_resources=[ResourceSummary(**b) for b in p["b_resources"]],
                path=p["path"],
                path_length=p["path_length"],
                plausibility_score=p["plausibility_score"],
                path_strength=p["path_strength"],
                common_neighbors=p["common_neighbors"],
                semantic_similarity=p["semantic_similarity"],
                is_direct=p["is_direct"],
                weights=p.get("weights"),
            )
            for p in paths
        ]

        logger.info(
            f"Closed discovery from {request.a_resource_id} to {request.c_resource_id}: {len(path_responses)} paths found"
        )

        return ClosedDiscoveryResponse(
            paths=path_responses, total_count=len(path_responses)
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server configuration error: {str(e)}",
        )
    except Exception as e:
        logger.error(
            f"Error in closed discovery from {request.a_resource_id} to {request.c_resource_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during closed discovery",
        )


@router.get(
    "/graph/resources/{resource_id}/neighbors",
    response_model=NeighborsResponse,
    summary="Get multi-hop neighbors with filtering",
    description=(
        "Discover neighbors at specified hop distance with intelligent filtering "
        "and ranking. Supports edge type filtering, weight thresholds, and "
        "combined scoring based on path strength, quality, and novelty."
    ),
)
def get_multihop_neighbors(
    resource_id: str,
    hops: int = Query(2, ge=1, le=2, description="Number of hops (1 or 2)"),
    edge_types: Optional[List[str]] = Query(
        None, description="Filter by edge types (e.g., citation, co_authorship)"
    ),
    min_weight: float = Query(
        0.0, ge=0.0, le=1.0, description="Minimum edge weight threshold"
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum neighbors to return"),
    db: Session = Depends(get_db),
) -> NeighborsResponse:
    """Get multi-hop neighbors with filtering."""
    try:
        graph_service = GraphService(db)
        neighbors = graph_service.get_neighbors_multihop(
            resource_id=resource_id,
            hops=hops,
            edge_types=edge_types,
            min_weight=min_weight,
            limit=limit,
        )

        neighbor_responses = [NeighborResponse(**n) for n in neighbors]

        logger.info(
            f"Multi-hop neighbors for resource {resource_id} (hops={hops}): {len(neighbor_responses)} found"
        )

        return NeighborsResponse(
            neighbors=neighbor_responses, total_count=len(neighbor_responses)
        )

    except ValueError as e:
        if "hops must be" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server configuration error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error getting neighbors for {resource_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during neighbor discovery",
        )


@router.get(
    "/hypotheses",
    response_model=HypothesesListResponse,
    summary="List discovery hypotheses with filtering",
    description=(
        "Retrieve stored discovery hypotheses with optional filtering by "
        "type, validation status, and plausibility threshold. "
        "Supports pagination for large result sets."
    ),
)
def list_hypotheses(
    hypothesis_type: Optional[str] = Query(
        None, description="Filter by hypothesis type ('open' or 'closed')"
    ),
    is_validated: Optional[bool] = Query(
        None, description="Filter by validation status"
    ),
    min_plausibility: float = Query(
        0.0, ge=0.0, le=1.0, description="Minimum plausibility threshold"
    ),
    skip: int = Query(0, ge=0, description="Number of items to skip (pagination)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items per page"),
    db: Session = Depends(get_db),
) -> HypothesesListResponse:
    """List discovery hypotheses with filtering and pagination."""
    try:
        if hypothesis_type and hypothesis_type not in ["open", "closed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hypothesis_type must be 'open' or 'closed'",
            )

        query = db.query(DiscoveryHypothesis)

        if hypothesis_type:
            query = query.filter(DiscoveryHypothesis.hypothesis_type == hypothesis_type)

        if is_validated is not None:
            query = query.filter(
                DiscoveryHypothesis.is_validated == (1 if is_validated else 0)
            )

        if min_plausibility > 0.0:
            query = query.filter(
                DiscoveryHypothesis.plausibility_score >= min_plausibility
            )

        total_count = query.count()

        hypotheses = (
            query.order_by(DiscoveryHypothesis.plausibility_score.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        hypothesis_responses = []

        for h in hypotheses:
            a_resource = (
                db.query(Resource).filter(Resource.id == h.a_resource_id).first()
            )
            c_resource = (
                db.query(Resource).filter(Resource.id == h.c_resource_id).first()
            )

            if not a_resource or not c_resource:
                continue

            try:
                b_resource_ids = (
                    json.loads(h.b_resource_ids)
                    if isinstance(h.b_resource_ids, str)
                    else h.b_resource_ids
                )
            except Exception:
                b_resource_ids = []

            b_resources = []
            if b_resource_ids:
                b_resources_query = (
                    db.query(Resource)
                    .filter(Resource.id.in_([UUID(bid) for bid in b_resource_ids]))
                    .all()
                )
                b_resources = [
                    ResourceSummary(
                        id=str(b.id),
                        title=b.title,
                        type=b.type,
                        publication_year=b.publication_year,
                        quality_overall=b.quality_overall,
                    )
                    for b in b_resources_query
                ]

            hypothesis_responses.append(
                HypothesisResponse(
                    id=str(h.id),
                    a_resource=ResourceSummary(
                        id=str(a_resource.id),
                        title=a_resource.title,
                        type=a_resource.type,
                        publication_year=a_resource.publication_year,
                        quality_overall=a_resource.quality_overall,
                    ),
                    c_resource=ResourceSummary(
                        id=str(c_resource.id),
                        title=c_resource.title,
                        type=c_resource.type,
                        publication_year=c_resource.publication_year,
                        quality_overall=c_resource.quality_overall,
                    ),
                    b_resources=b_resources,
                    hypothesis_type=h.hypothesis_type,
                    plausibility_score=h.plausibility_score,
                    path_strength=h.path_strength,
                    path_length=h.path_length,
                    common_neighbors=h.common_neighbors,
                    discovered_at=h.discovered_at.isoformat(),
                    is_validated=bool(h.is_validated)
                    if h.is_validated is not None
                    else None,
                    validation_notes=h.validation_notes,
                )
            )

        logger.info(
            f"Listed hypotheses: {len(hypothesis_responses)} returned, {total_count} total matching filters"
        )

        return HypothesesListResponse(
            hypotheses=hypothesis_responses,
            total_count=total_count,
            skip=skip,
            limit=limit,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing hypotheses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while listing hypotheses",
        )


@router.post(
    "/hypotheses/{hypothesis_id}/validate",
    status_code=status.HTTP_200_OK,
    summary="Validate or reject a hypothesis",
    description=(
        "Mark a hypothesis as validated or rejected. If validated, "
        "increases edge weights along the discovered path by 10% to "
        "strengthen the connection for future discoveries."
    ),
)
def validate_hypothesis(
    hypothesis_id: str,
    validation: HypothesisValidation,
    db: Session = Depends(get_db),
):
    """Validate or reject a hypothesis."""
    try:
        hypothesis = (
            db.query(DiscoveryHypothesis)
            .filter(DiscoveryHypothesis.id == UUID(hypothesis_id))
            .first()
        )

        if not hypothesis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hypothesis {hypothesis_id} not found",
            )

        hypothesis.is_validated = 1 if validation.is_valid else 0
        hypothesis.validation_notes = validation.notes

        if validation.is_valid:
            try:
                b_resource_ids = (
                    json.loads(hypothesis.b_resource_ids)
                    if isinstance(hypothesis.b_resource_ids, str)
                    else hypothesis.b_resource_ids
                )
                path = (
                    [str(hypothesis.a_resource_id)]
                    + b_resource_ids
                    + [str(hypothesis.c_resource_id)]
                )

                for i in range(len(path) - 1):
                    source_id = path[i]
                    target_id = path[i + 1]

                    edges = (
                        db.query(GraphEdge)
                        .filter(
                            GraphEdge.source_id == UUID(source_id),
                            GraphEdge.target_id == UUID(target_id),
                        )
                        .all()
                    )

                    for edge in edges:
                        new_weight = min(1.0, edge.weight * 1.1)
                        edge.weight = new_weight

                logger.info(
                    f"Increased edge weights along path for validated hypothesis {hypothesis_id}"
                )

            except Exception as e:
                logger.warning(
                    f"Failed to update edge weights for hypothesis {hypothesis_id}: {e}"
                )

        db.commit()

        logger.info(
            f"Hypothesis {hypothesis_id} validated: is_valid={validation.is_valid}"
        )

        return {
            "message": "Hypothesis validation updated successfully",
            "hypothesis_id": hypothesis_id,
            "is_valid": validation.is_valid,
            "edge_weights_updated": validation.is_valid,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating hypothesis {hypothesis_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during hypothesis validation",
        )
