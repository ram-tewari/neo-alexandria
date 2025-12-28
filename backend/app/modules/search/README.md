# Search Module

## Overview

The Search module provides comprehensive search functionality for Neo Alexandria 2.0, including full-text search, semantic search, sparse vector search, and hybrid search with advanced reranking capabilities.

## Purpose

This module enables:
- **Full-Text Search**: Database-specific FTS (FTS5 for SQLite, tsvector for PostgreSQL)
- **Semantic Search**: Dense vector similarity using embeddings
- **Sparse Vector Search**: Learned keyword importance with BGE-M3
- **Hybrid Search**: Three-way fusion with Reciprocal Rank Fusion (RRF)
- **Reranking**: ColBERT cross-encoder for improved relevance
- **Faceted Search**: Filter by tags, classifications, quality scores
- **Query Adaptation**: Automatic weight adjustment based on query type

## Module Structure

```
search/
├── __init__.py          # Public interface and module metadata
├── router.py            # FastAPI endpoints (5 endpoints)
├── service.py           # Unified search service
├── schema.py            # Pydantic schemas for search
├── handlers.py          # Event handlers (future)
├── README.md            # This file
└── tests/
    ├── test_service.py
    ├── test_router.py
    └── test_strategies.py
```

## Public Interface

### Router
```python
from app.modules.search import search_router

# Endpoints:
# POST /search - Unified search endpoint
# POST /search/keyword - Full-text search only
# POST /search/semantic - Semantic search only
# POST /search/hybrid - Three-way hybrid search
# GET /search/facets - Get available facets
```

### Service
```python
from app.modules.search import SearchService

service = SearchService(db)
# Methods:
# - search(query: SearchQuery) -> SearchResults
# - keyword_search(query: str, filters: SearchFilters) -> List[Resource]
# - semantic_search(query: str, limit: int) -> List[Resource]
# - sparse_search(query: str, limit: int) -> List[Resource]
# - hybrid_search(query: str, weights: HybridWeights) -> List[Resource]
# - get_facets(query: str) -> Facets
```

### Schemas
```python
from app.modules.search import (
    SearchQuery,
    SearchResults,
    SearchFilters,
    Facets,
    HybridWeights,
    ThreeWayHybridResults,
    RankedResult
)
```

## Search Architecture

### Three-Phase Pipeline

#### Phase 1: Candidate Retrieval
Retrieve candidates from three sources in parallel:
1. **Full-Text Search (FTS)**
   - SQLite: FTS5 with BM25 ranking
   - PostgreSQL: tsvector with ts_rank
   - Returns top-k keyword matches

2. **Dense Vector Search**
   - Semantic similarity using embeddings
   - Cosine similarity calculation
   - Returns top-k semantically similar resources

3. **Sparse Vector Search**
   - BGE-M3 model for learned keyword importance
   - Sparse dot product similarity
   - Returns top-k keyword-weighted matches

#### Phase 2: Fusion
Combine candidates using Reciprocal Rank Fusion (RRF):
```python
score(d) = Σ(w_i / (k + rank_i(d)))
```
- Adaptive weights based on query characteristics
- Configurable k parameter (default: 60)
- Handles missing candidates gracefully

#### Phase 3: Reranking
ColBERT cross-encoder for final ranking:
- Deep semantic matching
- Query-document interaction
- Top-N reranking (default: 100)

## Events

### Emitted Events
None currently. Future events may include:
- `search.performed` - Search analytics
- `search.zero_results` - Query refinement suggestions

### Subscribed Events
None currently. Search is a read-only module.

## Dependencies

### Shared Kernel
- `shared.database`: Database session management
- `shared.embeddings`: Embedding generation for queries

### External Libraries
- `sentence-transformers`: ColBERT reranking
- `transformers`: BGE-M3 sparse embeddings
- `torch`: Neural model inference
- `numpy`: Vector operations
- `faiss`: Vector similarity (optional)

## Usage Examples

### Basic Search
```python
from app.modules.search import SearchService, SearchQuery

service = SearchService(db)
query = SearchQuery(
    text="machine learning",
    limit=20
)
results = await service.search(query)
```

### Hybrid Search with Custom Weights
```python
from app.modules.search import HybridWeights

query = SearchQuery(
    text="neural networks",
    limit=10,
    hybrid_weights=HybridWeights(
        keyword=0.3,
        dense=0.4,
        sparse=0.3
    ),
    enable_reranking=True
)
results = await service.hybrid_search(query)
```

