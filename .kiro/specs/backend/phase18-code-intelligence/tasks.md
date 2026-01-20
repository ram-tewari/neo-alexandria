# Implementation Plan: Phase 18 - Code Intelligence Pipeline

## Overview

This implementation plan breaks down the Code Intelligence Pipeline into discrete, testable tasks. Each task builds on previous work and includes validation steps. The plan follows the vertical slice architecture and maintains zero circular dependencies.

## Tasks

- [x] 1. Install dependencies and verify Tree-Sitter
  - Add tree-sitter, tree-sitter-languages, gitpython, pathspec to requirements.txt
  - Create test script to verify Tree-Sitter can parse sample Python code
  - Verify all language grammars are available (Python, JS, TS, Rust, Go, Java)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 2. Implement file classification logic
  - [x] 2.1 Create file classification service
    - Implement `classify_file()` function in `app/modules/resources/logic/classification.py`
    - Support PRACTICE classification for code files (.py, .js, .ts, .rs, .go, .java)
    - Support THEORY classification for academic documents (.pdf, .md with academic keywords)
    - Support GOVERNANCE classification for policy files (CONTRIBUTING.md, CODE_OF_CONDUCT.md, .eslintrc)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 2.2 Write property test for file classification
    - **Property 4: File Classification Correctness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [x] 3. Implement repository ingestion service
  - [x] 3.1 Create RepoIngestionService class
    - Implement `crawl_directory()` method in `app/modules/resources/logic/repo_ingestion.py`
    - Implement recursive file discovery with Path.rglob()
    - Implement .gitignore parsing using pathspec library
    - Implement binary file detection (check for null bytes)
    - Store file path, repo_root in Resource metadata
    - _Requirements: 1.1, 1.3, 1.4, 1.5_

  - [x] 3.2 Implement Git repository cloning
    - Implement `clone_and_ingest()` method using gitpython
    - Clone to temporary directory with restricted permissions
    - Extract commit hash and branch name
    - Store commit_hash, branch in Resource metadata
    - Clean up temporary directory after ingestion
    - _Requirements: 1.2, 7.3, 7.4_

  - [x] 3.3 Write property tests for repository ingestion
    - **Property 1: Directory Crawling Completeness**
    - **Validates: Requirements 1.1, 1.5**
    - **Property 2: Gitignore Compliance**
    - **Validates: Requirements 1.3**
    - **Property 3: Binary File Exclusion**
    - **Validates: Requirements 1.4**

- [x] 4. Implement AST-based code chunking ✅ COMPLETE (Full Multi-Language Support)
  - [x] 4.1 Create CodeChunkingStrategy class
    - Implement `CodeChunkingStrategy` in `app/modules/resources/logic/chunking.py`
    - Initialize Tree-Sitter parser for given language
    - Implement `_parse_ast()` method to parse code into AST
    - Implement `_extract_logical_units()` to find functions and classes
    - Handle parsing errors with fallback to character-based chunking
    - _Requirements: 3.1, 3.2, 3.3, 3.7_

  - [x] 4.2 Implement chunk metadata creation
    - Implement `_create_chunk_from_unit()` method
    - Extract function_name, class_name from AST nodes
    - Extract start_line, end_line from AST node positions
    - Store language, type (function/class/method) in metadata
    - Create DocumentChunk with populated chunk_metadata JSON field
    - _Requirements: 3.4, 3.5_

  - [x] 4.3 Integrate CodeChunkingStrategy into ChunkingService
    - Update `ChunkingService.get_strategy()` to detect code files
    - Add language detection based on file extension
    - Return CodeChunkingStrategy for code files
    - Maintain backward compatibility with existing text strategies
    - _Requirements: 3.1_

  - [x] 4.4 Write property tests for code chunking
    - **Property 5: AST Logical Unit Extraction**
    - **Validates: Requirements 3.2, 3.3**
    - **Property 6: Code Chunk Metadata Completeness**
    - **Validates: Requirements 3.4, 3.5**
    - **Property 7: Parsing Fallback Safety**
    - **Validates: Requirements 3.7**
    - **All 16 property tests passing (100 examples each)**

  - [x] 4.5 Implement full multi-language AST extraction ✅ NEW
    - **Python**: functions, classes, methods (with parent class tracking)
    - **JavaScript**: functions, classes, methods (with class body traversal)
    - **TypeScript**: functions, classes, methods, interfaces
    - **Rust**: functions, structs, impl blocks, traits, methods within impl/trait
    - **Go**: functions, methods (with receiver), structs, interfaces
    - **Java**: classes, interfaces, methods, constructors (with visibility)
    - All extractors tested and verified working

