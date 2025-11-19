# Test Failure Analysis Report

## Summary

- **Total Tests**: 1750
- **Passed**: 1309 (74.8%)
- **Failed**: 242
- **Errors**: 175
- **Skipped**: 24

## Failure Pattern Matrix

| Category | Type | Count | Priority | Effort | Fix Approach |
|----------|------|-------|----------|--------|--------------|
| QualityScore Integration | AssertionError / AttributeError | 24 | Critical | Medium | Update tests to handle QualityScore domain objects, use .overall_score() method |
| API Endpoints | AssertionError | 7 | Critical | Small | Update API tests to handle domain object serialization |
| Recommendation Integration | ImportError / FixtureError | 65 | High | Small | Fix fixture dependencies and imports |
| Integration Tests | ImportError / FixtureError | 42 | High | Medium | Fix integration test fixtures and dependencies |
| Classification Integration | AssertionError / TypeError | 41 | High | Medium | Update tests to handle ClassificationResult domain objects |
| Search Integration | AssertionError / TypeError | 36 | High | Medium | Update tests to handle SearchResult domain objects |
| Graph/Discovery Integration | ImportError / FixtureError | 23 | High | Small | Fix fixture dependencies and imports |
| Database Schema | AssertionError | 3 | Medium | Small | Update database schema tests and initialization helpers |
| Discovery Hypothesis Compatibility | AssertionError | 3 | Medium | Small | Update compatibility layer for new field names |
| Celery Tasks | AssertionError | 1 | Medium | Small | Update Celery task tests for domain objects |
| Performance Tests | ImportError / FixtureError | 13 | Low | Small | Fix performance test fixtures and dependencies |
| Training/ML | AssertionError / ImportError | 10 | Low | Medium | Fix ML model mocking and training test setup |
| Domain Validation | ValidationError | 2 | Low | Small | Update domain object validation logic |

## Detailed Patterns

### QualityScore Integration

- **Failure Type**: AssertionError / AttributeError
- **Count**: 24
- **Priority**: Critical
- **Effort**: Medium
- **Example Test**: `tests/integration/phase2_curation/test_curation_endpoints.py::TestQualityAnalysisEndpoint::test_quality_analysis_success`
- **Example Error**: Tests expect dict but receive QualityScore domain object
- **Fix Approach**: Update tests to handle QualityScore domain objects, use .overall_score() method
- **Affected Files**: 11 files

  - tests/unit/phase9_quality/test_degradation_monitoring.py
  - tests/unit/test_celery_tasks.py
  - tests/integration/phase9_quality/test_quality_integration.py
  - tests/integration/phase9_quality/test_quality_endpoints_simple.py
  - tests/unit/phase11_recommendations/test_hybrid_recommendations.py
  - ... and 6 more

### API Endpoints

- **Failure Type**: AssertionError
- **Count**: 7
- **Priority**: Critical
- **Effort**: Small
- **Example Test**: `tests/api/test_phase2_curation_api.py::TestResourcesCRUDAndList::test_update_resource_partial`
- **Example Error**: API response serialization issues with domain objects
- **Fix Approach**: Update API tests to handle domain object serialization
- **Affected Files**: 2 files

  - tests/integration/phase10_graph_intelligence/test_phase10_discovery_api.py
  - tests/api/test_phase2_curation_api.py

### Recommendation Integration

- **Failure Type**: ImportError / FixtureError
- **Count**: 65
- **Priority**: High
- **Effort**: Small
- **Example Test**: `tests/integration/phase10_graph_intelligence/test_phase10_integration.py::TestRecommendationIntegration::test_graph_based_recommendations`
- **Example Error**: Fixture or import errors in recommendation tests
- **Fix Approach**: Fix fixture dependencies and imports
- **Affected Files**: 5 files

  - tests/unit/phase9_quality/test_recommendation_quality_integration.py
  - tests/integration/phase11_recommendations/test_recommendation_api.py
  - tests/integration/phase10_graph_intelligence/test_phase10_integration.py
  - tests/unit/phase11_recommendations/test_collaborative_filtering.py
  - tests/integration/phase5_graph/test_phase55_recommendations.py

### Integration Tests

- **Failure Type**: ImportError / FixtureError
- **Count**: 42
- **Priority**: High
- **Effort**: Medium
- **Example Test**: `tests/integration/phase1_ingestion/test_resource_ingestion_classification.py::test_classification_executes_after_embeddings`
- **Example Error**: Integration test fixture or import errors
- **Fix Approach**: Fix integration test fixtures and dependencies
- **Affected Files**: 4 files

  - tests/integration/phase6_citations/test_phase6_5_scholarly.py
  - tests/integration/phase9_quality/test_quality_workflows_integration.py
  - tests/integration/phase9_quality/test_quality_api_endpoints.py
  - tests/integration/phase1_ingestion/test_resource_ingestion_classification.py

### Classification Integration

