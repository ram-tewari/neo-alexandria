# Module Tests Rewrite - Design Document

## Overview

This document outlines the technical design for rewriting the failing module test files. The tests will be completely rewritten from scratch based on the actual implementation code, not the broken existing tests.

## Problem Analysis

### Root Causes of Test Failures

1. **Field Name Mismatches**
   - Old tests use outdated field names (e.g., `url` instead of `source` and `identifier`)
   - Annotation model mismatch: router expects `start_offset`/`end_offset`/`highlighted_text` but DB model uses `selection_start`/`selection_end`/`selection_text`
   - Resource model uses `source`, `identifier`, `title`, `ingestion_status` (not `url`)

2. **Database Type Compatibility Issues**
   - Boolean fields stored as INTEGER (0/1) for SQLite compatibility
   - PostgreSQL rejects Python boolean values for INTEGER columns
   - JSON fields must be stored as JSON strings, not Python objects

3. **Missing Mocking**
   - Celery tasks not mocked, causing test failures
   - AI services (embeddings, semantic search) not mocked
   - Background tasks attempting to run during tests

4. **Schema Validation Errors**
   - Missing required fields in payloads (e.g., `owner_id`, `visibility`)
   - UUID objects not converted to strings in JSON payloads
   - Incorrect data types for fields

## Design Principles

### 1. Read-First Approach
- **Always read the actual implementation** before writing tests
- Read router, schema, and model files for each module
- Understand the actual API contracts, not assumptions

### 2. Complete Mocking Strategy
- Mock ALL Celery tasks with `@patch` decorators
- Mock AI services (embedding generation, semantic search)
- Mock external dependencies (Redis, background workers)
- Use `MagicMock` for complex service dependencies

### 3. Database Compatibility
- Store booleans as integers (0/1) for SQLite compatibility
- Store JSON fields as JSON strings using `json.dumps()`
- Use proper type conversions for PostgreSQL compatibility
- Test against actual database constraints

### 4. Proper Fixtures Usage
- Use existing fixtures from `backend/tests/modules/conftest.py`
- Leverage `create_test_resource` and `create_test_collection` helpers
- Use `db` and `client` fixtures for database and API access
- Create module-specific fixtures as needed

## Module-Specific Analysis

### 1. Annotations Module

**Router**: `backend/app/routers/annotations.py`
**Schema**: `backend/app/schemas/annotation.py`
**Model**: `backend/app/database/models.py` (Annotation model)

**Key Endpoints**:
- `POST /annotations` - Create annotation
- `GET /annotations` - List annotations
- `GET /annotations/{id}` - Get annotation
- `PUT /annotations/{id}` - Update annotation
- `DELETE /annotations/{id}` - Delete annotation
- `GET /annotations/search` - Search annotations

**Critical Fields**:
- `start_offset`, `end_offset`, `highlighted_text` (in schema)
- `selection_start`, `selection_end`, `selection_text` (in DB model)
- `resource_id`, `user_id`, `note`, `tags`, `color`, `is_shared`

**Mocking Requirements**:
- Mock Celery tasks if any
- Mock semantic search for annotation search endpoint

### 2. Collections Module

**Router**: `backend/app/modules/collections/router.py`
**Schema**: `backend/app/modules/collections/schema.py`
**Model**: `backend/app/modules/collections/model.py`

**Key Endpoints**:
- `POST /collections` - Create collection
- `GET /collections` - List collections
- `GET /collections/{id}` - Get collection with resources
- `PUT /collections/{id}` - Update collection
- `DELETE /collections/{id}` - Delete collection
- `PUT /collections/{id}/resources` - Batch add/remove resources
- `GET /collections/{id}/recommendations` - Get recommendations

**Critical Fields**:
- `name`, `description`, `owner_id`, `visibility`, `parent_id`
- `resource_count` (computed field)
- `add_resource_ids`, `remove_resource_ids` (for batch operations)

**Mocking Requirements**:
- Mock embedding service for recommendations
- Mock event bus for resource deletion events

### 3. Curation Module

**Router**: `backend/app/routers/curation.py`
**Schema**: `backend/app/schemas/query.py`
**Model**: Uses Resource model

**Key Endpoints**:
- `GET /curation/review-queue` - Get review queue
- `POST /curation/batch-update` - Batch update resources
- `GET /curation/quality-analysis/{id}` - Get quality analysis
- `GET /curation/low-quality` - Get low quality resources
- `POST /curation/bulk-quality-check` - Bulk quality check

**Critical Fields**:
- `threshold`, `include_unread_only`, `limit`, `offset`
- `resource_ids`, `updates` (for batch operations)
- Quality scores and metrics

