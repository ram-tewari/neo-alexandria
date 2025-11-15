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

### Phase 8: Three-Way Hybrid Search Endpoints

#### GET /search/three-way-hybrid

Execute three-way hybrid search combining FTS5, dense vectors, and sparse vectors with RRF fusion and optional ColBERT reranking.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query text (required) | - |
| `limit` | integer | Number of results (1-100) | 20 |
| `offset` | integer | Number of results to skip | 0 |
| `enable_reranking` | boolean | Apply ColBERT reranking | true |
| `adaptive_weighting` | boolean | Use query-adaptive RRF weights | true |

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "description": "Comprehensive guide to ML concepts",
      "subject": ["Machine Learning", "Artificial Intelligence"],
      "quality_score": 0.85,
      "relevance_score": 0.92,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 42,
  "latency_ms": 145.3,
  "method_contributions": {
    "fts5": 45,
    "dense": 38,
    "sparse": 42
  },
  "weights_used": [0.35, 0.35, 0.30],
  "facets": {
    "classification_code": [{"key": "004", "count": 30}],
    "type": [{"key": "article", "count": 35}],
    "language": [{"key": "en", "count": 33}]
  }
}
```

**Example:**
```bash
# Three-way search with reranking and adaptive weighting
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=machine+learning&limit=20&enable_reranking=true&adaptive_weighting=true"

# Fast three-way search without reranking
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=neural+networks&limit=10&enable_reranking=false"

# Three-way search with fixed weights (no adaptation)
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=data+science&adaptive_weighting=false"
```

**Performance:**
- Target latency: <200ms at 95th percentile
- With reranking: <1 second for 100 candidates
- Parallel retrieval for optimal speed

---

#### GET /search/compare-methods

Compare different search methods side-by-side for debugging and optimization.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query text (required) | - |
| `limit` | integer | Number of results per method (1-50) | 20 |

**Response (200 OK):**
```json
{
  "query": "machine learning",
  "methods": {
    "fts5_only": {
      "results": [...],
      "latency_ms": 25.3,
      "count": 20
    },
    "dense_only": {
      "results": [...],
      "latency_ms": 42.1,
      "count": 20
    },
    "sparse_only": {
      "results": [...],
      "latency_ms": 38.7,
      "count": 20
    },
    "two_way_hybrid": {
      "results": [...],
      "latency_ms": 67.4,
      "count": 20
    },
    "three_way_hybrid": {
      "results": [...],
      "latency_ms": 106.1,
      "count": 20
    },
    "three_way_reranked": {
      "results": [...],
      "latency_ms": 856.8,
      "count": 20
    }
  }
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/search/compare-methods?query=artificial+intelligence&limit=10"
```

**Use Cases:**
- Debug search quality issues
- Compare method effectiveness for different query types
- Analyze latency trade-offs
- Validate search improvements

---

#### POST /search/evaluate

Evaluate search quality using information retrieval metrics (nDCG, Recall, Precision, MRR).

**Request Body:**
```json
{
  "query": "machine learning",
  "relevance_judgments": {
    "resource_id_1": 3,
    "resource_id_2": 2,
    "resource_id_3": 1,
    "resource_id_4": 0
  }
}
```

**Relevance Scale:**
- `3` - Highly relevant
- `2` - Relevant
- `1` - Marginally relevant
- `0` - Not relevant

**Response (200 OK):**
```json
{
  "query": "machine learning",
  "metrics": {
    "ndcg@20": 0.847,
    "recall@20": 0.923,
    "precision@20": 0.650,
    "mrr": 0.833
  },
  "baseline_comparison": {
    "two_way_ndcg": 0.651,
    "improvement": 0.301
  }
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/search/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deep learning",
    "relevance_judgments": {
      "550e8400-e29b-41d4-a716-446655440000": 3,
      "660e8400-e29b-41d4-a716-446655440001": 2,
      "770e8400-e29b-41d4-a716-446655440002": 1
    }
  }'
```

**Metrics Explained:**
- **nDCG@20**: Normalized Discounted Cumulative Gain at position 20 (0-1, higher is better)
- **Recall@20**: Fraction of relevant documents retrieved in top 20 (0-1, higher is better)
- **Precision@20**: Fraction of top 20 results that are relevant (0-1, higher is better)
- **MRR**: Mean Reciprocal Rank of first relevant result (0-1, higher is better)

---

#### POST /admin/sparse-embeddings/generate

Batch generate sparse embeddings for existing resources without them.

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2", ...],
  "batch_size": 32
}
```

**Parameters:**
- `resource_ids` (optional): Specific resources to process. If omitted, processes all resources without sparse embeddings.
- `batch_size` (optional): Batch size for processing (default: 32 for GPU, 8 for CPU)

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "job_id": "job_uuid",
  "estimated_duration_minutes": 45,
  "resources_to_process": 10000
}
```

**Example:**
```bash
# Generate for all resources without sparse embeddings
curl -X POST http://127.0.0.1:8000/admin/sparse-embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 32}'

# Generate for specific resources
curl -X POST http://127.0.0.1:8000/admin/sparse-embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "660e8400-e29b-41d4-a716-446655440001"
    ],
    "batch_size": 16
  }'
