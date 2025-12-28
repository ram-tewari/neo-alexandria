# Curation Module

## Overview

The Curation module provides content review queue management and batch operations for maintaining high-quality content in the knowledge base. It enables curators to identify, review, and improve low-quality resources through systematic workflows.

## Purpose

- Manage review queues for low-quality content
- Perform batch operations on multiple resources
- Analyze quality metrics and provide improvement suggestions
- Integrate with quality assessment system for automated flagging

## Public Interface

### Router
- `curation_router`: FastAPI router with 5 endpoints

### Service
- `CurationService`: Business logic for curation operations

### Schemas
- `ReviewQueueParams`: Parameters for review queue queries
- `ReviewQueueResponse`: Response containing review queue items
- `BatchUpdateRequest`: Request for batch updating resources
- `BatchUpdateResult`: Result of batch update operation
- `QualityAnalysisResponse`: Detailed quality analysis for a resource
- `LowQualityResponse`: Response containing low-quality resources
- `BulkQualityCheckRequest`: Request for bulk quality checking

## API Endpoints

### GET /curation/review-queue
Get items in the review queue based on quality threshold.

**Query Parameters:**
- `threshold` (float, optional): Quality score threshold
- `include_unread_only` (bool): Filter to unread items only
- `limit` (int): Number of items to return
- `offset` (int): Pagination offset

**Response:** `ReviewQueueResponse`

### POST /curation/batch-update
Apply batch updates to multiple resources.

**Request Body:** `BatchUpdateRequest`
- `resource_ids`: List of resource UUIDs
- `updates`: ResourceUpdate object with fields to update

**Response:** `BatchUpdateResult`

### GET /curation/quality-analysis/{resource_id}
Get detailed quality analysis for a specific resource.

**Path Parameters:**
- `resource_id` (UUID): Resource identifier

**Response:** `QualityAnalysisResponse`

### GET /curation/low-quality
Get list of low-quality resources.

**Query Parameters:**
- `threshold` (float): Quality score threshold (default: 0.5)
- `limit` (int): Number of items to return
- `offset` (int): Pagination offset

**Response:** `LowQualityResponse`

### POST /curation/bulk-quality-check
Perform bulk quality check on multiple resources.

**Request Body:** `BulkQualityCheckRequest`
- `resource_ids`: List of resource UUIDs to check

**Response:** `BatchUpdateResult`

## Events

### Emitted Events

#### curation.reviewed
Emitted when an item is reviewed by a curator.

**Payload:**
```python
{
    "resource_id": str,
    "reviewer_id": str,
    "timestamp": datetime,
    "action": str  # "approved", "rejected", "flagged"
}
```

#### curation.approved
Emitted when content is approved after review.

**Payload:**
```python
{
    "resource_id": str,
    "reviewer_id": str,
    "timestamp": datetime,
    "previous_quality": float,
    "new_quality": float
}
```

#### curation.rejected
Emitted when content is rejected during review.

**Payload:**
```python
{
    "resource_id": str,
    "reviewer_id": str,
    "timestamp": datetime,
    "reason": str
}
```

### Subscribed Events

#### quality.outlier_detected
Triggered when the Quality module detects an outlier.

**Handler:** `handle_quality_outlier_detected`

**Action:** Adds the resource to the review queue for curator attention.

## Dependencies

### Shared Kernel
- `shared.database`: Database session management
- `shared.event_bus`: Event emission and subscription
- `shared.ai_core`: AI operations for quality analysis

### External Modules (via Events)
- Quality Module: Receives outlier detection events

## Usage Example

```python
from app.modules.curation import curation_router, CurationService
from app.shared.database import get_sync_db

# Use in FastAPI app
app.include_router(curation_router)

# Use service directly
db = next(get_sync_db())
service = CurationService(db)

# Get review queue
items, total = service.review_queue(
    threshold=0.5,
    include_unread_only=True,
    limit=25,
    offset=0
)

# Batch update resources
result = service.batch_update(
    resource_ids=[uuid1, uuid2, uuid3],
    updates={"read_status": "read"}
)
```

## Testing

Tests are located in `modules/curation/tests/`:
- `test_service.py`: Service unit tests
- `test_router.py`: Endpoint integration tests
- `test_handlers.py`: Event handler tests

## Implementation Notes

- The module uses the Quality module's `ContentQualityAnalyzer` for quality assessment
- Review queue is sorted by quality score (ascending) and updated_at
- Batch operations are performed in a single database transaction
- Event handlers are isolated - failures don't affect other handlers
- All quality scores are stored as floats in the range [0.0, 1.0]

## Future Enhancements

- Duplicate detection and merging
- Automated curation workflows
- Curator assignment and workload balancing
- Quality trend tracking over time
- Integration with external quality assessment tools
