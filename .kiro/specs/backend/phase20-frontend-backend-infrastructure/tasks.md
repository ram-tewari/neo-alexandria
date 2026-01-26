# Implementation Plan: Phase 20 Frontend-Backend Infrastructure Support

## ⚠️ CRITICAL: Leverage Existing Infrastructure

**DO NOT duplicate existing features!** This phase MUST use:
- ✅ **Embeddings**: Use `shared.embeddings.EmbeddingGenerator` (already exists)
- ✅ **DocumentChunk embeddings**: Use `DocumentChunk.embedding` field (already exists)
- ✅ **Static Analysis**: Use `graph.logic.static_analysis.StaticAnalysisService` (already exists)
- ✅ **Caching**: Use `shared.cache.CacheService` (already exists)
- ✅ **Event Bus**: Use `shared.event_bus` (already exists)
- ✅ **Database**: Use existing models and sessions (already exists)

See `DUPLICATE_AUDIT.md` for complete list of existing features.

## Overview

This implementation plan delivers 7 new capabilities and 3 extensions to existing services, organized into 4 phases. Total estimated time: 4-5 weeks.

**Key Principles**:
- Leverage existing infrastructure (embeddings, static analysis, chunking, event bus)
- Extend existing services minimally (PDF extractor, graph service, repo parser)
- Build only genuinely missing features
- Meet strict performance requirements

## Tasks

### Phase 1: Code Intelligence Extensions (Week 1)

- [ ] 1. Implement hover information API
  - [x] 1.1 Create hover information endpoint in graph router
    - Add GET `/code/hover` endpoint with file_path, line, column, resource_id parameters
    - Implement `HoverInformationResponse` schema with symbol info and related chunks
    - _Requirements: 1.1, 1.2, 1.3, 1.5_
  
  - [x] 1.2 Integrate with existing StaticAnalyzer and embeddings
    - Use existing `StaticAnalyzer` from `graph.logic.static_analysis`
    - Extract symbol information at specified position
    - Query DocumentChunk table for related chunks using EXISTING embeddings
    - Use cosine similarity with existing chunk.embedding field (threshold 0.7)
    - **LEVERAGES**: Existing `EmbeddingGenerator` from `shared.embeddings`, existing `DocumentChunk.embedding` field
    - _Requirements: 1.2, 1.3_
  
  - [x] 1.3 Implement response caching
    - Add Redis cache with 5-minute TTL
    - Cache key: `hover:{resource_id}:{file_path}:{line}:{column}`
    - _Requirements: 1.1_
  
  - [x] 1.4 Write property test for hover response time
    - **Property 1: Hover response time**
    - **Validates: Requirements 1.1**
  
  - [x] 1.5 Write property test for multi-language support

    - **Property 4: Multi-language support**
    - **Validates: Requirements 1.5**

  
  - [x] 1.6 Write unit tests for hover API

    - Test valid positions with symbols
    - Test invalid positions (edge case)
    - Test unsupported file types
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Checkpoint - Ensure hover API tests pass
  - Ensure all tests pass, ask the user if questions arise.

---

### Phase 2: Document Intelligence (Week 2)