**Mocking Requirements**:
- Mock CurationInterface methods
- Mock quality service calls
- Mock Celery tasks for quality computation

### 4. Graph Module

**Router**: `backend/app/routers/graph.py`
**Schema**: `backend/app/schemas/graph.py`
**Model**: Uses Resource model

**Key Endpoints**:
- `GET /graph/resource/{id}/neighbors` - Get neighbors
- `GET /graph/overview` - Get global overview

**Critical Fields**:
- `limit`, `min_similarity`, `vector_threshold`
- `nodes` (list of GraphNode)
- `edges` (list of GraphEdge with weight and details)

**Mocking Requirements**:
- Mock graph service methods
- Mock embedding similarity calculations
- Mock vector search operations

### 5. Quality Module

**Router**: `backend/app/routers/quality.py`
**Schema**: `backend/app/schemas/quality.py`
**Model**: Uses Resource model with quality fields

**Key Endpoints**:
- `GET /resources/{id}/quality-details` - Get quality details
- `POST /quality/recalculate` - Trigger recalculation
- `GET /quality/outliers` - List outliers
- `GET /quality/degradation` - Get degradation report
- `POST /summaries/{id}/evaluate` - Evaluate summary
- `GET /quality/distribution` - Get distribution
- `GET /quality/trends` - Get trends
- `GET /quality/dimensions` - Get dimension averages
- `GET /quality/review-queue` - Get review queue

**Critical Fields**:
- Quality dimensions: `accuracy`, `completeness`, `consistency`, `timeliness`, `relevance`
- `quality_overall`, `quality_weights`, `quality_last_computed`
- `is_quality_outlier`, `needs_quality_review`, `outlier_score`, `outlier_reasons`

**Mocking Requirements**:
- Mock QualityService methods
- Mock SummarizationEvaluator
- Mock Celery tasks for quality computation and summary evaluation

### 6. Scholarly Module

**Router**: `backend/app/routers/scholarly.py`
**Schema**: `backend/app/schemas/scholarly.py`
**Model**: Uses Resource model with scholarly fields

**Key Endpoints**:
- `GET /scholarly/resources/{id}/metadata` - Get metadata
- `GET /scholarly/resources/{id}/equations` - Get equations
- `GET /scholarly/resources/{id}/tables` - Get tables
- `POST /scholarly/resources/{id}/metadata/extract` - Trigger extraction
- `GET /scholarly/metadata/completeness-stats` - Get stats

**Critical Fields**:
- `authors`, `affiliations`, `doi`, `pmid`, `arxiv_id`, `isbn`
- `journal`, `conference`, `volume`, `issue`, `pages`, `publication_year`
- `funding_sources`, `acknowledgments`
- `equation_count`, `table_count`, `figure_count`, `reference_count`
- `metadata_completeness_score`, `extraction_confidence`

**Mocking Requirements**:
- Mock Celery tasks for metadata extraction
- Mock equation parser
- Mock scholarly metadata extractor

## Test Structure Template

```python
import json
import uuid
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


class TestModuleEndpoints:
    """Test suite for [Module] endpoints."""
    
    @patch('backend.app.tasks.celery_tasks.some_task')
    def test_create_endpoint(self, mock_task, client, db, create_test_resource):
        """Test creating a [resource]."""
        # Arrange
        resource = create_test_resource(db)
        payload = {
            "field1": "value1",
            "field2": 123,
            "resource_id": str(resource.id),  # Convert UUID to string
            "is_active": 1,  # Boolean as integer
            "metadata": json.dumps({"key": "value"})  # JSON as string
        }
        
        # Act
        response = client.post("/api/endpoint", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["field1"] == "value1"
        assert data["field2"] == 123
        
        # Verify mock was called
        mock_task.apply_async.assert_called_once()
    
    def test_list_endpoint(self, client, db, create_test_resource):
        """Test listing [resources]."""
        # Arrange
        resource1 = create_test_resource(db, title="Resource 1")
        resource2 = create_test_resource(db, title="Resource 2")
        
        # Act
        response = client.get("/api/endpoint")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
    
    def test_get_endpoint(self, client, db, create_test_resource):
        """Test getting a single [resource]."""
        # Arrange
        resource = create_test_resource(db)
        
        # Act
        response = client.get(f"/api/endpoint/{resource.id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(resource.id)
    
    def test_update_endpoint(self, client, db, create_test_resource):
        """Test updating a [resource]."""
        # Arrange
        resource = create_test_resource(db)
        payload = {"field1": "updated_value"}
        
        # Act
        response = client.put(f"/api/endpoint/{resource.id}", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["field1"] == "updated_value"
    
    def test_delete_endpoint(self, client, db, create_test_resource):
        """Test deleting a [resource]."""
        # Arrange
        resource = create_test_resource(db)
        
        # Act
        response = client.delete(f"/api/endpoint/{resource.id}")
        
        # Assert
        assert response.status_code == 204
        
        # Verify deletion
        response = client.get(f"/api/endpoint/{resource.id}")
        assert response.status_code == 404
    
    def test_not_found(self, client):
        """Test 404 for non-existent [resource]."""
        # Act
        response = client.get(f"/api/endpoint/{uuid.uuid4()}")
        
        # Assert
        assert response.status_code == 404
```

