# Requirements Document

## Introduction

Phase 12.5 transforms Neo Alexandria from a monolithic request-response system into a production-grade event-driven architecture with distributed task processing. This phase implements automatic data consistency through event hooks, reliable background processing with Celery, multi-layer caching with Redis, and horizontal scalability through worker distribution. The system will support 100+ concurrent ingestions without performance degradation while reducing computation by 50-70% through intelligent caching.

## Glossary

- **Event System**: A publisher-subscriber pattern that enables decoupled component communication through event emission and listening
- **Event Hook**: An automatic reaction function that executes when a specific event is emitted, ensuring data consistency
- **Celery**: A distributed task queue system that processes background jobs with retry logic and priority queuing
- **Redis**: An in-memory data store used for caching and as a message broker for Celery
- **Task Queue**: A priority-based queue system that manages background job execution across distributed workers
- **Cache Invalidation**: The process of removing or marking stale cached data when source data changes
- **Worker**: A background process that executes tasks from the Celery queue
- **FTS5 Index**: SQLite's Full-Text Search index that enables fast text-based queries
- **Embedding Vector**: A numerical representation of content used for semantic search
- **Quality Score**: A computed metric representing resource quality based on multiple factors
- **Knowledge Graph**: A network of relationships between resources (citations, references)
- **Horizontal Scalability**: The ability to increase system capacity by adding more worker processes

## Requirements

### Requirement 1: Event System Foundation

**User Story:** As a system architect, I want a robust event system, so that components can communicate without tight coupling and react automatically to state changes.

#### Acceptance Criteria

1. THE Event System SHALL implement a singleton EventEmitter class that manages event listeners and dispatches events
2. THE Event System SHALL support both synchronous and asynchronous event handlers
3. THE Event System SHALL maintain an event history of the last 1000 events with timestamps and priority levels
4. THE Event System SHALL provide methods to register listeners, unregister listeners, and emit events with priority levels
5. WHEN an event is emitted, THE Event System SHALL execute all registered handlers and log any handler errors without stopping other handlers

### Requirement 2: System Event Definitions

**User Story:** As a developer, I want a centralized registry of all system events, so that I can understand what events are available and maintain consistent naming conventions.

#### Acceptance Criteria

1. THE System SHALL define all event types using the naming convention "{entity}.{action}" format
2. THE System SHALL provide event definitions for resource lifecycle events including created, updated, deleted, content_changed, and metadata_changed
3. THE System SHALL provide event definitions for processing events including ingestion, embedding generation, quality computation, and classification
4. THE System SHALL provide event definitions for search, graph, cache, and user interaction events
5. THE System SHALL provide event definitions for background task lifecycle events including started, completed, and failed

### Requirement 3: Automatic Data Consistency Hooks

**User Story:** As a system administrator, I want derived data to stay synchronized automatically, so that embeddings, quality scores, and search indexes never become stale.

#### Acceptance Criteria

1. WHEN a resource content changes, THE System SHALL queue an embedding regeneration task with HIGH priority and 5-second debounce delay
2. WHEN a resource metadata changes, THE System SHALL queue a quality recomputation task with MEDIUM priority and 10-second debounce delay
3. WHEN a resource is updated, THE System SHALL queue a search index update task with URGENT priority and 1-second delay
4. WHEN citations are extracted, THE System SHALL queue a graph edge update task with MEDIUM priority and 30-second batch delay
5. WHEN a resource is updated, THE System SHALL invalidate related cache entries immediately with URGENT priority
6. WHEN a user interaction is tracked, THE System SHALL queue a recommendation profile refresh task every 10 interactions with LOW priority
7. WHEN a resource is created, THE System SHALL queue a classification suggestion task with MEDIUM priority and 20-second delay
8. WHEN authors are extracted, THE System SHALL queue an author name normalization task with LOW priority and 60-second delay

### Requirement 4: Celery Task Queue Configuration

