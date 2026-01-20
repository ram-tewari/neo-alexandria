# Design Document: Phase 14.6 - Full Test Suite Expansion

## Overview

Phase 14.6 extends the Anti-Gaslighting test architecture to provide comprehensive coverage across all 13 modules in Neo Alexandria 2.0. The design implements four distinct testing layers: Golden Logic Tests, Edge Case & Pattern Tests, Integration Tests, and Performance Regression Tests.

## Architecture

### Test Layer Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Golden Logic Tests                                │
│ - Validates complex algorithms against immutable JSON      │
│ - Uses assert_against_golden() exclusively                 │
│ - No inline expected values                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Edge Case & Pattern Tests                         │
│ - Standard unit tests for boundary conditions              │
│ - Uses pytest.raises for error cases                       │
│ - Validates design pattern compliance                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Integration Tests                                 │
│ - Verifies API contracts and database persistence          │
│ - Uses TestClient and db_session fixtures                  │
│ - Validates event bus emissions                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Performance Regression Tests                      │
│ - Enforces strict execution time limits                    │
│ - Uses @performance_limit decorator                        │
│ - Fails on regression, not adjustable                      │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
backend/tests/
├── __init__.py
├── conftest.py                          # Enhanced fixtures
├── protocol.py                          # Golden data assertions (existing)
├── performance.py                       # NEW: Performance decorator
├── golden_data/                         # Immutable truth sources
│   ├── quality_scoring.json             # Existing
│   ├── search_ranking.json              # Existing
│   ├── resource_ingestion.json          # Existing
│   ├── taxonomy_prediction.json         # NEW
│   ├── graph_algorithms.json            # NEW
│   ├── scholarly_parsing.json           # NEW
│   ├── collections_logic.json           # NEW
│   ├── recommendations_ranking.json     # NEW
│   ├── annotations_search.json          # NEW
│   └── authority_tree.json              # NEW
├── modules/                             # Module-specific tests
│   ├── taxonomy/
│   │   ├── __init__.py
│   │   ├── test_classification.py       # Golden Logic
│   │   ├── test_tree_logic.py           # Edge Cases
│   │   └── test_flow.py                 # Integration
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── test_pagerank.py             # Golden Logic + Performance
│   │   └── test_traversal.py            # Edge Cases + Performance
│   ├── collections/
│   │   ├── __init__.py
│   │   ├── test_aggregation.py          # Golden Logic
│   │   ├── test_lifecycle.py            # Integration + Events
│   │   └── test_constraints.py          # Edge Cases
│   ├── scholarly/
│   │   ├── __init__.py
│   │   ├── test_latex_parsing.py        # Golden Logic
│   │   └── test_metadata_extraction.py  # Integration
│   ├── curation/
│   │   ├── __init__.py
│   │   ├── test_batch_operations.py     # Integration
│   │   └── test_review_workflow.py      # Edge Cases
│   ├── recommendations/
│   │   ├── __init__.py
│   │   ├── test_ncf_ranking.py          # Golden Logic + Performance
│   │   ├── test_content_similarity.py   # Golden Logic
│   │   └── test_hybrid_fusion.py        # Integration
│   ├── annotations/
│   │   ├── __init__.py
│   │   ├── test_text_ranges.py          # Edge Cases
│   │   └── test_semantic_search.py      # Golden Logic
│   ├── authority/
│   │   ├── __init__.py
│   │   ├── test_tree_operations.py      # Edge Cases
│   │   └── test_hierarchy.py            # Integration
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── test_health_checks.py        # Integration
│   │   └── test_metrics.py              # Golden Logic
│   ├── resources/                       # Existing
│   ├── search/                          # Existing
│   └── quality/                         # Existing
├── properties/                          # Property-based tests
│   └── test_protocol_properties.py      # Existing
└── test_template.py                     # NEW: Universal template
```

## Components and Interfaces

### 1. Performance Testing Infrastructure

#### performance.py Module

```python
"""Performance regression testing infrastructure."""
import time
import functools
from typing import Callable, Any

class PerformanceRegressionError(AssertionError):
    """Raised when execution time exceeds limit."""
    pass

