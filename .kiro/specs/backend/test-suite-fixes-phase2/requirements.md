# Requirements Document: Test Suite Fixes - Phase 2

## Introduction

Phase 2 addresses the remaining test failures and errors in the Neo Alexandria test suite. After Phase 1 fixed import errors and increased test coverage from 73.3% to 74.8%, Phase 2 focuses on fixing the 242 failed tests and 175 error tests to achieve >90% pass rate.

## Current State

**Test Results (Post-Phase 1):**
- Total Tests: 1,750
- Passing: 1,309 (74.8%)
- Failing: 242 (13.8%)
- Errors: 175 (10.0%)
- Skipped: 24 (1.4%)

**Primary Issues:**
1. QualityScore domain object integration incomplete
2. Test assertions outdated after Phase 12 refactoring
3. Mock/fixture incompatibilities with domain objects
4. SQLAlchemy UUID type mismatches
5. API response format changes not reflected in tests

## Glossary

- **Domain Object**: Rich objects that encapsulate business logic and validation (Phase 12 refactoring)
- **Value Object**: Immutable domain object defined by its attributes (e.g., QualityScore, Confidence)
- **Test Fixture**: Reusable test data and setup code
- **Mock**: Simulated object used in testing to replace real dependencies
- **Assertion**: Test condition that must be true for test to pass
- **Test Isolation**: Tests that don't depend on other tests or external state

## Requirements

### Requirement 1: QualityScore Domain Object Integration

**User Story:** As a developer, I want QualityScore domain objects to work seamlessly with existing code, so that quality-related tests pass without modification.

#### Acceptance Criteria

1. WHEN QualityService returns a QualityScore object, THE System SHALL support both domain object methods and dict-like access
2. WHEN code accesses quality_score['dimension'], THE System SHALL return the dimension value via __getitem__
3. WHEN code calls quality_score.get('dimension'), THE System SHALL return the dimension value or default
4. WHEN code accesses quality_score.dimension, THE System SHALL return the dimension value directly
5. WHEN QualityScore is serialized to JSON, THE System SHALL include all dimensions and overall_score
6. WHEN QualityScore is stored in database, THE System SHALL serialize to dict format
7. WHEN QualityScore is retrieved from database, THE System SHALL deserialize from dict format
8. WHEN tests expect dict format, THE System SHALL provide .to_dict() method that returns complete dict

### Requirement 2: Test Assertion Updates

**User Story:** As a developer, I want test assertions to match current system behavior, so that tests accurately validate functionality.

#### Acceptance Criteria

1. WHEN a test asserts quality_score value, THE Test SHALL use quality_score.overall_score() or quality_score['overall_score']
2. WHEN a test asserts dimension values, THE Test SHALL access dimensions via domain object interface
3. WHEN a test expects specific quality values, THE Test SHALL account for actual quality computation logic
4. WHEN a test validates API responses, THE Test SHALL expect domain object serialization format
5. WHEN a test mocks quality scores, THE Test SHALL create QualityScore domain objects not dicts

### Requirement 3: Fixture Compatibility

**User Story:** As a developer, I want test fixtures to create domain objects, so that tests use the same types as production code.

#### Acceptance Criteria

1. WHEN a fixture creates quality data, THE Fixture SHALL return QualityScore domain objects
2. WHEN a fixture creates classification data, THE Fixture SHALL return ClassificationResult domain objects
3. WHEN a fixture creates search data, THE Fixture SHALL return SearchResult domain objects
4. WHEN a fixture creates recommendation data, THE Fixture SHALL return Recommendation domain objects
5. WHEN fixtures are shared across tests, THE Fixtures SHALL maintain test isolation

### Requirement 4: Mock Object Updates

**User Story:** As a developer, I want mocks to return domain objects, so that tests accurately simulate production behavior.

#### Acceptance Criteria

1. WHEN a test mocks QualityService.compute_quality(), THE Mock SHALL return QualityScore domain object
2. WHEN a test mocks MLClassificationService.predict(), THE Mock SHALL return ClassificationResult domain object
3. WHEN a test mocks SearchService.search(), THE Mock SHALL return SearchResult domain object
4. WHEN a test mocks RecommendationService.get_recommendations(), THE Mock SHALL return list of Recommendation objects
5. WHEN mocks are used in integration tests, THE Mocks SHALL maintain domain object interfaces

### Requirement 5: SQLAlchemy UUID Compatibility

**User Story:** As a developer, I want UUID fields to work correctly with SQLAlchemy, so that database tests pass without type errors.

