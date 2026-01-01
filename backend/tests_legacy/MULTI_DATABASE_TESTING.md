# Multi-Database Testing Guide (Phase 13)

This guide explains how to run tests against both SQLite and PostgreSQL databases in Neo Alexandria 2.0.

## Overview

The test suite supports running tests against both SQLite and PostgreSQL databases. By default, tests use SQLite (in-memory for unit tests, file-based for integration tests). This allows for fast local development while ensuring production PostgreSQL compatibility.

## Quick Start

### Running Tests with SQLite (Default)

```bash
cd backend
pytest
```

### Running Tests with PostgreSQL

```bash
# Set TEST_DATABASE_URL environment variable
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db
pytest

# Or inline for a single test run
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest
```

## Database Type Detection

The test suite automatically detects the database type from the `TEST_DATABASE_URL` environment variable:

- **SQLite**: Default when `TEST_DATABASE_URL` is not set
  - Unit tests: In-memory database (`sqlite:///:memory:`)
  - Integration tests: File-based database (`sqlite:///temp_file.db`)

- **PostgreSQL**: When `TEST_DATABASE_URL` starts with `postgresql://`
  - Uses connection pooling (5 base + 10 overflow)
  - Applies PostgreSQL-specific optimizations

## Test Fixtures

### `test_db`

Creates an optimized database for testing with multi-database support.

```python
def test_example(test_db):
    """Test using the test database."""
    session = test_db()
    # Use session for testing
    session.close()
```

### `db_session`

Provides a database session for integration tests.

```python
def test_example(db_session):
    """Test using a database session."""
    from backend.app.database.models import Resource
    resources = db_session.query(Resource).all()
    assert isinstance(resources, list)
```

### `db_type`

Returns the database type being used for the current test.

```python
def test_example(db_session, db_type):
    """Test that conditionally executes based on database type."""
    if db_type == "postgresql":
        # PostgreSQL-specific test logic
        pass
    elif db_type == "sqlite":
        # SQLite-specific test logic
        pass
```

## PostgreSQL-Specific Tests

Tests marked with `@pytest.mark.postgresql` will only run when using a PostgreSQL database:

```python
import pytest

@pytest.mark.postgresql
def test_jsonb_feature(db_session, db_type):
    """Test PostgreSQL JSONB functionality."""
    if db_type != "postgresql":
        pytest.skip("PostgreSQL-specific test")
    
    # Test JSONB features
    pass
```

### Running PostgreSQL-Specific Tests

```bash
# Run only PostgreSQL-specific tests
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest -m postgresql

# Run PostgreSQL JSONB tests
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest tests/test_postgresql_jsonb.py -v

# Run PostgreSQL full-text search tests
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest tests/test_postgresql_fulltext.py -v
```

## Setting Up PostgreSQL for Testing

### Option 1: Docker Container

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

### Option 2: Docker Compose

```bash
# Start services
cd backend/docker
docker-compose up -d postgres

# Run tests
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/backend pytest
```

### Option 3: Local PostgreSQL

```bash
# Create test database
createdb test_db

# Run tests
TEST_DATABASE_URL=postgresql://localhost/test_db pytest
```

## Test Database Cleanup

PostgreSQL test databases should be cleaned between test runs:

```bash
# Drop and recreate test database
dropdb test_db
createdb test_db

# Or use a dedicated test database that gets recreated
TEST_DATABASE_URL=postgresql://localhost/test_neo_alexandria pytest
```

## Continuous Integration

In CI environments, set `TEST_DATABASE_URL` in your workflow configuration:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests with SQLite
        run: pytest
      
      - name: Run tests with PostgreSQL
        env:
          TEST_DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
        run: pytest
      
      - name: Run PostgreSQL-specific tests
        env:
          TEST_DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
        run: pytest -m postgresql
```

## Test Files

### Database-Agnostic Tests

Most tests are database-agnostic and will run against both SQLite and PostgreSQL:

- `tests/database/test_database_schema.py` - Schema validation
- `tests/services/test_*.py` - Service layer tests
- `tests/integration/test_*.py` - Integration tests

### PostgreSQL-Specific Tests

Tests that require PostgreSQL features:

- `tests/test_postgresql_jsonb.py` - JSONB containment queries, operators, and indexes
- `tests/test_postgresql_fulltext.py` - Full-text search with tsvector, tsquery, and ts_rank
- `tests/test_db_type_fixture.py` - Database type fixture validation

## Best Practices

1. **Write Database-Agnostic Tests**: Most tests should work with both SQLite and PostgreSQL
2. **Use `db_type` Fixture**: Conditionally execute database-specific logic
3. **Mark PostgreSQL Tests**: Use `@pytest.mark.postgresql` for PostgreSQL-only tests
4. **Skip Appropriately**: Use `pytest.skip()` when database type doesn't match
5. **Clean Test Data**: Ensure tests clean up after themselves
6. **Use Transactions**: Wrap tests in transactions for isolation
7. **Test Both Databases**: Run tests against both SQLite and PostgreSQL in CI

## Troubleshooting

### Tests Skip with "PostgreSQL-specific test"

This is expected when running without `TEST_DATABASE_URL` set. To run these tests:

```bash
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest -m postgresql
```

### Connection Errors

Ensure PostgreSQL is running and accessible:

```bash
# Test connection
psql -h localhost -U test_user -d test_db

# Check if PostgreSQL is running
docker ps | grep postgres
```

### Schema Errors

Ensure database schema is up to date:

```bash
# Run migrations
alembic upgrade head

# Or recreate test database
dropdb test_db
createdb test_db
alembic upgrade head
```

## Performance Considerations

- **SQLite**: Fast for unit tests (in-memory), slower for integration tests (file-based)
- **PostgreSQL**: Slower startup, but better for integration tests with concurrent operations
- **Recommendation**: Use SQLite for local development, PostgreSQL for CI and production testing

## Related Documentation

- [README.md](README.md) - General testing documentation
- [POSTGRESQL_MIGRATION_GUIDE.md](../docs/POSTGRESQL_MIGRATION_GUIDE.md) - PostgreSQL migration guide
- [DEVELOPER_GUIDE.md](../docs/DEVELOPER_GUIDE.md) - Developer setup guide