```

**Background Processing:**
- Processes resources in batches for efficiency
- Commits every 100 resources
- Logs progress updates
- Resumes from last committed batch if interrupted
- Target: <1 second per resource

---

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

### Taxonomy Management (Phase 8.5)

The taxonomy management endpoints provide full CRUD operations for hierarchical taxonomy trees with parent-child relationships, materialized paths for efficient queries, and resource classification support.

#### POST /taxonomy/nodes

Create a new taxonomy node in the hierarchical tree.

**Request Body:**
```json
{
  "name": "Machine Learning",
  "parent_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "ML and deep learning topics",
  "keywords": ["neural networks", "deep learning"],
  "allow_resources": true
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable category name |
| `parent_id` | string | No | UUID of parent node (null for root nodes) |
| `description` | string | No | Category description |
| `keywords` | array[string] | No | Related keywords for the category |
| `allow_resources` | boolean | No | Whether resources can be assigned (default: true) |

**Response (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Machine Learning",
  "slug": "machine-learning",
  "parent_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": 1,
  "path": "/computer-science/machine-learning",
  "description": "ML and deep learning topics",
  "keywords": ["neural networks", "deep learning"],
  "resource_count": 0,
  "descendant_resource_count": 0,
  "is_leaf": true,
  "allow_resources": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/taxonomy/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning",
    "description": "ML and deep learning topics",
    "keywords": ["neural networks", "deep learning"]
  }'
```

#### PUT /taxonomy/nodes/{node_id}

Update taxonomy node metadata (name, description, keywords, allow_resources).

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_id` | string | Taxonomy node UUID |

**Request Body:**
```json
{
  "name": "Deep Learning",
  "description": "Neural networks with multiple layers",
  "keywords": ["CNN", "RNN", "transformers"],
  "allow_resources": true
}
```

**Note:** To change the parent, use the move endpoint instead.

**Response (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Deep Learning",
  "slug": "deep-learning",
  "parent_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": 1,
  "path": "/computer-science/deep-learning",
  "description": "Neural networks with multiple layers",
  "keywords": ["CNN", "RNN", "transformers"],
  "resource_count": 5,
  "descendant_resource_count": 12,
  "is_leaf": false,
  "allow_resources": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:8000/taxonomy/nodes/{node_id} \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "keywords": ["new", "keywords"]
  }'
```

#### DELETE /taxonomy/nodes/{node_id}

Delete a taxonomy node with optional cascade deletion of descendants.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_id` | string | Taxonomy node UUID |

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `cascade` | boolean | Delete descendants vs reparent children | false |

**Response (200 OK):**
```json
{
  "deleted": true,
  "message": "Taxonomy node deleted successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Cannot delete taxonomy node with 15 assigned resources"
}
```

**Behavior:**
- If `cascade=false`: Child nodes are reparented to the deleted node's parent
- If `cascade=true`: All descendant nodes are deleted recursively
- Deletion fails if the node has assigned resources (must be removed first)

**Example:**
```bash
# Delete node and reparent children
curl -X DELETE "http://127.0.0.1:8000/taxonomy/nodes/{node_id}"

# Delete node and all descendants
curl -X DELETE "http://127.0.0.1:8000/taxonomy/nodes/{node_id}?cascade=true"
```

#### POST /taxonomy/nodes/{node_id}/move

Move a taxonomy node to a different parent (reparenting).

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_id` | string | Taxonomy node UUID to move |

**Request Body:**
```json
{
  "new_parent_id": "770e8400-e29b-41d4-a716-446655440002"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `new_parent_id` | string | Yes | UUID of new parent (null for root) |

**Response (200 OK):**
```json
{
  "moved": true,
  "message": "Node moved successfully",
  "node": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Machine Learning",
    "parent_id": "770e8400-e29b-41d4-a716-446655440002",
    "level": 2,
    "path": "/science/computer-science/machine-learning"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Cannot move node to its own descendant (circular reference)"
}
```

**Validation:**
- Prevents circular references (moving to own descendant)
- Prevents self-parenting
- Automatically updates level and path for node and all descendants

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/taxonomy/nodes/{node_id}/move \
  -H "Content-Type: application/json" \
  -d '{"new_parent_id": "{new_parent_id}"}'
```

#### GET /taxonomy/tree

Retrieve the hierarchical taxonomy tree as nested JSON structure.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `root_id` | string | Starting node UUID (null for all roots) | null |
| `max_depth` | integer | Maximum tree depth to retrieve | null |

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Computer Science",
    "slug": "computer-science",
    "parent_id": null,
    "level": 0,
    "path": "/computer-science",
    "description": "Computing and software topics",
    "keywords": ["programming", "algorithms"],
    "resource_count": 10,
    "descendant_resource_count": 45,
    "is_leaf": false,
    "allow_resources": true,
    "children": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Machine Learning",
        "slug": "machine-learning",
        "parent_id": "550e8400-e29b-41d4-a716-446655440000",
        "level": 1,
        "path": "/computer-science/machine-learning",
        "description": "ML and AI topics",
        "keywords": ["neural networks", "deep learning"],
        "resource_count": 15,
        "descendant_resource_count": 35,
        "is_leaf": false,
        "allow_resources": true,
        "children": [
          {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "name": "Deep Learning",
            "slug": "deep-learning",
            "parent_id": "660e8400-e29b-41d4-a716-446655440001",
            "level": 2,
            "path": "/computer-science/machine-learning/deep-learning",
            "description": "Neural networks with multiple layers",
            "keywords": ["CNN", "RNN", "transformers"],
            "resource_count": 20,
            "descendant_resource_count": 20,
            "is_leaf": true,
            "allow_resources": true,
            "children": []
          }
        ]
      }
    ]
  }
]
```

**Example:**
```bash
# Get full tree
curl "http://127.0.0.1:8000/taxonomy/tree"

# Get subtree from specific node
curl "http://127.0.0.1:8000/taxonomy/tree?root_id={node_id}"

# Get tree with depth limit
curl "http://127.0.0.1:8000/taxonomy/tree?max_depth=3"
```

#### GET /taxonomy/nodes/{node_id}/ancestors

Get all ancestor nodes for breadcrumb trail navigation.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_id` | string | Taxonomy node UUID |

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Computer Science",
    "slug": "computer-science",
    "level": 0,
    "path": "/computer-science"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Machine Learning",
    "slug": "machine-learning",
    "level": 1,
    "path": "/computer-science/machine-learning"
  },
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "name": "Deep Learning",
    "slug": "deep-learning",
    "level": 2,
    "path": "/computer-science/machine-learning/deep-learning"
  }
]
```

**Performance:** O(depth) using materialized path, typically <10ms

**Example:**
```bash
curl "http://127.0.0.1:8000/taxonomy/nodes/{node_id}/ancestors"
```

#### GET /taxonomy/nodes/{node_id}/descendants

Get all descendant nodes at any depth below the specified node.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `node_id` | string | Taxonomy node UUID |

**Response (200 OK):**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "name": "Deep Learning",
    "slug": "deep-learning",
    "parent_id": "660e8400-e29b-41d4-a716-446655440001",
    "level": 2,
    "path": "/computer-science/machine-learning/deep-learning",
    "resource_count": 20,
    "descendant_resource_count": 20
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "name": "Natural Language Processing",
    "slug": "natural-language-processing",
    "parent_id": "660e8400-e29b-41d4-a716-446655440001",
    "level": 2,
    "path": "/computer-science/machine-learning/nlp",
    "resource_count": 15,
    "descendant_resource_count": 15
  }
]
```

**Performance:** O(1) query using path pattern matching, typically <10ms

**Example:**
```bash
curl "http://127.0.0.1:8000/taxonomy/nodes/{node_id}/descendants"
```

### ML Classification (Phase 8.5)

The ML classification endpoints provide transformer-based resource classification with confidence scores, active learning for continuous improvement, and model training capabilities.

#### POST /taxonomy/classify/{resource_id}

Classify a resource using the fine-tuned ML model.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `resource_id` | string | Resource UUID to classify |

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Classification task enqueued",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Background Processing:**
1. Load ML model (lazy loading on first request)
2. Extract resource content (title + description + full text)
3. Predict taxonomy categories with confidence scores
4. Filter predictions (confidence >= 0.3)
5. Store classifications in database
6. Flag low-confidence predictions (< 0.7) for review
7. Update taxonomy node resource counts

**Classification Results:**
After processing, classifications are stored with:
- Taxonomy node IDs
- Confidence scores (0.0-1.0)
- Model version identifier
- `is_predicted=true` flag
- `needs_review=true` if confidence < 0.7

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/taxonomy/classify/{resource_id}"
```

