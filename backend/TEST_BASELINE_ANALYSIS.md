# Test Baseline Analysis - Phase 10.5 Code Standardization

**Date:** November 13, 2025
**Total Tests:** 896
**Passed:** 797
**Failed:** 75
**Errors:** 24
**Skipped:** 18
**Total Duration:** 28 minutes 11 seconds

## Executive Summary

This document provides a comprehensive baseline of all test failures and errors in the codebase, categorized by root cause. The analysis identifies 8 primary failure categories, with **Resource Model Schema Issues** being the highest priority, affecting 28 tests (28.3% of all failures).

---

## Failure Categories Overview

| Category | Failed Tests | Error Tests | Total | Priority | Impact |
|----------|--------------|-------------|-------|----------|--------|
| 1. Resource Model Schema Issues | 21 | 7 | 28 | **CRITICAL** | 28.3% |
| 2. SQLAlchemy Query/Binding Issues | 1 | 10 | 11 | **HIGH** | 11.1% |
| 3. Missing Dependencies | 11 | 0 | 11 | **HIGH** | 11.1% |
| 4. Pytest Fixture Misuse | 11 | 0 | 11 | **MEDIUM** | 11.1% |
| 5. API Response Schema Mismatches | 9 | 0 | 9 | **MEDIUM** | 9.1% |
| 6. Ingestion Pipeline Failures | 6 | 0 | 6 | **MEDIUM** | 6.1% |
| 7. UUID/Type Serialization Issues | 6 | 0 | 6 | **MEDIUM** | 6.1% |
| 8. Miscellaneous Issues | 10 | 7 | 17 | **LOW** | 17.2% |

---

## Category 1: Resource Model Schema Issues (CRITICAL - 28 tests)

**Root Cause:** Tests are using invalid keyword arguments for the `Resource` model, particularly `summary`, `resource_type`, and `url`. This suggests the Resource model schema has changed or tests are using outdated initialization patterns.

### Failed Tests (21):
1. `test_quality_api_endpoints.py::TestSummaryEvaluationEndpoint::test_evaluate_summary_success`
   - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
   
2. `test_quality_api_endpoints.py::TestSummaryEvaluationEndpoint::test_evaluate_summary_with_g_eval`
   - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
   
3. `test_quality_api_endpoints.py::TestSummaryEvaluationEndpoint::test_evaluate_summary_no_summary`
   - **Error:** `AttributeError: 'Resource' object has no attribute 'summary'`
   
4. `test_quality_performance.py::TestQualityComputationLatency::test_average_latency_multiple_resources`
   - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
   
5. `test_quality_performance.py::TestBatchQualityComputationThroughput::test_batch_throughput_100_resources`
   - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
   
6. `test_quality_performance.py::TestBatchQualityComputationThroughput::test_batch_computation_scales_linearly`
   - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
   
7. `test_quality_performance.py::TestOutlierDetectionPerformance::test_outlier_detection_1000_resources`
   - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
   
8. `test_quality_performance.py::TestOutlierDetectionPerformance::test_outlier_detection_with_batching`
   - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
   
9. `test_quality_performance.py::TestSummarizationEvaluationLatency::test_evaluation_without_g_eval_latency`
   - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
   
10. `test_quality_performance.py::TestDegradationMonitoringPerformance::test_degradation_monitoring_performance`
    - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
    
11. `test_quality_performance.py::TestMemoryUsage::test_batch_processing_memory_efficiency`
    - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
    
12. `test_quality_performance.py::TestMemoryUsage::test_outlier_detection_memory_efficiency`
    - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
    
13. `test_quality_performance.py::TestConcurrentOperations::test_concurrent_quality_computations`
    - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
    
14. `test_quality_workflows_integration.py::TestEndToEndQualityAssessment::test_resource_creation_to_quality_score`
    - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
    
15. `test_quality_workflows_integration.py::TestSummarizationEvaluationWorkflow::test_summary_generation_to_evaluation`
    - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
    
16. `test_quality_workflows_integration.py::TestOutlierDetectionWorkflow::test_batch_outlier_detection`
    - **Error:** `TypeError: 'url' is an invalid keyword argument for Resource`
    
17. `test_quality_workflows_integration.py::TestCrossPhaseIntegration::test_complete_resource_lifecycle`
    - **Error:** `TypeError: 'summary' is an invalid keyword argument for Resource`
    
18. `test_quality_workflows_integration.py::TestEndToEndQualityAssessment::test_quality_with_phase6_citations`
    - **Error:** `TypeError: 'resource_id' is an invalid keyword argument for Citation`
    
