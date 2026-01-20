# Requirements Document: Phase 17.5 - Advanced RAG Architecture Upgrade

## Introduction

Phase 17.5 upgrades Neo Alexandria 2.0 from "Naive RAG" to advanced RAG patterns based on the NirDiamant RAG Techniques resource. This phase decouples retrieval units from generation units, introduces semantic graph capabilities for GraphRAG, enables HyDE (Hypothetical Document Embeddings) query expansion, and implements rigorous evaluation metrics. The goal is to significantly improve retrieval quality, context relevance, and system measurability.

## Glossary

- **System**: Neo Alexandria 2.0 backend application
- **RAG**: Retrieval-Augmented Generation - pattern for combining retrieval with LLM generation
- **Naive_RAG**: Basic RAG pattern where entire documents are retrieved and used as context
- **Parent_Child_Chunking**: Pattern where small chunks are retrieved but larger parent context is provided to LLM
- **DocumentChunk**: Small, searchable unit of text with embedding (retrieval unit)
- **Resource**: Full document or parent context (generation unit)
- **GraphRAG**: RAG pattern that uses knowledge graph relationships to enhance retrieval
- **GraphEntity**: Named entity extracted from text (e.g., "Neural Networks", "Geoffrey Hinton")
- **GraphRelationship**: Semantic triple connecting entities (Subject -> Predicate -> Object)
- **HyDE**: Hypothetical Document Embeddings - technique where LLM generates hypothetical answers to improve retrieval
- **Reverse_HyDE**: Storing LLM-generated questions for each chunk to improve question-based retrieval
- **SyntheticQuestion**: LLM-generated question that a chunk could answer
- **RAGEvaluation**: Ground-truth data and metrics for evaluating RAG quality
- **RAGAS**: RAG Assessment framework with metrics like faithfulness, answer relevance, context precision
- **Embedding_Service**: Service for generating vector embeddings
- **Graph_Module**: Module responsible for knowledge graph and citation management
- **Resources_Module**: Module responsible for resource CRUD and document management
- **Search_Module**: Module responsible for hybrid search and retrieval
- **Quality_Module**: Module responsible for quality assessment and evaluation
- **Chunk_Index**: Integer indicating position of chunk within parent document
- **Provenance**: Link from graph relationship back to source chunk

## Requirements

### Requirement 1: Parent-Child Chunking Schema

**User Story:** As a system architect, I want to decouple retrieval units from generation units, so that I can retrieve small, precise chunks while providing larger context to the LLM.

#### Acceptance Criteria

1. THE Resources_Module SHALL define a DocumentChunk model with fields: id, resource_id, content, chunk_index, embedding_id, page_number
2. THE DocumentChunk model SHALL have a foreign key relationship to Resource (many chunks per resource)
3. THE DocumentChunk model SHALL have a foreign key relationship to Embedding (one embedding per chunk)
4. THE DocumentChunk.chunk_index SHALL indicate the sequential position within the parent resource
5. THE DocumentChunk.page_number SHALL optionally store the source page for PDF documents
6. THE Resource model SHALL have a backref relationship "chunks" to access all child chunks
7. WHEN a resource is deleted, THE System SHALL cascade delete all associated chunks
8. THE DocumentChunk table SHALL have indexes on resource_id and chunk_index for fast retrieval
9. THE System SHALL support creating resources without chunks (backward compatibility)
10. WHEN chunks are created, THE System SHALL validate that chunk_index values are sequential and unique per resource

### Requirement 2: GraphRAG Semantic Triple Storage

**User Story:** As a knowledge engineer, I want to store semantic triples (Subject -> Predicate -> Object), so that I can enhance retrieval with graph relationships and discover contradictions or connections.

#### Acceptance Criteria

1. THE Graph_Module SHALL define a GraphEntity model with fields: id, name, type, description
2. THE GraphEntity.type SHALL categorize entities (e.g., "Concept", "Person", "Organization", "Method")
3. THE Graph_Module SHALL define a GraphRelationship model with fields: id, source_entity_id, target_entity_id, relation_type, weight, provenance_chunk_id
4. THE GraphRelationship.relation_type SHALL describe the semantic relationship (e.g., "CONTRADICTS", "SUPPORTS", "EXTENDS", "CITES")
5. THE GraphRelationship.weight SHALL represent relationship strength (0.0 to 1.0)
6. THE GraphRelationship.provenance_chunk_id SHALL link back to the source DocumentChunk
7. THE GraphRelationship model SHALL have foreign keys to source and target GraphEntity
8. THE GraphRelationship model SHALL have a foreign key to DocumentChunk for provenance
9. THE System SHALL support querying entities by name and type
10. THE System SHALL support querying relationships by relation_type
11. THE System SHALL support traversing the graph from entity to related entities
12. WHEN an entity is deleted, THE System SHALL handle relationship cleanup appropriately

