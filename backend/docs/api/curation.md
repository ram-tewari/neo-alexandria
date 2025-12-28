# Curation API

## Overview

The Curation module provides content review workflows and batch operations for managing resource quality and organization.

**Module**: `app.modules.curation`  
**Router Prefix**: `/curation`  
**Version**: 1.0.0

## Endpoints

### Get Review Queue

Get resources pending review.

```http
GET /curation/review-queue?status={status}&limit={limit}&offset={offset}
```

**Query Parameters:**
- `status` (string, optional) - Filter by status: `pending`, `approved`, `rejected`
- `limit` (integer, optional) - Results per page (default: 25)
- `offset` (integer, optional) - Pagination offset (default: 0)

**Response:**
```json
{
  "items": [
    {
      "resource_id": 1,
      "title": "Example Resource",
      "status": "pending",
      "quality_score": 0.45,
      "flagged_reason": "Low quality score",
      "added_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 42
}
```

### Review Resource

Submit a review decision for a resource.

```http
POST /curation/review/{resource_id}
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Request Body:**
```json
{
  "decision": "approved",
  "notes": "High quality content, well-structured",
  "tags": ["verified", "high-quality"]
}
```

**Response:**
```json
{
  "resource_id": 1,
  "decision": "approved",
  "reviewed_by": "curator@example.com",
  "reviewed_at": "2024-01-01T00:00:00Z"
}
```

### Batch Update

Perform batch operations on multiple resources.

```http
POST /curation/batch
```

**Request Body:**
```json
{
  "resource_ids": [1, 2, 3],
  "operation": "add_tags",
  "parameters": {
    "tags": ["reviewed", "approved"]
  }
}
```

**Supported Operations:**
- `add_tags` - Add tags to resources
- `remove_tags` - Remove tags from resources
- `update_classification` - Update classification
- `approve` - Approve resources
- `reject` - Reject resources

**Response:**
```json
{
  "success": 3,
  "failed": 0,
  "results": [
    {
      "resource_id": 1,
      "status": "success"
    }
  ]
}
```

### Get Curation Stats

Get curation statistics.

```http
GET /curation/stats
```

**Response:**
```json
{
  "pending": 42,
  "approved": 1234,
  "rejected": 56,
  "total_reviewed": 1290,
  "avg_review_time_hours": 2.5
}
```

### Health Check

Check module health status.

```http
GET /curation/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "curation",
  "version": "1.0.0"
}
```

## Events

### Emitted Events

- `curation.reviewed` - When a resource is reviewed
- `curation.approved` - When a resource is approved
- `curation.rejected` - When a resource is rejected

### Subscribed Events

- `quality.outlier_detected` - Adds resources to review queue

## Module Structure

```python
from app.modules.curation import (
    curation_router,
    CurationService,
    ReviewDecision,
    BatchOperation
)
```

## Related Documentation

- [Architecture: Modules](../architecture/modules.md)
- [Architecture: Events](../architecture/events.md)
- [Quality API](quality.md)
- [Resources API](resources.md)