19. `test_integration.py::TestIngestionPipelineIntegration::test_pipeline_archive_structure`
    - **Error:** `TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'`
    - **Note:** Likely related to Resource model not returning expected path attribute
    
20. `test_integration.py::TestIngestionPipelineIntegration::test_pipeline_readability_calculation`
    - **Error:** `TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'`
    - **Note:** Likely related to Resource model not returning expected path attribute
    
21. `test_integration.py::TestIngestionPipelineIntegration::test_complete_pipeline_success`
    - **Error:** `assert 0.0 > 0`
    - **Note:** Quality score is 0.0, possibly due to Resource model issues

### Error Tests (7):
22. `test_phase10_integration.py::TestEndToEndDiscoveryWorkflow::test_complete_workflow`
    - **Error:** `TypeError: 'resource_type' is an invalid keyword argument for Resource`
    
23. `test_phase10_integration.py::TestEndToEndDiscoveryWorkflow::test_closed_discovery_workflow`
    - **Error:** `TypeError: 'resource_type' is an invalid keyword argument for Resource`
    
24. `test_phase10_integration.py::TestRecommendationIntegration::test_graph_based_recommendations`
    - **Error:** `TypeError: 'resource_type' is an invalid keyword argument for Resource`
    
25. `test_phase10_integration.py::TestRecommendationIntegration::test_recommendation_fusion`
    - **Error:** `TypeError: 'resource_type' is an invalid keyword argument for Resource`
    
26. `test_phase10_integration.py::TestRecommendationIntegration::test_hypothesis_based_recommendations`
    - **Error:** `TypeError: 'resource_type' is an invalid keyword argument for Resource`
    
27. `test_phase10_integration.py::TestGraphCaching::test_graph_cache_reuse`
    - **Error:** `TypeError: 'resource_type' is an invalid keyword argument for Resource`
    
28. `test_phase10_integration.py::TestGraphCaching::test_graph_cache_invalidation`
    - **Error:** `TypeError: 'resource_type' is an invalid keyword argument for Resource`

**Recommended Fix:** Review Resource model schema and update all test fixtures to use correct initialization parameters.

---

## Category 2: SQLAlchemy Query/Binding Issues (HIGH - 11 tests)

**Root Cause:** SQLite parameter binding error when trying to bind list types. Error message: "Error binding parameter 38: type 'list' is not supported". This suggests queries are attempting to bind Python lists directly instead of using proper SQLAlchemy array handling.

### Failed Tests (1):
1. `test_quality_api_endpoints.py::TestReviewQueueEndpoint::test_get_review_queue_empty`
   - **Error:** `KeyError: 'queue'`
   - **Note:** May be related to query failure causing missing response key

### Error Tests (10):
2. `test_quality_api_endpoints.py::TestOutliersEndpoint::test_get_outliers_success`
   - **Error:** `sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 38: type 'list' is not supported`
   
3. `test_quality_api_endpoints.py::TestOutliersEndpoint::test_get_outliers_with_pagination`
   - **Error:** `sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 38: type 'list' is not supported`
   
4. `test_quality_api_endpoints.py::TestOutliersEndpoint::test_get_outliers_filter_by_score`
   - **Error:** `sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 38: type 'list' is not supported`
   
5. `test_quality_api_endpoints.py::TestOutliersEndpoint::test_get_outliers_filter_by_reason`
   - **Error:** `sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 38: type 'list' is not supported`
   
6. `test_quality_api_endpoints.py::TestReviewQueueEndpoint::test_get_review_queue`
   - **Error:** `sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 38: type 'list' is not supported`
   
7. `test_quality_api_endpoints.py::TestReviewQueueEndpoint::test_get_review_queue_with_pagination`
   - **Error:** `sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 38: type 'list' is not supported`
   
8. `test_quality_api_endpoints.py::TestReviewQueueEndpoint::test_get_review_queue_sort_by_score`
   - **Error:** `sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 38: type 'list' is not supported`
   
9-15. `test_quality_degradation_unit.py::TestMonitorQualityDegradation::*` (7 tests)
    - **Error:** Various errors, likely stemming from the same query binding issue

**Recommended Fix:** Identify queries using list parameters and convert to proper SQLAlchemy array handling or use `IN` clauses with proper parameter expansion.

---

## Category 3: Missing Dependencies (HIGH - 11 tests)

**Root Cause:** Required Python packages `openai` and `bert_score` are not installed in the test environment.

