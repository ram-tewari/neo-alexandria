# Implementation Plan: Test Suite Fixes - Phase 2

## Overview

This implementation plan addresses 242 failed tests and 175 error tests to achieve >90% pass rate. Tasks are organized by priority and grouped by failure type for efficient batch fixes.

---

## Phase 2.1: Critical Fixes (Week 1) - Target: 85% Pass Rate

### Task 1: Analyze Test Failures

- [ ] 1.1 Run full test suite and capture all failure messages
  - Command: `pytest --tb=short -v > test_failures.txt 2>&1`
  - Categorize failures by type: Assertion, Mock, Fixture, Type, Logic
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 1.2 Identify QualityScore-related failures
  - Search for: `'QualityScore' object has no attribute`, `assert.*quality_score`
  - Count affected tests by category: API, Services, Unit, Integration
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 1.3 Create failure pattern matrix
  - Document: Failure type, Count, Example test, Fix approach
  - Prioritize by: Impact (Critical/High/Medium/Low), Effort (Small/Medium/Large)
  - _Requirements: 7.1, 7.3, 7.4, 7.5_

### Task 2: Fix QualityScore API Integration

- [ ] 2.1 Update ResourceService quality score handling
  - File: `backend/app/services/resource_service.py`
  - Ensure quality_score is serialized to dict when stored in database
  - Ensure quality_score is deserialized to QualityScore when retrieved
  - _Requirements: 1.6, 1.7_

- [ ] 2.2 Update API response serialization
  - Files: `backend/app/routers/*.py`
  - Ensure QualityScore objects are serialized via .to_dict() in responses
  - Update Pydantic schemas to accept QualityScore objects
  - _Requirements: 1.5, 6.1_

- [ ] 2.3 Fix test_update_resource_partial
  - File: `backend/tests/api/test_phase2_curation_api.py`
  - Update assertion: `assert data["quality_score"]["overall_score"] == expected`
  - Or update test to use actual computed quality score
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 2.4 Fix remaining API quality score tests
  - Search: `grep -r "quality_score.*==" tests/api/`
  - Update all assertions to use domain object format
  - Verify API responses include overall_score field
  - _Requirements: 2.1, 2.2, 6.1_

### Task 3: Fix QualityScore Service Integration

- [ ] 3.1 Update QualityService return types
  - File: `backend/app/services/quality_service.py`
  - Ensure all methods return QualityScore domain objects
  - Update type hints: `-> QualityScore` not `-> Dict`
  - _Requirements: 1.1, 1.2_

- [ ] 3.2 Update service tests for QualityScore
  - Files: `backend/tests/services/test_*quality*.py`
  - Update assertions to use: `result.overall_score()` or `result['overall_score']`
  - Update mocks to return QualityScore objects
  - _Requirements: 2.1, 2.2, 4.1_

- [ ] 3.3 Fix quality dimension access patterns
  - Search: `grep -r "quality\['accuracy'\]" tests/`
  - Update to: `quality.accuracy` or `quality['accuracy']` (both work now)
  - Ensure .get() method is used where defaults are needed
  - _Requirements: 1.2, 1.3, 1.4_

### Task 4: Update Critical Fixtures

- [ ] 4.1 Create QualityScore fixture factory
  - File: `backend/tests/conftest.py`
  - Add: `@pytest.fixture def quality_score_factory()` that returns QualityScore objects
  - Provide defaults for all dimensions
  - _Requirements: 3.1, 3.2, 5.1_

- [ ] 4.2 Update existing quality fixtures
  - Search: `grep -r "@pytest.fixture.*quality" tests/`
  - Update fixtures to use QualityScore.from_dict() or factory
  - Ensure fixtures return domain objects not dicts
  - _Requirements: 3.1, 3.2, 3.5_

- [ ] 4.3 Create domain object fixture utilities
  - File: `backend/tests/conftest.py`
  - Add factories for: ClassificationResult, SearchResult, Recommendation
  - Provide sensible defaults for testing
  - _Requirements: 3.2, 3.3, 3.4_

### Task 5: Run Critical Test Suite

