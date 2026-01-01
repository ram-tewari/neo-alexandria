# Requirements Document

## Introduction

Phase 14.5 introduces an "Anti-Gaslighting" Test Suite architecture for Neo Alexandria 2.0. This testing approach decouples test expectations from test logic using "Golden Data" (immutable JSON files). The goal is to prevent AI coding assistants from "fixing" tests by changing inline assertions when features are broken, ensuring that test failures accurately reflect implementation bugs rather than test modifications.

**CRITICAL: This test suite is built from SCRATCH.** It does NOT use, inherit from, or reference any existing test fixtures, conftest.py files, or test utilities from the legacy test suite. All fixtures, helpers, and infrastructure are newly created specifically for this anti-gaslighting architecture.

## Glossary

- **Golden_Data**: Immutable JSON files containing expected test outcomes that serve as the single source of truth for assertions
- **Anti_Gaslighting_Pattern**: Testing architecture where assertions read from read-only external files rather than inline values
- **Protocol_Module**: Helper module that enforces Golden Data pattern by loading and comparing against JSON truth sources
- **Test_Fixture**: Newly created reusable test data and setup code (NOT inherited from legacy tests)
- **Fresh_Infrastructure**: All test infrastructure created from scratch without dependencies on existing test code
- **Event_Bus**: Event-driven architecture component for inter-module communication
- **Quality_Service**: Service for calculating multi-dimensional quality scores
- **RRF_Fusion**: Reciprocal Rank Fusion algorithm for combining multiple search result rankings
- **Integration_Test**: Test that verifies multiple components working together including database and events

## Requirements

### Requirement 1: Golden Data Directory Structure

**User Story:** As a developer, I want immutable truth source files stored in a dedicated directory, so that test expectations cannot be accidentally modified during test fixes.

#### Acceptance Criteria

1. THE Test_Suite SHALL create a `tests/golden_data/` directory for storing all Golden Data JSON files
2. THE Golden_Data files SHALL be treated as read-only truth sources that define expected test outcomes
3. WHEN a test needs expected values, THE Test_Suite SHALL load them from Golden_Data files rather than inline assertions
4. THE Golden_Data directory SHALL contain separate JSON files for each domain: `quality_scoring.json`, `search_ranking.json`, `resource_ingestion.json`
5. WHERE test expectations need to change, THE developer SHALL explicitly update Golden_Data files with documented reasoning

### Requirement 2: Protocol Module Implementation

**User Story:** As a developer, I want a helper module that enforces the Golden Data pattern, so that all tests consistently use external truth sources for assertions.

#### Acceptance Criteria

1. THE Test_Suite SHALL create a `tests/protocol.py` module containing assertion helper functions
2. WHEN `assert_against_golden(module, case_id, actual_data)` is called, THE Protocol_Module SHALL load the corresponding JSON file from `golden_data/`
3. WHEN `assert_against_golden()` is called, THE Protocol_Module SHALL retrieve expected data by `case_id` key from the loaded JSON
4. WHEN actual data does not match expected data, THE Protocol_Module SHALL raise AssertionError with message containing "IMPLEMENTATION FAILURE"
5. WHEN assertion fails, THE Protocol_Module SHALL include "DO NOT UPDATE THE TEST" in the error message to prevent AI assistants from modifying test code
6. THE Protocol_Module SHALL provide clear diff output showing expected vs actual values on failure

### Requirement 3: Test Database Isolation

**User Story:** As a developer, I want each test to run with a fresh isolated database, so that tests do not interfere with each other.

#### Acceptance Criteria

1. THE Test_Suite SHALL use `sqlite:///:memory:` for all database tests
2. WHEN a test function starts, THE Test_Fixture SHALL create all required database tables from scratch
3. WHEN a test function completes, THE Test_Fixture SHALL drop all database tables
4. THE `db_session` fixture SHALL be function-scoped to ensure complete isolation between tests
5. THE `client` fixture SHALL override the application's `get_db` dependency to use the test `db_session`
6. THE Test_Suite SHALL NOT import or use any fixtures from existing `tests/conftest.py` or `tests_legacy/conftest.py` files
7. THE Test_Suite SHALL create its own independent `conftest.py` with all fixtures built from scratch

