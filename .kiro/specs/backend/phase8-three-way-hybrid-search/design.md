# Phase 8: Three-Way Hybrid Search with Reranking - Design Document

## Overview

Phase 8 implements a state-of-the-art three-way hybrid search system that combines full-text search (FTS5), dense vector search, and sparse vector search with Reciprocal Rank Fusion (RRF) for result merging and ColBERT-style reranking for optimal precision. This represents a significant advancement over the current two-way hybrid search (FTS5 + dense vectors) by adding learned keyword representations through sparse vectors and sophisticated result fusion.

### Key Innovations

1. **Sparse Vector Embeddings**: Learned keyword representations that capture term importance beyond traditional TF-IDF
2. **Three-Way Retrieval**: Parallel execution of FTS5, dense, and sparse methods for comprehensive coverage
3. **Reciprocal Rank Fusion**: Score-agnostic result merging that handles heterogeneous scoring functions
4. **Query-Adaptive Weighting**: Automatic adjustment of retrieval method importance based on query characteristics
5. **ColBERT Reranking**: Neural reranking of top candidates for maximum precision

### Performance Targets

- Query latency: <200ms at 95th percentile
- Sparse embedding generation: <1 second per resource
- Reranking throughput: >100 documents/second
- nDCG improvement: 30%+ over two-way hybrid baseline

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Search Request                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SearchService (Orchestrator)                  │
│  - Query analysis                                                │
│  - Parallel retrieval coordination                               │
│  - Result fusion and reranking                                   │
└─────┬──────────────┬──────────────┬─────────────────────────────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│   FTS5   │  │  Dense   │  │  Sparse  │
│  Search  │  │  Vector  │  │  Vector  │
│          │  │  Search  │  │  Search  │
└──────────┘  └──────────┘  └──────────┘
      │              │              │
      └──────────────┴──────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              RRF Service (Result Fusion)                         │
│  - Compute reciprocal rank scores                                │
│  - Apply query-adaptive weights                                  │
│  - Merge and sort results                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           RerankingService (ColBERT Reranking)                   │
│  - Cross-encoder relevance scoring                               │
│  - Top-K selection                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Final Results                               │
└─────────────────────────────────────────────────────────────────┘
```


### Data Flow

1. **Query Input**: User submits search query with optional filters
2. **Query Analysis**: Analyze query characteristics (length, type, technical indicators)
3. **Parallel Retrieval**: Execute three retrieval methods simultaneously
   - FTS5: Keyword matching with BM25 scoring
   - Dense: Semantic similarity using existing embeddings
   - Sparse: Learned keyword matching using sparse vectors
4. **Result Fusion**: Merge results using RRF with adaptive weights
5. **Reranking** (optional): Apply ColBERT cross-encoder to top-100 candidates
6. **Response**: Return ranked results with metadata

## Components and Interfaces

### 1. Resource Model Extension

**Purpose**: Store sparse vector embeddings alongside existing dense embeddings

**Schema Changes**:
```python
class Resource(Base):
    # ... existing fields ...
    
    # NEW FIELDS for Phase 8
    sparse_embedding: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True
    )  # JSON string: {"token_id": weight, ...}
    
    sparse_embedding_model: Mapped[str | None] = mapped_column(
        String(100), 
        nullable=True
    )  # Model name: "bge-m3" or "splade"
    
    sparse_embedding_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
```

**Design Decisions**:
- Store as JSON string (not binary) for portability and debugging
- Nullable fields for backward compatibility
- Track model version for future upgrades
- Separate timestamp for batch processing tracking

**Indexes**:
```sql
CREATE INDEX idx_resources_sparse_updated 
ON resources(sparse_embedding_updated_at);
```

### 2. SparseEmbeddingService

**Purpose**: Generate and manage sparse vector embeddings using BGE-M3 model

**Interface**:
```python
class SparseEmbeddingService:
    def __init__(self, db: Session, model_name: str = "BAAI/bge-m3")
    
    def generate_sparse_embedding(self, text: str) -> Dict[int, float]
    """Generate sparse vector for single text"""
    
    def generate_sparse_embeddings_batch(
        self, texts: List[str]
    ) -> List[Dict[int, float]]
    """Batch generate for efficiency"""
    
    def search_by_sparse_vector(
        self, 
        query_sparse: Dict[int, float],
        limit: int = 100,
        min_score: float = 0.0
    ) -> List[Tuple[str, float]]
    """Search resources using sparse similarity"""
    
    def update_resource_sparse_embedding(self, resource_id: str)
    """Generate and store sparse embedding for one resource"""
    
    def batch_update_sparse_embeddings(
        self, resource_ids: List[str] = None
    )
    """Batch update for multiple resources"""
