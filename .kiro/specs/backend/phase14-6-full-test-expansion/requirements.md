# Requirements Document: Phase 14.6 - Full Test Suite Expansion

## Introduction

Phase 14.6 expands the Anti-Gaslighting test architecture established in Phase 14.5 to cover ALL 13 modules in Neo Alexandria 2.0. This phase implements comprehensive testing across four distinct layers: Golden Logic Tests, Edge Case & Pattern Tests, Integration Tests, and Performance Regression Tests.

## Glossary

- **Golden Data**: Immutable JSON files containing expected outputs for algorithmic logic
- **Anti-Gaslighting Protocol**: Testing methodology that prevents AI from "fixing" tests by changing assertions
- **Performance Regression**: Execution time exceeding established baseline thresholds
- **Mock Heavy AI**: Testing strategy that mocks ML model inference to avoid loading real transformers
- **Event Bus**: Asynchronous event system for module communication
- **Vertical Slice**: Self-contained module with its own models, schemas, services, and routes

## Requirements

### Requirement 1: Test Infrastructure Expansion

**User Story:** As a developer, I want enhanced test infrastructure, so that I can write comprehensive tests for all modules efficiently.

#### Acceptance Criteria

1. WHEN the test suite runs, THE System SHALL provide a mock_ml_inference fixture that mocks sentence-transformers and HuggingFace pipelines
2. WHEN a performance test executes, THE System SHALL use a @performance_limit decorator to enforce strict time limits
3. WHEN a performance test exceeds its time limit, THE System SHALL raise AssertionError with "PERFORMANCE REGRESSION" message
4. THE System SHALL NOT allow increasing timeout values on test failure
5. WHEN tests require ML inference, THE System SHALL mock the inference methods but validate service handling of outputs

### Requirement 2: Golden Data Expansion

**User Story:** As a test engineer, I want comprehensive golden data files, so that I can validate complex algorithmic logic across all modules.

#### Acceptance Criteria

1. WHEN testing taxonomy classification, THE System SHALL provide taxonomy_prediction.json with input text mapped to expected Category ID and Confidence
2. WHEN testing graph algorithms, THE System SHALL provide graph_algorithms.json with adjacency lists mapped to expected PageRank scores
3. WHEN testing scholarly parsing, THE System SHALL provide scholarly_parsing.json with raw PDF snippets mapped to expected LaTeX lists
4. WHEN testing collection aggregation, THE System SHALL provide collections_logic.json with resource vectors mapped to expected mean vectors
5. THE System SHALL store all golden data in backend/tests/golden_data/ directory
6. THE System SHALL ensure all golden data files are immutable and version-controlled

### Requirement 3: Taxonomy Module Testing

**User Story:** As a developer, I want comprehensive taxonomy module tests, so that I can ensure classification accuracy and tree integrity.

#### Acceptance Criteria

1. WHEN testing classification logic, THE System SHALL mock BERT inference and verify service maps vectors to correct node IDs using taxonomy_prediction.json
2. WHEN testing tree logic, THE System SHALL detect circular dependencies and raise ValueError when attempting to make a child the parent of its own parent
3. WHEN testing tree logic, THE System SHALL handle orphan nodes gracefully when deleting a parent
4. WHEN testing taxonomy flow, THE System SHALL verify category creation, resource assignment, and database updates
5. THE System SHALL organize taxonomy tests in tests/modules/taxonomy/ directory with test_classification.py, test_tree_logic.py, and test_flow.py

### Requirement 4: Graph Module Testing

**User Story:** As a developer, I want comprehensive graph module tests, so that I can ensure citation network accuracy and performance.

#### Acceptance Criteria

1. WHEN testing PageRank algorithm, THE System SHALL build in-memory NetworkX graphs matching graph_algorithms.json and verify calculated scores match exactly
2. WHEN testing graph traversal performance, THE System SHALL complete "Related Resources" queries on nodes with 100 edges within 50ms
3. WHEN testing edge cases, THE System SHALL handle disconnected nodes (0 edges) gracefully by returning empty lists without errors
4. WHEN testing graph flow, THE System SHALL verify citation extraction, graph updates, and event emissions
5. THE System SHALL organize graph tests in tests/modules/graph/ directory with test_pagerank.py and test_traversal.py

### Requirement 5: Collections Module Testing

**User Story:** As a developer, I want comprehensive collections module tests, so that I can ensure aggregation logic and lifecycle management work correctly.

#### Acceptance Criteria

