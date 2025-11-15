# Phase 11 Monitoring Setup Guide

This guide explains how to set up monitoring for the Neo Alexandria Phase 11 Hybrid Recommendation Engine.

## Overview

Phase 11 includes comprehensive monitoring infrastructure:

1. **Performance Monitoring** - Track method execution times, cache performance, slow queries
2. **Prometheus Metrics** - Industry-standard metrics collection
3. **Custom Metrics API** - RESTful endpoints for monitoring dashboards
4. **Grafana Dashboards** - Pre-configured visualization dashboards

## Quick Start

### 1. Built-in Monitoring Endpoints

The application includes built-in monitoring endpoints that work out of the box:

```bash
# Health check
GET http://localhost:8000/api/monitoring/health

# Performance metrics
GET http://localhost:8000/api/monitoring/performance

# Recommendation quality metrics
GET http://localhost:8000/api/monitoring/recommendation-quality?time_window_days=7

# User engagement metrics
GET http://localhost:8000/api/monitoring/user-engagement?time_window_days=7

# NCF model health
GET http://localhost:8000/api/monitoring/model-health
```

### 2. Prometheus Metrics

Prometheus-compatible metrics are exposed at:

```bash
GET http://localhost:8000/metrics
```

## Detailed Setup

### Option 1: Built-in Monitoring (No External Tools)

Use the built-in monitoring API endpoints:

```python
import requests

# Get overall health
response = requests.get("http://localhost:8000/api/monitoring/health")
health = response.json()
print(f"Status: {health['status']}")

# Get performance metrics
response = requests.get("http://localhost:8000/api/monitoring/performance")
metrics = response.json()
print(f"Cache hit rate: {metrics['metrics']['cache_hit_rate']:.2%}")

# Get recommendation quality
response = requests.get("http://localhost:8000/api/monitoring/recommendation-quality")
quality = response.json()
print(f"CTR: {quality['metrics']['ctr_overall']:.2%}")
```

### Option 2: Prometheus + Grafana (Full Stack)

#### Install Prometheus

1. Download Prometheus from https://prometheus.io/download/

2. Use the provided configuration:
   ```bash
   cd backend/monitoring
   prometheus --config.file=prometheus_config.yml
   ```

3. Access Prometheus UI at http://localhost:9090

#### Install Grafana

1. Download Grafana from https://grafana.com/grafana/download

2. Start Grafana:
   ```bash
   # Linux/Mac
   grafana-server
   
   # Windows
   grafana-server.exe
   ```

3. Access Grafana at http://localhost:3000 (default: admin/admin)

4. Add Prometheus data source:
   - Configuration → Data Sources → Add data source
   - Select Prometheus
   - URL: http://localhost:9090
   - Save & Test

5. Import dashboard:
   - Dashboards → Import
   - Upload `grafana_dashboard.json`
   - Select Prometheus data source
   - Import

## Metrics Reference

### Performance Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `cache_hit_rate` | Percentage of cache hits | >80% |
| `method_timings` | Execution time by method | <200ms for recommendations |
| `slow_query_count` | Queries exceeding 100ms | <5% of total |

### Recommendation Quality Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `ctr_overall` | Click-through rate | 40% improvement vs baseline |
| `ctr_by_strategy` | CTR by recommendation strategy | Varies by strategy |
| `user_satisfaction` | Percentage of useful recommendations | >70% |

### User Engagement Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `total_users` | Total registered users | Growing |
| `active_users` | Users with recent interactions | >50% of total |
| `total_interactions` | Total user interactions | Growing |
| `positive_rate` | Percentage of positive interactions | >60% |

### Model Health Metrics

| Metric | Description | Status |
|--------|-------------|--------|
| `model.available` | NCF model availability | true/false |
| `model.num_users` | Users in training data | Growing |
| `model.num_items` | Items in training data | Growing |
| `model.last_modified` | Last training date | Recent |

### Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `neo_alexandria_request_duration_seconds` | Histogram | Request latency distribution |
| `neo_alexandria_requests_total` | Counter | Total requests by endpoint |
| `neo_alexandria_cache_hits_total` | Counter | Cache hits by type |
| `neo_alexandria_cache_misses_total` | Counter | Cache misses by type |
| `neo_alexandria_database_query_seconds` | Histogram | Database query time |
| `neo_alexandria_active_ingestions` | Gauge | Active ingestion processes |

## Alerting

### Recommended Alerts

Create alerts for these conditions:

1. **High Error Rate**
   ```promql
   rate(neo_alexandria_requests_total{status_code=~"5.."}[5m]) > 0.05
   ```
   Alert when 5xx error rate exceeds 5%

2. **Slow Recommendations**
   ```promql
   histogram_quantile(0.95, rate(neo_alexandria_request_duration_seconds_bucket{endpoint="/api/recommendations"}[5m])) > 0.2
   ```
   Alert when p95 latency exceeds 200ms

3. **Low Cache Hit Rate**
   ```promql
   rate(neo_alexandria_cache_hits_total[5m]) / (rate(neo_alexandria_cache_hits_total[5m]) + rate(neo_alexandria_cache_misses_total[5m])) < 0.8
   ```
   Alert when cache hit rate drops below 80%