def performance_limit(max_ms: int) -> Callable:
    """
    Decorator to enforce strict execution time limits.
    
    Args:
        max_ms: Maximum allowed execution time in milliseconds
        
    Raises:
        PerformanceRegressionError: If execution exceeds max_ms
        
    Example:
        @performance_limit(max_ms=50)
        def test_fast_operation():
            # Test code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            actual_ms = (end_time - start_time) * 1000
            
            if actual_ms > max_ms:
                raise PerformanceRegressionError(
                    f"PERFORMANCE REGRESSION DETECTED\n"
                    f"Function: {func.__name__}\n"
                    f"Expected: <{max_ms}ms\n"
                    f"Actual: {actual_ms:.2f}ms\n"
                    f"Regression: {actual_ms - max_ms:.2f}ms\n"
                    f"\n"
                    f"DO NOT INCREASE THE TIMEOUT\n"
                    f"This indicates a performance regression in the implementation.\n"
                    f"Fix the implementation, not the test."
                )
            
            return result
        return wrapper
    return decorator
```

### 2. Enhanced Test Fixtures

#### conftest.py Additions

```python
"""Enhanced test fixtures for Phase 14.6."""
import pytest
from unittest.mock import Mock, MagicMock
from typing import Generator, Any

@pytest.fixture(scope="session")
def mock_ml_inference() -> Generator[Mock, None, None]:
    """
    Mock ML model inference for all tests.
    
    Mocks:
        - sentence_transformers.SentenceTransformer.encode
        - transformers.pipeline.__call__
        
    Returns:
        Mock object with configurable return values
    """
    with patch('sentence_transformers.SentenceTransformer') as mock_st, \
         patch('transformers.pipeline') as mock_pipeline:
        
        # Configure SentenceTransformer mock
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [[0.1, 0.2, 0.3]]  # Default embedding
        mock_st.return_value = mock_encoder
        
        # Configure transformers pipeline mock
        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"label": "LABEL_0", "score": 0.95}]
        mock_pipeline.return_value = mock_pipe
        
        yield {
            "sentence_transformer": mock_encoder,
            "pipeline": mock_pipe
        }

@pytest.fixture
def mock_embedding_service(mock_ml_inference: dict) -> Mock:
    """
    Mock embedding service that uses mock_ml_inference.
    
    Returns:
        Mock embedding service with generate_embedding method
    """
    mock_service = Mock()
    mock_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
    return mock_service

@pytest.fixture
def create_test_category(db_session):
    """
    Factory fixture for creating test taxonomy categories.
    
    Returns:
        Function that creates and returns a Category instance
    """
    def _create(name: str = "Test Category", parent_id: int = None) -> Any:
        from app.modules.taxonomy.model import Category
        category = Category(name=name, parent_id=parent_id)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category
    return _create

@pytest.fixture
def create_test_collection(db_session):
    """
    Factory fixture for creating test collections.
    
    Returns:
        Function that creates and returns a Collection instance
    """
    def _create(name: str = "Test Collection", description: str = None) -> Any:
        from app.modules.collections.model import Collection
        collection = Collection(name=name, description=description)
        db_session.add(collection)
        db_session.commit()
        db_session.refresh(collection)
        return collection
    return _create

@pytest.fixture
def create_test_annotation(db_session, create_test_resource):
    """
    Factory fixture for creating test annotations.
    
    Returns:
        Function that creates and returns an Annotation instance
    """
    def _create(
        resource_id: int = None,
        text: str = "Test annotation",
        start_offset: int = 0,
        end_offset: int = 10
    ) -> Any:
        from app.modules.annotations.model import Annotation
        
        if resource_id is None:
            resource = create_test_resource()
            resource_id = resource.id
        
        annotation = Annotation(
            resource_id=resource_id,
            text=text,
            start_offset=start_offset,
            end_offset=end_offset
        )
        db_session.add(annotation)
        db_session.commit()
        db_session.refresh(annotation)
        return annotation
    return _create
```

### 3. Golden Data Schemas

#### taxonomy_prediction.json

```json
{
  "cases": {
    "machine_learning_paper": {
      "input": {
        "text": "This paper presents a novel deep learning approach for image classification using convolutional neural networks.",
        "embedding": [0.12, 0.45, 0.78, 0.23, 0.56]
      },
      "expected": {
        "category_id": 42,
        "category_name": "Machine Learning",
        "confidence": 0.92,
        "path": ["Computer Science", "Artificial Intelligence", "Machine Learning"]
      }
    },
    "quantum_physics_paper": {
      "input": {
        "text": "We investigate quantum entanglement in multi-particle systems using Bell inequality violations.",
        "embedding": [0.89, 0.12, 0.34, 0.67, 0.45]
      },
      "expected": {
        "category_id": 15,
        "category_name": "Quantum Physics",
        "confidence": 0.88,
        "path": ["Physics", "Quantum Mechanics", "Quantum Physics"]
      }
    }
  }
}
```

#### graph_algorithms.json

```json
{
  "cases": {
    "simple_citation_network": {
      "input": {
        "nodes": ["A", "B", "C", "D"],
        "edges": [
          {"from": "A", "to": "B"},
          {"from": "A", "to": "C"},
          {"from": "B", "to": "C"},
          {"from": "C", "to": "D"}
        ]
      },
      "expected": {
        "pagerank": {
          "A": 0.15,
          "B": 0.21,
          "C": 0.39,
          "D": 0.25
        },
        "tolerance": 0.01
      }
    },
    "disconnected_node": {
      "input": {
        "nodes": ["A", "B", "C"],
        "edges": [
          {"from": "A", "to": "B"}
        ]
      },
      "expected": {
        "related_to_C": [],
        "pagerank": {
          "A": 0.15,
          "B": 0.42,
          "C": 0.43
        }
      }
    }
  }
}
```

#### scholarly_parsing.json

```json
{
  "cases": {
    "simple_equation": {
      "input": {
        "text": "The equation $E = mc^2$ represents mass-energy equivalence."
      },
      "expected": {
        "equations": ["E = mc^2"],
        "count": 1
      }
    },
    "multiple_equations": {
      "input": {
        "text": "We have $\\alpha + \\beta = \\gamma$ and $\\int_0^1 f(x)dx = 1$."
      },
      "expected": {
        "equations": ["\\alpha + \\beta = \\gamma", "\\int_0^1 f(x)dx = 1"],
        "count": 2
      }
    },
    "malformed_latex": {
      "input": {
        "text": "Broken equation $\\frac{1}{0"
      },
      "expected": {
        "equations": [],
        "count": 0,
        "errors": ["Unclosed LaTeX delimiter"]
      }
    }
  }
}
```

#### collections_logic.json

```json
{
  "cases": {
    "mean_vector_calculation": {
      "input": {
        "resources": [
          {"id": 1, "embedding": [1.0, 0.0, 0.0]},
          {"id": 2, "embedding": [0.0, 1.0, 0.0]},
          {"id": 3, "embedding": [0.0, 0.0, 1.0]}
        ]
      },
      "expected": {
        "collection_embedding": [0.333, 0.333, 0.333],
        "tolerance": 0.001
      }
    },
    "empty_collection": {
      "input": {
        "resources": []
      },
      "expected": {
        "collection_embedding": null
      }
    }
  }
}
```

## Data Models

### Test Data Factories

```python
# Factory pattern for test data creation
class TestDataFactory:
    """Factory for creating test data with sensible defaults."""
    
    @staticmethod
    def create_resource(
        db_session,
        title: str = "Test Resource",
        url: str = "https://example.com/test",
        **kwargs
    ):
        """Create a test resource with defaults."""
        from app.modules.resources.model import Resource
        resource = Resource(title=title, url=url, **kwargs)
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        return resource
    
    @staticmethod
    def create_category(
        db_session,
        name: str = "Test Category",
        parent_id: int = None,
        **kwargs
    ):
        """Create a test category with defaults."""
        from app.modules.taxonomy.model import Category
        category = Category(name=name, parent_id=parent_id, **kwargs)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Performance Limit Enforcement

*For any* test decorated with @performance_limit(max_ms), if the test execution time exceeds max_ms, then a PerformanceRegressionError should be raised with a message containing "PERFORMANCE REGRESSION DETECTED" and "DO NOT INCREASE THE TIMEOUT".

**Validates: Requirements 1.2, 1.3, 1.4, 14.1-14.5**

### Property 2: Golden Data Immutability

*For any* golden data file in tests/golden_data/, the file content should remain unchanged across test runs, and any attempt to modify golden data during test execution should fail the test.

**Validates: Requirements 2.5, 2.6**

### Property 3: Event Verification Completeness

*For any* integration test that modifies system state, the test should verify that mock_event_bus.emit was called with the correct event type and payload.

**Validates: Requirements 13.1, 13.2, 13.3**

### Property 4: Mock ML Inference Isolation

*For any* test that uses ML models, the test should use mock_ml_inference fixture and should not load actual transformer models from disk.

**Validates: Requirements 1.1, 1.5, 15.1**

### Property 5: Test Data Cleanup

*For any* test that creates database records, all created records should be automatically cleaned up after the test completes, ensuring no data pollution between tests.

**Validates: Requirements 19.3, 19.4**

### Property 6: Error Message Quality

*For any* golden data assertion failure, the error message should contain both "IMPLEMENTATION FAILURE" and "DO NOT UPDATE THE TEST", along with clear expected vs actual value comparison.

**Validates: Requirements 20.1, 20.4, 20.5**

### Property 7: Test Organization Consistency

*For any* module in app/modules/, there should exist a corresponding test directory in tests/modules/ with the same name, containing at least one test file.

**Validates: Requirements 16.1, 16.2, 16.5**

### Property 8: Coverage Threshold Compliance

*For any* module in app/modules/, the code coverage for that module should be ≥80%, with critical paths achieving 100% coverage.

**Validates: Requirements 17.1, 17.2**

## Error Handling

### Performance Regression Errors

```python
# Example error message format
"""
PERFORMANCE REGRESSION DETECTED
Function: test_graph_traversal_100_edges
Expected: <50ms
Actual: 127.45ms
Regression: 77.45ms

