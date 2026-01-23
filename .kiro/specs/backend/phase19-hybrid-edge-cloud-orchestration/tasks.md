# Implementation Plan: Phase 19 - Hybrid Edge-Cloud Orchestration & Neural Graph Learning

## Overview

This implementation plan breaks down the hybrid edge-cloud architecture into incremental, testable steps. The approach follows a bottom-up strategy: build core services first, then integrate them into the cloud API and edge worker, and finally deploy and test the complete system.

## Tasks

- [x] 1. Set up project structure and configuration management
  - Create `requirements-base.txt` with shared dependencies (upstash-redis, gitpython, fastapi, uvicorn, pydantic, python-dotenv)
  - Create `requirements-cloud.txt` extending base with "-r requirements-base.txt" and cloud-specific deps (psycopg2-binary, qdrant-client)
  - Create `requirements-edge.txt` extending base with "-r requirements-base.txt" and full ML dependencies (torch, torch-geometric, tree-sitter, qdrant-client, numpy, psycopg2-binary)
  - Implement MODE-aware configuration in `app/core/config.py` that conditionally loads torch
  - Create `.env.cloud.template` and `.env.edge.template` configuration files
  - Add configuration validation that checks required environment variables on startup
  - Add PHAROS_ADMIN_TOKEN to environment variable templates with documentation
  - Document the base + extension strategy to prevent dependency hell
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 2.8_

- [x] 1.1 Write unit tests for configuration management
  - Test MODE=CLOUD doesn't import torch modules
  - Test MODE=EDGE verifies CUDA and logs GPU info
  - Test environment variable validation catches missing vars
  - Test requirements-base.txt is properly inherited by cloud and edge
  - Test version consistency across requirements files
  - _Requirements: 7.1, 7.2, 7.3, 7.6, 7.7, 7.8_

- [x] 2. Implement Repository Parser service
  - [x] 2.1 Create `app/utils/repo_parser.py` with RepositoryParser class
    - Implement `clone_repository()` method using GitPython
    - Implement `_find_source_files()` method to discover Python, JS, TS files
    - Implement cleanup method to remove temporary directories
    - _Requirements: 4.1, 11.5, 11.6_
  
  - [x] 2.2 Implement Tree-sitter parsing for import extraction
    - Initialize Tree-sitter parsers for Python, JavaScript, TypeScript
    - Implement `_extract_imports()` method with language detection
    - Implement `_extract_python_imports()` for Python import statements
    - Implement `_extract_javascript_imports()` for JS/TS import statements
    - Add error handling for parse failures (log and continue)
    - _Requirements: 4.2, 4.4, 4.5_
  
  - [x] 2.3 Implement dependency graph construction
    - Implement `build_dependency_graph()` method
    - Create file-to-index mapping for graph nodes
    - Implement `_resolve_import()` for relative and absolute imports
    - Build PyTorch edge_index tensor from import relationships
    - Handle empty graphs with self-loops
    - Return DependencyGraph object with edge_index and file_paths
    - _Requirements: 4.3_

- [x] 2.4 Write property tests for repository parser
  - **Property 5: Repository processing pipeline completeness**
  - **Validates: Requirements 4.1, 4.2, 4.3**
  - Test that for any repository, all source files are parsed and graph is built
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 2.5 Write unit tests for repository parser
  - Test clone with valid repository URL
  - Test parse error handling (continues with remaining files)
  - Test multi-language support (Python, JS, TS)
  - Test temporary directory cleanup
  - _Requirements: 4.1, 4.4, 4.5, 11.6_

