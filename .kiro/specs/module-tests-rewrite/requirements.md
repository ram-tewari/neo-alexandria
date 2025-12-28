# Requirements Document: Module Endpoint Tests Rewrite

## Introduction

The current test suite for 6 backend modules is broken beyond repair due to outdated assumptions about model fields, missing mocking of external dependencies, and database compatibility issues. This spec defines requirements for completely rewriting these test files to match the actual application code.

## Glossary

- **Module**: A vertical slice containing router, service, schema, and model for a specific feature
- **Endpoint Test**: Integration test that exercises API endpoints via TestClient
- **Mock**: Test double that replaces external dependencies (Celery, AI services)
- **Fixture**: Reusable test setup code (database session, test client, factory functions)
- **PostgreSQL Compatibility**: Handling type differences between SQLite and PostgreSQL

## Requirements

### Requirement 1: Rewrite Annotations Module Tests

**User Story:** As a developer, I want passing tests for the annotations module, so that I can verify annotation CRUD operations work correctly.

#### Acceptance Criteria

1. THE System SHALL create test file `tests/modules/test_annotations_endpoints.py` with tests matching actual router endpoints
2. WHEN testing annotation creation, THE System SHALL use correct field names from the Annotation model (selection_start, selection_end, selection_text)
3. WHEN testing annotation creation, THE System SHALL handle boolean-to-integer conversion for is_private field
4. WHEN testing search operations, THE System SHALL mock AnnotationService search methods to avoid database-specific dependencies
5. WHEN testing export operations, THE System SHALL mock export methods to avoid file I/O
6. THE System SHALL include tests for: create, list, get, update, delete, search (fulltext, semantic, tags), export (markdown, json)

### Requirement 2: Rewrite Collections Module Tests

**User Story:** As a developer, I want passing tests for the collections module, so that I can verify collection management works correctly.

#### Acceptance Criteria

1. THE System SHALL create test file `tests/modules/test_collections_endpoints.py` with tests matching actual router endpoints
2. WHEN creating test collections, THE System SHALL use correct required fields (name, owner_id, visibility)
3. WHEN testing collection-resource relationships, THE System SHALL properly handle the many-to-many association
4. WHEN testing hierarchical collections, THE System SHALL verify parent-child relationships
5. THE System SHALL include tests for: create, list, get, update, delete, add resource, remove resource, list resources

### Requirement 3: Rewrite Curation Module Tests

**User Story:** As a developer, I want passing tests for the curation module, so that I can verify content curation workflows work correctly.

#### Acceptance Criteria

1. THE System SHALL create test file `tests/modules/test_curation_endpoints.py` with tests matching actual router endpoints
2. WHEN testing curation operations, THE System SHALL mock Celery tasks to avoid worker dependencies
3. WHEN creating test resources, THE System SHALL use correct field names (source instead of url, identifier for unique IDs)
4. WHEN testing batch operations, THE System SHALL verify multiple resources are processed correctly
5. THE System SHALL include tests for all curation endpoints defined in the router

### Requirement 4: Rewrite Graph Module Tests

**User Story:** As a developer, I want passing tests for the graph module, so that I can verify knowledge graph operations work correctly.

#### Acceptance Criteria

1. THE System SHALL create test file `tests/modules/test_graph_endpoints.py` with tests matching actual router endpoints
2. WHEN testing citation operations, THE System SHALL create valid Citation model instances with source_id and target_id
3. WHEN testing graph edge operations, THE System SHALL verify edge_type, weight, and metadata fields
4. WHEN testing discovery operations, THE System SHALL mock AI-based hypothesis generation
5. THE System SHALL include tests for: citations, graph edges, embeddings, discovery hypotheses

### Requirement 5: Rewrite Quality Module Tests

**User Story:** As a developer, I want passing tests for the quality module, so that I can verify quality assessment operations work correctly.

#### Acceptance Criteria

1. THE System SHALL create test file `tests/modules/test_quality_endpoints.py` with tests matching actual router endpoints
2. WHEN testing quality computation, THE System SHALL mock ML model inference to avoid model dependencies
3. WHEN testing quality metrics, THE System SHALL verify all quality dimension fields (accuracy, completeness, consistency, timeliness, relevance)
4. WHEN testing outlier detection, THE System SHALL verify is_quality_outlier and outlier_score fields
5. THE System SHALL include tests for: compute quality, get quality metrics, detect outliers, quality reports