### Failed Tests (11):
1-7. `test_summarization_evaluator_unit.py::TestGEvalMethods::*` (7 tests)
   - **Error:** `ModuleNotFoundError: No module named 'openai'`
   - Tests: `test_g_eval_coherence_success`, `test_g_eval_consistency_success`, `test_g_eval_fluency_success`, `test_g_eval_relevance_success`, `test_g_eval_api_error_fallback`, `test_g_eval_parse_rating_variations`
   
8-10. `test_summarization_evaluator_unit.py::TestBERTScore::*` (3 tests)
   - **Error:** `ModuleNotFoundError: No module named 'bert_score'`
   - Tests: `test_bertscore_success`, `test_bertscore_error_fallback`, `test_bertscore_model_configuration`
   
11. `test_summarization_evaluator_unit.py::TestGEvalMethods::test_g_eval_without_api_key`
    - **Error:** `TypeError: SummarizationEvaluator.g_eval_coherence() takes 2 positional arguments but 3 were given`
    - **Note:** Different error, but in same test file

**Recommended Fix:** Add `openai` and `bert-score` to requirements.txt or requirements-test.txt, or mock these dependencies in tests.

---

## Category 4: Pytest Fixture Misuse (MEDIUM - 11 tests)

**Root Cause:** Tests are calling fixtures directly instead of using them as function parameters. Error: "Fixture 'large_test_dataset' called directly. Fixtures are not meant to be called directly"

### Failed Tests (11):
All in `test_phase10_performance.py`:

1-2. `TestGraphConstructionPerformance::test_graph_construction_time[1000]`, `[5000]`
3-4. `TestTwoHopQueryPerformance::test_two_hop_query_latency[1000]`, `[5000]`
5-7. `TestHNSWQueryPerformance::test_hnsw_query_latency[1000]`, `[5000]`, `[10000]`
8. `TestGraph2VecPerformance::test_graph2vec_computation_rate`
9. `TestMemoryUsage::test_graph_cache_memory`
10. `TestMemoryUsage::test_hnsw_index_memory`
11. `TestDiscoveryPerformance::test_open_discovery_latency`
12. `TestDiscoveryPerformance::test_closed_discovery_latency`

**Recommended Fix:** Refactor tests to accept `large_test_dataset` as a parameter instead of calling it directly.

---

## Category 5: API Response Schema Mismatches (MEDIUM - 9 tests)

**Root Cause:** API endpoints are returning response keys that don't match test expectations (e.g., `avg` instead of `average`, `data_points` instead of `trends`).

### Failed Tests (9):
1. `test_quality_api_endpoints.py::TestQualityDetailsEndpoint::test_get_quality_details_success`
   - **Error:** `AssertionError: assert '9d62a2fd-bf70-4d01-9b52-25d6bfd81dea' == UUID('9d62a2fd-bf70-4d01-9b52-25d6bfd81dea')`
   - **Issue:** String vs UUID type mismatch
   
2. `test_quality_api_endpoints.py::TestDegradationEndpoint::test_get_degradation_report`
   - **Error:** `AssertionError: assert 'total_checked' in {...}`
   - **Issue:** Missing expected key in response
   
3. `test_quality_api_endpoints.py::TestDegradationEndpoint::test_get_degradation_invalid_window`
   - **Error:** `assert 422 == 400`
   - **Issue:** Wrong HTTP status code
   
4. `test_quality_api_endpoints.py::TestQualityTrendsEndpoint::test_get_trends_daily`
   - **Error:** `AssertionError: assert 'trends' in {'data_points': [...], 'dimension': 'overall', 'granularity': 'daily'}`
   - **Issue:** Response uses `data_points` instead of `trends`
   
5. `test_quality_api_endpoints.py::TestQualityTrendsEndpoint::test_get_trends_with_date_range`
   - **Error:** `assert 400 == 200`
   - **Issue:** Endpoint returning error status
   
6. `test_quality_api_endpoints.py::TestDimensionAveragesEndpoint::test_get_dimension_averages`
   - **Error:** `AssertionError: assert 'average' in {'avg': 0.75, 'max': 0.75, 'min': 0.75}`
   - **Issue:** Response uses `avg` instead of `average`
   
7. `test_quality_degradation_unit.py::TestMonitorQualityDegradation::test_degradation_custom_time_window`
   - **Error:** `AssertionError: assert (UUID(...) in ['...'] or 1 == 0)`
   - **Issue:** UUID comparison issue
   
8. `test_phase10_discovery_api.py::TestDiscoveryAPIEndpoints::test_neighbors_endpoint`
   - **Error:** `assert 404 == 200`
   - **Issue:** Endpoint not found or not implemented
   