- [x] 3. Implement Neural Graph Service
  - [x] 3.1 Create `app/services/neural_graph.py` with NeuralGraphService class
    - Initialize with device parameter (cuda/cpu)
    - Set hyperparameters (embedding_dim=64, walk_length=20, context_size=10, walks_per_node=10)
    - _Requirements: 5.2, 5.3_
  
  - [x] 3.2 Implement Node2Vec training
    - Implement `train_embeddings()` method using PyTorch Geometric Node2Vec
    - Create data loader with batch_size=128
    - Implement training loop for 10 epochs with SparseAdam optimizer
    - Log training loss every 5 epochs
    - Return embeddings as CPU tensors
    - _Requirements: 5.1, 5.2, 5.4, 5.5, 5.6_
  
  - [x] 3.3 Implement Qdrant upload functionality
    - Implement `upload_embeddings()` method
    - Create Qdrant collection if it doesn't exist
    - Prepare PointStruct objects with embeddings and metadata
    - Implement batch upload with batch_size=100
    - Add retry logic with exponential backoff (3 attempts)
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 3.4 Write property tests for neural graph service
  - **Property 6: Embedding dimensionality invariant**
  - **Validates: Requirements 5.2**
  - Test that for any graph with N nodes, exactly N embeddings of 64 dimensions are generated
  - **Property 7: Embedding device location**
  - **Validates: Requirements 5.6**
  - Test that all returned embeddings are CPU tensors
  - **Property 8: Embedding upload completeness**
  - **Validates: Requirements 6.1, 6.2**
  - Test that all embeddings are uploaded with file_path and repo_url in payload
  - _Requirements: 5.2, 5.6, 6.1, 6.2_

- [x] 3.5 Write unit tests for neural graph service
  - Test training loss logging every 5 epochs
  - Test batch upload to Qdrant
  - Test retry logic on upload failure
  - _Requirements: 5.5, 6.3, 6.4_

- [x] 4. Checkpoint - Ensure core services work
  - Ensure all tests pass for repository parser and neural graph service
  - Verify services can be imported without errors
  - Ask the user if questions arise
  - **Note**: Neural graph tests require Linux environment with torch-cluster. Verified on Windows: service imports successfully, code structure correct. Full test verification deferred to task 5.7 on Linux/Edge environment.

- [x] 5. Implement Cloud API endpoints
  - [x] 5.1 Create `app/routers/ingestion.py` with ingestion endpoints
    - Implement Bearer token authentication using HTTPBearer and PHAROS_ADMIN_TOKEN
    - Implement POST `/api/v1/ingestion/ingest/{repo_url}` endpoint
    - Add URL validation using regex or urllib.parse
    - Check queue size and reject if >= 10 pending tasks (return 429)
    - Create task metadata with repo_url, submitted_at timestamp, and TTL
    - Push task as JSON to Upstash Redis queue using RPUSH
    - Set TTL on queue key using EXPIRE
    - Return IngestionResponse with job_id, queue_position, and queue_size
    - Handle Redis unavailable with 503 status code
    - Handle invalid/missing token with 401 status code
    - _Requirements: 2.1, 2.2, 2.4, 2.5, 2.6, 2.7, 2.8_
  
  - [x] 5.2 Implement worker status endpoint
    - Implement GET `/api/v1/ingestion/worker/status` endpoint
    - Fetch current status from Redis using GET
    - Return status or "Offline" if not available
    - Handle Redis errors gracefully
    - _Requirements: 2.3_
  
  - [x] 5.3 Implement job history endpoint
    - Implement GET `/api/v1/ingestion/jobs/history` endpoint
    - Fetch last N jobs from Redis using LRANGE
    - Parse JSON job records
    - Return list of job objects
    - _Requirements: 9.6_
  
  - [x] 5.4 Add health check endpoint
    - Implement GET `/health` endpoint
    - Check connections to Redis, Neon, Qdrant
    - Return 200 if healthy, 503 if any service unavailable
    - _Requirements: 12.6_

- [x] 5.5 Write property tests for cloud API
  - **Property 1: Task queue round trip**
  - **Validates: Requirements 2.1, 2.2**
  - Test that for any valid repo URL with valid token, task appears in queue and response contains job_id
  - **Property 3: URL validation rejects invalid input**
  - **Validates: Requirements 2.4, 11.4**
  - Test that malformed URLs are rejected with 400 status
  - **Property 4: Status endpoint reflects Redis state**
  - **Validates: Requirements 2.3**
  - Test that status endpoint returns exact value from Redis
  - **Property 15: Error status codes**
  - **Validates: Requirements 8.5**
  - Test that error conditions return appropriate HTTP status codes
  - **Property 16: Queue cap enforcement**
  - **Validates: Requirements 2.6**
  - Test that queue rejects new tasks when >= 10 pending
  - **Property 17: Authentication required**
  - **Validates: Requirements 2.8**
  - Test that requests without valid token are rejected with 401
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 2.8, 8.5, 11.4_

