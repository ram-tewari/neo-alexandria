# Implementation Plan

- [ ] 1. Setup Shared Kernel Infrastructure
  - Create `app/shared/` directory structure
  - Extract and consolidate common components
  - Update all existing imports to use shared kernel
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 1.1 Create shared database module
  - Create `app/shared/database.py` with engine, SessionLocal, and Base
  - Extract database initialization logic from `app/database/base.py`
  - Implement `init_database()` and `get_db()` functions
  - Add connection pool configuration
  - _Requirements: 1.2, 1.3_

- [ ] 1.2 Create shared event bus module
  - Create `app/shared/event_bus.py` with EventBus class
  - Implement `subscribe()` method for handler registration
  - Implement `emit()` method with error isolation
  - Add event metrics tracking (events_emitted, events_delivered, handler_errors)
  - Implement `get_metrics()` method for monitoring
  - _Requirements: 1.2, 1.3, 4.1, 4.4, 12.1, 12.2, 12.3, 12.4_

- [ ] 1.3 Create shared base model module
  - Create `app/shared/base_model.py` with Base declarative base
  - Implement TimestampMixin with created_at and updated_at
  - Implement UUIDMixin with UUID primary key
  - _Requirements: 1.2, 1.3_

- [ ] 1.4 Update existing imports to use shared kernel
  - Update all imports of `database.base` to use `shared.database`
  - Update all imports of `event_system` to use `shared.event_bus`
  - Run full test suite to verify no regressions
  - _Requirements: 1.3, 8.4_

- [ ] 2. Extract Collections Module (First Vertical Slice)
  - Create Collections module directory structure
  - Move Collections-related code to new module
  - Implement event handlers for cross-module communication
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 2.1 Create Collections module structure
  - Create `app/modules/collections/` directory
  - Create `__init__.py`, `router.py`, `service.py`, `schema.py`, `model.py`, `handlers.py`
  - Create `app/modules/collections/tests/` directory
  - Create `app/modules/collections/README.md` with module documentation
  - _Requirements: 2.1, 2.5_

- [ ] 2.2 Move Collections router
  - Copy `routers/collections.py` to `modules/collections/router.py`
  - Update imports to use shared kernel
  - Update imports to use module-local service and schema
  - Add deprecation warning to old import path
  - _Requirements: 2.1, 13.2, 13.3_

- [ ] 2.3 Move Collections service
  - Copy `services/collection_service.py` to `modules/collections/service.py`
  - Update imports to use shared kernel
  - Remove any direct imports of other services
  - Add method `find_collections_with_resource(resource_id)` for event handler
  - _Requirements: 2.2, 3.2, 4.3_

- [ ] 2.4 Move Collections schemas
  - Copy `schemas/collection.py` to `modules/collections/schema.py`
  - Update imports to use shared kernel
  - _Requirements: 2.3_

- [ ] 2.5 Extract Collections models
  - Extract Collection and CollectionResource models from `database/models.py`
  - Create `modules/collections/model.py` with extracted models
  - Update models to import from shared.base_model
  - Use string-based relationship references to avoid import cycles
  - _Requirements: 2.4_

- [ ] 2.6 Create Collections public interface
  - Implement `modules/collections/__init__.py`
  - Export collections_router, CollectionService, and schema classes
  - Add module metadata (__version__, __domain__)
  - Hide internal implementation details
  - _Requirements: 2.5, 2.6, 7.1, 7.2, 7.3_

- [ ] 2.7 Create Collections event handlers
  - Create `modules/collections/handlers.py`
  - Implement `handle_resource_deleted(payload)` handler
  - Implement `register_handlers()` function
  - Subscribe to "resource.deleted" event
  - Add proper error handling and logging
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ]* 2.8 Write Collections module tests
  - Create `modules/collections/tests/test_service.py` with service tests
  - Create `modules/collections/tests/test_router.py` with router tests
  - Create `modules/collections/tests/test_handlers.py` with event handler tests
  - Use in-memory database fixtures
  - Mock event bus for isolation
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 3. Decouple Resources from Collections
  - Remove direct service calls between Resources and Collections
  - Replace with event-driven communication
  - Verify circular dependency is eliminated
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3.1 Identify and document circular dependencies
  - Search for all imports of CollectionService in ResourceService
  - Document all direct method calls to CollectionService
  - Create list of events needed to replace direct calls
  - _Requirements: 3.1, 3.2, 11.4_

- [ ] 3.2 Replace direct calls with event emissions in ResourceService
  - Update `delete_resource()` to emit "resource.deleted" event
  - Remove import of CollectionService
  - Remove direct call to `recompute_embedding`
  - Add event emission with resource_id payload
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3.3 Verify event-driven flow
  - Test that resource deletion emits event
  - Test that Collections handler receives event
  - Test that collection embeddings are recomputed
  - Verify no direct imports remain
  - _Requirements: 3.2, 3.3, 4.2, 4.3_