### Requirement 3: HyDE Query Expansion with Synthetic Questions

**User Story:** As a search engineer, I want to store LLM-generated questions for each chunk, so that I can improve question-based retrieval using Reverse HyDE.

#### Acceptance Criteria

1. THE Search_Module SHALL define a SyntheticQuestion model with fields: id, chunk_id, question_text, embedding_id
2. THE SyntheticQuestion model SHALL have a foreign key relationship to DocumentChunk
3. THE SyntheticQuestion model SHALL have a foreign key relationship to Embedding
4. THE System SHALL support storing multiple synthetic questions per chunk
5. WHEN a chunk is processed, THE System SHALL optionally generate 1-3 synthetic questions using an LLM
6. THE Embedding_Service SHALL generate embeddings for synthetic questions
7. THE Search_Module SHALL support querying by question similarity (user query -> synthetic question -> chunk)
8. WHEN a chunk is deleted, THE System SHALL cascade delete all associated synthetic questions
9. THE SyntheticQuestion table SHALL have an index on chunk_id for fast retrieval
10. THE System SHALL support disabling synthetic question generation for performance-sensitive deployments

### Requirement 4: RAG Evaluation Metrics Storage

**User Story:** As a quality engineer, I want to store ground-truth evaluation data and metrics, so that I can measure and improve RAG system performance using RAGAS or TruLens frameworks.

#### Acceptance Criteria

1. THE Quality_Module SHALL define a RAGEvaluation model with fields: id, query, expected_answer, generated_answer, retrieved_chunk_ids, faithfulness_score, answer_relevance_score, context_precision_score, created_at
2. THE RAGEvaluation.query SHALL store the user's original question
3. THE RAGEvaluation.expected_answer SHALL store the ground-truth answer (for evaluation datasets)
4. THE RAGEvaluation.generated_answer SHALL store the LLM's generated response
5. THE RAGEvaluation.retrieved_chunk_ids SHALL store a JSON array of chunk IDs used for generation
6. THE RAGEvaluation.faithfulness_score SHALL measure how well the answer is grounded in retrieved context (0.0 to 1.0)
7. THE RAGEvaluation.answer_relevance_score SHALL measure how well the answer addresses the query (0.0 to 1.0)
8. THE RAGEvaluation.context_precision_score SHALL measure how relevant the retrieved chunks are (0.0 to 1.0)
9. THE RAGEvaluation.created_at SHALL timestamp when the evaluation was performed
10. THE System SHALL support querying evaluations by date range and score thresholds
11. THE System SHALL support aggregating metrics to compute average scores over time
12. THE Quality_Module SHALL provide an API endpoint to submit evaluation data
13. THE Quality_Module SHALL provide an API endpoint to retrieve evaluation statistics

### Requirement 5: Database Migration and Backward Compatibility

**User Story:** As a system administrator, I want a clean database migration, so that I can upgrade existing deployments without data loss.

#### Acceptance Criteria

1. THE System SHALL generate an Alembic migration file named "add_advanced_rag_tables"
2. THE Migration SHALL create document_chunks table with all required columns and indexes
3. THE Migration SHALL create graph_entities table with all required columns and indexes
4. THE Migration SHALL create graph_relationships table with all required columns and indexes
5. THE Migration SHALL create synthetic_questions table with all required columns and indexes
6. THE Migration SHALL create rag_evaluations table with all required columns and indexes
7. THE Migration SHALL define foreign key constraints with appropriate cascade behavior
8. THE Migration SHALL be reversible (support downgrade)
9. WHEN the migration runs on an existing database, THE System SHALL preserve all existing resource data
10. THE System SHALL support resources without chunks (chunks are optional)
11. THE Migration SHALL include indexes on resource_id, chunk_index, entity names, and chunk_id for performance

