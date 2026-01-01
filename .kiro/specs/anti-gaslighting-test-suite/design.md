# Design Document: Anti-Gaslighting Test Suite

## Overview

This design document describes the architecture for Phase 14.5's "Anti-Gaslighting" Test Suite. The core innovation is decoupling test expectations from test logic using immutable "Golden Data" JSON files. This prevents AI coding assistants from "fixing" tests by modifying inline assertions when the implementation is actually broken.

The test suite is built entirely from scratch with no dependencies on existing test infrastructure, ensuring a clean foundation free from legacy bugs and assumptions.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Test Execution Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │ Quality Tests   │  │ Search Tests    │  │ Resource Tests      │ │
│  │ test_scoring.py │  │ test_hybrid.py  │  │ test_ingestion.py   │ │
│  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘ │
│           │                    │                       │            │
│           └────────────────────┼───────────────────────┘            │
│                                │                                    │
│                                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Protocol Module                           │   │
│  │  assert_against_golden(module, case_id, actual_data)        │   │
│  │  - Loads Golden Data JSON                                    │   │
│  │  - Compares actual vs expected                               │   │
│  │  - Raises "IMPLEMENTATION FAILURE" on mismatch               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│                                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Golden Data Layer                         │   │
│  │  tests/golden_data/                                          │   │
│  │  ├── quality_scoring.json    (READ-ONLY)                    │   │
│  │  ├── search_ranking.json     (READ-ONLY)                    │   │
│  │  └── resource_ingestion.json (READ-ONLY)                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      Test Infrastructure Layer                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    conftest.py (Fresh)                       │   │
│  │  - db_session: In-memory SQLite, function-scoped            │   │
│  │  - client: TestClient with dependency override               │   │
│  │  - mock_event_bus: Spy on event_bus.emit calls              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      Application Layer (Imports)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │ app.modules.*   │  │ app.shared.*    │  │ app.database.*      │ │
│  │ Quality Service │  │ Event Bus       │  │ Models              │ │
│  │ Search Service  │  │ Database        │  │ Base                │ │
│  │ Resource Service│  │                 │  │                     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
backend/tests/
├── golden_data/                      # READ-ONLY Truth Sources
│   ├── quality_scoring.json          # Quality calculation expectations
│   ├── search_ranking.json           # RRF fusion expectations
│   └── resource_ingestion.json       # Ingestion workflow expectations
├── modules/                          # Vertical Slice Tests
│   ├── quality/
│   │   ├── __init__.py
│   │   └── test_scoring.py           # Quality service tests
│   ├── search/
│   │   ├── __init__.py
│   │   └── test_hybrid.py            # RRF fusion tests
│   └── resources/
│       ├── __init__.py
│       └── test_ingestion_flow.py    # Integration tests
├── __init__.py
├── conftest.py                       # Fresh fixtures (no legacy imports)
└── protocol.py                       # Golden Data assertion helpers
```

## Components and Interfaces

### 1. Protocol Module (`tests/protocol.py`)

The protocol module enforces the Golden Data pattern by providing assertion helpers that load expected values from JSON files.

```python
"""
Anti-Gaslighting Protocol Module

Provides assertion helpers that enforce the Golden Data pattern.
All test expectations are loaded from immutable JSON files.
"""

from pathlib import Path
from typing import Any, Dict
import json


GOLDEN_DATA_DIR = Path(__file__).parent / "golden_data"


class GoldenDataError(AssertionError):
    """Raised when actual data does not match Golden Data expectations."""
    pass


