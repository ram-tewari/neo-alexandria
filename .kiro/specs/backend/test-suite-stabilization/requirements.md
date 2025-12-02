# Requirements Document

## Introduction

This specification addresses the systematic resolution of 89 failing tests and 121 test errors across the Neo Alexandria backend test suite. The failures span multiple phases including ingestion, curation, search, graph intelligence, quality assessment, and classification systems. The goal is to restore test suite stability by fixing database schema mismatches, API endpoint issues, service method signatures, and SQLAlchemy session management problems.

## Glossary

- **Test Suite**: The complete collection of automated tests for the Neo Alexandria backend system
- **Database Schema**: The structure of database tables including columns, types, and relationships
- **API Endpoint**: HTTP routes that expose backend functionality to clients
- **Service Layer**: Business logic components that orchestrate data operations
- **SQLAlchemy Session**: Database connection context for ORM operations
- **Migration**: Database schema version control and update mechanism
- **Test Fixture**: Reusable test data and setup code
- **Mock Object**: Test double that simulates real component behavior
- **Integration Test**: Test that verifies multiple components working together
- **Unit Test**: Test that verifies a single component in isolation

## Requirements

### Requirement 1: Database Schema Consistency

**User Story:** As a developer, I want the database schema to match the model definitions, so that tests can create and query resources without operational errors.

#### Acceptance Criteria

1. WHEN THE Test_Suite executes database operations, THE Database_Schema SHALL include all columns referenced by model classes
2. WHEN THE Resource_Model defines a sparse_embedding field, THE resources_table SHALL contain a sparse_embedding column
3. WHEN THE Resource_Model defines description and publisher fields, THE resources_table SHALL contain description and publisher columns
4. WHEN THE Test_Suite creates test data, THE Database_Schema SHALL support all required fields without raising OperationalError exceptions
5. WHERE alembic migrations exist, THE Migration_System SHALL apply all pending migrations before test execution

### Requirement 2: API Endpoint Availability

**User Story:** As a test suite, I want all documented API endpoints to be registered and accessible, so that integration tests can verify API functionality.

#### Acceptance Criteria

1. WHEN THE Test_Suite requests the discovery API endpoints, THE API_Router SHALL return HTTP 200 status codes for valid requests
2. WHEN THE Test_Suite requests quality degradation endpoints, THE API_Router SHALL return HTTP 200 status codes for valid requests
3. WHEN THE Test_Suite requests invalid endpoints with bad parameters, THE API_Router SHALL return appropriate HTTP 4xx error codes
4. THE API_Router SHALL register all phase 9 quality assessment endpoints including /quality/degradation, /quality/details, and /quality/outliers
5. THE API_Router SHALL register all phase 10 graph intelligence endpoints including /discovery/open, /discovery/closed, and /discovery/neighbors

### Requirement 3: Service Method Signature Compatibility

**User Story:** As a test developer, I want service method signatures to match their documented interfaces, so that tests can call methods with correct parameters.

#### Acceptance Criteria

1. WHEN THE Test_Suite calls LBDService.open_discovery(), THE Method_Signature SHALL accept start_resource_id and end_resource_id parameters
2. WHEN THE Test_Suite calls generate_user_profile_vector(), THE Method_Signature SHALL accept db and user_id as required parameters
3. WHEN THE Test_Suite instantiates DiscoveryHypothesis models, THE Model_Constructor SHALL accept start_resource_id and end_resource_id parameters
4. WHEN THE Test_Suite calls GraphEmbeddingsService methods, THE Service_Class SHALL provide build_hnsw_index() and compute_graph2vec_embeddings() methods
5. WHEN THE Test_Suite calls recommendation_service functions, THE Service_Module SHALL export all functions referenced by tests

### Requirement 4: SQLAlchemy Session Management

**User Story:** As a test developer, I want database objects to remain attached to sessions throughout test execution, so that tests can access object attributes without DetachedInstanceError exceptions.

#### Acceptance Criteria

1. WHEN THE Test_Suite creates Resource objects in a session, THE Session_Manager SHALL keep objects attached until explicitly detached
2. WHEN THE Test_Suite accesses lazy-loaded relationships, THE Session_Manager SHALL maintain session binding for attribute access
3. WHEN THE Test_Suite commits transactions, THE Session_Manager SHALL refresh objects to maintain attribute accessibility
4. WHERE tests use fixtures that create database objects, THE Fixture_Implementation SHALL use session.refresh() or session.expunge() appropriately
5. WHEN THE Test_Suite passes objects between test phases, THE Test_Implementation SHALL use session.merge() or eager loading to prevent detachment

### Requirement 5: Quality Service Method Consistency

**User Story:** As a test developer, I want quality service methods to have consistent naming and return structures, so that tests can reliably verify quality assessment functionality.

