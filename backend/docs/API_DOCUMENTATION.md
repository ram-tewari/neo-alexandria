# Neo Alexandria 2.0 API Reference

## Overview

The Neo Alexandria 2.0 API provides comprehensive endpoints for knowledge management, content processing, search, and discovery. This reference documentation covers all available endpoints, request/response formats, authentication, and error handling.

## Base URL

```
http://127.0.0.1:8000
```

## Authentication

Currently, no authentication is required. Future releases will implement API key authentication.

**Future Authentication:**
- API Key in `Authorization` header: `Authorization: Bearer <api_key>`
- Rate limiting: 1000 requests/hour per API key
- Ingestion limits: 100 requests/hour per API key

## Content Types

All API endpoints accept and return JSON data with the following content type:
```
Content-Type: application/json
```

## Error Handling

The API uses standard HTTP status codes and returns structured error responses:

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 202 | Accepted - Request accepted for processing |
| 400 | Bad Request - Invalid request parameters |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

## Endpoints

### Content Management

#### POST /resources

Creates a new resource by ingesting content from a URL with AI-powered asynchronous processing.

**Request Body:**
```json
{
  "url": "string (required)",
  "title": "string (optional)",
  "description": "string (optional)",
  "language": "string (optional)",
  "type": "string (optional)",
  "source": "string (optional)"
}
```

**Response (202 Accepted):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

**Background Processing:**
The system performs the following steps asynchronously:
1. Fetch content from the provided URL
2. Extract text from HTML/PDF content
3. Generate AI-powered summary using transformers
4. Generate intelligent tags using zero-shot classification
5. Normalize metadata using authority control
6. Classify content using the classification system
7. Calculate quality score
8. Archive content locally
9. Update resource status to "completed" or "failed"

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

#### GET /resources/{resource_id}/status

Monitor the ingestion status of a resource.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ingestion_status": "completed",
  "ingestion_error": null,
  "ingestion_started_at": "2024-01-01T10:00:00Z",
  "ingestion_completed_at": "2024-01-01T10:02:30Z"
}
```

**Status Values:**
- `pending` - Request received, processing not started
- `processing` - Content is being processed
- `completed` - Processing finished successfully
- `failed` - Processing failed with error

#### GET /resources

List resources with filtering, sorting, and pagination.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `q` | string | Keyword search on title/description | - |
| `classification_code` | string | Filter by classification code | - |
| `type` | string | Filter by resource type | - |
| `language` | string | Filter by language | - |
| `read_status` | string | Filter by read status | - |
| `min_quality` | float | Minimum quality score (0.0-1.0) | - |
| `created_from` | datetime | Filter by creation date (ISO 8601) | - |
| `created_to` | datetime | Filter by creation date (ISO 8601) | - |
| `updated_from` | datetime | Filter by update date (ISO 8601) | - |
| `updated_to` | datetime | Filter by update date (ISO 8601) | - |
| `subject_any` | string[] | Filter by any of these subjects | - |
| `subject_all` | string[] | Filter by all of these subjects | - |
| `limit` | integer | Number of results (1-100) | 25 |
| `offset` | integer | Number of results to skip | 0 |
| `sort_by` | string | Sort field | updated_at |
| `sort_dir` | string | Sort direction (asc/desc) | desc |

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "description": "Comprehensive guide to ML concepts",
      "creator": "John Doe",
      "publisher": "Tech Publications",
      "source": "https://example.com/ml-guide",
      "language": "en",
      "type": "article",
      "subject": ["Machine Learning", "Artificial Intelligence"],
      "classification_code": "004",
      "quality_score": 0.85,
      "read_status": "unread",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:02:30Z"
    }
  ],
  "total": 1
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/resources?limit=5&classification_code=004&min_quality=0.8"
```

#### GET /resources/{resource_id}

Retrieve a specific resource by ID.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Machine Learning Fundamentals",
  "description": "Comprehensive guide to ML concepts",
  "creator": "John Doe",
  "publisher": "Tech Publications",
  "source": "https://example.com/ml-guide",
  "language": "en",
  "type": "article",
  "subject": ["Machine Learning", "Artificial Intelligence"],
  "classification_code": "004",
  "quality_score": 0.85,
  "read_status": "unread",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:02:30Z"
}
```

#### PUT /resources/{resource_id}

Update a resource with partial data. Only provided fields are modified.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "read_status": "in_progress",
  "subject": ["Updated", "Tags"]
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated Title",
  "description": "Updated description",
  "read_status": "in_progress",
  "subject": ["Updated", "Tags"],
  "updated_at": "2024-01-01T11:00:00Z"
}
```

#### DELETE /resources/{resource_id}

Delete a resource by ID.

**Response:**
```
204 No Content
```

#### PUT /resources/{resource_id}/classify

Override the classification code for a specific resource.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `resource_id` | string | Resource UUID |

**Request Body:**
```json
{
  "code": "004"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Resource Title",
  "classification_code": "004",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

### Search and Discovery

#### POST /search

Advanced search with hybrid keyword/semantic capabilities and faceted results.

**Request Body:**
```json
{
  "text": "machine learning algorithms",
  "hybrid_weight": 0.5,
  "filters": {
    "classification_code": ["004"],
    "language": ["en"],
    "min_quality": 0.7,
    "subject_any": ["Machine Learning"],
    "subject_all": ["Artificial Intelligence", "Machine Learning"]
  },
  "limit": 25,
  "offset": 0,
  "sort_by": "relevance",
  "sort_dir": "desc"
}
```

**Request Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `text` | string | Search query text | - |
| `hybrid_weight` | float | Weight for hybrid search (0.0-1.0) | 0.5 |
| `filters` | object | Filter criteria | - |
| `limit` | integer | Number of results (1-100) | 25 |
| `offset` | integer | Number of results to skip | 0 |
| `sort_by` | string | Sort field | relevance |
| `sort_dir` | string | Sort direction (asc/desc) | desc |

**Hybrid Search Weight:**
- `0.0` - Pure keyword search (FTS5)
- `0.5` - Balanced hybrid search (default)
- `1.0` - Pure semantic search (vector similarity)

**Response:**
```json
{
  "total": 42,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "description": "Comprehensive guide to ML concepts",
      "subject": ["Machine Learning", "Artificial Intelligence"],
      "quality_score": 0.85,
      "relevance_score": 0.92,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:02:30Z"
    }
  ],
  "facets": {
    "classification_code": [
      {"key": "004", "count": 30}
    ],
    "type": [
      {"key": "article", "count": 35}
    ],
    "language": [
      {"key": "en", "count": 33}
    ],
    "read_status": [
      {"key": "unread", "count": 20}
    ],
    "subject": [
      {"key": "Machine Learning", "count": 18}
    ]
  }
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "text": "artificial intelligence",
    "hybrid_weight": 0.7,
    "filters": {
      "min_quality": 0.8
    },
    "limit": 10
  }'
