# Test Failure Pattern Matrix

**Generated**: 2025-11-18  
**Baseline Pass Rate**: 74.8% (1309/1750 tests passing)  
**Target Pass Rate**: >90%

## Executive Summary

The test suite has **242 failed tests** and **175 error tests** across 13 distinct failure patterns. The primary root cause is the Phase 12 domain-driven design refactoring that introduced rich domain objects (QualityScore, ClassificationResult, SearchResult, Recommendation) while many tests still expect primitive dict representations.

### Key Findings

1. **Critical Issues** (31 tests): QualityScore integration and API endpoint serialization
2. **High Priority** (207 tests): Domain object integration across Search, Classification, Recommendations, and Graph/Discovery
3. **Medium Priority** (7 tests): Database schema, compatibility layers, and Celery tasks
4. **Low Priority** (25 tests): Performance tests, training/ML, and domain validation

### Recommended Fix Order

1. **Week 1 (Critical)**: QualityScore integration + API endpoints → Target 85% pass rate
2. **Week 2 (High Priority)**: Fixture/import errors + assertion mismatches → Target 88% pass rate
3. **Week 3 (Medium Priority)**: Remaining domain object updates → Target 90% pass rate
4. **Week 4 (Cleanup)**: Performance optimization + documentation → Target >90% pass rate

---

## Failure Pattern Matrix

| # | Category | Type | Count | Priority | Effort | Impact | Fix Approach |
|---|----------|------|-------|----------|--------|--------|--------------|
| 1 | QualityScore Integration | AssertionError / AttributeError | 24 | **Critical** | Medium | High | Update tests to handle QualityScore domain objects, use `.overall_score()` method |
| 2 | API Endpoints | AssertionError | 7 | **Critical** | Small | High | Update API tests to handle domain object serialization with `.to_dict()` |
| 3 | Recommendation Integration | ImportError / FixtureError | 65 | **High** | Small | High | Fix fixture dependencies and imports for recommendation tests |
| 4 | Integration Tests | ImportError / FixtureError | 42 | **High** | Medium | High | Fix integration test fixtures and dependencies |
| 5 | Classification Integration | AssertionError / TypeError | 41 | **High** | Medium | High | Update tests to handle ClassificationResult domain objects |
| 6 | Search Integration | AssertionError / TypeError | 36 | **High** | Medium | High | Update tests to handle SearchResult domain objects |
| 7 | Graph/Discovery Integration | ImportError / FixtureError | 23 | **High** | Small | Medium | Fix fixture dependencies and imports for graph/discovery tests |
| 8 | Database Schema | AssertionError | 3 | **Medium** | Small | Low | Update database schema tests and initialization helpers |
| 9 | Discovery Hypothesis Compatibility | AssertionError | 3 | **Medium** | Small | Low | Update compatibility layer for new field names |
| 10 | Celery Tasks | AssertionError | 1 | **Medium** | Small | Low | Update Celery task tests for domain objects |
| 11 | Performance Tests | ImportError / FixtureError | 13 | **Low** | Small | Low | Fix performance test fixtures and dependencies |
| 12 | Training/ML | AssertionError / ImportError | 10 | **Low** | Medium | Low | Fix ML model mocking and training test setup |
| 13 | Domain Validation | ValidationError | 2 | **Low** | Small | Low | Update domain object validation logic |

**Total**: 270 failing/error tests across 13 patterns

---

## Detailed Pattern Analysis

### Pattern 1: QualityScore Integration (Critical)

**Count**: 24 tests  
**Priority**: Critical  
**Effort**: Medium  
**Impact**: High - Affects core quality assessment functionality

#### Problem Description
Tests expect `quality_score` to be a dict with keys like `overall_score`, but the code now returns `QualityScore` domain objects. Tests fail with:
- `KeyError: 'overall_score'` when accessing `quality_score['overall_score']`
- `AttributeError` when calling dict methods on domain objects
- Assertion failures due to comparing dict vs domain object

#### Example Test
```
tests/unit/phase9_quality/test_quality_service.py::TestContentQualityAnalyzer::test_text_readability
```

#### Example Error
```python
# Test expects:
assert result['quality_score']['overall_score'] > 0.7

# But receives:
result['quality_score'] = QualityScore(accuracy=0.8, completeness=0.7, ...)
# Causes KeyError: 'overall_score'
```

#### Fix Approach
1. Update assertions to use `quality_score.overall_score()` method
2. Update dimension access to use `quality_score.accuracy` or `quality_score['accuracy']`
3. Use `quality_score.to_dict()` for serialization where needed
4. Create `quality_score_factory` fixture for test data generation
5. Create `assert_quality_score()` helper for common assertions

