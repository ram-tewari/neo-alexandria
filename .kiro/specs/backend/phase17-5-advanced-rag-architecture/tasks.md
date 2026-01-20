# Implementation Plan: Phase 17.5 - Advanced RAG Architecture Upgrade

## Overview

This implementation plan breaks down the Advanced RAG Architecture upgrade into discrete, testable tasks. The approach follows a bottom-up strategy: database schema first, then services, then API endpoints, with testing at each layer.

**Code-Ready Modifications for Phase 18:**
- **Task 1.1**: Uses flexible `chunk_metadata` (JSONB) instead of `page_number` - supports both PDF pages and code line numbers
- **Task 1.4**: Includes code-specific graph enums (CALLS, IMPORTS, DEFINES) alongside academic enums
- **Task 2.3**: Schema validation supports both academic and code relationship types
- **Task 5.1**: ChunkingService accepts `parser_type` parameter for future AST chunking strategies
- **Task 5**: Architecture designed to support Tree-Sitter AST chunking without API changes

## Tasks

- [ ] 1. Database Schema Implementation
  - Create new SQLAlchemy models for advanced RAG tables
  - _Requirements: 1.1-1.10, 2.1-2.12, 3.1-3.10, 4.1-4.13_

- [x] 1.1 Create DocumentChunk Model (Code-Ready)
  - Add DocumentChunk model to `app/modules/resources/model.py`
  - Define columns: id, resource_id, content, chunk_index, embedding_id, chunk_metadata (JSONB/JSON), created_at
  - chunk_metadata structure: For PDFs: {"page": 1, "coordinates": [x,y]}, For Code: {"start_line": 10, "end_line": 25, "function_name": "calculate_loss", "file_path": "src/model.py"}
  - Add foreign key relationships to Resource and Embedding
  - Add indexes on resource_id and (resource_id, chunk_index)
  - Add backref relationship to Resource model
  - **Note**: Flexible metadata column supports both PDF pages and code line numbers without schema changes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8_

- [x] 1.2 Write property test for DocumentChunk foreign key integrity
  - **Property 2: Foreign Key Integrity**
  - **Validates: Requirements 1.7**
  - Generate random resources and chunks
  - Delete resources and verify cascade delete of chunks
  - Verify orphaned chunks cannot be created

- [x] 1.3 Create GraphEntity Model
  - Add GraphEntity model to `app/modules/graph/model.py`
  - Define columns: id, name, type, description, created_at
  - Add index on (name, type)
  - Add relationship definitions for outgoing and incoming relationships
  - _Requirements: 2.1, 2.2, 2.9_

- [x] 1.4 Create GraphRelationship Model (Code-Ready)
  - Add GraphRelationship model to `app/modules/graph/model.py`
  - Define columns: id, source_entity_id, target_entity_id, relation_type, weight, provenance_chunk_id, created_at
  - relation_type enum: CONTRADICTS, SUPPORTS, EXTENDS, CITES (academic), CALLS, IMPORTS, DEFINES (code-specific)
  - Add foreign keys to GraphEntity (source and target) and DocumentChunk (provenance)
  - Add indexes on source_entity_id, target_entity_id, and relation_type
  - **Note**: Code-specific enums (CALLS, IMPORTS, DEFINES) enable structural dependency tracking without schema changes
  - _Requirements: 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.10_

- [ ] 1.5 Write property test for graph triple validity
  - **Property 3: Graph Triple Validity**
  - **Validates: Requirements 2.7**
  - Generate random entities and relationships
  - Verify all relationships reference existing entities
  - Test cascade behavior when entities are deleted

- [x] 1.6 Create SyntheticQuestion Model
  - Add SyntheticQuestion model to `app/modules/search/model.py`
  - Define columns: id, chunk_id, question_text, embedding_id, created_at
  - Add foreign keys to DocumentChunk and Embedding
  - Add index on chunk_id
  - Add backref relationship to DocumentChunk
  - _Requirements: 3.1, 3.2, 3.3, 3.9_