```

#### GET /recommendations

Get personalized content recommendations based on existing library content.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recommendations (1-100) | 10 |

**Response:**
```json
{
  "items": [
    {
      "url": "https://example.com/new-ml-article",
      "title": "Latest Advances in Machine Learning",
      "snippet": "Recent developments in ML algorithms and applications",
      "relevance_score": 0.85,
      "reasoning": ["Aligned with Machine Learning, Python"]
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/recommendations?limit=5"
```

### Knowledge Graph

#### GET /graph/resource/{resource_id}/neighbors

Find related resources for mind-map visualization.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of neighbors (1-50) | 7 |

**Response:**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "type": "article",
      "classification_code": "004"
    }
  ],
  "edges": [
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "550e8400-e29b-41d4-a716-446655440001",
      "weight": 0.76,
      "details": {
        "connection_type": "classification",
        "vector_similarity": 0.8,
        "shared_subjects": ["python", "programming"]
      }
    }
  ]
}
```

#### GET /graph/overview

Get global relationship overview of strongest connections across the library.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of edges (1-200) | 50 |
| `vector_threshold` | float | Minimum vector similarity threshold | 0.85 |

**Response:**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "type": "article",
      "classification_code": "004"
    }
  ],
  "edges": [
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "550e8400-e29b-41d4-a716-446655440001",
      "weight": 0.76,
      "details": {
        "connection_type": "hybrid",
        "vector_similarity": 0.8,
        "shared_subjects": ["python", "programming"],
        "classification_match": true
      }
    }
  ]
}
```

### Authority and Classification

#### GET /authority/subjects/suggest

Get subject suggestions for autocomplete functionality.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `q` | string | Search query for subjects (required) | - |

**Response:**
```json
[
  "Machine Learning",
  "Artificial Intelligence",
  "Data Science"
]
```

#### GET /authority/classification/tree

Retrieve the hierarchical classification tree.

**Response:**
```json
{
  "tree": [
    {
      "code": "000",
      "name": "General",
      "description": "General knowledge and reference",
      "children": [
        {
          "code": "004",
          "name": "Computer Science",
          "description": "Computer science and programming",
          "children": []
        }
      ]
    }
  ]
}
```

#### GET /classification/tree

Alternative endpoint for retrieving the hierarchical classification tree.

**Response:**
```json
{
  "tree": [
    {
      "code": "000",
      "name": "General",
      "description": "General knowledge and reference",
      "children": [
        {
          "code": "004",
          "name": "Computer Science",
          "description": "Computer science and programming",
          "children": []
        }
      ]
    }
  ]
}
```

### Curation and Quality Control

#### GET /curation/review-queue

Access low-quality items for review and curation.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold for filtering | null |
| `include_unread_only` | boolean | Include only unread items | false |
| `limit` | integer | Number of items (1-100) | 25 |
| `offset` | integer | Number of results to skip | 0 |

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Low Quality Article",
      "description": "Poor quality content",
      "quality_score": 0.3,
      "read_status": "unread",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### GET /curation/low-quality

Get resources with quality scores below a specified threshold.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold (0.0-1.0) | 0.5 |
| `limit` | integer | Number of items (1-100) | 25 |
| `offset` | integer | Number of results to skip | 0 |

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Low Quality Article",
      "description": "Poor quality content",
      "quality_score": 0.3,
      "read_status": "unread",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### GET /curation/quality-analysis/{resource_id}

Get detailed quality analysis for a specific resource.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `resource_id` | string | Resource UUID |

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata_completeness": 0.8,
  "readability": {
    "flesch_kincaid": 12.5,
    "gunning_fog": 14.2,
    "automated_readability": 11.8
  },
  "source_credibility": 0.7,
  "content_depth": 0.6,
  "overall_quality": 0.7,
  "quality_level": "good",
  "suggestions": [
    "Improve metadata completeness",
    "Add more detailed description"
  ]
}
```

#### POST /curation/batch-update

Apply partial updates to multiple resources in a single transaction.

**Request Body:**
```json
{
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
  ],
  "updates": {
    "read_status": "in_progress",
    "subject": ["Updated", "Tags"]
  }
}
```

**Response:**
```json
{
  "updated_count": 2,
  "updated_resources": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
  ]
}
```

#### POST /curation/bulk-quality-check

Perform quality analysis on multiple resources.

**Request Body:**
```json
{
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
  ]
}
```

**Response:**
```json
{
  "updated_count": 2,
  "updated_resources": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
  ]
}
```

## Data Models

### Resource Model

The core resource model follows Dublin Core metadata standards with custom extensions:

```json
{
  "id": "uuid",
  "title": "string (required)",
  "description": "string",
  "creator": "string",
  "publisher": "string",
  "contributor": "string",
  "source": "string",
  "language": "string",
  "type": "string",
  "format": "string",
  "identifier": "string",
  "subject": ["string"],
  "relation": ["string"],
  "coverage": "string",
  "rights": "string",
  "classification_code": "string",
  "read_status": "unread|in_progress|completed|archived",
  "quality_score": "float (0.0-1.0)",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### Search Request Model

```json
{
  "text": "string",
  "hybrid_weight": "float (0.0-1.0)",
  "filters": {
    "classification_code": ["string"],
    "language": ["string"],
    "type": ["string"],
    "read_status": ["string"],
    "min_quality": "float",
    "max_quality": "float",
    "created_from": "datetime",
    "created_to": "datetime",
    "updated_from": "datetime",
    "updated_to": "datetime",
    "subject_any": ["string"],
    "subject_all": ["string"]
  },
  "limit": "integer (1-100)",
  "offset": "integer (>=0)",
  "sort_by": "relevance|updated_at|created_at|quality_score|title",
  "sort_dir": "asc|desc"
}
```

### Search Response Model

```json
{
  "total": "integer",
  "items": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "subject": ["string"],
      "quality_score": "float",
      "relevance_score": "float",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "facets": {
    "classification_code": [{"key": "string", "count": "integer"}],
    "type": [{"key": "string", "count": "integer"}],
    "language": [{"key": "string", "count": "integer"}],
    "read_status": [{"key": "string", "count": "integer"}],
    "subject": [{"key": "string", "count": "integer"}]
  }
}
```

### Recommendation Response Model

```json
{
  "items": [
    {
      "url": "string",
      "title": "string",
      "snippet": "string",
      "relevance_score": "float (0.0-1.0)",
      "reasoning": ["string"]
    }
  ]
}
```

### Graph Response Model

```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "string",
      "type": "string",
      "classification_code": "string"
    }
  ],
  "edges": [
    {
      "source": "uuid",
      "target": "uuid",
      "weight": "float (0.0-1.0)",
      "details": {
        "connection_type": "vector|subject|classification|hybrid",
        "vector_similarity": "float",
        "shared_subjects": ["string"],
        "classification_match": "boolean"
      }
    }
  ]
}
```

## Rate Limits

Currently, no rate limits are enforced. Future releases will implement:

- **General API**: 1000 requests per hour per API key
- **Ingestion**: 100 requests per hour per API key
- **Search**: 500 requests per hour per API key
- **Burst Allowance**: 50 requests per minute for short-term spikes

## SDKs and Libraries

### Python
```python
import requests