#### GET /taxonomy/active-learning/uncertain

Get resources with uncertain classifications for human review (active learning).

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of samples to return (1-1000) | 100 |

**Response (200 OK):**
```json
[
  {
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Introduction to Neural Networks",
    "uncertainty_score": 0.87,
    "predicted_categories": [
      {
        "taxonomy_node_id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Machine Learning",
        "confidence": 0.65
      },
      {
        "taxonomy_node_id": "770e8400-e29b-41d4-a716-446655440002",
        "name": "Deep Learning",
        "confidence": 0.62
      }
    ]
  },
  {
    "resource_id": "660e8400-e29b-41d4-a716-446655440005",
    "title": "Data Structures and Algorithms",
    "uncertainty_score": 0.82,
    "predicted_categories": [
      {
        "taxonomy_node_id": "880e8400-e29b-41d4-a716-446655440003",
        "name": "Algorithms",
        "confidence": 0.58
      }
    ]
  }
]
```

**Uncertainty Metrics:**
The system computes uncertainty using three metrics:
- **Entropy**: Measures prediction uncertainty across all classes
- **Margin**: Difference between top-2 predictions (small = uncertain)
- **Confidence**: Maximum probability (low = uncertain)

Combined score: `entropy * (1 - margin) * (1 - max_confidence)`

**Use Case:** Present these resources to human reviewers for labeling to improve model accuracy with minimal effort.

**Example:**
```bash
curl "http://127.0.0.1:8000/taxonomy/active-learning/uncertain?limit=50"
```

#### POST /taxonomy/active-learning/feedback

Submit human classification feedback to improve the model.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "correct_taxonomy_ids": [
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resource_id` | string | Yes | Resource UUID |
| `correct_taxonomy_ids` | array[string] | Yes | Correct taxonomy node UUIDs |

**Response (200 OK):**
```json
{
  "updated": true,
  "message": "Feedback recorded successfully",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "manual_labels_count": 87,
  "retraining_threshold": 100,
  "retraining_recommended": false
}
```

**Behavior:**
1. Remove existing predicted classifications for the resource
2. Add human-labeled classifications with `confidence=1.0` and `is_predicted=false`
3. Check if retraining threshold reached (100 new manual labels)
4. Return recommendation to retrain model if threshold met

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/taxonomy/active-learning/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "{resource_id}",
    "correct_taxonomy_ids": ["{node_id_1}", "{node_id_2}"]
  }'
```

#### POST /taxonomy/train

Initiate ML model fine-tuning with labeled and unlabeled data.

**Request Body:**
```json
{
  "labeled_data": [
    {
      "text": "Introduction to neural networks and backpropagation algorithms",
      "taxonomy_ids": [
        "660e8400-e29b-41d4-a716-446655440001",
        "770e8400-e29b-41d4-a716-446655440002"
      ]
    },
    {
      "text": "Database normalization and SQL query optimization",
      "taxonomy_ids": [
        "880e8400-e29b-41d4-a716-446655440003"
      ]
    }
  ],
  "unlabeled_texts": [
    "Article about convolutional neural networks for image recognition",
    "Tutorial on recurrent neural networks and LSTM architectures"
  ],
  "epochs": 3,
  "batch_size": 16,
  "learning_rate": 2e-5
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `labeled_data` | array[object] | Yes | Training examples with text and taxonomy IDs |
| `unlabeled_texts` | array[string] | No | Unlabeled texts for semi-supervised learning |
| `epochs` | integer | No | Training epochs (default: 3) |
| `batch_size` | integer | No | Batch size (default: 16) |
| `learning_rate` | float | No | Learning rate (default: 2e-5) |

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Training task enqueued",
  "training_id": "990e8400-e29b-41d4-a716-446655440004",
  "labeled_examples": 150,
  "unlabeled_examples": 5000,
  "estimated_duration_minutes": 15
}
```

**Background Processing:**
1. Build label mapping from unique taxonomy IDs
2. Convert multi-label to multi-hot encoding
3. Split train/validation (80/20)
4. Tokenize texts (max_length=512)
5. Fine-tune BERT/DistilBERT model
6. If unlabeled data provided, perform semi-supervised iteration:
   - Predict on unlabeled data
   - Filter high-confidence predictions (>= 0.9)
   - Add pseudo-labels to training set
   - Re-train for 1 epoch
7. Evaluate on validation set (F1, precision, recall)
8. Save model checkpoint with version identifier
9. Save label mapping as JSON

**Semi-Supervised Learning:**
When unlabeled data is provided, the system uses pseudo-labeling:
- High-confidence predictions (>= 0.9) on unlabeled data become training examples
- Enables effective training with <500 labeled examples
- Leverages large unlabeled corpus for improved generalization

**Model Versioning:**
- Models saved to `models/classification/{version}/`
- Version format: `v{major}.{minor}`
- Includes model weights, tokenizer, and label mapping

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/taxonomy/train \
  -H "Content-Type: application/json" \
  -d '{
    "labeled_data": [
      {
        "text": "Machine learning tutorial",
        "taxonomy_ids": ["{ml_node_id}"]
      }
    ],
    "epochs": 3,
    "batch_size": 16
  }'
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
- `GET /search/three-way-hybrid` - Three-way hybrid search with RRF and reranking
- `GET /search/compare-methods` - Compare different search methods side-by-side
- `POST /search/evaluate` - Evaluate search quality with IR metrics
- `POST /admin/sparse-embeddings/generate` - Batch generate sparse embeddings

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

## Phase 8: Three-Way Hybrid Search Endpoints