DO NOT INCREASE THE TIMEOUT
This indicates a performance regression in the implementation.
Fix the implementation, not the test.
"""
```

### Golden Data Assertion Errors

```python
# Example error message format (from existing protocol.py)
"""
IMPLEMENTATION FAILURE: Golden data mismatch for 'taxonomy_prediction.machine_learning_paper'

Expected category_id: 42
Actual category_id: 38

DO NOT UPDATE THE TEST OR GOLDEN DATA
The implementation must be fixed to match the expected behavior.
"""
```

### Event Verification Errors

```python
# Example error message format
"""
EVENT VERIFICATION FAILURE

Expected event: resource.created
Actual events: []

The integration test expected an event to be emitted but none was found.
Verify that the service is calling event_bus.emit() correctly.
"""
```

## Testing Strategy

### Test Layer Distribution

| Module | Golden Logic | Edge Cases | Integration | Performance |
|--------|-------------|------------|-------------|-------------|
| Taxonomy | 3 tests | 5 tests | 2 tests | 0 tests |
| Graph | 2 tests | 3 tests | 2 tests | 2 tests |
| Collections | 2 tests | 3 tests | 2 tests | 0 tests |
| Scholarly | 3 tests | 2 tests | 2 tests | 0 tests |
| Curation | 0 tests | 2 tests | 3 tests | 0 tests |
| Recommendations | 3 tests | 2 tests | 2 tests | 1 test |
| Annotations | 2 tests | 3 tests | 2 tests | 0 tests |
| Authority | 1 test | 4 tests | 2 tests | 0 tests |
| Monitoring | 2 tests | 1 test | 3 tests | 0 tests |
| Resources | Existing | Existing | Existing | 0 tests |
| Search | Existing | Existing | Existing | Existing |
| Quality | Existing | Existing | Existing | 0 tests |

**Total New Tests**: ~60 tests across 9 modules

### Test Execution Strategy

1. **Unit Tests First**: Run golden logic and edge case tests
2. **Integration Tests Second**: Run API and database tests
3. **Performance Tests Last**: Run performance regression tests
4. **Parallel Execution**: Use pytest-xdist for faster execution

### Mock Strategy

```python
# ML Model Mocking Pattern
@pytest.fixture
def mock_bert_classifier(mock_ml_inference):
    """Mock BERT classifier for taxonomy tests."""
    mock_ml_inference["pipeline"].return_value = [
        {"label": "LABEL_42", "score": 0.92}
    ]
    return mock_ml_inference["pipeline"]

# Event Bus Mocking Pattern
@pytest.fixture
def mock_event_bus():
    """Mock event bus for integration tests."""
    with patch('app.shared.event_bus.EventBus.emit') as mock_emit:
        yield mock_emit

# Database Mocking Pattern (use real in-memory SQLite)
@pytest.fixture
def db_session():
    """In-memory SQLite session for tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