### Faceted Search
```python
from app.modules.search import SearchFilters

query = SearchQuery(
    text="deep learning",
    filters=SearchFilters(
        tags=["ai", "ml"],
        min_quality=0.7,
        classifications=["cs.AI"]
    )
)
results = await service.search(query)
```

### Get Search Facets
```python
facets = await service.get_facets(query="machine learning")
# Returns: {tags: [...], classifications: [...], quality_ranges: [...]}
```

## Search Strategies

### Keyword Search (FTS)
- Best for: Exact term matching, technical terms, acronyms
- Speed: < 50ms for typical queries
- Database-specific implementation

### Semantic Search (Dense Vectors)
- Best for: Conceptual similarity, paraphrases, synonyms
- Speed: < 100ms for 10k resources
- Uses sentence-transformers embeddings

### Sparse Search (BGE-M3)
- Best for: Learned keyword importance, domain-specific terms
- Speed: < 100ms for 10k resources
- Combines benefits of keyword and semantic

### Hybrid Search (Three-Way)
- Best for: General-purpose search, unknown query types
- Speed: < 500ms with reranking
- Adaptive weighting based on query characteristics

## Configuration

### Environment Variables
```bash
# Hybrid search weights
HYBRID_WEIGHT_KEYWORD=0.3
HYBRID_WEIGHT_DENSE=0.4
HYBRID_WEIGHT_SPARSE=0.3

# Reranking
ENABLE_RERANKING=true
RERANK_TOP_N=100

# Performance
SEARCH_CACHE_TTL=300
MAX_SEARCH_RESULTS=1000
```

### Query-Adaptive Weighting
Automatically adjusts weights based on:
- Query length (short vs long)
- Query type (question vs keywords)
- Presence of technical terms
- Historical performance

## Performance Benchmarks

| Search Type | Latency (p95) | Throughput |
|-------------|---------------|------------|
| Keyword     | < 50ms        | 200 qps    |
| Semantic    | < 100ms       | 100 qps    |
| Sparse      | < 100ms       | 100 qps    |
| Hybrid      | < 300ms       | 50 qps     |
| Hybrid+Rerank | < 500ms     | 30 qps     |

## Testing

### Unit Tests
```bash
pytest backend/tests/modules/test_search_endpoints.py -v
```

### Strategy Tests
```bash
pytest backend/app/modules/search/tests/test_strategies.py -v
```

### Integration Tests
```bash
pytest backend/tests/integration/ -k search -v
```

### Test Coverage
- Keyword search accuracy
- Semantic search relevance
- Hybrid fusion correctness
- Reranking effectiveness
- Facet generation
- Error handling

## Troubleshooting

### Issue: Slow Search Performance
**Solution**: 
- Enable caching for frequent queries
- Reduce reranking top-N parameter
- Add database indexes on search fields
- Use connection pooling

### Issue: Poor Semantic Search Results
**Solution**:
- Verify embeddings are generated for all resources
- Check embedding model is loaded correctly
- Increase embedding dimensions
- Retrain embeddings on domain-specific data

### Issue: FTS Returns No Results
**Solution**:
- Check FTS index is built (SQLite: FTS5, PostgreSQL: tsvector)
- Verify search_vector column is populated
- Check query syntax (no special characters)
- Try semantic search as fallback

### Issue: Hybrid Search Weights Not Applied
**Solution**:
- Verify weights sum to 1.0
- Check adaptive weighting is not overriding
- Disable adaptive weighting for testing
- Log intermediate scores for debugging

## Related Modules

- **Resources**: Source of searchable content
- **Collections**: Search within collections
- **Quality**: Quality scores influence ranking
- **Taxonomy**: Classifications used for faceting
- **Recommendations**: Search results feed recommendations

## Future Enhancements

- Elasticsearch integration for large-scale deployments
- Query expansion and spell correction
- Personalized search ranking
- Search analytics and query logging
- Multi-language search support
- Voice search integration

## Version History

- **1.0.0** (Phase 14): Initial extraction from layered architecture
  - Moved from `routers/search.py` and `services/search_service.py`
  - Implemented three-way hybrid search
  - Added ColBERT reranking
  - Implemented module isolation

## Module Metadata

- **Version**: 1.0.0
- **Domain**: search
- **Phase**: 14 (Complete Vertical Slice Refactor)