---

## Phase 9: Multi-Dimensional Quality Assessment Endpoints

Phase 9 introduces comprehensive quality assessment endpoints for evaluating resources across multiple dimensions, detecting quality outliers, monitoring quality degradation, and evaluating summary quality using state-of-the-art metrics.

### Quality Assessment Endpoints

#### GET /resources/{id}/quality-details

Retrieve full quality dimension breakdown for a resource.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Resource UUID |

**Response (200 OK):**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "quality_dimensions": {
    "accuracy": 0.75,
    "completeness": 0.82,
    "consistency": 0.88,
    "timeliness": 0.65,
    "relevance": 0.79
  },
  "quality_overall": 0.77,
  "quality_weights": {
    "accuracy": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.15,
    "relevance": 0.10
  },
  "quality_last_computed": "2025-11-10T12:00:00Z",
  "quality_computation_version": "v2.0",
  "is_quality_outlier": false,
  "outlier_score": null,
  "outlier_reasons": null,
  "needs_quality_review": false
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/resources/550e8400-e29b-41d4-a716-446655440000/quality-details
```

**Quality Dimensions Explained:**
- **Accuracy (0.0-1.0)**: Citation validity, source credibility, scholarly metadata presence
- **Completeness (0.0-1.0)**: Metadata coverage, content depth, multi-modal content
- **Consistency (0.0-1.0)**: Title-content alignment, internal coherence
- **Timeliness (0.0-1.0)**: Publication recency, content freshness
- **Relevance (0.0-1.0)**: Classification confidence, citation count

---

#### POST /quality/recalculate

Trigger quality recomputation for one or more resources with optional custom weights.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_ids": ["uuid1", "uuid2"],
  "weights": {
    "accuracy": 0.35,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.10,
    "relevance": 0.10
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resource_id` | string | No | Single resource UUID to recompute |
| `resource_ids` | array[string] | No | Multiple resource UUIDs to recompute |
| `weights` | object | No | Custom dimension weights (must sum to 1.0) |

**Note:** Must provide either `resource_id` or `resource_ids`, not both.

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "message": "Quality computation queued for background processing"
}
```

**Example:**
```bash
# Recalculate single resource with default weights
curl -X POST http://127.0.0.1:8000/quality/recalculate \
  -H "Content-Type: application/json" \
  -d '{"resource_id": "550e8400-e29b-41d4-a716-446655440000"}'

# Recalculate multiple resources with custom weights
curl -X POST http://127.0.0.1:8000/quality/recalculate \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["uuid1", "uuid2", "uuid3"],
    "weights": {
      "accuracy": 0.40,
      "completeness": 0.30,
      "consistency": 0.15,
      "timeliness": 0.10,
      "relevance": 0.05
    }
  }'
```

**Custom Weights Validation:**
- All five dimensions must be specified
- Weights must sum to 1.0 (±0.01 tolerance)
- Each weight must be between 0.0 and 1.0

---

#### GET /quality/outliers

Retrieve paginated list of detected quality outliers with filtering options.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number (1-indexed) | 1 |
| `limit` | integer | Results per page (1-100) | 50 |
| `min_outlier_score` | float | Minimum anomaly score (-1.0 to 1.0) | null |
| `reason` | string | Filter by specific outlier reason | null |

**Outlier Reasons:**
- `low_accuracy` - Accuracy dimension < 0.3
- `low_completeness` - Completeness dimension < 0.3
- `low_consistency` - Consistency dimension < 0.3
- `low_timeliness` - Timeliness dimension < 0.3
- `low_relevance` - Relevance dimension < 0.3
- `low_summary_coherence` - Summary coherence < 0.3
- `low_summary_consistency` - Summary consistency < 0.3
- `low_summary_fluency` - Summary fluency < 0.3
- `low_summary_relevance` - Summary relevance < 0.3

**Response (200 OK):**
```json
{
  "total": 42,
  "page": 1,
  "limit": 50,
  "outliers": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "quality_overall": 0.35,
      "outlier_score": -0.82,
      "outlier_reasons": ["low_accuracy", "low_completeness"],
      "needs_quality_review": true,
      "quality_last_computed": "2025-11-10T12:00:00Z"
    }
  ]
}
```

**Example:**
```bash
# Get all outliers
curl "http://127.0.0.1:8000/quality/outliers?limit=20"

# Filter by outlier reason
curl "http://127.0.0.1:8000/quality/outliers?reason=low_accuracy"

# Filter by minimum outlier score
curl "http://127.0.0.1:8000/quality/outliers?min_outlier_score=-0.5"
```

**Outlier Score Interpretation:**
- Lower scores indicate higher anomaly likelihood
- Scores < -0.5 are typically significant outliers
- Uses Isolation Forest algorithm with contamination=0.1

---

#### GET /quality/degradation

Monitor quality degradation over time by comparing historical scores.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `time_window_days` | integer | Lookback period in days | 30 |

**Response (200 OK):**
```json
{
  "time_window_days": 30,
  "degraded_count": 15,
  "degraded_resources": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "old_quality": 0.85,
      "new_quality": 0.62,
      "degradation_pct": 27.1,
      "quality_last_computed": "2025-10-15T12:00:00Z"
    }
  ]
}
```

**Example:**
```bash
# Monitor degradation over 30 days
curl "http://127.0.0.1:8000/quality/degradation?time_window_days=30"

# Monitor degradation over 90 days
curl "http://127.0.0.1:8000/quality/degradation?time_window_days=90"
```

**Degradation Detection:**
- Compares current quality to historical quality
- Flags resources with >20% quality drop
- Automatically sets `needs_quality_review` flag
- Common causes: broken links, outdated content, metadata corruption

---

#### POST /summaries/{id}/evaluate

Trigger summary quality evaluation for a resource using G-Eval, FineSurE, and BERTScore metrics.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Resource UUID |

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `use_g_eval` | boolean | Use GPT-4 for G-Eval metrics | false |

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "message": "Summary evaluation queued for background processing"
}
```

**Example:**
```bash
# Evaluate without G-Eval (fast, no API cost)
curl -X POST "http://127.0.0.1:8000/summaries/550e8400-e29b-41d4-a716-446655440000/evaluate?use_g_eval=false"

# Evaluate with G-Eval (slower, requires OpenAI API key)
curl -X POST "http://127.0.0.1:8000/summaries/550e8400-e29b-41d4-a716-446655440000/evaluate?use_g_eval=true"
```

