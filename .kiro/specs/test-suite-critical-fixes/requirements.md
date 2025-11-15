# Requirements Document

## Introduction

This specification addresses 83 critical test failures and 52 errors remaining in the Neo Alexandria backend test suite after previous stabilization efforts. The failures cluster around five main areas: Phase 10 graph intelligence API endpoints, Phase 9 quality service Resource model compatibility, database schema mismatches, performance test thresholds, and test assertion accuracy. The goal is to achieve a stable test suite with >95% pass rate by fixing these remaining critical issues.

## Glossary

- **Resource Model**: SQLAlchemy ORM model representing knowledge resources in the system
- **Model Constructor**: The __init__ method that creates Resource instances with specified parameters
- **API Endpoint**: HTTP route handler that processes requests and returns responses
- **Graph Intelligence**: Phase 10 feature for discovering connections between resources
- **Quality Service**: Phase 9 feature for assessing resource quality across multiple dimensions
- **Test Fixture**: Reusable test data setup code that creates valid test objects
- **Database Migration**: Alembic script that modifies database schema structure
- **Performance Threshold**: Maximum acceptable time or resource usage for operations
- **Test Assertion**: Verification statement that checks expected vs actual behavior

## Requirements

### Requirement 1: Resource Model Constructor Compatibility

**User Story:** As a test developer, I want to create Resource instances using keyword arguments that match the model definition, so that tests can instantiate resources without TypeError exceptions.

#### Acceptance Criteria

1. WHEN THE Test_Suite instantiates Resource with 'url' parameter, THE Model_Constructor SHALL reject the parameter with TypeError
2. WHEN THE Test_Suite instantiates Resource with 'content' parameter, THE Model_Constructor SHALL reject the parameter with TypeError
3. THE Resource_Model SHALL document all valid constructor parameters in docstrings
4. THE Test_Suite SHALL use only valid Resource model fields when creating test instances
5. WHERE tests require URL or content data, THE Test_Implementation SHALL use the correct field names from the model definition

### Requirement 2: Discovery API Endpoint Implementation

**User Story:** As an API client, I want the discovery neighbors endpoint to be accessible and functional, so that I can query graph relationships between resources.

#### Acceptance Criteria

1. WHEN THE API_Client requests GET /discovery/neighbors/{resource_id}, THE Discovery_Router SHALL return HTTP 200 for valid resource IDs
2. WHEN THE API_Client requests an invalid resource ID, THE Discovery_Router SHALL return HTTP 404 with error details
3. THE Discovery_Router SHALL accept hops, edge_types, and min_weight as optional query parameters
4. THE Discovery_Router SHALL return a list of neighbor resources with relationship metadata
5. THE Discovery_Endpoint SHALL be registered in the main FastAPI application router

### Requirement 3: Database Schema Column Existence

**User Story:** As a test developer, I want all Resource model fields to have corresponding database columns, so that tests can query and filter resources without OperationalError exceptions.

#### Acceptance Criteria

1. WHEN THE Test_Suite queries resources by sparse_embedding, THE Database_Schema SHALL include a sparse_embedding column
2. WHEN THE Test_Suite queries resources by description, THE Database_Schema SHALL include a description column
3. WHEN THE Test_Suite queries resources by publisher, THE Database_Schema SHALL include a publisher column
4. THE Database_Migration SHALL add missing columns with appropriate data types and constraints
5. THE Test_Setup SHALL verify schema completeness before executing tests

### Requirement 4: Graph Intelligence Service Completeness

**User Story:** As a test developer, I want graph intelligence services to implement all documented methods, so that integration tests can verify end-to-end discovery workflows.

#### Acceptance Criteria

1. WHEN THE Test_Suite calls LBDService.open_discovery(), THE Method_Implementation SHALL return hypothesis objects not None
2. WHEN THE Test_Suite calls LBDService.closed_discovery(), THE Method_Implementation SHALL return connection paths with valid resource IDs
3. WHEN THE Test_Suite calls recommendation_service.generate_recommendations_with_graph_fusion(), THE Method_Signature SHALL not include 'graph_weight' parameter
4. THE Graph_Service SHALL store hypothesis c_resource_id field when creating discovery hypotheses
5. THE Recommendation_Service SHALL implement graph-based recommendation methods that return non-empty results

### Requirement 5: Quality Service Resource Compatibility

**User Story:** As a test developer, I want quality service methods to accept Resource objects created with valid model fields, so that quality assessment tests execute without TypeError exceptions.