#### Acceptance Criteria

1. WHEN a test creates resources with UUIDs, THE System SHALL use proper UUID type conversion
2. WHEN SQLAlchemy inserts UUID values, THE System SHALL match sentinel values correctly
3. WHEN tests use in-memory SQLite, THE System SHALL handle UUID serialization properly
4. WHEN batch inserts occur, THE System SHALL maintain UUID type consistency
5. WHEN UUID fields are queried, THE System SHALL return proper UUID objects not strings

### Requirement 6: API Response Format Validation

**User Story:** As a developer, I want API tests to validate current response formats, so that API contract changes are detected.

#### Acceptance Criteria

1. WHEN an API returns quality scores, THE Response SHALL include domain object serialization with overall_score
2. WHEN an API returns classifications, THE Response SHALL include predictions array with confidence scores
3. WHEN an API returns search results, THE Response SHALL include results array and pagination metadata
4. WHEN an API returns recommendations, THE Response SHALL include score and explanation fields
5. WHEN API responses change format, THE Tests SHALL fail to alert developers

### Requirement 7: Test Categorization and Prioritization

**User Story:** As a developer, I want to fix high-priority tests first, so that critical functionality is validated quickly.

#### Acceptance Criteria

1. THE System SHALL categorize failed tests by: Critical (API/Integration), High (Services), Medium (Unit), Low (Edge cases)
2. THE System SHALL identify tests that block other tests from running
3. THE System SHALL group tests by failure type: Assertion, Mock, Fixture, Type, Logic
4. THE System SHALL provide fix priority ranking based on impact and dependencies
5. THE System SHALL track fix progress with metrics: tests fixed, pass rate improvement, categories completed

### Requirement 8: Batch Test Fixes

**User Story:** As a developer, I want to fix similar test failures in batches, so that fixes are efficient and consistent.

#### Acceptance Criteria

1. WHEN multiple tests fail with same assertion error, THE Fix SHALL update all tests in one batch
2. WHEN multiple tests use same fixture, THE Fix SHALL update fixture once to fix all dependent tests
3. WHEN multiple tests mock same service, THE Fix SHALL update mock pattern once for all tests
4. WHEN tests share common setup, THE Fix SHALL refactor shared code into conftest.py
5. WHEN batch fixes are applied, THE System SHALL verify all affected tests pass

### Requirement 9: Test Error Resolution

**User Story:** As a developer, I want test errors resolved systematically, so that all 175 error tests become runnable.

#### Acceptance Criteria

1. WHEN a test has AttributeError on domain object, THE Fix SHALL add missing method or update access pattern
2. WHEN a test has TypeError on domain object, THE Fix SHALL correct type conversion or serialization
3. WHEN a test has KeyError on domain object, THE Fix SHALL use proper attribute access or add __getitem__ support
4. WHEN a test has ImportError, THE Fix SHALL correct import path or add missing dependency
5. WHEN a test has fixture error, THE Fix SHALL update fixture to match current code structure

### Requirement 10: Regression Prevention

**User Story:** As a developer, I want fixes to prevent future regressions, so that tests remain stable after refactoring.

#### Acceptance Criteria

1. WHEN domain objects are used in tests, THE Tests SHALL use domain object interfaces not dict access
2. WHEN fixtures create test data, THE Fixtures SHALL use factory functions that create proper domain objects
3. WHEN mocks are created, THE Mocks SHALL return domain objects with all required methods
4. WHEN assertions check values, THE Assertions SHALL use domain object methods not dict keys
5. WHEN new domain objects are added, THE System SHALL provide test utilities for creating them

### Requirement 11: Test Performance Optimization

**User Story:** As a developer, I want tests to run faster, so that test suite execution time is reduced.

#### Acceptance Criteria

1. WHEN tests load ML models, THE Tests SHALL use cached models or mocks to avoid repeated loading
2. WHEN tests create database records, THE Tests SHALL use minimal required data
3. WHEN tests run in parallel, THE Tests SHALL maintain isolation without conflicts
4. WHEN test suite runs, THE Execution SHALL complete in <15 minutes (currently 28 minutes)
5. WHEN slow tests are identified, THE System SHALL provide optimization recommendations

### Requirement 12: Test Documentation

**User Story:** As a developer, I want clear test documentation, so that test purpose and expected behavior are understood.

#### Acceptance Criteria

