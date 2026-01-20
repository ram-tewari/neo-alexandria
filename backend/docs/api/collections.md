# Collections API

Collection management endpoints for organizing resources and generating recommendations.

## Overview

The Collections API provides functionality for creating and managing collections of resources. Collections enable users to organize content thematically, generate collection-based recommendations using semantic similarity, and discover related collections.

## Endpoints

### POST /collections

Create a new collection.

**Request Body:**
```json
{
  "name": "Machine Learning Papers",
  "description": "Collection of ML research papers",
  "owner_id": "user-123",
  "visibility": "private",
  "parent_id": null
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Collection of ML research papers",
  "owner_id": "user-123",
  "visibility": "private",
  "parent_id": null,
  "resource_count": 0,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ML Papers",
    "description": "Research papers on machine learning",
    "owner_id": "user-123",
    "visibility": "private"
  }'
```

---

### GET /collections

List collections for a user.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Owner user ID (optional) | - |
| `parent_id` | uuid | Parent collection ID filter | - |
| `include_public` | boolean | Include public collections | true |
| `visibility` | string | Filter by visibility (private/shared/public) | - |
| `limit` | integer | Maximum results (1-100) | 50 |
| `offset` | integer | Pagination offset | 0 |

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Machine Learning Papers",
    "description": "Collection of ML research papers",
    "owner_id": "user-123",
    "visibility": "private",
    "parent_id": null,
    "resource_count": 15,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

---

### GET /collections/{collection_id}

