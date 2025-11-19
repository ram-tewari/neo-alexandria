# Implementation Plan

- [x] 1. Set up infrastructure and dependencies





  - Install Redis and Celery dependencies in requirements.txt
  - Configure environment variables for Redis and Celery URLs
  - Create Docker Compose configuration with Redis, workers, beat, and Flower
  - _Requirements: 4.1, 4.2, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 2. Implement event system foundation






- [x] 2.1 Create event system core

  - Implement EventPriority enum with CRITICAL, HIGH, NORMAL, LOW levels
  - Implement Event dataclass with name, data, timestamp, priority, correlation_id
  - Implement EventEmitter singleton class with on(), off(), emit() methods
  - Add support for both synchronous and asynchronous event handlers
  - Implement event history storage (last 1000 events)
  - Add error isolation so handler failures don't affect other handlers
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_


- [x] 2.2 Define system event types

  - Create SystemEvent enum with all event type definitions
  - Implement resource lifecycle events (created, updated, deleted, content_changed, metadata_changed)
  - Implement processing events (ingestion, embedding, quality, classification)
  - Implement search, graph, cache, user, and system events
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_


- [x] 2.3 Write unit tests for event system

  - Test event emission and handler execution
  - Test handler error isolation
  - Test event history tracking
  - Test async handler support
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3. Implement Celery task queue





- [x] 3.1 Create Celery application configuration


  - Initialize Celery app with Redis broker and backend
  - Configure task serialization (JSON) and timezone (UTC)
  - Define task routing rules for different queue types (urgent, high_priority, ml_tasks, batch)
  - Configure priority queuing with 10 levels
  - Configure task acknowledgment (acks_late, reject_on_worker_lost)
  - Configure worker optimization (prefetch_multiplier=4, max_tasks_per_child=1000)
  - Configure result expiration (3600 seconds)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 3.2 Implement scheduled tasks with Celery Beat


  - Configure beat_schedule for quality degradation monitoring (daily 2 AM)
  - Configure beat_schedule for quality outlier detection (weekly Sunday 3 AM)
  - Configure beat_schedule for classification model retraining (monthly 1st at midnight)
  - Configure beat_schedule for cache cleanup (daily 4 AM)
  - _Requirements: 6.1, 6.2, 6.3, 6.4_


- [x] 3.3 Create DatabaseTask base class

  - Implement base Task class with automatic DB session management
  - Implement __call__ method that provides db session to tasks
  - Ensure proper session cleanup in finally block
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [x] 4. Implement core Celery tasks




- [x] 4.1 Implement embedding regeneration task

  - Create regenerate_embedding_task with DatabaseTask base
  - Configure max_retries=3, default_retry_delay=60
  - Implement exponential backoff for transient errors (timeout, connection)
  - Call EmbeddingService.generate_and_store_embedding()
  - Add comprehensive logging
  - _Requirements: 5.1_

- [x] 4.2 Implement quality recomputation task

  - Create recompute_quality_task with DatabaseTask base
  - Configure max_retries=2
  - Call QualityService.compute_quality()
  - Add logging for quality score results
  - _Requirements: 5.2_


- [x] 4.3 Implement search index update task

  - Create update_search_index_task with URGENT priority (9)
  - Configure max_retries=3, countdown=5
  - Call SearchService.update_fts5_index()
  - Add logging for index update completion
  - _Requirements: 5.3_


- [x] 4.4 Implement graph edge update task

  - Create update_graph_edges_task with DatabaseTask base
  - Accept resource_id and citations list parameters
  - Call GraphService.add_citation_edges()
  - Invalidate graph cache after update
  - _Requirements: 5.4_



- [x] 4.5 Implement classification task

  - Create classify_resource_task with max_retries=2
  - Call MLClassificationService.predict() with top_k=5
  - Store predictions using TaxonomyService.classify_resource()
  - Mark predictions with is_predicted=True
  - _Requirements: 5.5_

- [x] 4.6 Implement cache invalidation task

  - Create invalidate_cache_task with URGENT priority (9)
  - Support both exact key and pattern-based invalidation (wildcard *)
  - Call cache.delete() or cache.delete_pattern()
  - Add logging for invalidation counts
  - _Requirements: 5.6_


- [x] 4.7 Implement recommendation profile refresh task

  - Create refresh_recommendation_profile_task with DatabaseTask base
  - Call UserProfileService._update_learned_preferences()
  - Add logging for profile refresh completion
  - _Requirements: 5.7_