**Evaluation Metrics:**
- **G-Eval (optional)**: Coherence, consistency, fluency, relevance (1-5 scale, normalized to 0.0-1.0)
- **FineSurE**: Completeness and conciseness (0.0-1.0)
- **BERTScore**: Semantic similarity F1 score (0.0-1.0)
- **Composite Score**: Weighted average of all metrics

**Performance:**
- Without G-Eval: <2 seconds per resource
- With G-Eval: <10 seconds per resource (OpenAI API latency)

---

#### GET /quality/distribution

Retrieve quality score distribution histogram with statistics.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `bins` | integer | Number of histogram bins (1-50) | 10 |
| `dimension` | string | Dimension or "overall" | overall |

**Dimension Options:**
- `overall` - Overall quality score
- `accuracy` - Accuracy dimension
- `completeness` - Completeness dimension
- `consistency` - Consistency dimension
- `timeliness` - Timeliness dimension
- `relevance` - Relevance dimension

**Response (200 OK):**
```json
{
  "dimension": "overall",
  "bins": 10,
  "distribution": [
    {"range": "0.0-0.1", "count": 5},
    {"range": "0.1-0.2", "count": 12},
    {"range": "0.2-0.3", "count": 28},
    {"range": "0.3-0.4", "count": 45},
    {"range": "0.4-0.5", "count": 67},
    {"range": "0.5-0.6", "count": 89},
    {"range": "0.6-0.7", "count": 102},
    {"range": "0.7-0.8", "count": 78},
    {"range": "0.8-0.9", "count": 45},
    {"range": "0.9-1.0", "count": 23}
  ],
  "statistics": {
    "mean": 0.65,
    "median": 0.68,
    "std_dev": 0.18,
    "min": 0.12,
    "max": 0.98,
    "total_resources": 494
  }
}
```

**Example:**
```bash
# Get overall quality distribution
curl "http://127.0.0.1:8000/quality/distribution?bins=10&dimension=overall"

# Get accuracy dimension distribution
curl "http://127.0.0.1:8000/quality/distribution?bins=20&dimension=accuracy"
```

---

#### GET /quality/trends

Retrieve quality trends over time with configurable granularity.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `granularity` | string | Time period: daily, weekly, monthly | weekly |
| `start_date` | date | Start of time range (ISO 8601) | 90 days ago |
| `end_date` | date | End of time range (ISO 8601) | today |
| `dimension` | string | Dimension or "overall" | overall |

**Response (200 OK):**
```json
{
  "dimension": "overall",
  "granularity": "weekly",
  "start_date": "2025-08-01",
  "end_date": "2025-11-14",
  "data_points": [
    {
      "period": "2025-W31",
      "avg_quality": 0.72,
      "resource_count": 145,
      "date": "2025-08-03"
    },
    {
      "period": "2025-W32",
      "avg_quality": 0.74,
      "resource_count": 167,
      "date": "2025-08-10"
    },
    {
      "period": "2025-W33",
      "avg_quality": 0.71,
      "resource_count": 189,
      "date": "2025-08-17"
    }
  ]
}
```

**Example:**
```bash
# Get weekly quality trends
curl "http://127.0.0.1:8000/quality/trends?granularity=weekly&dimension=overall"

# Get daily accuracy trends for last 30 days
curl "http://127.0.0.1:8000/quality/trends?granularity=daily&dimension=accuracy&start_date=2025-10-15&end_date=2025-11-14"

# Get monthly completeness trends
curl "http://127.0.0.1:8000/quality/trends?granularity=monthly&dimension=completeness"
```

---

#### GET /quality/dimensions

Retrieve average scores per dimension across all resources.

**Response (200 OK):**
```json
{
  "dimensions": {
    "accuracy": {
      "avg": 0.75,
      "min": 0.12,
      "max": 0.98,
      "std_dev": 0.15
    },
    "completeness": {
      "avg": 0.68,
      "min": 0.25,
      "max": 0.95,
      "std_dev": 0.18
    },
    "consistency": {
      "avg": 0.82,
      "min": 0.45,
      "max": 0.99,
      "std_dev": 0.12
    },
    "timeliness": {
      "avg": 0.58,
      "min": 0.10,
      "max": 0.95,
      "std_dev": 0.22
    },
    "relevance": {
      "avg": 0.71,
      "min": 0.30,
      "max": 0.92,
      "std_dev": 0.14
    }
  },
  "overall": {
    "avg": 0.71,
    "min": 0.28,
    "max": 0.96,
    "std_dev": 0.16
  },
  "total_resources": 1247,
  "resources_with_quality": 1247
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/quality/dimensions"
```

**Use Cases:**
- Dashboard overview of quality metrics
- Identify dimensions needing improvement
- Compare quality across different resource types
- Monitor quality trends over time

---

#### GET /quality/review-queue

Retrieve resources flagged for quality review with priority ranking.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number (1-indexed) | 1 |
| `limit` | integer | Results per page (1-100) | 50 |
| `sort_by` | string | Sort field | outlier_score |

**Sort Options:**
- `outlier_score` - Most anomalous first (lowest scores)
- `quality_overall` - Lowest quality first
- `updated_at` - Most recently updated first

**Response (200 OK):**
```json
{
  "total": 87,
  "page": 1,
  "limit": 50,
  "review_queue": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "quality_overall": 0.35,
      "is_quality_outlier": true,
      "outlier_score": -0.82,
      "outlier_reasons": ["low_accuracy", "low_completeness"],
      "quality_last_computed": "2025-11-10T12:00:00Z",
      "updated_at": "2025-11-10T12:00:00Z"
    }
  ]
}
```

**Example:**
```bash
# Get review queue sorted by outlier score
curl "http://127.0.0.1:8000/quality/review-queue?limit=20&sort_by=outlier_score"

# Get review queue sorted by quality
curl "http://127.0.0.1:8000/quality/review-queue?sort_by=quality_overall"

# Get recently flagged resources
curl "http://127.0.0.1:8000/quality/review-queue?sort_by=updated_at"
```

**Review Queue Population:**
- Automatically populated by outlier detection
- Populated by quality degradation monitoring
- Can be manually flagged via resource updates
- Cleared when resource quality improves

---

### Quality Assessment Integration

#### Automatic Quality Computation

Quality is automatically computed during resource ingestion:

```python
# In resource_service.py process_ingestion()
# After successful ingestion:
background_tasks.add_task(quality_service.compute_quality, resource_id)
```

#### Quality-Filtered Recommendations

Recommendations automatically filter by quality:

