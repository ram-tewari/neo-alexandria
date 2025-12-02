# Implementation Plan

## Phase 1: Foundation Fixes (P0 - Critical)

- [x] 1. Audit and document current model field names



  - Read all SQLAlchemy model files to document actual field names
  - Create field mapping reference for Resource, User, and other core models
  - Compare with test fixture usage to identify mismatches

  - _Requirements: 1.1, 1.3_


- [x] 1.1 Document Resource model fields
  - Read `backend/app/models.py` and `backend/app/modules/resources/model.py`
  - List all fields with their types and Dublin Core mappings

  - _Requirements: 1.1_

- [x] 1.2 Document User model fields
  - Read User model definition

  - Verify password field name (hashed_password vs password_hash)
  - _Requirements: 1.2_

- [x] 1.3 Create field mapping reference document


  - Write mapping of legacy field names to current field names
  - Add to design.md or create separate reference file
  - _Requirements: 1.5_

- [x] 2. Fix database migrations and table creation


  - Verify all Alembic migration scripts are complete
  - Update test database setup to run migrations
  - Add migration verification to conftest.py
  - _Requirements: 3.1, 3.2, 3.3, 3.4_


- [x] 2.1 Audit Alembic migration scripts

  - List all migration files in `backend/alembic/versions/`
  - Verify each creates required tables (resources, users, taxonomy_nodes, etc.)
  - Check for missing tables or incomplete migrations
  - _Requirements: 3.1, 3.2_

- [x] 2.2 Update test database initialization in conftest.py


  - Modify `backend/tests/conftest.py` database fixture
  - Add Alembic migration execution before tests run
  - Add table existence verification
  - _Requirements: 3.2, 3.3_


- [x] 2.3 Create database setup helper functions

  - Add functions to `backend/tests/db_utils.py` for migration management
  - Include table verification and cleanup utilities
  - _Requirements: 3.3_

- [ ]* 2.4 Test database migration workflow
  - Run `alembic upgrade head` in test environment
  - Verify all tables created successfully
  - Test migration rollback and re-upgrade
  - _Requirements: 3.2, 3.4_


- [x] 3. Fix monitoring metrics initialization


  - Create test-safe monitoring module
  - Add conditional initialization based on environment
  - Mock metrics in test fixtures

  - _Requirements: 4.1, 4.2, 4.3_

- [x] 3.1 Add conditional metrics initialization to monitoring.py

  - Modify `backend/app/monitoring.py`
  - Add environment check (TESTING env var)
  - Create NoOpMetric class for test environment
  - _Requirements: 4.1, 4.2_


- [x] 3.2 Add metrics mocking fixture to conftest.py

  - Add autouse fixture in `backend/tests/conftest.py`
  - Set TESTING=true environment variable
  - Reload monitoring module with test metrics
  - _Requirements: 4.3, 4.5_

- [x] 4. Update test fixtures with correct model field names





  - Fix Resource fixtures to use Dublin Core fields
  - Fix User fixtures to use correct password field
  - Update all conftest.py files with fixture corrections

  - _Requirements: 1.1, 1.2, 1.4_

- [x] 4.1 Fix Resource fixtures in root conftest.py

  - Update `backend/tests/conftest.py`
  - Change `url` to `source`, `resource_type` to `type`
  - Update all Resource creation calls
  - _Requirements: 1.1, 1.4_


- [x] 4.2 Fix Resource fixtures in integration conftest.py

  - Update `backend/tests/integration/conftest.py`
  - Apply same field name corrections
  - _Requirements: 1.1, 1.4_

- [x] 4.3 Fix Resource fixtures in phase-specific conftest files


  - Update `backend/tests/unit/phase7_collections/conftest.py`
  - Update `backend/tests/integration/workflows/conftest.py`
  - Update `backend/tests/integration/phase8_classification/conftest.py`
  - Update `backend/tests/integration/phase9_quality/conftest.py`
  - Update `backend/tests/integration/phase11_recommendations/conftest.py`
  - _Requirements: 1.1, 1.4_

- [x] 4.4 Fix User fixtures across all conftest files


  - Update password field name in all User fixture definitions
  - Verify field name matches actual User model
  - _Requirements: 1.2, 1.4_

- [x] 4.5 Fix direct Resource/User instantiation in test files


  - Search for `Resource(url=` and replace with `Resource(source=`
  - Search for `Resource(resource_type=` and replace with `Resource(type=`
  - Update approximately 80 test files
  - _Requirements: 1.1, 1.4_