- [x] 4.8 Implement batch processing task

  - Create batch_process_resources_task with progress tracking
  - Support operations: regenerate_embeddings, recompute_quality
  - Use self.update_state() to report progress (current/total)
  - Queue individual tasks for each resource
  - Return completion status with processed count
  - _Requirements: 5.8_

- [x] 4.9 Write unit tests for Celery tasks


  - Test task retry logic with transient errors
  - Test task failure with permanent errors
  - Test batch processing progress tracking
  - Test DatabaseTask session management
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_


- [x] 5. Implement event hooks for data consistency

- [x] 5.1 Create embedding regeneration hook


  - Implement on_content_changed_regenerate_embedding handler
  - Extract resource_id from event data
  - Queue regenerate_embedding_task with priority=7, countdown=5
  - Add logging for task queuing
  - _Requirements: 3.1_



- [x] 5.2 Create quality recomputation hook

  - Implement on_metadata_changed_recompute_quality handler
  - Extract resource_id from event data
  - Queue recompute_quality_task with priority=5, countdown=10
  - Add logging for task queuing
  - _Requirements: 3.2_




- [x] 5.3 Create search index sync hook
  - Implement on_resource_updated_sync_search_index handler
  - Extract resource_id from event data
  - Queue update_search_index_task with priority=9, countdown=1
  - Add logging for urgent task queuing


  - _Requirements: 3.3_


- [x] 5.4 Create graph edge update hook
  - Implement on_citation_extracted_update_graph handler
  - Extract resource_id and citations from event data
  - Queue update_graph_edges_task with priority=5, countdown=30


  - Add logging with citation count

  - _Requirements: 3.4_

- [x] 5.5 Create cache invalidation hook
  - Implement on_resource_updated_invalidate_caches handler
  - Build cache key list: embedding, quality, resource, search_query patterns
  - Queue invalidate_cache_task with priority=9, countdown=0 (immediate)

  - Add logging for cache key count


  - _Requirements: 3.5_

- [x] 5.6 Create recommendation profile refresh hook
  - Implement on_user_interaction_refresh_profile handler
  - Extract user_id and total_interactions from event data

  - Only refresh every 10 interactions (check modulo)


  - Queue refresh_recommendation_profile_task with priority=3, countdown=300
  - _Requirements: 3.6_

- [x] 5.7 Create classification suggestion hook
  - Implement on_resource_created_suggest_classification handler

  - Extract resource_id from event data

  - Queue classify_resource_task with priority=5, countdown=20
  - Add logging for classification queuing
  - _Requirements: 3.7_

- [x] 5.8 Create author normalization hook

  - Implement on_author_extracted_normalize_names handler

  - Extract resource_id and authors from event data

  - Queue normalize_author_names_task with priority=3, countdown=60
  - Add logging for normalization queuing
  - _Requirements: 3.8_


- [x] 5.9 Implement hook registration function

  - Create register_all_hooks() function
  - Register all 8 hooks with event_emitter.on()
  - Add logging for hook registration count
  - Call from FastAPI startup event
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 5.10 Write integration tests for hooks

  - Test content change triggers embedding regeneration
  - Test metadata change triggers quality recomputation
  - Test resource update triggers search index sync
  - Test cache invalidation on resource update
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 6. Implement Redis caching layer


- [x] 6.1 Create Redis cache class


  - Implement RedisCache class with Redis connection
  - Implement get() method with hit/miss tracking
  - Implement set() method with TTL support
  - Implement delete() method for single keys
  - Implement delete_pattern() method for wildcard invalidation
  - Implement get_default_ttl() method with key-based TTL selection
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 6.2 Implement cache statistics tracking

  - Create CacheStats class with hits, misses, invalidations counters
  - Implement record_hit(), record_miss(), record_invalidation() methods
  - Implement hit_rate() calculation method
  - Integrate stats tracking into RedisCache methods
  - _Requirements: 7.4_


- [ ] 6.3 Configure cache TTL strategy
  - Set embedding cache TTL to 3600 seconds (1 hour)
  - Set quality cache TTL to 1800 seconds (30 minutes)
  - Set search_query cache TTL to 300 seconds (5 minutes)
  - Set resource cache TTL to 600 seconds (10 minutes)
  - Set default TTL to 300 seconds
  - _Requirements: 7.2_


- [x] 6.4 Add caching to embedding service

  - Wrap EmbeddingService.get_embedding() with cache.get()
  - Cache embeddings with key pattern "embedding:{resource_id}"
  - Store embeddings in cache after generation
  - _Requirements: 7.1, 7.5_