1. WHEN a test is complex, THE Test SHALL include docstring explaining purpose and setup
2. WHEN a test uses domain objects, THE Test SHALL document expected object structure
3. WHEN a test has specific requirements, THE Test SHALL document prerequisites in comments
4. WHEN tests are organized, THE Test files SHALL include module-level docstrings
5. WHEN test patterns are established, THE Documentation SHALL provide examples in tests/README.md

### Requirement 13: Continuous Integration Updates

**User Story:** As a developer, I want CI to run updated tests, so that test failures are caught before merge.

#### Acceptance Criteria

1. WHEN CI runs tests, THE CI SHALL use updated requirements.txt with tensorboard and optuna
2. WHEN CI runs tests, THE CI SHALL exclude known broken tests (test_active_learning.py)
3. WHEN CI runs tests, THE CI SHALL report pass rate and failure categories
4. WHEN tests fail in CI, THE CI SHALL provide clear error messages and logs
5. WHEN CI completes, THE CI SHALL update test coverage reports

### Requirement 14: Test Metrics and Reporting

**User Story:** As a developer, I want test metrics tracked, so that progress and quality are measurable.

#### Acceptance Criteria

1. THE System SHALL track pass rate over time: baseline (74.8%) → target (>90%)
2. THE System SHALL track tests fixed per category: API, Services, Unit, Integration
3. THE System SHALL track error types resolved: Assertion, Mock, Fixture, Type
4. THE System SHALL track test execution time: baseline (28 min) → target (<15 min)
5. THE System SHALL generate weekly test health reports

### Requirement 15: Success Criteria

**User Story:** As a project manager, I want clear success criteria, so that Phase 2 completion is measurable.

#### Acceptance Criteria

1. THE System SHALL achieve >90% test pass rate (currently 74.8%)
2. THE System SHALL reduce failed tests to <100 (currently 242)
3. THE System SHALL reduce error tests to <20 (currently 175)
4. THE System SHALL reduce test execution time to <15 minutes (currently 28 minutes)
5. THE System SHALL have zero import errors (currently 1)
6. THE System SHALL have all critical API and integration tests passing
7. THE System SHALL have comprehensive test documentation
8. THE System SHALL have updated CI configuration

## Test Failure Categories

### Category 1: QualityScore Integration (Estimated: 80 tests)
**Pattern:** Tests expect dict but receive QualityScore domain object
**Fix:** Update assertions to use domain object interface
**Priority:** Critical

### Category 2: Assertion Mismatches (Estimated: 60 tests)
**Pattern:** Expected values don't match actual computed values
**Fix:** Update expected values or fix computation logic
**Priority:** High

### Category 3: Mock Incompatibilities (Estimated: 40 tests)
**Pattern:** Mocks return dicts but code expects domain objects
**Fix:** Update mocks to return domain objects
**Priority:** High

### Category 4: Fixture Issues (Estimated: 30 tests)
**Pattern:** Fixtures create dicts but tests need domain objects
**Fix:** Update fixtures to create domain objects
**Priority:** Medium

### Category 5: Type Errors (Estimated: 20 tests)
**Pattern:** Type mismatches between domain objects and primitives
**Fix:** Add type conversions or update type hints
**Priority:** Medium

### Category 6: SQLAlchemy UUID (Estimated: 12 tests)
**Pattern:** UUID type mismatches in database operations
**Fix:** Use proper UUID type handling
**Priority:** Low

## Implementation Strategy

### Phase 2.1: Critical Fixes (Week 1)
- Fix QualityScore integration in API tests
- Fix QualityScore integration in service tests
- Update critical fixtures
- Target: 85% pass rate

### Phase 2.2: High Priority Fixes (Week 2)
- Fix assertion mismatches
- Update mock objects
- Fix integration test failures
- Target: 88% pass rate

### Phase 2.3: Medium Priority Fixes (Week 3)
- Fix remaining fixture issues
- Resolve type errors
- Update unit tests
- Target: 90% pass rate

### Phase 2.4: Cleanup and Optimization (Week 4)
- Fix SQLAlchemy UUID issues
- Optimize test performance
- Update documentation
- Update CI configuration
- Target: >90% pass rate, <15 min execution

## Success Metrics

**Baseline (Post-Phase 1):**
- Pass Rate: 74.8%
- Failed Tests: 242
- Error Tests: 175
- Execution Time: 28 minutes

**Target (Post-Phase 2):**
- Pass Rate: >90%
- Failed Tests: <100
- Error Tests: <20
- Execution Time: <15 minutes

**Stretch Goals:**
- Pass Rate: >95%
- Failed Tests: <50
- Error Tests: <10
- Execution Time: <10 minutes
