# Requirements Document: Phase 19 - Hybrid Edge-Cloud Orchestration & Neural Graph Learning

## Introduction

This specification defines the requirements for splitting Neo Alexandria's monolithic backend into a hybrid architecture consisting of a lightweight Cloud API (Render Free Tier) and a powerful Edge Worker (local laptop with GPU). The system will implement PyTorch Geometric for graph representation learning on code repositories, generating structural embeddings based on dependency graphs rather than just text content.

## Glossary

- **Cloud_API**: The stateless FastAPI control plane deployed on Render Free Tier (512MB RAM)
- **Edge_Worker**: The stateful Python worker running locally on laptop hardware (i9/RTX 4070/16GB RAM)
- **Task_Queue**: Upstash Redis queue that bridges Cloud and Edge components
- **Neural_Graph_Service**: PyTorch Geometric service that generates structural embeddings using Node2Vec
- **Dependency_Graph**: Graph representation of code repository where nodes are files and edges are import relationships
- **Structural_Embedding**: Vector representation of code files based on their position in the dependency graph
- **Node2Vec**: Graph representation learning algorithm that generates embeddings via random walks
- **Neon_Database**: Serverless PostgreSQL database for metadata storage
- **Qdrant_Cloud**: Cloud-hosted vector database for embedding storage
- **Upstash_Redis**: HTTP-based Redis service for task queue and status tracking

## Requirements

### Requirement 1: Cloud API Infrastructure

**User Story:** As a system architect, I want a lightweight cloud API that dispatches tasks without heavy ML dependencies, so that I can run on free-tier hosting with minimal resource consumption.

#### Acceptance Criteria

1. THE Cloud_API SHALL run on Render Free Tier with 512MB RAM or less
2. WHEN the Cloud_API starts, THE Cloud_API SHALL NOT load PyTorch, Transformers, or other heavy ML libraries
3. THE Cloud_API SHALL connect to Neon_Database for metadata operations
4. THE Cloud_API SHALL connect to Qdrant_Cloud for vector search operations
5. THE Cloud_API SHALL connect to Upstash_Redis for task queue operations
6. WHEN the Cloud_API receives a request, THE Cloud_API SHALL respond within 200ms for non-ML operations

### Requirement 2: Task Dispatch and Queue Management

**User Story:** As a developer, I want to submit code repository ingestion tasks through the cloud API, so that the edge worker can process them asynchronously.

#### Acceptance Criteria

1. WHEN a user submits a repository URL via POST /ingest/{repo_url}, THE Cloud_API SHALL push the task to the Task_Queue
2. WHEN a task is queued, THE Cloud_API SHALL return a job ID and queue position to the user
3. WHEN a user requests GET /worker/status, THE Cloud_API SHALL return the current Edge_Worker status from Redis
4. THE Cloud_API SHALL validate repository URLs before queuing tasks
5. IF the Task_Queue is unavailable, THEN THE Cloud_API SHALL return an error with status code 503
6. WHEN the Task_Queue has 10 or more pending tasks, THE Cloud_API SHALL reject new tasks with status code 429
7. WHEN a task is queued, THE Cloud_API SHALL set a TTL of 24 hours on the task
8. THE Cloud_API SHALL require Bearer token authentication (PHAROS_ADMIN_TOKEN) for the /ingest endpoint
9. WHEN the Cloud_API receives a request without valid authentication, THE Cloud_API SHALL return status code 401
10. THE Cloud_API SHALL log all authentication failures for security monitoring

### Requirement 3: Edge Worker Infrastructure

**User Story:** As a system architect, I want a local edge worker that leverages GPU hardware for ML operations, so that I can perform compute-intensive tasks without cloud costs.

#### Acceptance Criteria

1. THE Edge_Worker SHALL detect and utilize CUDA-enabled GPU when available
2. WHEN CUDA is unavailable, THE Edge_Worker SHALL fall back to CPU processing
3. THE Edge_Worker SHALL poll the Task_Queue for new jobs every 2 seconds when idle
4. WHEN the Edge_Worker starts, THE Edge_Worker SHALL log the detected hardware configuration
5. THE Edge_Worker SHALL update worker status in Redis before and after processing each job
6. WHEN the Edge_Worker encounters an error, THE Edge_Worker SHALL log the error to Redis and continue processing
7. WHEN the Edge_Worker receives a task older than its TTL, THE Edge_Worker SHALL skip it and mark it as "skipped" in job history

### Requirement 4: Repository Processing Pipeline

**User Story:** As a developer, I want the edge worker to clone, parse, and analyze code repositories, so that I can generate structural embeddings for code search.

#### Acceptance Criteria

1. WHEN the Edge_Worker receives a repository URL, THE Edge_Worker SHALL clone the repository to local storage
2. WHEN a repository is cloned, THE Edge_Worker SHALL parse all source files to extract import statements
3. THE Edge_Worker SHALL build a Dependency_Graph from the parsed import relationships
4. WHEN parsing fails for a file, THE Edge_Worker SHALL log the error and continue with remaining files
5. THE Edge_Worker SHALL support Python, JavaScript, TypeScript, Java, and Go import parsing

### Requirement 5: Graph Representation Learning

**User Story:** As a data scientist, I want to generate structural embeddings using Node2Vec on the dependency graph, so that code files can be searched by their structural relationships.

#### Acceptance Criteria

1. THE Neural_Graph_Service SHALL implement Node2Vec using PyTorch Geometric
2. THE Neural_Graph_Service SHALL generate 64-dimensional embeddings for each file node
3. THE Neural_Graph_Service SHALL use walk length of 20, context size of 10, and 10 walks per node
4. WHEN training Node2Vec, THE Neural_Graph_Service SHALL run for 10 epochs minimum
5. THE Neural_Graph_Service SHALL log training loss every 5 epochs
6. WHEN training completes, THE Neural_Graph_Service SHALL return embeddings as CPU tensors

