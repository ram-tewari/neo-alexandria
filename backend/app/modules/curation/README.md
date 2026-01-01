# Curation Module

## Overview

The Curation module provides content review queue management and batch operations for maintaining high-quality content in the knowledge base. It enables curators to identify, review, and improve low-quality resources through systematic workflows.

## Purpose

- Manage review queues for low-quality content
- Perform batch operations on multiple resources (Task 15 - Phase 16.7)
- Analyze quality metrics and provide improvement suggestions
- Integrate with quality assessment system for automated flagging
- Support curator assignment and workflow management

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

## Usage Examples

### Batch Review Operations (Task 15.1 - Phase 16.7)

```python
from app.modules.curation import CurationService

service = CurationService(db)

# Batch approve multiple resources
result = await service.batch_review(
    resource_ids=["uuid1", "uuid2", "uuid3"],
    action="approve",
    reviewer_id="curator-123",
    notes="Quality verified, content accurate"
)
# Returns: {"updated_count": 3, "failed_count": 0, "errors": []}

# Batch reject resources
result = await service.batch_review(
    resource_ids=["uuid4", "uuid5"],
    action="reject",
    reviewer_id="curator-123",
    notes="Low quality, needs improvement"
)

# Batch flag for review
result = await service.batch_review(
    resource_ids=["uuid6", "uuid7", "uuid8"],
    action="flag",
    reviewer_id="curator-123",
    notes="Requires expert review"
)

# Performance: <5s for 100 resources (target met)
```

### Batch Tagging (Task 15.2 - Phase 16.7)

```python
# Add tags to multiple resources
result = await service.batch_tag(
    resource_ids=["uuid1", "uuid2", "uuid3"],
    tags=["reviewed", "high-quality", "featured"]
)
# Tags are deduplicated (case-insensitive)
# Existing tags are preserved
```

### Enhanced Review Queue (Task 15.3 - Phase 16.7)

```python
# Filter by curation status
items, total = await service.get_review_queue(
    status="pending",  # pending, assigned, approved, rejected, flagged
    limit=25,
    offset=0
)

# Filter by quality score range
items, total = await service.get_review_queue(
    min_quality=0.3,
    max_quality=0.6,
    limit=25
)

# Filter by assigned curator
items, total = await service.get_review_queue(
    assigned_to="curator-123",
    limit=25
)

# Combine filters
items, total = await service.get_review_queue(
    status="assigned",
    assigned_to="curator-123",
    min_quality=0.4,
    limit=25,
    offset=0
)
```

### Curator Assignment (Task 15.4 - Phase 16.7)

```python
# Assign resources to curator
result = await service.batch_assign(
    resource_ids=["uuid1", "uuid2", "uuid3"],
    curator_id="curator-123"
)
# Updates status to 'assigned'
# Emits curation.assigned event
```

### Quality Analysis

```python
# Get review queue by quality threshold
items, total = service.review_queue(
    threshold=0.5,
    include_unread_only=True,
    limit=25,
    offset=0
)

# Get detailed quality analysis
analysis = await service.get_quality_analysis(resource_id="uuid1")
# Returns: Quality metrics, suggestions, outlier status

# Bulk quality check
result = await service.bulk_quality_check(
    resource_ids=["uuid1", "uuid2", "uuid3"]
)
# Returns: Quality scores for all resources
```

## Testing

Tests are located in `modules/curation/tests/`:
- `test_service.py`: Service unit tests
- `test_router.py`: Endpoint integration tests
- `test_handlers.py`: Event handler tests

## Implementation Notes

- The module uses the Quality module's `ContentQualityAnalyzer` for quality assessment
- Review queue is sorted by quality score (ascending) and updated_at
- **Batch operations** (Task 15 - Phase 16.7):
  - Performed in a single database transaction for atomicity
  - Support partial success with detailed error reporting
  - Performance target: <5s for 100 resources (met)
  - Emit events for tracking and auditing
- Event handlers are isolated - failures don't affect other handlers
- All quality scores are stored as floats in the range [0.0, 1.0]
- Curator assignment updates resource status automatically
- Tag deduplication is case-insensitive

## Future Enhancements

- Duplicate detection and merging
- Automated curation workflows
- Curator assignment and workload balancing
- Quality trend tracking over time
- Integration with external quality assessment tools
