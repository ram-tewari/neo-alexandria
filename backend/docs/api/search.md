# Search API

Advanced search endpoints with hybrid keyword/semantic capabilities, three-way fusion, and faceted results.

## Overview

The Search API provides multiple search strategies:
- **Hybrid Search** - Combines keyword (FTS5) and semantic (vector) search
- **Three-Way Hybrid** - Adds sparse vectors with RRF fusion and ColBERT reranking
- **Method Comparison** - Side-by-side comparison of search methods
- **Quality Evaluation** - IR metrics for search quality assessment

## Endpoints

### POST /search

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
    "classification_code": [{"key": "004", "count": 30}],
    "type": [{"key": "article", "count": 35}],
    "language": [{"key": "en", "count": 33}],
    "read_status": [{"key": "unread", "count": 20}],
    "subject": [{"key": "Machine Learning", "count": 18}]
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
    "filters": {"min_quality": 0.8},
    "limit": 10
  }'
```

---

### GET /search/three-way-hybrid

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
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=machine+learning&limit=20&enable_reranking=true"

# Fast three-way search without reranking
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=neural+networks&limit=10&enable_reranking=false"
```

**Performance:**
- Target latency: <200ms at 95th percentile
- With reranking: <1 second for 100 candidates
- Parallel retrieval for optimal speed

---

### GET /search/compare-methods

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

**Use Cases:**
- Debug search quality issues
- Compare method effectiveness for different query types
- Analyze latency trade-offs
- Validate search improvements

---

### POST /search/evaluate

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

**Metrics Explained:**
- **nDCG@20**: Normalized Discounted Cumulative Gain at position 20 (0-1, higher is better)
- **Recall@20**: Fraction of relevant documents retrieved in top 20 (0-1, higher is better)
- **Precision@20**: Fraction of top 20 results that are relevant (0-1, higher is better)
- **MRR**: Mean Reciprocal Rank of first relevant result (0-1, higher is better)

---

### POST /admin/sparse-embeddings/generate

Batch generate sparse embeddings for existing resources without them.

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2"],
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

**Background Processing:**
- Processes resources in batches for efficiency
- Commits every 100 resources
- Logs progress updates
- Resumes from last committed batch if interrupted
- Target: <1 second per resource

## Data Models

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

## Module Structure

The Search module is implemented as a self-contained vertical slice:

**Module**: `app.modules.search`  
**Router Prefix**: `/search`  
**Version**: 1.0.0

```python
from app.modules.search import (
    search_router,
    SearchService,
    SearchRequest,
    SearchResponse,
    SearchStrategy
)
```

### Events

**Emitted Events:**
- `search.executed` - When a search is performed
- `search.results_returned` - When search results are returned

**Subscribed Events:**
- `resource.created` - Updates search indices
- `resource.updated` - Updates search indices
- `resource.deleted` - Removes from search indices

## Related Documentation

- [Resources API](resources.md) - Content management
- [Recommendations API](recommendations.md) - Personalized discovery
- [Graph API](graph.md) - Knowledge graph exploration
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
