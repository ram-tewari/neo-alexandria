# Quality API

Quality assessment endpoints for multi-dimensional quality scoring and monitoring.

## Overview

The Quality API provides comprehensive quality assessment functionality including:
- Multi-dimensional quality scoring (accuracy, completeness, consistency, timeliness, relevance)
- Quality outlier detection
- Quality degradation monitoring
- Summary evaluation using Flan-T5
- Quality distribution analysis
- Review queue management

## Endpoints

### GET /resources/{resource_id}/quality-details

Retrieve full quality dimension breakdown for a resource.

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "quality_dimensions": {
    "accuracy": 0.85,
    "completeness": 0.90,
    "consistency": 0.88,
    "timeliness": 0.75,
    "relevance": 0.92
  },
  "quality_overall": 0.86,
  "quality_weights": {
    "accuracy": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.15,
    "relevance": 0.10
  },
  "quality_last_computed": "2024-01-01T10:00:00Z",
  "quality_computation_version": "1.0",
  "is_quality_outlier": false,
  "needs_quality_review": false,
  "outlier_score": null,
  "outlier_reasons": null
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/resources/550e8400-e29b-41d4-a716-446655440000/quality-details"
```

---

### POST /quality/recalculate

Trigger quality recomputation for one or more resources.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "weights": {
    "accuracy": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.15,
    "relevance": 0.10
  }
}
```

Or for multiple resources:

```json
{
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ],
  "weights": {
    "accuracy": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.15,
    "relevance": 0.10
  }
}
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Quality computation queued for 2 resource(s)"
}
```

---

### GET /quality/outliers

List detected quality outliers with pagination and filtering.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number (≥1) | 1 |
| `limit` | integer | Results per page (1-100) | 50 |
| `min_outlier_score` | float | Minimum outlier score (-1.0 to 1.0) | - |
| `reason` | string | Filter by specific outlier reason | - |

**Response:**
```json
{
  "total": 15,
  "page": 1,
  "limit": 50,
  "outliers": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "quality_overall": 0.35,
      "outlier_score": -2.5,
      "outlier_reasons": ["low_completeness", "inconsistent_metadata"],
      "needs_quality_review": true
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/quality/outliers?page=1&limit=20&min_outlier_score=-2.0"
```

---

### GET /quality/degradation

Get quality degradation report for specified time window.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `time_window_days` | integer | Lookback period in days (1-365) | 30 |

**Response:**
```json
{
  "time_window_days": 30,
  "degraded_count": 5,
  "degraded_resources": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "old_quality": 0.85,
      "new_quality": 0.65,
      "degradation_pct": 23.5
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/quality/degradation?time_window_days=30"
```

---

### POST /summaries/{resource_id}/evaluate

Trigger summary quality evaluation for a resource using Flan-T5.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `use_g_eval` | boolean | Whether to use G-Eval with Flan-T5 | true |

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Summary evaluation queued for resource 550e8400-e29b-41d4-a716-446655440000"
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/summaries/550e8400-e29b-41d4-a716-446655440000/evaluate?use_g_eval=true"
```

---

### GET /quality/distribution

Get quality score distribution histogram.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `bins` | integer | Number of histogram bins (5-50) | 10 |
| `dimension` | string | Quality dimension or 'overall' | overall |

**Valid dimensions:** overall, accuracy, completeness, consistency, timeliness, relevance

**Response:**
```json
{
  "dimension": "overall",
  "bins": 10,
  "distribution": [
    {
      "range": "0.0-0.1",
      "count": 5
    },
    {
      "range": "0.1-0.2",
      "count": 8
    },
    {
      "range": "0.8-0.9",
      "count": 45
    },
    {
      "range": "0.9-1.0",
      "count": 32
    }
  ],
  "statistics": {
    "mean": 0.78,
    "median": 0.82,
    "std_dev": 0.15
  }
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/quality/distribution?bins=10&dimension=overall"
```

---

### GET /quality/trends

Get quality trends over time.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `granularity` | string | Time granularity (daily/weekly/monthly) | weekly |
| `start_date` | string | Start date (YYYY-MM-DD) | 90 days ago |
| `end_date` | string | End date (YYYY-MM-DD) | today |
| `dimension` | string | Quality dimension or 'overall' | overall |

**Response:**
```json
{
  "dimension": "overall",
  "granularity": "weekly",
  "data_points": [
    {
      "period": "2024-W01",
      "avg_quality": 0.82,
      "resource_count": 45
    },
    {
      "period": "2024-W02",
      "avg_quality": 0.85,
      "resource_count": 52
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/quality/trends?granularity=weekly&dimension=overall&start_date=2024-01-01&end_date=2024-03-31"
```

---

### GET /quality/dimensions

Get average scores per dimension across all resources.

**Response:**
```json
{
  "dimensions": {
    "accuracy": {
      "avg": 0.85,
      "min": 0.45,
      "max": 1.0
    },
    "completeness": {
      "avg": 0.88,
      "min": 0.50,
      "max": 1.0
    },
    "consistency": {
      "avg": 0.82,
      "min": 0.40,
      "max": 1.0
    },
    "timeliness": {
      "avg": 0.75,
      "min": 0.30,
      "max": 1.0
    },
    "relevance": {
      "avg": 0.90,
      "min": 0.55,
      "max": 1.0
    }
  },
  "overall": {
    "avg": 0.84,
    "min": 0.42,
    "max": 1.0
  },
  "total_resources": 1250
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/quality/dimensions"
```

---

### GET /quality/review-queue

Get resources flagged for quality review with priority ranking.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number (≥1) | 1 |
| `limit` | integer | Results per page (1-100) | 50 |
| `sort_by` | string | Sort field (outlier_score/quality_overall/updated_at) | outlier_score |

**Response:**
```json
{
  "total": 25,
  "page": 1,
  "limit": 50,
  "review_queue": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "quality_overall": 0.35,
      "is_quality_outlier": true,
      "outlier_score": -2.5,
      "outlier_reasons": ["low_completeness", "inconsistent_metadata"],
      "quality_last_computed": "2024-01-01T10:00:00Z"
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/quality/review-queue?page=1&limit=20&sort_by=outlier_score"
```

---

### GET /quality/health

Health check endpoint for Quality module.

**Response:**
```json
{
  "status": "healthy",
  "module": "quality",
  "database": true,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Data Models

### Quality Dimensions

```json
{
  "accuracy": "float (0.0-1.0)",
  "completeness": "float (0.0-1.0)",
  "consistency": "float (0.0-1.0)",
  "timeliness": "float (0.0-1.0)",
  "relevance": "float (0.0-1.0)"
}
```

### Quality Weights

Default weights for computing overall quality score:

```json
{
  "accuracy": 0.30,
  "completeness": 0.25,
  "consistency": 0.20,
  "timeliness": 0.15,
  "relevance": 0.10
}
```

## Module Structure

The Quality module is implemented as a self-contained vertical slice:

**Module**: `app.modules.quality`  
**Router Prefix**: `/quality`  
**Version**: 1.0.0

```python
from app.modules.quality import (
    router,
    QualityService,
    SummarizationEvaluator,
    QualityDetailsResponse
)
```

### Events

**Emitted Events:**
- `quality.computed` - When quality scores are calculated
- `quality.outlier_detected` - When a quality outlier is detected

**Subscribed Events:**
- `resource.created` - Computes initial quality scores
- `resource.updated` - Recomputes quality scores

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Curation API](curation.md) - Content review and curation
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