# Ingest a resource
response = requests.post(
    "http://127.0.0.1:8000/resources",
    json={"url": "https://example.com/article"}
)

# Search resources
response = requests.post(
    "http://127.0.0.1:8000/search",
    json={
        "text": "machine learning",
        "hybrid_weight": 0.7,
        "limit": 10
    }
)
```

### JavaScript
```javascript
// Ingest a resource
const response = await fetch('http://127.0.0.1:8000/resources', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://example.com/article'
  })
});

// Search resources
const searchResponse = await fetch('http://127.0.0.1:8000/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'machine learning',
    hybrid_weight: 0.7,
    limit: 10
  })
});
```

## Webhooks

Webhooks are not currently supported but are planned for future releases to notify external systems of:
- Resource ingestion completion
- Quality score updates
- Classification changes
- System status updates

## Complete Endpoint Reference

### Content Management
- `POST /resources` - Ingest new resource from URL
- `GET /resources` - List resources with filtering and pagination
- `GET /resources/{resource_id}` - Get specific resource
- `PUT /resources/{resource_id}` - Update resource metadata
- `DELETE /resources/{resource_id}` - Delete resource
- `GET /resources/{resource_id}/status` - Check ingestion status
- `PUT /resources/{resource_id}/classify` - Override classification code

### Search and Discovery
- `POST /search` - Advanced hybrid search with faceted results

### Knowledge Graph
- `GET /graph/resource/{resource_id}/neighbors` - Get resource neighbors for mind-map
- `GET /graph/overview` - Get global overview of strongest connections

### Recommendations
- `GET /recommendations` - Get personalized content recommendations

### Authority and Classification
- `GET /authority/subjects/suggest` - Get subject suggestions for autocomplete
- `GET /authority/classification/tree` - Get hierarchical classification tree
- `GET /classification/tree` - Alternative classification tree endpoint

### Curation and Quality Control
- `GET /curation/review-queue` - Access low-quality items for review
- `GET /curation/low-quality` - Get resources below quality threshold
- `GET /curation/quality-analysis/{resource_id}` - Get detailed quality analysis
- `POST /curation/batch-update` - Apply batch updates to multiple resources
- `POST /curation/bulk-quality-check` - Perform quality analysis on multiple resources

### Collection Management
- `POST /collections` - Create new collection
- `GET /collections/{id}` - Get collection with member resources
- `PUT /collections/{id}` - Update collection metadata
- `DELETE /collections/{id}` - Delete collection and subcollections
- `GET /collections` - List collections with filtering
- `POST /collections/{id}/resources` - Add resources to collection
- `DELETE /collections/{id}/resources` - Remove resources from collection
- `GET /collections/{id}/recommendations` - Get similar resources and collections
- `GET /collections/{id}/embedding` - Get collection aggregate embedding

## Changelog

### Version 0.9.0 (Phase 7)
- Added collection management system
- Implemented hierarchical collection organization
- Added aggregate embedding computation
- Implemented collection-based recommendations
- Added batch resource membership operations
- Integrated collection cleanup with resource deletion

### Version 0.7.0 (Phase 5.5)
- Added personalized recommendation system
- Enhanced knowledge graph with hybrid scoring
- Improved search performance and accuracy

### Version 0.6.0 (Phase 5)
- Added hybrid knowledge graph system
- Implemented mind-map neighbor discovery
- Added global relationship overview

### Version 0.5.0 (Phase 4)
- Added vector embeddings and semantic search
- Implemented hybrid search fusion
- Enhanced search with faceted results

### Version 0.4.0 (Phase 3.5)
- Added AI-powered asynchronous ingestion
- Implemented real AI summarization and tagging
- Added status tracking for ingestion processes

### Version 0.3.0 (Phase 3)
- Added advanced search with FTS5
- Implemented faceted search capabilities
- Added authority control system

### Version 0.2.0 (Phase 2)
- Added CRUD operations for resources
- Implemented curation workflows
- Added batch update capabilities

### Version 0.1.0 (Phase 1)
- Initial URL ingestion system
- Basic content extraction and processing
- Local content archiving

## Support

For API support and questions:
- GitHub Issues for bug reports and feature requests
- Documentation updates and improvements
- Community contributions and feedback

##
 Citation Network Endpoints

### GET /citations/resources/{resource_id}/citations

Retrieve all citations for a specific resource, including both outbound citations (resources this one cites) and inbound citations (resources that cite this one).

**Path Parameters:**
- `resource_id` (string, required): UUID of the resource

**Query Parameters:**
- `direction` (string, optional): Citation direction filter
  - `outbound`: Only citations from this resource
  - `inbound`: Only citations to this resource
  - `both` (default): Both directions

**Response (200 OK):**
```json
{
  "resource_id": "uuid",
  "outbound": [
    {
      "id": "uuid",
      "source_resource_id": "uuid",
      "target_url": "string",
      "target_resource_id": "uuid or null",
      "citation_type": "reference|dataset|code|general",
      "context_snippet": "string or null",
      "position": "integer or null",
      "importance_score": "float or null",
      "created_at": "datetime",
      "updated_at": "datetime",
      "target_resource": {
        "id": "uuid",
        "title": "string",
        "source": "string"
      }
    }
  ],
  "inbound": [
    {
      "id": "uuid",
      "source_resource_id": "uuid",
      "target_url": "string",
      "target_resource_id": "uuid",
      "citation_type": "reference|dataset|code|general",
      "context_snippet": "string or null",
      "position": "integer or null",
      "importance_score": "float or null",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "counts": {
    "outbound": "integer",
    "inbound": "integer",
    "total": "integer"
  }
}
```

**Example:**
```bash
# Get all citations for a resource
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations"

# Get only outbound citations
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations?direction=outbound"

# Get only inbound citations
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations?direction=inbound"
```

**Use Cases:**
- Display citation information on resource detail pages
- Analyze citation patterns and relationships
- Identify highly-cited resources
- Track citation networks

---

### GET /citations/graph/citations

Get citation network for visualization, optionally filtered by specific resources or importance threshold.

**Query Parameters:**
- `resource_ids` (array[string], optional): Filter to specific resource UUIDs
- `min_importance` (float, optional): Minimum importance score (0.0-1.0), default: 0.0
- `depth` (integer, optional): Graph traversal depth (1-2), default: 1

**Response (200 OK):**
```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "string",
      "type": "source|cited|citing"
    }
  ],
  "edges": [
    {
      "source": "uuid",
      "target": "uuid",
      "type": "reference|dataset|code|general"
    }
  ]
}
```

**Example:**
```bash
# Get global citation network
curl "http://127.0.0.1:8000/citations/graph/citations"

