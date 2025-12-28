# Quality API

Multi-dimensional quality assessment endpoints for resource evaluation.

## Overview

The Quality API provides:
- Multi-dimensional quality scoring (accuracy, completeness, consistency, timeliness, relevance)
- Quality outlier detection using Isolation Forest
- Quality degradation monitoring over time
- Summary quality evaluation (G-Eval, FineSurE, BERTScore)
- Quality distribution analytics and trends

## Endpoints

### GET /resources/{id}/quality-details

Retrieve full quality dimension breakdown for a resource.

**Response (200 OK):**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "quality_dimensions": {
    "accuracy": 0.75,
    "completeness": 0.82,
    "consistency": 0.88,
    "timeliness": 0.65,
    "relevance": 0.79
  },
  "quality_overall": 0.77,
  "quality_weights": {
    "accuracy": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.15,
    "relevance": 0.10
  },
  "quality_last_computed": "2025-11-10T12:00:00Z",
  "quality_computation_version": "v2.0",
  "is_quality_outlier": false,
  "outlier_score": null,
  "outlier_reasons": null,
  "needs_quality_review": false
}
```

**Quality Dimensions:**
- **Accuracy (0.0-1.0)**: Citation validity, source credibility, scholarly metadata
- **Completeness (0.0-1.0)**: Metadata coverage, content depth, multi-modal content
- **Consistency (0.0-1.0)**: Title-content alignment, internal coherence
- **Timeliness (0.0-1.0)**: Publication recency, content freshness
- **Relevance (0.0-1.0)**: Classification confidence, citation count

---

### POST /quality/recalculate

Trigger quality recomputation with optional custom weights.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "weights": {
    "accuracy": 0.35,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.10,
    "relevance": 0.10
  }
}
```

**Note:** Provide either `resource_id` or `resource_ids` (array), not both. Weights must sum to 1.0.

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "message": "Quality computation queued for background processing"
}
```

---

### GET /quality/outliers

Retrieve paginated list of detected quality outliers.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number | 1 |
| `limit` | integer | Results per page (1-100) | 50 |
| `min_outlier_score` | float | Minimum anomaly score (-1.0 to 1.0) | null |
| `reason` | string | Filter by outlier reason | null |

**Outlier Reasons:**
- `low_accuracy`, `low_completeness`, `low_consistency`, `low_timeliness`, `low_relevance`
- `low_summary_coherence`, `low_summary_consistency`, `low_summary_fluency`, `low_summary_relevance`

**Response:**
```json
{
  "total": 42,
  "page": 1,
  "limit": 50,
  "outliers": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "quality_overall": 0.35,
      "outlier_score": -0.82,
      "outlier_reasons": ["low_accuracy", "low_completeness"],
      "needs_quality_review": true,
      "quality_last_computed": "2025-11-10T12:00:00Z"
    }
  ]
}
```

**Outlier Score Interpretation:**
- Lower scores indicate higher anomaly likelihood
- Scores < -0.5 are typically significant outliers
- Uses Isolation Forest with contamination=0.1

---

### GET /quality/degradation

Monitor quality degradation over time.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `time_window_days` | integer | Lookback period in days | 30 |

**Response:**
```json
{
  "time_window_days": 30,
  "degraded_count": 15,
  "degraded_resources": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "old_quality": 0.85,
      "new_quality": 0.62,
      "degradation_pct": 27.1,
      "quality_last_computed": "2025-10-15T12:00:00Z"
    }
  ]
}
```

**Detection:** Flags resources with >20% quality drop.

---

### POST /summaries/{id}/evaluate

Trigger summary quality evaluation using G-Eval, FineSurE, and BERTScore.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `use_g_eval` | boolean | Use GPT-4 for G-Eval metrics | false |

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "message": "Summary evaluation queued for background processing"
}
```

**Evaluation Metrics:**
- **G-Eval (optional)**: Coherence, consistency, fluency, relevance (1-5 scale)
- **FineSurE**: Completeness and conciseness (0.0-1.0)
- **BERTScore**: Semantic similarity F1 score (0.0-1.0)

**Performance:**
- Without G-Eval: <2 seconds per resource
- With G-Eval: <10 seconds per resource

---

### GET /quality/distribution

Retrieve quality score distribution histogram.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `bins` | integer | Number of histogram bins (1-50) | 10 |
| `dimension` | string | Dimension or "overall" | overall |

