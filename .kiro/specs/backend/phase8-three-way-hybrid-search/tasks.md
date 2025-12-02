# Implementation Plan

- [x] 1. Extend Resource model for sparse vector storage





  - Add sparse_embedding field (Text/JSON type) to store token-weight mappings
  - Add sparse_embedding_model field (String) to track model version
  - Add sparse_embedding_updated_at field (DateTime) for batch processing tracking
  - Create index on sparse_embedding_updated_at for efficient queries
  - _Requirements: 1.2, 1.4_

- [x] 2. Create and run database migration





  - Generate Alembic migration script for sparse embedding fields
  - Test migration upgrade and downgrade paths
  - Verify backward compatibility with existing queries
  - Run migration on development database
  - _Requirements: 1.2, 1.4_

- [x] 3. Implement SparseEmbeddingService





- [x] 3.1 Create sparse embedding generation methods


  - Implement generate_sparse_embedding() for single text
  - Implement generate_sparse_embeddings_batch() for batch processing
  - Use BGE-M3 model with lazy loading
  - Apply ReLU + log transformation and top-K selection
  - Normalize weights to [0, 1] range
  - _Requirements: 1.1, 1.3_

- [x] 3.2 Implement sparse vector search

  - Create search_by_sparse_vector() method
  - Implement sparse dot product computation
  - Support min_score filtering
  - Return sorted results by similarity score
  - _Requirements: 2.3_

- [x] 3.3 Implement resource update methods

  - Create update_resource_sparse_embedding() for single resource
  - Create batch_update_sparse_embeddings() for multiple resources
  - Handle empty content gracefully
  - Commit every 100 resources during batch processing
  - Log progress updates
  - _Requirements: 1.1, 1.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 3.4 Add error handling and fallbacks

  - Handle model loading failures gracefully
  - Fall back to CPU if GPU unavailable
  - Handle GPU out of memory errors
  - Log errors without blocking operations
  - _Requirements: 1.5_

- [x] 4. Implement ReciprocalRankFusionService





- [x] 4.1 Create RRF fusion algorithm


  - Implement fuse_results() with RRF formula: weight_i / (k + rank_i)
  - Support weighted fusion with custom weights
  - Handle empty result lists gracefully
  - Sort merged results by RRF score descending
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.2 Implement query-adaptive weighting

  - Create adaptive_weights() method
  - Detect short queries (1-3 words) and boost FTS5
  - Detect long queries (>10 words) and boost dense vectors
  - Detect technical queries (code, math) and boost sparse vectors
  - Detect question queries and boost dense vectors
  - Normalize weights to sum to 1.0
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
-

- [x] 5. Implement RerankingService




- [x] 5.1 Create ColBERT reranking methods


  - Implement rerank() using cross-encoder model
  - Fetch resource content for candidates
  - Build (query, document) pairs with title + first 500 chars
  - Batch predict relevance scores
  - Sort by relevance score descending
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 5.2 Add caching support

  - Implement rerank_with_caching() method
  - Compute cache keys from query + candidates
  - Support optional cache dictionary parameter
  - Return cached results when available
  - _Requirements: 5.5_

- [x] 5.3 Add performance optimizations

  - Use GPU acceleration when available
  - Implement batch processing for efficiency
  - Add timeout handling for long operations
  - _Requirements: 5.3_

- [x] 6. Enhance SearchService with three-way hybrid search









- [x] 6.1 Implement search_three_way_hybrid method



  - Create new search_three_way_hybrid() method in AdvancedSearchService
  - Implement query analysis for adaptive weighting
  - Execute three retrieval methods (FTS5, dense, sparse)
  - Integrate RRF fusion with adaptive weights
  - Apply optional ColBERT reranking
  - Fetch and return ordered resources
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4_


- [x] 6.2 Implement helper methods


  - Create _search_sparse() method for sparse vector search
  - Create _analyze_query() for query characteristic detection
  - Create _fetch_resources_ordered() to preserve ranking
  - Ensure backward compatibility with existing search methods
  - _Requirements: 2.3, 7.3_