- [x] 4.6 Verify fixture fixes with targeted tests















  - Run `pytest backend/tests/integration/workflows/ -v`
  - Run `pytest backend/tests/unit/phase8_classification/ -v`

  - Verify no "unexpected keyword argument" errors
  - _Requirements: 1.4_

## Phase 2: Core Service API Fixes (P0-P1)

- [x] 5. Fix CollectionService API



  - Update create_collection method signature
  - Verify add_resources method exists or update tests
  - Update service implementation and tests
  - _Requirements: 2.1, 2.2, 2.4_

- [x] 5.1 Audit CollectionService current API


  - Read `backend/app/services/collection_service.py`
  - Read `backend/app/modules/collections/service.py`
  - Document all method signatures
  - _Requirements: 2.1, 2.2_

- [x] 5.2 Update create_collection method


  - Add `description` parameter if missing
  - Ensure all required parameters are present
  - Update both legacy and modular service files
  - _Requirements: 2.1, 2.4_


- [x] 5.3 Verify or implement add_resources method

  - Check if method exists (may be named differently)
  - If missing, implement add_resources_to_collection method
  - Update method to accept collection_id and resource_ids
  - _Requirements: 2.2, 2.4_


- [x] 5.4 Update CollectionService test calls

  - Update tests in `backend/tests/unit/phase7_collections/`
  - Add description parameter to create_collection calls
  - Update add_resources method calls to match actual API
  - _Requirements: 2.4, 2.5_

- [ ]* 5.5 Verify CollectionService fixes
  - Run `pytest backend/tests/unit/phase7_collections/ -v`
  - Verify no missing parameter errors
  - _Requirements: 2.4_

- [x] 6. Modernize EventBus API





  - Add public API methods for test access
  - Add correlation_id to Event class
  - Update all tests to use new API
  - _Requirements: 5.1, 5.2, 5.3, 5.4_


- [x] 6.1 Add public API methods to EventBus

  - Update `backend/app/shared/event_bus.py` or `backend/app/events/event_system.py`
  - Add clear_history(), get_subscribers(), clear_subscribers() methods
  - Add get_history() method for test access
  - _Requirements: 5.1, 5.2_



- [x] 6.2 Add correlation_id to Event class

  - Update `backend/app/events/event_types.py`
  - Add correlation_id field with auto-generation
  - _Requirements: 5.3_


- [x] 6.3 Update EventBus tests to use public API

  - Update `backend/tests/unit/test_event_system.py`
  - Replace clear_listeners() with clear_history() and clear_subscribers()
  - Replace _subscribers access with get_subscribers()
  - _Requirements: 5.4_


- [x] 6.4 Update event hook tests

  - Update `backend/tests/integration/test_event_hooks.py`
  - Apply same API changes as event_system tests
  - _Requirements: 5.4_

- [ ]* 6.5 Verify EventBus API fixes
  - Run `pytest backend/tests/unit/test_event_system.py -v`
  - Run `pytest backend/tests/integration/test_event_hooks.py -v`
  - Verify no AttributeError on EventBus methods
  - _Requirements: 5.4_
-

- [x] 7. Fix RecommendationService API



  - Update generate_user_profile_vector signature
  - Restore removed utility methods
  - Fix return type mismatches
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 7.1 Update generate_user_profile_vector signature


  - Modify `backend/app/services/recommendation_service.py`
  - Add user_id parameter to method signature
  - Update method implementation to use user_id
  - _Requirements: 9.1, 9.4_



- [ ] 7.2 Restore utility methods if removed
  - Check if _compute_gini_coefficient exists
  - Check if apply_novelty_boost exists


  - Restore methods or make them public if tests depend on them
  - _Requirements: 9.2, 9.4_



- [ ] 7.3 Fix recommendation return types
  - Ensure methods return List[RecommendationResult]
  - Update domain models in `backend/app/domain/recommendation.py`
  - _Requirements: 9.3_

- [ ] 7.4 Update recommendation tests
  - Update `backend/tests/unit/phase5_graph/` test calls
  - Update `backend/tests/integration/phase11_recommendations/` test calls
  - Add user_id parameter to generate_user_profile_vector calls
  - _Requirements: 9.4, 9.5_



- [ ]* 7.5 Verify RecommendationService fixes
  - Run `pytest backend/tests/unit/phase5_graph/ -v -k recommendation`
  - Run `pytest backend/tests/integration/phase11_recommendations/ -v`
  - Verify no missing parameter errors
  - _Requirements: 9.4_



