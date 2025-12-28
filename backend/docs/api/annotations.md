# Annotations API

Active reading system for highlighting text and adding notes to resources.

## Overview

The Annotations API enables:
- Precise text highlighting with character offsets
- Notes with semantic embeddings for search
- Tag-based organization
- Full-text and semantic search across annotations
- Export to Markdown and JSON formats

## Endpoints

### POST /resources/{resource_id}/annotations

Create a new annotation on a resource.

**Request Body:**
```json
{
  "start_offset": "integer (required, >= 0)",
  "end_offset": "integer (required, > start_offset)",
  "highlighted_text": "string (required)",
  "note": "string (optional, max 10,000 characters)",
  "tags": ["string"] (optional, max 20 tags),
  "color": "string (optional, hex color, default: #FFFF00)",
  "collection_ids": ["uuid"] (optional)
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "user123",
  "start_offset": 150,
  "end_offset": 200,
  "highlighted_text": "This is the key finding of the paper",
  "note": "Important result - contradicts previous assumptions",
  "tags": ["key-finding", "methodology"],
  "color": "#FFD700",
  "context_before": "...previous text leading up to...",
  "context_after": "...text following the highlight...",
  "is_shared": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Performance:** <50ms creation time (excluding async embedding generation)

---

### GET /resources/{resource_id}/annotations

List all annotations for a specific resource in document order.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `include_shared` | boolean | Include shared annotations | false |
| `tags` | string[] | Filter by tags (comma-separated) | - |

**Response:** Array of annotations ordered by `start_offset` ascending.

---

### GET /annotations

List all annotations for the authenticated user across all resources.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Results per page (1-100) | 50 |
| `offset` | integer | Number to skip | 0 |
| `sort_by` | string | Sort order (recent/oldest) | recent |

---

### GET /annotations/{annotation_id}

Retrieve a specific annotation by ID.

---

### PUT /annotations/{annotation_id}

Update an annotation's note, tags, color, or sharing status.

**Request Body:**
```json
{
  "note": "string (optional)",
  "tags": ["string"] (optional),
  "color": "string (optional)",
  "is_shared": "boolean (optional)"
}
```

**Note:** Cannot update `start_offset`, `end_offset`, or `highlighted_text`.

---

### DELETE /annotations/{annotation_id}

Delete an annotation.

**Response:** `204 No Content`

---

## Search Endpoints

### GET /annotations/search/fulltext

Search annotations using full-text search across notes and highlighted text.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query (required) | - |
| `limit` | integer | Max results (1-100) | 25 |

**Performance:** <100ms for 10,000 annotations

---

### GET /annotations/search/semantic

Search annotations using semantic similarity for conceptual discovery.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query (required) | - |
| `limit` | integer | Max results (1-50) | 10 |

**Response includes `similarity` score (0.0-1.0).**

**Performance:** <500ms for 1,000 annotations

---

### GET /annotations/search/tags

Search annotations by tags with flexible matching.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `tags` | string[] | Tags to search (comma-separated) | - |
| `match_all` | boolean | Require all tags (true) or any (false) | false |
| `limit` | integer | Max results (1-100) | 50 |

---

## Export Endpoints

### GET /annotations/export/markdown

Export annotations to Markdown format.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `resource_id` | string | Filter by resource (optional) | - |

**Response:** `Content-Type: text/markdown`

```markdown
# Annotations Export

## Deep Learning Fundamentals

### Annotation 1
**Highlighted Text:**
> This is the key finding of the paper

**Note:** Important result

**Tags:** key-finding, methodology

**Created:** 2024-01-01 10:00:00
```

---

### GET /annotations/export/json

Export annotations to JSON format with complete metadata.

**Response:**
```json
{
  "annotations": [...],
  "total": 1,
  "exported_at": "2024-01-01T12:00:00Z"
}
```

## Features

### Text Offset Tracking

Annotations use character offsets for precise positioning:
- Zero-indexed character positions
- `start_offset`: First character (inclusive)
- `end_offset`: Last character (exclusive)
- Example: `"Hello World"[0:5]` = `"Hello"`

### Context Extraction

Automatically captures 50 characters before and after the highlight for preview.

### Semantic Embeddings

Annotations with notes get automatic semantic embeddings:
- Generated asynchronously after creation
- Uses nomic-ai/nomic-embed-text-v1 (384 dimensions)
- Enables semantic search across annotations

### Privacy Model

- `is_shared=false`: Only owner can view (default)
- `is_shared=true`: Visible to all users with resource access

## Data Models

### Annotation Model

```json
{
  "id": "uuid",
  "resource_id": "uuid",
  "user_id": "string",
  "start_offset": "integer (>= 0)",
  "end_offset": "integer (> start_offset)",
  "highlighted_text": "string",
  "note": "string or null (max 10,000 characters)",
  "tags": ["string"] (max 20 tags),
  "color": "string (hex color)",
  "embedding": [float] or null (384-dimensional),
  "context_before": "string or null",
  "context_after": "string or null",
  "is_shared": "boolean",
  "collection_ids": ["uuid"] or null,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Module Structure

The Annotations module is implemented as a self-contained vertical slice:

**Module**: `app.modules.annotations`  
**Router Prefix**: `/annotations`  
**Version**: 1.0.0

```python
from app.modules.annotations import (
    annotations_router,
    AnnotationService,
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse
)
```

### Events

**Emitted Events:**
- `annotation.created` - When a new annotation is created
- `annotation.updated` - When an annotation is modified
- `annotation.deleted` - When an annotation is removed

**Subscribed Events:**
- `resource.deleted` - Cascade deletes annotations for deleted resources

## Related Documentation

- [Resources API](resources.md) - Content management
- [Search API](search.md) - Search capabilities
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors
