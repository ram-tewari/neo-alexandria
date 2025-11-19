# Implementation Plan: Phase 12.6 Test Suite Fixes

- [x] 1. Analyze and categorize test failures





  - Run full test suite with detailed output and capture all failure messages
  - Parse test output to categorize failures by type (Assertion, Mock, Fixture, Type, Logic)
  - Identify QualityScore-related failures and count affected tests by category
  - Create failure pattern matrix documenting failure type, count, example test, and fix approach
  - Prioritize failures by impact (Critical/High/Medium/Low) and effort (Small/Medium/Large)
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

-

- [x] 2. Create domain object fixture factories



  - Create quality_score_factory fixture in backend/tests/conftest.py
  - Create classification_result_factory fixture with ClassificationPrediction support
  - Create search_result_factory fixture for SearchResult domain objects
  - Create recommendation_factory fixture for Recommendation domain objects
  - Ensure all factories provide sensible defaults for testing
  - _Requirements: 3.1, 3.2, 3.3, 3.4_



- [x] 3. Create mock utility functions



  - Implement create_quality_service_mock() utility in backend/tests/conftest.py
  - Implement create_classification_service_mock() utility
  - Implement create_search_service_mock() utility
  - Implement create_recommendation_service_mock() utility
  - Ensure all mocks return domain objects with required methods and attributes
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_






- [ ] 4. Create test assertion helper functions
  - Implement assert_quality_score() helper in backend/tests/conftest.py
  - Implement assert_classification_result() helper
  - Implement assert_search_result() helper



  - Implement assert_recommendation() helper
  - Support both domain object and dict formats for backward compatibility
  - _Requirements: 2.1, 2.2, 2.3, 2.4_


- [-] 5. Fix QualityScore API integration


  - Update ResourceService to serialize quality_score to dict before database storage
  - Update ResourceService to deserialize quality_score to QualityScore after retrieval
  - Update API routers to call QualityScore.to_dict() for response serialization
  - Update Pydantic schemas to accept QualityScore objects
  - Fix test_update_resource_partial in backend/tests/api/test_phase2_curation_api.py

  - _Requirements: 1.5, 1.6, 1.7, 6.1_

- [x] 6. Fix QualityScore service integration


  - Update QualityService methods to ensure they return QualityScore domain objects
  - Update type hints in backend/app/services/quality_service.py to use QualityScore
  - Update service tests to assert against QualityScore domain objects
  - Update mocks in service tests to return QualityScore objects
  - Fix quality dimension access patterns to use domain object interface
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2_


- [x] 7. Batch fix QualityScore assertion errors



  - Search for all tests asserting quality_score values using grep
  - Update assertions to use quality_score.overall_score() or quality_score['overall_score']
  - Update dimension access to use quality_score.accuracy or quality_score['accuracy']
  - Update expected values to match actual quality computation logic
  - Verify all updated tests pass
  - _Requirements: 2.1, 2.2, 2.3, 6.1_



- [x] 8. Update existing quality fixtures


  - Search for all fixtures creating quality data using grep
  - Update fixtures to return QualityScore domain objects using QualityScore.from_dict()
  - Update fixtures to use quality_score_factory where appropriate
  - Ensure fixtures maintain test isolation
  - Verify all tests using updated fixtures pass
  - _Requirements: 3.1, 3.2, 3.5_


- [x] 9. Fix classification service mocks



  - Search for all tests mocking MLClassificationService
  - Update mock return values to use ClassificationResult domain objects
  - Ensure mocks include predictions array with ClassificationPrediction objects
  - Update assertions to work with ClassificationResult domain objects
  - Verify all tests with updated mocks pass
  - _Requirements: 4.2, 4.5, 6.2_



- [x] 10. Fix search service mocks



  - Search for all tests mocking SearchService
  - Update mock return values to use SearchResult domain objects
  - Ensure mocks include results array and pagination metadata
  - Update assertions to work with SearchResult domain objects
  - Verify all tests with updated mocks pass
  - _Requirements: 4.3, 4.5, 6.3_

-


- [x] 11. Fix recommendation service mocks


  - Search for all tests mocking RecommendationService
  - Update mock return values to use Recommendation domain objects
  - Ensure mocks include score and explanation fields
  - Update assertions to work with Recommendation domain objects
  - Verify all tests with updated mocks pass
  - _Requirements: 4.4, 4.5, 6.4_

