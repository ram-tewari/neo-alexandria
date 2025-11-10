# RerankingService Usage Guide

## Overview
The RerankingService provides ColBERT-style cross-encoder reranking for search results. It refines the ranking of candidate documents by computing query-document relevance scores using a neural cross-encoder model.

## Basic Usage

### 1. Initialize the Service

```python
from sqlalchemy.orm import Session
from app.services.reranking_service import RerankingService

# With default model (cross-encoder/ms-marco-MiniLM-L-6-v2)
reranker = RerankingService(db)

# With custom model
reranker = RerankingService(
    db,
    model_name="cross-encoder/ms-marco-electra-base",
    max_length=1000  # Use more document content
)
```

### 2. Rerank Candidates

```python
# Basic reranking
query = "machine learning algorithms"
candidate_ids = ["uuid1", "uuid2", "uuid3", ...]  # Resource IDs

results = reranker.rerank(
    query=query,
    candidates=candidate_ids,
    top_k=20  # Return top 20 results
)

# Results: [(resource_id, relevance_score), ...]
for resource_id, score in results:
    print(f"Resource {resource_id}: {score:.4f}")
```

### 3. Rerank with Caching

```python
# Create a cache dictionary
cache = {}

# First call - performs reranking
results1 = reranker.rerank_with_caching(
    query="neural networks",
    candidates=candidate_ids,
    top_k=20,
    cache=cache
)

# Second call with same query - uses cache (much faster)
results2 = reranker.rerank_with_caching(
    query="neural networks",
    candidates=candidate_ids,
    top_k=20,
    cache=cache
)

# results1 == results2, but second call is faster
```

### 4. Rerank with Timeout

```python
# Set timeout to prevent long-running operations
results = reranker.rerank(
    query="complex query",
    candidates=large_candidate_list,
    top_k=20,
    timeout=1.0  # 1 second timeout
)

# Returns empty list if timeout exceeded before prediction
# Returns results if timeout exceeded after prediction
```

## Advanced Usage

### Custom Cache Implementation

```python
from cachetools import TTLCache

# Use TTL cache with 1-hour expiration
cache = TTLCache(maxsize=1000, ttl=3600)

results = reranker.rerank_with_caching(
    query=query,
    candidates=candidates,
    cache=cache
)
```

### Batch Reranking Multiple Queries

```python
queries = [
    "machine learning",
    "deep learning",
    "neural networks"
]

all_results = {}
for query in queries:
    results = reranker.rerank(query, candidates, top_k=10)
    all_results[query] = results
```

### Integration with Search Pipeline

```python
from app.services.search_service import AdvancedSearchService
from app.services.reciprocal_rank_fusion_service import ReciprocalRankFusionService

# 1. Get candidates from multiple retrieval methods
fts5_results = search_service.search_fts5(query, limit=100)
dense_results = search_service.search_dense(query, limit=100)
sparse_results = search_service.search_sparse(query, limit=100)

# 2. Fuse results using RRF
rrf_service = ReciprocalRankFusionService()
fused_results = rrf_service.fuse_results([
    fts5_results,
    dense_results,
    sparse_results
])

# 3. Rerank top candidates
candidate_ids = [resource_id for resource_id, _ in fused_results[:100]]
reranked_results = reranker.rerank(query, candidate_ids, top_k=20)

# 4. Fetch final resources
final_resources = []
for resource_id, score in reranked_results:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource:
        final_resources.append(resource)
```

## Performance Considerations

### GPU vs CPU
```python
# Check device being used
if reranker._ensure_loaded():
    print(f"Using device: {reranker._device}")
    # Output: "cuda" or "cpu"
```

### Batch Size Recommendations
- **GPU:** Can handle 100+ candidates efficiently
- **CPU:** Best with 20-50 candidates at a time
- **Large batches:** May cause GPU OOM, automatic CPU fallback

### Latency Expectations
- **GPU:** ~100-200ms for 100 candidates
- **CPU:** ~500-1000ms for 100 candidates
- **Cached:** <1ms for cache hits

### Memory Usage
- **Model:** ~90MB (ms-marco-MiniLM-L-6-v2)
- **GPU Memory:** ~500MB-1GB during inference
- **CPU Memory:** ~200-500MB

## Error Handling

### Model Not Available
```python
results = reranker.rerank(query, candidates)
if not results:
    # Model may not be available or dependencies missing
    # Fall back to non-reranked results
    print("Reranking unavailable, using original ranking")
```

### GPU Out of Memory
```python
# Automatic CPU fallback on GPU OOM
# Check logs for warnings:
# "GPU OOM during reranking, falling back to CPU"
```

### Empty Results
```python
# Returns empty list if:
# - Query is empty
# - Candidates list is empty
# - No resources found for candidate IDs
# - Model loading fails

results = reranker.rerank("", candidates)
assert results == []
```

## Best Practices

### 1. Rerank Only Top Candidates
```python
# Don't rerank all results - too expensive
# Rerank top 100-200 candidates from initial retrieval
candidates = initial_results[:100]
reranked = reranker.rerank(query, candidates, top_k=20)
```

### 2. Use Caching for Repeated Queries
```python
# Cache results for common queries
cache = {}
results = reranker.rerank_with_caching(query, candidates, cache=cache)
```

### 3. Set Reasonable Timeouts
```python
# Prevent long-running operations
results = reranker.rerank(query, candidates, timeout=2.0)
```

### 4. Monitor Performance
```python
import time

start = time.time()
results = reranker.rerank(query, candidates)
elapsed = time.time() - start

print(f"Reranking took {elapsed*1000:.1f}ms")
if elapsed > 1.0:
    print("Warning: Reranking is slow, consider reducing candidates")
```

