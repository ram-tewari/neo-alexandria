# Requirements Document

## Introduction

The Neo Alexandria 2.0 application has 1,867 tests with 386 failures (20.7%) and 102 errors (5.5%) after fixing import path issues. This spec addresses the systematic resolution of all genuine coding errors to ensure the website functions perfectly. The failures span across database models, service APIs, event systems, monitoring infrastructure, and ML classification features.

## Glossary

- **Test_Suite**: The collection of 1,867 pytest tests covering all application features
- **Resource_Model**: SQLAlchemy model representing scholarly resources with Dublin Core metadata fields
- **Service_Layer**: Business logic layer containing services like CollectionService, RecommendationService, QualityService
- **Event_Bus**: Event-driven architecture component for inter-module communication
- **Monitoring_System**: Prometheus-based metrics collection system
- **Database_Schema**: SQLAlchemy models and Alembic migrations defining the data structure
- **Test_Fixture**: Reusable test data and setup code in conftest.py files
- **Dublin_Core**: Metadata standard used for resource fields (type, source, identifier, etc.)
- **LBD_Service**: Literature-Based Discovery service for graph intelligence
- **Quality_Analyzer**: Service for analyzing content quality metrics

## Requirements

### Requirement 1: Database Model Field Alignment

**User Story:** As a developer, I want all test fixtures to use correct SQLAlchemy model field names, so that tests accurately reflect the production data model.

#### Acceptance Criteria

1. WHEN a test creates a Resource instance, THE Test_Suite SHALL use Dublin_Core field names (source, identifier, type) instead of legacy field names (url, resource_type)
2. WHEN a test creates a User instance, THE Test_Suite SHALL use the correct password field name as defined in the User_Model
3. WHEN test fixtures reference model fields, THE Test_Suite SHALL validate field names against current SQLAlchemy model definitions
4. THE Test_Suite SHALL update approximately 80 test files across phase8, phase9, and integration/workflows directories
5. WHERE a field mapping is ambiguous, THE Test_Suite SHALL document the correct Dublin_Core field mapping in test comments

### Requirement 2: Service Method Signature Consistency

**User Story:** As a developer, I want service method calls in tests to match actual service implementations, so that tests validate real API contracts.

#### Acceptance Criteria