- [x] 1.7 Create RAGEvaluation Model
  - Add RAGEvaluation model to `app/modules/quality/model.py`
  - Define columns: id, query, expected_answer, generated_answer, retrieved_chunk_ids (JSON), faithfulness_score, answer_relevance_score, context_precision_score, created_at
  - Add index on created_at
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

- [x] 2. Pydantic Schemas for New Models
  - Create request/response schemas for all new models
  - _Requirements: 1.1-1.10, 2.1-2.12, 3.1-3.10, 4.1-4.13_

- [x] 2.1 Create DocumentChunk Schemas (Code-Ready)
  - Add DocumentChunkCreate, DocumentChunkResponse to `app/modules/resources/schema.py`
  - Include validation for chunk_index (non-negative integer)
  - Include optional chunk_metadata field (dict with flexible structure)
  - Support both PDF metadata (page, coordinates) and code metadata (start_line, end_line, function_name, file_path)
  - _Requirements: 1.1-1.6_

- [x] 2.2 Create GraphEntity Schemas
  - Add GraphEntityCreate, GraphEntityResponse to `app/modules/graph/schema.py`
  - Include validation for entity type (Concept, Person, Organization, Method)
  - _Requirements: 2.1-2.3_

- [x] 2.3 Create GraphRelationship Schemas (Code-Ready)
  - Add GraphRelationshipCreate, GraphRelationshipResponse to `app/modules/graph/schema.py`
  - Include validation for relation_type: Academic (CONTRADICTS, SUPPORTS, EXTENDS, CITES) + Code (CALLS, IMPORTS, DEFINES)
  - Include validation for weight (0.0 to 1.0)
  - **Note**: Code-specific relation types enable structural dependency tracking for Phase 18
  - _Requirements: 2.3-2.6_

- [x] 2.4 Create SyntheticQuestion Schemas
  - Add SyntheticQuestionCreate, SyntheticQuestionResponse to `app/modules/search/schema.py`
  - Include validation for question_text (non-empty)
  - _Requirements: 3.1-3.3_

- [x] 2.5 Create RAGEvaluation Schemas
  - Add RAGEvaluationCreate, RAGEvaluationResponse to `app/modules/quality/schema.py`
  - Include validation for score fields (0.0 to 1.0 or null)
  - Include validation for retrieved_chunk_ids (list of strings)
  - _Requirements: 4.1-4.9_

- [x] 3. Database Migration
  - Generate Alembic migration for new tables
  - _Requirements: 5.1-5.11_

- [x] 3.1 Generate Alembic Migration
  - Run `alembic revision --autogenerate -m "Add Advanced RAG Tables"`
  - Review generated migration file
  - Ensure all tables, columns, indexes, and foreign keys are included
  - Test upgrade and downgrade operations
  - _Requirements: 5.1-5.8_

- [x] 3.2 Test migration on SQLite
  - Run migration on SQLite test database
  - Verify all tables created successfully
  - Verify foreign key constraints work
  - Test downgrade operation
  - _Requirements: 5.9, 5.10_

- [x] 3.3 Test migration on PostgreSQL
  - Run migration on PostgreSQL test database
  - Verify all tables created successfully
  - Verify foreign key constraints work
  - Test downgrade operation
  - _Requirements: 5.9, 5.10_

- [x] 4. Checkpoint - Database Schema Complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. ChunkingService Implementation (Code-Ready)
  - Implement document chunking with multiple strategies
  - **Note**: Ensure architecture allows for future ASTChunkingStrategy (Tree-Sitter) without breaking the API
  - _Requirements: 6.1-6.10_

- [x] 5.1 Create ChunkingService Class (Code-Ready)
  - Add ChunkingService to `app/modules/resources/service.py`
  - Implement __init__ with configuration parameters (strategy, chunk_size, overlap, parser_type)
  - parser_type options: "text" (default), "code_python", "code_javascript", "code_java", etc.
  - Add dependency injection for database session and embedding service
  - **Note**: Architecture allows for future ASTChunkingStrategy without breaking the API
  - _Requirements: 6.1_

