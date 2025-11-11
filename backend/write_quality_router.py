"""Script to write the quality router file."""

QUALITY_ROUTER_CONTENT = '''"""
Neo Alexandria 2.0 - Quality Assessment API Router

This module provides REST API endpoints for quality assessment in Neo Alexandria 2.0.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from ..database.base import get_sync_db
from ..database.models import Resource
from ..schemas.quality import (
    QualityDetailsResponse,
    QualityRecalculateRequest,
    OutlierListResponse,
    OutlierResponse,
    DegradationReport,
    DegradationResourceReport,
    SummaryEvaluationResponse,
    QualityDistributionResponse,
    QualityDistributionBin,
    QualityStatistics,
    QualityTrendsResponse,
    QualityTrendDataPoint,
    QualityDimensionsResponse,
    DimensionStatistics,
    ReviewQueueResponse,
    ReviewQueueItem,
)
from ..services.quality_service import QualityService
from ..services.summarization_evaluator import SummarizationEvaluator


router = APIRouter(prefix="", tags=["quality"])


def _get_quality_service(db: Session) -> QualityService:
    """Helper to create QualityService instance."""
    return QualityService(db)


def _get_summarization_evaluator(db: Session) -> SummarizationEvaluator:
    """Helper to create SummarizationEvaluator instance."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return SummarizationEvaluator(db, openai_api_key=openai_api_key)


@router.get("/resources/{resource_id}/quality-details", response_model=QualityDetailsResponse)
async def get_quality_details(
    resource_id: str,
    db: Session = Depends(get_sync_db),
):
    """Retrieve full quality dimension breakdown for a resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    quality_dimensions = {
        "accuracy": resource.quality_accuracy or 0.0,
        "completeness": resource.quality_completeness or 0.0,
        "consistency": resource.quality_consistency or 0.0,
        "timeliness": resource.quality_timeliness or 0.0,
        "relevance": resource.quality_relevance or 0.0,
    }
    
    quality_weights = {}
    if resource.quality_weights:
        try:
            quality_weights = json.loads(resource.quality_weights)
        except (json.JSONDecodeError, TypeError):
            quality_weights = {
                "accuracy": 0.30,
                "completeness": 0.25,
                "consistency": 0.20,
                "timeliness": 0.15,
                "relevance": 0.10,
            }
    else:
        quality_weights = {
            "accuracy": 0.30,
            "completeness": 0.25,
            "consistency": 0.20,
            "timeliness": 0.15,
            "relevance": 0.10,
        }
    
    outlier_reasons = None
    if resource.outlier_reasons:
        try:
            outlier_reasons = json.loads(resource.outlier_reasons)
        except (json.JSONDecodeError, TypeError):
            outlier_reasons = []
    
    return QualityDetailsResponse(
        resource_id=str(resource.id),
        quality_dimensions=quality_dimensions,
        quality_overall=resource.quality_overall or 0.0,
        quality_weights=quality_weights,
        quality_last_computed=resource.quality_last_computed,
        quality_computation_version=resource.quality_computation_version,
        is_quality_outlier=resource.is_quality_outlier or False,
        needs_quality_review=resource.needs_quality_review or False,
        outlier_score=resource.outlier_score,
        outlier_reasons=outlier_reasons,
    )


@router.post("/quality/recalculate", status_code=status.HTTP_202_ACCEPTED)
async def recalculate_quality(
    request: QualityRecalculateRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_sync_db),
):
    """Trigger quality recomputation for one or more resources."""
    quality_service = _get_quality_service(db)
    
    resource_ids = []
    if request.resource_id:
        resource_ids = [request.resource_id]
    elif request.resource_ids:
        resource_ids = request.resource_ids
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either resource_id or resource_ids"
        )
    
    for resource_id in resource_ids:
        background.add_task(
            _compute_quality_background,
            resource_id,
            request.weights,
            str(db.get_bind().url) if db.get_bind() else None
        )
    
    return {
        "status": "accepted",
        "message": f"Quality computation queued for {len(resource_ids)} resource(s)"
    }


def _compute_quality_background(resource_id: str, weights: Optional[dict], engine_url: Optional[str]):
    """Background task to compute quality for a resource."""
    from ..database.base import SessionLocal
    
    db = SessionLocal()
    try:
        quality_service = QualityService(db)
        quality_service.compute_quality(resource_id, weights=weights)
        db.commit()
    except Exception as e:
        print(f"Error computing quality for {resource_id}: {e}")
        db.rollback()
    finally:
        db.close()
'''

