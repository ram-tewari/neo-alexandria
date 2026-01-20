# Monitoring API

System monitoring, health checks, and metrics endpoints.

## Overview

The Monitoring API provides:
- Health check endpoints for load balancers
- System metrics and statistics
- Database connection monitoring
- Service status information

## Endpoints

### GET /health

Overall health check for the system. Returns detailed status of all components.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "message": "System is healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "details": "Connected"
    },
    "cache": {
      "status": "healthy",
      "details": "Connected"
    },
    "event_bus": {
      "status": "healthy",
      "details": "Operational"
    }
  },
  "modules": {
    "auth": "healthy",
    "resources": "healthy",
    "search": "healthy"
  }
}
```

**Use Cases:**
- Kubernetes liveness/readiness probes
- Load balancer health checks
- System status dashboard

**Example:**
```bash
curl http://127.0.0.1:8000/health
```

---

### GET /monitoring/status

Detailed system status with component health information.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.9.0",
  "uptime_seconds": 86400,
  "components": {
    "database": {
      "status": "healthy",
      "type": "postgresql",
      "connection_pool": {
        "size": 10,
        "available": 8,
        "in_use": 2
      }
    },
    "cache": {
      "status": "healthy",
      "type": "redis",
      "connected": true
    },
    "ml_models": {
      "status": "healthy",
      "embedding_model": "loaded",
      "classification_model": "loaded"
    }
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/monitoring/status
```

---

### GET /monitoring/metrics

System metrics and statistics.

**Response (200 OK):**
```json
{
  "status": "success",
  "timestamp": "2024-01-01T10:00:00Z",
  "metrics": {
    "resources": {
      "total": 10000,
      "by_status": {
        "completed": 9500,
        "pending": 300,
        "failed": 200
      }
    },
    "search": {
      "queries_last_hour": 1500,
      "avg_latency_ms": 145
    },
    "quality": {
      "avg_score": 0.72
    }
  }
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/monitoring/metrics
```

---

### GET /monitoring/database

Database-specific monitoring information.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "database": {
    "type": "postgresql",
    "version": "15.2",
    "connection_status": "connected"
  },
  "connection_pool": {
    "size": 10,
    "active": 3,
    "idle": 7,
    "overflow": 0
  },
  "warnings": []
}
```

---

### GET /monitoring/performance

Get performance metrics summary.

**Response:**
```json
{
  "status": "success",
  "timestamp": "2024-01-01T10:00:00Z",
  "metrics": {
    "cache_hit_rate": 0.85,
    "avg_response_time_ms": 120,
    "slow_query_count": 5
  }
}
```

---

### GET /monitoring/workers/status

Get Celery worker status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "workers": {
    "celery@worker1": {
      "active": [],
      "stats": {
        "processed": 150
      }
    }
  }
}
```

---

## Integration Examples

### Kubernetes Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Kubernetes Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /monitoring/status
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

## Module Structure

**Module**: `app.modules.monitoring`  
**Router Prefix**: `/api/monitoring`, `/health`  
**Version**: 1.0.0

```python
from app.modules.monitoring import (
    monitoring_router,
    MonitoringService,
    HealthStatus,
    SystemMetrics
)
```

## Related Documentation

- [API Overview](overview.md) - Authentication, errors
- [Architecture Overview](../architecture/overview.md) - System design
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Deployment Guide](../guides/deployment.md) - Production setup
