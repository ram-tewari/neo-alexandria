# Requirements Document

## Introduction

Phase 14 completes the vertical slice architecture transformation started in Phase 13.5. While Phase 13.5 successfully extracted Collections, Resources, and Search into self-contained modules, approximately 80% of the codebase remains in the traditional layered architecture. This phase migrates all remaining domains into vertical slice modules, establishing a fully modular monolith architecture.

The remaining domains to migrate include: Annotations, Quality, Taxonomy/Classification, Recommendations, Graph/Citations/Discovery, Curation, Scholarly/Metadata, Monitoring, and shared infrastructure services (Embeddings, AI Core).

## Glossary

- **System**: Neo Alexandria 2.0 backend application
- **Vertical Slice Module**: A self-contained module containing router, service, schema, model, and handlers for a specific business domain
- **Shared Kernel**: Common components used across all modules (database, event_bus, base_model, embeddings)
- **Domain Module**: A vertical slice representing a bounded context
- **Event-Driven Communication**: Modules communicate by emitting and subscribing to events rather than direct imports
- **Module Interface**: The public API exposed through a module's `__init__.py` file
- **Cross-Cutting Concern**: Functionality used by multiple modules (embeddings, AI core, caching)
- **Strangler Fig Pattern**: Incremental migration where new architecture gradually replaces old

## Requirements

### Requirement 1: Annotations Module Extraction

**User Story:** As a developer, I want the Annotations domain isolated into its own module, so that annotation logic can be developed and tested independently.

#### Acceptance Criteria

1. WHEN the Annotations module is created, THE System SHALL move `routers/annotations.py` to `modules/annotations/router.py`
2. WHEN the Annotations module is created, THE System SHALL move `services/annotation_service.py` to `modules/annotations/service.py`
3. WHEN the Annotations module is created, THE System SHALL move annotation-related schemas to `modules/annotations/schema.py`
4. WHEN the Annotations module is created, THE System SHALL extract Annotation model from `database/models.py` to `modules/annotations/model.py`
5. WHEN the Annotations module is accessed, THE System SHALL expose a clean public interface through `modules/annotations/__init__.py`
6. WHEN a resource is deleted, THE Annotations module SHALL subscribe to `resource.deleted` event and cascade delete associated annotations
7. THE Annotations module SHALL emit `annotation.created`, `annotation.updated`, and `annotation.deleted` events

### Requirement 2: Quality Module Extraction

**User Story:** As a developer, I want the Quality Assessment domain isolated into its own module, so that quality scoring logic can evolve independently.

#### Acceptance Criteria

1. WHEN the Quality module is created, THE System SHALL move `routers/quality.py` to `modules/quality/router.py`
2. WHEN the Quality module is created, THE System SHALL move `services/quality_service.py` to `modules/quality/service.py`
3. WHEN the Quality module is created, THE System SHALL move `services/summarization_evaluator.py` to `modules/quality/evaluator.py`
4. WHEN the Quality module is created, THE System SHALL move quality-related schemas to `modules/quality/schema.py`
5. WHEN the Quality module is accessed, THE System SHALL expose a clean public interface through `modules/quality/__init__.py`
6. WHEN a resource is created or updated, THE Quality module SHALL subscribe to resource events and trigger quality recomputation
7. THE Quality module SHALL emit `quality.computed`, `quality.outlier_detected`, and `quality.degradation_detected` events

### Requirement 3: Taxonomy Module Extraction

**User Story:** As a developer, I want the Taxonomy and Classification domain isolated into its own module, so that ML classification logic is self-contained.

#### Acceptance Criteria

1. WHEN the Taxonomy module is created, THE System SHALL move `routers/taxonomy.py` to `modules/taxonomy/router.py`
2. WHEN the Taxonomy module is created, THE System SHALL move `routers/classification.py` endpoints to `modules/taxonomy/router.py`
3. WHEN the Taxonomy module is created, THE System SHALL move `services/taxonomy_service.py` to `modules/taxonomy/service.py`
4. WHEN the Taxonomy module is created, THE System SHALL move `services/ml_classification_service.py` to `modules/taxonomy/ml_service.py`
5. WHEN the Taxonomy module is created, THE System SHALL move `services/classification_service.py` to `modules/taxonomy/classification_service.py`
6. WHEN the Taxonomy module is accessed, THE System SHALL expose a clean public interface through `modules/taxonomy/__init__.py`
7. WHEN a resource is ingested, THE Taxonomy module SHALL subscribe to `resource.created` event and trigger auto-classification
8. THE Taxonomy module SHALL emit `resource.classified`, `taxonomy.node_created`, and `taxonomy.model_trained` events

### Requirement 4: Recommendations Module Extraction

**User Story:** As a developer, I want the Recommendations domain isolated into its own module, so that recommendation algorithms can be developed independently.

#### Acceptance Criteria