```


**Sparse Vector Generation Algorithm**:
```
1. Tokenize input text (max 512 tokens)
2. Forward pass through BGE-M3 model
3. Extract sparse representation layer
4. Apply ReLU + log transformation (SPLADE-style)
5. Select top-200 non-zero dimensions
6. Normalize weights to [0, 1]
7. Return as dict {token_id: weight}
```

**Model Selection**: BGE-M3 (BAAI/bge-m3)
- Multi-functionality: dense + sparse + ColBERT in one model
- State-of-the-art performance on BEIR benchmark
- Efficient inference (similar speed to dense-only models)
- Unified architecture simplifies deployment

**Sparse Vector Format**:
```json
{
  "2453": 0.87,
  "8921": 0.65,
  "1234": 0.43,
  ...
}
```
- Keys: Token IDs from model vocabulary
- Values: Normalized weights [0, 1]
- Typical size: 50-200 non-zero entries
- Storage: ~2-5KB per resource as JSON

**Search Algorithm**:
```
1. Generate query sparse vector
2. For each resource with sparse embedding:
   a. Parse JSON to dict
   b. Compute sparse dot product (only overlapping dimensions)
   c. Accumulate score
3. Sort by score descending
4. Return top-K results
```

**Optimization Notes**:
- For databases >100K resources, implement inverted index
- Current linear scan acceptable for <100K resources
- GPU acceleration for batch generation
- CPU fallback for single-document generation

### 3. ReciprocalRankFusionService

**Purpose**: Merge results from multiple retrieval methods using RRF algorithm

**Interface**:
```python
class ReciprocalRankFusionService:
    def __init__(self, k: int = 60)
    
    def fuse_results(
        self,
        result_lists: List[List[Tuple[str, float]]],
        weights: List[float] = None
    ) -> List[Tuple[str, float]]
    """Merge multiple ranked lists using RRF"""
    
    def adaptive_weights(
        self,
        query: str,
        result_lists: List[List[Tuple[str, float]]]
    ) -> List[float]
    """Compute query-adaptive weights"""
```

**RRF Algorithm**:
```
For each document d:
    RRF_score(d) = Σ [weight_i / (k + rank_i(d))]

where:
- rank_i(d) = rank of document d in result list i (0-indexed)
- weight_i = importance weight for result list i
- k = constant (typically 60) that reduces impact of high ranks
```

**Why RRF?**
- Score-agnostic: Works with heterogeneous scoring functions
- No normalization needed: FTS5 BM25 scores vs cosine similarity
- Simple and effective: Proven in TREC competitions
- Robust: Less sensitive to outliers than score-based fusion

**Query-Adaptive Weighting Heuristics**:

| Query Characteristic | Weight Adjustment |
|---------------------|-------------------|
| Short (1-3 words) | FTS5 × 1.5, Dense × 0.8 |
| Long (>10 words) | Dense × 1.5, FTS5 × 0.8 |
| Question (who/what/when/where/why/how) | Dense × 1.3 |
| Technical (code, math symbols) | Sparse × 1.5, Dense × 0.9 |

Weights are normalized to sum to 1.0 after adjustment.


### 4. RerankingService

**Purpose**: Apply ColBERT-style cross-encoder reranking for maximum precision

**Interface**:
```python
class RerankingService:
    def __init__(
        self, 
        db: Session, 
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )
    
    def rerank(
        self,
        query: str,
        candidates: List[str],  # Resource IDs
        top_k: int = 20
    ) -> List[Tuple[str, float]]
    """Rerank candidates using cross-encoder"""
    
    def rerank_with_caching(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 20,
        cache: Dict = None
    ) -> List[Tuple[str, float]]
    """Rerank with optional result caching"""
```

**Reranking Algorithm**:
```
1. Fetch resource content for candidate IDs
2. Build (query, document) pairs
   - Use title + first 500 chars of content