- [x] 6.3 Add performance monitoring

  - Track query latency with timing
  - Log method contributions (FTS5, dense, sparse counts)
  - Log applied RRF weights
  - Monitor and log slow queries (>500ms)
  - _Requirements: 7.1, 7.2, 7.4_



- [x] 7. Implement SearchMetricsService






- [x] 7.1 Create nDCG computation


  - Implement compute_ndcg() method
  - Calculate DCG using formula: (2^rel - 1) / log2(i + 2)
  - Calculate ideal DCG from perfect ranking
  - Return normalized nDCG score
  - _Requirements: 6.1, 6.6_

- [x] 7.2 Create additional IR metrics

  - Implement compute_recall_at_k() method
  - Implement compute_precision_at_k() method
  - Implement compute_mean_reciprocal_rank() method
  - _Requirements: 6.2, 6.3, 6.4_
-

- [x] 8. Create search API endpoints




- [x] 8.1 Add three-way hybrid search endpoint


  - Create GET /search/three-way-hybrid endpoint
  - Accept query, limit, offset, enable_reranking, adaptive_weighting parameters
  - Return results with latency, method contributions, and weights
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 7.1, 7.2_

- [x] 8.2 Add comparison endpoint


  - Create GET /search/compare-methods endpoint
  - Execute all search methods (FTS5, dense, sparse, two-way, three-way, reranked)
  - Return side-by-side results with latencies
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 8.3 Add evaluation endpoint


  - Create POST /search/evaluate endpoint
  - Accept query and relevance judgments
  - Compute and return nDCG, Recall, Precision, MRR metrics
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 8.4 Add batch sparse embedding generation endpoint


  - Create POST /admin/sparse-embeddings/generate endpoint
  - Accept optional resource_ids and batch_size parameters
  - Queue background task for batch processing
  - Return job status and estimated duration
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
-

- [x] 9. Integrate sparse embedding generation into ingestion pipeline









  - Add sparse embedding generation to post-ingestion workflow
  - Enqueue background task after dense embedding generation
  - Handle failures gracefully without blocking ingestion
  - Update sparse_embedding_updated_at timestamp on completion
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 10. Create comprehensive test suite







- [x] 10.1 Write unit tests for SparseEmbeddingService


  - Test sparse embedding generation and format
  - Test batch generation efficiency
  - Test sparse vector search
  - Test error handling and fallbacks
  - _Requirements: 1.1, 1.3, 1.5_

- [x] 10.2 Write unit tests for RRFService

  - Test basic RRF fusion algorithm
  - Test weighted fusion
  - Test adaptive weighting for different query types
  - Test edge cases (empty lists, single method)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 10.3 Write unit tests for RerankingService


  - Test ColBERT reranking
  - Test caching functionality
  - Test performance (>100 docs/sec)
  - Test error handling
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 10.4 Write unit tests for SearchMetricsService

  - Test nDCG computation
  - Test Recall@K computation
  - Test Precision@K computation
  - Test MRR computation
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 10.5 Write integration tests for three-way search



  - Test three-way search combines all methods
  - Test search with reranking
  - Test adaptive weighting improves results
  - Test latency meets <200ms target
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 7.1, 7.2, 7.3_

- [x] 10.6 Write API endpoint tests



  - Test GET /search/three-way-hybrid
  - Test GET /search/compare-methods
  - Test POST /search/evaluate
  - Test POST /admin/sparse-embeddings/generate
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 10.7 Write quality validation tests


  - Test nDCG improvement over baseline (30%+ target)
  - Test sparse vectors improve technical queries
  - Test reranking improves precision
  - Requires test dataset with relevance judgments
  - _Requirements: 6.6_

- [x] 11. Update documentation












  - Update README.md with Phase 8 features
  - Update API_DOCUMENTATION.md with new endpoints
  - Update DEVELOPER_GUIDE.md with architecture details
  - Update CHANGELOG.md with Phase 8 changes
  - Add examples to EXAMPLES.md
  - _Requirements: All_