9. `test_integration.py::TestIngestionPipelineIntegration::test_pipeline_quality_scoring`
   - **Error:** `assert 0.0 > 0.5`
   - **Issue:** Quality score below expected threshold

**Recommended Fix:** Standardize API response schemas to match test expectations or update tests to match current API contracts.

---

## Category 6: Ingestion Pipeline Failures (MEDIUM - 6 tests)

**Root Cause:** Ingestion operations are completing with 'failed' status instead of 'completed', suggesting issues in the ingestion pipeline logic.

### Failed Tests (6):
1. `test_async_ingestion.py::TestAsyncIngestionIntegration::test_multiple_concurrent_ingestions`
   - **Error:** `AssertionError: assert 'failed' == 'completed'`
   
2. `test_ingestion_status.py::TestIngestionStatusTracking::test_status_endpoint_completed`
   - **Error:** `AssertionError: assert 'failed' == 'completed'`
   
3. `test_ingestion_status.py::TestIngestionStatusTracking::test_status_timestamps_progression`
   - **Error:** `AssertionError: assert 'failed' == 'completed'`
   
4. `test_ingestion_status.py::TestIngestionStatusPolling::test_polling_until_completion`
   - **Error:** `AssertionError: assert 'failed' == 'completed'`
   
5. `test_ingestion_status.py::TestIngestionStatusConcurrency::test_status_during_processing`
   - **Error:** `AssertionError: assert 'failed' in ['pending', 'completed']`
   
6. `test_phase1_ingestion.py::test_ingestion_pipeline_writes_archive_and_persists`
   - **Error:** `assert []`
   - **Issue:** Empty result when data expected

**Recommended Fix:** Debug ingestion pipeline to identify why operations are failing. Check error logging and exception handling.

---

## Category 7: UUID/Type Serialization Issues (MEDIUM - 6 tests)

**Root Cause:** UUID objects are not being properly serialized to JSON, causing `TypeError: Object of type UUID is not JSON serializable`.

### Failed Tests (6):
All in `test_quality_api_endpoints.py::TestQualityRecalculateEndpoint`:

1. `test_recalculate_single_resource`
2. `test_recalculate_multiple_resources`
3. `test_recalculate_with_custom_weights`
4. `test_recalculate_invalid_weights_sum`
5. `test_recalculate_missing_dimension`

All have error: `TypeError: Object of type UUID is not JSON serializable`

**Recommended Fix:** Add UUID serialization handler to JSON encoder or convert UUIDs to strings before serialization.

---

## Category 8: Miscellaneous Issues (LOW - 17 tests)

### Subcategory 8a: Model/Tensor Issues (2 tests)
1-2. `test_performance.py::test_single_prediction_inference_time`, `test_batch_prediction_performance`
   - **Error:** `NotImplementedError: Cannot copy out of meta tensor; no data!`
   - **Issue:** Model tensor operations failing

### Subcategory 8b: Test Logic Issues (5 tests)
1. `test_ai_integration.py::TestAIIntegration::test_ai_summary_generation`
   - **Error:** `AssertionError: assert 322 < 266`
   - **Issue:** Summary length exceeds expected maximum
   
2. `test_integration.py::TestIngestionPipelineIntegration::test_pipeline_with_ai_tag_generation`
   - **Error:** `assert None is not None`
   - **Issue:** Expected value is None
   
3. `test_ml_classification_service.py::test_update_from_human_feedback_preserves_existing_manual`
   - **Error:** `AssertionError: Expected 1 manual classification, found 2`
   
4. `test_phase6_5_scholarly.py::TestEquationExtraction::test_normalize_latex`
   - **Error:** `re.error: bad escape (end of pattern) at position 0`
   - **Issue:** Invalid regex pattern
   
5. `test_phase7_5_annotations.py::TestAnnotationPerformance::test_annotation_creation_performance`
   - **Error:** `assert 0.6063933372497559 < 0.05`
   - **Issue:** Performance threshold not met

### Subcategory 8c: Database Constraint Issues (2 tests)
1. `test_quality_workflows_integration.py::TestEndToEndQualityAssessment::test_quality_with_phase85_classification`
   - **Error:** `sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: taxonomy_nodes.slug`
   
2. `test_quality_workflows_integration.py::TestEndToEndQualityAssessment::test_quality_with_phase65_scholarly_metadata`
   - **Error:** `assert 0.55 > 0.7`
   - **Issue:** Quality score below threshold

