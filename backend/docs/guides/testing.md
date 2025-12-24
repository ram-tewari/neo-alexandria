# Testing Guide

Testing strategies and practices for Neo Alexandria 2.0.

## Running Tests

### All Tests

```bash
cd backend
pytest tests/ -v
```

### With Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

Coverage report generated in `htmlcov/index.html`

### Specific Test File

```bash
pytest tests/test_resources.py -v
```

### Specific Test Function

```bash
pytest tests/test_resources.py::test_create_resource -v
```

### By Marker

```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only integration tests
pytest tests/ -m integration -v

# Run PostgreSQL-specific tests
pytest tests/ -m postgresql -v
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_services.py
│   ├── test_schemas.py
│   └── test_domain.py
├── integration/             # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_events.py
└── performance/             # Performance tests
    └── test_benchmarks.py
```

## Test Fixtures

### Database Session

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

### Test Client

```python
@pytest.fixture
def client(db_session):
    """Create test API client."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.shared.database import get_db
    
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Sample Data

```python
@pytest.fixture
def sample_resource(db_session):
    """Create sample resource for testing."""
    from app.modules.resources.model import Resource
    
    resource = Resource(
        title="Test Resource",
        description="Test description",
        source="https://example.com/test"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource
```

## Writing Tests

### Unit Tests

Test individual functions in isolation:

```python
# tests/unit/test_quality_service.py
import pytest
from app.services.quality_service import compute_accuracy_score

def test_compute_accuracy_score_with_citations():
    """Test accuracy score with valid citations."""
    resource = MockResource(
        citations=["https://doi.org/10.1234/test"],
        source="https://arxiv.org/paper"
    )
    
    score = compute_accuracy_score(resource)
    
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Should be above baseline

def test_compute_accuracy_score_no_citations():
    """Test accuracy score without citations."""
    resource = MockResource(citations=[], source="https://example.com")
    
    score = compute_accuracy_score(resource)
    
    assert score == 0.5  # Baseline score
```

### Integration Tests

Test API endpoints end-to-end:

```python
# tests/integration/test_resources_api.py
def test_create_resource(client):
    """Test resource creation via API."""
    response = client.post(
        "/resources",
        json={"url": "https://example.com/article"}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"

def test_get_resource(client, sample_resource):
    """Test resource retrieval via API."""
    response = client.get(f"/resources/{sample_resource.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == sample_resource.title

def test_get_resource_not_found(client):
    """Test 404 for non-existent resource."""
    response = client.get("/resources/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404
```

### Event Tests

Test event publishing and handling:

```python
# tests/integration/test_events.py
from app.shared.event_bus import event_bus, Event

def test_resource_deleted_updates_collections(db_session, sample_resource, sample_collection):
    """Test that deleting a resource updates collections."""
    # Add resource to collection
    add_resource_to_collection(db_session, sample_collection.id, sample_resource.id)
    
    # Delete resource (triggers event)
    delete_resource(db_session, sample_resource.id)
    
    # Verify collection updated
    collection = get_collection(db_session, sample_collection.id)
    assert sample_resource.id not in [r.id for r in collection.resources]
```

### Database Tests

Test with different databases:

```python
# tests/test_postgresql.py
import pytest

@pytest.mark.postgresql
def test_jsonb_containment_query(db_session):
    """Test PostgreSQL JSONB containment query."""
    # Create resource with subjects
    resource = Resource(
        title="ML Paper",
        subject=["Machine Learning", "AI"]
    )
    db_session.add(resource)
    db_session.commit()
    
    # Query using JSONB containment
    results = db_session.query(Resource).filter(
        Resource.subject.contains(["Machine Learning"])
    ).all()
    
    assert len(results) == 1
    assert results[0].id == resource.id
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    postgresql: PostgreSQL-specific tests
    slow: Slow tests
addopts = -v --tb=short
```

### Environment Variables

```bash
# Use in-memory SQLite for tests
TEST_DATABASE_URL=sqlite:///:memory:

# Or test against PostgreSQL
TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/test_db
```

## Mocking

### Mock External Services

```python
from unittest.mock import Mock, patch

def test_ingestion_with_mock_http(db_session):
    """Test ingestion with mocked HTTP client."""
    with patch('httpx.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=200,
            text="<html><body>Test content</body></html>"
        )
        
        result = ingest_url(db_session, "https://example.com/test")
        
        assert result.title is not None
        mock_get.assert_called_once()
```

### Mock AI Models

```python
def test_classification_with_mock_model(db_session):
    """Test classification with mocked ML model."""
    with patch('app.services.ml_classification_service.model') as mock_model:
        mock_model.predict.return_value = [
            {"label": "Computer Science", "score": 0.95}
        ]
        
        result = classify_resource(db_session, resource_id)
        
        assert result.classification_code == "004"
```

## Performance Testing

```python
# tests/performance/test_benchmarks.py
import pytest
import time

@pytest.mark.slow
def test_search_performance(client, many_resources):
    """Test search completes within time limit."""
    start = time.time()
    
    response = client.post(
        "/search",
        json={"text": "machine learning", "limit": 100}
    )
    
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 0.5  # Should complete in <500ms
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Related Documentation

- [Setup Guide](setup.md) - Installation
- [Workflows](workflows.md) - Development tasks
- [Troubleshooting](troubleshooting.md) - Common issues
