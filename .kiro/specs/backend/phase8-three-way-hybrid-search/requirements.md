# Requirements Document

## Introduction

Phase 8 implements a state-of-the-art three-way hybrid search system for Neo Alexandria that combines full-text search (FTS5), dense vector search, and sparse vector search. The system uses Reciprocal Rank Fusion (RRF) to merge results from these three retrieval methods, followed by ColBERT-style reranking for optimal precision. This represents a significant advancement in search quality with query-adaptive weighting that automatically balances retrieval methods based on query characteristics.

## Glossary

- **Search System**: The Neo Alexandria search infrastructure that retrieves relevant resources based on user queries
- **FTS5**: SQLite Full-Text Search engine used for keyword-based retrieval
- **Dense Vector**: High-dimensional embeddings (768 dimensions) where all values are non-zero, used for semantic similarity
- **Sparse Vector**: High-dimensional embeddings with only 50-200 non-zero values, representing learned keyword importance
- **BGE-M3**: BAAI's multi-functionality embedding model that generates dense, sparse, and ColBERT representations
- **RRF Service**: Reciprocal Rank Fusion algorithm implementation for merging ranked result lists
- **ColBERT**: Contextualized Late Interaction over BERT, a neural reranking model
- **Cross-Encoder**: A neural model that scores query-document pairs directly for reranking
- **nDCG**: Normalized Discounted Cumulative Gain, an information retrieval metric measuring ranking quality
- **Retrieval Method**: A technique for finding relevant documents (FTS5, dense vectors, or sparse vectors)
- **Candidate Generation**: The first stage of search that retrieves potential relevant documents
- **Reranking**: The second stage that refines the ranking of candidate documents
- **Query-Adaptive Weighting**: Automatic adjustment of retrieval method importance based on query characteristics

## Requirements

### Requirement 1

**User Story:** As a researcher, I want the search system to use sparse vector embeddings, so that technical queries with specific terminology return more accurate results.

#### Acceptance Criteria

1. WHEN a Resource is created or updated, THE Search System SHALL generate a sparse vector embedding using the BGE-M3 model
2. THE Search System SHALL store sparse vector embeddings as JSON strings in the Resource model with token-to-weight mappings
3. THE Search System SHALL complete sparse embedding generation within 1 second per resource
4. THE Search System SHALL store the sparse embedding model name and generation timestamp with each embedding
5. WHEN sparse embedding generation fails, THE Search System SHALL log the error and continue operation without the sparse embedding

### Requirement 2

**User Story:** As a user, I want search results to combine three different retrieval methods, so that I get the most relevant results regardless of query type.

#### Acceptance Criteria

1. WHEN a user submits a search query, THE Search System SHALL execute FTS5 full-text search and retrieve up to 100 candidate results
2. WHEN a user submits a search query, THE Search System SHALL execute dense vector semantic search and retrieve up to 100 candidate results
3. WHEN a user submits a search query, THE Search System SHALL execute sparse vector keyword search and retrieve up to 100 candidate results
4. THE Search System SHALL execute all three retrieval methods within 150 milliseconds total
5. WHEN any retrieval method fails, THE Search System SHALL continue with the remaining methods and log the failure

### Requirement 3

**User Story:** As a user, I want search results from different methods to be intelligently merged, so that the best results from each method are surfaced.

#### Acceptance Criteria

1. WHEN three result lists are available, THE RRF Service SHALL compute a Reciprocal Rank Fusion score for each unique document
2. THE RRF Service SHALL apply the formula: RRF_score(d) = Σ [weight_i / (k + rank_i(d))] where k equals 60
3. THE RRF Service SHALL sort merged results by RRF score in descending order
4. THE RRF Service SHALL complete result fusion within 5 milliseconds
5. WHEN a document appears in multiple result lists, THE RRF Service SHALL combine its scores from all lists

### Requirement 4

**User Story:** As a user, I want the search system to automatically adjust retrieval method importance based on my query, so that I get optimal results without manual tuning.

#### Acceptance Criteria