4. **Database Performance**
   ```promql
   histogram_quantile(0.95, rate(neo_alexandria_database_query_seconds_bucket[5m])) > 0.1
   ```
   Alert when p95 query time exceeds 100ms

### Alert Configuration

Create `alerts.yml`:

```yaml
groups:
  - name: neo_alexandria_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(neo_alexandria_requests_total{status_code=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      - alert: SlowRecommendations
        expr: histogram_quantile(0.95, rate(neo_alexandria_request_duration_seconds_bucket{endpoint="/api/recommendations"}[5m])) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow recommendation generation"
          description: "p95 latency is {{ $value }}s"
      
      - alert: LowCacheHitRate
        expr: rate(neo_alexandria_cache_hits_total[5m]) / (rate(neo_alexandria_cache_hits_total[5m]) + rate(neo_alexandria_cache_misses_total[5m])) < 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }}"
```

## Custom Monitoring Scripts

### Python Monitoring Script

```python
#!/usr/bin/env python3
"""
Simple monitoring script for Neo Alexandria Phase 11.
Checks health and key metrics, sends alerts if needed.
"""

import requests
import time
import sys

API_BASE = "http://localhost:8000"

def check_health():
    """Check overall system health."""
    try:
        response = requests.get(f"{API_BASE}/api/monitoring/health", timeout=5)
        health = response.json()
        
        if health['status'] != 'healthy':
            print(f"WARNING: System status is {health['status']}")
            print(f"Message: {health['message']}")
            return False
        
        return True
    except Exception as e:
        print(f"ERROR: Health check failed: {e}")
        return False

def check_performance():
    """Check performance metrics."""
    try:
        response = requests.get(f"{API_BASE}/api/monitoring/performance", timeout=5)
        metrics = response.json()
        
        cache_hit_rate = metrics['metrics'].get('cache_hit_rate', 0)
        
        if cache_hit_rate < 0.8:
            print(f"WARNING: Low cache hit rate: {cache_hit_rate:.2%}")
            return False
        
        return True
    except Exception as e:
        print(f"ERROR: Performance check failed: {e}")
        return False

def main():
    """Run monitoring checks."""
    print("Neo Alexandria Phase 11 Monitoring")
    print("=" * 50)
    
    all_ok = True
    
    print("Checking health...")
    if not check_health():
        all_ok = False
    else:
        print("  OK")
    
    print("Checking performance...")
    if not check_performance():
        all_ok = False
    else:
        print("  OK")
    
    if all_ok:
        print("\nAll checks passed!")
        sys.exit(0)
    else:
        print("\nSome checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save as `monitor.py` and run:
```bash
python monitor.py
```

### Bash Monitoring Script

```bash
#!/bin/bash
# Simple health check script

API_BASE="http://localhost:8000"

echo "Checking Neo Alexandria health..."

# Health check
health=$(curl -s "$API_BASE/api/monitoring/health")
status=$(echo $health | jq -r '.status')

if [ "$status" != "healthy" ]; then
    echo "WARNING: System status is $status"
    exit 1
fi

echo "System is healthy"
exit 0
```

## Monitoring Best Practices

1. **Regular Checks**: Monitor health endpoints every 30-60 seconds
2. **Trend Analysis**: Track metrics over time to identify patterns
3. **Alert Fatigue**: Set appropriate thresholds to avoid false alarms
4. **Dashboard Review**: Review dashboards daily during initial deployment
5. **Log Correlation**: Correlate metrics with application logs for debugging

## Troubleshooting

### High Latency

If recommendation latency is high:
1. Check cache hit rate - low hit rate increases latency
2. Review database query performance
3. Check if NCF model is loaded (cold start can be slow)
4. Monitor concurrent request load

### Low Cache Hit Rate

If cache hit rate is low:
1. Verify cache TTL settings (default: 5 minutes)
2. Check if cache is being cleared too frequently
3. Monitor memory usage - cache may be evicted
4. Review cache key generation logic

### Model Unavailable

If NCF model is unavailable:
1. Check if model file exists: `backend/models/ncf_model.pt`
2. Verify sufficient training data (10+ positive interactions)
3. Run training script: `python scripts/train_ncf_model.py`
4. Check model file permissions

### Database Performance

If database queries are slow:
1. Verify indexes exist (run `scripts/verify_migration.py`)
2. Check database file size and fragmentation
3. Review query patterns in logs
4. Consider adding query limits

## Next Steps

1. Set up automated monitoring checks (cron job or systemd timer)
2. Configure alerting (email, Slack, PagerDuty)
3. Create custom dashboards for specific metrics
4. Integrate with existing monitoring infrastructure
5. Set up log aggregation (ELK stack, Splunk, etc.)

## Support

For monitoring issues:
1. Check application logs: `backend/logs/`
2. Review Prometheus targets: http://localhost:9090/targets
3. Verify API endpoints are accessible
4. Check firewall and network configuration

---

**Last Updated**: 2025-11-15  
**Phase**: 11 - Hybrid Recommendation Engine  
**Version**: 1.0