3. Batch predict relevance scores using cross-encoder
4. Sort by relevance score descending
5. Return top-K results
```

**Model Selection**: cross-encoder/ms-marco-MiniLM-L-6-v2
- Fast inference: ~10ms per document on CPU
- Good quality: Trained on MS MARCO passage ranking
- Lightweight: 90MB model size
- Alternative: cross-encoder/ms-marco-electra-base (higher quality, slower)

**Why Reranking?**
- First-stage retrievals are fast but approximate
- Cross-encoders model query-document interaction directly
- Significant precision improvement at top positions
- Applied only to top-100 candidates (manageable cost)

**Performance Optimization**:
- Batch processing: Process all candidates in one forward pass
- GPU acceleration: 5-10x speedup on GPU
- Caching: Cache results for repeated queries (TTL: 1 hour)
- Limit candidates: Rerank top-100 only (not all results)

### 5. Enhanced SearchService

**Purpose**: Orchestrate three-way hybrid search with fusion and reranking

**New Method**:
```python
class AdvancedSearchService:
    # ... existing methods ...
    
    @staticmethod
    def search_three_way_hybrid(
        db: Session,
        query: SearchQuery,
        enable_reranking: bool = True,
        adaptive_weighting: bool = True
    ) -> Tuple[List[Resource], int, Facets, Dict[str, str]]:
        """Three-way hybrid search with RRF and reranking"""
```

**Algorithm**:
```
1. Query Analysis
   - Parse query text
   - Detect query characteristics (length, type, technical)

2. Parallel Retrieval (target: <150ms total)
   - FTS5 search → top 100 results
   - Dense vector search → top 100 results
   - Sparse vector search → top 100 results

3. Adaptive Weighting (if enabled)
   - Compute weights based on query characteristics
   - Default: [1.0, 1.0, 1.0] (equal weights)

4. RRF Fusion
   - Merge three result lists using RRF
   - Apply adaptive weights
   - Sort by RRF score

5. Reranking (if enabled)
   - Extract top 100 candidates
   - Apply ColBERT cross-encoder
   - Sort by relevance score
   - Return top-K

6. Fetch Resources
   - Retrieve Resource objects preserving order
   - Apply structured filters
   - Compute facets

7. Return Results
   - Resources, total count, facets, snippets
```


**Integration with Existing Search**:
- Preserve existing `search()` method for backward compatibility
- Add new `search_three_way_hybrid()` method
- Existing two-way hybrid remains available
- Gradual migration path for clients

### 6. SearchMetricsService

**Purpose**: Compute information retrieval metrics for evaluation

**Interface**:
```python
class SearchMetricsService:
    def compute_ndcg(
        self,
        ranked_results: List[str],
        relevance_judgments: Dict[str, int],
        k: int = 20
    ) -> float
    """Compute nDCG@k"""
    
    def compute_recall_at_k(
        self,
        ranked_results: List[str],
        relevant_docs: List[str],
        k: int = 20
    ) -> float
    """Compute Recall@k"""
    
    def compute_precision_at_k(
        self,
        ranked_results: List[str],
        relevant_docs: List[str],
        k: int = 20
    ) -> float
    """Compute Precision@k"""
    
    def compute_mean_reciprocal_rank(
        self,
        ranked_results: List[str],
        relevant_docs: List[str]
    ) -> float
    """Compute MRR"""
```

**Metrics Explained**:

**nDCG (Normalized Discounted Cumulative Gain)**:
```
DCG@k = Σ [(2^rel_i - 1) / log2(i + 1)]
nDCG@k = DCG@k / IDCG@k