**User Story:** As a DevOps engineer, I want a production-grade distributed task queue, so that background jobs are reliable, prioritized, and can scale horizontally.

#### Acceptance Criteria

1. THE System SHALL configure Celery with Redis as both the message broker and result backend
2. THE System SHALL define task routing rules that assign tasks to appropriate queues based on priority and type
3. THE System SHALL configure priority queuing with 10 priority levels where higher numbers indicate higher priority
4. THE System SHALL configure task acknowledgment to occur after completion and reject tasks when workers are lost
5. THE System SHALL configure workers to prefetch 4 tasks and restart after processing 1000 tasks to prevent memory leaks
6. THE System SHALL configure task results to expire after 1 hour
7. THE System SHALL enable task event monitoring for real-time tracking

### Requirement 5: Celery Task Implementations

**User Story:** As a developer, I want all background operations converted to Celery tasks, so that they are reliable, retryable, and can be monitored.

#### Acceptance Criteria

1. THE System SHALL implement an embedding regeneration task with maximum 3 retries, 60-second retry delay, and exponential backoff for transient errors
2. THE System SHALL implement a quality recomputation task with maximum 2 retries
3. THE System SHALL implement a search index update task with URGENT priority (level 9) and maximum 3 retries with 5-second countdown
4. THE System SHALL implement a graph edge update task that adds citation relationships and invalidates graph cache
5. THE System SHALL implement a classification task with maximum 2 retries that predicts taxonomy categories and stores results
6. THE System SHALL implement a cache invalidation task with URGENT priority that supports both exact key and pattern-based invalidation
7. THE System SHALL implement a recommendation profile refresh task that updates user preferences from interaction history
8. THE System SHALL implement a batch processing task that processes multiple resources and reports progress

### Requirement 6: Scheduled Background Tasks

**User Story:** As a system administrator, I want periodic maintenance tasks to run automatically, so that the system stays healthy without manual intervention.

#### Acceptance Criteria

1. THE System SHALL schedule a quality degradation monitoring task to run daily at 2 AM
2. THE System SHALL schedule a quality outlier detection task to run weekly on Sundays at 3 AM
3. THE System SHALL schedule a classification model retraining task to run monthly on the 1st at midnight
4. THE System SHALL schedule a cache cleanup task to run daily at 4 AM to remove expired entries

### Requirement 7: Multi-Layer Redis Caching

**User Story:** As a performance engineer, I want intelligent multi-layer caching, so that repeated queries and computations are 50-70% faster.

#### Acceptance Criteria

1. THE System SHALL implement Redis-based caching for embeddings, quality scores, search query results, and resource data
2. THE System SHALL configure different TTL (time-to-live) values for each cache type based on data volatility
3. THE System SHALL support pattern-based cache invalidation using wildcard keys
4. THE System SHALL track cache statistics including hit rate, miss rate, and invalidation counts
5. THE System SHALL provide cache warming capabilities for frequently accessed data

### Requirement 8: Database Connection Pooling

**User Story:** As a database administrator, I want optimized connection pooling, so that the system handles high concurrency without connection exhaustion.

#### Acceptance Criteria

1. THE System SHALL configure SQLAlchemy connection pool with 20 base connections and 40 overflow connections
2. THE System SHALL configure connection recycling after 1 hour to prevent stale connections
3. THE System SHALL enable connection pre-ping health checks before using connections
4. THE System SHALL log connection pool statistics for monitoring

### Requirement 9: Docker Compose Orchestration

**User Story:** As a DevOps engineer, I want containerized deployment with all dependencies, so that the system can be deployed consistently across environments.

#### Acceptance Criteria

1. THE System SHALL provide a Docker Compose configuration that includes Redis, Celery workers, Celery beat scheduler, and Flower monitoring
2. THE System SHALL configure 4 Celery worker containers with appropriate resource limits
3. THE System SHALL configure Redis with persistence and appropriate memory limits
4. THE System SHALL configure Flower monitoring dashboard accessible on a dedicated port
5. THE System SHALL configure health checks for all containers