```python
# Exclude low-quality resources
recommendations = recommendation_service.generate_recommendations(
    user_id=user_id,
    min_quality=0.5,  # Filter out quality < 0.5
    exclude_outliers=True  # Exclude quality outliers
)
```

#### Scheduled Quality Monitoring

Set up scheduled tasks for quality monitoring:

```bash
# Daily outlier detection (cron job at 2 AM)
0 2 * * * curl -X POST http://127.0.0.1:8000/admin/quality/detect-outliers

# Weekly degradation monitoring (cron job Sunday at 3 AM)
0 3 * * 0 curl -X GET http://127.0.0.1:8000/quality/degradation?time_window_days=7
```

---

### Quality Metrics Reference

#### Quality Dimension Algorithms

**Accuracy Computation:**
```
accuracy = 0.5 (baseline)
  + 0.20 * (valid_citations / total_citations)
  + 0.15 * (1 if credible_domain else 0)
  + 0.15 * (1 if has_academic_identifier else 0)
  + 0.10 * (1 if has_authors else 0)
```

**Completeness Computation:**
```
completeness = 0.0
  + 0.30 * (filled_required_fields / 3)
  + 0.30 * (filled_important_fields / 4)
  + 0.20 * (filled_scholarly_fields / 4)
  + 0.20 * (multimodal_content_score / 3)
```

**Consistency Computation:**
```
consistency = 0.7 (baseline)
  + 0.15 * title_content_overlap
  + 0.15 * (1 if good_compression_ratio else 0)
```

**Timeliness Computation:**
```
age_years = current_year - publication_year
recency_score = max(0.0, 1.0 - (age_years / 20))
timeliness = recency_score + (0.1 if ingested_within_30_days else 0)
```

**Relevance Computation:**
```
relevance = 0.5 (baseline)
  + 0.20 * avg_classification_confidence
  + 0.30 * min(0.3, log10(citation_count + 1) / 10)
```

#### Summary Quality Metrics

**G-Eval Metrics (1-5 scale, normalized to 0.0-1.0):**
- **Coherence**: Logical flow and structure
- **Consistency**: Factual alignment with source
- **Fluency**: Grammatical correctness
- **Relevance**: Key information capture

**FineSurE Metrics (0.0-1.0):**
- **Completeness**: Coverage of key information (expect 15% overlap)
- **Conciseness**: Information density (optimal 5-15% compression)

**BERTScore (0.0-1.0):**
- **F1 Score**: Token-level semantic similarity using BERT embeddings

**Composite Summary Quality:**
```
summary_quality_overall = 
  0.20 * coherence +
  0.20 * consistency +
  0.15 * fluency +
  0.15 * relevance +
  0.15 * completeness +
  0.05 * conciseness +
  0.10 * bertscore
```

---

### Performance Characteristics

**Quality Computation:**
- Single resource: <1 second (excluding G-Eval)
- Batch (100 resources): <100 seconds
- Target throughput: 100 resources/minute

**Summarization Evaluation:**
- Without G-Eval: <2 seconds per resource
- With G-Eval: <10 seconds per resource (OpenAI API latency)
- BERTScore: <3 seconds per resource

**Outlier Detection:**
- 1000 resources: <30 seconds
- Feature matrix construction: <5 seconds
- Isolation Forest training: <10 seconds
- Prediction: <5 seconds

**API Response Times:**
- GET /quality/details: <100ms
- GET /quality/outliers: <200ms (paginated)
- GET /quality/distribution: <500ms (aggregation)
- GET /quality/trends: <1 second (time-series aggregation)

---

### Error Handling

**Missing Resource:**
```json
{
  "detail": "Resource not found",
  "status_code": 404
}
```

**Invalid Weights:**
```json
{
  "detail": "Weights must sum to 1.0",
  "status_code": 422
}
```

**No Summary for Evaluation:**
```json
{
  "detail": "Resource has no summary to evaluate",
  "status_code": 400
}
```

**OpenAI API Error:**
- Falls back to neutral scores (0.7) for G-Eval metrics
- Logs error for monitoring
- Does not fail the entire evaluation

**BERTScore Error:**
- Falls back to neutral score (0.5)
- Logs error for monitoring
- Does not fail the entire evaluation

---

## Phase 11: Hybrid Recommendation Engine

The Phase 11 Hybrid Recommendation Engine provides personalized, intelligent recommendations by combining Neural Collaborative Filtering (NCF), content-based similarity, and graph-based discovery. The system learns from user interactions, optimizes for diversity and novelty, and adapts to individual preferences.

### Key Features

- **Multi-Strategy Recommendations**: Combines collaborative filtering, content similarity, and graph relationships
- **User Profile Learning**: Automatically learns preferences from interaction history
- **Diversity Optimization**: Uses Maximal Marginal Relevance (MMR) to prevent filter bubbles
- **Novelty Promotion**: Surfaces lesser-known but relevant resources
- **Cold Start Handling**: Provides relevant recommendations for new users
- **Performance**: <200ms latency for 20 recommendations

---

### GET /api/recommendations

Get personalized recommendations for the authenticated user using hybrid strategy.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recommendations (1-100) | 20 |
| `strategy` | string | Recommendation strategy | hybrid |
| `diversity` | float | Diversity preference override (0.0-1.0) | user profile |
| `min_quality` | float | Minimum quality threshold (0.0-1.0) | 0.0 |

**Strategy Options:**
- `collaborative` - Neural Collaborative Filtering only (requires ≥5 interactions)
- `content` - Content-based similarity only
- `graph` - Graph-based relationships only
- `hybrid` - Combines all strategies with weighted scoring (default)

**Response (200 OK):**
```json
{
  "recommendations": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Advanced Machine Learning Techniques",
      "description": "Comprehensive guide to modern ML algorithms",
      "score": 0.87,
      "strategy": "hybrid",
      "scores": {
        "collaborative": 0.92,
        "content": 0.85,
        "graph": 0.78,
        "quality": 0.88,
        "recency": 0.65
      },
      "rank": 1,
      "novelty_score": 0.42,
      "source": "https://example.com/ml-guide",
      "classification_code": "004",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "metadata": {
    "total": 20,
    "strategy": "hybrid",
    "diversity_applied": true,
    "gini_coefficient": 0.24,
    "user_interactions": 47,
    "cold_start": false
  }
}
```

**Hybrid Scoring Formula:**
```
hybrid_score = 
  0.35 * collaborative_score +
  0.30 * content_score +
  0.20 * graph_score +
  0.10 * quality_score +
  0.05 * recency_score
```