1. WHEN testing aggregation logic, THE System SHALL mock 3 resources with specific vectors and verify collection mean vector matches collections_logic.json
2. WHEN testing collection lifecycle, THE System SHALL verify collection creation, resource addition, and event_bus.emit called with collection.updated
3. WHEN testing constraints, THE System SHALL prevent infinite folder nesting by enforcing max nesting depth
4. WHEN testing constraints, THE System SHALL handle duplicate resource additions idempotently or raise appropriate errors
5. THE System SHALL organize collections tests in tests/modules/collections/ directory with test_aggregation.py, test_lifecycle.py, and test_constraints.py

### Requirement 6: Scholarly Module Testing

**User Story:** As a developer, I want comprehensive scholarly module tests, so that I can ensure metadata extraction accuracy.

#### Acceptance Criteria

1. WHEN testing LaTeX parsing, THE System SHALL verify extracted equations match scholarly_parsing.json golden data
2. WHEN testing table extraction, THE System SHALL verify extracted tables match expected structure and content
3. WHEN testing citation extraction, THE System SHALL verify extracted citations match expected format
4. WHEN testing edge cases, THE System SHALL handle malformed LaTeX gracefully without crashing
5. THE System SHALL organize scholarly tests in tests/modules/scholarly/ directory

### Requirement 7: Curation Module Testing

**User Story:** As a developer, I want comprehensive curation module tests, so that I can ensure batch operations and review workflows function correctly.

#### Acceptance Criteria

1. WHEN testing batch operations, THE System SHALL verify multiple resources can be updated simultaneously
2. WHEN testing review workflows, THE System SHALL verify approval/rejection state transitions
3. WHEN testing edge cases, THE System SHALL handle empty batch operations gracefully
4. WHEN testing integration, THE System SHALL verify curation events are emitted correctly
5. THE System SHALL organize curation tests in tests/modules/curation/ directory

### Requirement 8: Recommendations Module Testing

**User Story:** As a developer, I want comprehensive recommendations module tests, so that I can ensure hybrid recommendation accuracy and performance.

#### Acceptance Criteria

1. WHEN testing NCF recommendations, THE System SHALL mock model inference and verify ranking logic
2. WHEN testing content-based recommendations, THE System SHALL verify similarity calculations match golden data
3. WHEN testing graph-based recommendations, THE System SHALL verify citation network traversal produces expected results
4. WHEN testing performance, THE System SHALL complete recommendation generation within 100ms for 100 candidates
5. THE System SHALL organize recommendations tests in tests/modules/recommendations/ directory

### Requirement 9: Annotations Module Testing

**User Story:** As a developer, I want comprehensive annotations module tests, so that I can ensure text highlighting and note management work correctly.

#### Acceptance Criteria

1. WHEN testing annotation creation, THE System SHALL verify precise text ranges are stored correctly
2. WHEN testing annotation search, THE System SHALL verify semantic search across annotations works correctly
3. WHEN testing edge cases, THE System SHALL handle overlapping annotations gracefully
4. WHEN testing integration, THE System SHALL verify annotation events are emitted correctly
5. THE System SHALL organize annotations tests in tests/modules/annotations/ directory

### Requirement 10: Authority Module Testing

**User Story:** As a developer, I want comprehensive authority module tests, so that I can ensure subject authority trees maintain integrity.

#### Acceptance Criteria

1. WHEN testing authority tree operations, THE System SHALL verify hierarchical relationships are maintained
2. WHEN testing edge cases, THE System SHALL prevent circular references in authority trees
3. WHEN testing integration, THE System SHALL verify authority assignments to resources
4. WHEN testing constraints, THE System SHALL enforce tree depth limits
5. THE System SHALL organize authority tests in tests/modules/authority/ directory

### Requirement 11: Monitoring Module Testing

**User Story:** As a developer, I want comprehensive monitoring module tests, so that I can ensure system health metrics are accurate.

#### Acceptance Criteria

1. WHEN testing health checks, THE System SHALL verify all module health endpoints return correct status
2. WHEN testing metrics collection, THE System SHALL verify performance metrics are captured accurately
3. WHEN testing edge cases, THE System SHALL handle missing metrics gracefully
4. WHEN testing integration, THE System SHALL verify monitoring events are emitted correctly
5. THE System SHALL organize monitoring tests in tests/modules/monitoring/ directory

### Requirement 12: Universal Test Template

**User Story:** As a developer, I want a universal test template, so that I can quickly create consistent tests for any module.

#### Acceptance Criteria

