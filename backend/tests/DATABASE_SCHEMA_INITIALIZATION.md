# Database Schema Initialization for Tests

## Overview

This document describes the database schema initialization system implemented for the Neo Alexandria test suite. The system ensures that all test databases have the current schema with all required fields before tests run.

## Problem Statement

Tests were failing due to database schema mismatches, specifically:
- Missing `sparse_embedding` field in Resource model
- Missing `description` field in Resource model  
- Missing `publisher` field in Resource model
- Outdated test databases not reflecting current model definitions

## Solution

### Database Initialization Helper

A new helper function `ensure_database_schema()` has been added to `backend/tests/conftest.py`:

```python
def ensure_database_schema(engine):
    """
    Ensure database schema is current before tests run.
    
    This helper verifies that all model fields exist in the database schema
    and creates/updates tables as needed. It handles:
    - Creating all tables if they don't exist
    - Verifying critical fields (sparse_embedding, description, publisher)
    - Applying schema updates for test databases
    
    Args:
        engine: SQLAlchemy engine instance
    """
```

### Key Features

1. **Automatic Table Creation**: Creates all tables from current model definitions if they don't exist
2. **Field Verification**: Checks that critical Resource fields exist in the database
3. **Schema Recreation**: Drops and recreates tables if required fields are missing
4. **Error Handling**: Gracefully handles errors and provides fallback behavior
5. **Logging**: Logs schema verification steps for debugging

### Integration with Test Fixtures

The `test_db` fixture has been updated to use the initialization helper:

```python
@pytest.fixture
def test_db():
    """
    Create a file-based SQLite database for testing with current schema.
    
    This fixture:
    - Creates a temporary SQLite database file
    - Ensures all tables are created with current model definitions
    - Verifies critical fields exist (sparse_embedding, description, publisher)
    - Provides session factory for test database operations
    - Cleans up database file after tests complete
    """
    # ... implementation uses ensure_database_schema(engine)
```

## Verified Fields

The initialization helper specifically verifies these critical Resource model fields:

- `sparse_embedding` (Text) - Sparse vector embeddings for hybrid search
- `description` (Text) - Dublin Core description field
- `publisher` (String) - Dublin Core publisher field
- `embedding` (JSON) - Dense vector embeddings
- `quality_score` (Float) - Resource quality score

## Usage

### In Tests

Tests automatically benefit from the schema initialization through the `test_db` fixture:

```python
def test_my_feature(test_db):
    """Test that uses database."""
    db = test_db()
    
    # Database is guaranteed to have current schema
    resource = Resource(
        title="Test",
        description="Test description",  # Field guaranteed to exist
        publisher="Test Publisher",       # Field guaranteed to exist
        sparse_embedding='{"1": 0.5}',   # Field guaranteed to exist
        quality_score=0.85
    )
    db.add(resource)
    db.commit()
```

### Manual Initialization

You can also call the helper directly for custom test scenarios:

```python
from backend.tests.conftest import ensure_database_schema
from sqlalchemy import create_engine

engine = create_engine("sqlite:///test.db")
ensure_database_schema(engine)
```

## Testing

Comprehensive tests verify the initialization system:

- `tests/test_database_schema.py` - Basic schema verification tests
- `tests/test_schema_verification.py` - Comprehensive schema verification tests

Run tests with:

```bash
pytest tests/test_database_schema.py -v
pytest tests/test_schema_verification.py -v
```

## Benefits

1. **Eliminates Schema Mismatch Errors**: Tests no longer fail due to missing database fields
2. **Automatic Updates**: Test databases automatically reflect current model definitions
3. **Consistent Test Environment**: All tests run against the same schema
4. **Reduced Maintenance**: No need to manually update test databases when models change
5. **Better Error Messages**: Clear logging when schema issues are detected

## Migration Compatibility

The initialization system is compatible with Alembic migrations:

- Uses `Base.metadata.create_all()` for test databases (no migrations needed)
- Verifies schema matches current model definitions
- Can detect and fix schema drift in test databases
- Does not interfere with production migration system

## Troubleshooting

### Schema Verification Failures

If you see warnings about missing fields:

```
WARNING: Missing fields in resources table: {'sparse_embedding', 'description'}
```

The helper will automatically recreate the schema. If issues persist:

1. Check that model definitions in `backend/app/database/models.py` are correct
2. Verify that `Base.metadata` includes all models
3. Check for conflicting table definitions

### Test Database Cleanup

If test databases are not being cleaned up:

1. Ensure tests are using the `test_db` fixture correctly
2. Check that temporary files are being deleted in fixture teardown
3. Verify no processes are holding database file locks

## Related Files

- `backend/tests/conftest.py` - Test configuration and fixtures
- `backend/app/database/models.py` - SQLAlchemy model definitions
- `backend/app/database/base.py` - Database configuration
- `backend/tests/test_database_schema.py` - Schema verification tests
- `backend/tests/test_schema_verification.py` - Comprehensive schema tests

## Requirements Addressed

This implementation addresses the following requirements from the test suite stabilization spec:

- **Requirement 1.1**: Database schema includes all columns referenced by model classes
- **Requirement 1.2**: Resources table contains sparse_embedding column
- **Requirement 1.3**: Resources table contains description and publisher columns
- **Requirement 1.4**: Database schema supports all required fields without errors
- **Requirement 1.5**: Migration system applies pending migrations before test execution
