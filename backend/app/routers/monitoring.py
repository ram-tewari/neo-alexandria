"""
Monitoring and Metrics Router for Phase 11.

Provides endpoints for:
- Performance metrics summary
- Recommendation quality metrics
- User engagement metrics
- NCF model health
- Cache statistics
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database.base import get_db
from backend.app.database.models import (
    UserInteraction,
    RecommendationFeedback,
    UserProfile
)
from backend.app.utils.performance_monitoring import metrics as perf_metrics
from backend.app.utils.recommendation_metrics import (
    compute_ctr,
    compute_gini_coefficient,
    compute_novelty_score
)

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