### 5. Handle Failures Gracefully
```python
try:
    results = reranker.rerank(query, candidates)
    if not results:
        # Fall back to original ranking
        results = [(cid, 0.0) for cid in candidates[:20]]
except Exception as e:
    logger.error(f"Reranking failed: {e}")
    # Use original ranking
    results = [(cid, 0.0) for cid in candidates[:20]]
```

## Configuration

### Model Selection
```python
# Fast and lightweight (default)
reranker = RerankingService(db, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

# Higher quality, slower
reranker = RerankingService(db, model_name="cross-encoder/ms-marco-electra-base")

# Multi-lingual
reranker = RerankingService(db, model_name="cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
```

### Document Length
```python
# Use more document content (slower but more accurate)
reranker = RerankingService(db, max_length=1000)

# Use less content (faster but may miss relevant info)
reranker = RerankingService(db, max_length=200)
```

## Troubleshooting

### Issue: Model Not Loading
**Symptoms:** Returns empty results, logs "Model not available"

**Solutions:**
1. Install dependencies: `pip install sentence-transformers torch`
2. Check internet connection (first-time model download)
3. Check disk space (~90MB needed)
4. Check logs for specific error messages

### Issue: GPU Out of Memory
**Symptoms:** Logs "GPU OOM during reranking"

**Solutions:**
1. Reduce number of candidates
2. Use smaller model
3. Reduce max_length parameter
4. Service automatically falls back to CPU

### Issue: Slow Performance
**Symptoms:** Reranking takes >1 second

**Solutions:**
1. Reduce number of candidates
2. Use GPU if available
3. Enable caching for repeated queries
4. Use smaller model (MiniLM vs electra-base)
5. Reduce max_length parameter

### Issue: Poor Ranking Quality
**Symptoms:** Reranked results don't seem relevant

**Solutions:**
1. Use larger model (electra-base instead of MiniLM)
2. Increase max_length to use more document content
3. Check that query and documents are in same language
4. Verify resources have meaningful title/description

## API Reference

### RerankingService.__init__()
```python
def __init__(
    self,
    db: Session,
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    max_length: int = 500
)
```
Initialize the reranking service.

**Parameters:**
- `db`: Database session for resource operations
- `model_name`: Hugging Face cross-encoder model identifier
- `max_length`: Maximum characters to use from document content

### RerankingService.rerank()
```python
def rerank(
    self,
    query: str,
    candidates: List[str],
    top_k: int = 20,
    timeout: Optional[float] = None
) -> List[Tuple[str, float]]
```
Rerank candidates using cross-encoder model.

**Parameters:**
- `query`: Search query text
- `candidates`: List of resource IDs to rerank
- `top_k`: Number of top results to return
- `timeout`: Optional timeout in seconds

**Returns:**
- List of (resource_id, relevance_score) tuples sorted by score descending

### RerankingService.rerank_with_caching()
```python
def rerank_with_caching(
    self,
    query: str,
    candidates: List[str],
    top_k: int = 20,
    cache: Optional[Dict[str, List[Tuple[str, float]]]] = None,
    timeout: Optional[float] = None
) -> List[Tuple[str, float]]
```
Rerank with optional result caching.

**Parameters:**
- `query`: Search query text
- `candidates`: List of resource IDs to rerank
- `top_k`: Number of top results to return
- `cache`: Optional cache dictionary to use
- `timeout`: Optional timeout in seconds

**Returns:**
- List of (resource_id, relevance_score) tuples sorted by score descending

## Examples

### Example 1: Basic Search with Reranking
```python
from app.services.search_service import AdvancedSearchService
from app.services.reranking_service import RerankingService

# Get initial candidates
search_service = AdvancedSearchService()
initial_results = search_service.hybrid_search(db, query, limit=100)

# Rerank top candidates
reranker = RerankingService(db)
candidate_ids = [r.id for r in initial_results]
reranked = reranker.rerank(query, candidate_ids, top_k=20)

# Fetch final resources
final_resources = []
for resource_id, score in reranked:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource:
        final_resources.append((resource, score))
```

### Example 2: Cached Reranking for API
```python
from fastapi import APIRouter, Depends
from cachetools import TTLCache

router = APIRouter()
reranking_cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour TTL

@router.get("/search")
def search(query: str, db: Session = Depends(get_db)):
    # Get candidates
    candidates = get_search_candidates(db, query)
    
    # Rerank with caching
    reranker = RerankingService(db)
    results = reranker.rerank_with_caching(
        query=query,
        candidates=candidates,
        top_k=20,
        cache=reranking_cache
    )
    
    return {"results": results}
```

### Example 3: A/B Testing Reranking
```python
import random

def search_with_ab_test(db, query, enable_reranking_prob=0.5):
    # Get candidates
    candidates = get_search_candidates(db, query)
    
    # Randomly enable reranking for A/B testing
    use_reranking = random.random() < enable_reranking_prob
    
    if use_reranking:
        reranker = RerankingService(db)
        results = reranker.rerank(query, candidates, top_k=20)
        variant = "reranked"
    else:
        results = [(cid, 0.0) for cid in candidates[:20]]
        variant = "baseline"
    
    # Log for analysis
    log_search_event(query, variant, results)
    
    return results, variant
```

## Related Documentation
- [Phase 8 Design Document](../specs/phase8-three-way-hybrid-search/design.md)
- [Phase 8 Requirements](../specs/phase8-three-way-hybrid-search/requirements.md)
- [SearchService Documentation](search_service_usage.md)
- [RRF Service Documentation](rrf_service_usage.md)
