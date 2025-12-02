# Requirements Document

## Introduction

Neo Alexandria 2.0 currently implements a traditional layered architecture with horizontal separation (routers/, services/, models/, schemas/). This creates tight coupling between domains, making features difficult to isolate, test, and maintain. The most critical issue is the tight coupling between ResourceService and CollectionService, where resource operations directly import and call collection operations, creating circular dependencies and preventing modular extraction.

Phase 13.5 transforms the architecture from a **Layered Architecture** to a **Modular Monolith (Vertical Slices)** using the "Strangler Fig" pattern. This refactoring will decouple the Resources, Search, and Collections domains, enabling independent development, testing, and potential future extraction into microservices.

## Glossary

- **System**: Neo Alexandria 2.0 backend application
- **Modular Monolith**: An architectural pattern where code is organized by business domain (vertical slices) rather than technical layers (horizontal slices)
- **Vertical Slice**: A self-contained module containing all layers (router, service, schema, model) for a specific business domain
- **Strangler Fig Pattern**: An incremental refactoring approach where new architecture gradually replaces old architecture
- **Event Bus**: A publish-subscribe messaging system that enables loose coupling between modules
- **Shared Kernel**: Common components used across all modules (database, events, base models)
- **Domain Module**: A vertical slice representing a bounded context (e.g., Resources, Collections, Search)
- **Circular Dependency**: When Module A depends on Module B, and Module B depends on Module A, creating a cycle
- **Direct Service Call**: When one service directly imports and invokes methods on another service
- **Event-Driven Communication**: Modules communicate by emitting and subscribing to events rather than direct calls

## Requirements

### Requirement 1: Architectural Foundation

**User Story:** As a developer, I want a clear modular architecture, so that I can understand and modify domain logic without affecting unrelated features.

#### Acceptance Criteria

1. WHEN the System is deployed, THE System SHALL organize code into vertical slices under `app/modules/` directory
2. WHEN a developer examines the codebase, THE System SHALL provide a `shared/` directory containing only database, event_bus, and base_model components
3. WHEN the shared kernel is modified, THE System SHALL ensure shared components depend on no other application modules
4. WHERE a module is created, THE System SHALL include router, service, schema, and model components within the module directory
5. WHEN the System initializes, THE System SHALL load all modules through a consistent module interface pattern

### Requirement 2: Collections Module Extraction

**User Story:** As a developer, I want the Collections domain isolated into its own module, so that collection logic can be developed and tested independently.

#### Acceptance Criteria

1. WHEN the Collections module is created, THE System SHALL move `routers/collections.py` to `modules/collections/router.py`
2. WHEN the Collections module is created, THE System SHALL move `services/collection_service.py` to `modules/collections/service.py`
3. WHEN the Collections module is created, THE System SHALL move `schemas/collection.py` to `modules/collections/schema.py`
4. WHEN the Collections module is created, THE System SHALL move Collection-related models from `database/models.py` to `modules/collections/model.py`
5. WHEN the Collections module is accessed, THE System SHALL expose a clean public interface through `modules/collections/__init__.py`
6. WHEN the Collections module is imported, THE System SHALL prevent direct access to internal implementation details

### Requirement 3: Circular Dependency Elimination

**User Story:** As a developer, I want to eliminate circular dependencies between services, so that modules can be tested and deployed independently.

#### Acceptance Criteria

1. WHEN ResourceService deletes a resource, THE System SHALL emit a `resource.deleted` event instead of directly calling CollectionService
2. WHEN ResourceService is modified, THE System SHALL remove all direct imports of CollectionService
3. WHEN ResourceService is modified, THE System SHALL remove all direct method calls to `recompute_embedding` on CollectionService
4. WHEN a resource is deleted, THE System SHALL publish the resource ID through the event bus
5. IF a resource deletion event is emitted, THEN THE System SHALL ensure the event contains resource_id in the payload

### Requirement 4: Event-Driven Communication

**User Story:** As a developer, I want modules to communicate through events, so that they remain loosely coupled and independently deployable.

#### Acceptance Criteria

1. WHEN the Collections module is initialized, THE System SHALL create `modules/collections/handlers.py` for event subscriptions
2. WHEN a `resource.deleted` event is published, THE System SHALL invoke the Collections module handler
3. WHEN the Collections handler receives a `resource.deleted` event, THE System SHALL call `CollectionService.recompute_embedding()` for affected collections
4. WHEN an event handler fails, THE System SHALL log the error without affecting the event publisher
5. WHEN the System starts, THE System SHALL register all event handlers before processing requests

### Requirement 5: Resources Module Extraction

**User Story:** As a developer, I want the Resources domain isolated into its own module, so that resource management logic is self-contained.

#### Acceptance Criteria

1. WHEN the Resources module is created, THE System SHALL move `routers/resources.py` to `modules/resources/router.py`
2. WHEN the Resources module is created, THE System SHALL move `services/resource_service.py` to `modules/resources/service.py`
3. WHEN the Resources module is created, THE System SHALL move `schemas/resource.py` to `modules/resources/schema.py`
4. WHEN the Resources module is created, THE System SHALL move Resource-related models from `database/models.py` to `modules/resources/model.py`
5. WHEN the Resources module is accessed, THE System SHALL expose a clean public interface through `modules/resources/__init__.py`

### Requirement 6: Search Module Extraction

**User Story:** As a developer, I want the Search domain isolated into its own module, so that search functionality can evolve independently.

#### Acceptance Criteria