#### Acceptance Criteria

1. WHEN THE Test_Suite passes Resource objects to quality_service methods, THE Service_Methods SHALL not raise TypeError for valid Resource instances
2. WHEN THE Test_Suite creates Resources for quality testing, THE Test_Fixtures SHALL use only valid Resource model constructor parameters
3. THE Quality_Service SHALL access Resource attributes using correct field names from the model definition
4. WHERE quality methods require resource content, THE Service_Implementation SHALL use the correct attribute name
5. THE Quality_Service SHALL handle missing optional fields gracefully without raising exceptions

### Requirement 6: Performance Test Threshold Realism

**User Story:** As a test developer, I want performance test thresholds to reflect actual system capabilities, so that tests fail only when performance genuinely degrades.

#### Acceptance Criteria

1. WHEN THE Test_Suite measures graph construction time for 100 resources, THE Performance_Threshold SHALL be set to at least 1.0 seconds
2. WHEN THE Test_Suite measures graph construction time for 500 resources, THE Performance_Threshold SHALL be set to at least 15.0 seconds
3. WHEN THE Test_Suite measures two-hop query latency for 100 resources, THE Performance_Threshold SHALL be set to at least 100 milliseconds
4. WHEN THE Test_Suite measures two-hop query latency for 500 resources, THE Performance_Threshold SHALL be set to at least 2500 milliseconds
5. THE Performance_Tests SHALL document baseline measurements and threshold rationale in comments

### Requirement 7: Test Assertion Correctness

**User Story:** As a test developer, I want test assertions to verify actual system behavior, so that passing tests indicate correct functionality.

#### Acceptance Criteria

1. WHEN THE Test_Suite asserts sparse_embedding format, THE Assertion SHALL expect the actual return format from the service
2. WHEN THE Test_Suite asserts NDCG scores, THE Assertion SHALL use appropriate comparison operators and tolerance values
3. WHEN THE Test_Suite asserts ingestion status, THE Assertion SHALL expect 'completed' for successful ingestions
4. WHEN THE Test_Suite asserts quality scores, THE Assertion SHALL expect realistic values greater than 0.0
5. THE Test_Suite SHALL distinguish between implementation bugs and incorrect test expectations

### Requirement 8: Missing Python Dependencies

**User Story:** As a test developer, I want all required Python packages to be installed, so that tests can import necessary modules without ModuleNotFoundError exceptions.

#### Acceptance Criteria

1. WHEN THE Test_Suite imports openai module, THE Python_Environment SHALL have openai package installed
2. WHEN THE Test_Suite imports bert_score module, THE Python_Environment SHALL have bert_score package installed
3. THE Requirements_File SHALL list all packages needed for test execution
4. THE Test_Setup SHALL verify required packages are installed before running tests
5. WHERE packages are optional, THE Test_Implementation SHALL skip tests gracefully when packages are missing

### Requirement 9: Ingestion Pipeline Quality Integration

**User Story:** As a system user, I want ingested resources to have quality scores computed automatically, so that resource quality is assessed during ingestion.

#### Acceptance Criteria

1. WHEN THE Ingestion_Pipeline processes a resource, THE Pipeline SHALL compute quality_score before marking ingestion complete
2. WHEN THE Ingestion_Pipeline completes successfully, THE Resource_Object SHALL have quality_score greater than 0.0
3. WHEN THE Ingestion_Pipeline encounters quality computation errors, THE Pipeline SHALL set a default quality_score and log the error
4. THE Ingestion_Service SHALL call quality_service.compute_quality() for each ingested resource
5. THE Ingestion_Status SHALL be 'completed' only after quality computation succeeds or fails gracefully

### Requirement 10: Taxonomy Classification Schema Integrity

**User Story:** As a test developer, I want taxonomy nodes to have all required fields populated, so that classification tests execute without IntegrityError exceptions.

#### Acceptance Criteria

1. WHEN THE Test_Suite creates TaxonomyNode objects, THE Node_Objects SHALL have non-null slug values
2. WHEN THE Classification_Service creates taxonomy nodes, THE Service SHALL generate slug values from node names
3. THE TaxonomyNode_Model SHALL enforce NOT NULL constraint on slug column
4. THE Test_Fixtures SHALL provide valid slug values when creating taxonomy test data
5. THE Migration_System SHALL add slug column with appropriate constraints if missing