## Universal Test Template

```python
"""
Universal test template for Neo Alexandria 2.0 modules.

Copy this file to tests/modules/[module_name]/test_[feature].py
and customize for your specific module.
"""
import pytest
from backend.tests.protocol import (
    assert_against_golden,
    assert_score_against_golden,
    assert_ranking_against_golden
)
from backend.tests.performance import performance_limit

# ============================================================================
# GOLDEN LOGIC TESTS
# ============================================================================

def test_[feature]_golden_logic(db_session, mock_ml_inference):
    """
    Test [feature] algorithm against golden data.
    
    This test validates that the [feature] implementation produces
    exactly the expected output for known inputs.
    
    Golden Data: [module_name]_[feature].json
    Case: [case_name]
    """
    # Arrange: Set up test data
    # TODO: Create test data based on golden data input
    
    # Act: Execute the algorithm
    # TODO: Call the service method being tested
    
    # Assert: Verify against golden data
    assert_against_golden(
        module="[module_name]_[feature]",
        case_id="[case_name]",
        actual_data={"result": actual_result}
    )

# ============================================================================
# EDGE CASE & PATTERN TESTS
# ============================================================================

def test_[feature]_empty_input(db_session):
    """
    Test [feature] handles empty input gracefully.
    
    Edge Case: Empty list/None input
    Expected: Return empty result or raise ValueError
    """
    # Arrange
    # TODO: Set up empty input scenario
    
    # Act & Assert
    with pytest.raises(ValueError, match="[expected error message]"):
        # TODO: Call service method with empty input
        pass

def test_[feature]_boundary_condition(db_session):
    """
    Test [feature] handles boundary conditions correctly.
    
    Edge Case: Maximum/minimum values
    Expected: Graceful handling without overflow/underflow
    """
    # Arrange
    # TODO: Set up boundary condition
    
    # Act
    # TODO: Execute with boundary values
    
    # Assert
    # TODO: Verify correct handling
    assert result is not None

def test_[feature]_circular_dependency_prevention(db_session):
    """
    Test [feature] prevents circular dependencies.
    
    Pattern Validation: Circular reference detection
    Expected: ValueError raised when circular dependency detected
    """
    # Arrange
    # TODO: Create scenario that would cause circular dependency
    
    # Act & Assert
    with pytest.raises(ValueError, match="Circular dependency detected"):
        # TODO: Attempt to create circular dependency
        pass

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_[feature]_integration_flow(client, db_session, mock_event_bus):
    """
    Test complete [feature] flow from API to database.
    
    Integration: API → Service → Database → Events
    Verifies: HTTP response, DB persistence, event emission
    """
    # Arrange: Prepare request data
    request_data = {
        # TODO: Add request payload
    }
    
    # Act: Make API request
    response = client.post("/api/[endpoint]", json=request_data)
    
    # Assert: Verify HTTP response
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    
    # Assert: Verify database persistence
    # TODO: Query database and verify record exists
    
    # Assert: Verify event emission
    mock_event_bus.emit.assert_called_once()
    call_args = mock_event_bus.emit.call_args
    assert call_args[0][0] == "[event_type]"  # Event type
    assert call_args[0][1]["id"] == response_data["id"]  # Event payload

# ============================================================================
# PERFORMANCE REGRESSION TESTS
# ============================================================================

@performance_limit(max_ms=100)
def test_[feature]_performance(db_session, create_test_resource):
    """
    Test [feature] completes within performance budget.
    
    Performance Requirement: <100ms for [operation]
    Test Data: [N] records
    """
    # Arrange: Create test data
    # TODO: Create sufficient test data to stress the operation
    
    # Act: Execute operation (timed by decorator)
    # TODO: Call the service method being tested
    
    # Assert: Implicit - decorator will fail if >100ms
    assert result is not None

# ============================================================================
# HELPER FUNCTIONS (if needed)
# ============================================================================

def _create_test_[entity](db_session, **kwargs):
    """Helper to create test [entity] with defaults."""
    # TODO: Implement factory helper if needed
    pass
```