# Get citation network for specific resources
curl "http://127.0.0.1:8000/citations/graph/citations?resource_ids=uuid1&resource_ids=uuid2"

# Get high-importance citations only
curl "http://127.0.0.1:8000/citations/graph/citations?min_importance=0.7"

# Get deeper citation network
curl "http://127.0.0.1:8000/citations/graph/citations?depth=2"
```

**Use Cases:**
- Visualize citation networks in graph UI
- Identify citation clusters and communities
- Analyze citation flow and influence
- Discover related resources through citations

**Performance Notes:**
- Results are limited to 100 nodes maximum
- Depth is capped at 2 to prevent exponential explosion
- Use `min_importance` to filter for significant citations

---

### POST /citations/resources/{resource_id}/citations/extract

Manually trigger citation extraction for a resource. This is typically done automatically during ingestion but can be triggered manually for debugging or re-extraction.

**Path Parameters:**
- `resource_id` (string, required): UUID of the resource

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "resource_id": "uuid",
  "message": "Citation extraction queued for processing"
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/citations/resources/{resource_id}/citations/extract"
```

**Background Processing:**
The system performs the following steps asynchronously:
1. Retrieve resource content from archive
2. Determine content type (HTML, PDF, Markdown)
3. Extract citations using appropriate parser
4. Classify citation types (dataset, code, reference, general)
5. Extract context snippets around citations
6. Store citations in database
7. Trigger internal citation resolution

**Use Cases:**
- Re-extract citations after content updates
- Debug citation extraction issues
- Manually process resources that failed automatic extraction

---

### POST /citations/resolve

Manually trigger internal citation resolution to match unresolved citation URLs to existing resources in the database.

**Response (202 Accepted):**
```json
{
  "status": "queued"
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/citations/resolve"
```

**Background Processing:**
The system performs the following steps asynchronously:
1. Query all citations with `target_resource_id = NULL`
2. Normalize citation URLs (remove fragments, trailing slashes)
3. Match URLs to existing resources in database
4. Update `target_resource_id` for matched citations
5. Process in batches of 100 for performance

**Use Cases:**
- Resolve citations after bulk resource imports
- Update citation links after URL changes
- Periodic maintenance to link new resources

**Performance Notes:**
- Processes citations in batches of 100
- Uses bulk database operations for efficiency
- Typically completes in <1 second for 100 citations

---

### POST /citations/importance/compute

Recompute PageRank importance scores for all citations. This is a computationally expensive operation that should be run periodically (e.g., daily) rather than on every request.

**Response (202 Accepted):**
```json
{
  "status": "queued"
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/citations/importance/compute"
```

**Background Processing:**
The system performs the following steps asynchronously:
1. Build citation graph from all resolved citations
2. Run PageRank algorithm with:
   - Damping factor: 0.85
   - Max iterations: 100
   - Convergence threshold: 1e-6
3. Normalize scores to [0, 1] range
4. Update `importance_score` for all citations
5. Return mapping of resource_id → importance_score

**Use Cases:**
- Periodic importance score updates (daily/weekly)
- After bulk citation imports
- Identify influential resources in citation network

**Performance Notes:**
- Uses NetworkX for PageRank computation
- Typically completes in <5 seconds for 1000 resources
- Sparse matrix representation for efficiency
- Can be scheduled as a background job

---

## Collection Management Endpoints

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

**Authentication:** Required (owner_id extracted from token)

**Error Responses:**
- `400 Bad Request` - Invalid name length, visibility value, or circular hierarchy
- `401 Unauthorized` - No authentication token provided
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

**Path Parameters:**
- `id` (string, required): UUID of the collection

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
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "title": "Neural Network Architectures",
      "creator": "Jane Smith",
      "quality_score": 0.88
    }
  ]
}
```

**Authentication:** Required (visibility check applied)

**Access Rules:**
- `private`: Only owner can access
- `shared`: Owner + explicit permissions (future)
- `public`: All authenticated users

**Error Responses:**
- `403 Forbidden` - User does not have access to collection
- `404 Not Found` - Collection not found

**Example:**
```bash
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000"
```

---

### PUT /collections/{id}

Update collection metadata (name, description, visibility, parent).

**Path Parameters:**
- `id` (string, required): UUID of the collection

**Request Body:**
```json
{
  "name": "string (optional, 1-255 characters)",
  "description": "string (optional, max 2000 characters)",
  "visibility": "private|shared|public (optional)",
  "parent_id": "string (optional, UUID or null)"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Collection Name",
  "description": "Updated description",
  "owner_id": "user123",
  "visibility": "private",
  "parent_id": null,
  "resource_count": 2,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:00:00Z",
  "resources": []
}
```

**Authentication:** Required (owner only)

**Error Responses:**
- `400 Bad Request` - Invalid field values or circular hierarchy
- `403 Forbidden` - User is not the collection owner
- `404 Not Found` - Collection or parent not found

**Example:**
```bash
curl -X PUT http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Collection Name",
    "visibility": "private"
  }'