- [x] 3. Extend PDF metadata extraction
  - [x] 3.1 Extend content_extractor.py for PDF metadata
    - **EXTEND EXISTING**: Modify `backend/app/utils/content_extractor.py` (DO NOT create new module)
    - Add `extract_metadata` parameter to EXISTING `extract_content` function
    - Extract page boundaries using PyPDF2 page-by-page extraction
    - Extract title, authors, abstract from PDF metadata
    - Store in `ContentExtractionResult.structured_metadata`
    - **LEVERAGES**: Existing PDF extraction with PyPDF2
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 3.2 Update resources module to store PDF metadata
    - **EXTEND EXISTING**: Update `backend/app/modules/resources/` (DO NOT create new module)
    - Store page boundaries in `resources.metadata.pdf_metadata`
    - Store structured metadata (title, authors, abstract)
    - **LEVERAGES**: Existing resources module infrastructure
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  
  - [ ]3.3 Write property test for page boundary preservation
    - **Property 5: Page boundary preservation**
    - **Validates: Requirements 2.1**
  
  - [x] 3.4 Write property test for metadata extraction

    - **Property 6: Metadata extraction completeness**
    - **Validates: Requirements 2.2, 2.3**
  
  - [] 3.5 Write unit tests for PDF extraction
    - Test PDFs with complete metadata
    - Test PDFs with missing metadata
    - Test single-page PDFs (edge case)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 4. Implement auto-linking service
  - [x] 4.1 Create ChunkLink database model
    - Add `chunk_links` table with source/target chunk IDs
    - Add similarity_score and link_type fields
    - Add indexes for efficient querying
    - Create Alembic migration
    - _Requirements: 3.4_
  
  - [x] 4.2 Implement AutoLinkingService class
    - Create service in `resources/service.py`
    - Implement `link_pdf_to_code` method
    - Implement `link_code_to_pdfs` method
    - **USE EXISTING**: `EmbeddingGenerator` from `shared.embeddings` (DO NOT create new embedding service)
    - **USE EXISTING**: `DocumentChunk.embedding` field (embeddings already exist!)
    - Compute cosine similarity between EXISTING chunk embeddings
    - Create bidirectional links for similarity > 0.7
    - **LEVERAGES**: Existing embedding infrastructure from Phase 17.5
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 4.3 Add auto-linking API endpoints
    - Add POST `/resources/{id}/auto-link` endpoint to EXISTING resources router
    - **USE EXISTING**: Event bus from `shared.event_bus` to trigger on ingestion
    - Emit `chunk.linked` event when links are created
    - **LEVERAGES**: Existing event-driven architecture
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 4.4 Write property test for similarity computation
    - **Property 8: Similarity computation**
    - **Validates: Requirements 3.1, 3.3**
  
  - [x] 4.5 Write property test for threshold-based linking
    - **Property 9: Threshold-based linking**
    - **Validates: Requirements 3.2**
  
  - [x] 4.6 Write property test for auto-linking performance
    - **Property 11: Auto-linking performance**
    - **Validates: Requirements 3.5**
  
  - [x] 4.7 Write unit tests for auto-linking
    - Test high similarity (>0.9)
    - Test threshold boundary (exactly 0.7)
    - Test no existing chunks (edge case)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Checkpoint - Ensure document intelligence tests pass
  - Ensure all tests pass, ask the user if questions arise.

---

### Phase 3: Graph Intelligence Extensions (Week 3)

- [x] 6. Extend graph service for centrality metrics
  - [x] 6.1 Add centrality computation methods to GraphService
    - **EXTEND EXISTING**: Add methods to `backend/app/modules/graph/service.py` (DO NOT create new module)
    - Implement `compute_degree_centrality` method
    - Implement `compute_betweenness_centrality` method
    - Implement `compute_pagerank` method with configurable damping factor
    - Use NetworkX built-in algorithms (already used in graph module)
    - **LEVERAGES**: Existing GraphService and NetworkX integration
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 6.2 Create GraphCentralityCache database model
    - Add `graph_centrality_cache` table
    - Store in-degree, out-degree, betweenness, pagerank
    - Add 10-minute TTL via computed_at timestamp
    - Create Alembic migration
    - _Requirements: 4.5_
  
  - [x] 6.3 Add centrality API endpoints
    - Add GET `/graph/centrality` endpoint to EXISTING graph router
    - Return `CentralityMetrics` for requested resources
    - **USE EXISTING**: `CacheService` from `shared.cache` for 10-minute TTL
    - **LEVERAGES**: Existing caching infrastructure
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [x] 6.4 Write property test for centrality completeness
    - **Property 12: Centrality metrics completeness**
    - **Validates: Requirements 4.1, 4.2, 4.3**
  
  - [x] 6.5 Write property test for centrality performance
    - **Property 13: Centrality performance**
    - **Validates: Requirements 4.4**
  
  - [x] 6.6 Write property test for centrality caching
    - **Property 14: Centrality caching**
    - **Validates: Requirements 4.5**