### Requirement 6: Chunking Service Implementation

**User Story:** As a content processor, I want an automated chunking service, so that resources are automatically split into optimal retrieval units.

#### Acceptance Criteria

1. THE Resources_Module SHALL implement a ChunkingService with configurable chunk size and overlap
2. THE ChunkingService SHALL support semantic chunking (split on sentence boundaries)
3. THE ChunkingService SHALL support fixed-size chunking with character or token limits
4. THE ChunkingService SHALL assign sequential chunk_index values starting from 0
5. THE ChunkingService SHALL extract page numbers from PDF metadata when available
6. WHEN a resource is created, THE System SHALL optionally trigger automatic chunking
7. THE ChunkingService SHALL generate embeddings for each chunk using Embedding_Service
8. THE ChunkingService SHALL store chunks and embeddings in a single transaction
9. THE ChunkingService SHALL emit a "resource.chunked" event when chunking completes
10. THE ChunkingService SHALL handle errors gracefully and log failures

### Requirement 7: Graph Extraction Service

**User Story:** As a knowledge engineer, I want automated entity and relationship extraction, so that the knowledge graph is populated from document content.

#### Acceptance Criteria

1. THE Graph_Module SHALL implement a GraphExtractionService using NLP or LLM-based extraction
2. THE GraphExtractionService SHALL extract named entities from chunk content
3. THE GraphExtractionService SHALL classify entity types (Concept, Person, Organization, Method)
4. THE GraphExtractionService SHALL extract relationships between entities within the same chunk
5. THE GraphExtractionService SHALL assign relation_type labels (CONTRADICTS, SUPPORTS, EXTENDS, CITES)
6. THE GraphExtractionService SHALL compute relationship weights based on extraction confidence
7. THE GraphExtractionService SHALL link relationships to source chunks via provenance_chunk_id
8. WHEN a chunk is processed, THE System SHALL optionally trigger graph extraction
9. THE GraphExtractionService SHALL deduplicate entities by name and type
10. THE GraphExtractionService SHALL emit "graph.entity_extracted" and "graph.relationship_extracted" events

### Requirement 8: Enhanced Search with Parent-Child Retrieval

**User Story:** As a search user, I want improved retrieval quality, so that I get precise results with sufficient context.

#### Acceptance Criteria

1. THE Search_Module SHALL implement a parent-child retrieval strategy
2. WHEN a user searches, THE Search_Module SHALL retrieve top-k chunks by embedding similarity
3. THE Search_Module SHALL expand retrieved chunks to include parent resource context
4. THE Search_Module SHALL support configurable context window (e.g., retrieve chunk ± 2 surrounding chunks)
5. THE Search_Module SHALL deduplicate results when multiple chunks from the same resource are retrieved
6. THE Search_Module SHALL return both chunk-level and resource-level results
7. THE Search_Module SHALL include chunk_index and page_number in search results for citation
8. THE Search_Module SHALL support filtering by resource metadata (type, quality score, etc.)
9. THE Search_Module SHALL log retrieval metrics (number of chunks retrieved, parent resources expanded)
10. THE Search_Module SHALL maintain backward compatibility with existing search API

### Requirement 9: GraphRAG-Enhanced Retrieval

**User Story:** As a search user, I want graph-enhanced retrieval, so that I can discover related concepts and contradictory information.

#### Acceptance Criteria

1. THE Search_Module SHALL implement a GraphRAG retrieval strategy
2. WHEN a user searches, THE Search_Module SHALL extract entities from the query
3. THE Search_Module SHALL find matching entities in the knowledge graph
4. THE Search_Module SHALL traverse relationships to find related entities
5. THE Search_Module SHALL retrieve chunks associated with related entities via provenance
6. THE Search_Module SHALL rank results by combining embedding similarity and graph relationship weights
7. THE Search_Module SHALL support filtering by relation_type (e.g., only show contradictions)
8. THE Search_Module SHALL return graph paths explaining why results were retrieved
9. THE Search_Module SHALL support hybrid retrieval combining keyword, semantic, and graph signals
10. THE Search_Module SHALL provide a "discover contradictions" mode that prioritizes CONTRADICTS relationships

### Requirement 10: Testing and Validation

**User Story:** As a developer, I want comprehensive tests for advanced RAG features, so that I can verify correctness and performance.

