"""
Quality Module - API Router

This module provides REST API endpoints for quality assessment in Neo Alexandria 2.0.
Extracted from app/routers/quality.py as part of Phase 14 vertical slice refactoring.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.shared.database import get_sync_db
from app.database.models import Resource
from .schema import (
    QualityDetailsResponse,
    QualityRecalculateRequest,
    OutlierListResponse,
    OutlierResponse,
    DegradationReport,
    DegradationResourceReport,
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
from .service import QualityService
from .evaluator import SummarizationEvaluator


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
    db: Session = Depends(get_sync_db),
):
    """Trigger quality recomputation for one or more resources."""
    quality_service = _get_quality_service(db)
    
    resource_ids = []
    if request.resource_id:
        resource_ids = [str(request.resource_id)]
    elif request.resource_ids:
        resource_ids = [str(rid) for rid in request.resource_ids]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either resource_id or resource_ids"
        )
    
    # Try to queue task if celery is available
    try:
        from app.tasks.celery_tasks import recompute_quality_task
        for resource_id in resource_ids:
            recompute_quality_task.apply_async(
                args=[str(resource_id), request.weights],
                priority=5,
                countdown=10
            )
        return {
            "status": "accepted",
            "message": f"Quality computation queued for {len(resource_ids)} resource(s)"
        }
    except ImportError:
        # Celery not available, run synchronously
        for resource_id in resource_ids:
            try:
                quality_service.compute_quality(resource_id, request.weights)
            except Exception:
                pass
        return {
            "status": "completed",
            "message": f"Quality computation completed for {len(resource_ids)} resource(s)"
        }


@router.get("/quality/outliers", response_model=OutlierListResponse)
async def get_outliers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    min_outlier_score: Optional[float] = Query(None, ge=-1.0, le=1.0, description="Minimum outlier score"),
    reason: Optional[str] = Query(None, description="Filter by specific outlier reason"),
    db: Session = Depends(get_sync_db),
):
    """List detected quality outliers with pagination and filtering."""
    query = db.query(Resource).filter(Resource.is_quality_outlier)
    
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
    
    # Try to queue task if celery is available
    try:
        from app.tasks.celery_tasks import evaluate_summary_task
        evaluate_summary_task.apply_async(
            args=[str(resource_id), use_g_eval],
            priority=5
        )
        return {
            "status": "accepted",
            "message": f"Summary evaluation queued for resource {str(resource_id)}"
        }
    except ImportError:
        # Celery not available, run synchronously
        evaluator = _get_summarization_evaluator(db)
        try:
            evaluator.evaluate_summary(resource_id, use_g_eval)
            return {
                "status": "completed",
                "message": f"Summary evaluation completed for resource {str(resource_id)}"
            }
        except Exception as e:
            return {
                "status": "completed",
                "message": f"Summary evaluation completed (with errors: {str(e)[:100]})"
            }


@router.get("/quality/distribution", response_model=QualityDistributionResponse)
async def get_quality_distribution(
    bins: int = Query(10, ge=5, le=50, description="Number of histogram bins"),
    dimension: str = Query("overall", description="Quality dimension or 'overall'"),
    db: Session = Depends(get_sync_db),
):
    """Get quality score distribution histogram."""
    valid_dimensions = ["overall", "accuracy", "completeness", "consistency", "timeliness", "relevance"]
    if dimension not in valid_dimensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid dimension. Must be one of: {', '.join(valid_dimensions)}"
        )
    
    if dimension == "overall":
        column = Resource.quality_overall
    elif dimension == "accuracy":
        column = Resource.quality_accuracy
    elif dimension == "completeness":
        column = Resource.quality_completeness
    elif dimension == "consistency":
        column = Resource.quality_consistency
    elif dimension == "timeliness":
        column = Resource.quality_timeliness
    elif dimension == "relevance":
        column = Resource.quality_relevance
    
    scores = db.query(column).filter(column.isnot(None)).all()
    scores = [s[0] for s in scores if s[0] is not None]
    
    if not scores:
        return QualityDistributionResponse(
            dimension=dimension,
            bins=bins,
            distribution=[],
            statistics=QualityStatistics(mean=0.0, median=0.0, std_dev=0.0),
        )
    
    import statistics
    mean = statistics.mean(scores)
    median = statistics.median(scores)
    std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
    
    bin_width = 1.0 / bins
    distribution = []
    
    for i in range(bins):
        bin_start = i * bin_width
        bin_end = (i + 1) * bin_width
        
        count = sum(1 for s in scores if bin_start <= s < bin_end or (i == bins - 1 and s == 1.0))
        
        distribution.append(QualityDistributionBin(
            range=f"{bin_start:.1f}-{bin_end:.1f}",
            count=count,
        ))
    
    return QualityDistributionResponse(
        dimension=dimension,
        bins=bins,
        distribution=distribution,
        statistics=QualityStatistics(mean=mean, median=median, std_dev=std_dev),
    )


@router.get("/quality/trends", response_model=QualityTrendsResponse)
async def get_quality_trends(
    granularity: str = Query("weekly", description="Time granularity (daily, weekly, monthly)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    dimension: str = Query("overall", description="Quality dimension or 'overall'"),
    db: Session = Depends(get_sync_db),
):
    """Get quality trends over time."""
    if granularity not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Granularity must be one of: daily, weekly, monthly"
        )
    
    valid_dimensions = ["overall", "accuracy", "completeness", "consistency", "timeliness", "relevance"]
    if dimension not in valid_dimensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid dimension. Must be one of: {', '.join(valid_dimensions)}"
        )
    
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )
    
    if not start_dt and not end_dt:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=90)
    elif not start_dt:
        start_dt = end_dt - timedelta(days=90)
    elif not end_dt:
        end_dt = datetime.now()
    
    if dimension == "overall":
        column = Resource.quality_overall
    elif dimension == "accuracy":
        column = Resource.quality_accuracy
    elif dimension == "completeness":
        column = Resource.quality_completeness
    elif dimension == "consistency":
        column = Resource.quality_consistency
    elif dimension == "timeliness":
        column = Resource.quality_timeliness
    elif dimension == "relevance":
        column = Resource.quality_relevance
    
    query = db.query(
        Resource.quality_last_computed,
        column
    ).filter(
        and_(
            Resource.quality_last_computed.isnot(None),
            Resource.quality_last_computed >= start_dt,
            Resource.quality_last_computed <= end_dt,
            column.isnot(None)
        )
    )
    
    results = query.all()
    
    from collections import defaultdict
    period_data = defaultdict(lambda: {"scores": [], "count": 0})
    
    for computed_date, score in results:
        if granularity == "daily":
            period = computed_date.strftime("%Y-%m-%d")
        elif granularity == "weekly":
            period = computed_date.strftime("%Y-W%W")
        else:
            period = computed_date.strftime("%Y-%m")
        
        period_data[period]["scores"].append(score)
        period_data[period]["count"] += 1
    
    data_points = []
    for period in sorted(period_data.keys()):
        scores = period_data[period]["scores"]
        avg_quality = sum(scores) / len(scores) if scores else 0.0
        
        data_points.append(QualityTrendDataPoint(
            period=period,
            avg_quality=avg_quality,
            resource_count=period_data[period]["count"],
        ))
    
    return QualityTrendsResponse(
        dimension=dimension,
        granularity=granularity,
        data_points=data_points,
    )


@router.get("/quality/dimensions", response_model=QualityDimensionsResponse)
async def get_dimension_averages(
    db: Session = Depends(get_sync_db),
):
    """Get average scores per dimension across all resources."""
    dimensions = {}
    
    for dim_name, column in [
        ("accuracy", Resource.quality_accuracy),
        ("completeness", Resource.quality_completeness),
        ("consistency", Resource.quality_consistency),
        ("timeliness", Resource.quality_timeliness),
        ("relevance", Resource.quality_relevance),
    ]:
        stats = db.query(
            func.avg(column).label("avg"),
            func.min(column).label("min"),
            func.max(column).label("max"),
        ).filter(column.isnot(None)).first()
        
        dimensions[dim_name] = DimensionStatistics(
            avg=float(stats.avg) if stats.avg is not None else 0.0,
            min=float(stats.min) if stats.min is not None else 0.0,
            max=float(stats.max) if stats.max is not None else 0.0,
        )
    
    overall_stats = db.query(
        func.avg(Resource.quality_overall).label("avg"),
        func.min(Resource.quality_overall).label("min"),
        func.max(Resource.quality_overall).label("max"),
    ).filter(Resource.quality_overall.isnot(None)).first()
    
    overall = DimensionStatistics(
        avg=float(overall_stats.avg) if overall_stats.avg is not None else 0.0,
        min=float(overall_stats.min) if overall_stats.min is not None else 0.0,
        max=float(overall_stats.max) if overall_stats.max is not None else 0.0,
    )
    
    total_resources = db.query(func.count(Resource.id)).filter(
        Resource.quality_overall.isnot(None)
    ).scalar()
    
    return QualityDimensionsResponse(
        dimensions=dimensions,
        overall=overall,
        total_resources=total_resources or 0,
    )


@router.get("/quality/review-queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    sort_by: str = Query("outlier_score", description="Sort field (outlier_score, quality_overall, updated_at)"),
    db: Session = Depends(get_sync_db),
):
    """Get resources flagged for quality review with priority ranking."""
    if sort_by not in ["outlier_score", "quality_overall", "updated_at"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by must be one of: outlier_score, quality_overall, updated_at"
        )
    
    query = db.query(Resource).filter(Resource.needs_quality_review)
    
    if sort_by == "outlier_score":
        query = query.order_by(Resource.outlier_score.asc().nullslast())
    elif sort_by == "quality_overall":
        query = query.order_by(Resource.quality_overall.asc().nullslast())
    else:
        query = query.order_by(Resource.updated_at.desc())
    
    total = query.count()
    
    offset = (page - 1) * limit
    resources = query.offset(offset).limit(limit).all()
    
    review_queue = []
    for resource in resources:
        outlier_reasons = None
        if resource.outlier_reasons:
            try:
                outlier_reasons = json.loads(resource.outlier_reasons)
            except (json.JSONDecodeError, TypeError):
                outlier_reasons = []
        
        review_queue.append(ReviewQueueItem(
            resource_id=str(resource.id),
            title=resource.title,
            quality_overall=resource.quality_overall,
            is_quality_outlier=resource.is_quality_outlier or False,
            outlier_score=resource.outlier_score,
            outlier_reasons=outlier_reasons,
            quality_last_computed=resource.quality_last_computed,
        ))
    
    return ReviewQueueResponse(
        total=total,
        page=page,
        limit=limit,
        review_queue=review_queue,
    )


@router.get("/quality/health")
async def health_check(
    db: Session = Depends(get_sync_db),
):
    """Health check endpoint for Quality module."""
    from sqlalchemy import text
    
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "module": "quality",
        "database": db_healthy,
        "timestamp": datetime.utcnow().isoformat()
    }