```

---

### DELETE /collections/{id}

Delete a collection and all its subcollections recursively.

**Path Parameters:**
- `id` (string, required): UUID of the collection

**Response (204 No Content)**

**Authentication:** Required (owner only)

**Cascade Behavior:**
- Deletes all descendant collections recursively
- Removes all collection-resource associations
- Does NOT delete the member resources themselves

**Error Responses:**
- `403 Forbidden` - User is not the collection owner
- `404 Not Found` - Collection not found

**Example:**
```bash
curl -X DELETE http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000
```

---

### GET /collections

List collections with filtering and pagination.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Filter by owner UUID | - |
| `visibility` | string | Filter by visibility (private/shared/public) | - |
| `page` | integer | Page number (1-based) | 1 |
| `limit` | integer | Results per page (1-100) | 50 |

**Response (200 OK):**
```json
{
  "items": [
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
      "resources": []
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

**Authentication:** Required (filtered by access)

**Access Filtering:**
- Returns collections where user is owner OR visibility is public
- Private collections only visible to owner

**Example:**
```bash
# List all accessible collections
curl "http://127.0.0.1:8000/collections"

# Filter by owner
curl "http://127.0.0.1:8000/collections?owner_id=user123"

# Filter by visibility
curl "http://127.0.0.1:8000/collections?visibility=public&limit=10"

# Pagination
curl "http://127.0.0.1:8000/collections?page=2&limit=25"
```

---

### POST /collections/{id}/resources

Add resources to a collection (batch operation).

**Path Parameters:**
- `id` (string, required): UUID of the collection

**Request Body:**
```json
{
  "resource_ids": ["uuid", "uuid", ...] (1-100 items)
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 5,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:10:00Z",
  "resources": []
}
```

**Authentication:** Required (owner only)

**Behavior:**
- Validates all resource IDs exist before adding
- Handles duplicate associations gracefully (idempotent)
- Triggers aggregate embedding recomputation
- Supports batch operations up to 100 resources

**Error Responses:**
- `400 Bad Request` - Invalid resource IDs or exceeds batch limit
- `403 Forbidden` - User is not the collection owner
- `404 Not Found` - Collection or resources not found

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "660e8400-e29b-41d4-a716-446655440001",
      "770e8400-e29b-41d4-a716-446655440002"
    ]
  }'
```

---

### DELETE /collections/{id}/resources

Remove resources from a collection (batch operation).

**Path Parameters:**
- `id` (string, required): UUID of the collection

**Request Body:**
```json
{
  "resource_ids": ["uuid", "uuid", ...] (1-100 items)
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 3,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:15:00Z",
  "resources": []
}
```

**Authentication:** Required (owner only)

**Behavior:**
- Removes specified resource associations
- Triggers aggregate embedding recomputation
- Supports batch operations up to 100 resources
- Idempotent (no error if resource not in collection)

**Error Responses:**
- `400 Bad Request` - Invalid resource IDs or exceeds batch limit
- `403 Forbidden` - User is not the collection owner
- `404 Not Found` - Collection not found

**Example:**
```bash
curl -X DELETE http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "660e8400-e29b-41d4-a716-446655440001"
    ]
  }'
```

---

### GET /collections/{id}/recommendations

Get recommendations for similar resources and collections based on aggregate embedding.

**Path Parameters:**
- `id` (string, required): UUID of the collection

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Max results per category (1-50) | 10 |
| `include_resources` | boolean | Include resource recommendations | true |
| `include_collections` | boolean | Include collection recommendations | true |

**Response (200 OK):**
```json
{
  "resources": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "title": "Advanced Neural Networks",
      "similarity": 0.92
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "title": "Reinforcement Learning Basics",
      "similarity": 0.87
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

**Authentication:** Required (visibility check applied)

**Algorithm:**
1. Retrieves collection aggregate embedding
2. Computes cosine similarity with all resources/collections
3. Excludes resources already in collection
4. Excludes source collection from collection recommendations
5. Applies access control (only public collections for other users)
6. Returns top N results sorted by similarity

**Error Responses:**
- `400 Bad Request` - Collection has no embedding (no member resources)
- `403 Forbidden` - User does not have access to collection
- `404 Not Found` - Collection not found

**Example:**
```bash
# Get all recommendations
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/recommendations"

# Get only resource recommendations
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/recommendations?include_collections=false&limit=20"

# Get only collection recommendations
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/recommendations?include_resources=false&limit=5"
```

---

### GET /collections/{id}/embedding

Retrieve the aggregate embedding vector for a collection.

**Path Parameters:**
- `id` (string, required): UUID of the collection

**Response (200 OK):**
```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimension": 768
}
```

**Authentication:** Required (visibility check applied)

**Use Cases:**
- Export embeddings for external analysis
- Verify embedding computation
- Custom similarity calculations

**Error Responses:**
- `400 Bad Request` - Collection has no embedding
- `403 Forbidden` - User does not have access to collection
- `404 Not Found` - Collection not found

**Example:**
```bash
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/embedding"
```

---

## Collection Data Models

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
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)",
  "resources": [
    {
      "id": "uuid",
      "title": "string",
      "creator": "string or null",
      "quality_score": "float (0.0-1.0)"
    }
  ]
}
```

**Field Descriptions:**
- `id`: Unique collection identifier
- `name`: Collection name (required, 1-255 characters)
- `description`: Optional description (max 2000 characters)
- `owner_id`: User who created the collection
- `visibility`: Access control level
  - `private`: Only owner can access
  - `shared`: Owner + explicit permissions (future)
  - `public`: All authenticated users can read
- `parent_id`: Parent collection for hierarchical organization (null for top-level)
- `resource_count`: Number of resources in collection
- `resources`: Array of resource summaries (only in GET /collections/{id})

### Collection List Response Model

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string or null",
      "owner_id": "string",
      "visibility": "private|shared|public",
      "parent_id": "uuid or null",
      "resource_count": "integer",
      "created_at": "datetime",
      "updated_at": "datetime",
      "resources": []
    }
  ],
  "total": "integer",
  "page": "integer",
  "limit": "integer"
}
```

### Recommendation Response Model

```json
{
  "resources": [
    {
      "id": "uuid",
      "title": "string",
      "similarity": "float (0.0-1.0)"
    }
  ],
  "collections": [
    {
      "id": "uuid",
      "name": "string",
      "similarity": "float (0.0-1.0)"
    }
  ]
}
```

---

## Collection Features

### Hierarchical Organization

Collections support parent-child relationships for organizing complex topic structures:

**Creating Nested Collections:**
```bash
# Create parent collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "Computer Science", "visibility": "public"}'

# Create child collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning",
    "parent_id": "{parent_id}",
    "visibility": "public"
  }'
```

**Circular Reference Prevention:**
The system validates hierarchy changes to prevent circular references. Attempting to set a collection's parent to one of its descendants will result in a `400 Bad Request` error.

**Cascade Deletion:**
Deleting a parent collection automatically deletes all descendant collections recursively.

### Aggregate Embeddings

Collections automatically compute aggregate embeddings from member resources:

**Computation Algorithm:**
1. Query all member resources with non-null embeddings
2. Compute mean vector across all dimensions
3. Normalize to unit length (L2 norm)
4. Store in collection.embedding field

**Automatic Updates:**
- Embedding recomputed when resources are added
- Embedding recomputed when resources are removed
- Embedding set to null if no member resources have embeddings