def load_golden_data(module: str) -> Dict[str, Any]:
    """
    Load Golden Data JSON file for a module.
    
    Args:
        module: Module name (e.g., "quality_scoring", "search_ranking")
        
    Returns:
        Dictionary containing all test cases for the module
        
    Raises:
        FileNotFoundError: If Golden Data file does not exist
    """
    file_path = GOLDEN_DATA_DIR / f"{module}.json"
    if not file_path.exists():
        raise FileNotFoundError(
            f"Golden Data file not found: {file_path}\n"
            f"Create the file with expected test values."
        )
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def assert_against_golden(module: str, case_id: str, actual_data: Any) -> None:
    """
    Assert actual data matches Golden Data expectations.
    
    This is the core anti-gaslighting assertion. It loads expected values
    from an immutable JSON file and compares against actual implementation output.
    
    Args:
        module: Module name (e.g., "quality_scoring")
        case_id: Test case identifier within the module
        actual_data: Actual data from implementation to verify
        
    Raises:
        GoldenDataError: If actual data does not match expected data
    """
    golden_data = load_golden_data(module)
    
    if case_id not in golden_data:
        raise GoldenDataError(
            f"IMPLEMENTATION FAILURE: Test case '{case_id}' not found in Golden Data.\n"
            f"DO NOT UPDATE THE TEST - Add the test case to golden_data/{module}.json\n"
            f"Available cases: {list(golden_data.keys())}"
        )
    
    expected_data = golden_data[case_id]
    
    if actual_data != expected_data:
        raise GoldenDataError(
            f"IMPLEMENTATION FAILURE: Actual data does not match Golden Data.\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
            f"\n"
            f"Golden Data File: golden_data/{module}.json\n"
            f"Test Case ID: {case_id}\n"
            f"\n"
            f"Expected (from Golden Data):\n{json.dumps(expected_data, indent=2)}\n"
            f"\n"
            f"Actual (from implementation):\n{json.dumps(actual_data, indent=2)}\n"
        )


def assert_score_against_golden(
    module: str, 
    case_id: str, 
    actual_score: float,
    tolerance: float = 0.001
) -> None:
    """
    Assert a numeric score matches Golden Data with tolerance.
    
    Args:
        module: Module name
        case_id: Test case identifier
        actual_score: Actual score from implementation
        tolerance: Acceptable difference (default: 0.001)
        
    Raises:
        GoldenDataError: If score differs by more than tolerance
    """
    golden_data = load_golden_data(module)
    
    if case_id not in golden_data:
        raise GoldenDataError(
            f"IMPLEMENTATION FAILURE: Test case '{case_id}' not found.\n"
            f"DO NOT UPDATE THE TEST - Add case to golden_data/{module}.json"
        )
    
    expected = golden_data[case_id]
    expected_score = expected.get("score") if isinstance(expected, dict) else expected
    
    if abs(actual_score - expected_score) > tolerance:
        raise GoldenDataError(
            f"IMPLEMENTATION FAILURE: Score mismatch.\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
            f"\n"
            f"Golden Data File: golden_data/{module}.json\n"
            f"Test Case ID: {case_id}\n"
            f"\n"
            f"Expected score: {expected_score}\n"
            f"Actual score: {actual_score}\n"
            f"Difference: {abs(actual_score - expected_score)} (tolerance: {tolerance})"
        )


def assert_ranking_against_golden(
    module: str,
    case_id: str,
    actual_ids: list,
    check_order: bool = True
) -> None:
    """
    Assert a ranking matches Golden Data expectations.
    
    Args:
        module: Module name
        case_id: Test case identifier
        actual_ids: Actual ranked IDs from implementation
        check_order: Whether order matters (True) or just membership (False)
        
    Raises:
        GoldenDataError: If ranking does not match
    """
    golden_data = load_golden_data(module)
    
    if case_id not in golden_data:
        raise GoldenDataError(
            f"IMPLEMENTATION FAILURE: Test case '{case_id}' not found.\n"
            f"DO NOT UPDATE THE TEST - Add case to golden_data/{module}.json"
        )
    
    expected = golden_data[case_id]
    expected_ids = expected.get("ranked_ids", expected)
    
    if check_order:
        if actual_ids != expected_ids:
            raise GoldenDataError(
                f"IMPLEMENTATION FAILURE: Ranking order mismatch.\n"
                f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
                f"\n"
                f"Golden Data File: golden_data/{module}.json\n"
                f"Test Case ID: {case_id}\n"
                f"\n"
                f"Expected order: {expected_ids}\n"
                f"Actual order: {actual_ids}"
            )
    else:
        if set(actual_ids) != set(expected_ids):
            raise GoldenDataError(
                f"IMPLEMENTATION FAILURE: Ranking membership mismatch.\n"
                f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
                f"\n"
                f"Expected IDs: {set(expected_ids)}\n"
                f"Actual IDs: {set(actual_ids)}"
            )
```

### 2. Test Fixtures (`tests/conftest.py`)

Fresh fixtures built from scratch with no legacy dependencies.

```python
"""
Anti-Gaslighting Test Suite - Fresh Fixtures

IMPORTANT: This file is built from scratch with NO imports from legacy test code.
All fixtures are self-contained and independent.
"""