- [x] 7. Implement community detection service
  - [x] 7.1 Create CommunityDetectionService class
    - Create service in `backend/app/modules/graph/service.py` or separate service file
    - Implement `detect_communities` method
    - Use python-louvain library for Louvain algorithm
    - Compute modularity score
    - Support configurable resolution parameter
    - **LEVERAGES**: Existing graph module and NetworkX integration
    - _Requirements: 5.1, 5.2, 5.3, 5.5_
  
  - [x] 7.2 Create CommunityAssignment database model
    - Add `community_assignments` table
    - Store resource_id, community_id, modularity, resolution
    - Add 15-minute TTL via computed_at timestamp
    - Create Alembic migration
    - _Requirements: 5.2, 5.3_
  
  - [x] 7.3 Add community detection API endpoint
    - Add POST `/graph/communities` endpoint to EXISTING graph router
    - Return `CommunityDetectionResult`
    - **USE EXISTING**: `CacheService` from `shared.cache` for 15-minute TTL
    - **LEVERAGES**: Existing caching infrastructure
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 7.4 Write property test for community assignment completeness
    - **Property 15: Community assignment completeness**
    - **Validates: Requirements 5.2**
  
  - [x] 7.5 Write property test for modularity computation
    - **Property 16: Modularity computation**
    - **Validates: Requirements 5.3**
  
  - [x] 7.6 Write property test for community detection performance
    - **Property 17: Community detection performance**
    - **Validates: Requirements 5.4**

- [x] 8. Implement graph visualization service
  - [x] 8.1 Create GraphVisualizationService class
    - Create service in `backend/app/modules/graph/` (integrate with existing graph module)
    - Implement force-directed layout (Fruchterman-Reingold)
    - Implement hierarchical layout (Kamada-Kawai)
    - Implement circular layout
    - Normalize coordinates to [0, 1000] range
    - **LEVERAGES**: Existing NetworkX integration in graph module
    - _Requirements: 6.1, 6.2, 6.3, 6.5_
  
  - [x] 8.2 Add graph visualization API endpoint
    - Add POST `/graph/layout` endpoint to EXISTING graph router
    - Accept layout_type parameter ("force", "hierarchical", "circular")
    - Return `GraphLayoutResult` with node positions and edge routing
    - **USE EXISTING**: `CacheService` from `shared.cache` for 10-minute TTL
    - **LEVERAGES**: Existing caching infrastructure
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 8.3 Write property test for layout coordinate generation
    - **Property 19: Layout coordinate generation**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
  
  - [x] 8.4 Write property test for visualization performance
    - **Property 20: Visualization performance**
    - **Validates: Requirements 6.4**
  
  - [x] 8.5 Write unit tests for graph visualization
    - Test small graphs (10 nodes)
    - Test medium graphs (100 nodes)
    - Test single node (edge case)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9. Checkpoint - Ensure graph intelligence tests pass
  - Ensure all tests pass, ask the user if questions arise.

---

### Phase 4: AI Planning & MCP Infrastructure (Week 4-5)

- [x] 10. Implement multi-hop planning agent
  - [x] 10.1 Create planning module structure
    - Create `backend/app/modules/planning/` directory
    - Add `__init__.py`, `router.py`, `service.py`, `schema.py`, `model.py`
    - Register module in main.py
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 10.2 Create PlanningSession database model
    - Add `planning_sessions` table
    - Store task_description, context, steps, dependencies, status
    - Create Alembic migration
    - _Requirements: 7.1, 7.3, 7.5_
  
  - [x] 10.3 Implement MultiHopAgent class
    - Implement `generate_plan` method using LLM
    - Implement `refine_plan` method for iterative refinement
    - Maintain context history across steps
    - Extract dependencies from step descriptions
    - **LEVERAGES**: Existing LLM infrastructure if available
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
  
  - [x] 10.4 Add planning API endpoints
    - Add POST `/planning/generate` endpoint
    - Add PUT `/planning/{plan_id}/refine` endpoint
    - Add GET `/planning/{plan_id}` endpoint
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 10.5 Write property test for dependency DAG validity
    - **Property 21: Dependency DAG validity**
    - **Validates: Requirements 7.3**
  
  - [x] 10.6 Write property test for planning step performance
    - **Property 22: Planning step performance**
    - **Validates: Requirements 7.4**