- [x] 6.5 Add caching to quality service

  - Wrap QualityService.get_quality_scores() with cache.get()
  - Cache quality scores with key pattern "quality:{resource_id}"
  - Store quality scores in cache after computation
  - _Requirements: 7.1, 7.5_

- [x] 6.6 Add caching to search service


  - Wrap SearchService.search() with cache.get()
  - Generate cache key from query hash
  - Cache search results with key pattern "search_query:{hash}"
  - _Requirements: 7.1, 7.5_

- [ ] 6.7 Write unit tests for caching
  - Test cache get/set operations
  - Test pattern-based invalidation
  - Test TTL expiration
  - Test cache statistics tracking
  - _Requirements: 7.1, 7.2, 7.3, 7.4_
-

- [x] 7. Optimize database connection pooling



- [x] 7.1 Configure SQLAlchemy connection pool


  - Set pool_size=20 for base connections
  - Set max_overflow=40 for additional connections
  - Set pool_recycle=3600 for 1-hour connection recycling
  - Enable pool_pre_ping for health checks
  - Enable echo_pool for logging
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 7.2 Implement pool monitoring endpoint


  - Create get_pool_status() function
  - Return pool size, checked_in, checked_out, overflow, total
  - Add API endpoint GET /db/pool for monitoring
  - _Requirements: 8.4_

- [x] 8. Integrate events into services






- [x] 8.1 Add events to ResourceService

  - Emit resource.created event in create() method
  - Emit resource.updated event in update() method
  - Emit resource.content_changed event when content field changes
  - Emit resource.metadata_changed event when metadata fields change
  - Emit resource.deleted event in delete() method
  - _Requirements: 10.1, 10.2, 10.3_


- [x] 8.2 Add events to IngestionService

  - Emit ingestion.started event at beginning of process()
  - Emit ingestion.completed event on successful completion
  - Emit ingestion.failed event on error
  - Include duration and success status in event data
  - _Requirements: 10.4_


- [x] 8.3 Add events to user interaction tracking

  - Emit user.interaction_tracked event when users view/download resources
  - Include user_id, resource_id, interaction_type, total_interactions
  - _Requirements: 10.5_


- [x] 8.4 Add events to citation extraction

  - Emit citations.extracted event after citation parsing
  - Include resource_id and citations list in event data
  - _Requirements: 3.4_


- [x] 8.5 Add events to author extraction

  - Emit authors.extracted event after author parsing
  - Include resource_id and authors list in event data
  - _Requirements: 3.8_


- [x] 8.6 Write integration tests for service events

  - Test ResourceService emits correct events
  - Test IngestionService emits lifecycle events
  - Test user interaction tracking emits events



  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 9. Create monitoring and observability endpoints


- [x] 9.1 Implement event history endpoint

  - Create GET /events/history endpoint
  - Accept limit parameter (default 100)
  - Return event_emitter.get_event_history(limit)
  - _Requirements: 11.2_


- [x] 9.2 Implement cache statistics endpoint


  - Create GET /cache/stats endpoint
  - Return hit_rate, hits, misses, invalidations
  - Calculate percentages and totals
  - _Requirements: 11.3_




- [ ] 9.3 Implement worker status endpoint
  - Create GET /workers/status endpoint
  - Use celery_app.control.inspect() to get worker info
  - Return active tasks, scheduled tasks, worker stats



  - _Requirements: 11.4_

- [ ] 9.4 Implement database pool status endpoint
  - Create GET /db/pool endpoint
  - Call get_pool_status() function
  - Return connection pool metrics
  - _Requirements: 11.4_




- [x] 10. Update Docker Compose configuration

- [x] 10.1 Add Redis service
  - Configure Redis 7 Alpine image
  - Set maxmemory to 2GB with allkeys-lru eviction
  - Enable appendonly persistence
  - Add health check with redis-cli ping


  - Expose port 6379
  - _Requirements: 9.1, 9.3_

- [x] 10.2 Add Celery worker services
  - Configure 4 worker replicas

  - Set concurrency=4 per worker
  - Configure resource limits (2 CPU, 2GB RAM)

  - Set environment variables for database and Redis
  - Add dependency on postgres and redis
  - _Requirements: 9.2_


- [x] 10.3 Add Celery Beat service

  - Configure beat scheduler
  - Set environment variables for Redis
  - Add dependency on redis
  - _Requirements: 9.2_

