"""
Monitoring Module

This module provides system health monitoring, metrics aggregation, and
observability features for Neo Alexandria 2.0.

Public Interface:
- monitoring_router: FastAPI router with monitoring endpoints
- MonitoringService: Service for metrics collection and aggregation
- Schema classes: Request/response models for monitoring endpoints

Events Subscribed:
- All events (for metrics aggregation)

Events Emitted:
- monitoring.alert_triggered: When a monitoring threshold is exceeded
- monitoring.health_degraded: When system health degrades

Module Metadata:
- Version: 1.0.0
- Domain: monitoring
- Dependencies: shared kernel only
"""

__version__ = "1.0.0"
__domain__ = "monitoring"

from .router import router as monitoring_router
from .service import MonitoringService, register_module_health_check
from .schema import (
    PerformanceMetrics,
    RecommendationQualityMetrics,
    UserEngagementMetrics,
    ModelHealthMetrics,
    DatabaseMetrics,
    EventBusMetrics,
    CacheStats,
    WorkerStatus,
    HealthCheckResponse,
)
from .handlers import register_handlers

__all__ = [
    "monitoring_router",
    "MonitoringService",
    "register_module_health_check",
    "PerformanceMetrics",
    "RecommendationQualityMetrics",
    "UserEngagementMetrics",
    "ModelHealthMetrics",
    "DatabaseMetrics",
    "EventBusMetrics",
    "CacheStats",
    "WorkerStatus",
    "HealthCheckResponse",
    "register_handlers",
]