- [ ] 5.1 Run API tests
  - Command: `pytest tests/api/ -v`
  - Target: >90% passing
  - Document remaining failures
  - _Requirements: 15.6_

- [ ] 5.2 Run service tests
  - Command: `pytest tests/services/ -v`
  - Target: >85% passing
  - Document remaining failures
  - _Requirements: 15.6_

- [ ] 5.3 Run integration tests
  - Command: `pytest tests/integration/ -v`
  - Target: >80% passing
  - Document remaining failures
  - _Requirements: 15.6_

---

## Phase 2.2: High Priority Fixes (Week 2) - Target: 88% Pass Rate

### Task 6: Fix Assertion Mismatches

- [ ] 6.1 Identify assertion mismatch patterns
  - Search test output for: `assert.*==.*AssertionError`
  - Group by: Expected vs Actual value patterns
  - Determine if test or code needs fixing
  - _Requirements: 2.3, 2.4_

- [ ] 6.2 Fix quality score computation assertions
  - Files: Tests expecting specific quality values
  - Option A: Update expected values to match actual computation
  - Option B: Fix quality computation if logic is wrong
  - _Requirements: 2.3, 6.1_

- [ ] 6.3 Fix classification confidence assertions
  - Files: Tests expecting specific confidence scores
  - Update to use confidence ranges or mock ML model
  - Ensure tests don't depend on exact ML output
  - _Requirements: 2.4, 6.2_

- [ ] 6.4 Fix search result assertions
  - Files: Tests expecting specific search rankings
  - Update to check result presence not exact order
  - Use relevance thresholds not exact scores
  - _Requirements: 2.4, 6.3_

### Task 7: Update Mock Objects

- [ ] 7.1 Create domain object mock utilities
  - File: `backend/tests/conftest.py`
  - Add: `create_mock_quality_score()`, `create_mock_classification_result()`
  - Ensure mocks have all required methods and attributes
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 7.2 Update QualityService mocks
  - Search: `grep -r "mock.*QualityService" tests/`
  - Update return values to use QualityScore domain objects
  - Ensure mocks support both .get() and attribute access
  - _Requirements: 4.1, 4.5_

- [ ] 7.3 Update MLClassificationService mocks
  - Search: `grep -r "mock.*MLClassificationService" tests/`
  - Update return values to use ClassificationResult domain objects
  - Ensure mocks include predictions array with confidence
  - _Requirements: 4.2, 4.5_

- [ ] 7.4 Update SearchService mocks
  - Search: `grep -r "mock.*SearchService" tests/`
  - Update return values to use SearchResult domain objects
  - Ensure mocks include results array and pagination
  - _Requirements: 4.3, 4.5_

- [ ] 7.5 Update RecommendationService mocks
  - Search: `grep -r "mock.*RecommendationService" tests/`
  - Update return values to use Recommendation domain objects
  - Ensure mocks include score and explanation
  - _Requirements: 4.4, 4.5_

### Task 8: Fix Integration Test Failures

- [ ] 8.1 Update integration test fixtures
  - Files: `backend/tests/integration/*/conftest.py`
  - Ensure fixtures create domain objects
  - Update shared fixtures in main conftest.py
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 8.2 Fix workflow integration tests
  - Files: `backend/tests/integration/workflows/*.py`
  - Update to handle domain objects in workflows
  - Ensure end-to-end flows work with new types
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 8.3 Fix phase-specific integration tests
  - Files: `backend/tests/integration/phase*/*.py`
  - Update assertions for domain objects
  - Fix any phase-specific mock issues
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

### Task 9: Run High Priority Test Suite

- [ ] 9.1 Run all tests except known broken
  - Command: `pytest --ignore=tests/unit/phase8_classification/test_active_learning.py -v`
  - Target: >88% passing
  - Document remaining failures by category
  - _Requirements: 15.1, 15.2_

- [ ] 9.2 Verify critical paths passing
  - Run: API tests, Integration tests, Service tests
  - Ensure: Resource CRUD, Search, Quality, Classification all work
  - _Requirements: 15.6_

---

## Phase 2.3: Medium Priority Fixes (Week 3) - Target: 90% Pass Rate