## Phase 3: Advanced Feature Fixes (P2)

- [x] 8. Fix QualityService API



  - Restore content_readability method
  - Restore overall_quality_score method
  - Update test assertions for return structures

  - _Requirements: 7.1, 7.2, 7.3, 7.4_


- [ ] 8.1 Audit QualityService current implementation
  - Read `backend/app/services/quality_service.py`
  - Document existing methods and their signatures
  - Identify missing methods that tests expect


  - _Requirements: 7.1, 7.2_

- [ ] 8.2 Restore or implement content_readability method
  - Add content_readability method to ContentQualityAnalyzer
  - Implement Flesch reading ease and Gunning Fog calculations
  - Return ReadabilityScore structured object
  - _Requirements: 7.1, 7.4_

- [ ] 8.3 Restore or implement overall_quality_score method
  - Add overall_quality_score method to ContentQualityAnalyzer
  - Calculate weighted average of quality dimensions
  - Return float score between 0-100
  - _Requirements: 7.2, 7.4_

- [ ] 8.4 Update quality domain models
  - Update `backend/app/domain/quality.py`
  - Add ReadabilityScore and QualityMetrics dataclasses
  - Ensure structures match test expectations
  - _Requirements: 7.3_

- [ ] 8.5 Update quality service tests
  - Update `backend/tests/unit/phase9_quality/test_quality_service_phase9.py`
  - Update assertions to match structured return types
  - _Requirements: 7.4, 7.5_

- [ ] 8.6 Update quality integration tests
  - Update `backend/tests/integration/phase9_quality/` tests
  - Apply same assertion updates
  - _Requirements: 7.4, 7.5_

- [ ]* 8.7 Verify QualityService fixes
  - Run `pytest backend/tests/unit/phase9_quality/ -v`
  - Run `pytest backend/tests/integration/phase9_quality/ -v`
  - Verify no AttributeError on quality methods
  - _Requirements: 7.4_

- [x] 9. Complete ClassificationService implementation




  - Implement ClassificationTrainer.train method
  - Fix semi-supervised learning workflow
  - Correct checkpoint directory paths
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 9.1 Audit ClassificationService implementation


  - Read `backend/app/services/ml_classification_service.py`
  - Document existing methods and identify gaps
  - Check ClassificationTrainer class structure
  - _Requirements: 8.1_


- [x] 9.2 Implement ClassificationTrainer.train method

  - Add train method with proper signature
  - Implement training loop and checkpoint saving
  - Return TrainingResult with metrics
  - _Requirements: 8.1, 8.4_


- [x] 9.3 Fix semi-supervised learning methods

  - Update train_semi_supervised method
  - Ensure return type matches TrainingResult
  - Implement pseudo-labeling workflow
  - _Requirements: 8.2, 8.4_



- [x] 9.4 Fix checkpoint path handling
  - Update load_checkpoint method
  - Create models/classification directory structure
  - Handle relative and absolute checkpoint paths
  - _Requirements: 8.3, 8.4_


- [x] 9.5 Update classification domain models

  - Update `backend/app/domain/classification.py`
  - Add TrainingExample and TrainingResult dataclasses

  - _Requirements: 8.4_

- [x] 9.6 Update classification tests

  - Update `backend/tests/unit/phase8_classification/test_ml_classification_service.py`
  - Update test calls to match implemented API
  - _Requirements: 8.4, 8.5_

- [ ]* 9.7 Verify ClassificationService fixes
  - Run `pytest backend/tests/unit/phase8_classification/ -v`
  - Run `pytest backend/tests/integration/phase8_classification/ -v`
  - Verify training methods execute without errors
  - _Requirements: 8.4_

## Phase 4: Graph Intelligence Completion (P2)

- [ ] 10. Implement LBD discovery features
  - Implement LBDService.open_discovery method
  - Implement closed_discovery method
  - Fix edge type filtering in graph construction
  - Complete multi-layer graph construction
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ] 10.1 Create or update LBDService class
  - Check if LBDService exists in `backend/app/services/graph_service.py`
  - Create class if missing or update existing implementation
  - _Requirements: 10.1_

- [ ] 10.2 Implement open_discovery method
  - Add open_discovery method to LBDService
  - Implement Swanson's ABC model for literature-based discovery
  - Find paths between start and end concepts
  - Score and rank discovery paths
  - _Requirements: 10.1, 10.4_