### Requirement 6: Rewrite Scholarly Module Tests

**User Story:** As a developer, I want passing tests for the scholarly module, so that I can verify scholarly metadata extraction works correctly.

#### Acceptance Criteria

1. THE System SHALL create test file `tests/modules/test_scholarly_endpoints.py` with tests matching actual router endpoints
2. WHEN testing metadata extraction, THE System SHALL mock external API calls (DOI, PubMed, arXiv)
3. WHEN testing scholarly fields, THE System SHALL verify all scholarly metadata fields (authors, affiliations, doi, pmid, arxiv_id, journal, etc.)
4. WHEN testing extraction confidence, THE System SHALL verify metadata_completeness_score and extraction_confidence fields
5. THE System SHALL include tests for: extract metadata, enrich resource, validate identifiers

### Requirement 7: Shared Test Infrastructure

**User Story:** As a developer, I want reusable test fixtures, so that I can write tests efficiently without duplication.

#### Acceptance Criteria

1. THE System SHALL use existing conftest.py fixtures (db, client, create_test_resource, create_test_collection)
2. WHEN creating test resources, THE System SHALL use correct Resource model fields (title, source, identifier, ingestion_status)
3. WHEN creating test data, THE System SHALL handle JSON fields correctly (tags as JSON string, not Python list)
4. WHEN handling boolean fields, THE System SHALL use integer values (0/1) for SQLite compatibility
5. THE System SHALL provide clear error messages when tests fail

### Requirement 8: Mocking Strategy

**User Story:** As a developer, I want external dependencies mocked, so that tests run without Celery workers or AI services.

#### Acceptance Criteria

1. WHEN testing endpoints that trigger Celery tasks, THE System SHALL mock celery.send_task or specific task functions
2. WHEN testing endpoints that use AI services, THE System SHALL mock embedding generation and model inference
3. WHEN testing search operations, THE System SHALL mock database-specific full-text search
4. WHEN testing external API calls, THE System SHALL mock HTTP requests
5. THE System SHALL use unittest.mock.patch decorator for all mocking

### Requirement 9: Database Compatibility

**User Story:** As a developer, I want tests that work with both SQLite and PostgreSQL, so that tests pass in all environments.

#### Acceptance Criteria

1. WHEN using boolean fields, THE System SHALL store as integers (0/1) for SQLite compatibility
2. WHEN using JSON fields, THE System SHALL store as JSON strings, not Python objects
3. WHEN using UUID fields, THE System SHALL convert to strings in API payloads
4. WHEN creating test data, THE System SHALL use server_default values where defined
5. THE System SHALL handle timezone-aware datetime fields correctly

### Requirement 10: Test Coverage

**User Story:** As a developer, I want comprehensive test coverage, so that I can catch regressions early.

#### Acceptance Criteria

1. THE System SHALL test all HTTP methods (GET, POST, PUT, DELETE) for each endpoint
2. THE System SHALL test success cases (200, 201, 204 status codes)
3. THE System SHALL test error cases (400, 404, 422 status codes)
4. THE System SHALL test validation errors (invalid input data)
5. THE System SHALL test edge cases (empty lists, missing optional fields, boundary values)

### Requirement 11: Test Organization

**User Story:** As a developer, I want well-organized tests, so that I can find and maintain tests easily.

#### Acceptance Criteria

1. THE System SHALL organize tests into classes by functionality (e.g., TestAnnotationCRUD, TestAnnotationSearch)
2. THE System SHALL use descriptive test method names (test_create_annotation_success, test_create_annotation_invalid_offsets)
3. THE System SHALL include docstrings explaining what each test verifies
4. THE System SHALL follow AAA pattern (Arrange, Act, Assert) in test methods
5. THE System SHALL keep tests focused on single behaviors

### Requirement 12: Test Execution

**User Story:** As a developer, I want tests that run quickly and reliably, so that I get fast feedback.

#### Acceptance Criteria

1. WHEN running tests, THE System SHALL complete all 6 modules in under 30 seconds
2. WHEN tests fail, THE System SHALL provide clear error messages with actual vs expected values
3. WHEN tests use mocks, THE System SHALL verify mock calls where appropriate
4. WHEN tests create database records, THE System SHALL clean up after each test
5. THE System SHALL use function-scoped fixtures for database isolation
