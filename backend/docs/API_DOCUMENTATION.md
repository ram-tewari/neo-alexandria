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
