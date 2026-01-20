# Annotations API

Annotation management endpoints for active reading with highlights, notes, and semantic search.

## Overview

The Annotations API provides comprehensive functionality for creating, managing, and searching text annotations. Annotations enable active reading by allowing users to highlight text passages, add notes, tag content, and search across their annotations using both full-text and semantic search.

## Endpoints

### POST /resources/{resource_id}/annotations

Create a new annotation on a resource.

**Request Body:**
```json
{
  "start_offset": 100,
  "end_offset": 250,
  "highlighted_text": "This is the highlighted text passage",
  "note": "My thoughts on this passage",
  "tags": ["important", "review"],
  "color": "#FFFF00",
  "collection_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "test-user",
  "start_offset": 100,
  "end_offset": 250,
  "highlighted_text": "This is the highlighted text passage",
  "note": "My thoughts on this passage",
  "tags": ["important", "review"],
  "color": "#FFFF00",
  "context_before": "...preceding text...",
  "context_after": "...following text...",
  "is_shared": false,
  "collection_ids": ["550e8400-e29b-41d4-a716-446655440000"],
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/annotations/resources/{resource_id}/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 100,
    "end_offset": 250,
    "highlighted_text": "Important passage",
    "note": "Key insight",
    "tags": ["important"]
  }'
```

---

### GET /resources/{resource_id}/annotations

List all annotations for a specific resource.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `include_shared` | boolean | Include shared annotations from other users | false |
| `tags` | string[] | Filter by tags | - |

**Response:**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "test-user",
      "start_offset": 100,
      "end_offset": 250,
      "highlighted_text": "Important passage",
      "note": "Key insight",
      "tags": ["important"],
      "color": "#FFFF00",
      "context_before": "...",
      "context_after": "...",
      "is_shared": false,
      "collection_ids": null,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### GET /annotations

List all annotations for the authenticated user across all resources.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of annotations to return (1-100) | 50 |
| `offset` | integer | Number of annotations to skip | 0 |
| `sort_by` | string | Sort order: "recent" or "oldest" | recent |

**Response:**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_title": "Machine Learning Fundamentals",
      "user_id": "test-user",
      "start_offset": 100,
      "end_offset": 250,
      "highlighted_text": "Important passage",
      "note": "Key insight",
      "tags": ["important"],
      "color": "#FFFF00",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

---

### GET /annotations/{annotation_id}

Get a specific annotation by ID.

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_title": "Machine Learning Fundamentals",
  "user_id": "test-user",
  "start_offset": 100,
  "end_offset": 250,
  "highlighted_text": "Important passage",
  "note": "Key insight",
  "tags": ["important"],
  "color": "#FFFF00",
  "context_before": "...",
  "context_after": "...",
  "is_shared": false,
  "collection_ids": null,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

---

### PUT /annotations/{annotation_id}

Update an existing annotation.

Only the annotation owner can update it. Supports updating: note, tags, color, is_shared.

**Request Body:**
```json
{
  "note": "Updated note text",
  "tags": ["important", "review", "updated"],
  "color": "#FF0000",
  "is_shared": true
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "test-user",
  "start_offset": 100,
  "end_offset": 250,
  "highlighted_text": "Important passage",
  "note": "Updated note text",
  "tags": ["important", "review", "updated"],
  "color": "#FF0000",
  "is_shared": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

---

### DELETE /annotations/{annotation_id}

Delete an annotation.

Only the annotation owner can delete it.

**Response:** `204 No Content`

---

### GET /annotations/search/fulltext

Full-text search across annotation notes and highlighted text.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query (required) | - |
| `limit` | integer | Maximum results (1-100) | 50 |

**Response:**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_title": "Machine Learning Fundamentals",
      "highlighted_text": "Important passage about neural networks",
      "note": "Key insight on backpropagation",
      "tags": ["important", "neural-networks"],
      "created_at": "2024-01-01T10:00:00Z",
      "similarity_score": null
    }
  ],
  "total": 1,
  "query": "neural networks"
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/annotations/search/fulltext?query=neural+networks&limit=10"
```