where:
- rel_i = relevance score of document at position i (0-3 scale)
- IDCG@k = ideal DCG (perfect ranking)
```
- Measures ranking quality considering position and relevance
- Range: [0, 1], higher is better
- Target: >0.7 for excellent search quality

**Recall@K**:
```
Recall@k = (# relevant docs in top-k) / (total # relevant docs)
```
- Measures retrieval completeness
- Range: [0, 1], higher is better

**Precision@K**:
```
Precision@k = (# relevant docs in top-k) / k
```
- Measures retrieval accuracy
- Range: [0, 1], higher is better

**MRR (Mean Reciprocal Rank)**:
```
MRR = 1 / (rank of first relevant document)
```
- Measures how quickly a relevant result appears
- Range: [0, 1], higher is better

## Data Models

### Sparse Embedding Storage

**Format**: JSON string in `Resource.sparse_embedding`
```json
{
  "2453": 0.87,
  "8921": 0.65,
  "1234": 0.43
}
```

**Size Estimates**:
- Typical sparse vector: 50-200 non-zero dimensions
- JSON size: ~2-5KB per resource
- For 100K resources: ~200-500MB total

**Alternative Considered**: Binary format (pickle, msgpack)
- Pros: Smaller size, faster parsing
- Cons: Not human-readable, less portable
- Decision: Use JSON for Phase 8, consider binary in future if needed

### Search Result Format

**Three-Way Hybrid Response**:
```python
{
    "results": List[Resource],
    "total": int,
    "facets": Facets,
    "snippets": Dict[str, str],
    "latency_ms": float,
    "method_contributions": {
        "fts5": int,  # Count of results from FTS5
        "dense": int,  # Count from dense vectors
        "sparse": int  # Count from sparse vectors
    },
    "weights_used": [float, float, float]  # Applied RRF weights
}
```


## Error Handling

### Model Loading Failures

**Scenario**: BGE-M3 or cross-encoder model fails to load

**Handling**:
```python
try:
    self._model = AutoModel.from_pretrained(self.model_name)
except Exception as e:
    logger.error(f"Failed to load model {self.model_name}: {e}")
    self._model = None
    # Fall back to two-way hybrid (skip sparse/reranking)
```

**Fallback Strategy**:
- Sparse embedding generation fails → Skip sparse search, use two-way hybrid
- Reranking model fails → Return RRF results without reranking
- Both fail → Fall back to existing two-way hybrid search

### Sparse Embedding Generation Failures

**Scenario**: Individual resource fails during sparse embedding generation

**Handling**:
```python
try:
    sparse_vec = self.generate_sparse_embedding(resource.content)
    resource.sparse_embedding = json.dumps(sparse_vec)
except Exception as e:
    logger.warning(f"Sparse embedding failed for {resource.id}: {e}")
    # Continue without sparse embedding for this resource
    resource.sparse_embedding = None
```

**Recovery**:
- Log error with resource ID
- Mark resource for retry in next batch update
- Don't block ingestion pipeline

### Search-Time Failures

**Scenario**: One retrieval method fails during search

**Handling**:
```python
try:
    fts5_results = self._search_fts5(query, limit=100)
except Exception as e:
    logger.error(f"FTS5 search failed: {e}")
    fts5_results = []  # Empty list, continue with other methods

# Continue with dense and sparse...
# RRF handles empty lists gracefully
```

**Graceful Degradation**:
- If FTS5 fails → Use dense + sparse only
- If dense fails → Use FTS5 + sparse only
- If sparse fails → Fall back to two-way hybrid
- If all fail → Return empty results with error message

### GPU Out of Memory

**Scenario**: GPU runs out of memory during batch processing

**Handling**:
```python
try:
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
except RuntimeError as e:
    if "out of memory" in str(e):
        logger.warning("GPU OOM, falling back to CPU")
        torch.cuda.empty_cache()
        # Retry on CPU
        inputs = {k: v.cpu() for k, v in inputs.items()}
```

**Mitigation**:
- Reduce batch size dynamically
- Clear GPU cache between batches
- Fall back to CPU processing

## Testing Strategy

### Unit Tests

**SparseEmbeddingService**:
- `test_generate_sparse_embedding`: Verify format and size
- `test_sparse_embedding_normalization`: Check weights in [0, 1]
- `test_sparse_search`: Verify similarity computation
- `test_batch_generation`: Check batch processing efficiency
- `test_model_loading_failure`: Verify graceful fallback

**ReciprocalRankFusionService**:
- `test_rrf_basic_fusion`: Verify RRF formula
- `test_rrf_with_weights`: Check weighted fusion
- `test_adaptive_weights_short_query`: Verify FTS5 boost
- `test_adaptive_weights_long_query`: Verify dense boost
- `test_adaptive_weights_technical`: Verify sparse boost
- `test_empty_result_lists`: Handle edge cases

**RerankingService**:
- `test_colbert_reranking`: Verify relevance scoring
- `test_reranking_performance`: Check throughput >100 docs/sec
- `test_reranking_with_caching`: Verify cache hits
- `test_model_loading_failure`: Verify fallback

**SearchMetricsService**:
- `test_compute_ndcg`: Verify nDCG calculation
- `test_compute_recall`: Verify recall calculation
- `test_compute_precision`: Verify precision calculation
- `test_compute_mrr`: Verify MRR calculation


### Integration Tests

**Three-Way Hybrid Search**:
- `test_three_way_search_combines_methods`: Verify all methods contribute
- `test_three_way_vs_two_way`: Compare quality improvement
- `test_search_with_reranking`: Verify reranking improves results
- `test_search_latency`: Verify <200ms at p95
- `test_adaptive_weighting_improves_results`: Measure quality gain

**API Endpoints**:
- `test_three_way_hybrid_api`: GET /search/three-way-hybrid
- `test_compare_methods_api`: GET /search/compare-methods
- `test_evaluate_api`: POST /search/evaluate

### Performance Tests

**Latency Benchmarks**:
```python
def test_search_latency_p95():
    """Verify 95th percentile latency <200ms"""
    latencies = []
    for query in test_queries:
        start = time.time()
        results = search_service.search_three_way_hybrid(db, query)
        latency = (time.time() - start) * 1000
        latencies.append(latency)
    
    p95 = np.percentile(latencies, 95)
    assert p95 < 200, f"P95 latency {p95}ms exceeds 200ms target"
```

**Throughput Benchmarks**:
```python
def test_reranking_throughput():
    """Verify reranking >100 docs/second"""
    candidates = [f"doc_{i}" for i in range(100)]
    
    start = time.time()
    results = reranking_service.rerank(query, candidates, top_k=20)
    elapsed = time.time() - start
    
    throughput = 100 / elapsed
    assert throughput > 100, f"Throughput {throughput} docs/sec below target"
```

### Quality Tests

**nDCG Improvement**:
```python
def test_ndcg_improvement():
    """Verify 30%+ nDCG improvement over baseline"""
    # Requires test dataset with relevance judgments
    
    # Baseline: two-way hybrid
    baseline_results = search_service.hybrid_search(db, query)
    baseline_ndcg = metrics_service.compute_ndcg(
        [r.id for r in baseline_results],
        relevance_judgments,
        k=20
    )
    
    # Phase 8: three-way hybrid
    phase8_results = search_service.search_three_way_hybrid(db, query)
    phase8_ndcg = metrics_service.compute_ndcg(
        [r.id for r in phase8_results],
        relevance_judgments,
        k=20
    )
    
    improvement = (phase8_ndcg - baseline_ndcg) / baseline_ndcg
    assert improvement >= 0.30, f"nDCG improvement {improvement:.1%} below 30% target"
```

## Performance Optimization

### Parallel Retrieval

**Current**: Sequential execution
```python
fts5_results = self._search_fts5(query, limit=100)
dense_results = self._search_dense(query, limit=100)
sparse_results = self._search_sparse(query, limit=100)
```

**Optimized**: Parallel execution using asyncio
```python
import asyncio

async def parallel_retrieval(query):
    tasks = [
        asyncio.to_thread(self._search_fts5, query, limit=100),
        asyncio.to_thread(self._search_dense, query, limit=100),
        asyncio.to_thread(self._search_sparse, query, limit=100)
    ]
    results = await asyncio.gather(*tasks)
    return results

fts5_results, dense_results, sparse_results = asyncio.run(parallel_retrieval(query))
```

**Expected Speedup**: 2-3x (from ~150ms sequential to ~50-75ms parallel)

### Sparse Vector Indexing

**Current**: Linear scan through all resources
```python
for resource in resources:
    score = sparse_dot_product(query_sparse, resource_sparse)
```

**Optimized**: Inverted index (for >100K resources)
```python
# Build inverted index: token_id → [(resource_id, weight), ...]
inverted_index = defaultdict(list)
for resource in resources:
    for token_id, weight in resource.sparse_embedding.items():
        inverted_index[token_id].append((resource.id, weight))

# Search using inverted index
scores = defaultdict(float)
for token_id, query_weight in query_sparse.items():
    for resource_id, resource_weight in inverted_index[token_id]:
        scores[resource_id] += query_weight * resource_weight
```

**Expected Speedup**: 10-100x for large databases


### Caching Strategy

**Query Result Caching**:
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_search(query_hash: str, filters_hash: str):
    # Cache search results for 5 minutes
    pass

# Usage
query_hash = hashlib.md5(query.encode()).hexdigest()
filters_hash = hashlib.md5(str(filters).encode()).hexdigest()
results = cached_search(query_hash, filters_hash)
```

**Sparse Embedding Caching**:
- Cache in memory during batch processing
- Avoid redundant model loading
- Clear cache after batch completion

**Reranking Result Caching**:
```python
# Cache reranking results for 1 hour
reranking_cache = TTLCache(maxsize=500, ttl=3600)

cache_key = f"{query}|{sorted(candidates)}"
if cache_key in reranking_cache:
    return reranking_cache[cache_key]
```

### GPU Acceleration

**Sparse Embedding Generation**:
```python
if torch.cuda.is_available():
    self._model = self._model.cuda()
    inputs = {k: v.cuda() for k, v in inputs.items()}
```

**Expected Speedup**: 5-10x for batch processing

**Reranking**:
```python
# Cross-encoder automatically uses GPU if available
self._model = CrossEncoder(model_name, device='cuda' if torch.cuda.is_available() else 'cpu')
```

**Expected Speedup**: 5-10x for reranking 100 documents

## Migration Strategy

### Phase 1: Database Migration

1. Create Alembic migration for new fields
2. Run migration on development database
3. Verify backward compatibility (existing queries work)
4. Test rollback procedure

### Phase 2: Sparse Embedding Generation

1. Deploy SparseEmbeddingService
2. Create admin endpoint for batch generation
3. Run batch update for existing resources (background job)
4. Monitor progress and error rates
5. Verify sparse embeddings stored correctly

### Phase 3: Search Service Enhancement

1. Deploy RRF and Reranking services
2. Add new search_three_way_hybrid method
3. Keep existing search methods unchanged
4. Deploy to staging environment
5. Run A/B tests comparing two-way vs three-way

### Phase 4: API Rollout

1. Add new /search/three-way-hybrid endpoint
2. Keep existing /search endpoint unchanged
3. Add /search/compare-methods for debugging
4. Add /search/evaluate for quality measurement
5. Document new endpoints in API docs

### Phase 5: Integration

1. Update ingestion pipeline to generate sparse embeddings
2. Add background task for new resources
3. Monitor sparse embedding generation success rate
4. Set up alerts for failures

### Phase 6: Monitoring and Optimization

1. Track query latency metrics (p50, p95, p99)
2. Monitor nDCG improvements
3. Analyze query patterns for adaptive weighting tuning
4. Optimize based on production data

## Dependencies

### New Python Packages

```txt
transformers>=4.35.0  # For BGE-M3 model
torch>=2.0.0  # Neural network inference
sentence-transformers>=2.2.0  # For cross-encoder reranking
faiss-cpu>=1.7.4  # Optional: for sparse vector indexing
numpy>=1.24.0  # Already installed, for vector operations
```

### Model Downloads

**BGE-M3** (~2GB):
```python
from transformers import AutoModel, AutoTokenizer
model = AutoModel.from_pretrained("BAAI/bge-m3")
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
```

**Cross-Encoder** (~90MB):
```python
from sentence_transformers import CrossEncoder
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
```

**First-Time Setup**:
- Models downloaded to `~/.cache/huggingface/`
- Requires internet connection for initial download
- Subsequent runs use cached models


## API Endpoints

### GET /search/three-way-hybrid

**Purpose**: Execute three-way hybrid search with RRF and reranking

**Query Parameters**:
```
query: str (required) - Search query text
limit: int = 20 - Number of results to return
offset: int = 0 - Pagination offset
enable_reranking: bool = true - Apply ColBERT reranking
adaptive_weighting: bool = true - Use query-adaptive RRF weights
hybrid_weight: float = 0.5 - Fusion weight (for compatibility)
```

**Response**:
```json
{
  "results": [...],
  "total": 150,
  "facets": {...},
  "snippets": {...},
  "latency_ms": 145.3,
  "method_contributions": {
    "fts5": 45,
    "dense": 38,
    "sparse": 42
  },
  "weights_used": [0.35, 0.35, 0.30]
}
```

### GET /search/compare-methods

**Purpose**: Compare different search methods side-by-side for debugging

**Query Parameters**:
```
query: str (required) - Search query text
limit: int = 20 - Number of results per method
```

**Response**:
```json
{
  "query": "machine learning",
  "methods": {
    "fts5_only": {
      "results": [...],
      "latency_ms": 25.3
    },
    "dense_only": {
      "results": [...],
      "latency_ms": 42.1
    },
    "sparse_only": {
      "results": [...],
      "latency_ms": 38.7
    },
    "two_way_hybrid": {
      "results": [...],
      "latency_ms": 67.4
    },
    "three_way_hybrid": {
      "results": [...],
      "latency_ms": 106.1
    },
    "three_way_reranked": {
      "results": [...],
      "latency_ms": 156.8
    }
  }
}
```

### POST /search/evaluate

**Purpose**: Evaluate search quality using IR metrics

**Request Body**:
```json
{
  "query": "machine learning",
  "relevance_judgments": {
    "doc_uuid_1": 3,
    "doc_uuid_2": 2,
    "doc_uuid_3": 1,
    "doc_uuid_4": 0
  }
}
```

Relevance scale: 0 (not relevant), 1 (marginally relevant), 2 (relevant), 3 (highly relevant)

**Response**:
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

### POST /admin/sparse-embeddings/generate

**Purpose**: Batch generate sparse embeddings for existing resources

**Request Body**:
```json
{
  "resource_ids": ["uuid1", "uuid2", ...],  // Optional: specific resources
  "batch_size": 32  // Optional: batch size for processing
}
```

**Response**:
```json
{
  "status": "queued",
  "job_id": "job_uuid",
  "estimated_duration_minutes": 45,
  "resources_to_process": 10000
}
```

## Security Considerations

### Input Validation

**Query Text**:
- Max length: 1000 characters
- Sanitize special characters for FTS5
- Prevent SQL injection through parameterized queries

**Resource IDs**:
- Validate UUID format
- Check resource ownership for private resources
- Rate limit batch operations

### Model Security

**Model Loading**:
- Load models from trusted sources only (Hugging Face)
- Verify model checksums
- Sandbox model execution (no arbitrary code execution)

**Resource Limits**:
- Limit batch size to prevent memory exhaustion
- Timeout long-running operations
- Monitor GPU memory usage

### API Rate Limiting

**Search Endpoints**:
- Rate limit: 100 requests/minute per user
- Burst limit: 10 requests/second
- Throttle expensive operations (reranking, batch generation)

## Monitoring and Observability

### Metrics to Track

**Performance Metrics**:
- Query latency (p50, p95, p99)
- Retrieval method latencies (FTS5, dense, sparse)
- Reranking latency
- Sparse embedding generation time

**Quality Metrics**:
- nDCG@20 (requires relevance judgments)
- Click-through rate (CTR) on search results
- Zero-result query rate
- Query refinement rate

**System Metrics**:
- GPU utilization
- Memory usage
- Model loading time
- Cache hit rates

### Logging

**Search Queries**:
```python
logger.info(
    "three_way_search",
    query=query,
    latency_ms=latency,
    results_count=len(results),
    weights_used=weights,
    reranking_enabled=enable_reranking
)
```

**Errors**:
```python
logger.error(
    "sparse_embedding_failed",
    resource_id=resource_id,
    error=str(e),
    traceback=traceback.format_exc()
)
```

### Alerts

**Performance Degradation**:
- Alert if p95 latency >300ms for 5 minutes
- Alert if sparse embedding generation fails >10% of time

**Quality Degradation**:
- Alert if zero-result rate >20%
- Alert if nDCG drops >10% from baseline

## Future Enhancements

### Phase 8.1: Inverted Index for Sparse Vectors

- Implement inverted index for sparse vector search
- Expected 10-100x speedup for large databases
- Required when database exceeds 100K resources

### Phase 8.2: Query Expansion

- Expand queries using synonyms and related terms
- Use WordNet or custom thesaurus
- Improve recall for ambiguous queries

### Phase 8.3: Learning to Rank

- Train custom ranking model on user interaction data
- Replace RRF with learned fusion weights
- Personalize ranking based on user preferences

### Phase 8.4: Multi-Modal Search

- Extend to image and table search
- Use CLIP for image embeddings
- Support mixed text + image queries

## Conclusion

Phase 8 represents a significant advancement in Neo Alexandria's search capabilities by implementing state-of-the-art three-way hybrid search with sparse vectors, RRF fusion, and ColBERT reranking. The design prioritizes performance (<200ms latency), quality (30%+ nDCG improvement), and maintainability (graceful degradation, comprehensive testing).

Key success factors:
- Parallel retrieval execution for performance
- Query-adaptive weighting for quality
- Comprehensive error handling for reliability
- Extensive testing for confidence
- Clear migration path for deployment