- [x] 12. Fix integration test fixtures





  - Update fixtures in backend/tests/integration/*/conftest.py to create domain objects
  - Update shared fixtures in main conftest.py
  - Ensure integration tests use domain objects throughout workflows
  - Fix workflow integration tests to handle domain objects
  - Fix phase-specific integration tests
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 6.1, 6.2, 6.3, 6.4_

-

- [x] 13. Fix assertion mismatch patterns



  - Identify tests with assertion mismatches from failure analysis
  - Update quality score computation assertions to use computed values or ranges
  - Update classification confidence assertions to use ranges or mock ML model
  - Update search result assertions to check presence not exact order
  - Verify all updated assertions pass
  - _Requirements: 2.3, 2.4, 6.1, 6.2, 6.3_

- [x] 14. Resolve AttributeError on domain objects








  - Search test output for AttributeError on QualityScore and other domain objects
  - Add missing methods to domain objects or update access patterns in tests
  - Ensure all expected attributes exist on domain objects
  - Verify all AttributeError tests now pass
  - _Requirements: 9.1, 10.1_



- [x] 15. Resolve TypeError on domain objects





  - Search test output for TypeError on domain objects
  - Fix type conversions from dict to domain object using from_dict()
  - Update serialization/deserialization in services and APIs
  - Verify all TypeError tests now pass

  - _Requirements: 9.2, 10.2_


- [x] 16. Resolve KeyError on domain objects

  - Search test output for KeyError on domain objects
  - Update code to use .get() method or attribute access
  - Ensure __getitem__ is properly implemented on domain objects

  - Verify all KeyError tests now pass
  - _Requirements: 9.3, 10.3_





- [ ] 17. Fix SQLAlchemy UUID type issues
  - Fix test_active_learning.py UUID issue in backend/tests/unit/phase8_classification/
  - Use proper UUID type conversion with uuid.uuid4() in test data
  - Audit UUID usage in tests and fix string to UUID conversions
  - Update UUID fixtures to create proper UUID objects



  - Verify all UUID-related tests pass

  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 18. Refactor duplicate fixtures








  - Identify fixtures defined in multiple test files
  - Move shared fixtures to appropriate conftest.py files
  - Ensure test isolation is maintained after refactoring
  - Remove duplicate fixture definitions
  - Verify all tests still pass after refactoring
  - _Requirements: 3.5, 8.3_

- [x] 19. Add comprehensive domain object unit tests


  - Create tests for QualityScore validation in backend/tests/domain/
  - Create tests for ClassificationResult validation
  - Create tests for SearchResult validation
  - Create tests for Recommendation validation
  - Test serialization (to_dict) and deserialization (from_dict) for all domain objects
  - _Requirements: 10.1, 10.2, 10.3_

- [x] 20. Optimize ML model loading in tests





  - Identify tests loading ML models (BAAI/bge-m3, classification models)
  - Create module-level fixtures to load models once per test module
  - Mock ML models in unit tests to avoid loading
  - Verify test execution time improves


  - _Requirements: 11.1_


- [x] 21. Optimize database fixtures





  - Update database fixtures to use minimal required data
  - Batch insert operations where possible in fixtures
  - Use in-memory SQLite for unit tests
  - Verify test execution time improves
  - _Requirements: 11.2_








- [x] 22. Enable parallel test execution





  - Install pytest-xdist package
  - Run tests with pytest -n auto to identify isolation issues
  - Fix any test isolation issues preventing parallel execution
  - Update CI configuration to use parallel execution
  - _Requirements: 11.3, 11.4_

- [ ]* 23. Create fixture documentation
  - Create backend/tests/FIXTURES.md documenting all shared fixtures
  - Document fixture purpose, parameters, and return types
  - Provide usage examples for each fixture
  - Document fixture scopes and when to use each
  - _Requirements: 12.1, 12.2, 12.5_

- [ ]* 24. Create test pattern guide
  - Create backend/tests/PATTERNS.md documenting common test patterns
  - Document domain object testing patterns with examples
  - Document mocking patterns for services
  - Document fixture usage patterns
  - Document assertion patterns for domain objects
  - _Requirements: 12.5, 10.5_

- [ ]* 25. Add docstrings to complex tests
  - Identify tests over 50 lines without docstrings
  - Add docstrings explaining purpose, setup, and assertions
  - Document any non-obvious test requirements
  - Ensure all complex tests are well-documented
  - _Requirements: 12.1, 12.3_

- [ ]* 26. Update tests/README.md
  - Document domain object usage in tests
  - Add section on fixture factories and mock utilities
  - Add section on test assertion helpers
  - Update running tests section with new commands
  - Add troubleshooting section for common issues
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 27. Update CI requirements
  - Ensure CI installs tensorboard and optuna dependencies
  - Verify requirements.txt includes all test dependencies
  - Update CI workflow to install pytest-xdist for parallel execution
  - _Requirements: 13.1_

- [ ] 28. Update CI test execution
  - Update CI to exclude test_active_learning.py if still broken
  - Add --tb=short -v flags for better error reporting
  - Configure parallel execution with -n auto
  - _Requirements: 13.2_

- [ ] 29. Add CI test metrics reporting
  - Update CI to report pass rate, failed count, and error count
  - Add step to track pass rate trend over time
  - Configure alerts if pass rate drops below 90% threshold
  - Generate and upload HTML coverage reports
  - _Requirements: 13.3, 13.4, 13.5, 14.1, 14.2_

- [ ] 30. Create test metrics collection script
  - Create backend/scripts/test_metrics.py to collect test metrics
  - Implement collection of pass rate, failed count, error count, execution time
  - Output metrics in JSON and Markdown formats
  - Support comparison against baseline metrics
  - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [ ]* 31. Set up weekly test reporting
  - Configure test metrics script to run weekly
  - Generate weekly test health reports in Markdown format
  - Set up distribution via email or Slack
  - Track trends over time in reports
  - _Requirements: 14.5_

- [ ] 32. Run final validation
  - Run full test suite excluding known broken tests
  - Verify pass rate is >90%
  - Verify failed tests <100
  - Verify error tests <20
  - Verify test execution time <15 minutes
  - Verify zero import errors
  - Verify all critical API and integration tests passing
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [ ] 33. Generate final test metrics report
  - Run test metrics script to generate final report
  - Document pass rate improvement from baseline (74.8%) to final
  - Document tests fixed by category
  - Document execution time improvement
  - Compare all metrics against success criteria
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
