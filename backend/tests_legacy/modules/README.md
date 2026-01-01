# Module Endpoint Tests

This directory contains comprehensive endpoint tests for all 13 modules in the Phase 14 vertical slice architecture.

## Test Files

### Core Modules
- `test_resources_endpoints.py` - Resource CRUD, ingestion, status tracking
- `test_collections_endpoints.py` - Collection management, resource relationships
- `test_search_endpoints.py` - Keyword, semantic, and hybrid search

### Content Modules
- `test_annotations_endpoints.py` - Text annotations and semantic search
- `test_scholarly_endpoints.py` - Academic metadata extraction

### Organization Modules
- `test_authority_endpoints.py` - Subject authority and classification
- `test_curation_endpoints.py` - Content review and batch operations
- `test_taxonomy_endpoints.py` - Taxonomy management and ML classification

### Intelligence Modules
- `test_quality_endpoints.py` - Quality assessment and metrics
- `test_graph_endpoints.py` - Knowledge graph and citations

### User Experience Modules
- `test_recommendations_endpoints.py` - Personalized recommendations
- `test_monitoring_endpoints.py` - System health and metrics

## Running Tests

### Run All Module Tests
```bash
cd backend
pytest tests/modules/ -v
```

### Run Specific Module
```bash
pytest tests/modules/test_resources_endpoints.py -v
pytest tests/modules/test_search_endpoints.py -v
```

### Run with Coverage
```bash
pytest tests/modules/ --cov=app.modules --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/modules/test_resources_endpoints.py::TestResourceIngestion -v
```

### Run Specific Test Method
```bash
pytest tests/modules/test_resources_endpoints.py::TestResourceIngestion::test_ingest_url_success -v
```

## Test Structure

Each test file follows a consistent structure:

```python
"""
Module docstring describing endpoints tested
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Fixtures
@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def create_test_resource(db: Session):
    """Factory fixture for creating test data."""
    # Implementation

# Test Classes
class TestFeatureName:
    """Test specific feature."""
    
    def test_operation_success(self, client):
        """Test successful operation."""
        # Test implementation
    
    def test_operation_failure(self, client):
        """Test failure case."""
        # Test implementation
```

## Test Coverage

### Standard Tests (All Modules)
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ List/filter operations with pagination
- ✅ Health check endpoints
- ✅ Error handling (404, 422, etc.)
- ✅ Integration workflows

### Module-Specific Tests

**Resources**
- URL ingestion with background processing
- Status tracking and progression
- Resource classification
- Metadata management

**Collections**
- Resource-collection relationships
- Sharing and permissions
- Event emission verification

**Search**
- Multiple search strategies (keyword, semantic, hybrid)
- Search result ranking
- Filter and pagination
- Search suggestions

**Annotations**
- Text highlighting and notes
- Semantic search across annotations
- Cascade deletion on resource removal

**Scholarly**
- Metadata extraction from academic papers
- Equation and table parsing
- Automatic extraction on resource creation

**Authority**
- Subject authority suggestions
- Classification tree retrieval

**Curation**
- Review queue management
- Batch operations
- Quality outlier handling

**Quality**
- Multi-dimensional quality assessment
- Quality metrics and trends
- Quality computation on resource events

**Taxonomy**
- Taxonomy node CRUD
- ML classification
- Model training
- Auto-classification on resource creation

**Graph**
- Knowledge graph operations
- Citation extraction and network
- Discovery hypothesis generation
- Graph updates on resource events

**Recommendations**
- Recommendation generation
- User profile management
- Feedback collection
- Profile updates on user interactions

**Monitoring**
- System-wide health checks
- Metrics aggregation
- Module status reporting
- Event metrics collection

## Test Patterns

### Flexible Assertions
Tests use flexible assertions to handle various valid response formats:

```python
# Accept multiple valid status codes
assert response.status_code in [200, 201]

# Handle different response structures
data = response.json()
items = data.get("items", data.get("results", data))
```

### Factory Fixtures
Factory fixtures allow creating test data with custom attributes:

```python
@pytest.fixture
def create_test_resource(db: Session):
    def _create_resource(**kwargs):
        defaults = {"title": "Test", "url": "https://example.com"}
        defaults.update(kwargs)
        resource = Resource(**defaults)
        db.add(resource)
        db.commit()
        return resource
    return _create_resource

# Usage
def test_something(create_test_resource):
    resource = create_test_resource(title="Custom Title")
```

### Test Organization
- Tests grouped by functionality using classes
- Clear, descriptive test names
- Comprehensive docstrings
- Proper setup and teardown

## Database Fixtures

Tests rely on pytest fixtures defined in `backend/tests/conftest.py`:

- `db` - Database session
- `client` - FastAPI test client
- Module-specific factory fixtures

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run Module Tests
  run: |
    cd backend
    pytest tests/modules/ -v --cov=app.modules
```

## Maintenance

### Adding New Tests
1. Follow the existing test file structure
2. Use factory fixtures for test data
3. Include docstrings for all tests
4. Test both success and failure cases
5. Use flexible assertions

### Updating Tests
When endpoints change:
1. Update relevant test file
2. Maintain backward compatibility where possible
3. Update docstrings if endpoint behavior changes
4. Run full test suite to verify no regressions

## Notes

- Tests use in-memory SQLite database by default
- Some tests may require additional setup for event bus
- Tests are designed to be independent and can run in any order
- Mock data is created fresh for each test

## Troubleshooting

### Import Errors
Ensure you're running from the backend directory:
```bash
cd backend
pytest tests/modules/
```

### Database Errors
Check that database fixtures are properly configured in `conftest.py`

### Test Failures
Run with verbose output to see detailed error messages:
```bash
pytest tests/modules/ -vv
```

## Related Documentation

- [Testing Guide](../../docs/guides/testing.md)
- [Module Architecture](../../docs/architecture/modules.md)
- [API Documentation](../../docs/api/)
- [Task 12.1 Completion Summary](./TASK_12_1_COMPLETION_SUMMARY.md)
