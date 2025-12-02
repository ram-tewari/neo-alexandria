# Design Document: Phase 12.6 Test Suite Fixes

## Overview

Phase 12.6 addresses the comprehensive test suite fixes needed to achieve >90% pass rate (from current 74.8%). The design focuses on systematic resolution of 242 failed tests and 175 error tests through domain object integration, fixture refactoring, mock updates, and performance optimization.

The core challenge is that Phase 12's domain-driven design refactoring introduced rich domain objects (QualityScore, ClassificationResult, SearchResult, Recommendation) but many tests still expect primitive dict representations. This design provides a systematic approach to update tests while maintaining backward compatibility and test isolation.

## Architecture

### High-Level Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Suite Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   API Tests  │    │Service Tests │    │  Unit Tests  │  │
│  │              │    │              │    │              │  │
│  │ - Domain obj │    │ - Domain obj │    │ - Domain obj │  │
│  │ - Serialized │    │ - Mocked     │    │ - Validated  │  │
│  │   responses  │    │   services   │    │   logic      │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         └───────────────────┴───────────────────┘           │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │  Shared Fixtures │                      │
│                    │                  │                      │
│                    │ - Domain object  │                      │
│                    │   factories      │                      │
│                    │ - Mock utilities │                      │
│                    │ - Test data      │                      │
│                    └────────┬─────────┘                      │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │  Domain Objects  │                      │
│                    │                  │                      │
│                    │ - QualityScore   │                      │
│                    │ - Classification │                      │
│                    │ - SearchResult   │                      │
│                    │ - Recommendation │                      │
│                    └──────────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Layers

1. **Test Layer**: API, Service, Unit, Integration tests
2. **Fixture Layer**: Shared test data factories and utilities
3. **Domain Layer**: Rich domain objects with validation
4. **Compatibility Layer**: Dict-like interfaces for backward compatibility

## Components and Interfaces

### 1. Domain Object Fixture Factories

**Purpose**: Provide reusable factories for creating domain objects in tests

**Location**: `backend/tests/conftest.py`

**Interface**:
```python
@pytest.fixture
def quality_score_factory():
    """Factory for creating QualityScore domain objects."""
    def _create(
        accuracy: float = 0.8,
        completeness: float = 0.7,
        consistency: float = 0.75,
        timeliness: float = 0.9,
        relevance: float = 0.85
    ) -> QualityScore:
        return QualityScore(
            accuracy=accuracy,
            completeness=completeness,
            consistency=consistency,
            timeliness=timeliness,
            relevance=relevance
        )
    return _create

@pytest.fixture
def classification_result_factory():
    """Factory for creating ClassificationResult domain objects."""
    def _create(
        predictions: List[Dict] = None,
        model_version: str = "test-model-v1",
        inference_time_ms: float = 50.0,
        resource_id: str = None
    ) -> ClassificationResult:
        if predictions is None:
            predictions = [
                ClassificationPrediction(
                    taxonomy_id="cat1",
                    confidence=0.9,
                    rank=1
                )
            ]
        return ClassificationResult(
            predictions=predictions,
            model_version=model_version,
            inference_time_ms=inference_time_ms,
            resource_id=resource_id
        )
    return _create

@pytest.fixture
def search_result_factory():
    """Factory for creating SearchResult domain objects."""
    # Similar pattern
    pass

@pytest.fixture
def recommendation_factory():
    """Factory for creating Recommendation domain objects."""
    # Similar pattern
    pass
```

### 2. Mock Utility Functions

**Purpose**: Provide utilities for creating properly configured mocks

**Location**: `backend/tests/conftest.py`

**Interface**:
```python
def create_quality_service_mock(quality_score: QualityScore = None):
    """Create a mock QualityService that returns domain objects."""
    mock = Mock(spec=QualityService)
    if quality_score is None:
        quality_score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.75,
            timeliness=0.9,
            relevance=0.85
        )
    mock.compute_quality.return_value = quality_score
    mock.assess_resource_quality.return_value = quality_score
    return mock

def create_classification_service_mock(result: ClassificationResult = None):
    """Create a mock MLClassificationService that returns domain objects."""
    mock = Mock(spec=MLClassificationService)
    if result is None:
        result = ClassificationResult(
            predictions=[
                ClassificationPrediction(
                    taxonomy_id="cat1",
                    confidence=0.9,
                    rank=1
                )
            ],
            model_version="test-v1",
            inference_time_ms=50.0
        )
    mock.predict.return_value = result
    mock.classify_resource.return_value = result
    return mock

# Similar utilities for SearchService, RecommendationService
```