### Requirement 4: Event Bus Verification

**User Story:** As a developer, I want integration tests to verify that events are actually fired, so that I can confirm event-driven workflows function correctly.

#### Acceptance Criteria

1. THE Test_Suite SHALL provide a `mock_event_bus` fixture that spies on `event_bus.emit` calls
2. WHEN an integration test creates a resource, THE Test_Suite SHALL verify that `resource.created` event was emitted
3. WHEN verifying events, THE Test_Suite SHALL check both event type and event payload
4. THE `mock_event_bus` fixture SHALL use `unittest.mock` to capture event emissions without blocking actual event handling
5. WHERE event verification is critical, THE Test_Suite SHALL fail if expected events are not emitted

### Requirement 5: Quality Scoring Golden Data

**User Story:** As a developer, I want quality scoring expectations defined in Golden Data, so that quality calculation tests have immutable truth sources.

#### Acceptance Criteria

1. THE Golden_Data SHALL define `quality_scoring.json` with test cases for quality score calculations
2. WHEN testing partial completeness, THE Golden_Data SHALL specify expected score (0.5) and reasoning (["Missing subject", "Missing language"])
3. WHEN testing full completeness, THE Golden_Data SHALL specify expected score (1.0) and empty reasoning array
4. THE Quality_Service tests SHALL use `assert_against_golden("quality_scoring", case_id, result)` for all assertions
5. WHERE quality scoring algorithm changes, THE developer SHALL update Golden_Data with documented reasoning

### Requirement 6: Search Ranking Golden Data

**User Story:** As a developer, I want search ranking expectations defined in Golden Data, so that RRF fusion algorithm tests have immutable truth sources.

#### Acceptance Criteria

1. THE Golden_Data SHALL define `search_ranking.json` with test cases for RRF fusion scenarios
2. WHEN testing RRF fusion, THE Golden_Data SHALL specify expected `ranked_ids` order (e.g., ["doc_C", "doc_A", "doc_B", "doc_D", "doc_E"])
3. WHEN testing RRF fusion, THE Golden_Data SHALL specify expected `scores` for top results (e.g., {"doc_C": 0.8, "doc_A": 0.75})
4. THE Search tests SHALL use `assert_against_golden("search_ranking", case_id, result)` for ranking assertions
5. WHERE RRF algorithm parameters change, THE developer SHALL update Golden_Data with documented reasoning

### Requirement 7: Resource Ingestion Golden Data

**User Story:** As a developer, I want resource ingestion expectations defined in Golden Data, so that ingestion workflow tests have immutable truth sources.

#### Acceptance Criteria

1. THE Golden_Data SHALL define `resource_ingestion.json` with test cases for resource creation workflows
2. WHEN testing resource creation, THE Golden_Data SHALL specify expected HTTP status codes and response structures
3. WHEN testing resource creation, THE Golden_Data SHALL specify expected database state (status="pending")
4. WHEN testing resource creation, THE Golden_Data SHALL specify expected events to be emitted
5. THE Resource tests SHALL use `assert_against_golden("resource_ingestion", case_id, result)` for workflow assertions

### Requirement 8: Quality Module Test Implementation

**User Story:** As a developer, I want quality scoring tests that use Golden Data, so that quality calculations are validated against immutable truth sources.

#### Acceptance Criteria

1. THE Test_Suite SHALL create `tests/modules/quality/test_scoring.py` for quality service tests
2. WHEN testing completeness calculation, THE test SHALL construct a resource object with missing fields
3. WHEN testing completeness calculation, THE test SHALL call QualityService to calculate the score
4. WHEN asserting results, THE test SHALL use `assert_against_golden("quality_scoring", "completeness_partial", result)`
5. THE test SHALL NOT contain inline expected values - all expectations come from Golden_Data