Retrieve a collection with its resources.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Owner user ID for access control | - |
| `limit` | integer | Maximum resources to return (1-100) | 50 |
| `offset` | integer | Pagination offset for resources | 0 |

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Collection of ML research papers",
  "owner_id": "user-123",
  "visibility": "private",
  "parent_id": null,
  "resource_count": 15,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "resources": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Deep Learning Fundamentals",
      "description": "Introduction to deep learning",
      "creator": "John Doe",
      "type": "article",
      "quality_score": 0.85,
      "created_at": "2024-01-01T09:00:00Z"
    }
  ]
}
```

---

### PUT /collections/{collection_id}

Update collection metadata.

**Request Body:**
```json
{
  "name": "Updated Collection Name",
  "description": "Updated description",
  "visibility": "shared"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Collection Name",
  "description": "Updated description",
  "owner_id": "user-123",
  "visibility": "shared",
  "parent_id": null,
  "resource_count": 15,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

---

### DELETE /collections/{collection_id}

Delete a collection.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Owner user ID for access control | - |

**Response:** `204 No Content`

---

### POST /collections/{collection_id}/resources

Add a single resource to a collection.

**Request Body:**
```json
{
  "resource_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Response (201 Created):**
```json
{
  "collection_id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_id": "660e8400-e29b-41d4-a716-446655440001",
  "added": true,
  "message": "Resource added to collection"
}
```

---

### GET /collections/{collection_id}/resources

List resources in a collection.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Owner user ID for access control | - |
| `limit` | integer | Maximum resources to return (1-100) | 50 |
| `offset` | integer | Pagination offset | 0 |

**Response:**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Deep Learning Fundamentals",
    "description": "Introduction to deep learning",
    "creator": "John Doe",
    "type": "article",
    "quality_score": 0.85,
    "created_at": "2024-01-01T09:00:00Z"
  }
]
```

---

### DELETE /collections/{collection_id}/resources/{resource_id}

Remove a single resource from a collection.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Owner user ID for access control | - |

**Response:** `204 No Content`

---

### PUT /collections/{collection_id}/resources

Batch add/remove resources from a collection.

**Request Body:**
```json
{
  "add_resource_ids": [
    "660e8400-e29b-41d4-a716-446655440001",
    "660e8400-e29b-41d4-a716-446655440002"
  ],
  "remove_resource_ids": [
    "660e8400-e29b-41d4-a716-446655440003"
  ]
}
```

**Response:**
```json
{
  "collection_id": "550e8400-e29b-41d4-a716-446655440000",
  "added": 2,
  "removed": 1,
  "message": "Added 2 and removed 1 resources"
}
```

---

### POST /collections/{collection_id}/resources/batch

Add multiple resources to a collection in a single batch operation.

More efficient than adding resources one at a time. Supports up to 100 resources per batch.

**Request Body:**
```json
{
  "resource_ids": [
    "660e8400-e29b-41d4-a716-446655440001",
    "660e8400-e29b-41d4-a716-446655440002",
    "660e8400-e29b-41d4-a716-446655440003"
  ]
}
```

**Response:**
```json
{
  "collection_id": "550e8400-e29b-41d4-a716-446655440000",
  "added": 3,
  "skipped": 0,
  "invalid": 0,
  "message": "Added 3 resources, skipped 0 duplicates, 0 invalid"
}
```

---

### DELETE /collections/{collection_id}/resources/batch

Remove multiple resources from a collection in a single batch operation.

More efficient than removing resources one at a time. Supports up to 100 resources per batch.

**Request Body:**
```json
{
  "resource_ids": [
    "660e8400-e29b-41d4-a716-446655440001",
    "660e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Response:**
```json
{
  "collection_id": "550e8400-e29b-41d4-a716-446655440000",
  "removed": 2,
  "not_found": 0,
  "message": "Removed 2 resources, 0 not found in collection"
}
```

---

### GET /collections/{collection_id}/recommendations

Get resource recommendations based on collection embedding.

Uses semantic similarity between the collection's aggregate embedding and individual resource embeddings to find related content.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Owner user ID for access control | - |
| `limit` | integer | Maximum recommendations (1-100) | 20 |
| `min_similarity` | float | Minimum similarity threshold (0.0-1.0) | 0.5 |
| `exclude_collection_resources` | boolean | Exclude resources already in collection | true |

**Response:**
```json
{
  "collection_id": "550e8400-e29b-41d4-a716-446655440000",
  "collection_name": "Machine Learning Papers",
  "recommendations": [
    {
      "resource_id": "770e8400-e29b-41d4-a716-446655440004",
      "title": "Neural Network Architectures",
      "description": "Overview of modern neural network designs",
      "similarity_score": 0.87,
      "reason": "Semantically similar to collection (similarity: 0.87)"
    }
  ],
  "total": 1
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/recommendations?limit=10&min_similarity=0.7"
```

---

### GET /collections/{collection_id}/similar-collections

Get similar collections based on embedding similarity.

Uses semantic similarity between collection embeddings to find related collections that might be of interest.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Owner user ID for access control | - |
| `limit` | integer | Maximum recommendations (1-100) | 20 |
| `min_similarity` | float | Minimum similarity threshold (0.0-1.0) | 0.5 |

**Response:**
```json
[
  {
    "collection_id": "880e8400-e29b-41d4-a716-446655440005",
    "name": "Deep Learning Resources",
    "description": "Curated deep learning materials",
    "similarity_score": 0.82,
    "owner_id": "user-456",
    "visibility": "public",
    "resource_count": 25
  }
]
```

---

### GET /collections/health

Health check endpoint for Collections module.

**Response:**
```json
{
  "status": "healthy",
  "module": {
    "name": "collections",
    "version": "1.0.0",
    "domain": "collections"
  },
  "database": {
    "healthy": true,
    "message": "Database connection healthy"
  },
  "event_handlers": {
    "registered": true,
    "count": 1,
    "events": ["resource.deleted"]
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Data Models

### Collection Model

```json
{
  "id": "uuid",
  "name": "string (required)",
  "description": "string (optional)",
  "owner_id": "string (required)",
  "visibility": "private|shared|public (default: private)",
  "parent_id": "uuid (optional)",
  "resource_count": "integer",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### Resource Summary Model

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "creator": "string",
  "type": "string",
  "quality_score": "float (0.0-1.0)",
  "created_at": "datetime (ISO 8601)"
}
```

### Collection Recommendation Model

```json
{
  "resource_id": "uuid",
  "title": "string",
  "description": "string",
  "similarity_score": "float (0.0-1.0)",
  "reason": "string"
}
```

## Module Structure

The Collections module is implemented as a self-contained vertical slice:

**Module**: `app.modules.collections`  
**Router Prefix**: `/collections`  
**Version**: 1.0.0

```python
from app.modules.collections import (
    router,
    CollectionService,
    CollectionCreate,
    CollectionUpdate,
    CollectionRead
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
- `resource.deleted` - Removes resource from all collections when deleted

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Recommendations API](recommendations.md) - Recommendation system
- [Search API](search.md) - Search functionality
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