## Implementation Phases

### Phase 1: Infrastructure (Week 1)
- Create performance.py module
- Add mock_ml_inference fixture to conftest.py
- Add factory fixtures to conftest.py
- Create all golden data JSON files

### Phase 2: Core Modules (Week 2)
- Implement Taxonomy module tests (3 files)
- Implement Graph module tests (2 files)
- Implement Collections module tests (3 files)

### Phase 3: Content Modules (Week 3)
- Implement Scholarly module tests (2 files)
- Implement Curation module tests (2 files)
- Implement Recommendations module tests (3 files)

### Phase 4: Supporting Modules (Week 4)
- Implement Annotations module tests (2 files)
- Implement Authority module tests (2 files)
- Implement Monitoring module tests (2 files)

### Phase 5: Validation & Documentation (Week 5)
- Run full test suite and verify coverage
- Document performance baselines
- Create test execution reports
- Update developer guides

## Performance Baselines

| Operation | Baseline | Test Method |
|-----------|----------|-------------|
| Hybrid Search | 500ms | @performance_limit(500) |
| Graph Traversal (100 edges) | 50ms | @performance_limit(50) |
| Recommendation Generation | 100ms | @performance_limit(100) |
| Quality Score Computation | 200ms | @performance_limit(200) |
| Taxonomy Classification | 150ms | @performance_limit(150) |
| Collection Aggregation | 100ms | @performance_limit(100) |
| Annotation Search | 300ms | @performance_limit(300) |

## Success Criteria

1. **Coverage**: >80% code coverage across all modules
2. **Performance**: All performance tests pass with established baselines
3. **Reliability**: Zero flaky tests in CI/CD pipeline
4. **Maintainability**: All tests use golden data or clear assertions
5. **Speed**: Full test suite completes in <120 seconds
6. **Documentation**: All modules have comprehensive test documentation