### Requirement 6: Embedding Storage and Retrieval

**User Story:** As a developer, I want structural embeddings stored in Qdrant Cloud, so that they can be searched alongside text-based embeddings.

#### Acceptance Criteria

1. WHEN embeddings are generated, THE Edge_Worker SHALL push them to Qdrant_Cloud
2. THE Edge_Worker SHALL associate each embedding with its file path and repository metadata
3. THE Edge_Worker SHALL use batch uploads to Qdrant_Cloud for efficiency
4. IF Qdrant_Cloud upload fails, THEN THE Edge_Worker SHALL retry up to 3 times with exponential backoff
5. WHEN all embeddings are uploaded, THE Edge_Worker SHALL update the job status in Redis to "complete"

### Requirement 7: Configuration Management

**User Story:** As a DevOps engineer, I want separate configuration for cloud and edge deployments with a base + extension strategy, so that each environment loads only necessary dependencies and version mismatches are prevented.

#### Acceptance Criteria

1. THE system SHALL support a MODE environment variable with values "CLOUD" or "EDGE"
2. WHEN MODE=CLOUD, THE system SHALL NOT import torch or torch_geometric modules
3. WHEN MODE=EDGE, THE system SHALL verify CUDA availability and log GPU information
4. THE system SHALL maintain requirements-base.txt containing shared dependencies (upstash-redis, gitpython, fastapi, uvicorn, pydantic, python-dotenv)
5. THE requirements-cloud.txt SHALL extend base using "-r requirements-base.txt" and add cloud-specific dependencies (psycopg2-binary, qdrant-client)
6. THE requirements-edge.txt SHALL extend base using "-r requirements-base.txt" and add ML dependencies (torch, torch-geometric, tree-sitter, qdrant-client, numpy, psycopg2-binary)
7. THE system SHALL validate all required environment variables on startup
8. WHEN updating shared dependencies, THE system SHALL update requirements-base.txt only once
9. THE system SHALL document the base + extension strategy to prevent "dependency hell" where cloud and edge have different versions of the same package

### Requirement 8: Error Handling and Resilience

**User Story:** As a system administrator, I want robust error handling and recovery, so that transient failures don't require manual intervention.

#### Acceptance Criteria

1. WHEN the Edge_Worker encounters a network error, THE Edge_Worker SHALL retry the operation up to 3 times
2. WHEN a repository clone fails, THE Edge_Worker SHALL mark the job as failed and continue to the next job
3. WHEN the Task_Queue is empty, THE Edge_Worker SHALL sleep for 2 seconds before polling again
4. IF the Edge_Worker crashes, THEN THE Edge_Worker SHALL be restartable without data loss
5. THE Cloud_API SHALL return appropriate HTTP status codes for all error conditions
6. WHEN Redis connection fails, THE system SHALL log the error and attempt reconnection

### Requirement 9: Monitoring and Observability

**User Story:** As a system administrator, I want to monitor worker status and job progress, so that I can diagnose issues and track performance.

#### Acceptance Criteria

1. THE Edge_Worker SHALL update Redis with status "Idle", "Training Graph on {repo}", or "Error: {message}"
2. THE Cloud_API SHALL expose GET /worker/status endpoint returning current worker state
3. THE Edge_Worker SHALL log job start time, end time, and duration for each repository
4. THE Edge_Worker SHALL log the number of files processed and embeddings generated
5. WHEN training completes, THE Edge_Worker SHALL log final training loss
6. THE system SHALL maintain job history in Redis for the last 100 jobs

### Requirement 10: Performance Requirements

**User Story:** As a developer, I want fast task dispatch and efficient GPU utilization, so that the system can handle multiple repositories per day.

#### Acceptance Criteria

1. THE Cloud_API SHALL dispatch tasks to the queue in under 100ms
2. THE Edge_Worker SHALL process a repository with 100 files in under 5 minutes on GPU
3. THE Neural_Graph_Service SHALL utilize at least 70% of available GPU memory during training
4. THE Edge_Worker SHALL process at least 10 repositories per hour on average
5. THE system SHALL support repositories with up to 10,000 files

### Requirement 11: Security and Authentication

**User Story:** As a security engineer, I want secure communication between components, so that unauthorized users cannot submit malicious tasks.

#### Acceptance Criteria

1. THE Cloud_API SHALL validate Upstash_Redis credentials before accepting tasks
2. THE Edge_Worker SHALL validate Upstash_Redis credentials on startup
3. THE system SHALL use HTTPS for all external API calls to Neon, Qdrant, and Upstash
4. THE Cloud_API SHALL sanitize repository URLs to prevent injection attacks
5. THE Edge_Worker SHALL clone repositories in isolated temporary directories
6. WHEN a job completes, THE Edge_Worker SHALL clean up all temporary files

### Requirement 12: Deployment and Operations

**User Story:** As a DevOps engineer, I want simple deployment procedures for both cloud and edge components, so that I can deploy updates quickly.

#### Acceptance Criteria

1. THE Cloud_API SHALL be deployable to Render via GitHub integration
2. THE Edge_Worker SHALL be runnable with a single command: `python worker.py`
3. THE system SHALL provide separate .env.cloud and .env.edge configuration templates
4. THE Cloud_API SHALL start successfully within 10 seconds
5. THE Edge_Worker SHALL start successfully within 30 seconds (including GPU initialization)
6. THE system SHALL provide health check endpoints for monitoring
