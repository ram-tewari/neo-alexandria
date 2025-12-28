# Monitoring Module

## Purpose

The Monitoring module provides comprehensive system health monitoring, metrics aggregation, and observability features for Neo Alexandria 2.0. It aggregates metrics from all other modules and provides a unified view of system health.

## Responsibilities

- System health monitoring
- Performance metrics collection
- Database connection pool monitoring
- Event bus metrics aggregation
- Cache statistics tracking
- ML model health checks
- Worker status monitoring
- User engagement metrics
- Recommendation quality metrics

## Public Interface

### Router
- `monitoring_router`: FastAPI router with 12 monitoring endpoints

### Service
- `MonitoringService`: Core service for metrics collection and aggregation

### Schemas
- `PerformanceMetrics`: Performance metrics response
- `RecommendationQualityMetrics`: Recommendation quality metrics
- `UserEngagementMetrics`: User engagement metrics
- `ModelHealthMetrics`: ML model health status
- `DatabaseMetrics`: Database and connection pool metrics
- `EventBusMetrics`: Event bus performance metrics
- `CacheStats`: Cache performance statistics
- `WorkerStatus`: Celery worker status
- `HealthCheckResponse`: Overall health check response

## API Endpoints

### Performance Monitoring
- `GET /api/monitoring/performance` - Get performance metrics summary
- `GET /api/monitoring/recommendation-quality` - Get recommendation quality metrics
- `GET /api/monitoring/user-engagement` - Get user engagement metrics

### System Health
- `GET /api/monitoring/health` - Overall system health check
- `GET /api/monitoring/health/ml` - ML model health check
- `GET /api/monitoring/model-health` - NCF model health metrics

### Infrastructure
- `GET /api/monitoring/database` - Database metrics and pool status
- `GET /api/monitoring/db/pool` - Connection pool statistics
- `GET /api/monitoring/events` - Event bus metrics
- `GET /api/monitoring/events/history` - Recent event history
- `GET /api/monitoring/cache/stats` - Cache performance statistics
- `GET /api/monitoring/workers/status` - Celery worker status

## Events

### Subscribed Events
The monitoring module subscribes to ALL events for metrics aggregation:
- `resource.*` - Resource lifecycle events
- `collection.*` - Collection events
- `search.*` - Search events
- `annotation.*` - Annotation events
- `quality.*` - Quality assessment events
- `taxonomy.*` - Classification events
- `graph.*` - Graph and citation events
- `recommendation.*` - Recommendation events
- `curation.*` - Curation events

### Emitted Events
- `monitoring.alert_triggered` - When a monitoring threshold is exceeded
- `monitoring.health_degraded` - When system health degrades

## Dependencies

### Shared Kernel
- `shared.database`: Database session and pool status
- `shared.event_bus`: Event bus metrics
- `shared.cache`: Cache statistics

### External Dependencies
- `prometheus_client`: Metrics collection
- `sqlalchemy`: Database queries for metrics

## Module Structure

```
monitoring/
├── __init__.py          # Public interface
├── README.md            # This file
├── router.py            # API endpoints
├── service.py           # Monitoring service
├── schema.py            # Pydantic schemas
└── handlers.py          # Event handlers for metrics aggregation
```

## Usage Examples

### Get System Health
```python
from app.modules.monitoring import MonitoringService

service = MonitoringService()
health = await service.get_system_health(db)
print(f"System status: {health['status']}")
```

### Get Performance Metrics
```python
from app.modules.monitoring import monitoring_router

# Via API
GET /api/monitoring/performance
```

### Monitor Event Bus
```python
from app.modules.monitoring import MonitoringService

service = MonitoringService()
metrics = await service.get_event_bus_metrics()
print(f"Events emitted: {metrics['events_emitted']}")
```

## Design Decisions

### Aggregation Module
The monitoring module is an aggregation module that:
- Subscribes to all events for metrics collection
- Does not emit domain events (only monitoring alerts)
- Provides read-only views of system state
- Does not modify other modules' data

### Module Health Checks
Each module can register a health check function that the monitoring module calls to determine module-specific health status.

### Metrics Storage
Metrics are stored in-memory using Prometheus client library. For persistent metrics, use external Prometheus server.

## Version History

- 1.0.0: Initial extraction from layered architecture
  - Migrated from `routers/monitoring.py`
  - Consolidated monitoring services
  - Added event-driven metrics aggregation
  - Implemented module health checks