- [x] 5. Checkpoint - Verify chunking works end-to-end
  - Create a test Python file with functions and classes
  - Manually trigger chunking via existing endpoint
  - Verify DocumentChunks are created with correct metadata
  - Ensure all tests pass, ask the user if questions arise

- [x] 6. Implement static analysis service
  - [x] 6.1 Create StaticAnalysisService class
    - Implement `StaticAnalysisService` in `app/modules/graph/logic/static_analysis.py`
    - Implement `analyze_code_chunk()` method to extract relationships
    - Implement `_extract_imports()` to find import statements
    - Implement `_extract_definitions()` to find class/function definitions
    - Implement `_extract_calls()` for basic function call detection
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 6.2 Create graph relationships with metadata
    - Create GraphRelationship entries with type IMPORTS, DEFINES, CALLS
    - Store source_file, target_symbol, line_number in metadata JSON
    - Store confidence score for ambiguous relationships
    - Ensure no code execution occurs (static analysis only)
    - _Requirements: 4.4, 4.5, 4.7_

  - [x] 6.3 Integrate static analysis into GraphExtractionService
    - Update `GraphExtractionService.extract_from_resource()` to detect code resources
    - Add `_extract_code_relationships()` method
    - Call StaticAnalysisService for code resources
    - Maintain backward compatibility with semantic extraction
    - _Requirements: 4.1_

  - [x] 6.4 Write property tests for static analysis
    - **Property 8: Static Analysis Relationship Extraction**
    - **Validates: Requirements 4.1, 4.2, 4.3**
    - **Property 9: Static Analysis Safety**
    - **Validates: Requirements 4.7**

- [x] 7. Implement async ingestion task
  - [x] 7.1 Create Celery task for repository ingestion
    - Implement `ingest_repo_task` in `app/tasks/celery_tasks.py`
    - Accept path or git_url parameter
    - Create async database session
    - Call RepoIngestionService to crawl/clone
    - Update task state with progress (PENDING → PROCESSING → COMPLETED)
    - _Requirements: 1.7, 5.1, 5.2_

  - [x] 7.2 Implement progress tracking
    - Update task state with files_processed, total_files, current_file
    - Emit resource.created events for each file
    - Handle errors gracefully and mark task as FAILED on exception
    - Log detailed error information for debugging
    - _Requirements: 5.3, 5.4, 5.5_

  - [x] 7.3 Write property tests for task lifecycle
    - **Property 10: Task State Transitions**
    - **Validates: Requirements 5.1, 5.2, 5.4**

- [ ] 8. Implement API endpoints
  - [x] 8.1 Create repository ingestion endpoint
    - Add POST /resources/ingest-repo endpoint in `app/modules/resources/router.py`
    - Create RepoIngestionRequest schema (path, git_url)
    - Validate that path exists or URL is valid
    - Trigger ingest_repo_task and return task ID
    - Require authentication and apply rate limiting
    - _Requirements: 6.1, 6.3, 6.4, 6.5_

  - [x] 8.2 Create ingestion status endpoint
    - Add GET /resources/ingest-repo/{task_id}/status endpoint
    - Create IngestionStatusResponse schema
    - Query Celery task state and return progress
    - Include files_processed, total_files, current_file in response
    - Require authentication
    - _Requirements: 6.2, 6.6_

  - [x] 8.3 Write integration tests for API endpoints
    - Test POST /resources/ingest-repo with mock directory
    - Test GET /resources/ingest-repo/{task_id}/status
    - Test authentication and rate limiting
    - Test error handling (invalid path, invalid URL)

- [x] 9. Checkpoint - Verify API works end-to-end
  - Create a small test repository with 5-10 files
  - Call POST /resources/ingest-repo via API
  - Poll GET /resources/ingest-repo/{task_id}/status until complete
  - Verify Resources, DocumentChunks, and GraphRelationships are created
  - Ensure all tests pass, ask the user if questions arise