### 3. Test Assertion Helpers

**Purpose**: Provide helper functions for common assertion patterns

**Location**: `backend/tests/conftest.py`

**Interface**:
```python
def assert_quality_score(
    actual: Union[QualityScore, Dict],
    expected_overall: float = None,
    expected_level: str = None,
    tolerance: float = 0.01
):
    """Assert quality score matches expectations."""
    if isinstance(actual, dict):
        actual_score = actual.get('overall_score')
        actual_level = actual.get('quality_level')
    else:
        actual_score = actual.overall_score()
        actual_level = actual.get_quality_level()
    
    if expected_overall is not None:
        assert abs(actual_score - expected_overall) < tolerance
    
    if expected_level is not None:
        assert actual_level == expected_level

def assert_classification_result(
    actual: Union[ClassificationResult, Dict],
    min_confidence: float = None,
    expected_count: int = None,
    expected_taxonomy_ids: List[str] = None
):
    """Assert classification result matches expectations."""
    if isinstance(actual, dict):
        predictions = actual.get('predictions', [])
    else:
        predictions = actual.predictions
    
    if expected_count is not None:
        assert len(predictions) == expected_count
    
    if min_confidence is not None:
        for pred in predictions:
            conf = pred.confidence if hasattr(pred, 'confidence') else pred['confidence']
            assert conf >= min_confidence
    
    if expected_taxonomy_ids is not None:
        actual_ids = [
            p.taxonomy_id if hasattr(p, 'taxonomy_id') else p['taxonomy_id']
            for p in predictions
        ]
        assert set(actual_ids) == set(expected_taxonomy_ids)
```

### 4. Backward Compatibility Layer

**Purpose**: Ensure domain objects work with existing dict-based code

**Implementation**: Already exists in domain objects via:
- `__getitem__()` method for dict-style access
- `.get()` method for safe access with defaults
- `.to_dict()` method for serialization
- `.from_dict()` classmethod for deserialization

**Example Usage**:
```python
# All these work with QualityScore domain object
quality_score['accuracy']  # Dict-style access
quality_score.get('accuracy', 0.0)  # Safe access
quality_score.accuracy  # Attribute access
quality_score.to_dict()  # Serialization
```

## Data Models

### Test Failure Categories

```python
@dataclass
class TestFailurePattern:
    """Represents a pattern of test failures."""
    category: str  # 'QualityScore', 'Assertion', 'Mock', 'Fixture', 'Type', 'UUID'
    failure_type: str  # 'AttributeError', 'AssertionError', 'TypeError', 'KeyError'
    count: int
    example_test: str
    example_error: str
    fix_approach: str
    priority: str  # 'Critical', 'High', 'Medium', 'Low'
    effort: str  # 'Small', 'Medium', 'Large'
    affected_files: List[str]
```

### Test Metrics

```python
@dataclass
class TestMetrics:
    """Test suite health metrics."""
    timestamp: datetime
    total_tests: int
    passing: int
    failing: int
    errors: int
    skipped: int
    pass_rate: float
    execution_time_seconds: float
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_tests': self.total_tests,
            'passing': self.passing,
            'failing': self.failing,
            'errors': self.errors,
            'skipped': self.skipped,
            'pass_rate': self.pass_rate,
            'execution_time_seconds': self.execution_time_seconds
        }
```

## Error Handling

### Test Failure Analysis

**Strategy**: Capture and categorize all test failures systematically

**Process**:
1. Run full test suite with detailed output: `pytest --tb=short -v > test_failures.txt 2>&1`
2. Parse output to extract failure patterns
3. Group failures by error type and affected component
4. Prioritize by impact and fix effort
5. Create failure pattern matrix

**Error Categories**:
- **AttributeError**: Domain object missing expected attribute
- **AssertionError**: Expected value doesn't match actual
- **TypeError**: Type mismatch (dict vs domain object)
- **KeyError**: Dict key access on domain object
- **ImportError**: Missing dependency or incorrect import
- **FixtureError**: Fixture setup/teardown issue

### Graceful Degradation

**Principle**: Tests should fail clearly with actionable error messages

**Implementation**:
```python
def safe_get_quality_score(obj: Union[QualityScore, Dict, None]) -> float:
    """Safely extract overall quality score from various formats."""
    if obj is None:
        return 0.0
    
    if isinstance(obj, QualityScore):
        return obj.overall_score()
    
    if isinstance(obj, dict):
        return obj.get('overall_score', 0.0)
    
    raise TypeError(
        f"Expected QualityScore or dict, got {type(obj).__name__}. "
        f"This test may need updating for domain object compatibility."
    )
```