# Write part 2
QUALITY_ROUTER_PART2 = '''

@router.get("/quality/outliers", response_model=OutlierListResponse)
async def get_outliers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    min_outlier_score: Optional[float] = Query(None, ge=-1.0, le=1.0, description="Minimum outlier score"),
    reason: Optional[str] = Query(None, description="Filter by specific outlier reason"),
    db: Session = Depends(get_sync_db),
):
    """List detected quality outliers with pagination and filtering."""
    query = db.query(Resource).filter(Resource.is_quality_outlier == True)
    
    if min_outlier_score is not None:
        query = query.filter(Resource.outlier_score >= min_outlier_score)
    
    if reason:
        query = query.filter(Resource.outlier_reasons.like(f'%"{reason}"%'))
    
    total = query.count()
    
    offset = (page - 1) * limit
    resources = query.order_by(Resource.outlier_score.asc()).offset(offset).limit(limit).all()
    
    outliers = []
    for resource in resources:
        outlier_reasons = []
        if resource.outlier_reasons:
            try:
                outlier_reasons = json.loads(resource.outlier_reasons)
            except (json.JSONDecodeError, TypeError):
                outlier_reasons = []
        
        outliers.append(OutlierResponse(
            resource_id=str(resource.id),
            title=resource.title,
            quality_overall=resource.quality_overall or 0.0,
            outlier_score=resource.outlier_score or 0.0,
            outlier_reasons=outlier_reasons,
            needs_quality_review=resource.needs_quality_review or False,
        ))
    
    return OutlierListResponse(
        total=total,
        page=page,
        limit=limit,
        outliers=outliers,
    )


@router.get("/quality/degradation", response_model=DegradationReport)
async def get_degradation_report(
    time_window_days: int = Query(30, ge=1, le=365, description="Lookback period in days"),
    db: Session = Depends(get_sync_db),
):
    """Get quality degradation report for specified time window."""
    quality_service = _get_quality_service(db)
    
    degraded_resources = quality_service.monitor_quality_degradation(
        time_window_days=time_window_days
    )
    
    degradation_reports = [
        DegradationResourceReport(
            resource_id=item["resource_id"],
            title=item["title"],
            old_quality=item["old_quality"],
            new_quality=item["new_quality"],
            degradation_pct=item["degradation_pct"],
        )
        for item in degraded_resources
    ]
    
    return DegradationReport(
        time_window_days=time_window_days,
        degraded_count=len(degradation_reports),
        degraded_resources=degradation_reports,
    )


@router.post("/summaries/{resource_id}/evaluate", status_code=status.HTTP_202_ACCEPTED)
async def evaluate_summary(
    resource_id: str,
    use_g_eval: bool = Query(False, description="Whether to use G-Eval (requires OpenAI API)"),
    background: BackgroundTasks = None,
    db: Session = Depends(get_sync_db),
):
    """Trigger summary quality evaluation for a resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    if not resource.summary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource has no summary to evaluate"
        )
    
    background.add_task(
        _evaluate_summary_background,
        resource_id,
        use_g_eval,
        str(db.get_bind().url) if db.get_bind() else None
    )
    
    return {
        "status": "accepted",
        "message": f"Summary evaluation queued for resource {resource_id}"
    }


def _evaluate_summary_background(resource_id: str, use_g_eval: bool, engine_url: Optional[str]):
    """Background task to evaluate summary quality."""
    from ..database.base import SessionLocal
    
    db = SessionLocal()
    try:
        evaluator = _get_summarization_evaluator(db)
        evaluator.evaluate_summary(resource_id, use_g_eval=use_g_eval)
        db.commit()
    except Exception as e:
        print(f"Error evaluating summary for {resource_id}: {e}")
        db.rollback()
    finally:
        db.close()
'''

# Write the file
with open("app/routers/quality.py", "w", encoding="utf-8") as f:
    f.write(QUALITY_ROUTER_CONTENT)
    f.write(QUALITY_ROUTER_PART2)

print("Quality router file written successfully!")
print(f"File size: {os.path.getsize('app/routers/quality.py')} bytes")