---

### GET /annotations/search/semantic

Semantic search across annotation notes using embeddings.

Finds annotations with similar meaning to the query, not just keyword matches.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Semantic search query (required) | - |
| `limit` | integer | Maximum results (1-50) | 10 |

**Response:**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_title": "Machine Learning Fundamentals",
      "highlighted_text": "Important passage",
      "note": "Key insight",
      "tags": ["important"],
      "similarity_score": 0.87,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "query": "deep learning concepts"
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/annotations/search/semantic?query=deep+learning+concepts&limit=10"
```

---

### GET /annotations/search/tags

Search annotations by tags.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `tags` | string[] | Tags to search for (required) | - |
| `match_all` | boolean | Match ALL tags (true) or ANY tag (false) | false |

**Response:**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_title": "Machine Learning Fundamentals",
      "highlighted_text": "Important passage",
      "note": "Key insight",
      "tags": ["important", "review"],
      "created_at": "2024-01-01T10:00:00Z",
      "similarity_score": null
    }
  ],
  "total": 1,
  "query": "tags: important, review"
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/annotations/search/tags?tags=important&tags=review&match_all=false"
```

---

### GET /annotations/export/markdown

Export annotations to Markdown format.

Exports all user annotations or annotations for a specific resource. Annotations are grouped by resource with formatted headers.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `resource_id` | string | Optional resource UUID to filter by | - |

**Response:** Markdown-formatted text

**Example Output:**
```markdown
# Annotations Export

## Machine Learning Fundamentals

### Annotation 1
**Highlighted Text:** Important passage about neural networks

**Note:** Key insight on backpropagation

**Tags:** important, neural-networks

**Created:** 2024-01-01 10:00:00

---
```

**Example:**
```bash
curl "http://127.0.0.1:8000/annotations/export/markdown?resource_id=550e8400-e29b-41d4-a716-446655440000"
```

---

### GET /annotations/export/json

Export annotations to JSON format.

Exports all user annotations or annotations for a specific resource with complete metadata.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `resource_id` | string | Optional resource UUID to filter by | - |

**Response:**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "resource_title": "Machine Learning Fundamentals",
    "user_id": "test-user",
    "start_offset": 100,
    "end_offset": 250,
    "highlighted_text": "Important passage",
    "note": "Key insight",
    "tags": ["important"],
    "color": "#FFFF00",
    "context_before": "...",
    "context_after": "...",
    "is_shared": false,
    "collection_ids": null,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

**Example:**
```bash
curl "http://127.0.0.1:8000/annotations/export/json"
```

## Data Models

### Annotation Model

```json
{
  "id": "uuid",
  "resource_id": "uuid (required)",
  "user_id": "string (required)",
  "start_offset": "integer (required)",
  "end_offset": "integer (required)",
  "highlighted_text": "string (required)",
  "note": "string (optional)",
  "tags": ["string"] (optional),
  "color": "string (hex color, default: #FFFF00)",
  "context_before": "string (auto-generated)",
  "context_after": "string (auto-generated)",
  "is_shared": "boolean (default: false)",
  "collection_ids": ["uuid"] (optional),
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### Annotation Search Result

```json
{
  "id": "uuid",
  "resource_id": "uuid",
  "resource_title": "string",
  "highlighted_text": "string",
  "note": "string",
  "tags": ["string"],
  "similarity_score": "float (0.0-1.0, optional)",
  "created_at": "datetime"
}
```

## Module Structure

The Annotations module is implemented as a self-contained vertical slice:

**Module**: `app.modules.annotations`  
**Router Prefix**: `/annotations`  
**Version**: 1.0.0

```python
from app.modules.annotations import (
    router,
    AnnotationService,
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse
)
```

### Events

**Emitted Events:**
- `annotation.created` - When a new annotation is created
- `annotation.updated` - When annotation metadata is updated
- `annotation.deleted` - When an annotation is removed

**Subscribed Events:**
- `resource.deleted` - Removes annotations when resource is deleted

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Collections API](collections.md) - Collection management
- [Search API](search.md) - Search functionality
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