1. WHEN a query contains 3 or fewer words, THE RRF Service SHALL increase the FTS5 weight by 50 percent relative to baseline
2. WHEN a query contains more than 10 words, THE RRF Service SHALL increase the dense vector weight by 50 percent relative to baseline
3. WHEN a query contains technical indicators such as code syntax or mathematical symbols, THE RRF Service SHALL increase the sparse vector weight by 50 percent relative to baseline
4. WHEN a query starts with question words (who, what, when, where, why, how), THE RRF Service SHALL increase the dense vector weight by 30 percent relative to baseline
5. THE RRF Service SHALL normalize all weights to sum to 1.0 before applying them

### Requirement 5

**User Story:** As a user, I want the top search results to be reranked using advanced neural models, so that the most relevant results appear first.

#### Acceptance Criteria

1. WHEN reranking is enabled, THE Search System SHALL apply ColBERT cross-encoder reranking to the top 100 candidate documents
2. THE Search System SHALL compute relevance scores for each query-document pair using the cross-encoder model
3. THE Search System SHALL complete reranking of 100 documents within 1 second
4. THE Search System SHALL return results sorted by reranking score in descending order
5. WHEN reranking is disabled or fails, THE Search System SHALL return results sorted by RRF score

### Requirement 6

**User Story:** As a system administrator, I want to measure search quality improvements, so that I can validate that Phase 8 enhances search performance.

#### Acceptance Criteria

1. THE Search System SHALL provide an nDCG@20 metric computation function that accepts ranked results and relevance judgments
2. THE Search System SHALL provide a Recall@K metric computation function that measures retrieval completeness
3. THE Search System SHALL provide a Precision@K metric computation function that measures retrieval accuracy
4. THE Search System SHALL provide a Mean Reciprocal Rank (MRR) metric computation function
5. THE Search System SHALL achieve at least 30 percent improvement in nDCG@20 compared to two-way hybrid search baseline

### Requirement 7

**User Story:** As a user, I want search queries to complete quickly, so that I can efficiently find information without delays.

#### Acceptance Criteria

1. THE Search System SHALL complete 95 percent of three-way hybrid search queries within 200 milliseconds
2. THE Search System SHALL log query latency for each search request
3. THE Search System SHALL execute the three retrieval methods in parallel to minimize total latency
4. WHEN query latency exceeds 500 milliseconds, THE Search System SHALL log a warning with query details
5. THE Search System SHALL utilize GPU acceleration when available for embedding generation and reranking

### Requirement 8

**User Story:** As a developer, I want to compare different search methods side-by-side, so that I can debug and optimize search quality.

#### Acceptance Criteria

1. THE Search System SHALL provide an API endpoint that returns results from FTS5 only, dense only, sparse only, two-way hybrid, three-way hybrid, and three-way with reranking
2. THE Search System SHALL execute all comparison methods for the same query
3. THE Search System SHALL return results in a structured format showing method name and corresponding results
4. THE Search System SHALL complete the comparison within 1 second
5. THE Search System SHALL include result counts and latency metrics for each method

### Requirement 9

**User Story:** As a system administrator, I want to batch-generate sparse embeddings for existing resources, so that all content benefits from the enhanced search capabilities.

#### Acceptance Criteria

1. THE Search System SHALL provide a batch update function that generates sparse embeddings for resources without them
2. THE Search System SHALL process sparse embeddings in batches of 32 resources for GPU or 8 resources for CPU
3. THE Search System SHALL commit database updates every 100 resources during batch processing
4. THE Search System SHALL log progress updates showing completed count and total count
5. WHEN batch processing is interrupted, THE Search System SHALL resume from the last committed batch

### Requirement 10

**User Story:** As a user, I want sparse embeddings to be automatically generated when I add new resources, so that new content is immediately searchable with all methods.

#### Acceptance Criteria

1. WHEN a Resource completes content extraction, THE Search System SHALL enqueue a background task to generate sparse embeddings
2. THE Search System SHALL generate sparse embeddings after dense embeddings are generated
3. WHEN sparse embedding generation fails for a resource, THE Search System SHALL log the error and mark the resource for retry
4. THE Search System SHALL update the sparse_embedding_updated_at timestamp when generation completes
5. THE Search System SHALL not block resource creation or updates while generating sparse embeddings
