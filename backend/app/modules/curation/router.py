"""
Neo Alexandria 2.0 - Curation API Router

This module provides API endpoints for content curation and quality control in Neo Alexandria 2.0.
It offers review queue management, batch operations, and quality-based filtering for
maintaining high-quality content in the knowledge base.

Related files:
- app/modules/curation/service.py: CurationService class for business logic
- app/modules/curation/schema.py: Schemas for batch operations and filtering
- app/shared/database.py: Database session management

Endpoints:
- GET /curation/review-queue: Access low-quality items for review
- POST /curation/batch-update: Apply batch updates to multiple resources
- GET /curation/quality-analysis/{resource_id}: Get quality analysis
- GET /curation/low-quality: List low-quality resources
- POST /curation/bulk-quality-check: Bulk quality check
"""

from __future__ import annotations

from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...config.settings import get_settings, Settings
from ...shared.database import get_sync_db
from .schema import (
    ReviewQueueParams,
    ReviewQueueResponse,
    BatchUpdateRequest,
    BatchUpdateResult,
    QualityAnalysisResponse,
    LowQualityResponse,
    BulkQualityCheckRequest,
)
from .service import CurationService


router = APIRouter(prefix="/curation", tags=["curation"])


@router.get("/review-queue", response_model=ReviewQueueResponse)
def review_queue_endpoint(
    threshold: Optional[float] = None,
    include_unread_only: bool = False,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_sync_db),
    settings: Settings = Depends(get_settings),
):
    """
    Get items in the review queue based on quality threshold.
    
    Returns resources with quality scores below the threshold,
    sorted by quality score (ascending) and updated_at.
    """
    params = ReviewQueueParams(
        threshold=threshold,
        include_unread_only=include_unread_only,
        limit=limit,
        offset=offset,
    )
    service = CurationService(db, settings)
    items, total = service.review_queue(params)
    return ReviewQueueResponse(items=items, total=total)


@router.post("/batch-update", response_model=BatchUpdateResult)
def batch_update_endpoint(
    payload: BatchUpdateRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Apply batch updates to multiple resources.
    
    Updates are applied in a single transaction. Failed updates
    are tracked and returned in the response.
    """
    try:
        service = CurationService(db)
        result = service.batch_update(payload.resource_ids, payload.updates)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/quality-analysis/{resource_id}", response_model=QualityAnalysisResponse)
def quality_analysis_endpoint(
    resource_id: str,
    db: Session = Depends(get_sync_db),
):
    """
    Get detailed quality analysis for a specific resource.
    
    Returns quality dimensions, overall score, and improvement suggestions.
    """
    try:
        rid = uuid.UUID(resource_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource id")

    try:
        service = CurationService(db)
        data = service.quality_analysis(rid)
        data["suggestions"] = service.improvement_suggestions(rid)
        return data
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.get("/low-quality", response_model=LowQualityResponse)
def low_quality_endpoint(
    threshold: float = 0.5,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_sync_db),
    settings: Settings = Depends(get_settings),
):
    """
    Get list of low-quality resources.
    
    Returns resources with quality scores below the threshold.
    """
    params = ReviewQueueParams(
        threshold=threshold,
        include_unread_only=False,
        limit=limit,
        offset=offset,
    )
    service = CurationService(db, settings)
    items, total = service.review_queue(params)
    return LowQualityResponse(items=items, total=total)


@router.post("/bulk-quality-check", response_model=BatchUpdateResult)
def bulk_quality_check_endpoint(
    payload: BulkQualityCheckRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Perform bulk quality check on multiple resources.
    
    Recalculates quality scores for all specified resources.
    """
    if not payload.resource_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No resource ids provided")
    
    try:
        ids = [uuid.UUID(rid) for rid in payload.resource_ids]
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource id in list")

    service = CurationService(db)
    result = service.bulk_quality_check(ids)
    return result


# Export router for module interface
curation_router = router