import pytest
from typing import Generator
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Direct imports from application code only
from app.shared.database import Base
from app.shared.event_bus import event_bus, EventBus
from app.main import app
from app.database.models import Resource


# ============================================================================
# Database Fixtures (Fresh Implementation)
# ============================================================================

@pytest.fixture(scope="function")
def db_engine():
    """
    Create a fresh in-memory SQLite engine for each test.
    
    This fixture is function-scoped to ensure complete isolation.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    
    Provides complete isolation - each test gets its own session
    with a fresh database state.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ============================================================================
# FastAPI TestClient Fixture (Fresh Implementation)
# ============================================================================

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a TestClient with database dependency override.
    
    Overrides the app's get_db dependency to use our test session.
    """
    from app.shared.database import get_sync_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_sync_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# Event Bus Fixtures (Fresh Implementation)
# ============================================================================

@pytest.fixture(scope="function")
def mock_event_bus():
    """
    Create a mock/spy for the event bus emit method.
    
    This allows tests to verify that events are emitted without
    actually triggering event handlers.
    
    Usage:
        def test_resource_creation(client, mock_event_bus):
            response = client.post("/resources", json={...})
            
            # Verify event was emitted
            mock_event_bus.assert_called_with(
                "resource.created",
                {"resource_id": "...", ...}
            )
    """
    original_emit = event_bus.emit
    mock_emit = MagicMock(wraps=original_emit)
    
    with patch.object(event_bus, 'emit', mock_emit):
        yield mock_emit


@pytest.fixture(scope="function")
def clean_event_bus():
    """
    Provide a clean event bus state for each test.
    
    Clears all handlers and history before and after the test.
    """
    # Clear before test
    event_bus.clear_handlers()
    event_bus.clear_history()
    event_bus.reset_metrics()
    
    yield event_bus
    
    # Clear after test
    event_bus.clear_handlers()
    event_bus.clear_history()
    event_bus.reset_metrics()


# ============================================================================
# Test Data Factory Fixtures (Fresh Implementation)
# ============================================================================

@pytest.fixture(scope="function")
def create_test_resource(db_session: Session):
    """
    Factory fixture for creating test resources.
    
    Returns a function that creates resources with sensible defaults.
    """
    def _create_resource(**kwargs) -> Resource:
        defaults = {
            "title": "Test Resource",
            "description": "A test resource for unit testing",
            "source": "https://example.com/test",
            "ingestion_status": "pending",
            "quality_score": 0.0,
        }
        defaults.update(kwargs)
        
        resource = Resource(**defaults)
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        return resource
    
    return _create_resource


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test(db_session: Session):
    """
    Automatic cleanup after each test.
    
    This runs after every test to ensure clean state.
    """
    yield
    
    # Rollback any uncommitted changes
    db_session.rollback()