## Testing Strategy

### Test Organization

```
backend/tests/
├── conftest.py                    # Shared fixtures and utilities
├── FIXTURES.md                    # Fixture documentation
├── PATTERNS.md                    # Test pattern guide
├── README.md                      # Test suite overview
│
├── api/                           # API endpoint tests
│   ├── conftest.py               # API-specific fixtures
│   └── test_*.py                 # API test files
│
├── services/                      # Service layer tests
│   ├── conftest.py               # Service-specific fixtures
│   └── test_*.py                 # Service test files
│
├── unit/                          # Unit tests
│   ├── conftest.py               # Unit test fixtures
│   ├── domain/                   # Domain object tests
│   └── phase*/                   # Phase-specific tests
│
├── integration/                   # Integration tests
│   ├── conftest.py               # Integration fixtures
│   └── test_*.py                 # Integration test files
│
├── performance/                   # Performance tests
│   └── test_*.py                 # Performance benchmarks
│
└── standalone/                    # Standalone tests
    └── test_*.py                 # Self-contained tests
```

### Test Execution Strategy

**Phase 2.1 (Week 1) - Critical Fixes**:
```bash
# Run API tests
pytest tests/api/ -v

# Run service tests
pytest tests/services/ -v

# Run integration tests
pytest tests/integration/ -v
```

**Phase 2.2 (Week 2) - High Priority**:
```bash
# Run all tests except known broken
pytest --ignore=tests/unit/phase8_classification/test_active_learning.py -v
```

**Phase 2.3 (Week 3) - Medium Priority**:
```bash
# Run unit tests
pytest tests/unit/ -v

# Run domain tests
pytest tests/domain/ -v
```

**Phase 2.4 (Week 4) - Optimization**:
```bash
# Run with performance profiling
pytest --durations=20

# Run with parallel execution
pytest -n auto

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test Isolation

**Principle**: Each test should run independently

**Strategies**:
1. **Database Isolation**: Use transaction rollback or in-memory SQLite
2. **Mock Isolation**: Reset mocks between tests
3. **Fixture Scope**: Use appropriate fixture scopes (function, class, module, session)
4. **State Cleanup**: Ensure fixtures clean up after themselves

**Example**:
```python
@pytest.fixture(scope="function")
def db_session():
    """Provide a database session with transaction rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
```

### Performance Optimization

**ML Model Caching**:
```python
@pytest.fixture(scope="module")
def ml_model():
    """Load ML model once per test module."""
    model = load_model("BAAI/bge-m3")
    yield model
    # Cleanup if needed
```

**Database Optimization**:
```python
@pytest.fixture(scope="session")
def in_memory_db():
    """Use in-memory SQLite for unit tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine
```

**Parallel Execution**:
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Implementation Phases

### Phase 2.1: Critical Fixes (Week 1)

**Goal**: Fix QualityScore integration issues
**Target**: 85% pass rate

**Tasks**:
1. Analyze test failures and create failure pattern matrix
2. Update ResourceService quality score handling
3. Update API response serialization
4. Fix QualityService return types
5. Create domain object fixture factories
6. Run critical test suites

**Success Criteria**:
- API tests >90% passing
- Service tests >85% passing
- Integration tests >80% passing

### Phase 2.2: High Priority Fixes (Week 2)

**Goal**: Fix assertion mismatches and mock objects
**Target**: 88% pass rate

**Tasks**:
1. Identify and fix assertion mismatch patterns
2. Create domain object mock utilities
3. Update service mocks to return domain objects
4. Fix integration test failures
5. Run high priority test suite

**Success Criteria**:
- All tests except known broken >88% passing
- Critical paths verified passing

### Phase 2.3: Medium Priority Fixes (Week 3)

**Goal**: Fix remaining fixture and type issues
**Target**: 90% pass rate

**Tasks**:
1. Audit and refactor duplicate fixtures
2. Resolve AttributeError, TypeError, KeyError issues
3. Update unit tests for domain objects
4. Add comprehensive domain object tests
5. Run medium priority test suite

**Success Criteria**:
- Unit tests >90% passing
- Domain tests 100% passing
- Overall pass rate >90%

### Phase 2.4: Cleanup and Optimization (Week 4)

**Goal**: Optimize performance and finalize documentation
**Target**: >90% pass rate, <15 min execution

**Tasks**:
1. Fix SQLAlchemy UUID issues
2. Optimize test performance (caching, parallel execution)
3. Update test documentation (FIXTURES.md, PATTERNS.md)
4. Update CI configuration
5. Create test health dashboard
6. Final validation

**Success Criteria**:
- Pass rate >90%
- Failed tests <100
- Error tests <20
- Execution time <15 minutes
- Zero import errors
- All critical tests passing

## Monitoring and Metrics

### Test Metrics Collection

**Script**: `backend/scripts/test_metrics.py`

**Functionality**:
```python
def collect_test_metrics() -> TestMetrics:
    """Run tests and collect metrics."""
    result = pytest.main([
        '--tb=no',
        '-q',
        '--json-report',
        '--json-report-file=test_results.json'
    ])
    
    with open('test_results.json') as f:
        data = json.load(f)
    
    return TestMetrics(
        timestamp=datetime.now(),
        total_tests=data['summary']['total'],
        passing=data['summary']['passed'],
        failing=data['summary']['failed'],
        errors=data['summary']['error'],
        skipped=data['summary']['skipped'],
        pass_rate=data['summary']['passed'] / data['summary']['total'],
        execution_time_seconds=data['duration']
    )
