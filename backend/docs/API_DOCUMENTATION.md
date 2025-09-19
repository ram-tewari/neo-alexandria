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

## Changelog

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