**Example:**
```bash
# Get 20 hybrid recommendations
curl "http://127.0.0.1:8000/api/recommendations?limit=20"

# Get collaborative filtering recommendations only
curl "http://127.0.0.1:8000/api/recommendations?strategy=collaborative&limit=10"

# Get diverse recommendations with high quality threshold
curl "http://127.0.0.1:8000/api/recommendations?diversity=0.8&min_quality=0.7"
```

**Performance:**
- Target latency: <200ms for 20 recommendations
- Candidate generation: <100ms
- Ranking and diversification: <100ms
- Cache hit rate: >80% for user embeddings

**Cold Start Behavior:**
- Users with <5 interactions: Uses content + graph strategies only
- Collaborative filtering enabled after 5+ interactions
- Recommendations available immediately for new users

---

### POST /api/interactions

Track user-resource interactions for personalized learning.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "interaction_type": "view",
  "dwell_time": 45,
  "scroll_depth": 0.8,
  "session_id": "session_abc123"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resource_id` | string | Yes | UUID of the resource |
| `interaction_type` | string | Yes | Type of interaction |
| `dwell_time` | integer | No | Time spent in seconds |
| `scroll_depth` | float | No | Scroll percentage (0.0-1.0) |
| `session_id` | string | No | Session identifier |

**Interaction Types:**
- `view` - User viewed the resource (strength: 0.1-0.5 based on dwell time and scroll depth)
- `annotation` - User annotated the resource (strength: 0.7)
- `collection_add` - User added to collection (strength: 0.8)
- `export` - User exported the resource (strength: 0.9)
- `rating` - User rated the resource (strength: based on rating value)

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "user123",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "interaction_type": "view",
  "interaction_strength": 0.42,
  "is_positive": true,
  "confidence": 0.85,
  "dwell_time": 45,
  "scroll_depth": 0.8,
  "return_visits": 1,
  "interaction_timestamp": "2024-01-15T14:30:00Z"
}
```

**Interaction Strength Calculation:**
```python
# View interaction
strength = 0.1 + min(0.3, dwell_time/1000) + 0.1 * scroll_depth

# Annotation
strength = 0.7

# Collection add
strength = 0.8

# Export
strength = 0.9

# Positive interaction threshold
is_positive = strength > 0.4
```

**Example:**
```bash
# Track a view interaction
curl -X POST http://127.0.0.1:8000/api/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "interaction_type": "view",
    "dwell_time": 120,
    "scroll_depth": 0.95,
    "session_id": "session_xyz789"
  }'

# Track a collection add
curl -X POST http://127.0.0.1:8000/api/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "interaction_type": "collection_add"
  }'
```

**Automatic Profile Updates:**
- Updates `total_interactions` count
- Updates `last_active_at` timestamp
- Triggers preference learning every 10 interactions
- Recomputes user embedding for collaborative filtering

---

### GET /api/profile

Retrieve user profile settings and learned preferences.

**Response (200 OK):**
```json
{
  "user_id": "user123",
  "research_domains": ["Machine Learning", "Artificial Intelligence"],
  "active_domain": "Machine Learning",
  "preferred_taxonomy_ids": ["tax_001", "tax_002"],
  "preferred_authors": ["John Doe", "Jane Smith"],
  "preferred_sources": ["arxiv.org", "nature.com"],
  "excluded_sources": ["example.com"],
  "diversity_preference": 0.5,
  "novelty_preference": 0.3,
  "recency_bias": 0.5,
  "total_interactions": 47,
  "avg_session_duration": 180,
  "last_active_at": "2024-01-15T14:30:00Z",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

**Preference Ranges:**
- `diversity_preference`: 0.0 (focused) to 1.0 (diverse)
- `novelty_preference`: 0.0 (popular) to 1.0 (novel)
- `recency_bias`: 0.0 (timeless) to 1.0 (recent only)

**Example:**
```bash
curl "http://127.0.0.1:8000/api/profile"
```

---

### PUT /api/profile

Update user profile preferences.

**Request Body:**
```json
{
  "diversity_preference": 0.7,
  "novelty_preference": 0.5,
  "recency_bias": 0.4,
  "research_domains": ["Machine Learning", "Natural Language Processing"],
  "excluded_sources": ["example.com", "spam-site.com"]
}
```

**Request Fields:**

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `diversity_preference` | float | Diversity preference | 0.0-1.0 |
| `novelty_preference` | float | Novelty preference | 0.0-1.0 |
| `recency_bias` | float | Recency bias | 0.0-1.0 |
| `research_domains` | array[string] | Research domains | Max 10 items |
| `excluded_sources` | array[string] | Excluded sources | Max 50 items |

**Response (200 OK):**
```json
{
  "user_id": "user123",
  "diversity_preference": 0.7,
  "novelty_preference": 0.5,
  "recency_bias": 0.4,
  "research_domains": ["Machine Learning", "Natural Language Processing"],
  "excluded_sources": ["example.com", "spam-site.com"],
  "updated_at": "2024-01-15T15:00:00Z"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:8000/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "diversity_preference": 0.8,
    "novelty_preference": 0.6,
    "research_domains": ["Deep Learning", "Computer Vision"]
  }'
