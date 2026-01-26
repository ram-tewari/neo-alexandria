# Unused Backend APIs - Not Mapped to Frontend

This document lists all backend APIs that are **NOT** currently mapped to any frontend phase in the ROADMAP.

## Summary

- **Total Backend Modules**: 15
- **APIs Mapped to Frontend**: ~90 endpoints across 8 phases
- **Unused APIs**: ~60+ endpoints

---

## 1. Resources Module

### Unused Endpoints:
- `PUT /resources/{resource_id}/classify` - Manual classification override
- `POST /resources/{resource_id}/chunks` - Manual chunking trigger
- `GET /chunks/{chunk_id}` - Get specific chunk by ID
- `POST /resources/ingest-repo` - Repository ingestion (used in Phase 7 but not Phase 3)
- `GET /resources/ingest-repo/{task_id}/status` - Ingestion status tracking

**Potential Use**: Phase 3 could add manual chunking controls and chunk inspection

---

## 2. Quality Module

### Unused Endpoints:
- `GET /resources/{resource_id}/quality-details` - Full quality dimension breakdown
- `POST /quality/recalculate` - Trigger quality recomputation
- `GET /quality/outliers` - List quality outliers with pagination
- `GET /quality/degradation` - Quality degradation report over time
- `POST /summaries/{resource_id}/evaluate` - Summary quality evaluation
- `GET /quality/distribution` - Quality score distribution histogram
- `GET /quality/trends` - Quality trends over time
- `GET /quality/dimensions` - Average scores per dimension
- `GET /quality/review-queue` - Resources flagged for review
- `POST /evaluation/submit` - Submit RAG evaluation data
- `GET /evaluation/metrics` - Aggregated RAG metrics
- `GET /evaluation/history` - RAG evaluation history

**Potential Use**: 
- Phase 2 uses basic quality badges, but could add detailed quality analytics dashboard
- Phase 6 could use RAG evaluation endpoints for search quality monitoring

---

## 3. Scholarly Module

### Unused Endpoints:
- `POST /resources/{resource_id}/metadata/extract` - Manual metadata extraction trigger
- `GET /metadata/{resource_id}` - Alias for metadata retrieval
- `GET /equations/{resource_id}` - Alias for equations retrieval
- `GET /tables/{resource_id}` - Alias for tables retrieval
- `GET /metadata/completeness-stats` - Metadata completeness statistics

**Potential Use**: Phase 3 uses main endpoints, but aliases and stats could be added for admin dashboard

---

## 4. Search Module

### Unused Endpoints:
- `POST /admin/sparse-embeddings/generate` - Batch sparse embedding generation
- `POST /search/advanced` - Advanced RAG search (parent-child, GraphRAG, hybrid)

**Potential Use**: 
- Phase 6 uses basic search, but advanced RAG search could enhance results
- Phase 7 could use sparse embedding generation for admin operations

---

## 5. Curation Module

### ALL Endpoints Unused:
- `GET /curation/review-queue` - Review queue with quality threshold
- `POST /curation/batch-update` - Batch resource updates
- `GET /curation/quality-analysis/{resource_id}` - Quality analysis details
- `GET /curation/low-quality` - List low-quality resources
- `POST /curation/bulk-quality-check` - Bulk quality recalculation
- `POST /curation/batch/review` - Batch review operations
- `POST /curation/batch/tag` - Batch tagging
- `POST /curation/batch/assign` - Assign curator to resources
- `GET /curation/queue` - Enhanced review queue with filters

**Potential Use**: Could be entire new Phase 9 - "Content Curation Dashboard"

---

## 6. Taxonomy Module

### ALL Endpoints Unused:
- `POST /taxonomy/categories` - Create taxonomy category
- `POST /taxonomy/classify/{resource_id}` - Classify resource
- `GET /taxonomy/predictions/{resource_id}` - Get classification predictions
- `POST /taxonomy/retrain` - Retrain ML classification model
- `GET /taxonomy/uncertain` - Get uncertain predictions for active learning

**Potential Use**: Could be Phase 10 - "Taxonomy Management & Active Learning"

---

## 7. Recommendations Module

### Unused Endpoints:
- `GET /recommendations/simple` - Simple recommendations (Phase 5.5 basic)
- `GET /recommendations/profile` - Get user profile settings
- `GET /recommendations/interactions` - Get user interaction history
- `PUT /recommendations/profile` - Update user profile settings
- `POST /recommendations/feedback` - Submit recommendation feedback
- `GET /recommendations/metrics` - Performance metrics
- `POST /recommendations/refresh` - Trigger recommendation refresh

**Potential Use**: Phase 6 uses basic recommendations, but profile management and feedback could enhance personalization

---

## 8. Collections Module

### Unused Endpoints:
- `POST /collections/{collection_id}/resources` - Add single resource (has batch version)
- `GET /collections/{collection_id}/resources` - List collection resources (redundant with main endpoint)
- `DELETE /collections/{collection_id}/resources/{resource_id}` - Remove single resource
- `GET /collections/{collection_id}/similar-collections` - Find similar collections
- `POST /collections/{collection_id}/resources/batch` - Batch add resources
- `DELETE /collections/{collection_id}/resources/batch` - Batch remove resources

**Potential Use**: Phase 3 uses basic collection operations, but batch operations and similar collections could improve UX

---

