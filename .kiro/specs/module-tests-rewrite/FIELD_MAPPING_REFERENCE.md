# Field Mapping Reference for Module Tests

## Overview

This document provides the definitive field mapping reference for all 6 modules being tested. It documents the correct field names, data types, required vs optional status, and special handling notes based on the actual implementation code.

**Purpose**: Ensure test payloads use correct field names and types to avoid validation errors and database compatibility issues.

**Last Updated**: December 26, 2024

## Critical Data Type Rules

### Boolean Fields
- **Database Storage**: INTEGER (0 or 1) for SQLite compatibility
- **Test Payloads**: Use integers `0` or `1`, NOT Python booleans `True`/`False`
- **PostgreSQL**: Rejects Python boolean values for INTEGER columns

### JSON Fields
- **Database Storage**: JSON or TEXT column type
- **Test Payloads**: Use `json.dumps()` to convert Python objects to JSON strings
- **Example**: `{"tags": json.dumps(["tag1", "tag2"])}`

### UUID Fields
- **Database Storage**: GUID() custom type
- **Test Payloads**: Convert UUID objects to strings using `str(uuid_obj)`
- **Example**: `{"resource_id": str(resource.id)}`

---

## 1. Annotations Module

### Router
- **File**: `backend/app/routers/annotations.py`
- **Base Path**: `/annotations`

### Schema vs Database Field Mapping

**CRITICAL MISMATCH**: The API schema uses different field names than the database model!