#### Acceptance Criteria

1. THE Test_Suite SHALL include unit tests for DocumentChunk model and relationships
2. THE Test_Suite SHALL include unit tests for GraphEntity and GraphRelationship models
3. THE Test_Suite SHALL include unit tests for SyntheticQuestion model
4. THE Test_Suite SHALL include unit tests for RAGEvaluation model
5. THE Test_Suite SHALL include integration tests for ChunkingService
6. THE Test_Suite SHALL include integration tests for GraphExtractionService
7. THE Test_Suite SHALL include integration tests for parent-child retrieval
8. THE Test_Suite SHALL include integration tests for GraphRAG retrieval
9. THE Test_Suite SHALL verify foreign key constraints and cascade behavior
10. THE Test_Suite SHALL verify that existing resource tests pass with optional chunks
11. THE Test_Suite SHALL include performance tests for chunking and graph extraction
12. THE Test_Suite SHALL verify that migrations run successfully on both SQLite and PostgreSQL

### Requirement 11: Documentation Updates

**User Story:** As a developer, I want updated documentation, so that I understand the new RAG architecture and how to use it.

#### Acceptance Criteria

1. THE Documentation SHALL update the Database Architecture section to include 5 new tables
2. THE Documentation SHALL include an Advanced RAG Architecture guide explaining parent-child chunking
3. THE Documentation SHALL include a GraphRAG guide explaining semantic triple storage and retrieval
4. THE Documentation SHALL include a HyDE guide explaining synthetic question generation
5. THE Documentation SHALL include a RAG Evaluation guide explaining metrics and measurement
6. THE Documentation SHALL update the Graph Module description to mention semantic triples
7. THE Documentation SHALL update the Search Module description to mention advanced retrieval strategies
8. THE Documentation SHALL include API examples for chunking, graph extraction, and evaluation
9. THE Documentation SHALL include a migration guide for upgrading from Naive RAG
10. THE Documentation SHALL include performance tuning recommendations for chunking and graph extraction

### Requirement 12: Performance and Efficiency

**User Story:** As a system administrator, I want efficient processing, so that advanced RAG features don't degrade system performance.

#### Acceptance Criteria

1. THE System SHALL index chunk_index and resource_id columns for fast chunk retrieval
2. THE System SHALL index entity names for fast graph queries
3. THE System SHALL index chunk_id in synthetic_questions for fast lookup
4. THE ChunkingService SHALL process chunks in batches to minimize database round-trips
5. THE GraphExtractionService SHALL cache entity lookups to avoid duplicate queries
6. THE Search_Module SHALL use database query optimization for parent-child retrieval
7. THE System SHALL support asynchronous processing for chunking and graph extraction
8. THE System SHALL provide configuration options to disable expensive features (synthetic questions, graph extraction)
9. THE System SHALL log processing times for chunking, graph extraction, and retrieval
10. THE System SHALL support incremental processing (only process new/updated resources)

## Non-Functional Requirements

### Performance

- Chunking: < 5 seconds per 10,000 words
- Graph extraction: < 10 seconds per chunk
- Parent-child retrieval: < 200ms for top-10 results
- GraphRAG retrieval: < 500ms for top-10 results with graph traversal
- Synthetic question generation: < 2 seconds per chunk

### Scalability

- Support 1M+ chunks in database
- Support 100K+ graph entities
- Support 500K+ graph relationships
- Efficient indexing for sub-second retrieval

### Data Quality

- Chunk boundaries respect sentence boundaries (no mid-sentence splits)
- Entity extraction accuracy > 80%
- Relationship extraction accuracy > 70%
- Synthetic questions are grammatically correct and relevant

### Maintainability

- Clear separation between chunking, graph extraction, and retrieval services
- Modular design allows disabling features independently
- Comprehensive logging for debugging and monitoring
- Type-safe Pydantic schemas for all new models

## Success Metrics

- All 5 new tables created successfully via migration
- Zero foreign key constraint violations
- All existing resource tests pass with optional chunks
- Parent-child retrieval improves context relevance by 20% (measured via evaluation)
- GraphRAG retrieval discovers 30% more related content than semantic search alone
- Chunking processes 10,000 words in < 5 seconds
- Graph extraction processes 100 chunks in < 5 minutes
- 100% test coverage for new models and services
- Documentation complete for all new features