- [x] 10.4 Add Flower monitoring service

  - Configure Flower on port 5555
  - Set environment variables for Celery broker and backend
  - Expose port 5555 for web access
  - Add dependency on redis
  - _Requirements: 9.4, 11.1_

- [x] 10.5 Update API service configuration
  - Add CELERY_BROKER_URL and CELERY_RESULT_BACKEND environment variables
  - Add dependency on r




edis
  - _Requirements: 9.1_


- [x] 11. Migrate from BackgroundTasks to Celery





- [x] 11.1 Identify all BackgroundTasks usage

  - Search codebase for background_tasks.add_task()
  - Document all current background task calls
  - Map each to equivalent Celery task
  - _Requirements: 12.1, 12.3_



- [x] 11.2 Replace embedding generation background tasks
  - Replace background_tasks.add_task(generate_embedding) with regenerate_embedding_task.apply_async()
  - Maintain same parameters and functionality


  - _Requirements: 12.1, 12.4_

- [x] 11.3 Replace quality computation background tasks


  - Replace background_tasks.add_task(compute_quality) with recompute_quality_task.apply_async()
  - Maintain same parameters and functionality
  - _Requirements: 12.1, 12.4_



- [x] 11.4 Replace search indexing background tasks
  - Replace background_tasks.add_task(update_index) with update_search_index_task.apply_async()

  - Maintain same parameters and functionality
  - _Requirements: 12.1, 12.4_

- [x] 11.5 Replace classification background tasks
  - Replace background_tasks.add_task(classify) with classify_resource_task.apply_async()
  - Maintain same parameters and functionality
  - _Requirements: 12.1, 12.4_

- [x] 11.6 Remove BackgroundTasks dependencies


  - Remove BackgroundTasks imports from routers
  - Remove background_tasks parameters from endpoint functions

  - Update API documentation
  - _Requirements: 12.1, 12.3_



- [x] 12. Update requirements.txt and configuration


- [x] 12.1 Add Celery dependencies


  - Add celery[redis]>=5.3.0
  - Add flower>=2.0.0 for monitoring

  - Add redis>=5.0.0 for caching
  - _Requirements: 4.1, 9.1_






- [ ] 12.2 Add environment variables
  - Add REDIS_HOST, REDIS_PORT, REDIS_CACHE_DB to config
  - Add CELERY_BROKER_URL to config

  - Add CELERY_RESULT_BACKEND to config
  - Update .env.example with new variables
  - _Requirements: 4.1, 7.1_

- [x] 12.3 Update FastAPI startup

  - Call register_all_hooks() in startup event

  - Initialize Redis cache connection
  - Log event system initialization
  - _Requirements: 3.8, 7.1_


- [x] 13. Performance testing and validation


- [x] 13.1 Run concurrent ingestion test

  - Test 100 concurrent ingestions
  - Verify all complete without degradation
  - Measure completion time and success rate
  - _Requirements: 13.1_


- [x] 13.2 Measure cache performance

  - Run system for 1 week with production-like load
  - Measure cache hit rate (target >60%)
  - Measure computation reduction (target 50-70%)
  - _Requirements: 13.2, 13.3_



- [x] 13.3 Validate search index update speed
  - Update resource and measure time until searchable
  - Verify update completes within 5 seconds
  - _Requirements: 13.4_

- [x] 13.4 Measure task reliability
  - Track task success/failure rates over 1 week
  - Verify failure rate <1%
  - Verify automatic retries work correctly
  - _Requirements: 13.5, 14.1, 14.2_

- [x] 13.5 Test horizontal scalability

  - Start with 2 workers, measure throughput
  - Scale to 4 workers, verify throughput doubles
  - Scale to 8 workers, verify linear scaling
  - _Requirements: 15.1, 15.2_

- [x] 14. Documentation and deployment






- [x] 14.1 Create deployment documentation

  - Document Docker Compose setup
  - Document environment variable configuration
  - Document worker scaling procedures
  - _Requirements: 9.1, 9.2, 15.1_


- [x] 14.2 Create monitoring guide

  - Document Flower dashboard usage
  - Document API monitoring endpoints
  - Document cache statistics interpretation
  - _Requirements: 11.1, 11.2, 11.3_



- [x] 14.3 Create migration guide

  - Document migration steps from Phase 12
  - Document rollback procedures
  - Document testing checklist
  - _Requirements: 12.1, 12.2, 12.3_