- [-] 10. Implement error handling and resilience
  - [x] 10.1 Add file-level error handling
    - Wrap file processing in try-except blocks
    - Log errors and continue processing other files
    - Track failed files in task metadata
    - _Requirements: 9.1, 9.2, 9.3_

  - [x] 10.2 Add transaction management
    - Process files in batches of 50
    - Commit database transactions per batch
    - Rollback on database errors and mark task as FAILED
    - Allow task retry after failure
    - _Requirements: 9.5, 9.6_

  - [ ] 10.3 Write property tests for error handling
    - **Property 12: Graceful Error Handling**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.5, 9.6**

- [x] 11. Implement performance optimizations
  - [x] 11.1 Add batch processing
    - Process files in batches of 50 to avoid memory exhaustion
    - Emit events per batch instead of per file
    - Use generators for directory traversal
    - _Requirements: 10.1_

  - [x] 11.2 Add caching
    - Cache Tree-Sitter parsers (one per language)
    - Cache .gitignore patterns per repository
    - Cache file classification rules
    - _Requirements: 10.2, 10.3_

  - [x] 11.3 Add concurrency limits
    - Limit concurrent ingestion tasks to 3 per user
    - Configure Celery worker pool size
    - Add task timeout (30 minutes for 1000 files)
    - _Requirements: 10.4, 10.5_

  - [x] 11.4 Write performance tests
    - **Property 13: Performance Bounds**
    - **Validates: Requirements 10.2, 10.3**
    - Benchmark AST parsing speed (should be < 2s per file P95)
    - Benchmark static analysis speed (should be < 1s per file P95)

- [x] 12. Update documentation
  - [x] 12.1 Update API documentation
    - Add POST /resources/ingest-repo to `backend/docs/api/resources.md`
    - Add GET /resources/ingest-repo/{task_id}/status to `backend/docs/api/resources.md`
    - Document request/response schemas
    - Add example requests and responses
    - _Requirements: 6.1, 6.2_

  - [x] 12.2 Update graph API documentation
    - Update `backend/docs/api/graph.md` to include code relationship types
    - Document IMPORTS, DEFINES, CALLS relationship types
    - Add examples of code graph queries
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 12.3 Update architecture documentation
    - Update `backend/docs/architecture/modules.md` for Resources module
    - Update `backend/docs/architecture/modules.md` for Graph module
    - Document AST chunking and static analysis capabilities
    - Add architecture diagrams for code pipeline
    - _Requirements: All_

  - [x] 12.4 Create code ingestion guide
    - Create `backend/docs/guides/code-ingestion.md`
    - Explain how to ingest local repositories
    - Explain how to ingest Git repositories
    - Document supported languages and file types
    - Provide troubleshooting tips
    - _Requirements: All_

  - [x] 12.5 Update documentation index and changelog
    - Update `backend/docs/index.md` to link to code-ingestion.md
    - Update `backend/docs/CHANGELOG.md` with Phase 18 entry
    - Update `backend/README.md` to mention code intelligence features
    - _Requirements: All_

- [x] 13. Final checkpoint - Run full test suite
  - Run all unit tests: `pytest tests/modules/resources/ tests/modules/graph/ tests/tasks/ -v`
  - Run all property tests: `pytest tests/properties/test_code_intelligence_properties.py -v`
  - Run all integration tests: `pytest tests/integration/test_code_pipeline.py -v`
  - Run performance tests: `pytest tests/performance/test_code_intelligence_performance.py -v`
  - Verify all tests pass with >90% coverage
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- Performance tests validate latency and throughput requirements

## Dependencies

- tree-sitter==0.20.4
- tree-sitter-languages==1.10.2
- gitpython==3.1.40
- pathspec==0.12.1

## Success Criteria

- [ ] Can ingest local directory with 100+ files
- [ ] Can ingest Git repository from URL
- [ ] Code files are chunked by functions/classes with metadata
- [ ] Graph relationships extracted for imports/definitions/calls
- [ ] API endpoints work with authentication and rate limiting
- [ ] All tests pass with >90% coverage
- [ ] Documentation is complete and accurate
- [ ] Performance requirements met (P95 < 2s parsing, < 1s extraction)