### Task 10: Fix Remaining Fixture Issues

- [ ] 10.1 Audit all fixtures for domain objects
  - Command: `grep -r "@pytest.fixture" tests/ | grep -v conftest`
  - Identify fixtures returning dicts that should return domain objects
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 10.2 Refactor duplicate fixtures
  - Identify fixtures defined in multiple files
  - Move shared fixtures to conftest.py
  - Ensure test isolation is maintained
  - _Requirements: 3.5, 8.3_

- [ ] 10.3 Create fixture documentation
  - File: `backend/tests/FIXTURES.md`
  - Document all shared fixtures: Purpose, Parameters, Returns
  - Provide usage examples
  - _Requirements: 12.1, 12.2, 12.5_

### Task 11: Resolve Type Errors

- [ ] 11.1 Fix AttributeError on domain objects
  - Search test output for: `AttributeError.*QualityScore`
  - Add missing methods or update access patterns
  - Ensure all expected attributes exist
  - _Requirements: 9.1, 10.1_

- [ ] 11.2 Fix TypeError on domain objects
  - Search test output for: `TypeError.*QualityScore`
  - Fix type conversions (dict → domain object)
  - Update serialization/deserialization
  - _Requirements: 9.2, 10.2_

- [ ] 11.3 Fix KeyError on domain objects
  - Search test output for: `KeyError.*quality`
  - Use .get() method or attribute access
  - Ensure __getitem__ is implemented
  - _Requirements: 9.3, 10.3_

### Task 12: Update Unit Tests

- [ ] 12.1 Fix unit tests for domain objects
  - Files: `backend/tests/unit/*/test_*.py`
  - Update to test domain object methods
  - Ensure validation logic is tested
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 12.2 Fix unit tests for services
  - Files: `backend/tests/unit/*/test_*_service.py`
  - Update mocks to return domain objects
  - Test service methods with domain objects
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 12.3 Add domain object unit tests
  - Files: `backend/tests/domain/test_*.py`
  - Ensure all domain objects have comprehensive tests
  - Test validation, serialization, methods
  - _Requirements: 10.1, 10.2, 10.3_

### Task 13: Run Medium Priority Test Suite

- [ ] 13.1 Run unit tests
  - Command: `pytest tests/unit/ -v`
  - Target: >90% passing
  - Document remaining failures
  - _Requirements: 15.1, 15.2_

- [ ] 13.2 Run domain tests
  - Command: `pytest tests/domain/ -v`
  - Target: 100% passing
  - Fix any domain object issues
  - _Requirements: 15.6_

- [ ] 13.3 Measure overall pass rate
  - Command: `pytest --tb=no -q`
  - Target: >90% passing
  - _Requirements: 15.1_

---

## Phase 2.4: Cleanup and Optimization (Week 4) - Target: >90% Pass Rate

### Task 14: Fix SQLAlchemy UUID Issues

- [ ] 14.1 Fix test_active_learning.py UUID issue
  - File: `backend/tests/unit/phase8_classification/test_active_learning.py`
  - Use proper UUID type conversion in test data
  - Ensure SQLAlchemy UUID column type is correct
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 14.2 Audit UUID usage in tests
  - Search: `grep -r "uuid" tests/ | grep -i "string"`
  - Ensure UUIDs are proper UUID objects not strings
  - Fix any string → UUID conversions
  - _Requirements: 5.1, 5.2_

- [ ] 14.3 Update UUID fixtures
  - Ensure fixtures create proper UUID objects
  - Use: `uuid.uuid4()` not `str(uuid.uuid4())`
  - _Requirements: 5.1, 5.5_

### Task 15: Optimize Test Performance

- [ ] 15.1 Identify slow tests
  - Command: `pytest --durations=20`
  - Document tests taking >5 seconds
  - Categorize by: ML model loading, Database operations, Network calls
  - _Requirements: 11.1, 11.2, 11.5_

- [ ] 15.2 Cache ML model loading
  - Files: Tests loading BAAI/bge-m3, classification models
  - Use module-level fixtures to load once
  - Or mock ML models in unit tests
  - _Requirements: 11.1_

