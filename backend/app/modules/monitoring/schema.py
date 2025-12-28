"""
Monitoring Schemas

Pydantic models for monitoring API requests and responses.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class PerformanceMetrics(BaseModel):
    """Performance metrics response."""
    status: str
    timestamp: str
    metrics: Dict[str, Any]


class RecommendationQualityMetrics(BaseModel):
    """Recommendation quality metrics response."""
    status: str
    timestamp: str
    time_window_days: int
    metrics: Dict[str, Any]
    message: Optional[str] = None


class UserEngagementMetrics(BaseModel):
    """User engagement metrics response."""
    status: str
    timestamp: str
    time_window_days: int
    metrics: Dict[str, Any]


class ModelHealthMetrics(BaseModel):
    """Model health metrics response."""
    status: str
    timestamp: str
    model: Dict[str, Any]
    error: Optional[str] = None


class DatabaseMetrics(BaseModel):
    """Database metrics response."""
    status: str
    timestamp: str
    database: Dict[str, Any]
    connection_pool: Dict[str, Any]
    warnings: List[Dict[str, str]]
    error: Optional[str] = None


class EventBusMetrics(BaseModel):
    """Event bus metrics response."""
    status: str
    timestamp: str
    metrics: Dict[str, Any]
    error: Optional[str] = None


class CacheStats(BaseModel):
    """Cache statistics response."""
    status: str
    timestamp: str
    cache_stats: Dict[str, Any]
    error: Optional[str] = None


class WorkerStatus(BaseModel):
    """Worker status response."""
    status: str
    timestamp: str
    workers: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
    timestamp: str
    components: Dict[str, str]
    error: Optional[str] = None