#### Acceptance Criteria

1. WHEN THE Test_Suite calls quality analysis methods, THE Quality_Service SHALL return dictionaries containing word_count, fk_grade, and reading_ease keys
2. WHEN THE Test_Suite accesses ContentQualityAnalyzer attributes, THE Analyzer_Class SHALL provide text_readability() and overall_quality() methods
3. WHEN THE Test_Suite calls quality dimension methods, THE Quality_Service SHALL compute accuracy, completeness, consistency, timeliness, and relevance scores
4. THE ContentQualityAnalyzer SHALL not expose deprecated method names like content_readability or overall_quality_score
5. WHEN THE Test_Suite evaluates summaries, THE Summarization_Evaluator SHALL return structured evaluation results with all expected metrics

### Requirement 6: Test Data Fixture Reliability

**User Story:** As a test developer, I want test fixtures to create valid test data that matches production data structures, so that tests accurately verify system behavior.

#### Acceptance Criteria

1. WHEN THE Test_Suite uses resource fixtures, THE Fixture_Implementation SHALL create resources with all required fields populated
2. WHEN THE Test_Suite creates test resources with quality scores, THE Resource_Objects SHALL have quality_score values greater than 0.0
3. WHEN THE Test_Suite creates test resources with file paths, THE Resource_Objects SHALL have valid file_path values that are not None
4. WHEN THE Test_Suite creates test embeddings, THE Embedding_Objects SHALL have valid vector data that is not empty or None
5. WHERE tests require specific resource states, THE Fixture_Implementation SHALL provide factory methods for common test scenarios

### Requirement 7: Vector Operation Correctness

**User Story:** As a test developer, I want vector operations to produce mathematically correct results, so that recommendation and similarity tests verify actual algorithm behavior.

#### Acceptance Criteria

1. WHEN THE Test_Suite calculates cosine similarity between orthogonal vectors, THE Similarity_Function SHALL return 0.0 within floating-point tolerance
2. WHEN THE Test_Suite converts embeddings to numpy vectors, THE Conversion_Function SHALL return valid numpy arrays for non-empty inputs
3. WHEN THE Test_Suite converts None or empty embeddings, THE Conversion_Function SHALL return None or empty arrays as documented
4. WHEN THE Test_Suite calculates vector similarities, THE Algorithm_Implementation SHALL handle edge cases like zero vectors without raising exceptions
5. THE Vector_Operations SHALL use consistent data types and shapes across all vector manipulation functions

### Requirement 8: Performance Test Threshold Adjustment

**User Story:** As a test developer, I want performance test thresholds to reflect realistic system capabilities, so that tests fail only when actual performance degrades.

#### Acceptance Criteria

1. WHEN THE Test_Suite measures annotation creation performance, THE Performance_Threshold SHALL be set to achievable values based on actual system performance
2. WHEN THE Test_Suite measures AI summary generation, THE Performance_Threshold SHALL account for actual token counts and model behavior
3. WHEN THE Test_Suite measures search latency, THE Performance_Threshold SHALL reflect realistic query execution times
4. WHERE performance tests fail consistently, THE Test_Implementation SHALL either fix performance issues or adjust thresholds to realistic values
5. THE Performance_Tests SHALL document the rationale for threshold values in test comments

### Requirement 9: Test File Path Resolution

**User Story:** As a test developer, I want test files to correctly resolve paths to application code, so that tests can import and verify the correct modules.

#### Acceptance Criteria

1. WHEN THE Test_Suite imports application modules, THE Import_Statements SHALL use correct relative or absolute paths
2. WHEN THE Test_Suite verifies file existence, THE Path_Resolution SHALL use paths relative to the project root
3. WHERE tests reference router files, THE File_Paths SHALL point to backend/app/routers/ not backend/tests/integration/phase*/app/routers/
4. WHERE tests reference service files, THE File_Paths SHALL point to backend/app/services/ not test-specific paths
5. THE Test_Suite SHALL not create duplicate directory structures that shadow application code

### Requirement 10: Test Assertion Accuracy

**User Story:** As a test developer, I want test assertions to verify actual system behavior, so that passing tests indicate correct functionality.

#### Acceptance Criteria

1. WHEN THE Test_Suite asserts dictionary key presence, THE Assertion SHALL check for keys that the system actually returns
2. WHEN THE Test_Suite asserts numeric comparisons, THE Assertion SHALL use appropriate comparison operators and tolerance values
3. WHEN THE Test_Suite asserts response structure, THE Assertion SHALL match the actual API response format
4. WHERE assertions fail due to incorrect expectations, THE Test_Implementation SHALL update assertions to match correct system behavior
5. THE Test_Suite SHALL distinguish between bugs in application code and bugs in test code when fixing failures