#### Affected Files (11 files)
- `tests/unit/phase9_quality/test_quality_service.py` (7 tests)
- `tests/unit/phase9_quality/test_degradation_monitoring.py` (1 test)
- `tests/unit/test_celery_tasks.py` (1 test)
- `tests/integration/phase9_quality/test_quality_integration.py` (2 tests)
- `tests/integration/phase9_quality/test_quality_endpoints_simple.py` (1 test)
- `tests/unit/phase11_recommendations/test_hybrid_recommendations.py` (1 test)
- `tests/integration/phase2_curation/test_curation_endpoints.py` (1 test)
- `tests/unit/phase2_curation/test_curation_service.py` (1 test)
- `tests/integration/workflows/test_integration.py` (1 test)
- `tests/ml_benchmarks/test_search_quality_metrics.py` (1 test)
- `tests/integration/phase9_quality/test_quality_api_endpoints.py` (7 tests)

#### Batch Fix Strategy
```bash
# Search for all quality_score dict access patterns
grep -r "quality_score\['overall_score'\]" tests/
grep -r "quality_score\['accuracy'\]" tests/

# Replace with domain object access
# quality_score['overall_score'] → quality_score.overall_score()
# quality_score['accuracy'] → quality_score.accuracy
```

---

### Pattern 2: API Endpoints (Critical)

**Count**: 7 tests  
**Priority**: Critical  
**Effort**: Small  
**Impact**: High - Affects API response contracts

#### Problem Description
API endpoints return domain objects but tests expect serialized dicts. The API routers need to call `.to_dict()` on domain objects before returning responses.

#### Example Test
```
tests/api/test_phase2_curation_api.py::TestResourcesCRUDAndList::test_update_resource_partial
```

#### Example Error
```python
# API returns:
response.json()['quality_score'] = QualityScore object (not JSON serializable)

# Test expects:
response.json()['quality_score'] = {'overall_score': 0.8, 'accuracy': 0.9, ...}
```

#### Fix Approach
1. Update API routers to call `.to_dict()` on domain objects before response
2. Update Pydantic response models to accept domain objects
3. Update tests to verify serialized format
4. Ensure backward compatibility with existing API contracts

#### Affected Files (2 files)
- `tests/api/test_phase2_curation_api.py` (1 test)
- `tests/integration/phase10_graph_intelligence/test_phase10_discovery_api.py` (6 tests)

#### Code Fix Example
```python
# In API router:
@router.put("/resources/{resource_id}")
async def update_resource(resource_id: str, ...):
    resource = await resource_service.update_resource(resource_id, ...)
    
    # Add serialization before response
    if hasattr(resource.quality_score, 'to_dict'):
        resource.quality_score = resource.quality_score.to_dict()
    
    return resource
```

---

### Pattern 3: Recommendation Integration (High Priority)

**Count**: 65 tests  
**Priority**: High  
**Effort**: Small  
**Impact**: High - Blocks entire recommendation test suite

#### Problem Description
Recommendation tests have fixture or import errors preventing them from running. These are ERROR tests, not FAILED tests, meaning they don't even execute.

#### Example Test
```
tests/integration/phase11_recommendations/test_recommendation_api.py::TestRecommendationsEndpoint::test_get_recommendations_default
```

#### Example Error
```
ERROR at collection - ImportError or FixtureNotFoundError
```

#### Fix Approach
1. Identify missing fixtures in `tests/integration/phase11_recommendations/conftest.py`
2. Fix import paths for recommendation services
3. Create mock utilities for recommendation services
4. Ensure database fixtures are properly scoped

#### Affected Files (5 files)
- `tests/integration/phase11_recommendations/test_recommendation_api.py` (29 tests)
- `tests/unit/phase11_recommendations/test_collaborative_filtering.py` (17 tests)
- `tests/integration/phase5_graph/test_phase55_recommendations.py` (13 tests)
- `tests/unit/phase9_quality/test_recommendation_quality_integration.py` (6 tests)
- `tests/integration/phase10_graph_intelligence/test_phase10_integration.py` (5 tests - overlap with Pattern 7)

#### Investigation Steps
```bash
# Run single test with verbose output to see exact error
pytest tests/integration/phase11_recommendations/test_recommendation_api.py::TestRecommendationsEndpoint::test_get_recommendations_default -vv

# Check for missing fixtures
grep -r "@pytest.fixture" tests/integration/phase11_recommendations/
```

---

### Pattern 4: Integration Tests (High Priority)

**Count**: 42 tests  
**Priority**: High  
**Effort**: Medium  
**Impact**: High - Affects end-to-end workflows

#### Problem Description
Integration tests have fixture or import errors, particularly in phase6 (citations), phase9 (quality), and phase1 (ingestion) tests.

#### Example Test
```
tests/integration/phase9_quality/test_quality_api_endpoints.py::TestQualityDetailsEndpoint::test_get_quality_details_success
```