### Requirement 10: Event Integration in Services

**User Story:** As a developer, I want all service operations to emit appropriate events, so that hooks can maintain data consistency automatically.

#### Acceptance Criteria

1. WHEN ResourceService updates a resource, THE System SHALL emit resource.updated event with resource_id
2. WHEN ResourceService changes resource content, THE System SHALL emit resource.content_changed event
3. WHEN ResourceService changes resource metadata, THE System SHALL emit resource.metadata_changed event
4. WHEN IngestionService completes processing, THE System SHALL emit ingestion.completed event
5. WHEN users interact with resources, THE System SHALL emit user.interaction_tracked event with user_id and resource_id

### Requirement 11: Monitoring and Observability

**User Story:** As a system administrator, I want comprehensive monitoring dashboards, so that I can track task execution, cache performance, and system health.

#### Acceptance Criteria

1. THE System SHALL provide Flower dashboard for monitoring Celery tasks including active, scheduled, and failed tasks
2. THE System SHALL provide an API endpoint that returns the last 1000 events from event history
3. THE System SHALL provide cache statistics endpoint showing hit rate, miss rate, and total operations
4. THE System SHALL log all task executions with timestamps, duration, and success/failure status
5. THE System SHALL provide worker health status endpoint showing active workers and their task counts

### Requirement 12: Migration from BackgroundTasks

**User Story:** As a developer, I want all FastAPI BackgroundTasks replaced with Celery tasks, so that background operations are reliable and persistent.

#### Acceptance Criteria

1. THE System SHALL replace all background_tasks.add_task() calls with equivalent Celery task.apply_async() calls
2. THE System SHALL maintain backward compatibility during migration by supporting both mechanisms temporarily
3. THE System SHALL provide migration documentation listing all replaced background tasks
4. THE System SHALL verify that all replaced tasks maintain the same functionality and parameters

### Requirement 13: Performance and Scalability

**User Story:** As a performance engineer, I want the system to handle 100+ concurrent ingestions, so that bulk imports complete quickly without degradation.

#### Acceptance Criteria

1. WHEN processing 100 concurrent ingestions, THE System SHALL complete all tasks without performance degradation beyond 10%
2. THE System SHALL achieve 50-70% computation reduction through caching for repeated operations
3. THE System SHALL achieve greater than 60% cache hit rate for repeated queries
4. THE System SHALL update search indexes within 5 seconds of resource updates
5. THE System SHALL maintain task failure rate below 1% through automatic retries

### Requirement 14: Reliability and Error Handling

**User Story:** As a system administrator, I want robust error handling and recovery, so that transient failures don't cause data loss or inconsistency.

#### Acceptance Criteria

1. WHEN a task fails due to a transient error, THE System SHALL retry the task with exponential backoff up to the maximum retry limit
2. WHEN a task fails permanently, THE System SHALL log the error with full context and mark the task as failed
3. WHEN a worker crashes, THE System SHALL reject in-progress tasks and requeue them for other workers
4. WHEN Redis becomes unavailable, THE System SHALL queue tasks in memory and flush when Redis recovers
5. THE System SHALL provide dead letter queue for tasks that exceed maximum retries

### Requirement 15: Horizontal Scalability

**User Story:** As a DevOps engineer, I want to scale the system by adding workers, so that throughput increases linearly with worker count.

#### Acceptance Criteria

1. WHEN additional Celery workers are added, THE System SHALL distribute tasks across all available workers
2. THE System SHALL support running workers on different machines for distributed processing
3. THE System SHALL maintain task ordering guarantees for tasks with dependencies
4. THE System SHALL provide worker auto-scaling based on queue depth
5. THE System SHALL support graceful worker shutdown that completes in-progress tasks before terminating