- [x] 5.6 Write unit tests for cloud API
  - Test MODE=CLOUD doesn't load torch (1.2)
  - Test database connection check
  - Test Qdrant connection check
  - Test Redis connection check
  - Test 503 when Redis unavailable
  - Test 429 when queue is full (>= 10 tasks)
  - Test 401 when token is invalid or missing
  - Test authentication failure logging
  - Test health check endpoint
  - Test GET /worker/status returns real-time updates for UI
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 2.5, 2.6, 2.8, 2.9, 2.10, 12.6_

- [x] 5.7 Verify neural graph service on Linux (Edge environment)
  - Run neural graph unit tests on Linux with torch-cluster installed
  - Run neural graph property tests on Linux
  - Verify all 7 unit tests pass
  - Verify all 3 property tests pass
  - Document any environment-specific issues
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4_

- [x] 6. Implement Edge Worker
  - [x] 6.1 Create `worker.py` main worker script
    - Initialize Redis client with Upstash credentials
    - Detect CUDA availability and log hardware configuration
    - Set worker status to "Idle" on startup
    - Implement main loop that polls queue every 2 seconds
    - Handle SIGINT for graceful shutdown
    - _Requirements: 3.1, 3.2, 3.4, 8.3_
  
  - [x] 6.2 Implement job processing function
    - Implement `process_job(task_data)` function that accepts task metadata dict
    - Parse task_data to extract repo_url, submitted_at, and ttl
    - Check if task age exceeds TTL and skip if stale
    - Record skipped tasks in job_history with reason
    - Update status to "Training Graph on {repo_url}"
    - Call RepositoryParser to clone and parse repository
    - Call NeuralGraphService to train embeddings
    - Call NeuralGraphService to upload embeddings
    - Record job completion in job_history with all metrics
    - Update status back to "Idle"
    - _Requirements: 3.5, 3.7, 6.5, 9.3, 9.4_
  
  - [x] 6.3 Implement error handling in worker
    - Catch clone failures, mark job as failed, continue to next job
    - Catch training failures, mark job as failed, clean up GPU memory
    - Catch upload failures, mark job as failed after retries
    - Catch Redis connection errors, attempt reconnection
    - Always clean up temporary files in finally block
    - _Requirements: 8.1, 8.2, 8.6, 11.6_
  
  - [x] 6.4 Implement job history management
    - Push job records to Redis job_history list
    - Trim list to 100 most recent entries using LTRIM
    - Include all required fields in job record JSON
    - _Requirements: 9.3, 9.4, 9.6_

- [x] 6.5 Write property tests for edge worker
  - **Property 2: Worker status consistency**
  - **Validates: Requirements 3.5, 6.5**
  - Test that status transitions from Idle → Training → Idle for any job
  - **Property 9: Job history record completeness**
  - **Validates: Requirements 9.3, 9.4**
  - Test that job records contain all required fields
  - **Property 10: Job history size cap**
  - **Validates: Requirements 9.6**
  - Test that job_history list is capped at 100 entries
  - **Property 11: Status format validation**
  - **Validates: Requirements 9.1**
  - Test that status strings match expected patterns
  - **Property 18: Stale task handling**
  - **Validates: Requirements 3.7**
  - Test that tasks older than TTL are skipped and marked as "skipped"
  - _Requirements: 3.5, 3.7, 6.5, 9.1, 9.3, 9.4, 9.6_

