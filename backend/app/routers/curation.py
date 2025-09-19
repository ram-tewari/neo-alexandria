"""
Neo Alexandria 2.0 - Curation API Router

This module provides API endpoints for content curation and quality control in Neo Alexandria 2.0.
It offers review queue management, batch operations, and quality-based filtering for
maintaining high-quality content in the knowledge base.

Related files:
- app/services/curation_service.py: CurationService class for business logic
- app/schemas/query.py: Schemas for batch operations and filtering
- app/schemas/resource.py: Resource schemas for updates
- app/database/base.py: Database session management

Endpoints:
- GET /curation/review-queue: Access low-quality items for review
- POST /curation/batch-update: Apply batch updates to multiple resources
- GET /curation/stats: Get curation statistics and metrics
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.config.settings import get_settings, Settings
from backend.app.database.base import get_sync_db
from backend.app.schemas.resource import ResourceRead
from backend.app.schemas.query import ReviewQueueParams, BatchUpdateRequest, BatchUpdateResult
from backend.app.services.curation_service import CurationInterface


router = APIRouter(prefix="/curation", tags=["curation"])


class ReviewQueueResponse(BaseModel):
    items: list[ResourceRead]
    total: int


@router.get("/review-queue", response_model=ReviewQueueResponse)
def review_queue_endpoint(
    threshold: Optional[float] = None,
    include_unread_only: bool = False,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_sync_db),
    settings: Settings = Depends(get_settings),
):
    params = ReviewQueueParams(
        threshold=threshold,
        include_unread_only=include_unread_only,
        limit=limit,
        offset=offset,
    )
    items, total = CurationInterface.review_queue(db, params, settings)
    return ReviewQueueResponse(items=items, total=total)


@router.post("/batch-update", response_model=BatchUpdateResult)
def batch_update_endpoint(
    payload: BatchUpdateRequest,
    db: Session = Depends(get_sync_db),
):
    try:
        result = CurationInterface.batch_update(db, payload.resource_ids, payload.updates)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

class QualityAnalysisResponse(BaseModel):
    resource_id: str
    metadata_completeness: float
    readability: dict
    source_credibility: float
    content_depth: float
    overall_quality: float
    quality_level: str
    suggestions: list[str]


@router.get("/quality-analysis/{resource_id}", response_model=QualityAnalysisResponse)
def quality_analysis_endpoint(
    resource_id: str,
    db: Session = Depends(get_sync_db),
):
    try:
        import uuid
        rid = uuid.UUID(resource_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource id")

    try:
        data = CurationInterface.quality_analysis(db, rid)
        data["suggestions"] = CurationInterface.improvement_suggestions(db, rid)
        return data
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


class LowQualityResponse(BaseModel):
    items: list[ResourceRead]
    total: int


@router.get("/low-quality", response_model=LowQualityResponse)
def low_quality_endpoint(
    threshold: float = 0.5,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_sync_db),
    settings: Settings = Depends(get_settings),
):
    params = ReviewQueueParams(
        threshold=threshold,
        include_unread_only=False,
        limit=limit,
        offset=offset,
    )
    items, total = CurationInterface.review_queue(db, params, settings)
    return LowQualityResponse(items=items, total=total)


class BulkQualityCheckRequest(BaseModel):
    resource_ids: list[str]


@router.post("/bulk-quality-check", response_model=BatchUpdateResult)
def bulk_quality_check_endpoint(
    payload: BulkQualityCheckRequest,
    db: Session = Depends(get_sync_db),
):
    import uuid
    if not payload.resource_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No resource ids provided")
    try:
        ids = [uuid.UUID(rid) for rid in payload.resource_ids]
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource id in list")

    result = CurationInterface.bulk_quality_check(db, ids)
    return result