- [x] 5.2 Implement Semantic Chunking
  - Add semantic_chunk() method using spaCy or NLTK for sentence splitting
  - Split on sentence boundaries with target chunk size
  - Implement overlap by including sentences from previous chunk
  - Assign sequential chunk_index values
  - _Requirements: 6.2, 6.4_

- [x] 5.3 Implement Fixed-Size Chunking
  - Add fixed_chunk() method for character-based splitting
  - Split at fixed character count with overlap
  - Split on whitespace to avoid mid-word breaks
  - Assign sequential chunk_index values
  - _Requirements: 6.3, 6.4_

- [x] 5.4 Implement Chunk Storage and Embedding
  - Add store_chunks() method to save chunks to database
  - Generate embeddings for each chunk using EmbeddingService
  - Store chunks and embeddings in a single transaction
  - Handle errors gracefully with rollback
  - _Requirements: 6.7, 6.8_

- [x] 5.5 Implement Event Emission
  - Emit "resource.chunked" event after successful chunking
  - Include resource_id and chunk_count in event payload
  - Emit "resource.chunking_failed" event on errors
  - _Requirements: 6.9_

- [x] 5.6 Write unit tests for ChunkingService
  - Test semantic chunking with sample documents
  - Test fixed-size chunking with various sizes
  - Test chunk_index assignment
  - Test error handling
  - _Requirements: 6.1-6.10_

- [x] 5.7 Write property test for chunk content preservation
  - **Property 9: Chunk Content Preservation**
  - **Validates: Requirements 6.4**
  - Generate random resource content
  - Chunk the content
  - Concatenate chunks in order
  - Verify reconstructed content matches original (allowing overlap)