- **Failure Type**: AssertionError / TypeError
- **Count**: 41
- **Priority**: High
- **Effort**: Medium
- **Example Test**: `tests/integration/phase1_ingestion/test_resource_ingestion_classification.py::test_classification_triggered_during_ingestion`
- **Example Error**: Tests expect dict but receive ClassificationResult domain object
- **Fix Approach**: Update tests to handle ClassificationResult domain objects
- **Affected Files**: 14 files

  - tests/integration/training/test_classification_training.py
  - tests/integration/phase1_ingestion/test_resource_ingestion_classification.py
  - tests/integration/phase8_classification/test_classification_endpoints.py
  - tests/integration/workflows/test_api_endpoints.py
  - tests/services/test_ml_classification_cqs.py
  - ... and 9 more

### Search Integration

- **Failure Type**: AssertionError / TypeError
- **Count**: 36
- **Priority**: High
- **Effort**: Medium
- **Example Test**: `tests/api/test_phase3_search_api.py::test_post_search_basic_total_and_items`
- **Example Error**: Tests expect dict but receive SearchResult domain object
- **Fix Approach**: Update tests to handle SearchResult domain objects
- **Affected Files**: 14 files

  - tests/unit/training/test_hyperparameter_search.py
  - tests/integration/phase3_search/test_enhanced_search_api.py
  - tests/integration/phase4_hybrid_search/test_phase4_hybrid_search.py
  - tests/api/test_phase3_search_api.py
  - tests/integration/phase7_collections/test_phase7_5_annotations.py
  - ... and 9 more

### Graph/Discovery Integration

- **Failure Type**: ImportError / FixtureError
- **Count**: 23
- **Priority**: High
- **Effort**: Small
- **Example Test**: `tests/integration/phase10_graph_intelligence/test_phase10_integration.py::TestEndToEndDiscoveryWorkflow::test_complete_workflow`
- **Example Error**: Fixture or import errors in graph/discovery tests
- **Fix Approach**: Fix fixture dependencies and imports
- **Affected Files**: 3 files

  - tests/unit/phase9_quality/test_recommendation_quality_integration.py
  - tests/integration/phase10_graph_intelligence/test_phase10_integration.py
  - tests/integration/phase5_graph/test_phase55_recommendations.py

### Database Schema

- **Failure Type**: AssertionError
- **Count**: 3
- **Priority**: Medium
- **Effort**: Small
- **Example Test**: `tests/database/test_database_schema.py::test_database_initialization_helper`
- **Example Error**: Database schema or initialization issues
- **Fix Approach**: Update database schema tests and initialization helpers
- **Affected Files**: 3 files

  - tests/database/test_schema_verification.py
  - tests/database/test_database_schema.py
  - tests/integration/workflows/test_api_endpoints.py

### Discovery Hypothesis Compatibility

- **Failure Type**: AssertionError
- **Count**: 3
- **Priority**: Medium
- **Effort**: Small
- **Example Test**: `tests/unit/test_discovery_hypothesis_compatibility.py::TestDiscoveryHypothesisCompatibility::test_backward_compatibility_properties`
- **Example Error**: Backward compatibility issues with discovery/hypothesis fields
- **Fix Approach**: Update compatibility layer for new field names
- **Affected Files**: 1 files

  - tests/unit/test_discovery_hypothesis_compatibility.py

### Celery Tasks

- **Failure Type**: AssertionError
- **Count**: 1
- **Priority**: Medium
- **Effort**: Small
- **Example Test**: `tests/unit/test_celery_tasks.py::TestRecomputeQualityTask::test_successful_quality_recomputation`
- **Example Error**: Celery task test failures
- **Fix Approach**: Update Celery task tests for domain objects
- **Affected Files**: 1 files

  - tests/unit/test_celery_tasks.py

### Performance Tests

- **Failure Type**: ImportError / FixtureError
- **Count**: 13
- **Priority**: Low
- **Effort**: Small
- **Example Test**: `tests/integration/phase5_graph/test_phase55_recommendations.py::TestPerformance::test_large_library_performance`
- **Example Error**: Performance test fixture or import errors
- **Fix Approach**: Fix performance test fixtures and dependencies
- **Affected Files**: 2 files

  - tests/performance/phase9_quality/test_quality_performance.py
  - tests/integration/phase5_graph/test_phase55_recommendations.py

### Training/ML

- **Failure Type**: AssertionError / ImportError
- **Count**: 10
- **Priority**: Low
- **Effort**: Medium
- **Example Test**: `tests/integration/training/test_ab_testing.py::TestABTestingFramework::test_prediction_logging`
- **Example Error**: Training and hyperparameter search test failures
- **Fix Approach**: Fix ML model mocking and training test setup
- **Affected Files**: 5 files

  - tests/unit/training/test_hyperparameter_search.py
  - tests/integration/training/test_classification_training.py
  - tests/unit/training/test_error_handling.py
  - tests/unit/phase8_classification/test_ml_training.py
  - tests/integration/training/test_ab_testing.py

### Domain Validation

- **Failure Type**: ValidationError
- **Count**: 2
- **Priority**: Low
- **Effort**: Small
- **Example Test**: `tests/domain/test_domain_search.py::TestSearchQuery::test_query_text_validation_empty`
- **Example Error**: Domain object validation not raising expected errors
- **Fix Approach**: Update domain object validation logic
- **Affected Files**: 1 files

  - tests/domain/test_domain_search.py