```

### 3. Golden Data Files

#### `tests/golden_data/quality_scoring.json`

```json
{
  "completeness_partial": {
    "score": 0.5,
    "reasoning": ["Missing subject", "Missing language"],
    "fields_present": ["title", "description", "creator"],
    "fields_missing": ["subject", "language"]
  },
  "completeness_full": {
    "score": 1.0,
    "reasoning": [],
    "fields_present": ["title", "description", "subject", "creator", "language", "type", "identifier"],
    "fields_missing": []
  },
  "completeness_minimal": {
    "score": 0.14285714285714285,
    "reasoning": ["Missing description", "Missing subject", "Missing creator", "Missing language", "Missing type", "Missing identifier"],
    "fields_present": ["title"],
    "fields_missing": ["description", "subject", "creator", "language", "type", "identifier"]
  },
  "metadata_completeness_empty": {
    "score": 0.0,
    "reasoning": ["All required fields missing"],
    "fields_present": [],
    "fields_missing": ["title", "description", "subject", "creator", "language", "type", "identifier"]
  }
}
```

#### `tests/golden_data/search_ranking.json`

```json
{
  "rrf_fusion_scenario_1": {
    "description": "Basic RRF fusion with three result lists",
    "inputs": {
      "dense_results": ["doc_A", "doc_B", "doc_C"],
      "sparse_results": ["doc_C", "doc_A", "doc_D"],
      "keyword_results": ["doc_B", "doc_A", "doc_E"]
    },
    "ranked_ids": ["doc_A", "doc_C", "doc_B", "doc_D", "doc_E"],
    "scores": {
      "doc_A": 0.04918032786885246,
      "doc_C": 0.03278688524590164,
      "doc_B": 0.03278688524590164,
      "doc_D": 0.016129032258064516,
      "doc_E": 0.016129032258064516
    }
  },
  "rrf_fusion_empty_lists": {
    "description": "RRF fusion with empty input lists",
    "inputs": {
      "dense_results": [],
      "sparse_results": [],
      "keyword_results": []
    },
    "ranked_ids": [],
    "scores": {}
  },
  "rrf_fusion_single_list": {
    "description": "RRF fusion with only one non-empty list",
    "inputs": {
      "dense_results": ["doc_X", "doc_Y", "doc_Z"],
      "sparse_results": [],
      "keyword_results": []
    },
    "ranked_ids": ["doc_X", "doc_Y", "doc_Z"],
    "scores": {
      "doc_X": 0.016393442622950822,
      "doc_Y": 0.01639344262295082,
      "doc_Z": 0.015873015873015872
    }
  }
}
```

#### `tests/golden_data/resource_ingestion.json`

```json
{
  "create_resource_success": {
    "description": "Successful resource creation via API",
    "request": {
      "url": "https://example.com/article",
      "title": "Test Article"
    },
    "expected_response": {
      "status_code": 202,
      "body_contains": ["id", "title", "ingestion_status"]
    },
    "expected_db_state": {
      "ingestion_status": "pending",
      "title": "Test Article"
    },
    "expected_events": [
      {
        "event_type": "resource.created",
        "payload_contains": ["resource_id", "title", "source"]
      }
    ]
  },
  "create_resource_missing_url": {
    "description": "Resource creation fails without URL",
    "request": {
      "title": "Test Article"
    },
    "expected_response": {
      "status_code": 422
    },
    "expected_events": []
  },
  "create_resource_duplicate_url": {
    "description": "Duplicate URL returns existing resource",
    "request": {
      "url": "https://example.com/existing",
      "title": "Duplicate Article"
    },
    "expected_response": {
      "status_code": 200
    },
    "expected_db_state": {
      "is_existing": true
    },
    "expected_events": []
  }
}
```

## Data Models

### Golden Data Schema

Each Golden Data file follows a consistent schema:

```python
# Type definitions for Golden Data structures

from typing import TypedDict, List, Dict, Any, Optional


class QualityScoringCase(TypedDict):
    score: float
    reasoning: List[str]
    fields_present: List[str]
    fields_missing: List[str]


class SearchRankingInputs(TypedDict):
    dense_results: List[str]
    sparse_results: List[str]
    keyword_results: List[str]


class SearchRankingCase(TypedDict):
    description: str
    inputs: SearchRankingInputs
    ranked_ids: List[str]
    scores: Dict[str, float]


class ExpectedResponse(TypedDict):
    status_code: int
    body_contains: Optional[List[str]]


class ExpectedDbState(TypedDict, total=False):
    ingestion_status: str
    title: str
    is_existing: bool


class ExpectedEvent(TypedDict):
    event_type: str
    payload_contains: List[str]


class ResourceIngestionCase(TypedDict):
    description: str
    request: Dict[str, Any]
    expected_response: ExpectedResponse
    expected_db_state: Optional[ExpectedDbState]
    expected_events: List[ExpectedEvent]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*



Based on the prework analysis, the following properties have been identified and consolidated:

### Property 1: Golden Data Loading Correctness

*For any* valid module name that corresponds to an existing Golden Data JSON file, calling `load_golden_data(module)` shall return the complete contents of that JSON file as a dictionary.

**Validates: Requirements 2.2**

### Property 2: Case ID Retrieval Correctness

*For any* valid case_id that exists within a Golden Data file, calling `assert_against_golden(module, case_id, actual_data)` with matching actual_data shall not raise an exception, and calling it with non-matching actual_data shall raise a GoldenDataError.

**Validates: Requirements 2.3**

### Property 3: Error Message Format Compliance

*For any* assertion failure (when actual_data does not match expected_data), the raised GoldenDataError message shall contain both the string "IMPLEMENTATION FAILURE" and the string "DO NOT UPDATE THE TEST".

**Validates: Requirements 2.4, 2.5, 11.1, 11.2**

### Property 4: Error Message Content Completeness

*For any* assertion failure, the raised GoldenDataError message shall contain: (1) the Golden Data file path, (2) the case_id, (3) the expected value from Golden Data, and (4) the actual value from the implementation.