## Mocking Patterns

### 1. Celery Tasks

```python
@patch('backend.app.tasks.celery_tasks.task_name')
def test_endpoint(mock_task, client, db):
    # Configure mock
    mock_task.apply_async.return_value = MagicMock(id="task-123")
    
    # Test code
    response = client.post("/endpoint", json=payload)
    
    # Verify
    mock_task.apply_async.assert_called_once()
```

### 2. AI Services

```python
@patch('backend.app.services.embedding_service.EmbeddingService.generate_embedding')
def test_endpoint(mock_embedding, client, db):
    # Configure mock
    mock_embedding.return_value = [0.1] * 768
    
    # Test code
    response = client.post("/endpoint", json=payload)
    
    # Verify
    mock_embedding.assert_called_once()
```

### 3. Service Methods

```python
@patch('backend.app.services.quality_service.QualityService.compute_quality')
def test_endpoint(mock_compute, client, db):
    # Configure mock
    mock_compute.return_value = {
        "accuracy": 0.8,
        "completeness": 0.9,
        "overall": 0.85
    }
    
    # Test code
    response = client.get("/endpoint")
    
    # Verify
    mock_compute.assert_called_once()
```

## Data Compatibility Patterns

### 1. Boolean Fields

```python
# SQLite compatibility: store as integer
payload = {
    "is_active": 1,  # Not True
    "is_shared": 0,  # Not False
}
```

### 2. JSON Fields

```python
import json

# Store as JSON string
payload = {
    "metadata": json.dumps({"key": "value"}),
    "tags": json.dumps(["tag1", "tag2"]),
}
```

### 3. UUID Fields

```python
# Convert UUID to string in payloads
payload = {
    "resource_id": str(resource.id),
    "collection_id": str(collection.id),
}
```

## Validation Patterns

### 1. Required Fields

```python
# Always include required fields
payload = {
    "name": "Test Collection",
    "owner_id": "user-123",  # Required
    "visibility": "private",  # Required with default
}
```

### 2. Field Constraints

```python
# Respect field constraints from schemas
payload = {
    "name": "A" * 255,  # Max length 255
    "tags": ["tag1", "tag2"],  # Max 20 items
    "color": "#FF0000",  # Hex color pattern
}
```

### 3. Validation Errors

```python
# Test validation errors
def test_invalid_payload(client):
    payload = {"name": ""}  # Empty name
    response = client.post("/endpoint", json=payload)
    assert response.status_code == 422
```

## Test Organization

### File Structure

```
backend/tests/modules/
├── conftest.py                          # Shared fixtures
├── test_annotations_endpoints.py        # Annotations tests
├── test_collections_endpoints.py        # Collections tests
├── test_curation_endpoints.py           # Curation tests
├── test_graph_endpoints.py              # Graph tests
├── test_quality_endpoints.py            # Quality tests
└── test_scholarly_endpoints.py          # Scholarly tests
```

### Test Class Organization

```python
class TestModuleEndpoints:
    """Main test class for module endpoints."""
    
    # CRUD operations
    def test_create(self): pass
    def test_list(self): pass
    def test_get(self): pass
    def test_update(self): pass
    def test_delete(self): pass
    
    # Special operations
    def test_special_operation(self): pass
    
    # Error cases
    def test_not_found(self): pass
    def test_validation_error(self): pass
    def test_permission_denied(self): pass
```

## Success Criteria

1. **All tests pass** on both SQLite and PostgreSQL
2. **No database errors** (type mismatches, missing tables)
3. **No unmocked dependencies** (Celery, AI services)
4. **Proper field names** matching actual models
5. **Complete coverage** of all endpoints
6. **Clear test names** describing what is tested
7. **Proper assertions** verifying expected behavior

## Related Documentation

- [Requirements](.kiro/specs/module-tests-rewrite/requirements.md)
- [Tasks](.kiro/specs/module-tests-rewrite/tasks.md)
- [Test Fixtures](backend/tests/modules/conftest.py)
- [API Documentation](backend/docs/api/)
