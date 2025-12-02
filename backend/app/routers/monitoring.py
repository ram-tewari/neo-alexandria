"""
Monitoring and Metrics Router for Phase 11 and Phase 12.5.

Provides endpoints for:
- Performance metrics summary
- Recommendation quality metrics
- User engagement metrics
- NCF model health
- Cache statistics
- Event history (Phase 12.5)
- Worker status (Phase 12.5)
- Database pool status (Phase 12.5)
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.shared.database import get_db, get_pool_status
from backend.app.database.models import (
    UserInteraction,
    RecommendationFeedback,
    UserProfile
)
from backend.app.utils.performance_monitoring import metrics as perf_metrics
from backend.app.ml_monitoring.health_check import check_classification_model_health
from backend.app.shared.event_bus import event_bus
from backend.app.cache.redis_cache import cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Get performance metrics summary.
    
    Returns:
        Dictionary with performance metrics including:
        - Cache hit rate
        - Method execution times
        - Slow query count
        - Recommendation generation metrics
    """
    try:
        summary = perf_metrics.get_summary()
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": summary
        }
    
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/recommendation-quality")
async def get_recommendation_quality_metrics(
    time_window_days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get recommendation quality metrics.
    
    Args:
        time_window_days: Time window for metrics calculation (1-90 days)
        db: Database session
        
    Returns:
        Dictionary with quality metrics including:
        - Click-through rate (CTR) by strategy
        - Average diversity (Gini coefficient)
        - Novelty percentage
        - User satisfaction scores
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        # Get feedback data
        feedback_query = db.query(RecommendationFeedback).filter(
            RecommendationFeedback.recommended_at >= cutoff_date
        )
        
        total_recommendations = feedback_query.count()
        
        if total_recommendations == 0:
            return {
                "status": "ok",
                "message": "No recommendation data available",
                "time_window_days": time_window_days,
                "metrics": {
                    "total_recommendations": 0,
                    "ctr_overall": 0.0,
                    "ctr_by_strategy": {},
                    "avg_diversity": 0.0,
                    "novelty_percentage": 0.0,
                    "user_satisfaction": 0.0
                }
            }
        
        # Calculate CTR overall
        clicked = feedback_query.filter(
            RecommendationFeedback.was_clicked == 1
        ).count()
        ctr_overall = clicked / total_recommendations if total_recommendations > 0 else 0.0
        
        # Calculate CTR by strategy
        strategies = db.query(
            RecommendationFeedback.recommendation_strategy,
            func.count(RecommendationFeedback.id).label('total'),
            func.sum(RecommendationFeedback.was_clicked).label('clicked')
        ).filter(
            RecommendationFeedback.recommended_at >= cutoff_date
        ).group_by(
            RecommendationFeedback.recommendation_strategy
        ).all()
        
        ctr_by_strategy = {}
        for strategy, total, clicked_count in strategies:
            clicked_count = clicked_count or 0
            ctr_by_strategy[strategy] = clicked_count / total if total > 0 else 0.0
        
        # Calculate user satisfaction (from was_useful feedback)
        useful_feedback = feedback_query.filter(
            RecommendationFeedback.was_useful.isnot(None)
        ).all()
        
        if useful_feedback:
            useful_count = sum(1 for f in useful_feedback if f.was_useful == 1)
            user_satisfaction = useful_count / len(useful_feedback)
        else:
            user_satisfaction = 0.0
        
        # Note: Diversity and novelty would need actual recommendation data
        # For now, return placeholder values
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "time_window_days": time_window_days,
            "metrics": {
                "total_recommendations": total_recommendations,
                "total_clicked": clicked,
                "ctr_overall": round(ctr_overall, 4),
                "ctr_by_strategy": {k: round(v, 4) for k, v in ctr_by_strategy.items()},
                "user_satisfaction": round(user_satisfaction, 4),
                "feedback_count": len(useful_feedback)
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting recommendation quality metrics: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/user-engagement")
async def get_user_engagement_metrics(
    time_window_days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user engagement metrics.
    
    Args:
        time_window_days: Time window for metrics calculation (1-90 days)
        db: Database session
        
    Returns:
        Dictionary with engagement metrics including:
        - Total users
        - Active users
        - Total interactions
        - Interactions by type
        - Average session duration
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        # Total users with profiles
        total_users = db.query(UserProfile).count()
        
        # Active users (with interactions in time window)
        active_users = db.query(UserInteraction.user_id).filter(
            UserInteraction.interaction_timestamp >= cutoff_date
        ).distinct().count()
        
        # Total interactions
        total_interactions = db.query(UserInteraction).filter(
            UserInteraction.interaction_timestamp >= cutoff_date
        ).count()
        
        # Interactions by type
        interactions_by_type = db.query(
            UserInteraction.interaction_type,
            func.count(UserInteraction.id).label('count')
        ).filter(
            UserInteraction.interaction_timestamp >= cutoff_date
        ).group_by(
            UserInteraction.interaction_type
        ).all()
        
        interaction_breakdown = {
            itype: count for itype, count in interactions_by_type
        }
        
        # Average session duration
        avg_session = db.query(
            func.avg(UserProfile.avg_session_duration)
        ).scalar()
        
        # Positive interaction rate
        positive_interactions = db.query(UserInteraction).filter(
            UserInteraction.interaction_timestamp >= cutoff_date,
            UserInteraction.is_positive == 1
        ).count()
        
        positive_rate = positive_interactions / total_interactions if total_interactions > 0 else 0.0
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "time_window_days": time_window_days,
            "metrics": {
                "total_users": total_users,
                "active_users": active_users,
                "total_interactions": total_interactions,
                "positive_interactions": positive_interactions,
                "positive_rate": round(positive_rate, 4),
                "interactions_by_type": interaction_breakdown,
                "avg_session_duration_seconds": round(avg_session, 2) if avg_session else 0.0
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting user engagement metrics: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/model-health")
async def get_model_health() -> Dict[str, Any]:
    """
    Get NCF model health metrics.
    
    Returns:
        Dictionary with model health information including:
        - Model availability
        - Model size (users, items)
        - Last training date
        - Prediction statistics
    """
    try:
        import os
        from pathlib import Path
        
        # Check if model file exists
        backend_dir = Path(__file__).parent.parent.parent
        model_path = os.path.join(backend_dir, "models", "ncf_model.pt")
        
        model_exists = os.path.exists(model_path)
        
        if model_exists:
            # Get model file info
            model_stat = os.stat(model_path)
            model_size_mb = model_stat.st_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(model_stat.st_mtime)
            
            # Try to load model info
            try:
                import torch
                checkpoint = torch.load(model_path, map_location='cpu')
                
                return {
                    "status": "ok",
                    "timestamp": datetime.utcnow().isoformat(),
                    "model": {
                        "available": True,
                        "path": model_path,
                        "size_mb": round(model_size_mb, 2),
                        "last_modified": last_modified.isoformat(),
                        "num_users": checkpoint.get('num_users', 0),
                        "num_items": checkpoint.get('num_items', 0),
                        "embedding_dim": checkpoint.get('embedding_dim', 64)
                    }
                }
            except Exception as e:
                return {
                    "status": "warning",
                    "timestamp": datetime.utcnow().isoformat(),
                    "model": {
                        "available": True,
                        "path": model_path,
                        "size_mb": round(model_size_mb, 2),
                        "last_modified": last_modified.isoformat(),
                        "error": f"Could not load model details: {str(e)}"
                    }
                }
        else:
            return {
                "status": "warning",
                "timestamp": datetime.utcnow().isoformat(),
                "model": {
                    "available": False,
                    "message": "NCF model not trained yet. System will use content-based and graph-based recommendations."
                }
            }
    
    except Exception as e:
        logger.error(f"Error getting model health: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/ml")
async def ml_model_health_check() -> Dict[str, Any]:
    """
    Health check for ML classification model.
    
    Returns:
        Dictionary with ML model health status including:
        - Model loaded status
        - Checkpoint validity
        - Inference functionality
        - Latency metrics
    
    Returns 200 if healthy, 503 if unhealthy.
    """
    try:
        # Import classification service
        from backend.app.services.ml_classification_service import MLClassificationService
        
        # Initialize service (will load model if available)
        try:
            service = MLClassificationService()
            
            # Run health check
            health_results = check_classification_model_health(service)
            
            # Determine HTTP status code
            if health_results["overall_healthy"]:
                status_code = 200
                status = "healthy"
            else:
                status_code = 503
                status = "unhealthy"
            
            return {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": health_results,
                "http_status": status_code
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize ML classification service: {str(e)}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": f"Failed to initialize service: {str(e)}",
                "checks": {
                    "model_loaded": False,
                    "checkpoint_valid": False,
                    "inference_working": False,
                    "latency_acceptable": False,
                    "overall_healthy": False
                },
                "http_status": 503
            }
    
    except Exception as e:
        logger.error(f"ML health check failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "http_status": 503
        }


@router.get("/database")
async def get_database_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive database metrics including connection pool status,
    database type, and health information.
    
    This endpoint provides detailed monitoring data for database operations,
    including connection pool utilization, database type detection, and
    PostgreSQL-specific metrics when applicable.
    
    Args:
        db: Database session for connectivity check
        
    Returns:
        Dictionary with database metrics including:
        - database_type: Type of database (sqlite/postgresql)
        - connection_pool: Detailed pool statistics
        - health: Database connectivity status
        - warnings: Any warnings about pool capacity or performance
    """
    try:
        # Get pool statistics
        pool_stats = get_pool_status()
        
        # Check database connectivity
        try:
            db.execute("SELECT 1")
            db_healthy = True
            health_message = "Database connection healthy"
        except Exception as e:
            db_healthy = False
            health_message = f"Database connection failed: {str(e)}"
            logger.error(f"Database health check failed: {str(e)}")
        
        # Check for pool capacity warnings
        warnings = []
        if pool_stats["pool_usage_percent"] > 90:
            warnings.append({
                "level": "warning",
                "message": f"Connection pool near capacity: {pool_stats['pool_usage_percent']:.1f}% in use",
                "recommendation": "Consider increasing pool size or investigating connection leaks"
            })
        elif pool_stats["pool_usage_percent"] > 75:
            warnings.append({
                "level": "info",
                "message": f"Connection pool usage elevated: {pool_stats['pool_usage_percent']:.1f}% in use",
                "recommendation": "Monitor pool usage trends"
            })
        
        # Build response
        response = {
            "status": "ok" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "type": pool_stats["database_type"],
                "healthy": db_healthy,
                "health_message": health_message
            },
            "connection_pool": pool_stats,
            "warnings": warnings
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error getting database metrics: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/db/pool")
async def get_db_pool_status() -> Dict[str, Any]:
    """
    Get database connection pool statistics.
    
    Returns detailed metrics about the current state of the database
    connection pool for monitoring and capacity planning.
    
    Returns:
        Dictionary with connection pool statistics including:
        - size: Total pool size (base connections)
        - checked_in: Number of connections available in the pool
        - checked_out: Number of connections currently in use
        - overflow: Number of overflow connections in use
        - total: Total connections (size + overflow)
        - utilization: Percentage of pool capacity in use
    """
    try:
        pool_stats = get_pool_status()
        
        # Calculate utilization percentage
        # overflow can be negative (available overflow capacity), so use max(0, overflow)
        max_connections = 60  # pool_size (20) + max_overflow (40)
        active_overflow = max(0, pool_stats["overflow"])
        utilization = (pool_stats["checked_out"] + active_overflow) / max_connections * 100
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "pool": {
                **pool_stats,
                "max_connections": max_connections,
                "utilization_percent": round(max(0, utilization), 2)
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting database pool status: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/events")
async def get_event_bus_metrics() -> Dict[str, Any]:
    """
    Get comprehensive event bus metrics for monitoring.
    
    Returns detailed metrics about event bus performance including:
    - Total events emitted and delivered
    - Handler error counts
    - Event type breakdown
    - Handler latency percentiles (p50, p95, p99)
    
    These metrics are essential for monitoring inter-module communication
    health and identifying performance bottlenecks in event-driven flows.
    
    Returns:
        Dictionary with event bus metrics including:
        - events_emitted: Total events emitted
        - events_delivered: Total successful handler executions
        - handler_errors: Total handler failures
        - event_types: Breakdown of events by type
        - handler_latency_p50: 50th percentile latency (ms)
        - handler_latency_p95: 95th percentile latency (ms)
        - handler_latency_p99: 99th percentile latency (ms)
    """
    try:
        metrics = event_bus.get_metrics()
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
    
    except Exception as e:
        logger.error(f"Error getting event bus metrics: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/events/history")
async def get_event_history(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of events to return")
) -> Dict[str, Any]:
    """
    Get recent event history from the event system.
    
    Returns the most recent events emitted by the system, useful for
    debugging, auditing, and understanding system behavior.
    
    Args:
        limit: Maximum number of events to return (default: 100, max: 1000)
        
    Returns:
        Dictionary with event history including:
        - events: List of recent events with name, data, timestamp, priority
        - count: Number of events returned
        - timestamp: When the query was executed
    """
    try:
        events = event_bus.get_event_history(limit=limit)
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(events),
            "events": events
        }
    
    except Exception as e:
        logger.error(f"Error getting event history: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache performance statistics.
    
    Returns detailed metrics about cache performance including hit rate,
    miss rate, and invalidation counts. These metrics help evaluate
    caching effectiveness and identify optimization opportunities.
    
    Returns:
        Dictionary with cache statistics including:
        - hit_rate: Percentage of cache hits (0.0 to 1.0)
        - hits: Total number of cache hits
        - misses: Total number of cache misses
        - invalidations: Total number of cache invalidations
        - total_requests: Total cache requests (hits + misses)
        - hit_rate_percent: Hit rate as percentage (0-100)
    """
    try:
        hit_rate = cache.stats.hit_rate()
        total_requests = cache.stats.hits + cache.stats.misses
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "cache_stats": {
                "hit_rate": round(hit_rate, 4),
                "hit_rate_percent": round(hit_rate * 100, 2),
                "hits": cache.stats.hits,
                "misses": cache.stats.misses,
                "invalidations": cache.stats.invalidations,
                "total_requests": total_requests
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting cache statistics: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/workers/status")
async def get_worker_status() -> Dict[str, Any]:
    """
    Get Celery worker status and task information.
    
    Returns information about active Celery workers, their current tasks,
    scheduled tasks, and worker statistics. Useful for monitoring
    distributed task processing and worker health.
    
    Returns:
        Dictionary with worker information including:
        - active: Currently executing tasks by worker
        - scheduled: Tasks scheduled for future execution
        - stats: Worker statistics (processed tasks, etc.)
        - worker_count: Number of active workers
    """
    try:
        from backend.app.tasks.celery_app import celery_app
        
        # Get Celery inspector
        inspect = celery_app.control.inspect()
        
        # Get worker information
        active_tasks = inspect.active() or {}
        scheduled_tasks = inspect.scheduled() or {}
        worker_stats = inspect.stats() or {}
        
        # Count active workers
        worker_count = len(worker_stats)
        
        # Count total active and scheduled tasks
        total_active = sum(len(tasks) for tasks in active_tasks.values())
        total_scheduled = sum(len(tasks) for tasks in scheduled_tasks.values())
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "workers": {
                "worker_count": worker_count,
                "total_active_tasks": total_active,
                "total_scheduled_tasks": total_scheduled,
                "active_tasks": active_tasks,
                "scheduled_tasks": scheduled_tasks,
                "stats": worker_stats
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting worker status: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "message": "Could not connect to Celery workers. Ensure Redis and workers are running.",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Overall health check for Phase 11 recommendation system.
    
    Returns:
        Dictionary with overall system health status
    """
    try:
        # Check database connectivity
        db.execute("SELECT 1")
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_healthy = False
    
    # Check model availability
    import os
    from pathlib import Path
    backend_dir = Path(__file__).parent.parent.parent
    model_path = os.path.join(backend_dir, "models", "ncf_model.pt")
    model_available = os.path.exists(model_path)
    
    # Overall status
    if db_healthy:
        if model_available:
            status = "healthy"
            message = "All systems operational"
        else:
            status = "degraded"
            message = "Database healthy, NCF model not available (using fallback recommendations)"
    else:
        status = "unhealthy"
        message = "Database connection failed"
    
    return {
        "status": status,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "ncf_model": "available" if model_available else "unavailable",
            "api": "healthy"
        }
    }