1. WHEN tests call CollectionService.create_collection(), THE Service_Layer SHALL accept all required parameters including description
2. WHEN tests call CollectionService methods, THE Test_Suite SHALL use existing method names (not add_resources if it doesn't exist)
3. WHEN tests call recommendation_service methods, THE Test_Suite SHALL pass parameters matching current method signatures
4. THE Test_Suite SHALL update approximately 50 test files in phase7_collections and phase11_recommendations
5. WHERE service APIs have changed, THE Test_Suite SHALL update test calls to match current implementations

### Requirement 3: Database Migration and Table Creation

**User Story:** As a developer, I want all required database tables to exist before tests run, so that tests can execute without "no such table" errors.

#### Acceptance Criteria

1. WHEN the test suite initializes, THE Database_Schema SHALL create all required tables (resources, taxonomy_nodes, users, annotations, classification_codes)
2. WHEN tests run, THE Database_Schema SHALL execute Alembic migrations to ensure schema is current
3. WHEN conftest.py sets up test databases, THE Test_Fixture SHALL verify all migrations have been applied
4. THE Database_Schema SHALL include alembic_version table for migration tracking
5. THE Test_Suite SHALL fix approximately 100 tests across all phases that fail with table errors

### Requirement 4: Monitoring Metrics Initialization

**User Story:** As a developer, I want Prometheus metrics to be properly initialized in test environments, so that monitoring code doesn't cause AttributeError exceptions.

#### Acceptance Criteria

1. WHEN tests import monitoring modules, THE Monitoring_System SHALL initialize all Prometheus metric objects (Counter, Histogram, Gauge)
2. WHEN test code calls metric.inc() or metric.observe(), THE Monitoring_System SHALL provide valid metric objects (not None)
3. WHEN running in test mode, THE Monitoring_System SHALL provide test-safe metric implementations or mocks
4. THE Test_Suite SHALL fix approximately 40 tests in phase1_ingestion and workflows
5. WHERE metrics are not needed for test logic, THE Test_Suite SHALL mock metrics to prevent initialization issues

### Requirement 5: Event System API Modernization

**User Story:** As a developer, I want tests to use the current EventBus API, so that event system tests validate actual production behavior.

#### Acceptance Criteria

1. WHEN tests need to clear event state, THE Event_Bus SHALL provide clear_history() method instead of clear_listeners()
2. WHEN tests verify event handling, THE Event_Bus SHALL expose public API methods instead of private _subscribers attribute
3. WHEN Event objects are created, THE Event_Bus SHALL include correlation_id attribute if required by tests
4. THE Test_Suite SHALL update approximately 30 tests in test_event_system.py and test_event_hooks.py
5. WHERE EventBus API has changed, THE Test_Suite SHALL update all test code to use current public methods

### Requirement 6: Python Dependency Management

**User Story:** As a developer, I want all required Python packages to be installed or gracefully handled, so that tests don't fail with import errors.

#### Acceptance Criteria

1. WHEN tests import optional modules (trio, openai, plotly), THE Test_Suite SHALL skip tests gracefully if modules are unavailable
2. WHEN requirements.txt is processed, THE Test_Suite SHALL include all required dependencies for test execution
3. WHEN optional dependencies are missing, THE Test_Suite SHALL display clear skip messages explaining why tests were skipped
4. THE Test_Suite SHALL fix approximately 15 tests that fail with ImportError
5. WHERE dependencies are truly optional, THE Test_Suite SHALL use pytest.importorskip() to handle missing modules

### Requirement 7: Quality Service API Restoration

**User Story:** As a developer, I want quality analysis methods to be available and consistent, so that quality metrics tests pass successfully.

#### Acceptance Criteria

1. WHEN tests call ContentQualityAnalyzer.content_readability(), THE Quality_Analyzer SHALL provide this method or an equivalent
2. WHEN tests call ContentQualityAnalyzer.overall_quality_score(), THE Quality_Analyzer SHALL return quality scores in expected format
3. WHEN quality dimensions are calculated, THE Quality_Analyzer SHALL return consistent data structures
4. THE Test_Suite SHALL fix approximately 25 tests in phase9_quality
5. WHERE quality methods have been renamed, THE Test_Suite SHALL update test calls to use new method names

### Requirement 8: Classification Service Implementation Completion

**User Story:** As a developer, I want ML classification training and prediction methods to be fully implemented, so that classification tests validate real ML workflows.

#### Acceptance Criteria

1. WHEN tests call ClassificationTrainer.train(), THE Service_Layer SHALL provide this method with correct signature
2. WHEN semi-supervised learning is tested, THE Service_Layer SHALL return expected data types and structures
3. WHEN model checkpoints are loaded, THE Service_Layer SHALL use correct checkpoint directory paths
4. THE Test_Suite SHALL fix approximately 40 tests in phase8_classification
5. WHERE ClassificationTrainer methods are missing, THE Service_Layer SHALL implement required training methods

### Requirement 9: Recommendation Service Refactoring Alignment

**User Story:** As a developer, I want recommendation service tests to match the refactored implementation, so that recommendation features are properly validated.

#### Acceptance Criteria

1. WHEN tests call generate_user_profile_vector(), THE Service_Layer SHALL accept all required parameters including user_id
2. WHEN tests use utility methods, THE Service_Layer SHALL provide _compute_gini_coefficient() and apply_novelty_boost() or update tests
3. WHEN recommendation methods return results, THE Service_Layer SHALL return data types matching test expectations
4. THE Test_Suite SHALL fix approximately 20 tests in phase5_graph and phase11_recommendations
5. WHERE recommendation methods have been removed, THE Test_Suite SHALL update tests to use current API

### Requirement 10: Graph Intelligence Feature Completion

**User Story:** As a developer, I want graph construction and LBD discovery features to be fully implemented, so that advanced graph intelligence tests pass.

#### Acceptance Criteria

1. WHEN tests call LBDService.open_discovery(), THE LBD_Service SHALL provide this method for literature-based discovery
2. WHEN edge type filtering is applied, THE Service_Layer SHALL correctly filter graph edges by type
3. WHEN multi-layer graphs are constructed, THE Service_Layer SHALL build complete graph structures
4. THE Test_Suite SHALL fix approximately 15 tests in phase10_graph_intelligence
5. WHERE LBD methods are incomplete, THE Service_Layer SHALL implement missing discovery algorithms

### Requirement 11: Test Suite Success Metrics

**User Story:** As a project stakeholder, I want all tests to pass or be properly skipped, so that I can trust the test suite validates application quality.

#### Acceptance Criteria

1. WHEN the full test suite runs, THE Test_Suite SHALL achieve 100% pass rate for non-skipped tests
2. WHEN tests are skipped, THE Test_Suite SHALL provide clear reasons (missing optional dependencies, known limitations)
3. WHEN core features are tested, THE Test_Suite SHALL have zero failures in critical paths (database, models, core services)
4. THE Test_Suite SHALL reduce failures from 386 to 0 and errors from 102 to 0
5. WHERE tests validate end-to-end workflows, THE Test_Suite SHALL confirm website functions correctly in production scenarios