### Subcategory 8d: Test Assertion Issues (1 test)
1. `test_summarization_evaluator_unit.py::TestEvaluateSummary::test_evaluate_summary_no_summary`
   - **Error:** `Failed: DID NOT RAISE <class 'ValueError'>`
   - **Issue:** Expected exception not raised

### Subcategory 8e: Sparse Embedding Issues (1 test)
1. `test_sparse_embedding_service.py::TestSparseEmbeddingService::test_generate_sparse_embedding_with_mock_model`
   - **Error:** `assert (False or None == {})`
   - **Issue:** Unexpected return value

### Subcategory 8f: Resource Model Errors (6 tests)
All in `test_summarization_evaluator_unit.py::TestEvaluateSummary`:
- `test_evaluate_summary_with_g_eval`
- `test_evaluate_summary_without_g_eval`
- `test_evaluate_summary_composite_calculation`

All have error: `TypeError: 'summary' is an invalid keyword argument for Resource`
(Already counted in Category 1)

---

## Priority Action Plan

### Phase 1: Critical Fixes (28 tests - 28.3%)
1. **Fix Resource Model Schema Issues**
   - Audit Resource model definition
   - Update all test fixtures using `summary`, `resource_type`, `url` parameters
   - Update Citation model usage in tests
   - Estimated impact: 28 tests fixed

### Phase 2: High Priority Fixes (22 tests - 22.2%)
2. **Fix SQLAlchemy Query Binding Issues**
   - Identify queries with list parameter binding
   - Refactor to use proper SQLAlchemy array handling
   - Estimated impact: 11 tests fixed

3. **Add Missing Dependencies**
   - Add `openai` and `bert-score` to requirements
   - Or implement proper mocking for these dependencies
   - Estimated impact: 11 tests fixed

### Phase 3: Medium Priority Fixes (37 tests - 37.4%)
4. **Fix Pytest Fixture Usage**
   - Refactor `test_phase10_performance.py` to use fixtures correctly
   - Estimated impact: 11 tests fixed

5. **Standardize API Response Schemas**
   - Update API endpoints or tests to align on response structure
   - Fix UUID serialization issues
   - Estimated impact: 15 tests fixed

6. **Debug Ingestion Pipeline**
   - Investigate why ingestions are failing
   - Fix error handling and status tracking
   - Estimated impact: 6 tests fixed

7. **Fix UUID Serialization**
   - Add JSON encoder for UUID types
   - Estimated impact: 6 tests fixed (overlap with #5)

### Phase 4: Low Priority Fixes (12 tests - 12.1%)
8. **Address Miscellaneous Issues**
   - Fix model/tensor issues
   - Update test assertions and thresholds
   - Fix regex patterns
   - Address database constraints
   - Estimated impact: 12 tests fixed

---

## Test Files Requiring Attention

### High Impact Files (>5 failures):
1. **test_quality_api_endpoints.py** - 20 failures/errors
2. **test_quality_performance.py** - 10 failures
3. **test_phase10_performance.py** - 11 failures
4. **test_summarization_evaluator_unit.py** - 11 failures
5. **test_quality_workflows_integration.py** - 7 failures
6. **test_phase10_integration.py** - 7 errors
7. **test_quality_degradation_unit.py** - 8 errors
8. **test_ingestion_status.py** - 4 failures
9. **test_integration.py** - 5 failures

### Medium Impact Files (2-4 failures):
10. **test_async_ingestion.py** - 1 failure
11. **test_performance.py** - 2 failures
12. **test_phase10_discovery_api.py** - 1 failure

### Low Impact Files (1 failure):
13. **test_ai_integration.py** - 1 failure
14. **test_ml_classification_service.py** - 1 failure
15. **test_phase1_ingestion.py** - 1 failure
16. **test_phase6_5_scholarly.py** - 1 failure
17. **test_phase7_5_annotations.py** - 1 failure
18. **test_sparse_embedding_service.py** - 1 failure

---

## Conclusion

The test suite has **75 failures and 24 errors** affecting **99 total test cases** out of 896 tests (11% failure rate). The highest priority issue is **Resource Model Schema Issues**, which affects 28 tests across multiple test files. Fixing this single category would reduce the failure count by 28.3%.

The recommended approach is to tackle issues in priority order:
1. Fix Resource model schema (28 tests)
2. Fix SQLAlchemy binding issues (11 tests)
3. Add missing dependencies (11 tests)
4. Fix fixture usage (11 tests)
5. Standardize API schemas (15 tests)
6. Debug ingestion pipeline (6 tests)
7. Address remaining miscellaneous issues (17 tests)

This systematic approach should restore the test suite to a healthy state with >95% pass rate.