1. WHEN the Recommendations module is created, THE System SHALL move `routers/recommendation.py` and `routers/recommendations.py` to `modules/recommendations/router.py`
2. WHEN the Recommendations module is created, THE System SHALL move `services/recommendation_service.py` to `modules/recommendations/service.py`
3. WHEN the Recommendations module is created, THE System SHALL move `services/recommendation_strategies.py` to `modules/recommendations/strategies.py`
4. WHEN the Recommendations module is created, THE System SHALL move `services/hybrid_recommendation_service.py` to `modules/recommendations/hybrid_service.py`
5. WHEN the Recommendations module is created, THE System SHALL move `services/collaborative_filtering_service.py` to `modules/recommendations/collaborative.py`
6. WHEN the Recommendations module is created, THE System SHALL move `services/ncf_service.py` to `modules/recommendations/ncf.py`
7. WHEN the Recommendations module is created, THE System SHALL move `services/user_profile_service.py` to `modules/recommendations/user_profile.py`
8. WHEN the Recommendations module is accessed, THE System SHALL expose a clean public interface through `modules/recommendations/__init__.py`
9. WHEN a user interacts with a resource, THE Recommendations module SHALL subscribe to interaction events and update user profiles
10. THE Recommendations module SHALL emit `recommendation.generated`, `user.profile_updated`, and `interaction.recorded` events

### Requirement 5: Graph Module Extraction

**User Story:** As a developer, I want the Graph Intelligence and Citations domain isolated into its own module, so that knowledge graph logic is self-contained.

#### Acceptance Criteria

1. WHEN the Graph module is created, THE System SHALL move `routers/graph.py` to `modules/graph/router.py`
2. WHEN the Graph module is created, THE System SHALL move `routers/citations.py` to `modules/graph/citations_router.py`
3. WHEN the Graph module is created, THE System SHALL move `routers/discovery.py` to `modules/graph/discovery_router.py`
4. WHEN the Graph module is created, THE System SHALL move `services/graph_service.py` to `modules/graph/service.py`
5. WHEN the Graph module is created, THE System SHALL move `services/graph_service_phase10.py` to `modules/graph/advanced_service.py`
6. WHEN the Graph module is created, THE System SHALL move `services/graph_embeddings_service.py` to `modules/graph/embeddings.py`
7. WHEN the Graph module is created, THE System SHALL move `services/citation_service.py` to `modules/graph/citations.py`
8. WHEN the Graph module is created, THE System SHALL move `services/lbd_service.py` to `modules/graph/discovery.py`
9. WHEN the Graph module is accessed, THE System SHALL expose a clean public interface through `modules/graph/__init__.py`
10. WHEN a resource is created, THE Graph module SHALL subscribe to `resource.created` event and extract citations
11. THE Graph module SHALL emit `citation.extracted`, `graph.updated`, and `hypothesis.discovered` events

### Requirement 6: Curation Module Extraction

**User Story:** As a developer, I want the Curation domain isolated into its own module, so that content curation logic can be managed independently.

#### Acceptance Criteria

1. WHEN the Curation module is created, THE System SHALL move `routers/curation.py` to `modules/curation/router.py`
2. WHEN the Curation module is created, THE System SHALL move `services/curation_service.py` to `modules/curation/service.py`
3. WHEN the Curation module is created, THE System SHALL move curation-related schemas to `modules/curation/schema.py`
4. WHEN the Curation module is accessed, THE System SHALL expose a clean public interface through `modules/curation/__init__.py`
5. WHEN quality outliers are detected, THE Curation module SHALL subscribe to `quality.outlier_detected` event and add to review queue
6. THE Curation module SHALL emit `curation.reviewed`, `curation.approved`, and `curation.rejected` events

### Requirement 7: Scholarly Module Extraction

**User Story:** As a developer, I want the Scholarly Metadata domain isolated into its own module, so that academic metadata extraction is self-contained.

#### Acceptance Criteria

1. WHEN the Scholarly module is created, THE System SHALL move `routers/scholarly.py` to `modules/scholarly/router.py`
2. WHEN the Scholarly module is created, THE System SHALL move `services/metadata_extractor.py` to `modules/scholarly/extractor.py`
3. WHEN the Scholarly module is created, THE System SHALL move scholarly-related schemas to `modules/scholarly/schema.py`
4. WHEN the Scholarly module is accessed, THE System SHALL expose a clean public interface through `modules/scholarly/__init__.py`
5. WHEN a resource is ingested, THE Scholarly module SHALL subscribe to `resource.created` event and extract scholarly metadata
6. THE Scholarly module SHALL emit `metadata.extracted`, `equations.parsed`, and `tables.extracted` events

### Requirement 8: Monitoring Module Extraction

**User Story:** As a developer, I want the Monitoring domain isolated into its own module, so that observability features can be managed independently.

#### Acceptance Criteria

