# API Overview

## Base URL

```
Development: http://127.0.0.1:8000
Production: https://your-domain.com/api
```

## Authentication

**Phase 17 Implementation**: JWT-based authentication with OAuth2 support

### Authentication Methods

#### 1. JWT Bearer Token (Primary)

All protected endpoints require a JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

**Example:**
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  http://127.0.0.1:8000/resources
```

#### 2. OAuth2 Password Flow

Obtain tokens via username/password:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 3. OAuth2 Social Login

Authenticate via Google or GitHub:

```bash
# Initiate Google OAuth2 flow
GET http://127.0.0.1:8000/auth/google

# Initiate GitHub OAuth2 flow
GET http://127.0.0.1:8000/auth/github
```

After authorization, you'll be redirected to the callback URL with tokens.

### Token Management

**Access Token:**
- Expires in 30 minutes (default)
- Used for API requests
- Short-lived for security

**Refresh Token:**
- Expires in 7 days (default)
- Used to obtain new access tokens
- Longer-lived for convenience

**Refresh Access Token:**
```bash
curl -X POST http://127.0.0.1:8000/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

**Logout (Revoke Token):**
```bash
curl -X POST http://127.0.0.1:8000/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

### Public Endpoints (No Authentication Required)

The following endpoints are publicly accessible:

- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `GET /auth/google` - Google OAuth2 initiation
- `GET /auth/google/callback` - Google OAuth2 callback
- `GET /auth/github` - GitHub OAuth2 initiation
- `GET /auth/github/callback` - GitHub OAuth2 callback
- `GET /docs` - API documentation
- `GET /openapi.json` - OpenAPI schema
- `GET /monitoring/health` - Health check

All other endpoints require authentication.

### Test Mode

For development and testing, you can bypass authentication:

```bash
# In .env file
TEST_MODE=true
```

**Warning:** Never enable TEST_MODE in production!

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
| 401 | Unauthorized - Missing or invalid authentication token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Authentication Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials",
  "error_code": "INVALID_TOKEN"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions for this operation",
  "error_code": "FORBIDDEN"
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded. Try again in 3600 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

Response includes rate limit headers (see Rate Limiting section).

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

**Phase 17 Implementation**: Tiered rate limiting with Redis-backed sliding window algorithm

### Rate Limit Tiers

| Tier | Requests per Hour | Use Case |
|------|-------------------|----------|
| Free | 100 | Development, personal use |
| Premium | 1,000 | Professional use, small teams |
| Admin | 10,000 | System administrators, automation |

Rate limits are enforced per user based on the `tier` claim in the JWT token.

### Rate Limit Headers

All API responses include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1704067200
```

**Header Descriptions:**
- `X-RateLimit-Limit`: Maximum requests allowed in the current window
- `X-RateLimit-Remaining`: Requests remaining in the current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit resets

### Rate Limit Exceeded

When rate limit is exceeded, the API returns HTTP 429:

```json
{
  "detail": "Rate limit exceeded. Try again in 3600 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

Response includes `Retry-After` header:
```
Retry-After: 3600
```

### Excluded Endpoints

The following endpoints are excluded from rate limiting:
- `GET /monitoring/health` - Health check

### Graceful Degradation

If Redis is unavailable, rate limiting fails open (allows requests) to maintain service availability. Monitor logs for Redis connectivity issues.

### Best Practices

1. **Monitor Headers**: Check `X-RateLimit-Remaining` to avoid hitting limits
2. **Implement Backoff**: Use exponential backoff when receiving 429 responses
3. **Cache Responses**: Cache API responses to reduce request volume
4. **Batch Operations**: Use batch endpoints when available
5. **Upgrade Tier**: Contact support for higher rate limits if needed

## API Endpoints by Domain

Neo Alexandria 2.0 uses a modular architecture where each domain is implemented as a self-contained module. All modules follow consistent patterns for routing, services, and event handling.

| Module | Description | Documentation |
|--------|-------------|---------------|
| Auth | JWT authentication and OAuth2 | [auth.md](auth.md) |
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

# Authenticate and get token
auth_response = requests.post(
    "http://127.0.0.1:8000/auth/login",
    data={"username": "user@example.com", "password": "password"}
)
token = auth_response.json()["access_token"]

# Set up headers with authentication
headers = {"Authorization": f"Bearer {token}"}

# Ingest a resource
response = requests.post(
    "http://127.0.0.1:8000/resources",
    json={"url": "https://example.com/article"},
    headers=headers
)

# Search resources
response = requests.post(
    "http://127.0.0.1:8000/search",
    json={
        "text": "machine learning",
        "hybrid_weight": 0.7,
        "limit": 10
    },
    headers=headers
)

# Check rate limit status
print(f"Remaining requests: {response.headers.get('X-RateLimit-Remaining')}")

# Create a collection
response = requests.post(
    "http://127.0.0.1:8000/collections",
    json={
        "name": "ML Papers",
        "description": "Machine learning research papers"
    },
    headers=headers
)
```

### JavaScript

```javascript
// Authenticate and get token
const authResponse = await fetch('http://127.0.0.1:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'password'
  })
});
const { access_token } = await authResponse.json();

// Set up headers with authentication
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${access_token}`
};

// Ingest a resource
const response = await fetch('http://127.0.0.1:8000/resources', {
  method: 'POST',
  headers,
  body: JSON.stringify({ url: 'https://example.com/article' })
});

// Search resources
const searchResponse = await fetch('http://127.0.0.1:8000/search', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    text: 'machine learning',
    hybrid_weight: 0.7,
    limit: 10
  })
});

// Check rate limit status
console.log('Remaining requests:', searchResponse.headers.get('X-RateLimit-Remaining'));

// Create a collection
const collectionResponse = await fetch('http://127.0.0.1:8000/collections', {
  method: 'POST',
  headers,
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