1. THE System SHALL provide test_template.py with Golden Logic test stub
2. THE System SHALL provide test_template.py with Edge Case test stub using pytest.raises
3. THE System SHALL provide test_template.py with Integration test stub using mock_event_bus
4. THE System SHALL provide test_template.py with Performance test stub using @performance_limit
5. THE System SHALL ensure template is copy-paste ready for all remaining modules

### Requirement 13: Event Verification Standards

**User Story:** As a developer, I want standardized event verification, so that I can ensure all integration tests validate event bus interactions.

#### Acceptance Criteria

1. WHEN testing any integration flow, THE System SHALL assert mock_event_bus.called is True
2. WHEN testing any integration flow, THE System SHALL verify the correct event type was emitted
3. WHEN testing any integration flow, THE System SHALL verify event payload contains expected data
4. THE System SHALL provide helper functions for common event verification patterns
5. THE System SHALL enforce event verification in all integration tests through protocol.py

### Requirement 14: Performance Baseline Establishment

**User Story:** As a developer, I want established performance baselines, so that I can detect regressions early.

#### Acceptance Criteria

1. WHEN testing search operations, THE System SHALL complete hybrid search within 500ms
2. WHEN testing graph traversal, THE System SHALL complete related resource queries within 50ms
3. WHEN testing recommendations, THE System SHALL generate recommendations within 100ms
4. WHEN testing quality scoring, THE System SHALL compute scores within 200ms
5. THE System SHALL document all performance baselines in test files

### Requirement 15: Mock Strategy Consistency

**User Story:** As a developer, I want consistent mocking strategies, so that tests are maintainable and reliable.

#### Acceptance Criteria

1. WHEN mocking ML models, THE System SHALL mock at the inference method level, not the model loading level
2. WHEN mocking external services, THE System SHALL use unittest.mock.patch with clear target paths
3. WHEN mocking database operations, THE System SHALL use in-memory SQLite for isolation
4. WHEN mocking event bus, THE System SHALL capture all emitted events for verification
5. THE System SHALL document mocking patterns in conftest.py

### Requirement 16: Test Organization Standards

**User Story:** As a developer, I want clear test organization, so that I can find and maintain tests easily.

#### Acceptance Criteria

1. THE System SHALL organize tests by module in tests/modules/[module_name]/ directories
2. THE System SHALL name test files descriptively: test_[feature].py
3. THE System SHALL group related tests in the same file
4. THE System SHALL provide __init__.py in each test directory
5. THE System SHALL maintain parallel structure between app/modules/ and tests/modules/

### Requirement 17: Coverage Requirements

**User Story:** As a developer, I want comprehensive test coverage, so that I can ensure system reliability.

#### Acceptance Criteria

1. WHEN running tests, THE System SHALL achieve >80% code coverage for all modules
2. WHEN running tests, THE System SHALL achieve 100% coverage for critical paths (resource creation, search, recommendations)
3. WHEN running tests, THE System SHALL report coverage metrics per module
4. THE System SHALL exclude mock and test files from coverage calculations
5. THE System SHALL fail CI builds if coverage drops below thresholds

### Requirement 18: Test Execution Performance

**User Story:** As a developer, I want fast test execution, so that I can iterate quickly during development.

#### Acceptance Criteria

1. WHEN running unit tests, THE System SHALL complete all unit tests within 30 seconds
2. WHEN running integration tests, THE System SHALL complete all integration tests within 60 seconds
3. WHEN running full test suite, THE System SHALL complete within 120 seconds
4. THE System SHALL support parallel test execution with pytest-xdist
5. THE System SHALL provide test execution time reports

### Requirement 19: Test Data Management

**User Story:** As a developer, I want efficient test data management, so that tests remain fast and maintainable.

#### Acceptance Criteria

1. WHEN tests require database records, THE System SHALL use factory fixtures to create minimal test data
2. WHEN tests require golden data, THE System SHALL load only the specific cases needed
3. WHEN tests complete, THE System SHALL clean up all test data automatically
4. THE System SHALL prevent test data pollution between test runs
5. THE System SHALL provide clear factory fixture documentation

### Requirement 20: Error Message Quality

**User Story:** As a developer, I want high-quality error messages, so that I can debug test failures quickly.

#### Acceptance Criteria

1. WHEN a golden data assertion fails, THE System SHALL display expected vs actual values clearly
2. WHEN a performance test fails, THE System SHALL display actual execution time vs limit
3. WHEN an event verification fails, THE System SHALL display expected vs actual event types
4. THE System SHALL include "IMPLEMENTATION FAILURE" in all golden data assertion errors
5. THE System SHALL include "DO NOT UPDATE THE TEST" in all golden data assertion errors
