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

Basic health check endpoint for load balancers and orchestration systems.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "error": "Database connection failed"
}
```

**Use Cases:**
- Kubernetes liveness probes
- Load balancer health checks
- Uptime monitoring

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
  "resources": {
    "total": 10000,
    "by_status": {
      "completed": 9500,
      "pending": 300,
      "failed": 200
    },
    "by_type": {
      "article": 6000,
      "paper": 3000,
      "book": 1000
    }
  },
  "collections": {
    "total": 500,
    "by_visibility": {
      "private": 300,
      "public": 150,
      "shared": 50
    }
  },
  "annotations": {
    "total": 25000,
    "by_user_count": 150
  },
  "search": {
    "queries_last_hour": 1500,
    "avg_latency_ms": 145
  },
  "quality": {
    "avg_score": 0.72,
    "outliers_count": 42,
    "review_queue_size": 87
  },
  "timestamp": "2024-01-01T10:00:00Z"
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
  "type": "postgresql",
  "version": "15.2",
  "connection": {
    "status": "connected",
    "pool_size": 10,
    "active_connections": 3,
    "idle_connections": 7
  },
  "tables": {
    "resources": {
      "row_count": 10000,
      "size_mb": 256
    },
    "annotations": {
      "row_count": 25000,
      "size_mb": 64
    },
    "collections": {
      "row_count": 500,
      "size_mb": 8
    }
  },
  "indexes": {
    "total": 45,
    "size_mb": 128
  },
  "timestamp": "2024-01-01T10:00:00Z"
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

### Prometheus Metrics (Planned)

Future releases will expose Prometheus-compatible metrics at `/metrics`:

```
# HELP neo_alexandria_resources_total Total number of resources
# TYPE neo_alexandria_resources_total gauge
neo_alexandria_resources_total 10000

# HELP neo_alexandria_search_latency_seconds Search latency histogram
# TYPE neo_alexandria_search_latency_seconds histogram
neo_alexandria_search_latency_seconds_bucket{le="0.1"} 500
neo_alexandria_search_latency_seconds_bucket{le="0.2"} 1200
```

### Alerting Rules (Example)

```yaml
groups:
  - name: neo-alexandria
    rules:
      - alert: HighSearchLatency
        expr: neo_alexandria_search_latency_seconds > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High search latency detected"
          
      - alert: DatabaseConnectionPoolExhausted
        expr: neo_alexandria_db_pool_available == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool exhausted"
```

## Health Check Best Practices

1. **Use `/health` for simple checks** - Fast, lightweight, suitable for frequent polling
2. **Use `/monitoring/status` for detailed checks** - More comprehensive, use for debugging
3. **Set appropriate timeouts** - Health checks should respond within 5 seconds
4. **Monitor trends** - Track metrics over time to identify degradation

## Related Documentation

- [API Overview](overview.md) - Authentication, errors
- [Architecture Overview](../architecture/overview.md) - System design
- [Deployment Guide](../guides/deployment.md) - Production setup