- [ ] 15.3 Optimize database fixtures
  - Use minimal data in fixtures
  - Batch insert operations where possible
  - Use in-memory SQLite for unit tests
  - _Requirements: 11.2_

- [ ] 15.4 Enable parallel test execution
  - Install: `pip install pytest-xdist`
  - Run: `pytest -n auto`
  - Fix any test isolation issues
  - _Requirements: 11.3, 11.4_

### Task 16: Update Test Documentation

- [ ] 16.1 Update tests/README.md
  - Document domain object usage in tests
  - Provide fixture examples
  - Explain mock patterns
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 16.2 Add docstrings to complex tests
  - Identify tests >50 lines without docstrings
  - Add docstrings explaining: Purpose, Setup, Assertions
  - _Requirements: 12.1, 12.3_

- [ ] 16.3 Create test pattern guide
  - File: `backend/tests/PATTERNS.md`
  - Document: Domain object testing, Mocking, Fixtures, Assertions
  - Provide code examples
  - _Requirements: 12.5, 10.5_

### Task 17: Update CI Configuration

- [ ] 17.1 Update CI requirements
  - Ensure CI installs: tensorboard, optuna
  - Update requirements.txt is used
  - _Requirements: 13.1_

- [ ] 17.2 Update CI test command
  - Exclude: `tests/unit/phase8_classification/test_active_learning.py`
  - Add: `--tb=short -v` for better error reporting
  - _Requirements: 13.2_

- [ ] 17.3 Add CI test metrics
  - Report: Pass rate, Failed count, Error count
  - Track: Pass rate trend over time
  - Alert: If pass rate drops below threshold
  - _Requirements: 13.3, 13.4, 14.1, 14.2_

- [ ] 17.4 Update CI coverage reporting
  - Generate: HTML coverage reports
  - Upload: To coverage service (Codecov, Coveralls)
  - _Requirements: 13.5_

### Task 18: Final Validation

- [ ] 18.1 Run full test suite
  - Command: `pytest --ignore=tests/unit/phase8_classification/test_active_learning.py`
  - Verify: >90% pass rate
  - Document: All remaining failures
  - _Requirements: 15.1, 15.2, 15.3_

- [ ] 18.2 Measure test execution time
  - Record: Total execution time
  - Verify: <15 minutes
  - Identify: Any remaining slow tests
  - _Requirements: 15.4_

- [ ] 18.3 Verify critical paths
  - Run: API, Integration, Service tests
  - Ensure: All critical functionality tested
  - _Requirements: 15.6_

- [ ] 18.4 Generate test metrics report
  - Document: Pass rate improvement, Tests fixed, Categories completed
  - Compare: Baseline vs Final metrics
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

### Task 19: Create Test Health Dashboard

- [ ] 19.1 Create test metrics script
  - File: `backend/scripts/test_metrics.py`
  - Collect: Pass rate, Failed count, Error count, Execution time
  - Output: JSON and Markdown reports
  - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [ ] 19.2 Set up weekly reporting
  - Schedule: Run test metrics weekly
  - Distribute: Email or Slack report
  - Track: Trends over time
  - _Requirements: 14.5_

---

## Success Criteria Checklist

- [ ] Pass rate >90% (currently 74.8%)
- [ ] Failed tests <100 (currently 242)
- [ ] Error tests <20 (currently 175)
- [ ] Test execution time <15 minutes (currently 28 minutes)
- [ ] Zero import errors (currently 1)
- [ ] All critical API tests passing
- [ ] All critical integration tests passing
- [ ] Comprehensive test documentation
- [ ] Updated CI configuration
- [ ] Test metrics tracking in place

---

## Estimated Timeline

**Week 1 (Phase 2.1):** Tasks 1-5 - Critical Fixes  
**Week 2 (Phase 2.2):** Tasks 6-9 - High Priority Fixes  
**Week 3 (Phase 2.3):** Tasks 10-13 - Medium Priority Fixes  
**Week 4 (Phase 2.4):** Tasks 14-19 - Cleanup and Optimization  

**Total Duration:** 4 weeks  
**Expected Outcome:** >90% pass rate, <15 min execution time