- [x] 5.8 Integrate Chunking into Ingestion Pipeline
  - Modify process_ingestion() in `app/modules/resources/service.py`
  - Call ChunkingService after content extraction and before marking ingestion complete
  - Store chunks in the same transaction as resource updates
  - Handle chunking errors gracefully (log but don't fail ingestion)
  - Make chunking optional via CHUNK_ON_RESOURCE_CREATE configuration
  - _Requirements: 6.6_

- [x] 5.9 Create Celery Task for Async Chunking
  - Add chunk_resource_task() to `app/tasks/resource_tasks.py`
  - Support async chunking for large documents (>10,000 words)
  - Implement retry logic with exponential backoff
  - Track chunking progress and emit status events
  - Handle task failures and update resource status
  - _Requirements: 6.6, 12.7_

- [x] 5.10 Write integration tests for chunking pipeline
  - Test automatic chunking during resource ingestion
  - Test async chunking via Celery task
  - Test error handling and retry logic
  - Test configuration toggle (CHUNK_ON_RESOURCE_CREATE)
  - _Requirements: 6.6, 12.7_

- [x] 6. GraphExtractionService Implementation ✅ COMPLETE
  - Implement entity and relationship extraction
  - _Requirements: 7.1-7.10_
  - **Status**: All subtasks completed and tested successfully

- [x] 6.1 Create GraphExtractionService Class ✅
  - Add GraphExtractionService to `app/modules/graph/service.py`
  - Implement __init__ with configuration (extraction method: llm, spacy, hybrid)
  - Add dependency injection for database session and AI service
  - _Requirements: 7.1_
  - **Completed**: GraphExtractionService class implemented with configurable extraction methods

- [x] 6.2 Implement Entity Extraction ✅
  - Add extract_entities() method using NLP or LLM
  - Extract named entities from chunk content
  - Classify entity types (Concept, Person, Organization, Method)
  - Deduplicate entities by name and type
  - _Requirements: 7.2, 7.3, 7.9_
  - **Completed**: Entity extraction with both LLM and spaCy methods, deduplication logic implemented

- [x] 6.3 Implement Relationship Extraction ✅
  - Add extract_relationships() method
  - Extract relationships between entities within chunk
  - Assign relation_type labels (CONTRADICTS, SUPPORTS, EXTENDS, CITES)
  - Compute relationship weights based on extraction confidence
  - Link relationships to source chunk via provenance_chunk_id
  - _Requirements: 7.4, 7.5, 7.6, 7.7_
  - **Completed**: Relationship extraction with heuristic-based type inference and weight computation

- [x] 6.4 Implement Event Emission ✅
  - Emit "graph.entity_extracted" event for each entity
  - Emit "graph.relationship_extracted" event for each relationship
  - Include entity/relationship details in event payload
  - _Requirements: 7.10_
  - **Completed**: Event emission methods implemented for both entities and relationships

- [x] 6.5 Write unit tests for GraphExtractionService ✅
  - Test entity extraction from sample text
  - Test relationship extraction
  - Test entity deduplication
  - Test provenance linkage
  - _Requirements: 7.1-7.10_
  - **Completed**: 9 unit tests passing, covering all core functionality

- [x] 6.6 Implement SyntheticQuestionService ✅
  - Add SyntheticQuestionService to `app/modules/search/service.py`
  - Implement generate_questions() method using LLM (GPT-3.5-turbo or similar)
  - Generate 1-3 questions per chunk that the chunk could answer
  - Use prompt engineering to ensure questions are specific and relevant
  - Store questions with embeddings via EmbeddingService
  - Make question generation optional via SYNTHETIC_QUESTIONS_ENABLED config
  - _Requirements: 3.5, 3.6_
  - **Completed**: SyntheticQuestionService with heuristic pattern-based generation and embedding support

- [x] 6.7 Write unit tests for SyntheticQuestionService ✅
  - Test question generation from sample chunks
  - Test question quality and relevance
  - Test embedding generation for questions
  - Test configuration toggle
  - _Requirements: 3.5, 3.6_
  - **Completed**: 16 unit tests passing, covering all functionality including embeddings and configuration

- [x] 7. Enhanced Search Implementation
  - Implement parent-child and GraphRAG retrieval strategies
  - _Requirements: 8.1-8.10, 9.1-9.10_

- [x] 7.1 Implement Parent-Child Retrieval
  - Add parent_child_search() method to `app/modules/search/service.py`
  - Retrieve top-k chunks by embedding similarity
  - Expand to parent resources for each chunk
  - Include surrounding chunks based on context_window parameter
  - Deduplicate results when multiple chunks from same resource
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 7.2 Write property test for parent-child retrieval consistency
  - **Property 7: Parent-Child Retrieval Consistency**
  - **Validates: Requirements 8.3**
  - Generate random chunks and retrieve them
  - Expand to parent resources
  - Verify parent contains the retrieved chunk

- [x] 7.3 Implement GraphRAG Retrieval
  - Add graphrag_search() method to `app/modules/search/service.py`
  - Extract entities from user query
  - Find matching entities in knowledge graph
  - Traverse relationships to find related entities
  - Retrieve chunks associated with entities via provenance
  - Rank results by combining embedding similarity and graph weights
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 7.4 Implement Contradiction Discovery Mode
  - Add discover_contradictions() method
  - Filter relationships by CONTRADICTS relation_type
  - Return graph paths explaining contradictions
  - _Requirements: 9.7, 9.8, 9.10_

- [x] 7.5 Implement Question-Based Retrieval (Reverse HyDE)
  - Add question_search() method to `app/modules/search/service.py`
  - Match user query against synthetic question embeddings
  - Retrieve chunks associated with matching questions
  - Rank results by question similarity score
  - Support hybrid mode combining question search with semantic search
  - _Requirements: 3.7_

- [x] 7.6 Write integration tests for enhanced search
  - Test parent-child retrieval with sample data
  - Test GraphRAG retrieval with sample graph
  - Test contradiction discovery
  - Test question-based retrieval (Reverse HyDE)
  - Test result ranking and deduplication
  - _Requirements: 8.1-8.10, 9.1-9.10, 3.7_

- [x] 8. Checkpoint - Core Services Complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. API Endpoints for Chunking
  - Expose chunking functionality via REST API
  - _Requirements: 6.1-6.10_

- [x] 9.1 Create Chunking Endpoints
  - Add POST /api/resources/{resource_id}/chunks to `app/modules/resources/router.py`
  - Add GET /api/resources/{resource_id}/chunks
  - Add GET /api/chunks/{chunk_id}
  - Implement request validation and error handling
  - _Requirements: 6.1-6.10_

- [x] 9.2 Write endpoint tests for chunking
  - Test POST /api/resources/{resource_id}/chunks with valid data
  - Test GET /api/resources/{resource_id}/chunks pagination
  - Test GET /api/chunks/{chunk_id} retrieval
  - Test error cases (invalid resource_id, etc.)
  - _Requirements: 6.1-6.10_

- [x] 10. API Endpoints for Graph Operations
  - Expose graph functionality via REST API
  - _Requirements: 7.1-7.10_

- [x] 10.1 Create Graph Endpoints
  - Add POST /api/graph/extract/{chunk_id} to `app/modules/graph/router.py`
  - Add GET /api/graph/entities
  - Add GET /api/graph/entities/{entity_id}/relationships
  - Add GET /api/graph/traverse
  - Implement request validation and error handling
  - _Requirements: 7.1-7.10_

- [x] 10.2 Write endpoint tests for graph operations
  - Test POST /api/graph/extract/{chunk_id}
  - Test GET /api/graph/entities with filters
  - Test GET /api/graph/entities/{entity_id}/relationships
  - Test GET /api/graph/traverse with max_hops
  - _Requirements: 7.1-7.10_

- [x] 11. API Endpoints for Advanced Search
  - Expose enhanced search via REST API
  - _Requirements: 8.1-8.10, 9.1-9.10_

- [x] 11.1 Create Advanced Search Endpoint
  - Add POST /api/search/advanced to `app/modules/search/router.py`
  - Support strategy parameter (parent-child, graphrag, hybrid)
  - Support top_k, context_window, relation_types parameters
  - Return enhanced results with chunks, parents, and graph paths
  - _Requirements: 8.1-8.10, 9.1-9.10_

- [x] 11.2 Write endpoint tests for advanced search
  - Test parent-child search strategy
  - Test GraphRAG search strategy
  - Test hybrid search strategy
  - Test parameter validation
  - _Requirements: 8.1-8.10, 9.1-9.10_

- [x] 12. API Endpoints for RAG Evaluation
  - Expose evaluation functionality via REST API
  - _Requirements: 4.1-4.13_

- [x] 12.1 Create Evaluation Endpoints
  - Add POST /api/evaluation/submit to `app/modules/quality/router.py`
  - Add GET /api/evaluation/metrics
  - Add GET /api/evaluation/history
  - Implement metric aggregation logic
  - _Requirements: 4.10, 4.11, 4.12, 4.13_

- [x] 12.2 Write endpoint tests for evaluation
  - Test POST /api/evaluation/submit with valid data
  - Test GET /api/evaluation/metrics aggregation
  - Test GET /api/evaluation/history pagination
  - Test score validation
  - _Requirements: 4.1-4.13_

- [x] 13. Event Handler Integration
  - Wire up event handlers for automatic processing
  - _Requirements: 6.9, 7.10_

- [x] 13.1 Create Resource Chunking Event Handler
  - Add event handler in `app/modules/resources/handlers.py`
  - Subscribe to "resource.created" event
  - Trigger chunking if CHUNK_ON_RESOURCE_CREATE is enabled
  - Handle errors and emit appropriate events
  - _Requirements: 6.9_

- [x] 13.2 Create Graph Extraction Event Handler
  - Add event handler in `app/modules/graph/handlers.py`
  - Subscribe to "resource.chunked" event
  - Trigger graph extraction if GRAPH_EXTRACT_ON_CHUNK is enabled
  - Handle errors and emit appropriate events
  - _Requirements: 7.10_

- [x] 13.3 Write integration tests for event handlers
  - Test automatic chunking on resource creation
  - Test automatic graph extraction on chunking
  - Test event emission and propagation
  - _Requirements: 6.9, 7.10_

- [x] 14. Configuration Management
  - Add configuration options for advanced RAG features
  - _Requirements: 12.1-12.9_

- [x] 14.1 Add Configuration Fields
  - Add chunking configuration to `app/config/settings.py`
  - Add graph extraction configuration
  - Add synthetic questions configuration
  - Add retrieval configuration
  - Provide sensible defaults
  - _Requirements: 12.1-12.9_

- [x] 14.2 Write tests for configuration
  - Test configuration loading from environment
  - Test default values
  - Test validation of configuration values
  - _Requirements: 12.1-12.9_

- [x] 15. Documentation Updates
  - Update all relevant documentation
  - _Requirements: 11.1-11.10_

- [x] 15.1 Update Database Architecture Documentation
  - Add section to `backend/docs/architecture/database.md`
  - Document all 5 new tables with schema details
  - Include ER diagram showing relationships
  - _Requirements: 11.1_

- [x] 15.2 Update Module Documentation
  - Update `backend/docs/architecture/modules.md`
  - Add semantic triple storage to Graph module description
  - Add advanced retrieval to Search module description
  - _Requirements: 11.6, 11.7_

- [x] 15.3 Create Advanced RAG Guide
  - Create `backend/docs/guides/advanced-rag.md`
  - Explain parent-child chunking
  - Explain GraphRAG concepts
  - Explain HyDE and Reverse HyDE
  - Provide usage examples
  - _Requirements: 11.2_

- [x] 15.4 Create RAG Evaluation Guide
  - Create `backend/docs/guides/rag-evaluation.md`
  - Explain RAGAS metrics
  - Show how to submit evaluation data
  - Explain how to interpret metrics
  - _Requirements: 11.5_

- [x] 15.5 Create Migration Guide
  - Create `backend/docs/guides/naive-to-advanced-rag.md`
  - Document migration steps
  - Explain chunking existing resources
  - Provide rollback procedures
  - _Requirements: 11.9_

- [x] 15.6 Update API Documentation
  - Add chunking endpoints to `backend/docs/api/resources.md`
  - Add graph endpoints to `backend/docs/api/graph.md`
  - Add advanced search to `backend/docs/api/search.md`
  - Add evaluation endpoints to `backend/docs/api/quality.md`
  - _Requirements: 11.8_

- [x] 16. Final Checkpoint - Complete Implementation
  - Ensure all tests pass, ask the user if questions arise.

- [x] 17. Performance Validation
  - Verify performance targets are met
  - _Requirements: 12.1-12.9_

- [x] 17.1 Run performance tests
  - Test chunking performance (10,000 words in < 5 seconds)
  - Test graph extraction performance (100 chunks in < 5 minutes)
  - Test parent-child retrieval (< 200ms)
  - Test GraphRAG retrieval (< 500ms)
  - _Requirements: 12.1-12.9_

- [x] 17.2 Optimize slow operations
  - Profile slow operations
  - Add indexes if needed
  - Optimize database queries
  - Add caching where appropriate
  - _Requirements: 12.1-12.9_

- [x] 18. Migrate Existing Resources
  - Create migration script to chunk existing resources
  - _Requirements: 5.9, 5.10_

- [x] 18.1 Create Resource Migration Script
  - Add migrate_existing_resources.py to `backend/scripts/`
  - Query all resources without chunks (WHERE NOT EXISTS chunks)
  - Process resources in batches of 10
  - Call ChunkingService for each resource
  - Track progress (processed count, success count, failure count)
  - Log errors and continue processing
  - Support resume from last processed resource
  - _Requirements: 5.9, 5.10_

- [x] 18.2 Test migration script
  - Test with sample resources
  - Test batch processing
  - Test error handling and resume
  - Test progress tracking
  - _Requirements: 5.9, 5.10_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- Performance tests validate non-functional requirements