- [x] 11. Implement architecture document parser
  - [x] 11.1 Create ArchitectureParser class
    - Implement `parse_architecture_doc` method
    - Extract components and relationships using LLM
    - Identify design patterns via pattern matching
    - **USE EXISTING**: `repo_parser` from `backend/app/utils/repo_parser.py` to compare with actual codebase
    - Detect gaps between documented and implemented
    - **LEVERAGES**: Existing RepositoryParser from Phase 18
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 11.2 Add architecture parsing API endpoint
    - Add POST `/planning/parse-architecture` endpoint
    - Accept resource_id parameter
    - Return `ArchitectureParseResult`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 11.3 Write property test for format support
    - **Property 23: Format support**
    - **Validates: Requirements 8.5**
  
  - [x] 11.4 Write unit tests for architecture parser
    - Test component extraction (example)
    - Test relationship extraction (example)
    - Test pattern recognition (example)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 12. Extend repository parser for best practices
  - [x] 12.1 Add best practices detection to RepositoryParser
    - **EXTEND EXISTING**: Add methods to `backend/app/utils/repo_parser.py` (DO NOT create new module)
    - Implement `detect_best_practices` method
    - **USE EXISTING**: AST parsing from `StaticAnalyzer` in `graph.logic.static_analysis`
    - Pattern matching for common best practices
    - Analyze test coverage and documentation
    - **LEVERAGES**: Existing RepositoryParser and StaticAnalyzer from Phase 18
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [x] 12.2 Implement reusable component extraction
    - **EXTEND EXISTING**: Add to `backend/app/utils/repo_parser.py`
    - Implement `extract_reusable_components` method
    - Extract interface definitions
    - Identify utility functions/classes
    - **LEVERAGES**: Existing RepositoryParser infrastructure
    - _Requirements: 9.2, 9.4_
  
  - [x] 12.3 Write property test for confidence score validity
    - **Property 24: Confidence score validity**
    - **Validates: Requirements 9.4**
  
  - [x] 12.4 Write property test for language support
    - **Property 25: Language support**
    - **Validates: Requirements 9.5**

- [x] 13. Implement MCP server infrastructure
  - [x] 13.1 Create MCP module structure
    - Create `backend/app/modules/mcp/` directory
    - Add `__init__.py`, `router.py`, `service.py`, `schema.py`, `model.py`
    - Register module in main.py
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_
  
  - [x] 13.2 Create MCPSession database model
    - Add `mcp_sessions` table
    - Store user_id, context, tool_invocations, status
    - Create Alembic migration
    - _Requirements: 10.6_
  
  - [x] 13.3 Implement ToolRegistry class
    - Define tool registration interface
    - Store tool schemas and handlers
    - Implement schema validation
    - _Requirements: 10.1, 10.2_
  
  - [x] 13.4 Implement MCPServer class
    - Implement `register_tool` method
    - Implement `invoke_tool` method with validation
    - Implement `list_tools` method
    - **USE EXISTING**: JWT authentication from `shared.oauth2` (Phase 17)
    - **USE EXISTING**: Rate limiting infrastructure (Phase 17)
    - **USE EXISTING**: Logging from existing infrastructure
    - **LEVERAGES**: Existing auth, rate limiting, and logging from Phase 17
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.7_
  
  - [x] 13.5 Register existing backend capabilities as MCP tools
    - Register search_resources tool
    - Register get_hover_info tool
    - Register compute_graph_metrics tool
    - Register detect_communities tool
    - Register generate_plan tool
    - Register parse_architecture tool
    - Register link_pdf_to_code tool
    - _Requirements: 10.1_
  
  - [x] 13.6 Add MCP API endpoints
    - Add GET `/mcp/tools` endpoint (list tools)
    - Add POST `/mcp/invoke` endpoint (invoke tool)
    - Add POST `/mcp/sessions` endpoint (create session)
    - Add DELETE `/mcp/sessions/{id}` endpoint (close session)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_
  
  - [x] 13.7 Write property test for schema validation
    - **Property 26: Schema validation**
    - **Validates: Requirements 10.2**
  
  - [x] 13.8 Write property test for authentication enforcement
    - **Property 28: Authentication enforcement**
    - **Validates: Requirements 10.4**
  
  - [x] 13.9 Write property test for rate limiting
    - **Property 29: Rate limiting**
    - **Validates: Requirements 10.5**
  
  - [x] 13.10 Write property test for session context preservation
    - **Property 30: Session context preservation**
    - **Validates: Requirements 10.6**
  
  - [x] 13.11 Write unit tests for MCP server
    - Test valid tool invocations
    - Test invalid tool names
    - Test schema validation failures
    - Test session management
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [x] 14. Integration and end-to-end testing
  - [x] 14.1 Write E2E test for code intelligence workflow
    - Ingest code repository
    - Request hover information
    - Verify chunks are linked
    - Verify performance
  
  - [x] 14.2 Write E2E test for document intelligence workflow
    - Ingest PDF document
    - Verify metadata extraction
    - Auto-link to existing code
    - Verify bidirectional links
  
  - [x] 14.3 Write E2E test for graph intelligence workflow
    - Build citation graph
    - Compute centrality metrics
    - Detect communities
    - Generate visualization layout
    - Verify consistency
  
  - [x] 14.4 Write E2E test for AI planning workflow
    - Submit planning request
    - Generate multi-step plan
    - Refine plan with feedback
    - Verify dependencies
  
  - [x] 14.5 Write E2E test for MCP workflow
    - Start MCP session
    - Invoke multiple tools
    - Verify context preservation
    - Close session