**Performance:**
- Computation completes in <1 second for collections with 1000 resources
- Uses NumPy for efficient vector operations

### Access Control

Collections implement granular access control based on visibility:

**Visibility Levels:**

| Level | Owner Access | Other Users Access |
|-------|-------------|-------------------|
| `private` | Full (read/write) | None |
| `shared` | Full (read/write) | Read only (future: explicit permissions) |
| `public` | Full (read/write) | Read only |

**Authorization Rules:**
- Only owner can update or delete collections
- Only owner can modify resource membership
- Read access determined by visibility level
- Collections filtered by access in list endpoint

### Resource Deletion Integration

Collections automatically update when resources are deleted:

**Automatic Cleanup:**
1. Resource deletion removes all collection-resource associations
2. Affected collections have embeddings recomputed
3. Resource counts updated automatically
4. No orphaned associations remain

**Performance:**
- Cleanup completes in <2 seconds for resources in 100 collections
- Uses database CASCADE constraints for efficiency

---

## Annotation Management Endpoints

### POST /resources/{resource_id}/annotations

Create a new annotation on a resource by highlighting text and optionally adding a note.

**Path Parameters:**
- `resource_id` (string, required): UUID of the resource

**Request Body:**
```json
{
  "start_offset": "integer (required, >= 0)",
  "end_offset": "integer (required, > start_offset)",
  "highlighted_text": "string (required)",
  "note": "string (optional, max 10,000 characters)",
  "tags": ["string"] (optional, max 20 tags, max 50 chars each),
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

**Authentication:** Required

**Behavior:**
- Validates resource exists and user has access
- Validates offsets (start < end, non-negative)
- Extracts 50 characters of context before/after highlight
- Generates semantic embedding if note provided (async)
- Target: <50ms creation time (excluding embedding)

**Error Responses:**
- `400 Bad Request` - Invalid offsets, text too long, or validation errors
- `401 Unauthorized` - No authentication token
- `404 Not Found` - Resource not found

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 150,
    "end_offset": 200,
    "highlighted_text": "This is the key finding of the paper",
    "note": "Important result - contradicts previous assumptions",
    "tags": ["key-finding", "methodology"],
    "color": "#FFD700"
  }'
```

---

### GET /resources/{resource_id}/annotations

List all annotations for a specific resource in document order.

**Path Parameters:**
- `resource_id` (string, required): UUID of the resource

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `include_shared` | boolean | Include shared annotations from other users | false |
| `tags` | string[] | Filter by tags (comma-separated) | - |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "user_id": "user123",
      "start_offset": 150,
      "end_offset": 200,
      "highlighted_text": "This is the key finding",
      "note": "Important result",
      "tags": ["key-finding"],
      "color": "#FFD700",
      "context_before": "...previous text...",
      "context_after": "...following text...",
      "is_shared": false,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Authentication:** Required

**Ordering:** Results ordered by start_offset ascending (document order)

**Example:**
```bash
# Get all user's annotations for resource
curl "http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations"

# Include shared annotations
curl "http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations?include_shared=true"

# Filter by tags
curl "http://127.0.0.1:8000/resources/660e8400-e29b-41d4-a716-446655440001/annotations?tags=key-finding,methodology"
```

---

### GET /annotations

List all annotations for the authenticated user across all resources.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Results per page (1-100) | 50 |
| `offset` | integer | Number of results to skip | 0 |
| `sort_by` | string | Sort order (recent/oldest) | recent |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "user_id": "user123",
      "start_offset": 150,
      "end_offset": 200,
      "highlighted_text": "This is the key finding",
      "note": "Important result",
      "tags": ["key-finding"],
      "color": "#FFD700",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

**Authentication:** Required

**Sorting:**
- `recent`: Sort by created_at descending (newest first)
- `oldest`: Sort by created_at ascending (oldest first)

**Example:**
```bash
# Get recent annotations
curl "http://127.0.0.1:8000/annotations?limit=20&sort_by=recent"

# Get oldest annotations with pagination
curl "http://127.0.0.1:8000/annotations?limit=50&offset=50&sort_by=oldest"
```

---

### GET /annotations/{annotation_id}

Retrieve a specific annotation by ID.

**Path Parameters:**
- `annotation_id` (string, required): UUID of the annotation

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_id": "660e8400-e29b-41d4-a716-446655440001",
  "resource_title": "Deep Learning Fundamentals",
  "user_id": "user123",
  "start_offset": 150,
  "end_offset": 200,
  "highlighted_text": "This is the key finding",
  "note": "Important result",
  "tags": ["key-finding"],
  "color": "#FFD700",
  "context_before": "...previous text...",
  "context_after": "...following text...",
  "is_shared": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Authentication:** Required

**Access Control:**
- User must be owner OR annotation must be shared

**Error Responses:**
- `403 Forbidden` - User does not have access to annotation
- `404 Not Found` - Annotation not found

**Example:**
```bash
curl "http://127.0.0.1:8000/annotations/550e8400-e29b-41d4-a716-446655440000"
```

---

### PUT /annotations/{annotation_id}

Update an existing annotation's note, tags, color, or sharing status.

**Path Parameters:**
- `annotation_id` (string, required): UUID of the annotation

**Request Body:**
```json
{
  "note": "string (optional, max 10,000 characters)",
  "tags": ["string"] (optional, max 20 tags),
  "color": "string (optional, hex color)",
  "is_shared": "boolean (optional)"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "user123",
  "start_offset": 150,
  "end_offset": 200,
  "highlighted_text": "This is the key finding",
  "note": "Updated note with new insights",
  "tags": ["key-finding", "revised"],
  "color": "#00FF00",
  "is_shared": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

**Authentication:** Required (owner only)

**Behavior:**
- Cannot update start_offset, end_offset, or highlighted_text
- Regenerates embedding if note is changed
- Updates updated_at timestamp automatically

**Error Responses:**
- `403 Forbidden` - User is not the annotation owner
- `404 Not Found` - Annotation not found

**Example:**
```bash
curl -X PUT http://127.0.0.1:8000/annotations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "note": "Updated note with new insights",
    "tags": ["key-finding", "revised"],
    "is_shared": true
  }'
