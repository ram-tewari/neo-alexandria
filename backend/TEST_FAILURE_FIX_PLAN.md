# Test Failure Fix Plan

## Summary
58 tests failing across 3 main categories:
1. **Monitoring tests (33 failures)**: Missing `@pytest.mark.asyncio` decorator
2. **Recommendations tests (23 failures)**: Service implementation issues, score calculation bugs, performance regressions
3. **E2E workflow tests (2 failures)**: Annotation endpoint 404 errors

## Category 1: Monitoring Tests (33 failures)

### Issue
All async test functions in `test_service.py` are missing the `@pytest.mark.asyncio` decorator, causing pytest to fail with "async def functions are not natively supported".

### Files Affected
- `backend/tests/modules/monitoring/test_service.py`

### Fix
Add `@pytest.mark.asyncio` decorator to all async test functions. The decorator is already imported but not applied to the test methods.

### Impact
- Low risk: Only adding missing decorators
- High confidence: Standard pytest-asyncio pattern

---

## Category 2: Recommendations Tests (23 failures)

### Issue 2.1: Router returning 500 errors (13 failures)
All router tests are getting 500 Internal Server Error instead of expected status codes.

**Root Cause**: Service implementation errors or missing dependencies in the recommendation service initialization.

**Files Affected**:
- `backend/tests/modules/recommendations/test_router.py`
- `backend/app/modules/recommendations/router.py`
- `backend/app/modules/recommendations/hybrid_service.py`

**Fix Strategy**:
1. Check service initialization in router
2. Add proper error handling
3. Verify all dependencies are available
4. Check if user authentication is properly mocked in tests

### Issue 2.2: Score calculation mismatch (1 failure)
`test_signal_fusion_with_multiple_strategies` expects score 0.7675 but gets 0.7877.

**Root Cause**: Signal fusion algorithm weights or calculation changed.

**Files Affected**:
- `backend/tests/modules/recommendations/test_hybrid_service.py`
- `backend/tests/golden_data/hybrid_recommendations.json`

**Fix Strategy**:
1. Review signal fusion implementation in `HybridRecommendationService._rank_candidates`
2. Either fix the algorithm or update golden data to match current implementation
3. Verify weights are applied correctly

### Issue 2.3: Performance regressions (3 failures)
Tests failing performance limits:
- `test_ranking_performance`: Expected <50ms
- `test_mmr_performance`: Expected <30ms  
- `test_novelty_boost_performance`: Expected <20ms

**Root Cause**: Algorithm inefficiencies or test environment issues.

**Fix Strategy**:
1. Profile the slow operations
2. Optimize database queries (add indexes, reduce N+1 queries)
3. Consider relaxing performance limits if current implementation is acceptable
4. Check if test fixtures are creating too much data

### Issue 2.4: Missing metadata fields (2 failures)
- `test_novelty_boosting_promotes_lesser_known`: Missing 'novelty_score' in candidate dict
- `test_full_recommendation_pipeline`: Missing 'gini_coefficient' in metadata

**Root Cause**: Service not populating expected fields.

**Files Affected**:
- `backend/app/modules/recommendations/hybrid_service.py`

**Fix Strategy**:
1. Ensure `_apply_novelty_boost` adds 'novelty_score' to each candidate
2. Ensure `generate_recommendations` calculates and includes 'gini_coefficient' in metadata
3. Review service implementation for missing field calculations

### Issue 2.5: Quality filtering not working (1 failure)
`test_quality_filtering_excludes_low_quality` expects 1 filtered result but gets 0.

**Root Cause**: Quality filtering logic not properly excluding low-quality resources.

**Files Affected**:
- `backend/app/modules/recommendations/hybrid_service.py`

**Fix Strategy**:
1. Review quality filtering implementation
2. Check if filters are being applied in the correct order
3. Verify min_quality threshold logic

### Issue 2.6: Graph traversal test (1 failure)
`test_graph_based_multihop_traversal` - UUID not found in expected results.

**Root Cause**: Test data setup or graph traversal logic issue.

**Files Affected**:
- `backend/tests/modules/recommendations/test_strategies.py`

**Fix Strategy**:
1. Review test data setup
2. Verify UUID mapping is correct
3. Check graph traversal implementation

---

## Category 3: Search Performance (1 failure)

### Issue
`test_search_latency_target` took 2089ms, expected <500ms.

**Root Cause**: Search operation too slow, likely due to:
- Missing database indexes
- Inefficient query patterns
- Large test dataset

**Files Affected**:
- `backend/tests/modules/search/test_three_way_hybrid.py`
- `backend/app/modules/search/` (various files)

**Fix Strategy**:
1. Add database indexes for search queries
2. Optimize hybrid search implementation
3. Reduce test dataset size
4. Consider relaxing performance limit if current speed is acceptable

---

## Category 4: E2E Workflow Tests (2 failures)

### Issue
Annotation workflow tests getting 404 errors when creating annotations.

**Root Cause**: Annotation endpoints not properly registered or route mismatch.

**Files Affected**:
- `backend/tests/test_annotation_workflow_e2e.py`
- `backend/tests/test_e2e_workflows.py`
- `backend/app/modules/annotations/router.py`

**Fix Strategy**:
1. Verify annotation routes are registered in main.py
2. Check route paths match test expectations
3. Ensure test client is using correct base URL
4. Verify resource exists before creating annotation

---

## Execution Priority

### Phase 1: Quick Wins (Low Risk, High Impact)
1. ✅ Fix monitoring test decorators (33 tests)
2. ✅ Fix E2E annotation 404 errors (2 tests)

### Phase 2: Service Fixes (Medium Risk, High Impact)
3. Fix recommendation router 500 errors (13 tests)
4. Fix missing metadata fields (2 tests)
5. Fix quality filtering (1 test)

### Phase 3: Algorithm Fixes (Medium Risk, Medium Impact)
6. Fix score calculation mismatch (1 test)
7. Fix graph traversal test (1 test)

### Phase 4: Performance Optimization (Low Priority)
8. Address performance regressions (4 tests)

---

## Testing Strategy

After each fix:
1. Run affected test file to verify fix
2. Run full test suite to check for regressions
3. Document any changes to expected behavior
4. Update golden data if algorithm changes are intentional

---

## Success Criteria

- All 58 failing tests pass
- No new test failures introduced
- Performance targets met or justified if relaxed
- Documentation updated for any behavior changes