- [x] 6.6 Write unit tests for edge worker
  - Test CUDA detection and GPU logging
  - Test CPU fallback when CUDA unavailable
  - Test error continuation (doesn't crash on errors)
  - Test clone failure handling
  - Test Redis reconnection logic
  - Test worker startup command works
  - Test stale task detection and skipping
  - Test backward compatibility with legacy string format tasks
  - _Requirements: 3.1, 3.2, 3.6, 3.7, 8.2, 8.6, 12.2_

- [x] 7. Checkpoint - Ensure cloud and edge components work independently
  - Ensure all tests pass for cloud API and edge worker
  - Verify cloud API can start in MODE=CLOUD without torch
  - Verify edge worker can start in MODE=EDGE with torch
  - Ask the user if questions arise

- [x] 7.5 Final Graph Service Verification (Pre-Deployment)
  - [x] 7.5.1 Set up proper Linux/Edge environment for torch-cluster
    - Install torch-cluster using Docker with pre-built wheels OR conda environment
    - Verify CUDA availability and GPU detection
    - Document environment setup steps
    - _Requirements: 5.1, 5.6_
  
  - [x] 7.5.2 Run complete neural graph test suite
    - Run all 7 neural graph unit tests in `tests/test_neural_graph.py`
    - Verify test_initialization passes
    - Verify test_train_embeddings_shape passes
    - Verify test_train_embeddings_device passes
    - Verify test_train_embeddings_logging passes
    - Verify test_upload_embeddings_batch passes
    - Verify test_upload_embeddings_retry passes
    - Verify test_upload_embeddings_collection_creation passes
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4_
  
  - [x] 7.5.3 Run neural graph property tests
    - Run all 3 property tests in `tests/properties/test_neural_graph_properties.py`
    - Verify Property 6: Embedding dimensionality invariant passes
    - Verify Property 7: Embedding device location passes
    - Verify Property 8: Embedding upload completeness passes
    - _Requirements: 5.2, 5.6, 6.1, 6.2_
  
  - [x] 7.5.4 Run repository parser tests
    - Run all repository parser unit tests in `tests/test_repo_parser.py`
    - Run repository parser property tests in `tests/properties/test_repo_parser_properties.py`
    - Verify all tests pass
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 7.5.5 End-to-end graph generation verification
    - Create test script that runs complete pipeline:
      1. Clone a small test repository
      2. Parse repository and build dependency graph
      3. Train embeddings on dependency graph
      4. Upload embeddings to Qdrant (test instance)
      5. Verify embeddings are retrievable from Qdrant
    - Document results and any issues encountered
    - Verify GPU utilization during training
    - Verify memory cleanup after completion
    - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4_
  
  - [x] 7.5.6 Document verification results
    - Create `PHASE19_GRAPH_SERVICE_VERIFICATION.md` with:
      - Environment setup details (OS, CUDA version, GPU model)
      - Test results summary (all tests passed/failed)
      - Performance metrics (training time, GPU utilization)
      - Any environment-specific issues and workarounds
      - Recommendations for production deployment
    - Update `PHASE19_WSL_TEST_RESULTS.md` with final verification status
    - _Requirements: All graph-related requirements_

- [x] 8. Implement security features
  - [x] 8.1 Add URL sanitization to cloud API
    - Implement `is_valid_repo_url()` validation function
    - Check for malicious patterns (command injection, path traversal)
    - Validate URL format and protocol
    - _Requirements: 11.4_
  
  - [x] 8.2 Add credential validation
    - Validate Redis credentials on Cloud API startup
    - Validate Redis credentials on Edge Worker startup
    - Fail fast with clear error messages if credentials invalid
    - _Requirements: 11.1, 11.2_
  
  - [x] 8.3 Enforce HTTPS for external APIs
    - Verify all Neon, Qdrant, Upstash URLs use https://
    - Add validation in configuration loading
    - Raise error if non-HTTPS URLs detected
    - _Requirements: 11.3_
  
  - [x] 8.4 Implement temporary directory isolation
    - Use `tempfile.mkdtemp()` with unique prefixes for each clone
    - Verify different jobs use different temp directories
    - _Requirements: 11.5_

- [x] 8.5 Write property tests for security
  - **Property 12: HTTPS protocol enforcement**
  - **Validates: Requirements 11.3**
  - Test that all external API URLs use HTTPS
  - **Property 13: Temporary directory isolation**
  - **Validates: Requirements 11.5**
  - Test that concurrent clones use different temp directories
  - **Property 14: Cleanup removes temporary files**
  - **Validates: Requirements 11.6**
  - Test that temp directories are removed after jobs
  - _Requirements: 11.3, 11.5, 11.6_

- [x] 8.6 Write unit tests for security
  - Test credential validation with invalid credentials
  - Test URL sanitization rejects malicious inputs
  - _Requirements: 11.1, 11.2, 11.4_

- [x] 9. Create deployment configurations
  - [x] 9.1 Create Render deployment configuration
    - Create `render.yaml` with service configuration
    - Set MODE=CLOUD environment variable
    - Configure health check path
    - Set resource limits for free tier
    - _Requirements: 12.1_
  
  - [x] 9.2 Create edge worker setup scripts
    - Create `setup_edge.sh` for Linux/macOS
    - Create `setup_edge.ps1` for Windows
    - Add CUDA verification step
    - Create systemd service file for Linux
    - Create NSSM service configuration for Windows
    - _Requirements: 12.2_
  
  - [x] 9.3 Create infrastructure setup guide
    - Document Neon database provisioning steps
    - Document Qdrant Cloud setup steps
    - Document Upstash Redis setup steps
    - Create step-by-step deployment guide
    - _Requirements: 12.3_

- [x] 10. Integration testing
  - [x] 10.1 Create end-to-end workflow test
    - Start Cloud API in test mode
    - Start Edge Worker in test mode (CPU)
    - Submit test repository URL via API
    - Verify task appears in Redis queue
    - Verify worker picks up and processes task
    - Verify embeddings uploaded to Qdrant
    - Verify job history updated correctly
    - Verify worker returns to idle status
    - _Requirements: All_
  
  - [x] 10.2 Create multi-repository test
    - Queue multiple test repositories
    - Verify sequential processing
    - Verify status updates for each job
    - Verify all embeddings uploaded
    - Verify job history contains all jobs
    - _Requirements: All_

- [x] 10.3 Write integration tests
  - Test end-to-end workflow
  - Test multi-repository processing
  - Test error recovery scenarios
  - _Requirements: All_

- [x] 11. Performance and stress testing
  - [x] 11.1 Create performance benchmarks
    - Measure API dispatch latency (target: <100ms)
    - Measure embedding generation time (target: <5min for 100 files)
    - Measure GPU utilization (target: >70%)
    - Measure throughput (target: >10 repos/hour)
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [x] 11.2 Create stress tests
    - Test with large repository (10,000 files)
    - Test with 100 concurrent API requests
    - Test with queue of 1000 repositories
    - Test with limited GPU memory scenarios
    - _Requirements: 10.5_

- [x] 11.3 Write performance tests
  - Test API dispatch latency
  - Test embedding generation time
  - Test large repository handling
  - _Requirements: 10.1, 10.2, 10.5_

- [x] 12. Documentation and deployment
  - [x] 12.1 Create deployment documentation in docs/guides/
    - Create `docs/guides/phase19-deployment.md` - Cloud deployment guide
    - Create `docs/guides/phase19-edge-setup.md` - Edge worker setup guide
    - Document environment variable configuration
    - Create troubleshooting section
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [x] 12.2 Create monitoring documentation in docs/guides/
    - Create `docs/guides/phase19-monitoring.md` - Monitoring guide
    - Document how to check worker status via API
    - Document how to view job history
    - Document GPU monitoring with nvidia-smi
    - Document log locations and formats
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 12.3 Update main project documentation in docs/
    - Update `docs/architecture/overview.md` - Add Phase 19 hybrid architecture
    - Update `docs/api/ingestion.md` - Document new ingestion endpoints
    - Create `docs/architecture/phase19-hybrid.md` - Hybrid architecture diagram and explanation
    - Update `docs/index.md` - Add Phase 19 to documentation index
    - Document cost analysis and scaling options in architecture docs
    - _Requirements: All_

- [x] 13. Final checkpoint - Complete system verification
  - Ensure all tests pass (unit, property, integration, performance)
  - Verify cloud API can be deployed to Render
  - Verify edge worker can run locally
  - Verify end-to-end workflow works
  - Ask the user if questions arise

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate complete workflows
- Performance tests validate scalability requirements

## Implementation Order Rationale

1. **Configuration First**: Ensures MODE-aware loading works before building components
2. **Core Services**: Build repository parser and neural graph service independently
3. **API Layer**: Implement cloud API endpoints that dispatch to queue
4. **Worker Layer**: Implement edge worker that consumes from queue
5. **Security**: Add security features after core functionality works
6. **Deployment**: Create deployment configurations and documentation
7. **Testing**: Integration and performance testing after all components integrated
8. **Documentation**: Final documentation after system is complete

## Estimated Timeline

- Tasks 1-4: 2-3 days (core services)
- Tasks 5-7: 2-3 days (API and worker)
- Tasks 8-9: 1-2 days (security and deployment)
- Tasks 10-11: 2-3 days (testing)
- Tasks 12-13: 1-2 days (documentation)
- **Total: 8-13 days** (depending on optional tasks)

## Success Criteria

- [ ] All unit tests pass
- [ ] All property tests pass (100+ iterations each)
- [ ] Integration tests pass end-to-end
- [ ] Cloud API deploys successfully to Render
- [ ] Edge worker runs successfully on local GPU
- [ ] Complete workflow: submit URL → process → embeddings in Qdrant
- [ ] Documentation complete and accurate
- [ ] Cost remains at $0/month for free tier