## 9. Authority Module

### ALL Endpoints Unused:
- `GET /authority/subjects/suggest` - Subject suggestions
- `GET /authority/classification/tree` - Classification tree

**Potential Use**: Could enhance Phase 2 or Phase 3 with subject authority suggestions

---

## 10. Annotations Module

### Unused Endpoints:
- `GET /annotations` - List all user annotations across resources
- `GET /annotations/search/fulltext` - Full-text search in annotations
- `GET /annotations/search/tags` - Search by tags
- `GET /annotations/export/markdown` - Export to Markdown
- `GET /annotations/export/json` - Export to JSON

**Potential Use**: Phase 2 uses basic annotation CRUD, but search and export could be added

---

## 11. Graph Module

### Unused Endpoints:
- `POST /api/graph/resources/{resource_id}/extract-citations` - Extract citations
- `POST /api/graph/embeddings/generate` - Generate graph embeddings
- `GET /api/graph/embeddings/{node_id}` - Get node embedding
- `GET /api/graph/embeddings/{node_id}/similar` - Find similar nodes
- `POST /api/graph/discover` - Discover hypotheses (LBD)
- `GET /api/graph/hypotheses/{hypothesis_id}` - Get hypothesis details
- `POST /api/graph/extract/{chunk_id}` - Extract entities/relationships from chunk
- `GET /api/graph/entities` - List graph entities
- `GET /api/graph/entities/{id}/relationships` - Get entity relationships
- `GET /api/graph/traverse` - Traverse knowledge graph

**Potential Use**: Phase 4 uses basic graph endpoints, but LBD and entity extraction could be powerful additions

---

## 12. MCP Module

### Unused Endpoints:
- `GET /mcp/sessions/{session_id}` - Get session details

**Potential Use**: Phase 8 uses main MCP endpoints, session details could be added for debugging

---

## 13. Monitoring Module

### Unused Endpoints:
- `GET /api/monitoring/performance` - Performance metrics summary
- `GET /api/monitoring/recommendation-quality` - Recommendation quality metrics
- `GET /api/monitoring/user-engagement` - User engagement metrics
- `GET /api/monitoring/model-health` - NCF model health
- `GET /api/monitoring/health/ml` - ML model health check
- `GET /api/monitoring/database` - Database metrics
- `GET /api/monitoring/db/pool` - DB connection pool status
- `GET /api/monitoring/events` - Event bus metrics
- `GET /api/monitoring/events/history` - Event history
- `GET /api/monitoring/cache/stats` - Cache statistics
- `GET /api/monitoring/workers/status` - Celery worker status
- `GET /api/monitoring/health/module/{module_name}` - Module health

**Potential Use**: Phase 7 uses basic health checks, but detailed monitoring could be added

---

## 14. Auth Module

### Unused Endpoints:
- `POST /api/auth/logout` - Logout endpoint
- `GET /api/auth/google` - Google OAuth2 initiation
- `GET /api/auth/google/callback` - Google OAuth2 callback
- `GET /api/auth/github` - GitHub OAuth2 initiation
- `GET /api/auth/github/callback` - GitHub OAuth2 callback

**Potential Use**: Phase 1 uses basic auth, but OAuth2 social login could be added

---

## 15. Planning Module

### Unused Endpoints:
None - All endpoints are mapped to Phase 5

---

## Recommendations for Frontend Phases

### Phase 2 Enhancements:
- Add quality analytics dashboard using quality module endpoints
- Add annotation search and export features

### Phase 3 Enhancements:
- Add manual chunking controls
- Add batch collection operations
- Add similar collections discovery

### Phase 4 Enhancements:
- Add LBD hypothesis discovery
- Add entity extraction and relationship visualization
- Add graph embedding similarity search

### Phase 6 Enhancements:
- Add advanced RAG search (parent-child, GraphRAG)
- Add RAG evaluation metrics
- Add recommendation feedback and profile management

### Phase 7 Enhancements:
- Add detailed monitoring dashboards
- Add sparse embedding generation
- Add event bus metrics

### New Phase 9 - Content Curation:
- Implement entire curation module
- Review queue management
- Batch operations
- Quality analysis

### New Phase 10 - Taxonomy Management:
- Implement entire taxonomy module
- Category management
- ML model retraining
- Active learning with uncertain predictions

### New Phase 11 - Social Authentication:
- Add OAuth2 Google login
- Add OAuth2 GitHub login
- Add logout functionality

---

## Statistics

**By Module**:
- Resources: 5 unused endpoints
- Quality: 12 unused endpoints
- Scholarly: 5 unused endpoints
- Search: 2 unused endpoints
- Curation: 9 unused endpoints (100% unused)
- Taxonomy: 5 unused endpoints (100% unused)
- Recommendations: 7 unused endpoints
- Collections: 6 unused endpoints
- Authority: 2 unused endpoints (100% unused)
- Annotations: 5 unused endpoints
- Graph: 10 unused endpoints
- MCP: 1 unused endpoint
- Monitoring: 12 unused endpoints
- Auth: 5 unused endpoints
- Planning: 0 unused endpoints

**Total Unused**: ~86 endpoints across 14 modules

**Modules with 100% Unused APIs**:
1. Curation (9 endpoints)
2. Taxonomy (5 endpoints)
3. Authority (2 endpoints)

These represent significant opportunities for new frontend features!