1. WHEN the Monitoring module is created, THE System SHALL move `routers/monitoring.py` to `modules/monitoring/router.py`
2. WHEN the Monitoring module is created, THE System SHALL consolidate monitoring-related services into `modules/monitoring/service.py`
3. WHEN the Monitoring module is created, THE System SHALL move monitoring-related schemas to `modules/monitoring/schema.py`
4. WHEN the Monitoring module is accessed, THE System SHALL expose a clean public interface through `modules/monitoring/__init__.py`
5. THE Monitoring module SHALL aggregate metrics from all other modules via event subscriptions
6. THE Monitoring module SHALL expose health check endpoints for all registered modules

### Requirement 9: Shared Kernel Enhancement

**User Story:** As a developer, I want cross-cutting concerns centralized in the shared kernel, so that all modules can access common functionality consistently.

#### Acceptance Criteria

1. WHEN the shared kernel is enhanced, THE System SHALL move `services/embedding_service.py` to `shared/embeddings.py`
2. WHEN the shared kernel is enhanced, THE System SHALL move `services/ai_core.py` to `shared/ai_core.py`
3. WHEN the shared kernel is enhanced, THE System SHALL move `cache/redis_cache.py` to `shared/cache.py`
4. THE shared kernel SHALL NOT depend on any domain modules
5. THE shared kernel SHALL provide consistent interfaces for embeddings, caching, and AI operations
6. WHEN a shared kernel component is modified, THE System SHALL ensure backward compatibility with existing modules

### Requirement 10: Authority Module Extraction

**User Story:** As a developer, I want the Authority/Subject domain isolated into its own module, so that subject authority logic is self-contained.

#### Acceptance Criteria

1. WHEN the Authority module is created, THE System SHALL move `routers/authority.py` to `modules/authority/router.py`
2. WHEN the Authority module is created, THE System SHALL move `services/authority_service.py` to `modules/authority/service.py`
3. WHEN the Authority module is accessed, THE System SHALL expose a clean public interface through `modules/authority/__init__.py`
4. THE Authority module SHALL provide subject suggestion and classification tree endpoints

### Requirement 11: Event-Driven Integration

**User Story:** As a developer, I want all modules to communicate through events, so that they remain loosely coupled.

#### Acceptance Criteria

1. WHEN a module needs data from another module, THE System SHALL use event-driven communication instead of direct imports
2. WHEN a module emits an event, THE System SHALL include all necessary data in the event payload
3. WHEN an event handler fails, THE System SHALL log the error and continue processing other handlers
4. THE System SHALL provide an event catalog documenting all events, their payloads, and subscribers
5. THE System SHALL support both synchronous and asynchronous event delivery

### Requirement 12: Module Isolation Enforcement

**User Story:** As a developer, I want automated validation of module isolation, so that coupling violations are detected early.

#### Acceptance Criteria

1. WHEN the isolation checker runs, THE System SHALL detect direct imports between domain modules
2. WHEN the isolation checker runs, THE System SHALL allow imports from shared kernel only
3. WHEN the isolation checker runs, THE System SHALL fail CI/CD if violations are found
4. THE System SHALL generate a module dependency graph showing all relationships
5. THE System SHALL provide clear error messages identifying violation locations

### Requirement 13: Backward Compatibility

**User Story:** As a developer, I want the refactoring to maintain API compatibility, so that existing clients continue to work.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE System SHALL maintain all existing API endpoints at their current paths
2. WHEN API responses are generated, THE System SHALL maintain the same response schemas
3. WHEN the System is deployed, THE System SHALL pass all existing integration tests
4. THE System SHALL provide deprecation warnings for any changed import paths
5. THE System SHALL maintain the same performance characteristics

### Requirement 14: Documentation and Migration Guide

**User Story:** As a developer, I want comprehensive documentation of the complete modular architecture, so that I can understand and contribute effectively.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE System SHALL update ARCHITECTURE_DIAGRAM.md with Phase 14 section
2. WHEN the refactoring is complete, THE System SHALL update MIGRATION_GUIDE.md with complete module list
3. WHEN a module is created, THE System SHALL include a README.md documenting its purpose, interface, and events
4. THE System SHALL provide an event catalog documenting all cross-module events
5. THE System SHALL update the DEVELOPER_GUIDE.md with complete modular architecture documentation

### Requirement 15: Legacy Code Cleanup

**User Story:** As a developer, I want all legacy layered structure files removed, so that the codebase is clean and consistent.

#### Acceptance Criteria

1. WHEN all modules are migrated, THE System SHALL delete the `routers/` directory
2. WHEN all modules are migrated, THE System SHALL delete the `services/` directory (except shared services moved to shared kernel)
3. WHEN all modules are migrated, THE System SHALL delete the `schemas/` directory
4. WHEN all modules are migrated, THE System SHALL update `database/models.py` to only contain truly shared models
5. THE System SHALL update all import statements throughout the codebase to use new module paths

