# Curation API

Content review and batch operation endpoints for quality control.

## Overview

The Curation API provides functionality for:
- Review queue management for low-quality resources
- Batch operations on multiple resources
- Quality analysis and improvement suggestions
- Curator assignment and workflow management
- Batch review, tagging, and quality checks

## Endpoints

### GET /curation/review-queue

Get items in the review queue based on quality threshold.

Returns resources with quality scores below the threshold, sorted by quality score (ascending) and updated_at.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold (0.0-1.0) | 0.5 |
| `include_unread_only` | boolean | Only unread items | false |
| `limit` | integer | Maximum results (1-100) | 25 |
| `offset` | integer | Pagination offset | 0 |

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "description": "Resource description",
      "quality_score": 0.35,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 15
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/curation/review-queue?threshold=0.5&limit=25"
```

---

### POST /curation/batch-update

Apply batch updates to multiple resources.

Updates are applied in a single transaction. Failed updates are tracked and returned in the response.

**Request Body:**
```json
{
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ],
  "updates": {
    "read_status": "reviewed",
    "quality_score": 0.75
  }
}
```

**Response:**
```json
{
  "updated_count": 2,
  "failed_count": 0,
  "failed_ids": []
}
```

---

### GET /curation/quality-analysis/{resource_id}

Get detailed quality analysis for a specific resource.

Returns quality dimensions, overall score, and improvement suggestions.

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "quality_dimensions": {
    "accuracy": 0.75,
    "completeness": 0.65,
    "consistency": 0.80,
    "timeliness": 0.70,
    "relevance": 0.85
  },
  "quality_overall": 0.75,
  "suggestions": [
    "Add more complete metadata",
    "Verify source information",
    "Update publication date"
  ]
}
```

---

### GET /curation/low-quality

Get list of low-quality resources.

Returns resources with quality scores below the threshold.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold (0.0-1.0) | 0.5 |
| `limit` | integer | Maximum results (1-100) | 25 |
| `offset` | integer | Pagination offset | 0 |

**Response:**
```json
{
  "items": [...],
  "total": 15
}
```

---

### POST /curation/bulk-quality-check

Perform bulk quality check on multiple resources.

Recalculates quality scores for all specified resources.

**Request Body:**
```json
{
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ]
}
```

**Response:**
```json
{
  "updated_count": 2,
  "failed_count": 0,
  "failed_ids": []
}
```

---

### POST /curation/batch/review

Perform batch review operations on multiple resources.

Applies review action (approve/reject/flag) to all specified resources and tracks review records for audit trail.

**Request Body:**
```json
{
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000"
  ],
  "action": "approve",
  "curator_id": "curator-123",
  "comment": "Quality verified"
}
```

**Response:**
```json
{
  "updated_count": 1,
  "failed_count": 0,
  "failed_ids": []
}
```

---

### POST /curation/batch/tag

Add tags to multiple resources in batch.

Tags are deduplicated and merged with existing tags.

**Request Body:**
```json
{
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000"
  ],
  "tags": ["reviewed", "high-quality"]
}
```

---

### POST /curation/batch/assign

Assign multiple resources to a curator for review.

Updates curation status to 'assigned' and sets assigned curator.

**Request Body:**
```json
{
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000"
  ],
  "curator_id": "curator-123"
}
```

---

### GET /curation/queue

Get items in the review queue with enhanced filtering.

Supports filtering by quality threshold, curation status, assigned curator, quality score range, and read status.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold | - |
| `status` | string | Curation status (pending/approved/rejected/assigned) | - |
| `assigned_curator` | string | Curator ID | - |
| `min_quality` | float | Minimum quality score | - |
| `max_quality` | float | Maximum quality score | - |
| `include_unread_only` | boolean | Only unread items | false |
| `limit` | integer | Maximum results | 25 |
| `offset` | integer | Pagination offset | 0 |

**Response:**
```json
{
  "items": [...],
  "total": 15
}
```

## Module Structure

**Module**: `app.modules.curation`  
**Router Prefix**: `/curation`  
**Version**: 1.0.0

### Events

**Emitted Events:**
- `curation.reviewed` - When resources are reviewed
- `curation.approved` - When resources are approved

**Subscribed Events:**
- `quality.computed` - Updates review queue

## Related Documentation

- [Quality API](quality.md) - Quality assessment
- [Resources API](resources.md) - Resource management
- [API Overview](overview.md) - Authentication, errors, pagination