```

### CI Integration

**GitHub Actions Workflow**:
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest-xdist pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest --ignore=tests/unit/phase8_classification/test_active_learning.py \
                 --tb=short \
                 -v \
                 --cov=app \
                 --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./backend/coverage.xml
      
      - name: Check pass rate
        run: |
          python backend/scripts/test_metrics.py --check-threshold 0.90
```

### Weekly Reporting

**Report Format** (Markdown):
```markdown
# Test Suite Health Report - Week of 2025-11-18

## Summary
- **Pass Rate**: 91.2% (↑ 16.4% from baseline)
- **Total Tests**: 1,750
- **Passing**: 1,596 (+287)
- **Failing**: 98 (-144)
- **Errors**: 18 (-157)
- **Execution Time**: 12.5 minutes (↓ 15.5 min)

## Progress by Category
- ✅ QualityScore Integration: 100% complete (80/80 tests fixed)
- ✅ Assertion Mismatches: 100% complete (60/60 tests fixed)
- ✅ Mock Updates: 95% complete (38/40 tests fixed)
- 🔄 Fixture Issues: 85% complete (26/30 tests fixed)
- 🔄 Type Errors: 80% complete (16/20 tests fixed)

## Next Week Focus
- Complete remaining fixture refactoring
- Fix final type errors
- Optimize slow tests
- Update documentation
```

## Documentation

### FIXTURES.md

**Purpose**: Document all shared fixtures

**Structure**:
```markdown
# Test Fixtures Guide

## Domain Object Factories

### quality_score_factory
Creates QualityScore domain objects for testing.

**Usage**:
```python
def test_quality_assessment(quality_score_factory):
    score = quality_score_factory(accuracy=0.9, completeness=0.8)
    assert score.overall_score() > 0.8
```

**Parameters**:
- accuracy (float): Accuracy dimension (default: 0.8)
- completeness (float): Completeness dimension (default: 0.7)
- ...

[Continue for all fixtures]
```

### PATTERNS.md

**Purpose**: Document common test patterns

**Structure**:
```markdown
# Test Patterns Guide

## Testing Domain Objects

### Pattern: Create and Validate
```python
def test_domain_object_validation(quality_score_factory):
    # Arrange
    score = quality_score_factory(accuracy=0.9)
    
    # Act & Assert
    assert score.accuracy == 0.9
    assert score.overall_score() > 0.7
```

### Pattern: Mock Service Returning Domain Object
```python
def test_service_with_mock(mocker):
    # Arrange
    mock_service = create_quality_service_mock()
    
    # Act
    result = mock_service.compute_quality(resource)
    
    # Assert
    assert isinstance(result, QualityScore)
    assert result.overall_score() > 0.0
```

[Continue with more patterns]
```

## Success Criteria

1. **Pass Rate**: >90% (from 74.8%)
2. **Failed Tests**: <100 (from 242)
3. **Error Tests**: <20 (from 175)
4. **Execution Time**: <15 minutes (from 28 minutes)
5. **Import Errors**: 0 (from 1)
6. **Critical Tests**: 100% passing
7. **Documentation**: Complete (FIXTURES.md, PATTERNS.md, updated README.md)
8. **CI**: Updated and passing
9. **Metrics**: Tracking in place with weekly reports
10. **Code Quality**: All tests follow established patterns
