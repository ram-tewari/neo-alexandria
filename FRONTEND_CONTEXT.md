# Neo Alexandria 2.0 - Frontend Development Context

> **Purpose**: This document provides comprehensive backend context for generating frontend specifications and implementations. It consolidates API contracts, data models, authentication patterns, and architectural decisions.

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [Architecture Summary](#architecture-summary)
3. [Authentication & Authorization](#authentication--authorization)
4. [API Reference](#api-reference)
5. [Data Models](#data-models)
6. [Event System](#event-system)
7. [Performance Requirements](#performance-requirements)
8. [Frontend Integration Patterns](#frontend-integration-patterns)

---

## Product Overview

### What We're Building

Neo Alexandria 2.0 is an advanced knowledge management system combining traditional information retrieval with modern AI-powered features:

- **Intelligent Content Processing**: Auto-summarization, tagging, classification, quality assessment
- **Advanced Discovery**: Hybrid search (keyword + semantic), knowledge graph, citation analysis
- **Active Reading**: Text highlighting, notes, semantic annotation search
- **Organization**: Collections, hierarchical taxonomy, quality filtering

### Target Users

1. **Researchers** - Managing papers, articles, datasets
2. **Knowledge Workers** - Domain-specific knowledge bases
3. **Students** - Study materials and research organization
4. **Teams** - Collaborative knowledge management

### Non-Goals (What We're NOT Building)

❌ Social network features  
❌ Content creation/authoring tools  
❌ General file storage  
❌ Real-time collaboration  
❌ Native mobile apps (web-first, responsive only)  
❌ Enterprise SSO  
❌ Multi-tenancy  
❌ Video/audio processing

---

## Architecture Summary

### Backend Architecture

**Type**: Modular Monolith with Event-Driven Communication  
**Pattern**: Vertical slices with shared kernel  
**API**: RESTful JSON API with FastAPI

### 13 Domain Modules

Each module is self-contained with its own router, service, schema, model, and event handlers:

| Module | Purpose | Key Features |
|--------|---------|--------------|
| **Auth** | Authentication & authorization | JWT tokens, OAuth2 (Google/GitHub), rate limiting |
| **Resources** | Content management | URL ingestion, metadata extraction, chunking, code analysis |
| **Search** | Hybrid search | Keyword + semantic + full-text, GraphRAG, evaluation |
| **Collections** | Organization | Collection management, recommendations, hierarchies |
| **Annotations** | Active reading | Highlights, notes, tags, semantic search, export |
| **Taxonomy** | Classification | ML-based classification, hierarchical trees, active learning |
| **Graph** | Knowledge graph | Citations, entities, relationships, hypothesis discovery |
| **Recommendations** | Personalization | Hybrid (collaborative + content + graph), user profiles |
| **Quality** | Assessment | Multi-dimensional scoring, outlier detection, RAG evaluation |
| **Scholarly** | Academic metadata | Equations, tables, citations, author extraction |
| **Authority** | Subject authority | Classification trees, authority management |
| **Curation** | Content review | Batch operations, quality workflows |
| **Monitoring** | System health | Health checks, metrics, status |

### Module Communication

- **Direct calls**: Use shared kernel services (database, cache, embeddings, AI)
- **Cross-module**: Event bus only (no direct imports)
- **Event latency**: <1ms (p95) for emission + delivery

---

## Authentication & Authorization

### Authentication Methods

#### 1. JWT Bearer Token (Primary)

All protected endpoints require JWT access token:

```http
Authorization: Bearer <access_token>
```

#### 2. OAuth2 Password Flow

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 3. OAuth2 Social Login

```http
GET /auth/google      # Initiate Google OAuth2
GET /auth/github      # Initiate GitHub OAuth2
```

### Token Management

| Token Type | Lifetime | Purpose |
|------------|----------|---------|
| Access Token | 30 minutes | API requests |
| Refresh Token | 7 days | Obtain new access tokens |

**Refresh Token:**
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

**Logout (Revoke):**
```http
POST /auth/logout
Authorization: Bearer <access_token>
```

### Rate Limiting

**Tiered System** (Redis-backed sliding window):

| Tier | Requests/Hour | Use Case |
|------|---------------|----------|
| Free | 100 | Development, personal |
| Premium | 1,000 | Professional, small teams |
| Admin | 10,000 | System administrators |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1704067200
```

**Rate Limit Exceeded (429):**
```json
{
  "detail": "Rate limit exceeded. Try again in 3600 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

### Public Endpoints (No Auth Required)

- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/google`, `GET /auth/google/callback`
- `GET /auth/github`, `GET /auth/github/callback`
- `GET /docs`, `GET /openapi.json`
- `GET /monitoring/health`

**All other endpoints require authentication.**

---

## API Reference

### Base URL

```
Development: http://127.0.0.1:8000
Production: https://your-domain.com/api
```

### Response Format

**Success:**
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

**Error:**
```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 202 | Accepted (async processing) |
| 204 | No Content (successful deletion) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

### Pagination

**Offset-based:**
```http
GET /resources?limit=25&offset=0
```

**Page-based:**
```http
GET /collections?page=1&limit=50
```

### Sorting

```http
GET /resources?sort_by=created_at&sort_dir=desc
```

Common fields: `created_at`, `updated_at`, `quality_score`, `title`, `relevance`

---

## API Endpoints by Module

### Auth Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login with credentials |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Revoke token |
| GET | `/auth/me` | Get current user |
| PUT | `/auth/me` | Update user profile |
| GET | `/auth/google` | Google OAuth2 initiation |
| GET | `/auth/google/callback` | Google OAuth2 callback |
| GET | `/auth/github` | GitHub OAuth2 initiation |
| GET | `/auth/github/callback` | GitHub OAuth2 callback |

### Resources Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/resources` | Ingest resource from URL |
| GET | `/resources` | List resources (with filters) |
| GET | `/resources/{id}` | Get resource details |
| PUT | `/resources/{id}` | Update resource metadata |
| DELETE | `/resources/{id}` | Delete resource |
| GET | `/resources/{id}/status` | Check ingestion status |
| POST | `/resources/{id}/rechunk` | Trigger rechunking |
| GET | `/resources/{id}/chunks` | Get resource chunks |
| POST | `/resources/batch` | Batch ingest resources |
| POST | `/resources/repo` | Ingest code repository |
| GET | `/resources/repo/{id}/status` | Check repo ingestion status |

**Key Filters:**
- `language`, `type`, `classification_code`
- `min_quality`, `max_quality`
- `start_date`, `end_date`
- `search` (keyword search)

### Search Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/search` | Advanced hybrid search |
| GET | `/search/three-way-hybrid` | Three-way hybrid (keyword + semantic + FTS) |
| GET | `/search/compare-methods` | Compare search methods |
| POST | `/search/evaluate` | Evaluate search quality |
| POST | `/search/synthetic-questions` | Generate synthetic questions |

**Search Request:**
```json
{
  "text": "machine learning",
  "hybrid_weight": 0.7,
  "limit": 10,
  "filters": {
    "min_quality": 0.7,
    "classification_code": "004"
  }
}
```

### Collections Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/collections` | Create collection |
| GET | `/collections` | List collections |
| GET | `/collections/{id}` | Get collection with resources |
| PUT | `/collections/{id}` | Update collection |
| DELETE | `/collections/{id}` | Delete collection |
| POST | `/collections/{id}/resources` | Add resource |
| DELETE | `/collections/{id}/resources/{resource_id}` | Remove resource |
| POST | `/collections/{id}/resources/batch` | Batch add resources |
| DELETE | `/collections/{id}/resources/batch` | Batch remove resources |
| GET | `/collections/{id}/recommendations` | Get recommendations |
| GET | `/collections/{id}/similar-collections` | Find similar collections |

### Annotations Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/resources/{id}/annotations` | Create annotation |
| GET | `/resources/{id}/annotations` | List resource annotations |
| GET | `/annotations` | List all user annotations |
| GET | `/annotations/{id}` | Get annotation |
| PUT | `/annotations/{id}` | Update annotation |
| DELETE | `/annotations/{id}` | Delete annotation |
| GET | `/annotations/search/fulltext` | Full-text search |
| GET | `/annotations/search/semantic` | Semantic search |
| GET | `/annotations/search/tags` | Search by tags |
| GET | `/annotations/export/markdown` | Export to Markdown |
| GET | `/annotations/export/json` | Export to JSON |

**Annotation Model:**
```json
{
  "start_offset": 100,
  "end_offset": 250,
  "highlighted_text": "Selected text",
  "note": "My thoughts",
  "tags": ["important", "review"],
  "color": "#FFFF00",
  "is_shared": false
}
```

### Taxonomy Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/taxonomy/categories` | Create category |
| POST | `/taxonomy/classify/{id}` | Classify resource |
| GET | `/taxonomy/predictions/{id}` | Get predictions |
| POST | `/taxonomy/retrain` | Retrain ML model |
| GET | `/taxonomy/uncertain` | Get uncertain classifications |

### Graph Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/graph/citations/{id}` | Get citations |
| GET | `/graph/network` | Get citation network |
| GET | `/graph/entities/{id}` | Get entities |
| GET | `/graph/relationships/{id}` | Get relationships |
| GET | `/graph/hypotheses` | Get discovered hypotheses |
| POST | `/graph/extract/{id}` | Extract graph data |

### Recommendations Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/recommendations` | Get personalized recommendations |
| GET | `/recommendations/simple` | Simple recommendations |
| POST | `/recommendations/interactions` | Track interaction |
| GET | `/recommendations/profile` | Get user profile |
| PUT | `/recommendations/profile` | Update user profile |
| GET | `/recommendations/interactions` | Get interaction history |
| POST | `/recommendations/feedback` | Submit feedback |
| POST | `/recommendations/refresh` | Refresh recommendations |

**Recommendation Response:**
```json
{
  "recommendations": [
    {
      "resource_id": "uuid",
      "title": "Resource Title",
      "score": 0.87,
      "strategy": "hybrid",
      "scores": {
        "collaborative": 0.85,
        "content": 0.90,
        "graph": 0.82
      },
      "novelty_score": 0.65
    }
  ],
  "metadata": {
    "strategy": "hybrid",
    "is_cold_start": false,
    "diversity_applied": true
  }
}
```

### Quality Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/resources/{id}/quality-details` | Quality breakdown |
| POST | `/quality/recalculate` | Recalculate quality |
| GET | `/quality/outliers` | Get outliers |
| GET | `/quality/distribution` | Quality distribution |
| POST | `/quality/evaluate-rag` | Evaluate RAG quality |
| GET | `/quality/rag-metrics` | Get RAG metrics |

### Monitoring Module

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Basic health check |
| GET | `/monitoring/status` | Detailed system status |
| GET | `/monitoring/metrics` | System metrics |

---

## Data Models

### Resource Model

```typescript
interface Resource {
  id: string;  // UUID
  url: string;
  title: string;
  description?: string;
  content?: string;
  content_type: string;
  language?: string;
  creator?: string;
  publisher?: string;
  publication_date?: string;  // ISO 8601
  type: 'article' | 'paper' | 'book' | 'video' | 'code' | 'other';
  
  // Status
  status: 'pending' | 'processing' | 'completed' | 'failed';
  ingestion_status?: string;
  error_message?: string;
  
  // Quality
  quality_score?: number;  // 0.0-1.0
  is_outlier?: boolean;
  
  // Classification
  classification_code?: string;
  classification_confidence?: number;
  
  // Metadata
  word_count?: number;
  reading_time_minutes?: number;
  tags?: string[];
  
  // Advanced RAG
  chunking_strategy?: 'fixed' | 'semantic' | 'parent_child' | 'code_ast';
  chunk_count?: number;
  has_embeddings?: boolean;
  
  // Code-specific
  is_code_repository?: boolean;
  repository_url?: string;
  primary_language?: string;
  
  // Timestamps
  created_at: string;  // ISO 8601
  updated_at: string;  // ISO 8601
}
```

### Collection Model

```typescript
interface Collection {
  id: string;  // UUID
  name: string;
  description?: string;
  owner_id: string;
  visibility: 'private' | 'shared' | 'public';
  parent_id?: string;  // UUID
  resource_count: number;
  created_at: string;
  updated_at: string;
}
```

### Annotation Model

```typescript
interface Annotation {
  id: string;  // UUID
  resource_id: string;  // UUID
  user_id: string;
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color?: string;  // Hex color
  context_before?: string;
  context_after?: string;
  is_shared: boolean;
  collection_ids?: string[];  // UUIDs
  created_at: string;
  updated_at: string;
}
```

### Search Result Model

```typescript
interface SearchResult {
  resource_id: string;
  title: string;
  description?: string;
  score: number;  // 0.0-1.0
  rank: number;
  method: 'keyword' | 'semantic' | 'hybrid' | 'three_way';
  scores?: {
    keyword?: number;
    semantic?: number;
    fulltext?: number;
  };
  quality_score?: number;
  classification_code?: string;
  created_at: string;
}
```

### User Profile Model

```typescript
interface UserProfile {
  user_id: string;
  email: string;
  full_name?: string;
  tier: 'free' | 'premium' | 'admin';
  is_active: boolean;
  oauth_provider?: 'google' | 'github';
  
  // Recommendation preferences
  diversity_preference?: number;  // 0.0-1.0
  novelty_preference?: number;  // 0.0-1.0
  recency_bias?: number;  // 0.0-1.0
  research_domains?: string[];
  active_domain?: string;
  excluded_sources?: string[];
  
  created_at: string;
  last_login_at?: string;
}
```

### Quality Dimensions Model

```typescript
interface QualityDimensions {
  resource_id: string;
  overall_score: number;  // 0.0-1.0
  
  // Individual dimensions
  completeness: number;
  accuracy: number;
  readability: number;
  authority: number;
  recency: number;
  
  // Flags
  is_outlier: boolean;
  outlier_reason?: string;
  
  computed_at: string;
}
```

### Chunk Model (Advanced RAG)

```typescript
interface Chunk {
  id: string;  // UUID
  resource_id: string;  // UUID
  content: string;
  chunk_index: number;
  chunk_type: 'parent' | 'child' | 'standard';
  parent_chunk_id?: string;  // UUID
  
  // Metadata
  start_offset: number;
  end_offset: number;
  token_count: number;
  
  // Code-specific
  code_metadata?: {
    language?: string;
    file_path?: string;
    function_name?: string;
    class_name?: string;
    start_line?: number;
    end_line?: number;
  };
  
  // Embeddings
  has_embedding: boolean;
  
  created_at: string;
}
```

---

## Event System

### Event-Driven Architecture

Modules communicate via an in-memory async event bus with <1ms latency (p95).

### Event Categories

**Resource Events:**
- `resource.created` - New resource ingested
- `resource.updated` - Resource metadata updated
- `resource.deleted` - Resource removed
- `resource.chunked` - Resource chunked for RAG
- `resource.classified` - Resource classified

**Collection Events:**
- `collection.created` - New collection created
- `collection.resource_added` - Resource added to collection
- `collection.resource_removed` - Resource removed from collection

**Annotation Events:**
- `annotation.created` - New annotation created
- `annotation.updated` - Annotation updated
- `annotation.deleted` - Annotation removed

**Quality Events:**
- `quality.computed` - Quality scores calculated
- `quality.outlier_detected` - Outlier detected

**Graph Events:**
- `citation.extracted` - Citations extracted
- `graph.updated` - Knowledge graph updated
- `hypothesis.discovered` - New hypothesis found
- `graph.entity_extracted` - Entities extracted
- `graph.relationship_extracted` - Relationships extracted

**Recommendation Events:**
- `recommendation.generated` - Recommendations generated
- `user.profile_updated` - User profile updated

**Search Events:**
- `search.query_executed` - Search performed
- `search.evaluated` - Search quality evaluated

---

## Performance Requirements

### API Response Times

| Operation | Target (P95) |
|-----------|--------------|
| Resource CRUD | < 200ms |
| Search (hybrid) | < 500ms |
| Collection operations | < 200ms |
| Annotation CRUD | < 100ms |
| Health check | < 50ms |

### Scalability Targets

- 100K+ resources
- 10K+ concurrent embeddings
- 1K+ collections per user
- 100+ requests/second

### Resource Limits

- Memory: 4GB min, 8GB recommended
- Storage: 10GB min for models/data
- CPU: 2+ cores recommended
- GPU: Optional (10x ML performance boost)

---

## Frontend Integration Patterns

### Authentication Flow

```typescript
// 1. Login
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ username, password })
});
const { access_token, refresh_token } = await loginResponse.json();

// 2. Store tokens
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// 3. Use token in requests
const response = await fetch('/resources', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

// 4. Handle 401 (token expired)
if (response.status === 401) {
  // Refresh token
  const refreshResponse = await fetch('/auth/refresh', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${refresh_token}` }
  });
  const { access_token: newToken } = await refreshResponse.json();
  localStorage.setItem('access_token', newToken);
  // Retry original request
}
```

### Rate Limit Handling

```typescript
const response = await fetch('/resources');

// Check rate limit headers
const remaining = response.headers.get('X-RateLimit-Remaining');
const reset = response.headers.get('X-RateLimit-Reset');

if (response.status === 429) {
  const retryAfter = response.headers.get('Retry-After');
  // Show user message: "Rate limit exceeded. Try again in {retryAfter} seconds"
}
```

### Async Operation Polling

```typescript
// 1. Start async operation (returns 202 Accepted)
const ingestResponse = await fetch('/resources', {
  method: 'POST',
  body: JSON.stringify({ url: 'https://example.com/article' })
});
const { id } = await ingestResponse.json();

// 2. Poll for status
const pollStatus = async () => {
  const statusResponse = await fetch(`/resources/${id}/status`);
  const { status, progress } = await statusResponse.json();
  
  if (status === 'completed') {
    // Done!
  } else if (status === 'failed') {
    // Handle error
  } else {
    // Still processing, poll again
    setTimeout(pollStatus, 2000);
  }
};
pollStatus();
```

### Pagination Pattern

```typescript
// Offset-based
const fetchResources = async (limit = 25, offset = 0) => {
  const response = await fetch(`/resources?limit=${limit}&offset=${offset}`);
  const { items, total } = await response.json();
  return { items, total, hasMore: offset + limit < total };
};

// Page-based
const fetchCollections = async (page = 1, limit = 50) => {
  const response = await fetch(`/collections?page=${page}&limit=${limit}`);
  return await response.json();
};
```

### Error Handling

```typescript
const handleApiError = (response, data) => {
  switch (response.status) {
    case 400:
      return { error: 'Invalid request', details: data.detail };
    case 401:
      return { error: 'Unauthorized', action: 'refresh_token' };
    case 403:
      return { error: 'Forbidden', details: data.detail };
    case 404:
      return { error: 'Not found', details: data.detail };
    case 422:
      return { error: 'Validation error', details: data.detail };
    case 429:
      return { error: 'Rate limit exceeded', retryAfter: data.detail };
    case 500:
      return { error: 'Server error', details: data.detail };
    default:
      return { error: 'Unknown error', status: response.status };
  }
};
```

### WebSocket Support (Future)

Currently not implemented. All operations use REST API with polling for async operations.

---

## Testing Considerations

### Test Mode

For development/testing, bypass authentication:

```bash
# .env file
TEST_MODE=true
```

**⚠️ Never enable in production!**

### Mock Data

Backend provides test fixtures in `backend/tests/conftest.py`:
- Sample resources
- Sample collections
- Sample annotations
- Sample users

### API Documentation

Interactive API docs available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Related Documentation

### Backend Documentation

- [API Overview](backend/docs/api/overview.md)
- [Architecture Overview](backend/docs/architecture/overview.md)
- [Module Documentation](backend/docs/architecture/modules.md)
- [Event System](backend/docs/architecture/event-system.md)
- [Database Schema](backend/docs/architecture/database.md)

### Steering Documentation

- [Product Overview](.kiro/steering/product.md)
- [Tech Stack](.kiro/steering/tech.md)
- [Repository Structure](.kiro/steering/structure.md)

### Specifications

- [Backend Specs](.kiro/specs/backend/)
- [Frontend Specs](.kiro/specs/frontend/)

---

## Quick Reference

### Common API Patterns

```typescript
// Authentication
POST /auth/login → { access_token, refresh_token }
POST /auth/refresh → { access_token }

// Resources
POST /resources → { id, status: 'pending' }
GET /resources/{id}/status → { status, progress }
GET /resources?limit=25&offset=0 → { items, total }

// Search
POST /search → { results, total, method }

// Collections
POST /collections → { id, name, resource_count }
POST /collections/{id}/resources → { added: true }

// Annotations
POST /resources/{id}/annotations → { id, highlighted_text }
GET /annotations/search/semantic?query=... → { items, total }

// Recommendations
GET /recommendations?limit=20 → { recommendations, metadata }
POST /recommendations/interactions → { interaction_id }
```

### Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Frontend
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_GOOGLE_CLIENT_ID=...
VITE_GITHUB_CLIENT_ID=...
```

---

**Last Updated**: January 6, 2026  
**Backend Version**: 0.9.0 (Phase 18 - Code Intelligence)  
**API Version**: 1.0.0