- [x] 15. Final checkpoint - Ensure all Phase 20 tests pass
  - Ensure all tests pass, ask the user if questions arise.

---

### Phase 5: Documentation (Week 5)

- [-] 16. Comprehensive Phase 20 documentation
  - [x] 16.1 Update backend/docs/api/ with all new endpoints
    - Document hover information endpoint in `api/graph.md`
    - Document auto-linking endpoint in `api/resources.md`
    - Document centrality metrics endpoint in `api/graph.md`
    - Document community detection endpoint in `api/graph.md`
    - Document graph visualization endpoint in `api/graph.md`
    - Create new `api/planning.md` for planning endpoints
    - Create new `api/mcp.md` for MCP server endpoints
    - Include request/response schemas, parameters, and examples
    - _Requirements: All Phase 20 requirements_
  
  - [x] 16.2 Update backend/docs/architecture/ with Phase 20 architecture
    - Update `architecture/overview.md` with new modules (planning, mcp)
    - Update `architecture/database.md` with new tables (ChunkLink, GraphCentralityCache, CommunityAssignment, PlanningSession, MCPSession)
    - Update `architecture/event-system.md` with new events (chunk.linked)
    - Create `architecture/phase20-features.md` documenting:
      - Code intelligence architecture
      - Document intelligence architecture
      - Graph intelligence architecture
      - AI planning architecture
      - MCP server architecture
    - _Requirements: All Phase 20 requirements_
  
  - [x] 16.3 Update backend/docs/guides/ with feature guides
    - Create `guides/code-intelligence.md` - How to use hover info and code navigation
    - Create `guides/document-intelligence.md` - How to use PDF metadata and auto-linking
    - Create `guides/graph-intelligence.md` - How to use centrality, communities, and visualization
    - Create `guides/ai-planning.md` - How to use multi-hop planning and architecture parsing
    - Create `guides/mcp-integration.md` - How to integrate with MCP server
    - Update `guides/testing.md` with Phase 20 test patterns
    - _Requirements: All Phase 20 requirements_
  
  - [x] 16.4 Update .kiro/steering/ documentation
    - Update `.kiro/steering/product.md`:
      - Add Phase 20 features to completed phases
      - Update success metrics with Phase 20 capabilities
      - Update roadmap themes
    - Update `.kiro/steering/tech.md`:
      - Add new dependencies (python-louvain, PyPDF2 enhancements)
      - Add new modules (planning, mcp) to module list
      - Add new commands for Phase 20 testing
      - Update performance requirements with Phase 20 metrics
    - Update `.kiro/steering/structure.md`:
      - Add planning and mcp modules to module list
      - Update event categories with chunk.linked
      - Update migration status to Phase 20 complete
      - Add Phase 20 to architecture achievements
    - _Requirements: All Phase 20 requirements_
  
  - [x] 16.5 Update backend/docs/index.md
    - Add Phase 20 section to documentation index
    - Link to all new API documentation
    - Link to all new architecture documentation
    - Link to all new feature guides
    - Update quick start guide with Phase 20 features
    - _Requirements: All Phase 20 requirements_
  
  - [ ] 16.6 Create Phase 20 summary document
    - Create `backend/docs/PHASE20_SUMMARY.md` documenting:
      - Overview of all Phase 20 features
      - Architecture decisions and rationale
      - Performance benchmarks achieved
      - Integration points with existing features
      - Migration guide from Phase 19
      - Known limitations and future work
      - Complete API endpoint list (7 new endpoints)
      - Complete database schema changes (5 new tables)
    - _Requirements: All Phase 20 requirements_

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (31 total)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- Documentation ensures Phase 20 is fully integrated into project knowledge base
- Total estimated time: 5 weeks (4 weeks implementation + 1 week documentation)