- [ ] 10.3 Implement closed_discovery method
  - Add closed_discovery method to LBDService
  - Find intermediate concepts related to start concept
  - Return ranked list of related concepts
  - _Requirements: 10.1, 10.4_

- [ ] 10.4 Fix edge type filtering in GraphService
  - Update build_knowledge_graph method
  - Add edge_types parameter for filtering
  - Filter relationships by type when building graph
  - _Requirements: 10.2, 10.4_

- [ ] 10.5 Complete multi-layer graph construction
  - Implement build_multi_layer_graph method
  - Create separate graph layers (citation, semantic, author, topic)
  - Return dictionary of layer graphs
  - _Requirements: 10.3, 10.4_

- [ ] 10.6 Update graph domain models
  - Update `backend/app/domain/graph.py`
  - Add DiscoveryPath dataclass
  - Add supporting data structures
  - _Requirements: 10.4_

- [ ] 10.7 Update graph intelligence tests
  - Update `backend/tests/unit/phase10_graph_intelligence/` tests
  - Update test calls to match implemented API
  - _Requirements: 10.4, 10.5_

- [ ]* 10.8 Verify graph intelligence fixes
  - Run `pytest backend/tests/unit/phase10_graph_intelligence/ -v`
  - Run `pytest backend/tests/integration/phase10_graph_intelligence/ -v`
  - Verify LBD discovery methods work correctly
  - _Requirements: 10.4_

## Phase 5: Dependencies and Final Verification (P3)

- [ ] 11. Handle optional Python dependencies
  - Add optional dependencies to requirements-dev.txt
  - Add pytest.importorskip for optional modules
  - Mark tests with clear skip messages
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 11.1 Add optional dependencies to requirements-dev.txt
  - Add trio, openai, plotly to `backend/requirements-dev.txt`
  - Document which features require which dependencies
  - _Requirements: 6.2_

- [ ] 11.2 Add importorskip to tests using trio
  - Find tests importing trio
  - Add `pytest.importorskip("trio")` at module or test level
  - _Requirements: 6.1, 6.3_

- [ ] 11.3 Add importorskip to tests using openai
  - Find tests importing openai (G-Eval metrics)
  - Add `pytest.importorskip("openai")` with clear reason
  - _Requirements: 6.1, 6.3_

- [ ] 11.4 Add importorskip to tests using plotly
  - Find tests importing plotly (visualization)
  - Add `pytest.importorskip("plotly")` with clear reason
  - _Requirements: 6.1, 6.3_

- [ ] 11.5 Update test README with dependency documentation
  - Update `backend/tests/README.md`
  - Document required vs optional dependencies
  - Add instructions for running tests with/without optional deps
  - _Requirements: 6.4_

- [ ] 11.6 Add optional marker to pytest.ini
  - Update `backend/pytest.ini`
  - Add custom marker for optional tests
  - _Requirements: 6.3_

- [ ]* 11.7 Verify dependency handling
  - Run tests without optional dependencies installed
  - Verify tests skip with clear messages
  - Install optional dependencies and verify tests run
  - _Requirements: 6.3_

- [ ] 12. Final test suite verification
  - Run full test suite and analyze results
  - Fix any remaining failures
  - Document test success metrics
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 12.1 Run full test suite with coverage
  - Execute `pytest backend/tests/ -v --tb=short --cov`
  - Capture test results and failure analysis
  - _Requirements: 11.1, 11.2_

- [ ] 12.2 Analyze remaining failures
  - Review any tests still failing
  - Categorize by root cause
  - Create fix plan for remaining issues
  - _Requirements: 11.1, 11.2_

- [ ] 12.3 Fix remaining edge cases
  - Address any uncategorized failures
  - Update tests or implementation as needed
  - _Requirements: 11.1, 11.2_

- [ ] 12.4 Verify test success metrics
  - Confirm 100% pass rate for non-skipped tests
  - Verify skip messages are clear and accurate
  - Check test execution time (<10 minutes target)
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 12.5 Update documentation
  - Update `backend/docs/MIGRATION_GUIDE.md` with breaking changes
  - Update API documentation for changed services
  - Document test execution best practices
  - _Requirements: 11.5_

- [ ]* 12.6 Final verification run
  - Run `pytest backend/tests/ -v` one final time
  - Verify all 1,867 tests pass or skip appropriately
  - Confirm zero genuine coding errors remain
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