**Response:**
```json
{
  "dimension": "overall",
  "bins": 10,
  "distribution": [
    {"range": "0.0-0.1", "count": 5},
    {"range": "0.1-0.2", "count": 12},
    ...
  ],
  "statistics": {
    "mean": 0.65,
    "median": 0.68,
    "std_dev": 0.18,
    "min": 0.12,
    "max": 0.98,
    "total_resources": 494
  }
}
```

---

### GET /quality/trends

Retrieve quality trends over time.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `granularity` | string | daily, weekly, monthly | weekly |
| `start_date` | date | Start of range (ISO 8601) | 90 days ago |
| `end_date` | date | End of range (ISO 8601) | today |
| `dimension` | string | Dimension or "overall" | overall |

**Response:**
```json
{
  "dimension": "overall",
  "granularity": "weekly",
  "data_points": [
    {
      "period": "2025-W31",
      "avg_quality": 0.72,
      "resource_count": 145,
      "date": "2025-08-03"
    }
  ]
}
```

---

### GET /quality/dimensions

Retrieve average scores per dimension across all resources.

**Response:**
```json
{
  "dimensions": {
    "accuracy": {"avg": 0.75, "min": 0.12, "max": 0.98, "std_dev": 0.15},
    "completeness": {"avg": 0.68, "min": 0.25, "max": 0.95, "std_dev": 0.18},
    ...
  },
  "overall": {"avg": 0.71, "min": 0.28, "max": 0.96, "std_dev": 0.16},
  "total_resources": 1247
}
```

---

### GET /quality/review-queue

Retrieve resources flagged for quality review.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number | 1 |
| `limit` | integer | Results per page (1-100) | 50 |
| `sort_by` | string | outlier_score, quality_overall, updated_at | outlier_score |

---

## Curation Endpoints

### GET /curation/review-queue

Access low-quality items for review and curation.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold | null |
| `include_unread_only` | boolean | Include only unread | false |
| `limit` | integer | Number of items (1-100) | 25 |
| `offset` | integer | Results to skip | 0 |

---

### GET /curation/low-quality

Get resources with quality scores below threshold.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold (0.0-1.0) | 0.5 |
| `limit` | integer | Number of items (1-100) | 25 |

---

### GET /curation/quality-analysis/{resource_id}

Get detailed quality analysis for a specific resource.

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata_completeness": 0.8,
  "readability": {
    "flesch_kincaid": 12.5,
    "gunning_fog": 14.2,
    "automated_readability": 11.8
  },
  "source_credibility": 0.7,
  "content_depth": 0.6,
  "overall_quality": 0.7,
  "quality_level": "good",
  "suggestions": [
    "Improve metadata completeness",
    "Add more detailed description"
  ]
}
```

---

### POST /curation/batch-update

Apply partial updates to multiple resources.

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2"],
  "updates": {
    "read_status": "in_progress",
    "subject": ["Updated", "Tags"]
  }
}
```

---

### POST /curation/bulk-quality-check

Perform quality analysis on multiple resources.

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2"]
}
```

## Quality Dimension Algorithms

**Accuracy:**
```
accuracy = 0.5 (baseline)
  + 0.20 * (valid_citations / total_citations)
  + 0.15 * (1 if credible_domain else 0)
  + 0.15 * (1 if has_academic_identifier else 0)
  + 0.10 * (1 if has_authors else 0)
```

**Completeness:**
```
completeness = 
  0.30 * (filled_required_fields / 3)
  + 0.30 * (filled_important_fields / 4)
  + 0.20 * (filled_scholarly_fields / 4)
  + 0.20 * (multimodal_content_score / 3)
```

**Timeliness:**
```
age_years = current_year - publication_year
recency_score = max(0.0, 1.0 - (age_years / 20))
timeliness = recency_score + (0.1 if ingested_within_30_days else 0)
```

## Module Structure

The Quality module is implemented as a self-contained vertical slice:

**Module**: `app.modules.quality`  
**Router Prefix**: `/quality`  
**Version**: 1.0.0

```python
from app.modules.quality import (
    quality_router,
    QualityService,
    SummarizationEvaluator,
    QualityDimensions,
    QualityResponse,
    OutlierReport
)
```

### Events

**Emitted Events:**
- `quality.computed` - When quality scores are calculated
- `quality.outlier_detected` - When anomalous quality is found
- `quality.degradation_detected` - When quality degrades over time

**Subscribed Events:**
- `resource.created` - Triggers initial quality computation
- `resource.updated` - Recomputes quality on changes

## Related Documentation

- [Resources API](resources.md) - Content management
- [Taxonomy API](taxonomy.md) - Classification
- [Curation API](curation.md) - Content review
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors
