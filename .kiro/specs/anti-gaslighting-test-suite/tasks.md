# Implementation Plan: Anti-Gaslighting Test Suite

## Overview

This implementation plan creates a fresh "Anti-Gaslighting" test suite from scratch. The suite uses Golden Data (immutable JSON files) to decouple test expectations from test logic, preventing AI assistants from "fixing" tests by changing assertions.

All code is built from scratch with no dependencies on legacy test infrastructure.

## Tasks

- [x] 1. Create directory structure and base files
  - Create `backend/tests/` directory structure
  - Create `backend/tests/__init__.py`
  - Create `backend/tests/golden_data/` directory
  - Create `backend/tests/modules/` directory with subdirectories
  - _Requirements: 1.1, 12.1, 12.2, 12.3, 12.4_

- [x] 2. Implement Protocol Module
  - [x] 2.1 Create `backend/tests/protocol.py` with core assertion functions
    - Implement `load_golden_data(module)` function
    - Implement `assert_against_golden(module, case_id, actual_data)` function
    - Implement `GoldenDataError` exception class
    - Ensure error messages contain "IMPLEMENTATION FAILURE" and "DO NOT UPDATE THE TEST"
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 2.2 Add specialized assertion helpers
    - Implement `assert_score_against_golden()` for numeric comparisons with tolerance
    - Implement `assert_ranking_against_golden()` for ordered list comparisons
    - _Requirements: 2.2, 2.3_

  - [x] 2.3 Write property tests for protocol module
    - **Property 3: Error Message Format Compliance**
    - **Property 4: Error Message Content Completeness**
    - **Validates: Requirements 2.4, 2.5, 2.6, 11.1-11.5**

- [x] 3. Create Golden Data Files
  - [x] 3.1 Create `backend/tests/golden_data/quality_scoring.json`
    - Define `completeness_partial` case with score 0.5
    - Define `completeness_full` case with score 1.0
    - Define `completeness_minimal` case
    - Define `metadata_completeness_empty` case
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 3.2 Create `backend/tests/golden_data/search_ranking.json`
    - Define `rrf_fusion_scenario_1` with inputs and expected rankings
    - Define `rrf_fusion_empty_lists` case
    - Define `rrf_fusion_single_list` case
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 3.3 Create `backend/tests/golden_data/resource_ingestion.json`
    - Define `create_resource_success` case with expected response, db state, events
    - Define `create_resource_missing_url` case
    - Define `create_resource_duplicate_url` case
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 4. Implement Fresh Test Fixtures
  - [x] 4.1 Create `backend/tests/conftest.py` with database fixtures
    - Implement `db_engine` fixture (in-memory SQLite)
    - Implement `db_session` fixture (function-scoped)
    - Ensure tables are created before and dropped after each test
    - NO imports from legacy test code
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 3.7, 13.1, 13.2, 13.3, 13.4_

  - [x] 4.2 Add TestClient fixture
    - Implement `client` fixture with dependency override
    - Override `get_db` to use test `db_session`
    - _Requirements: 3.5, 13.5_

  - [x] 4.3 Add Event Bus fixtures
    - Implement `mock_event_bus` fixture using `unittest.mock`
    - Implement `clean_event_bus` fixture for state cleanup
    - _Requirements: 4.1, 4.4, 13.6_

  - [x] 4.4 Add test data factory fixtures
    - Implement `create_test_resource` factory fixture
    - _Requirements: 13.7_

  - [x] 4.5 Write property tests for database lifecycle
    - **Property 5: Database Lifecycle Isolation**
    - **Validates: Requirements 3.2, 3.3**

- [x] 5. Checkpoint - Verify infrastructure
  - Ensure all tests pass, ask the user if questions arise.
  - Verify protocol module loads Golden Data correctly
  - Verify fixtures create isolated database sessions
  - Verify event bus mock captures events

- [x] 6. Implement Quality Module Tests
  - [x] 6.1 Create `backend/tests/modules/quality/__init__.py`
    - _Requirements: 8.1_

  - [x] 6.2 Create `backend/tests/modules/quality/test_scoring.py`
    - Import `ContentQualityAnalyzer` from `app.modules.quality.service`
    - Implement `test_completeness_partial` using Golden Data
    - Implement `test_completeness_full` using Golden Data
    - Implement `test_completeness_minimal` using Golden Data
    - All assertions use `assert_against_golden()` or `assert_score_against_golden()`
    - NO inline expected values
    - _Requirements: 8.2, 8.3, 8.4, 8.5_

- [x] 7. Implement Search Module Tests
  - [x] 7.1 Create `backend/tests/modules/search/__init__.py`
    - _Requirements: 9.1_

  - [x] 7.2 Create `backend/tests/modules/search/test_hybrid.py`
    - Import RRF service from `app.modules.search.service`
    - Implement `test_rrf_fusion_basic` with mock inputs [A,B,C], [C,A,D], [B,A,E]
    - Implement `test_rrf_fusion_empty_lists`
    - Implement `test_rrf_fusion_single_list`
    - All assertions use `assert_ranking_against_golden()`
    - NO inline expected rankings
    - _Requirements: 9.2, 9.3, 9.4, 9.5_

- [ ] 8. Implement Resource Module Integration Tests
  - [x] 8.1 Create `backend/tests/modules/resources/__init__.py`
    - _Requirements: 10.1_

  - [x] 8.2 Create `backend/tests/modules/resources/test_ingestion_flow.py`
    - Implement `test_create_resource_success` integration test
    - Use `client` fixture to POST to `/resources`
    - Use `mock_event_bus` fixture to capture events
    - Verify HTTP 202 response
    - Verify database row with `status="pending"`
    - Verify `resource.created` event emitted
    - _Requirements: 10.2, 10.3, 10.4, 10.5, 10.6_

  - [x] 8.3 Implement error case tests
    - Implement `test_create_resource_missing_url`
    - Implement `test_create_resource_duplicate_url`
    - _Requirements: 10.4_

  - [x] 8.4 Write property tests for event verification
    - **Property 6: Event Verification Completeness**
    - **Validates: Requirements 4.1, 4.3, 4.5**

- [x] 9. Checkpoint - Verify all module tests
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest backend/tests/modules/ -v`
  - Verify all tests use Golden Data assertions
  - Verify no inline expected values in test files

- [x] 10. Final validation and documentation
  - [x] 10.1 Run full test suite
    - Execute `pytest backend/tests/ -v`
    - Verify all tests pass
    - _Requirements: 13.8_

  - [x] 10.2 Verify independence from legacy tests
    - Confirm no imports from `tests_legacy/`
    - Confirm test suite runs independently
    - _Requirements: 13.1, 13.2, 13.3, 13.8_

## Notes

- All tasks are required for comprehensive test coverage
- Each task references specific requirements for traceability
- All tests must use Golden Data assertions - no inline expected values
- The test suite must be completely independent of legacy test code
- Property-based tests use `hypothesis` library with minimum 100 iterations