#### Fix Approach
1. Fix fixture dependencies in integration test conftest files
2. Update fixtures to create domain objects
3. Ensure proper database session management
4. Fix service mocking in integration tests

#### Affected Files (4 files)
- `tests/integration/phase9_quality/test_quality_api_endpoints.py` (28 tests)
- `tests/integration/phase9_quality/test_quality_workflows_integration.py` (8 tests)
- `tests/integration/phase6_citations/test_phase6_5_scholarly.py` (7 tests)
- `tests/integration/phase1_ingestion/test_resource_ingestion_classification.py` (2 tests - overlap with Pattern 5)

---

### Pattern 5: Classification Integration (High Priority)

**Count**: 41 tests  
**Priority**: High  
**Effort**: Medium  
**Impact**: High - Affects ML classification functionality

#### Problem Description
Tests expect classification results as dicts but receive `ClassificationResult` domain objects with nested `ClassificationPrediction` objects.

#### Example Test
```
tests/unit/phase8_classification/test_taxonomy_classification_standalone.py::test_classify_resource
```

#### Example Error
```python
# Test expects:
result['predictions'][0]['confidence'] > 0.8

# But receives:
result = ClassificationResult(
    predictions=[ClassificationPrediction(taxonomy_id='cat1', confidence=0.9, rank=1)]
)
# Causes TypeError or AttributeError
```

#### Fix Approach
1. Update tests to handle `ClassificationResult` domain objects
2. Access predictions via `result.predictions` not `result['predictions']`
3. Access prediction fields via `pred.confidence` not `pred['confidence']`
4. Create `classification_result_factory` fixture
5. Create `assert_classification_result()` helper

#### Affected Files (14 files)
- `tests/unit/phase8_classification/test_taxonomy_classification_standalone.py` (4 tests)
- `tests/unit/phase8_classification/test_ml_classification_service.py` (5 tests)
- `tests/integration/phase8_classification/test_classification_endpoints.py` (4 tests)
- `tests/integration/phase8_classification/test_phase8_5_integration.py` (5 tests)
- `tests/integration/phase8_classification/test_phase8_api_endpoints.py` (1 test)
- And 9 more files...

---

### Pattern 6: Search Integration (High Priority)

**Count**: 36 tests  
**Priority**: High  
**Effort**: Medium  
**Impact**: High - Affects search functionality

#### Problem Description
Tests expect search results as dicts but receive `SearchResult` domain objects.

#### Example Test
```
tests/api/test_phase3_search_api.py::test_post_search_basic_total_and_items
```

#### Example Error
```python
# Test expects:
results['items'][0]['score'] > 0.5

# But receives:
results = SearchResults(
    results=[SearchResult(resource_id='123', score=0.9, rank=1)]
)
```

#### Fix Approach
1. Update tests to handle `SearchResult` domain objects
2. Access results via `results.results` not `results['items']`
3. Create `search_result_factory` fixture
4. Create `assert_search_result()` helper

#### Affected Files (14 files)
- `tests/api/test_phase3_search_api.py` (4 tests)
- `tests/integration/phase3_search/test_enhanced_search_api.py` (3 tests)
- `tests/integration/phase3_search/test_phase3_search_api.py` (3 tests)
- `tests/services/test_search_service.py` (6 tests)
- And 10 more files...

---

### Pattern 7: Graph/Discovery Integration (High Priority)

**Count**: 23 tests  
**Priority**: High  
**Effort**: Small  
**Impact**: Medium - Affects graph intelligence features

#### Problem Description
Graph and discovery tests have fixture or import errors.

#### Example Test
```
tests/integration/phase10_graph_intelligence/test_phase10_integration.py::TestEndToEndDiscoveryWorkflow::test_complete_workflow
```

#### Fix Approach
1. Fix fixture dependencies in phase10 integration tests
2. Ensure graph service mocks are properly configured
3. Fix import paths for graph-related services

#### Affected Files (3 files)
- `tests/integration/phase10_graph_intelligence/test_phase10_integration.py` (7 tests)
- `tests/integration/phase5_graph/test_phase55_recommendations.py` (13 tests - overlap with Pattern 3)
- `tests/unit/phase9_quality/test_recommendation_quality_integration.py` (6 tests - overlap with Pattern 3)

---

### Patterns 8-13: Medium and Low Priority

These patterns have fewer tests and lower impact. They should be addressed after the critical and high-priority patterns are fixed.

**Pattern 8: Database Schema** (3 tests, Medium priority)
- Fix database initialization helper tests
- Update schema verification tests

**Pattern 9: Discovery Hypothesis Compatibility** (3 tests, Medium priority)
- Update backward compatibility layer for renamed fields
- Fix property accessors and setters

