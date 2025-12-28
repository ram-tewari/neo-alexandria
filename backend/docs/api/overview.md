# API Overview

## Base URL

```
Development: http://127.0.0.1:8000
Production: https://your-domain.com/api
```

## Authentication

Currently, no authentication is required for development and testing.

**Future Authentication (Planned):**
- API Key in `Authorization` header: `Authorization: Bearer <api_key>`
- Rate limiting: 1000 requests/hour per API key
- Ingestion limits: 100 requests/hour per API key

## Content Types

All API endpoints accept and return JSON data:
```
Content-Type: application/json
```

## Response Format

### Success Response

```json
{
  "data": {},
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 25
  }
}
```

### Error Response

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 202 | Accepted - Request accepted for processing |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid request parameters |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

## Pagination

List endpoints support pagination with `limit` and `offset`:

```
GET /resources?limit=25&offset=0
```

Response includes total count:

```json
{
  "items": [...],
  "total": 100
}
```

Some endpoints use page-based pagination:

```
GET /collections?page=1&limit=50
```

## Filtering

Most list endpoints support filtering:

```
GET /resources?language=en&min_quality=0.7&classification_code=004
```

See individual endpoint documentation for available filters.

## Sorting

List endpoints support sorting:

```
GET /resources?sort_by=created_at&sort_dir=desc
```

Common sort fields: `created_at`, `updated_at`, `quality_score`, `title`, `relevance`

## Rate Limiting

**Current**: No rate limits enforced

**Planned**:
- General API: 1000 requests per hour per API key
- Ingestion: 100 requests per hour per API key
- Search: 500 requests per hour per API key
- Burst Allowance: 50 requests per minute for short-term spikes

## API Endpoints by Domain

Neo Alexandria 2.0 uses a modular architecture where each domain is implemented as a self-contained module. All modules follow consistent patterns for routing, services, and event handling.

| Module | Description | Documentation |
|--------|-------------|---------------|
| Resources | Content management and ingestion | [resources.md](resources.md) |
| Search | Hybrid search with vector and FTS | [search.md](search.md) |
| Collections | Collection management and sharing | [collections.md](collections.md) |
| Annotations | Active reading with highlights and notes | [annotations.md](annotations.md) |
| Taxonomy | ML classification and taxonomy trees | [taxonomy.md](taxonomy.md) |
| Graph | Knowledge graph, citations, and discovery | [graph.md](graph.md) |
| Recommendations | Hybrid recommendation engine | [recommendations.md](recommendations.md) |
| Quality | Multi-dimensional quality assessment | [quality.md](quality.md) |
| Scholarly | Academic metadata extraction | [scholarly.md](scholarly.md) |
| Authority | Subject authority and classification | [authority.md](authority.md) |
| Curation | Content review and batch operations | [curation.md](curation.md) |
| Monitoring | System health and metrics | [monitoring.md](monitoring.md) |

### Module Architecture

Each module is self-contained with:
- **Router**: FastAPI endpoints at `/module-name/*`
- **Service**: Business logic and data access
- **Schema**: Pydantic models for validation
- **Model**: SQLAlchemy database models
- **Handlers**: Event subscribers and emitters
- **README**: Module-specific documentation

Modules communicate through an event bus, eliminating direct dependencies.

## Complete Endpoint Reference

### Content Management
- `POST /resources` - Ingest new resource from URL
- `GET /resources` - List resources with filtering
- `GET /resources/{id}` - Get specific resource
- `PUT /resources/{id}` - Update resource metadata
- `DELETE /resources/{id}` - Delete resource
- `GET /resources/{id}/status` - Check ingestion status
- `PUT /resources/{id}/classify` - Override classification

### Search and Discovery
- `POST /search` - Advanced hybrid search
- `GET /search/three-way-hybrid` - Three-way hybrid search
- `GET /search/compare-methods` - Compare search methods
- `POST /search/evaluate` - Evaluate search quality

### Collections
- `POST /collections` - Create collection
- `GET /collections/{id}` - Get collection
- `PUT /collections/{id}` - Update collection
- `DELETE /collections/{id}` - Delete collection
- `GET /collections` - List collections
- `POST /collections/{id}/resources` - Add resources
- `DELETE /collections/{id}/resources` - Remove resources
- `GET /collections/{id}/recommendations` - Get recommendations

### Annotations
- `POST /resources/{id}/annotations` - Create annotation
- `GET /resources/{id}/annotations` - List annotations
- `GET /annotations` - List all user annotations
- `PUT /annotations/{id}` - Update annotation
- `DELETE /annotations/{id}` - Delete annotation
- `GET /annotations/search/fulltext` - Full-text search
- `GET /annotations/search/semantic` - Semantic search
- `GET /annotations/export/markdown` - Export to Markdown
- `GET /annotations/export/json` - Export to JSON

### Taxonomy
- `POST /taxonomy/nodes` - Create taxonomy node
- `PUT /taxonomy/nodes/{id}` - Update node
- `DELETE /taxonomy/nodes/{id}` - Delete node
- `POST /taxonomy/nodes/{id}/move` - Move node
- `GET /taxonomy/tree` - Get taxonomy tree
- `POST /taxonomy/classify/{id}` - Classify resource
- `POST /taxonomy/train` - Train ML model

### Quality
- `GET /resources/{id}/quality-details` - Quality breakdown
- `POST /quality/recalculate` - Recalculate quality
- `GET /quality/outliers` - Get quality outliers
- `GET /quality/degradation` - Monitor degradation
- `GET /quality/distribution` - Quality distribution
- `GET /quality/trends` - Quality trends

### Monitoring
- `GET /health` - Health check
- `GET /monitoring/status` - System status
- `GET /monitoring/metrics` - System metrics

## SDKs and Libraries

### Python

```python
import requests

# Import from modules (new structure)
from app.modules.resources.schema import ResourceCreate
from app.modules.search.schema import SearchRequest

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

# Create a collection
response = requests.post(
    "http://127.0.0.1:8000/collections",
    json={
        "name": "ML Papers",
        "description": "Machine learning research papers"
    }
)
```

### JavaScript

```javascript
// Ingest a resource
const response = await fetch('http://127.0.0.1:8000/resources', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com/article' })
});

// Search resources
const searchResponse = await fetch('http://127.0.0.1:8000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'machine learning',
    hybrid_weight: 0.7,
    limit: 10
  })
});

// Create a collection
const collectionResponse = await fetch('http://127.0.0.1:8000/collections', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'ML Papers',
    description: 'Machine learning research papers'
  })
});
```

### Module Imports (Backend Development)

When developing backend features, import from modules:

```python
# Import from modules
from app.modules.resources import ResourceService, ResourceCreate
from app.modules.search import SearchService, SearchRequest
from app.modules.collections import CollectionService, CollectionCreate
from app.modules.annotations import AnnotationService, AnnotationCreate
from app.modules.taxonomy import TaxonomyService, ClassificationResult
from app.modules.graph import GraphService, CitationService
from app.modules.recommendations import RecommendationService
from app.modules.quality import QualityService, QualityDimensions

# Import from shared kernel
from app.shared.embeddings import EmbeddingService
from app.shared.ai_core import AICore
from app.shared.cache import CacheService
from app.shared.database import get_db
from app.shared.event_bus import event_bus
```

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Developer Setup](../guides/setup.md)
- [Testing Guide](../guides/testing.md)