```

**Validation Errors:**
```json
{
  "detail": [
    {
      "loc": ["body", "diversity_preference"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

### POST /api/recommendations/feedback

Submit feedback on recommendation quality.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "was_clicked": true,
  "was_useful": true,
  "feedback_notes": "Exactly what I was looking for!"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resource_id` | string | Yes | UUID of recommended resource |
| `was_clicked` | boolean | Yes | Whether user clicked the recommendation |
| `was_useful` | boolean | No | Whether recommendation was useful |
| `feedback_notes` | string | No | Optional feedback text |

**Response (201 Created):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "user123",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "recommendation_strategy": "hybrid",
  "recommendation_score": 0.87,
  "rank_position": 1,
  "was_clicked": true,
  "was_useful": true,
  "feedback_notes": "Exactly what I was looking for!",
  "recommended_at": "2024-01-15T14:00:00Z",
  "feedback_at": "2024-01-15T14:05:00Z"
}
```

**Example:**
```bash
# Positive feedback
curl -X POST http://127.0.0.1:8000/api/recommendations/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "was_clicked": true,
    "was_useful": true,
    "feedback_notes": "Very relevant!"
  }'

# Negative feedback
curl -X POST http://127.0.0.1:8000/api/recommendations/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "was_clicked": false,
    "was_useful": false
  }'
```

**Feedback Usage:**
- Computes click-through rate (CTR) by strategy
- Identifies underperforming recommendation strategies
- Trains NCF model with implicit feedback
- Improves future recommendations

---

### Recommendation Algorithms

#### Neural Collaborative Filtering (NCF)

**Architecture:**
```
User ID → User Embedding (64-dim)  ┐
                                    ├→ Concatenate → MLP (128→64→32) → Score
Item ID → Item Embedding (64-dim)  ┘
```

**Training:**
- Positive samples: User interactions with `is_positive=True`
- Negative samples: Random non-interacted items
- Loss function: Binary Cross-Entropy
- Optimizer: Adam with learning rate 0.001
- Batch size: 256
- Epochs: 10

**Prediction:**
```python
score = ncf_model.predict(user_id, resource_id)
# Returns float in [0, 1] range
```

**Requirements:**
- Minimum 5 interactions per user for collaborative filtering
- Model retraining recommended every 100 new interactions
- GPU acceleration: 5-10x speedup over CPU

---

#### Content-Based Similarity

**User Embedding:**
```python
user_embedding = weighted_average(
    resource_embeddings,
    weights=interaction_strengths
)
# Limited to 100 most recent positive interactions
```

**Similarity Computation:**
```python
content_score = cosine_similarity(
    user_embedding,
    resource_embedding
)
# Returns float in [0, 1] range
```

**Threshold:**
- Minimum similarity: 0.3
- Candidates with similarity < 0.3 are filtered out

---

#### Graph-Based Discovery

**Multi-Hop Neighbors:**
```python
candidates = graph_service.get_neighbors_multihop(
    resource_ids=user_interacted_resources,
    hops=2,
    limit=100
)
```

**Edge Types:**
- Citation relationships
- Co-authorship networks
- Subject similarity
- Temporal connections

**Scoring:**
```python
graph_score = edge_weight * (1 / distance)
# Normalized to [0, 1] range
```

---

#### Diversity Optimization (MMR)

**Maximal Marginal Relevance:**
```python
MMR_score = λ * relevance - (1-λ) * max_similarity_to_selected

where:
  λ = user.diversity_preference (default 0.5)
  relevance = hybrid_score
  max_similarity = max cosine similarity to already-selected items
```

**Algorithm:**
1. Start with empty result set
2. Select highest-scoring candidate
3. For remaining candidates, compute MMR score
4. Select candidate with highest MMR score
5. Repeat until limit reached

**Target:**
- Gini coefficient < 0.3 for diverse recommendations
- Ensures coverage of different topics and perspectives

---

#### Novelty Promotion

**Novelty Score:**
```python
novelty_score = 1.0 - (resource.view_count / median_view_count)
# Normalized to [0, 1] range
```

**Boosting:**
```python
if novelty_score > user.novelty_preference:
    hybrid_score *= (1.0 + 0.2 * novelty_score)
```

**Guarantee:**
- At least 20% of recommendations from outside top-viewed resources
- Promotes discovery of hidden gems

---

### Performance Metrics

#### Recommendation Quality

**Click-Through Rate (CTR):**
```python
CTR = clicked_recommendations / total_recommendations
# Target: 40% improvement over baseline
```

**Diversity (Gini Coefficient):**
```python
Gini = 2 * sum(i * score_i) / (n * sum(scores)) - (n+1)/n
# Target: < 0.3 (lower is more diverse)
```

**Novelty:**
```python
novelty_percentage = novel_recommendations / total_recommendations
# Target: > 20%
```

#### System Performance

**Latency Targets:**
- Recommendation generation: <200ms for 20 items
- User embedding computation: <10ms
- NCF prediction: <5ms per resource
- Database queries: <50ms per query

**Cache Performance:**
- User embedding cache TTL: 5 minutes
- Cache hit rate target: >80%
- Cache invalidation: On new interactions

**Throughput:**
- Concurrent users: 100+
- Recommendations per second: 50+
- Interaction tracking: 1000+ per second

---

### Error Handling

**Insufficient Interactions:**
```json
{
  "detail": "Collaborative filtering requires at least 5 interactions",
  "current_interactions": 3,
  "strategy_used": "content+graph"
}
```

**Invalid Strategy:**
```json
{
  "detail": "Invalid strategy. Must be one of: collaborative, content, graph, hybrid",
  "status_code": 422
}
```

**Invalid Preference Range:**
```json
{
  "detail": "diversity_preference must be between 0.0 and 1.0",
  "status_code": 422
}
```

**NCF Model Unavailable:**
- Falls back to content + graph strategies
- Logs warning for monitoring
- Returns recommendations with `cold_start: true` in metadata

**Resource Not Found:**
```json
{
  "detail": "Resource not found",
  "status_code": 404
}
```

---

### Best Practices

#### For Users

**Building Your Profile:**
1. Start interacting with resources (view, annotate, collect)
2. After 5 interactions, collaborative filtering activates
3. After 10 interactions, preference learning begins
4. Adjust diversity/novelty preferences based on results

**Optimizing Recommendations:**
- Higher diversity (0.7-1.0): Explore new topics
- Lower diversity (0.0-0.3): Focus on known interests
- Higher novelty (0.7-1.0): Discover hidden gems
- Lower novelty (0.0-0.3): Stick to popular resources

**Providing Feedback:**
- Click recommendations you find useful
- Submit explicit feedback for best/worst recommendations
- Helps improve future recommendations for all users

#### For Developers

**Training NCF Model:**
```bash
# Initial training with existing interactions
curl -X POST http://127.0.0.1:8000/admin/ncf/train \
  -H "Content-Type: application/json" \
  -d '{"epochs": 10, "batch_size": 256}'

# Retrain after 100+ new interactions
curl -X POST http://127.0.0.1:8000/admin/ncf/train
```

**Monitoring Performance:**
```bash
# Check recommendation metrics
curl "http://127.0.0.1:8000/admin/recommendations/metrics"

# Check cache hit rate
curl "http://127.0.0.1:8000/admin/recommendations/cache-stats"

# Check NCF model health
curl "http://127.0.0.1:8000/admin/ncf/health"
```

**Debugging Recommendations:**
```bash
# Get detailed scoring breakdown
curl "http://127.0.0.1:8000/api/recommendations?limit=5&debug=true"

# Compare strategies
curl "http://127.0.0.1:8000/api/recommendations/compare-strategies"
```

---
