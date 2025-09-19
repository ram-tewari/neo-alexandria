"""
Neo Alexandria 2.0 - Performance Monitoring

This module provides performance monitoring and metrics collection using Prometheus.
It tracks request durations, error rates, and custom business metrics.

Related files:
- app/__init__.py: FastAPI app initialization with monitoring
- app/routers/: API endpoints that are automatically monitored
- app/services/: Business logic services with custom metrics

Features:
- Request duration tracking
- Error rate monitoring
- Custom business metrics (ingestion success/failure rates)
- Database query performance tracking
- AI processing time monitoring
"""

import time
import asyncio
from typing import Callable, Any
from functools import wraps

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse


# Custom Prometheus metrics
REQUEST_DURATION = Histogram(
    'neo_alexandria_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint', 'status_code']
)

REQUEST_COUNT = Counter(
    'neo_alexandria_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

INGESTION_SUCCESS = Counter(
    'neo_alexandria_ingestion_success_total',
    'Total successful resource ingestions'
)

INGESTION_FAILURE = Counter(
    'neo_alexandria_ingestion_failure_total',
    'Total failed resource ingestions',
    ['error_type']
)

AI_PROCESSING_TIME = Histogram(
    'neo_alexandria_ai_processing_seconds',
    'AI processing time in seconds',
    ['operation']  # 'summarize', 'tag', 'classify'
)

DATABASE_QUERY_TIME = Histogram(
    'neo_alexandria_database_query_seconds',
    'Database query execution time in seconds',
    ['operation']  # 'select', 'insert', 'update', 'delete'
)

ACTIVE_INGESTIONS = Gauge(
    'neo_alexandria_active_ingestions',
    'Number of currently active ingestion processes'
)

CACHE_HITS = Counter(
    'neo_alexandria_cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'neo_alexandria_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)


def setup_monitoring(app) -> Instrumentator:
    """
    Set up Prometheus monitoring for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Instrumentator: Configured Prometheus instrumentator
    """
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="neo_alexandria_inprogress",
        inprogress_labels=True,
    )
    
    # Add custom metrics
    instrumentator.add(metrics.default())
    
    # Add custom business metrics
    instrumentator.add(custom_metrics)
    
    # Instrument the app
    instrumentator.instrument(app)
    
    # Add metrics endpoint
    @app.get("/metrics")
    async def metrics_endpoint():
        """Prometheus metrics endpoint."""
        return PlainTextResponse(
            generate_latest(),
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    
    return instrumentator


def custom_metrics(request: Request, response: Response) -> None:
    """
    Add custom metrics for business logic tracking.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
    """
    # Track request duration and count
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).observe(0)  # Duration is handled by default metrics
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()


def track_ai_processing(operation: str):
    """
    Decorator to track AI processing time.
    
    Args:
        operation: The AI operation being performed ('summarize', 'tag', 'classify')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                AI_PROCESSING_TIME.labels(operation=operation).observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                AI_PROCESSING_TIME.labels(operation=operation).observe(duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def track_database_query(operation: str):
    """
    Decorator to track database query performance.
    
    Args:
        operation: The database operation being performed ('select', 'insert', 'update', 'delete')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                DATABASE_QUERY_TIME.labels(operation=operation).observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                DATABASE_QUERY_TIME.labels(operation=operation).observe(duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def track_ingestion_success():
    """Track successful resource ingestion."""
    INGESTION_SUCCESS.inc()


def track_ingestion_failure(error_type: str):
    """
    Track failed resource ingestion.
    
    Args:
        error_type: Type of error that caused the failure
    """
    INGESTION_FAILURE.labels(error_type=error_type).inc()


def track_cache_hit(cache_type: str):
    """
    Track cache hit.
    
    Args:
        cache_type: Type of cache ('ai_model', 'classification', 'quality')
    """
    CACHE_HITS.labels(cache_type=cache_type).inc()


def track_cache_miss(cache_type: str):
    """
    Track cache miss.
    
    Args:
        cache_type: Type of cache ('ai_model', 'classification', 'quality')
    """
    CACHE_MISSES.labels(cache_type=cache_type).inc()


def increment_active_ingestions():
    """Increment the number of active ingestion processes."""
    ACTIVE_INGESTIONS.inc()


def decrement_active_ingestions():
    """Decrement the number of active ingestion processes."""
    ACTIVE_INGESTIONS.dec()