1. WHEN the Search module is created, THE System SHALL move `routers/search.py` to `modules/search/router.py`
2. WHEN the Search module is created, THE System SHALL move search-related services to `modules/search/service.py`
3. WHEN the Search module is created, THE System SHALL move `schemas/search.py` to `modules/search/schema.py`
4. WHEN the Search module is created, THE System SHALL consolidate hybrid_search_methods, search_service, and related services
5. WHEN the Search module is accessed, THE System SHALL expose a clean public interface through `modules/search/__init__.py`

### Requirement 7: Module Interface Contracts

**User Story:** As a developer, I want clear module interfaces, so that I know exactly what functionality each module provides.

#### Acceptance Criteria

1. WHEN a module is created, THE System SHALL define a public interface in the module's `__init__.py` file
2. WHEN a module interface is defined, THE System SHALL expose only router, service, and schema classes
3. WHEN a module interface is defined, THE System SHALL hide internal implementation details (models, helpers, utilities)
4. WHEN external code imports from a module, THE System SHALL enforce imports only from the module's `__init__.py`
5. WHEN a module interface changes, THE System SHALL update the interface version number

### Requirement 8: Backward Compatibility

**User Story:** As a developer, I want the refactoring to maintain API compatibility, so that existing clients continue to work without changes.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE System SHALL maintain all existing API endpoints at their current paths
2. WHEN an API request is received, THE System SHALL route to the new modular structure transparently
3. WHEN API responses are generated, THE System SHALL maintain the same response schemas as before refactoring
4. WHEN the System is deployed, THE System SHALL pass all existing integration tests without modification
5. WHEN the System is deployed, THE System SHALL maintain the same performance characteristics as before refactoring

### Requirement 9: Testing Infrastructure

**User Story:** As a developer, I want module-level testing capabilities, so that I can test each domain in isolation.

#### Acceptance Criteria

1. WHEN a module is created, THE System SHALL provide a `tests/` directory within the module
2. WHEN module tests are executed, THE System SHALL run tests without requiring other modules
3. WHEN module tests are executed, THE System SHALL mock event bus interactions
4. WHEN module tests are executed, THE System SHALL use in-memory database fixtures
5. WHEN the test suite runs, THE System SHALL execute module tests in parallel

### Requirement 10: Documentation and Migration Guide

**User Story:** As a developer, I want comprehensive documentation of the new architecture, so that I can understand and contribute to the modular structure.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE System SHALL provide an updated ARCHITECTURE_DIAGRAM.md with Phase 13.5 section
2. WHEN the architecture documentation is updated, THE System SHALL include ASCII diagrams showing module communication via Event Bus
3. WHEN the refactoring is complete, THE System SHALL provide a MIGRATION_GUIDE.md explaining the transition
4. WHEN the migration guide is created, THE System SHALL document how to add new modules
5. WHEN the migration guide is created, THE System SHALL document event-driven communication patterns

### Requirement 11: Cross-Module Dependencies

**User Story:** As a developer, I want to understand and minimize cross-module dependencies, so that modules remain loosely coupled.

#### Acceptance Criteria

1. WHEN modules need to communicate, THE System SHALL use event-driven communication as the primary mechanism
2. WHEN a module needs shared functionality, THE System SHALL access only the shared kernel components
3. WHEN cross-module queries are required, THE System SHALL use read-only repository interfaces
4. WHEN a module dependency is added, THE System SHALL document the dependency in the module's README
5. WHEN the System is analyzed, THE System SHALL provide a dependency graph showing module relationships

### Requirement 12: Event Bus Implementation

**User Story:** As a developer, I want a robust event bus implementation, so that modules can communicate reliably.

#### Acceptance Criteria

1. WHEN the event bus is initialized, THE System SHALL support synchronous event delivery
2. WHEN an event is emitted, THE System SHALL deliver the event to all registered handlers
3. WHEN an event handler fails, THE System SHALL continue delivering to remaining handlers
4. WHEN an event is emitted, THE System SHALL log the event type and payload for debugging
5. WHEN the System shuts down, THE System SHALL ensure all pending events are processed

### Requirement 13: Gradual Migration Strategy

**User Story:** As a developer, I want to migrate incrementally, so that the system remains functional throughout the refactoring process.

#### Acceptance Criteria

1. WHEN the migration begins, THE System SHALL start with the Collections module as the first vertical slice
2. WHEN a module is migrated, THE System SHALL maintain backward-compatible imports in the old location
3. WHEN a module is migrated, THE System SHALL add deprecation warnings to old import paths
4. WHEN all modules are migrated, THE System SHALL remove old layered structure files
5. WHEN the migration is complete, THE System SHALL update all import statements to use new module paths

### Requirement 14: Module Isolation Validation

**User Story:** As a developer, I want automated validation of module isolation, so that I can detect coupling violations early.

#### Acceptance Criteria

1. WHEN the System is built, THE System SHALL run a module isolation checker
2. WHEN the isolation checker runs, THE System SHALL detect direct imports between modules (excluding shared kernel)
3. WHEN the isolation checker runs, THE System SHALL detect circular dependencies
4. WHEN the isolation checker runs, THE System SHALL fail the build if violations are found
5. WHEN the isolation checker runs, THE System SHALL generate a report of module dependencies

### Requirement 15: Performance Monitoring

**User Story:** As a developer, I want to monitor the performance impact of event-driven communication, so that I can ensure the refactoring doesn't degrade performance.

#### Acceptance Criteria

1. WHEN an event is emitted, THE System SHALL record the event emission time
2. WHEN an event handler executes, THE System SHALL record the handler execution time
3. WHEN event metrics are collected, THE System SHALL expose metrics through the monitoring endpoint
4. WHEN event latency exceeds 100ms, THE System SHALL log a warning
5. WHEN the System is monitored, THE System SHALL provide event throughput metrics (events/second)