```

---

### DELETE /annotations/{annotation_id}

Delete an annotation.

**Path Parameters:**
- `annotation_id` (string, required): UUID of the annotation

**Response (204 No Content)**

**Authentication:** Required (owner only)

**Error Responses:**
- `403 Forbidden` - User is not the annotation owner
- `404 Not Found` - Annotation not found

**Example:**
```bash
curl -X DELETE http://127.0.0.1:8000/annotations/550e8400-e29b-41d4-a716-446655440000
```

---

### GET /annotations/search/fulltext

Search annotations using full-text search across notes and highlighted text.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query (required) | - |
| `limit` | integer | Max results (1-100) | 25 |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "highlighted_text": "machine learning algorithms",
      "note": "Key discussion of ML algorithms",
      "tags": ["algorithms"],
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Authentication:** Required

**Search Behavior:**
- Searches both note and highlighted_text fields
- Case-insensitive LIKE query
- Returns only user's own annotations
- Target: <100ms for 10,000 annotations

**Example:**
```bash
curl "http://127.0.0.1:8000/annotations/search/fulltext?query=machine+learning&limit=10"
```

---

### GET /annotations/search/semantic

Search annotations using semantic similarity for conceptual discovery.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query (required) | - |
| `limit` | integer | Max results (1-50) | 10 |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "highlighted_text": "neural network architectures",
      "note": "Discussion of CNN and RNN structures",
      "tags": ["architecture"],
      "similarity": 0.92,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Authentication:** Required

**Search Behavior:**
- Generates embedding for query text
- Computes cosine similarity with annotation embeddings
- Returns results sorted by similarity descending
- Only searches annotations with embeddings
- Target: <500ms for 1,000 annotations

**Example:**
```bash
curl "http://127.0.0.1:8000/annotations/search/semantic?query=deep+learning+architectures&limit=10"
```

---

### GET /annotations/search/tags

Search annotations by tags with flexible matching.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `tags` | string[] | Tags to search (comma-separated, required) | - |
| `match_all` | boolean | Require all tags (true) or any tag (false) | false |
| `limit` | integer | Max results (1-100) | 50 |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "highlighted_text": "key finding",
      "note": "Important result",
      "tags": ["key-finding", "methodology"],
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Authentication:** Required

**Matching Modes:**
- `match_all=false`: Returns annotations with ANY of the specified tags
- `match_all=true`: Returns annotations with ALL of the specified tags

**Example:**
```bash
# Find annotations with any of these tags
curl "http://127.0.0.1:8000/annotations/search/tags?tags=key-finding,methodology&match_all=false"

# Find annotations with all of these tags
curl "http://127.0.0.1:8000/annotations/search/tags?tags=key-finding,methodology&match_all=true"
```

---

### GET /annotations/export/markdown

Export annotations to Markdown format for use in external note-taking applications.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `resource_id` | string | Filter by resource UUID (optional) | - |

**Response (200 OK):**
```markdown
Content-Type: text/markdown

# Annotations Export

## Deep Learning Fundamentals

### Annotation 1
**Highlighted Text:**
> This is the key finding of the paper

**Note:** Important result - contradicts previous assumptions

**Tags:** key-finding, methodology

**Created:** 2024-01-01 10:00:00

---

## Neural Network Architectures

### Annotation 2
**Highlighted Text:**
> Convolutional layers extract spatial features

**Note:** Core concept for image processing

**Tags:** architecture, cnn

**Created:** 2024-01-01 11:00:00

---
```

**Authentication:** Required

**Behavior:**
- Groups annotations by resource
- Formats each annotation with highlighted text, note, tags, timestamp
- Exports all user annotations if no resource_id specified
- Target: <2s for 1,000 annotations

**Example:**
```bash
# Export all annotations
curl "http://127.0.0.1:8000/annotations/export/markdown" > annotations.md

# Export annotations for specific resource
curl "http://127.0.0.1:8000/annotations/export/markdown?resource_id=660e8400-e29b-41d4-a716-446655440001" > resource_annotations.md
```

---

### GET /annotations/export/json

Export annotations to JSON format with complete metadata.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `resource_id` | string | Filter by resource UUID (optional) | - |

**Response (200 OK):**
```json
{
  "annotations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "resource_id": "660e8400-e29b-41d4-a716-446655440001",
      "resource_title": "Deep Learning Fundamentals",
      "start_offset": 150,
      "end_offset": 200,
      "highlighted_text": "This is the key finding",
      "note": "Important result",
      "tags": ["key-finding", "methodology"],
      "color": "#FFD700",
      "is_shared": false,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "exported_at": "2024-01-01T12:00:00Z"
}
```

**Authentication:** Required

**Behavior:**
- Includes complete annotation metadata
- Includes resource title for context
- Exports all user annotations if no resource_id specified

**Example:**
```bash
# Export all annotations to JSON
curl "http://127.0.0.1:8000/annotations/export/json" > annotations.json

