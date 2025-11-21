# Tests Directory

## Structure

### API Tests (`api/`)
Tests for API endpoints and request/response handling:
- `test_collections.py` - Collection management endpoints
- `test_enhanced_search_api.py` - Enhanced search API
- `test_phase2_curation_api.py` - Curation endpoints
- `test_phase3_search_api.py` - Search endpoints

### Service Tests (`services/`)
Tests for business logic and service layer:
- `test_hybrid_search_query.py` - Hybrid search implementation
- `test_ml_classification_*.py` - ML classification services
- `test_recommendation_*.py` - Recommendation services
- `test_search_*.py` - Search services
- `test_sparse_embedding_service.py` - Sparse embedding service

### Database Tests (`database/`)
Tests for database schema and queries:
- `test_database_schema.py` - Schema validation
- `test_schema_verification.py` - Schema integrity checks

### Domain Tests (`domain/`)
Tests for domain-driven design objects:
- `test_domain_base.py` - Base domain objects
- `test_domain_classification.py` - Classification domain objects
- `test_domain_quality.py` - Quality domain objects
- `test_domain_recommendation.py` - Recommendation domain objects
- `test_domain_search.py` - Search domain objects

### Unit Tests (`unit/`)
Isolated component tests organized by phase:
- `test_celery_*.py` - Celery task tests
- `test_event_system.py` - Event system tests
- `test_refactoring_framework.py` - Refactoring tools tests
- Phase-specific subdirectories (phase1-11)

### Integration Tests (`integration/`)
End-to-end workflow tests organized by phase:
- `test_event_hooks.py` - Event hook integration
- `test_monitoring_endpoints.py` - Monitoring API integration
- `test_service_events.py` - Service event integration
- Phase-specific subdirectories (phase1-11)

### Performance Tests (`performance/`)
Load and performance benchmarks:
- `test_ml_latency.py` - ML inference latency
- `test_performance.py` - General performance tests
- `test_phase12_5_performance.py` - Phase 12.5 performance

### ML Benchmarks (`ml_benchmarks/`)
Machine learning model evaluation:
- `test_classification_metrics.py` - Classification model metrics
- `test_collaborative_filtering_metrics.py` - NCF model metrics
- `test_search_quality_metrics.py` - Search quality metrics
- `test_summarization_quality_metrics.py` - Summarization metrics

### Standalone Tests (`standalone/`)
Self-contained tests that can run independently:
- `test_classification_standalone.py` - Standalone classification test
- `test_domain_base_standalone.py` - Standalone domain test

## Running Tests

### All Tests
```bash
cd backend
pytest
```

### Specific Category
```bash
pytest tests/api/
pytest tests/services/
pytest tests/unit/
pytest tests/integration/
```

### Specific Test File
```bash
pytest tests/services/test_search_service.py
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

### Multi-Database Testing (Phase 13)

The test suite supports running tests against both SQLite and PostgreSQL databases. By default, tests use SQLite (in-memory for unit tests, file-based for integration tests).

#### Running Tests Against PostgreSQL

Set the `TEST_DATABASE_URL` environment variable to use PostgreSQL:

```bash
# Using a local PostgreSQL database
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db
pytest

# Or inline for a single test run
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest
```

#### PostgreSQL-Specific Tests

Some tests are marked with `@pytest.mark.postgresql` and will only run when using a PostgreSQL database:

```bash
# Run only PostgreSQL-specific tests
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest -m postgresql

# Run PostgreSQL JSONB tests
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest tests/test_postgresql_jsonb.py -v

# Run PostgreSQL full-text search tests
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest tests/test_postgresql_fulltext.py -v
```

#### Database-Agnostic Tests

Most tests are database-agnostic and will run against both SQLite and PostgreSQL. The test fixtures automatically detect the database type and configure appropriately.

#### Setting Up PostgreSQL for Testing

1. **Using Docker:**
```bash
# Start PostgreSQL container
docker run -d \
  --name postgres-test \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_pass \
  -e POSTGRES_DB=test_db \
  -p 5432:5432 \
  postgres:15

# Run tests
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db pytest
```

2. **Using Docker Compose:**
```bash
# Start services
cd backend/docker
docker-compose up -d postgres

# Run tests
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/backend pytest
```

3. **Using Local PostgreSQL:**
```bash
# Create test database
createdb test_db

# Run tests
TEST_DATABASE_URL=postgresql://localhost/test_db pytest
```

#### Test Database Cleanup

PostgreSQL test databases should be cleaned between test runs:

```bash
# Drop and recreate test database
dropdb test_db
createdb test_db

# Or use a dedicated test database that gets recreated
TEST_DATABASE_URL=postgresql://localhost/test_neo_alexandria pytest
```

#### Continuous Integration

In CI environments, set `TEST_DATABASE_URL` in your workflow configuration:

```yaml
# .github/workflows/test.yml
env:
  TEST_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
```

### Parallel Execution (Phase 12.6)
```bash
# Run tests in parallel with automatic worker count
pytest -n auto

# Run with specific worker count
pytest -n 4

# Run non-ML tests in parallel (recommended)
pytest -n auto -m "not use_real_models"

# Run ML tests separately (sequential)
pytest -m use_real_models
```

See [PARALLEL_EXECUTION.md](PARALLEL_EXECUTION.md) for detailed guide on parallel test execution, isolation issues, and best practices.

### Performance Tests Only
```bash
pytest tests/performance/ -v
```

### ML Benchmarks
```bash
pytest tests/ml_benchmarks/ -v
```

## Test Configuration

- **conftest.py** - Shared fixtures and test configuration
- **pytest.ini** - Pytest settings (in backend root)

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Test Organization
- **Unit tests**: Test single components in isolation
- **Integration tests**: Test component interactions
- **API tests**: Test HTTP endpoints
- **Performance tests**: Measure speed and resource usage
- **Benchmarks**: Evaluate ML model quality

### Example Test Structure
```python
# tests/services/test_my_service.py
import pytest
from app.services.my_service import MyService

class TestMyService:
    def test_basic_functionality(self, db_session):
        service = MyService(db_session)
        result = service.do_something()
        assert result is not None
    
    def test_error_handling(self, db_session):
        service = MyService(db_session)
        with pytest.raises(ValueError):
            service.do_invalid_thing()
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Scheduled nightly builds

## Test Coverage Goals

- Overall: >80%
- Critical paths: >90%
- New features: 100%