| Schema Field (API) | Database Field | Type | Required | Notes |
|-------------------|----------------|------|----------|-------|
| `start_offset` | `selection_start` | int | Yes | Character offset (≥0) |
| `end_offset` | `selection_end` | int | Yes | Character offset (≥0) |
| `highlighted_text` | `selection_text` | str | Yes | Selected text content |
| `note` | `content` | str | No | Max 10,000 chars |
| `tags` | `tags` | List[str] | No | JSON array, max 20 items |
| `color` | `color` | str | No | Hex color (default: #FFFF00) |
| `is_shared` | `is_private` | bool | No | **INVERTED**: is_shared=True → is_private=0 |
| `resource_id` | `resource_id` | UUID | Yes | Foreign key to resources |
| `user_id` | `user_id` | str | Yes | Owner user ID |


### Database Model Fields (Complete List)

```python
# backend/app/database/models.py - Annotation model
id: UUID (primary key)
resource_id: UUID (foreign key, indexed)
user_id: str (indexed)
annotation_type: str (default: "note")
content: str (TEXT, nullable=False)
selection_text: str | None (TEXT)
selection_start: int | None
selection_end: int | None
page_number: int | None
color: str | None (max 20 chars)
tags: List[str] (JSON, default: [])
is_private: bool (INTEGER, default: 1)  # 1=private, 0=shared
created_at: datetime
updated_at: datetime
```

### Test Payload Examples

**Create Annotation**:
```python
payload = {
    "start_offset": 100,
    "end_offset": 200,
    "highlighted_text": "This is the selected text",
    "note": "My annotation note",
    "tags": ["important", "review"],
    "color": "#FF0000",
    "resource_id": str(resource.id)  # Convert UUID to string
}
```

**Update Annotation**:
```python
payload = {
    "note": "Updated note",
    "tags": ["updated", "tag"],
    "color": "#00FF00",
    "is_shared": 1  # Use integer, not boolean
}
```

### Special Handling Notes

1. **Field Name Translation**: Router translates between API schema names and database field names
2. **Boolean Inversion**: `is_shared` (API) is inverted to `is_private` (DB)
3. **Tags as JSON**: Store tags as JSON array string in database
4. **Context Fields**: `context_before` and `context_after` are computed, not stored

---

## 2. Collections Module

### Router
- **File**: `backend/app/modules/collections/router.py`
- **Base Path**: `/collections`

### Schema Fields

| Field Name | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `name` | str | Yes | - | Max 255 chars, min 1 char |
| `description` | str | No | None | TEXT field |
| `owner_id` | str | Yes | - | Max 255 chars |
| `visibility` | str | No | "private" | Enum: "private", "shared", "public" |
| `parent_id` | UUID | No | None | Foreign key to parent collection |


### Database Model Fields (Complete List)

```python
# backend/app/modules/collections/model.py
id: UUID (primary key)
name: str (max 255, nullable=False)
description: str | None (TEXT)
owner_id: str (max 255, indexed)
visibility: str (default: "private", indexed)
parent_id: UUID | None (foreign key, indexed)
embedding: List[float] | None (JSON)
created_at: datetime
updated_at: datetime
```

### Computed Fields

| Field Name | Type | Description |
|-----------|------|-------------|
| `resource_count` | int | Count of resources in collection (computed) |

### Batch Operations Schema

**CollectionResourcesUpdate**:
```python
{
    "add_resource_ids": [uuid1, uuid2, ...],      # List of UUIDs to add
    "remove_resource_ids": [uuid3, uuid4, ...]    # List of UUIDs to remove
}
```

### Test Payload Examples

**Create Collection**:
```python
payload = {
    "name": "My Collection",
    "description": "Collection description",
    "owner_id": "user-123",
    "visibility": "private"  # or "shared", "public"
}
```

**Update Collection**:
```python
payload = {
    "name": "Updated Name",
    "description": "Updated description",
    "visibility": "public"
}
```

**Batch Add/Remove Resources**:
```python
payload = {
    "add_resource_ids": [str(resource1.id), str(resource2.id)],
    "remove_resource_ids": [str(resource3.id)]
}
```

### Special Handling Notes

1. **Visibility Enum**: Must be one of "private", "shared", or "public"
2. **Parent Collections**: Can create hierarchical collections via `parent_id`
3. **Resource Count**: Computed from `collection_resources` join table
4. **UUID Conversion**: Always convert UUID objects to strings in payloads

---

## 3. Curation Module

### Router
- **File**: `backend/app/routers/curation.py`
- **Base Path**: `/curation`

### Query Parameter Schemas

**ReviewQueueParams**:
| Field Name | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `threshold` | float | No | None | Quality threshold filter |
| `include_unread_only` | bool | No | False | Filter for unread resources |
| `limit` | int | No | 25 | Min: 1, Max: 100 |
| `offset` | int | No | 0 | Min: 0 |


**BatchUpdateRequest**:
| Field Name | Type | Required | Notes |
|-----------|------|----------|-------|
| `resource_ids` | List[UUID] | Yes | Min 1 item |
| `updates` | ResourceUpdate | Yes | Partial update object |

### Resource Update Fields

From `backend/app/schemas/resource.py`:
```python
{
    "title": str,
    "description": str,
    "creator": str,
    "publisher": str,
    "type": str,
    "classification_code": str,
    "read_status": str,  # "unread", "in_progress", "completed", "archived"
    "quality_score": float,
    # ... all fields are optional for partial updates
}
```

### Test Payload Examples

**Review Queue Query**:
```python
params = {
    "threshold": 0.5,
    "include_unread_only": True,
    "limit": 50,
    "offset": 0
}
response = client.get("/curation/review-queue", params=params)
```

**Batch Update**:
```python
payload = {
    "resource_ids": [str(resource1.id), str(resource2.id)],
    "updates": {
        "read_status": "completed",
        "quality_score": 0.85
    }
}
response = client.post("/curation/batch-update", json=payload)
```

**Bulk Quality Check**:
```python
payload = {
    "resource_ids": [str(resource1.id), str(resource2.id)]
}
response = client.post("/curation/bulk-quality-check", json=payload)
```

### Special Handling Notes

1. **Threshold Filter**: Filters resources by quality score
2. **Unread Filter**: Uses `read_status` field from Resource model
3. **Batch Operations**: Requires at least 1 resource ID
4. **Quality Computation**: May trigger Celery tasks (mock required)

---

## 4. Graph Module

### Router
- **File**: `backend/app/routers/graph.py`
- **Base Path**: `/graph`

### Query Parameter Schemas

**Neighbors Query**:
| Field Name | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `limit` | int | No | 10 | Max neighbors to return |
| `min_similarity` | float | No | 0.0 | Min similarity threshold (0.0-1.0) |
| `vector_threshold` | float | No | 0.5 | Vector similarity threshold |

### Response Schemas

**GraphNode**:
```python
{
    "id": UUID,
    "title": str,
    "type": str | None,
    "classification_code": str | None
}
```

**GraphEdgeDetails**:
```python
{
    "connection_type": str,  # "semantic", "topical", "classification"
    "vector_similarity": float | None,  # 0.0-1.0
    "shared_subjects": List[str]
}
```

**GraphEdge**:
```python
{
    "source": UUID,
    "target": UUID,
    "weight": float,  # 0.0-1.0
    "details": GraphEdgeDetails
}
```


**KnowledgeGraph**:
```python
{
    "nodes": List[GraphNode],
    "edges": List[GraphEdge]
}
```

### Test Payload Examples

**Get Neighbors**:
```python
params = {
    "limit": 20,
    "min_similarity": 0.3,
    "vector_threshold": 0.6
}
response = client.get(f"/graph/resource/{resource_id}/neighbors", params=params)
```

**Get Global Overview**:
```python
response = client.get("/graph/overview")
```

### Special Handling Notes

1. **Vector Similarity**: Requires embeddings to be present on resources
2. **Shared Subjects**: Uses `subject` field from Resource model (JSON array)
3. **Classification Matching**: Uses `classification_code` field
4. **Hybrid Scoring**: Combines vector, subject, and classification weights
5. **Mocking Required**: Mock graph service methods and embedding calculations

---

## 5. Quality Module

### Router
- **File**: `backend/app/routers/quality.py`
- **Base Path**: `/quality` and `/resources/{id}/quality-details`

### Quality Dimension Fields

From `backend/app/database/models.py` Resource model:

| Field Name | Type | Description |
|-----------|------|-------------|
| `quality_accuracy` | float | Accuracy dimension score |
| `quality_completeness` | float | Completeness dimension score |
| `quality_consistency` | float | Consistency dimension score |
| `quality_timeliness` | float | Timeliness dimension score |
| `quality_relevance` | float | Relevance dimension score |
| `quality_overall` | float | Weighted overall score |
| `quality_weights` | str | JSON string of dimension weights |
| `quality_last_computed` | datetime | Last computation timestamp |
| `quality_computation_version` | str | Algorithm version |
| `is_quality_outlier` | bool | INTEGER (0/1) |
| `outlier_score` | float | Anomaly score |
| `outlier_reasons` | str | JSON string of reasons |
| `needs_quality_review` | bool | INTEGER (0/1) |

### Summary Quality Fields

| Field Name | Type | Description |
|-----------|------|-------------|
| `summary_coherence` | float | Summary coherence score |
| `summary_consistency` | float | Summary consistency score |
| `summary_fluency` | float | Summary fluency score |
| `summary_relevance` | float | Summary relevance score |


### Request Schemas

**QualityRecalculateRequest**:
```python
{
    "resource_id": str | None,  # Single resource
    "resource_ids": List[str] | None,  # Batch resources
    "weights": {  # Optional custom weights (must sum to 1.0)
        "accuracy": float,
        "completeness": float,
        "consistency": float,
        "timeliness": float,
        "relevance": float
    }
}
```

### Response Schemas

**QualityDetailsResponse**:
```python
{
    "resource_id": str,
    "quality_dimensions": {
        "accuracy": float,
        "completeness": float,
        "consistency": float,
        "timeliness": float,
        "relevance": float
    },
    "quality_overall": float,
    "quality_weights": Dict[str, float],
    "quality_last_computed": datetime | None,
    "quality_computation_version": str | None,
    "is_quality_outlier": bool,
    "needs_quality_review": bool,
    "outlier_score": float | None,
    "outlier_reasons": List[str] | None
}
```

**OutlierResponse**:
```python
{
    "resource_id": str,
    "title": str,
    "quality_overall": float,
    "outlier_score": float,
    "outlier_reasons": List[str],
    "needs_quality_review": bool
}
```

### Test Payload Examples

**Get Quality Details**:
```python
response = client.get(f"/resources/{resource_id}/quality-details")
```

**Recalculate Quality**:
```python
payload = {
    "resource_id": str(resource.id),
    "weights": {
        "accuracy": 0.3,
        "completeness": 0.2,
        "consistency": 0.2,
        "timeliness": 0.15,
        "relevance": 0.15
    }
}
response = client.post("/quality/recalculate", json=payload)
```

**Get Outliers**:
```python
params = {"page": 1, "limit": 25}
response = client.get("/quality/outliers", params=params)
```

**Evaluate Summary**:
```python
response = client.post(f"/summaries/{resource_id}/evaluate")
```

### Special Handling Notes

1. **Boolean Fields**: Use integers (0/1) for `is_quality_outlier` and `needs_quality_review`
2. **JSON Fields**: `quality_weights` and `outlier_reasons` stored as JSON strings
3. **Dimension Weights**: Must include all 5 dimensions and sum to 1.0
4. **Celery Tasks**: Mock quality computation and summary evaluation tasks
5. **Quality Service**: Mock QualityService and SummarizationEvaluator methods

---

## 6. Scholarly Module

### Router
- **File**: `backend/app/routers/scholarly.py`
- **Base Path**: `/scholarly`


### Scholarly Metadata Fields

From `backend/app/database/models.py` Resource model:

| Field Name | Type | Description |
|-----------|------|-------------|
| `authors` | str | TEXT field (JSON string) |
| `affiliations` | str | TEXT field (JSON string) |
| `doi` | str | Max 255 chars, indexed |
| `pmid` | str | Max 50 chars, indexed |
| `arxiv_id` | str | Max 50 chars, indexed |
| `isbn` | str | Max 20 chars |
| `journal` | str | Journal name |
| `conference` | str | Conference name |
| `volume` | str | Max 50 chars |
| `issue` | str | Max 50 chars |
| `pages` | str | Max 50 chars |
| `publication_year` | int | Indexed |
| `funding_sources` | str | TEXT field (JSON string) |
| `acknowledgments` | str | TEXT field |
| `equation_count` | int | Default: 0 |
| `table_count` | int | Default: 0 |
| `figure_count` | int | Default: 0 |
| `reference_count` | int | Optional |
| `equations` | str | TEXT field (JSON string) |
| `tables` | str | TEXT field (JSON string) |
| `figures` | str | TEXT field (JSON string) |
| `metadata_completeness_score` | float | 0.0-1.0 |
| `extraction_confidence` | float | 0.0-1.0 |
| `requires_manual_review` | bool | INTEGER (0/1) |
| `is_ocr_processed` | bool | INTEGER (0/1) |
| `ocr_confidence` | float | 0.0-1.0 |
| `ocr_corrections_applied` | int | Optional |

### Response Schemas

**ScholarlyMetadataResponse**:
```python
{
    "resource_id": str,
    "authors": List[Author] | None,
    "affiliations": List[str] | None,
    "doi": str | None,
    "pmid": str | None,
    "arxiv_id": str | None,
    "isbn": str | None,
    "journal": str | None,
    "conference": str | None,
    "volume": str | None,
    "issue": str | None,
    "pages": str | None,
    "publication_year": int | None,
    "funding_sources": List[str] | None,
    "acknowledgments": str | None,
    "equation_count": int,
    "table_count": int,
    "figure_count": int,
    "reference_count": int | None,
    "metadata_completeness_score": float | None,
    "extraction_confidence": float | None,
    "requires_manual_review": bool,
    "is_ocr_processed": bool,
    "ocr_confidence": float | None,
    "ocr_corrections_applied": int | None
}
```

**Author**:
```python
{
    "name": str,
    "affiliation": str | None,
    "orcid": str | None
}
```

**Equation**:
```python
{
    "position": int,
    "latex": str,
    "context": str | None,
    "confidence": float  # 0.0-1.0
}
```

**TableData**:
```python
{
    "position": int,
    "caption": str | None,
    "headers": List[str],
    "rows": List[List[str]],
    "format": str,
    "confidence": float  # 0.0-1.0
}
```


### Test Payload Examples

**Get Metadata**:
```python
response = client.get(f"/scholarly/resources/{resource_id}/metadata")
```

**Get Equations**:
```python
response = client.get(f"/scholarly/resources/{resource_id}/equations")
```

**Get Tables**:
```python
response = client.get(f"/scholarly/resources/{resource_id}/tables")
```

**Trigger Metadata Extraction**:
```python
payload = {"force": True}  # Optional, default: False
response = client.post(f"/scholarly/resources/{resource_id}/metadata/extract", json=payload)
```

**Get Completeness Stats**:
```python
response = client.get("/scholarly/metadata/completeness-stats")
```

### Special Handling Notes

1. **Boolean Fields**: Use integers (0/1) for `requires_manual_review`, `is_ocr_processed`
2. **JSON Fields**: `authors`, `affiliations`, `funding_sources`, `equations`, `tables`, `figures` stored as JSON strings
3. **Academic Identifiers**: DOI, PMID, arXiv ID are indexed for fast lookup
4. **Celery Tasks**: Mock metadata extraction tasks
5. **Equation Parser**: Mock equation parser service
6. **Scholarly Extractor**: Mock scholarly metadata extractor service

---

## Common Patterns Across All Modules

### 1. UUID Handling
```python
# Always convert UUID objects to strings in payloads
payload = {
    "resource_id": str(resource.id),
    "collection_id": str(collection.id)
}
```

### 2. Boolean Fields
```python
# Use integers for SQLite compatibility
payload = {
    "is_active": 1,      # Not True
    "is_shared": 0,      # Not False
    "needs_review": 1    # Not True
}
```

### 3. JSON Fields
```python
import json

# Convert Python objects to JSON strings
payload = {
    "tags": json.dumps(["tag1", "tag2"]),
    "metadata": json.dumps({"key": "value"}),
    "weights": json.dumps({"accuracy": 0.5, "completeness": 0.5})
}
```

### 4. Datetime Fields
```python
from datetime import datetime

# Use ISO format strings or datetime objects
payload = {
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": "2024-12-26T10:00:00Z"
}
```

### 5. Enum Fields
```python
# Use exact string values from enum definitions
payload = {
    "visibility": "private",  # Not "PRIVATE"
    "read_status": "completed",  # Not "COMPLETED"
    "ingestion_status": "pending"  # Not "PENDING"
}
```

---

## Mocking Requirements by Module

### Annotations
- `backend.app.tasks.celery_tasks.semantic_search_annotations` (if exists)
- Semantic search service for annotation search endpoint

### Collections
- `backend.app.services.embedding_service.EmbeddingService.generate_embedding`
- Event bus for resource deletion events

### Curation
- `backend.app.services.curation_service.CurationInterface` methods
- `backend.app.services.quality_service.QualityService.compute_quality`
- `backend.app.tasks.celery_tasks.compute_quality_task`

### Graph
- `backend.app.services.graph_service.GraphService` methods
- Embedding similarity calculations
- Vector search operations

### Quality
- `backend.app.services.quality_service.QualityService` methods
- `backend.app.services.summarization_evaluator.SummarizationEvaluator`
- `backend.app.tasks.celery_tasks.compute_quality_task`
- `backend.app.tasks.celery_tasks.evaluate_summary_task`

### Scholarly
- `backend.app.tasks.celery_tasks.extract_metadata_task`
- `backend.app.utils.equation_parser.EquationParser`
- `backend.app.services.metadata_extractor.ScholarlyMetadataExtractor`

---

## Validation Rules Summary

### Annotations
- `start_offset` < `end_offset`
- `highlighted_text` min length: 1
- `note` max length: 10,000
- `tags` max items: 20, each tag max 50 chars
- `color` pattern: `^#[0-9A-Fa-f]{6}$`

### Collections
- `name` min length: 1, max length: 255
- `owner_id` min length: 1, max length: 255
- `visibility` enum: "private", "shared", "public"

### Quality
- Dimension weights must sum to 1.0
- Must include all 5 dimensions: accuracy, completeness, consistency, timeliness, relevance
- Quality scores range: 0.0-1.0

### Scholarly
- Confidence scores range: 0.0-1.0
- Completeness scores range: 0.0-1.0

---

## Testing Checklist

For each module test file:

- [ ] All field names match actual models
- [ ] Boolean fields use integers (0/1)
- [ ] JSON fields use `json.dumps()`
- [ ] UUID fields converted to strings
- [ ] Required fields included in payloads
- [ ] Optional fields handled correctly
- [ ] Enum values use exact strings
- [ ] All Celery tasks mocked
- [ ] All AI services mocked
- [ ] Tests pass on SQLite
- [ ] Tests pass on PostgreSQL

---

## References

- [Requirements](.kiro/specs/module-tests-rewrite/requirements.md)
- [Design](.kiro/specs/module-tests-rewrite/design.md)
- [Tasks](.kiro/specs/module-tests-rewrite/tasks.md)
- [Database Models](backend/app/database/models.py)
- [API Schemas](backend/app/schemas/)
- [Module Schemas](backend/app/modules/*/schema.py)