# Export annotations for specific resource
curl "http://127.0.0.1:8000/annotations/export/json?resource_id=660e8400-e29b-41d4-a716-446655440001" > resource_annotations.json
```

---

## Annotation Data Models

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
  "tags": ["string"] (max 20 tags, max 50 chars each),
  "color": "string (hex color, default: #FFFF00)",
  "embedding": [float] or null (384-dimensional vector),
  "context_before": "string or null (50 characters)",
  "context_after": "string or null (50 characters)",
  "is_shared": "boolean (default: false)",
  "collection_ids": ["uuid"] or null,
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

**Field Descriptions:**
- `id`: Unique annotation identifier
- `resource_id`: Resource being annotated
- `user_id`: User who created the annotation
- `start_offset`: Zero-indexed character position where highlight starts
- `end_offset`: Zero-indexed character position where highlight ends
- `highlighted_text`: The actual text that was highlighted
- `note`: User's commentary or observation (optional)
- `tags`: User-defined labels for categorization
- `color`: Hex color code for visual organization
- `embedding`: Semantic vector for note content (generated async)
- `context_before`: 50 characters before highlight for preview
- `context_after`: 50 characters after highlight for preview
- `is_shared`: Whether annotation is visible to other users
- `collection_ids`: Associated research collections

### Annotation List Response Model

```json
{
  "items": [
    {
      "id": "uuid",
      "resource_id": "uuid",
      "resource_title": "string (optional)",
      "user_id": "string",
      "start_offset": "integer",
      "end_offset": "integer",
      "highlighted_text": "string",
      "note": "string or null",
      "tags": ["string"],
      "color": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": "integer",
  "limit": "integer (optional)",
  "offset": "integer (optional)"
}
```

### Semantic Search Response Model

```json
{
  "items": [
    {
      "id": "uuid",
      "resource_id": "uuid",
      "resource_title": "string",
      "highlighted_text": "string",
      "note": "string or null",
      "tags": ["string"],
      "similarity": "float (0.0-1.0)",
      "created_at": "datetime"
    }
  ],
  "total": "integer"
}
```

---

## Annotation Features

### Text Offset Tracking

Annotations use character offsets for precise text positioning:

**Offset Calculation:**
- Zero-indexed character positions in resource content
- `start_offset`: First character of highlight (inclusive)
- `end_offset`: Last character of highlight (exclusive)
- Example: "Hello World"[0:5] = "Hello"

**Validation Rules:**
- `start_offset >= 0`
- `end_offset > start_offset`
- `end_offset <= content_length`
- Zero-length highlights rejected

**Advantages:**
- Works with any text format (HTML, PDF, plain text)
- More reliable than DOM-based selection
- Survives content reformatting
- Simple to implement and understand

### Context Extraction

Annotations automatically capture surrounding text:

**Algorithm:**
1. Extract 50 characters before start_offset
2. Extract 50 characters after end_offset
3. Handle document boundaries gracefully
4. Store in context_before and context_after fields

**Use Cases:**
- Preview annotations in list views
- Understand highlight context without full document
- Quick reference in search results

**Performance:** <10ms per annotation

### Semantic Embedding Generation

Annotations with notes get automatic semantic embeddings:

**Process:**
1. User creates annotation with note
2. Annotation saved immediately (fast path)
3. Embedding generation queued (background)
4. Embedding computed using sentence-transformers
5. Annotation updated with embedding vector

**Model:** nomic-ai/nomic-embed-text-v1 (384 dimensions)

**Performance:**
- Annotation creation: <50ms (excluding embedding)
- Embedding generation: <500ms (async)
- Semantic search: <500ms for 1,000 annotations

### Privacy and Sharing

Annotations are private by default:

**Privacy Model:**
- `is_shared=false`: Only owner can view (default)
- `is_shared=true`: Visible to all users with resource access

**Access Control:**
- Create: Authenticated users only
- Read: Owner OR (shared AND has resource access)
- Update: Owner only
- Delete: Owner only
- Search: User's own annotations only

### Collection Integration

Annotations can be associated with collections:

**Association:**
- Store collection UUIDs in `collection_ids` JSON array
- Multiple collections per annotation supported
- Optional field (can be null or empty)

**Use Cases:**
- Organize annotations by research project
- Filter annotations by collection context
- Export collection-specific annotations

### Export Capabilities

Annotations support multiple export formats:

**Markdown Export:**
- Human-readable format
- Grouped by resource
- Includes all metadata
- Compatible with note-taking apps (Obsidian, Notion, etc.)

**JSON Export:**
- Machine-readable format
- Complete metadata preservation
- Suitable for backup and migration
- Easy to parse programmatically

**Performance:**
- Target: <2s for 1,000 annotations
- Efficient batch queries
- Single database transaction

---

## Citation Data Models

### Citation Model

```json
{
  "id": "uuid",
  "source_resource_id": "uuid",
  "target_resource_id": "uuid or null",
  "target_url": "string",
  "citation_type": "reference|dataset|code|general",
  "context_snippet": "string or null",
  "position": "integer or null",
  "importance_score": "float or null (0.0-1.0)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Field Descriptions:**
- `id`: Unique citation identifier
- `source_resource_id`: Resource that contains the citation
- `target_resource_id`: Cited resource if it exists in the database (null if external)
- `target_url`: URL being cited
- `citation_type`: Classification of citation:
  - `reference`: Academic papers, articles, documentation
  - `dataset`: Data files (.csv, .json, .xml, etc.)
  - `code`: Code repositories (GitHub, GitLab, etc.)
  - `general`: Other web links
- `context_snippet`: Text surrounding the citation (up to 100 characters)
- `position`: Position in the document (for ordering)
- `importance_score`: PageRank-based importance (computed periodically)

### Citation Graph Response Model

```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "string",
      "type": "source|cited|citing"
    }
  ],
  "edges": [
    {
      "source": "uuid",
      "target": "uuid",
      "type": "reference|dataset|code|general"
    }
  ]
}
```

**Node Types:**
- `source`: The focal resource being explored
- `cited`: Resources cited by the focal resource
- `citing`: Resources that cite the focal resource

---

## Citation Extraction Details

### Supported Content Types

#### HTML
- Extracts `<a href="...">` links
- Extracts `<cite>` tags
- Captures link text and surrounding context
- Filters out internal anchors and JavaScript links

#### PDF
- Uses pdfplumber to extract hyperlinks
- Extracts URLs from text using regex
- Captures page numbers for position tracking
- Handles both embedded links and plain text URLs

#### Markdown
- Parses `[text](url)` syntax
- Extracts link text and URLs
- Captures surrounding context
- Filters out internal anchors

### Citation Type Classification

The system uses heuristics to automatically classify citations:

**Dataset Indicators:**
- File extensions: `.csv`, `.json`, `.xml`, `.xlsx`, `.tsv`
- Example: `https://example.com/data.csv` → `dataset`

**Code Repository Indicators:**
- Domains: `github.com`, `gitlab.com`, `bitbucket.org`
- Example: `https://github.com/user/repo` → `code`

**Academic Reference Indicators:**
- Domains: `doi.org`, `arxiv.org`, `scholar.google`, `pubmed`
- Example: `https://doi.org/10.1234/example` → `reference`

**General:**
- All other URLs default to `general`

### Performance Characteristics

**Citation Extraction:**
- HTML: <500ms per resource
- PDF: <2s per resource (depends on size)
- Markdown: <200ms per resource
- Limit: 50 citations per resource (for performance)

**Citation Resolution:**
- Batch size: 100 citations
- Processing time: <100ms per batch
- Uses bulk database operations

**PageRank Computation:**
- Small graphs (<100 nodes): <1s
- Medium graphs (100-1000 nodes): <5s
- Large graphs (1000+ nodes): <30s
- Uses sparse matrix representation

---

## Integration Examples

### Automatic Citation Extraction During Ingestion

Citations are automatically extracted when a resource completes ingestion:

```python
# In resource_service.py process_ingestion()
# After successful ingestion:
if resource.format in ["text/html", "application/pdf", "text/markdown"]:
    background_tasks.add_task(citation_service.extract_citations, resource_id)
```

### Periodic Citation Resolution

Run citation resolution periodically to link new resources:

```bash
# Cron job (daily at 2 AM)
0 2 * * * curl -X POST http://127.0.0.1:8000/citations/resolve
```

### Periodic Importance Score Updates

Recompute PageRank scores periodically:

```bash
# Cron job (weekly on Sunday at 3 AM)
0 3 * * 0 curl -X POST http://127.0.0.1:8000/citations/importance/compute
```

### Citation Network Visualization

Build a citation network visualization:

```javascript
// Fetch citation graph
const response = await fetch(
  `/citations/graph/citations?resource_ids=${resourceId}&depth=2`
);
const graph = await response.json();

// Render with D3.js or similar
renderGraph(graph.nodes, graph.edges);
```

---