### Requirement 9: Search Module Test Implementation

**User Story:** As a developer, I want search ranking tests that use Golden Data, so that RRF fusion is validated against immutable truth sources.

#### Acceptance Criteria

1. THE Test_Suite SHALL create `tests/modules/search/test_hybrid.py` for search ranking tests
2. WHEN testing RRF algorithm, THE test SHALL provide mock inputs: Dense results [A, B, C], Sparse results [C, A, D], Keyword results [B, A, E]
3. WHEN testing RRF algorithm, THE test SHALL run fusion logic and capture ranked results
4. WHEN asserting results, THE test SHALL use `assert_against_golden("search_ranking", "rrf_fusion_scenario_1", result)`
5. THE test SHALL NOT contain inline expected rankings - all expectations come from Golden_Data

### Requirement 10: Resource Module Integration Test Implementation

**User Story:** As a developer, I want resource ingestion integration tests that verify database state and event emissions, so that the full ingestion workflow is validated.

#### Acceptance Criteria

1. THE Test_Suite SHALL create `tests/modules/resources/test_ingestion_flow.py` for integration tests
2. WHEN testing resource creation, THE test SHALL use the `client` fixture to POST to `/resources`
3. WHEN testing resource creation, THE test SHALL use the `mock_event_bus` fixture to capture events
4. WHEN asserting HTTP response, THE test SHALL verify HTTP 202 status code
5. WHEN asserting database state, THE test SHALL verify resource row created with `status="pending"`
6. WHEN asserting events, THE test SHALL verify `event_bus.emit` was called with `resource.created` event type

### Requirement 11: Error Message Standards

**User Story:** As a developer, I want clear error messages that prevent AI assistants from modifying tests, so that implementation bugs are fixed rather than tests being changed.

#### Acceptance Criteria

1. WHEN a Golden Data assertion fails, THE error message SHALL start with "IMPLEMENTATION FAILURE:"
2. WHEN a Golden Data assertion fails, THE error message SHALL include "DO NOT UPDATE THE TEST - Fix the implementation instead"
3. WHEN a Golden Data assertion fails, THE error message SHALL show the Golden Data file path and case_id
4. WHEN a Golden Data assertion fails, THE error message SHALL show expected value from Golden Data
5. WHEN a Golden Data assertion fails, THE error message SHALL show actual value from implementation

### Requirement 12: Test Suite Organization

**User Story:** As a developer, I want a well-organized test structure, so that tests are easy to find and maintain.

#### Acceptance Criteria

1. THE Test_Suite SHALL organize tests in `tests/modules/[module_name]/` directories
2. THE Test_Suite SHALL place Golden Data in `tests/golden_data/` directory
3. THE Test_Suite SHALL place shared fixtures in `tests/conftest.py`
4. THE Test_Suite SHALL place assertion helpers in `tests/protocol.py`
5. THE Test_Suite SHALL use descriptive test function names that indicate what is being tested

### Requirement 13: Fresh Infrastructure - No Legacy Dependencies

**User Story:** As a developer, I want a completely fresh test infrastructure, so that legacy bugs and assumptions do not contaminate the new test suite.

#### Acceptance Criteria

1. THE Test_Suite SHALL NOT import any fixtures from `backend/tests_legacy/conftest.py`
2. THE Test_Suite SHALL NOT import any utilities from existing test helper modules
3. THE Test_Suite SHALL NOT reference or depend on any existing test files in `backend/tests_legacy/`
4. THE Test_Suite SHALL create all database session management code from scratch
5. THE Test_Suite SHALL create all TestClient setup code from scratch
6. THE Test_Suite SHALL create all mock/spy utilities from scratch using only `unittest.mock`
7. WHERE existing application code is needed, THE Test_Suite SHALL import directly from `app.modules.*` and `app.shared.*`
8. THE Test_Suite SHALL be completely self-contained and runnable independently of legacy tests