- [ ]* 3.4 Write integration tests for event-driven communication
  - Create `tests/integration/test_resource_collection_events.py`
  - Test resource deletion triggers collection update
  - Test event payload validation
  - Test error handling in event handlers
  - _Requirements: 4.4, 8.4, 9.5_

- [ ] 4. Extract Resources Module
  - Create Resources module directory structure
  - Move Resources-related code to new module
  - Update all imports to use new module paths
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 4.1 Create Resources module structure
  - Create `app/modules/resources/` directory
  - Create `__init__.py`, `router.py`, `service.py`, `schema.py`, `model.py`, `handlers.py`
  - Create `app/modules/resources/tests/` directory
  - Create `app/modules/resources/README.md` with module documentation
  - _Requirements: 5.1, 5.5_

- [ ] 4.2 Move Resources router
  - Move `routers/resources.py` to `modules/resources/router.py`
  - Update imports to use shared kernel
  - Update imports to use module-local service and schema
  - _Requirements: 5.1, 13.4_

- [ ] 4.3 Move Resources service
  - Move `services/resource_service.py` to `modules/resources/service.py`
  - Update imports to use shared kernel
  - Verify event emissions are in place (from step 3.2)
  - _Requirements: 5.2, 3.1_

- [ ] 4.4 Move Resources schemas
  - Move `schemas/resource.py` to `modules/resources/schema.py`
  - Update imports to use shared kernel
  - _Requirements: 5.3_

- [ ] 4.5 Extract Resources models
  - Extract Resource model from `database/models.py`
  - Create `modules/resources/model.py` with extracted model
  - Update model to import from shared.base_model
  - Use string-based relationship references for collections
  - _Requirements: 5.4_

- [ ] 4.6 Create Resources public interface
  - Implement `modules/resources/__init__.py`
  - Export resources_router, ResourceService, and schema classes
  - Add module metadata (__version__, __domain__)
  - _Requirements: 5.5, 7.1, 7.2, 7.3_

- [ ] 4.7 Create Resources event handlers
  - Create `modules/resources/handlers.py`
  - Implement `handle_collection_updated(payload)` handler (placeholder)
  - Implement `register_handlers()` function
  - _Requirements: 4.1, 4.5_

- [ ]* 4.8 Write Resources module tests
  - Create `modules/resources/tests/test_service.py` with service tests
  - Create `modules/resources/tests/test_router.py` with router tests
  - Create `modules/resources/tests/test_handlers.py` with event handler tests
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 5. Extract Search Module
  - Create Search module directory structure
  - Consolidate multiple search services into unified module
  - Update all imports to use new module paths
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 5.1 Create Search module structure
  - Create `app/modules/search/` directory
  - Create `__init__.py`, `router.py`, `service.py`, `schema.py`, `model.py`, `handlers.py`
  - Create `app/modules/search/tests/` directory
  - Create `app/modules/search/README.md` with module documentation
  - _Requirements: 6.1, 6.5_

- [ ] 5.2 Consolidate search services
  - Merge `search_service.py`, `hybrid_search_methods.py`, `reciprocal_rank_fusion_service.py` into `modules/search/service.py`
  - Merge `reranking_service.py` and `sparse_embedding_service.py` into unified SearchService
  - Create internal strategy classes (FTSSearchStrategy, VectorSearchStrategy, HybridSearchStrategy)
  - Update imports to use shared kernel
  - _Requirements: 6.2, 6.4_

- [ ] 5.3 Move Search router
  - Move `routers/search.py` to `modules/search/router.py`
  - Update imports to use shared kernel
  - Update imports to use module-local service and schema
  - _Requirements: 6.1, 13.4_

- [ ] 5.4 Move Search schemas
  - Move `schemas/search.py` to `modules/search/schema.py`
  - Update imports to use shared kernel
  - _Requirements: 6.3_

- [ ] 5.5 Create Search public interface
  - Implement `modules/search/__init__.py`
  - Export search_router, SearchService, and schema classes
  - Add module metadata (__version__, __domain__)
  - _Requirements: 6.5, 7.1, 7.2, 7.3_

- [ ]* 5.6 Write Search module tests
  - Create `modules/search/tests/test_service.py` with service tests
  - Create `modules/search/tests/test_router.py` with router tests
  - Test FTS, vector, and hybrid search strategies
  - _Requirements: 9.1, 9.2_

- [ ] 6. Update Application Entry Point
  - Modify main.py to register all modules
  - Register event handlers on startup
  - Maintain backward compatibility
  - _Requirements: 1.5, 4.5, 7.4, 8.1, 8.2, 13.4_

- [ ] 6.1 Create module registration system
  - Implement `register_all_modules()` function in main.py
  - Load modules dynamically with error handling
  - Register routers for each module
  - Register event handlers for each module
  - _Requirements: 1.5, 4.5_

- [ ] 6.2 Update FastAPI application initialization
  - Call `init_database()` on startup
  - Call `register_all_modules()` on startup
  - Ensure event handlers are registered before processing requests
  - Add startup logging for module registration
  - _Requirements: 4.5, 8.1_

