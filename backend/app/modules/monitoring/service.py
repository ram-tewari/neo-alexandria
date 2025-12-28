"""
Monitoring Service

Provides comprehensive monitoring and metrics collection for the system.
"""

import logging
import os
from typing import Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import func

from ...shared.database import get_pool_status
from ...shared.event_bus import event_bus
from ...shared.cache import cache
from ...database.models import (
    UserInteraction,
    RecommendationFeedback,
    UserProfile
)
from ...utils.performance_monitoring import metrics as perf_metrics
from ...ml_monitoring.health_check import check_classification_model_health

logger = logging.getLogger(__name__)


# Registry for module health check functions
_module_health_checks = {}


def register_module_health_check(module_name: str, health_check_func):
    """
    Register a health check function for a module.
    
    Args:
        module_name: Name of the module
        health_check_func: Function that returns health status dict
    """
    _module_health_checks[module_name] = health_check_func
    logger.info(f"Registered health check for module: {module_name}")


class MonitoringService:
    """Service for monitoring and metrics collection."""
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics summary.
        
        Returns:
            Dictionary with performance metrics
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
    
    async def get_recommendation_quality_metrics(
        self,
        db: Session,
        time_window_days: int
    ) -> Dict[str, Any]:
        """
        Get recommendation quality metrics.
        
        Args:
            db: Database session
            time_window_days: Time window for metrics calculation
            
        Returns:
            Dictionary with quality metrics
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
    
    async def get_user_engagement_metrics(
        self,
        db: Session,
        time_window_days: int
    ) -> Dict[str, Any]:
        """
        Get user engagement metrics.
        
        Args:
            db: Database session
            time_window_days: Time window for metrics calculation
            
        Returns:
            Dictionary with engagement metrics
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
    
    async def get_model_health(self) -> Dict[str, Any]:
        """
        Get NCF model health metrics.
        
        Returns:
            Dictionary with model health information
        """
        try:
            # Check if model file exists
            backend_dir = Path(__file__).parent.parent.parent.parent
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
    
    async def ml_model_health_check(self) -> Dict[str, Any]:
        """
        Health check for ML classification model.
        
        Returns:
            Dictionary with ML model health status
        """
        try:
            # Import classification service
            from ...services.ml_classification_service import MLClassificationService
            
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
    
    async def get_database_metrics(self, db: Session) -> Dict[str, Any]:
        """
        Get comprehensive database metrics.
        
        Args:
            db: Database session for connectivity check
            
        Returns:
            Dictionary with database metrics
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
    
    async def get_db_pool_status(self) -> Dict[str, Any]:
        """
        Get database connection pool statistics.
        
        Returns:
            Dictionary with connection pool statistics
        """
        try:
            pool_stats = get_pool_status()
            
            # Calculate utilization percentage
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
    
    async def get_event_bus_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive event bus metrics.
        
        Returns:
            Dictionary with event bus metrics
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
    
    async def get_event_history(self, limit: int) -> Dict[str, Any]:
        """
        Get recent event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            Dictionary with event history
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
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with cache statistics
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
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """
        Get Celery worker status.
        
        Returns:
            Dictionary with worker information
        """
        try:
            from ...tasks.celery_app import celery_app
            
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
    
    async def health_check(self, db: Session) -> Dict[str, Any]:
        """
        Overall health check for the system.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with overall system health status
        """
        try:
            # Check database connectivity
            try:
                db.execute("SELECT 1")
                db_healthy = True
            except Exception as e:
                logger.error(f"Database health check failed: {str(e)}")
                db_healthy = False
            
            # Check model availability
            backend_dir = Path(__file__).parent.parent.parent.parent
            model_path = os.path.join(backend_dir, "models", "ncf_model.pt")
            model_available = os.path.exists(model_path)
            
            # Check all registered modules
            module_health = {}
            for module_name, health_check_func in _module_health_checks.items():
                try:
                    module_health[module_name] = health_check_func()
                except Exception as e:
                    logger.error(f"Health check failed for module {module_name}: {str(e)}")
                    module_health[module_name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            
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
            
            # Check if any modules are unhealthy
            unhealthy_modules = [
                name for name, health in module_health.items()
                if health.get("status") == "unhealthy"
            ]
            
            if unhealthy_modules:
                status = "degraded"
                message = f"Some modules unhealthy: {', '.join(unhealthy_modules)}"
            
            response = {
                "status": status,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "database": "healthy" if db_healthy else "unhealthy",
                    "ncf_model": "available" if model_available else "unavailable",
                    "api": "healthy"
                }
            }
            
            # Add module health if any modules are registered
            if module_health:
                response["modules"] = module_health
            
            return response
        
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_module_health(self, module_name: str) -> Dict[str, Any]:
        """
        Get health status for a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Dictionary with module health status
        """
        try:
            if module_name not in _module_health_checks:
                return {
                    "status": "error",
                    "error": f"Module {module_name} not registered",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            health_check_func = _module_health_checks[module_name]
            health_status = health_check_func()
            
            return {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
                "module": module_name,
                "health": health_status
            }
        
        except Exception as e:
            logger.error(f"Error getting module health for {module_name}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