**Validates: Requirements 2.6, 11.3, 11.4, 11.5**

### Property 5: Database Lifecycle Isolation

*For any* test function using the `db_session` fixture, all required database tables shall exist at the start of the test, and all tables shall be dropped after the test completes, ensuring complete isolation between tests.

**Validates: Requirements 3.2, 3.3**

### Property 6: Event Verification Completeness

*For any* event emission captured by `mock_event_bus`, the mock shall record both the event type and the event payload, and tests that expect specific events shall fail if those events are not emitted.

**Validates: Requirements 4.1, 4.3, 4.5**

## Error Handling

### Protocol Module Errors

| Error Type | Condition | Message Format |
|------------|-----------|----------------|
| `FileNotFoundError` | Golden Data file does not exist | "Golden Data file not found: {path}" |
| `GoldenDataError` | Case ID not found in Golden Data | "IMPLEMENTATION FAILURE: Test case '{case_id}' not found..." |
| `GoldenDataError` | Actual data does not match expected | "IMPLEMENTATION FAILURE: Actual data does not match Golden Data..." |

### Database Fixture Errors

| Error Type | Condition | Handling |
|------------|-----------|----------|
| `RuntimeError` | Database not initialized | Raise with message "Database not initialized" |
| `SQLAlchemyError` | Table creation fails | Log error and re-raise |

### Event Bus Fixture Errors

| Error Type | Condition | Handling |
|------------|-----------|----------|
| `AssertionError` | Expected event not emitted | Test fails with clear message |

## Testing Strategy

### Dual Testing Approach

This test suite uses both unit tests and property-based tests:

1. **Unit Tests**: Verify specific examples from Golden Data files
   - Test specific quality scoring scenarios
   - Test specific RRF fusion scenarios
   - Test specific resource ingestion workflows

2. **Property-Based Tests**: Verify universal properties
   - Error message format compliance
   - Error message content completeness
   - Database lifecycle isolation

### Property-Based Testing Configuration

- **Framework**: `hypothesis` (Python property-based testing library)
- **Minimum iterations**: 100 per property test
- **Tag format**: `**Feature: anti-gaslighting-test-suite, Property {number}: {property_text}**`

### Test Organization

```
tests/
├── modules/
│   ├── quality/
│   │   └── test_scoring.py          # Unit tests using Golden Data
│   ├── search/
│   │   └── test_hybrid.py           # Unit tests using Golden Data
│   └── resources/
│       └── test_ingestion_flow.py   # Integration tests using Golden Data
├── properties/
│   └── test_protocol_properties.py  # Property-based tests for protocol module
├── golden_data/
│   ├── quality_scoring.json
│   ├── search_ranking.json
│   └── resource_ingestion.json
├── conftest.py
└── protocol.py
```

### Test Execution

```bash
# Run all anti-gaslighting tests
pytest backend/tests/modules/ -v

# Run property-based tests
pytest backend/tests/properties/ -v

# Run with coverage
pytest backend/tests/ --cov=backend/tests --cov-report=html
```

## Implementation Notes

### Why Golden Data?

The Golden Data pattern addresses a critical problem with AI-assisted development: when tests fail, AI assistants often "fix" the test by changing the expected values rather than fixing the implementation. By storing expected values in separate, read-only JSON files with explicit "DO NOT UPDATE" warnings, we:

1. Make it harder to accidentally modify expectations
2. Provide clear audit trail when expectations change
3. Force developers to consciously update Golden Data files
4. Enable version control tracking of expectation changes

### Fixture Independence

All fixtures are built from scratch to avoid inheriting bugs from legacy test code:

1. **No imports from `tests_legacy/`**: Prevents contamination from buggy fixtures
2. **Self-contained database setup**: Uses in-memory SQLite with explicit table creation
3. **Fresh event bus mocking**: Uses `unittest.mock` directly without legacy wrappers
4. **Explicit cleanup**: Each fixture handles its own teardown

### Error Message Design

Error messages are designed to be:

1. **Unambiguous**: Start with "IMPLEMENTATION FAILURE" to clearly indicate the problem
2. **Directive**: Include "DO NOT UPDATE THE TEST" to guide AI assistants
3. **Informative**: Show file path, case_id, expected, and actual values
4. **Actionable**: Point to the Golden Data file that defines expectations