- [ ] 6.3 Maintain API backward compatibility
  - Verify all existing API endpoints remain at same paths
  - Test that API responses match previous schemas
  - Run full integration test suite
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 7. Implement Module Isolation Validation
  - Create automated checker for module dependencies
  - Detect circular dependencies
  - Enforce dependency rules
  - _Requirements: 11.1, 11.2, 11.5, 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 7.1 Create module isolation checker script
  - Create `scripts/check_module_isolation.py`
  - Parse Python imports using AST
  - Detect direct imports between modules (excluding shared kernel)
  - Detect circular dependencies
  - Generate dependency graph
  - _Requirements: 14.1, 14.2, 14.3, 14.5_

- [ ] 7.2 Integrate isolation checker into CI/CD
  - Add isolation checker to pre-commit hooks
  - Add isolation checker to GitHub Actions workflow
  - Fail build if violations are found
  - _Requirements: 14.4_

- [ ]* 7.3 Write tests for isolation checker
  - Test detection of direct module imports
  - Test detection of circular dependencies
  - Test allowance of shared kernel imports
  - _Requirements: 14.1, 14.2, 14.3_

- [ ] 8. Add Monitoring and Observability
  - Expose event bus metrics
  - Add module health checks
  - Implement structured logging
  - _Requirements: 12.4, 12.5, 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ] 8.1 Create event bus monitoring endpoint
  - Add `/monitoring/events` endpoint to monitoring router
  - Expose events_emitted, events_delivered, handler_errors
  - Expose event_types breakdown
  - Calculate and expose handler latency percentiles (p50, p95, p99)
  - _Requirements: 15.1, 15.2, 15.3, 15.5_

- [ ] 8.2 Add module health check endpoints
  - Add `/health` endpoint to each module router
  - Check database connection
  - Check event handlers registered
  - Return module version and status
  - _Requirements: 12.5_

- [ ] 8.3 Implement structured logging for events
  - Add structured logging to event emission
  - Add structured logging to event handler execution
  - Include module, operation, duration in log context
  - Log warnings for slow events (>100ms)
  - _Requirements: 12.4, 15.4_

- [ ] 8.4 Add performance tracking
  - Track event emission time
  - Track event handler execution time
  - Calculate latency percentiles
  - Expose metrics through monitoring endpoint
  - _Requirements: 15.1, 15.2, 15.3_

- [ ] 9. Cleanup and Documentation
  - Remove old layered structure files
  - Update architecture documentation
  - Create migration guide
  - Add module-specific documentation
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 13.4, 13.5_

- [ ] 9.1 Remove deprecated files
  - Delete `routers/` directory (after verifying all moved)
  - Delete `services/` directory (after verifying all moved)
  - Delete `schemas/` directory (after verifying all moved)
  - Update `database/models.py` to only contain shared models
  - Remove deprecation warnings
  - _Requirements: 13.4, 13.5_

- [ ] 9.2 Update ARCHITECTURE_DIAGRAM.md
  - Add "Phase 13.5: Vertical Slicing" section
  - Create ASCII diagram showing modular structure
  - Create ASCII diagram showing event-driven communication
  - Document module dependencies
  - _Requirements: 10.1, 10.2_

- [ ] 9.3 Create MIGRATION_GUIDE.md
  - Document the transition from layered to modular architecture
  - Explain how to add new modules
  - Document event-driven communication patterns
  - Provide examples of module creation
  - _Requirements: 10.3, 10.4, 10.5_

- [ ] 9.4 Create module README files
  - Create README.md for Collections module
  - Create README.md for Resources module
  - Create README.md for Search module
  - Document module purpose, public interface, and events
  - _Requirements: 11.4_

- [ ] 9.5 Update DEVELOPER_GUIDE.md
  - Add section on modular architecture
  - Document module structure and conventions
  - Document event-driven communication
  - Update code examples to use new module paths
  - _Requirements: 10.1, 10.4_

- [ ] 10. Final Validation and Performance Testing
  - Run full test suite
  - Perform load testing
  - Verify performance benchmarks
  - Validate backward compatibility
  - _Requirements: 8.4, 8.5, 15.4_

- [ ] 10.1 Run comprehensive test suite
  - Run all unit tests
  - Run all integration tests
  - Run all module-specific tests
  - Verify 100% test pass rate
  - _Requirements: 8.4, 9.5_

- [ ] 10.2 Perform load testing
  - Test event bus under high load (1000+ events/second)
  - Test concurrent module operations
  - Verify connection pool sizing
  - _Requirements: 8.5_

- [ ] 10.3 Validate performance benchmarks
  - Verify event emission + delivery < 1ms (p95)
  - Verify application startup < 5 seconds
  - Verify memory usage increase < 10%
  - Compare performance to baseline (layered architecture)
  - _Requirements: 8.5, 15.4_

- [ ] 10.4 Validate backward compatibility
  - Test all existing API endpoints
  - Verify response schemas unchanged
  - Test with existing client applications
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ]* 10.5 Create performance regression tests
  - Add automated performance tests to CI/CD
  - Set performance thresholds
  - Alert on performance regressions
  - _Requirements: 8.5, 15.4_
