# Collections API

Collection management endpoints for organizing resources into hierarchical groups.

## Overview

Collections allow users to organize resources into named groups with:
- Hierarchical parent-child relationships
- Visibility controls (private, shared, public)
- Aggregate embeddings for similarity-based recommendations
- Batch resource membership operations

## Endpoints

### POST /collections

Create a new collection with metadata and optional hierarchical parent.

**Request Body:**
```json
{
  "name": "string (required, 1-255 characters)",
  "description": "string (optional, max 2000 characters)",
  "visibility": "private|shared|public (optional, default: private)",
  "parent_id": "string (optional, UUID of parent collection)"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 0,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "resources": []
}
```

**Error Responses:**
- `400 Bad Request` - Invalid name length, visibility value, or circular hierarchy
- `404 Not Found` - Parent collection not found

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning Papers",
    "description": "Curated collection of ML research",
    "visibility": "public"
  }'
```

---

### GET /collections/{id}

Retrieve a specific collection with member resource summaries.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 2,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:05:00Z",
  "resources": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Deep Learning Fundamentals",
      "creator": "John Doe",
      "quality_score": 0.92
    }
  ]
}
```

**Access Rules:**
- `private`: Only owner can access
- `shared`: Owner + explicit permissions (future)
- `public`: All authenticated users

---

### PUT /collections/{id}

Update collection metadata (name, description, visibility, parent).

**Request Body:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "visibility": "private|shared|public (optional)",
  "parent_id": "string (optional, UUID or null)"
}
```

**Response (200 OK):** Returns updated collection object.

---

### DELETE /collections/{id}

Delete a collection. Cascade deletes all descendant collections.

**Response:** `204 No Content`

---

### GET /collections

List collections with filtering and pagination.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Filter by owner | - |
| `visibility` | string | Filter by visibility | - |
| `parent_id` | string | Filter by parent (null for root) | - |
| `page` | integer | Page number | 1 |
| `limit` | integer | Results per page (1-100) | 50 |

**Response:**
```json
{
  "items": [...],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

---

### POST /collections/{id}/resources

Add resources to a collection (batch operation, up to 100 resources).

**Request Body:**
```json
{
  "resource_ids": ["uuid", "uuid"]
}
```

**Response (200 OK):** Returns updated collection with new resource count.

**Behavior:**
- Validates all resource IDs exist before adding
- Handles duplicate associations gracefully (idempotent)
- Triggers aggregate embedding recomputation

---

### DELETE /collections/{id}/resources

Remove resources from a collection (batch operation).

**Request Body:**
```json
{
  "resource_ids": ["uuid", "uuid"]
}
```

**Response (200 OK):** Returns updated collection.

---

### GET /collections/{id}/recommendations

Get recommendations for similar resources and collections based on aggregate embedding.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Max results per category (1-50) | 10 |
| `include_resources` | boolean | Include resource recommendations | true |
| `include_collections` | boolean | Include collection recommendations | true |

**Response:**
```json
{
  "resources": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "title": "Advanced Neural Networks",
      "similarity": 0.92
    }
  ],
  "collections": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "name": "AI Research Papers",
      "similarity": 0.85
    }
  ]
}
```

---

### GET /collections/{id}/embedding

Retrieve the aggregate embedding vector for a collection.

**Response:**
```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimension": 768
}
```

## Features

### Hierarchical Organization

Collections support parent-child relationships:

```bash
# Create parent
curl -X POST http://127.0.0.1:8000/collections \
  -d '{"name": "Computer Science", "visibility": "public"}'

# Create child
curl -X POST http://127.0.0.1:8000/collections \
  -d '{"name": "Machine Learning", "parent_id": "{parent_id}"}'
```

### Aggregate Embeddings

Collections automatically compute aggregate embeddings from member resources:
- Mean vector across all member resource embeddings
- Normalized to unit length (L2 norm)
- Recomputed when resources are added/removed

### Access Control

| Level | Owner | Other Users |
|-------|-------|-------------|
| `private` | Full access | None |
| `shared` | Full access | Read only (future) |
| `public` | Full access | Read only |

## Data Models

### Collection Model

```json
{
  "id": "uuid",
  "name": "string (1-255 characters)",
  "description": "string (max 2000 characters) or null",
  "owner_id": "string",
  "visibility": "private|shared|public",
  "parent_id": "uuid or null",
  "resource_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime",
  "resources": [...]
}
```

## Module Structure

The Collections module is implemented as a self-contained vertical slice:

**Module**: `app.modules.collections`  
**Router Prefix**: `/collections`  
**Version**: 1.0.0

```python
from app.modules.collections import (
    collections_router,
    CollectionService,
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse
)
```

### Events

**Emitted Events:**
- `collection.created` - When a new collection is created
- `collection.updated` - When collection metadata is updated
- `collection.deleted` - When a collection is removed
- `collection.resource_added` - When a resource is added to a collection
- `collection.resource_removed` - When a resource is removed from a collection

**Subscribed Events:**
- `resource.deleted` - Removes resource from all collections

## Related Documentation

- [Resources API](resources.md) - Content management
- [Recommendations API](recommendations.md) - Personalized discovery
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