**Pattern 10: Celery Tasks** (1 test, Medium priority)
- Update Celery task test to handle QualityScore domain object

**Pattern 11: Performance Tests** (13 tests, Low priority)
- Fix performance test fixtures
- These can be addressed last as they don't affect core functionality

**Pattern 12: Training/ML** (10 tests, Low priority)
- Fix ML model mocking in training tests
- Update hyperparameter search tests

**Pattern 13: Domain Validation** (2 tests, Low priority)
- Fix SearchQuery validation to properly raise ValidationError for empty/whitespace queries

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1) - Target 85% Pass Rate

**Goal**: Fix QualityScore integration and API endpoints (31 tests)

**Tasks**:
1. Create domain object fixture factories in `backend/tests/conftest.py`
2. Create assertion helper functions
3. Fix QualityScore API integration in ResourceService
4. Update API routers to serialize domain objects
5. Batch fix QualityScore assertion errors (24 tests)
6. Fix API endpoint tests (7 tests)

**Expected Outcome**: +31 passing tests → 1340/1750 = 76.6% → 85% (with some cascading fixes)

### Phase 2: High Priority Fixes (Week 2) - Target 88% Pass Rate

**Goal**: Fix fixture/import errors and domain object integration (207 tests)

**Tasks**:
1. Fix recommendation test fixtures (65 tests)
2. Fix integration test fixtures (42 tests)
3. Fix graph/discovery test fixtures (23 tests)
4. Update classification service mocks (41 tests)
5. Update search service mocks (36 tests)

**Expected Outcome**: +207 passing tests → 1547/1750 = 88.4%

### Phase 3: Medium Priority Fixes (Week 3) - Target 90% Pass Rate

**Goal**: Fix remaining domain object and compatibility issues (7 tests)

**Tasks**:
1. Fix database schema tests (3 tests)
2. Fix discovery hypothesis compatibility (3 tests)
3. Fix Celery task test (1 test)

**Expected Outcome**: +7 passing tests → 1554/1750 = 88.8% → 90% (with cascading fixes)

### Phase 4: Cleanup and Optimization (Week 4) - Target >90% Pass Rate

**Goal**: Fix low-priority tests and optimize performance (25 tests)

**Tasks**:
1. Fix performance test fixtures (13 tests)
2. Fix training/ML tests (10 tests)
3. Fix domain validation tests (2 tests)
4. Optimize test execution time
5. Enable parallel test execution
6. Update documentation

**Expected Outcome**: +25 passing tests → 1579/1750 = 90.2% → >90%

---

## Success Metrics

### Baseline (Current State)
- **Pass Rate**: 74.8% (1309/1750)
- **Failed Tests**: 242
- **Error Tests**: 175
- **Execution Time**: ~22 minutes

### Target (After Phase 12.6)
- **Pass Rate**: >90% (>1575/1750)
- **Failed Tests**: <100
- **Error Tests**: <20
- **Execution Time**: <15 minutes

### Milestones
- **Week 1**: 85% pass rate (Critical fixes complete)
- **Week 2**: 88% pass rate (High priority fixes complete)
- **Week 3**: 90% pass rate (Medium priority fixes complete)
- **Week 4**: >90% pass rate (All fixes complete + optimization)

---

## Risk Assessment

### High Risk
- **QualityScore Integration**: Affects many downstream tests. Must be fixed first.
- **Fixture Dependencies**: Circular dependencies could block multiple test suites.

### Medium Risk
- **API Contract Changes**: Must maintain backward compatibility.
- **Performance Regression**: Fixing tests shouldn't slow down execution.

### Low Risk
- **Domain Validation**: Isolated to specific domain object tests.
- **Training/ML Tests**: Can be addressed last without blocking other work.

---

## Appendix: Quick Reference Commands

### Run Specific Pattern Tests
```bash
# Pattern 1: QualityScore Integration
pytest tests/unit/phase9_quality/test_quality_service.py -v

# Pattern 2: API Endpoints
pytest tests/api/test_phase2_curation_api.py::TestResourcesCRUDAndList::test_update_resource_partial -v

# Pattern 3: Recommendation Integration
pytest tests/integration/phase11_recommendations/ -v

# Pattern 5: Classification Integration
pytest tests/unit/phase8_classification/test_taxonomy_classification_standalone.py -v

# Pattern 6: Search Integration
pytest tests/api/test_phase3_search_api.py -v
```

### Search for Patterns
```bash
# Find all quality_score dict access
grep -r "quality_score\['overall_score'\]" tests/

# Find all classification result dict access
grep -r "result\['predictions'\]" tests/

# Find all search result dict access
grep -r "results\['items'\]" tests/
```

### Generate Updated Report
```bash
cd backend
python scripts/analyze_test_failures.py
```
