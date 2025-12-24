# Test Suite PostgreSQL Error Fix Summary

## Problem
The test suite was failing with 805 errors due to PostgreSQL-specific issues:
- Tests were trying to create tables that already existed in a persistent PostgreSQL database
- The error: `relation "resources" already exists`

## Root Cause Analysis
1. **Database Initialization**: The app's `__init__.py` was calling `init_database()` with the production `DATABASE_URL` (PostgreSQL) even during tests
2. **Alembic Configuration**: The Alembic `env.py` was ignoring the test database connection and using `settings.DATABASE_URL` instead
3. **Test Fixture**: The `test_db` fixture was creating a test database, but the app was still connecting to the production PostgreSQL database

## Fixes Applied

### 1. App Initialization (backend/app/__init__.py)
**Changed**: Skip database initialization during tests
```python
# Skip database initialization during tests - test fixtures handle it
import os
if os.getenv("TESTING") != "true":
    settings = get_settings()
    init_database(settings.DATABASE_URL, settings.ENV)
```

### 2. Alembic Configuration (backend/alembic/env.py)
**Changed**: Check for test-provided connection before creating new one
```python
def run_migrations_online() -> None:
    # Check if connection is provided (e.g., from tests)
    connection = config.attributes.get('connection', None)
    
    if connection is None:
        # Use settings for database URL (production)
        ...
    else:
        # Use provided connection (from tests)
        context.configure(connection=connection, ...)
```

### 3. Test Database Fixture (backend/tests/conftest.py)
**Changed**: Added PostgreSQL schema cleanup
```python
# For PostgreSQL, drop all tables first to ensure clean state
if db_type == "postgresql":
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        ...
```

### 4. Migration Fixes

#### a. Classification Codes Migration (backend/alembic/versions/20250912_add_classification_codes.py)
**Fixed**: SQLite parameter binding for JSON data
```python
# Convert list to JSON string for SQLite
import json
op.execute(
    sa.text("UPDATE classification_codes SET keywords=:kw WHERE code=:code")
    .bindparams(kw=json.dumps(keywords), code=code)
)
```

#### b. Retraining Runs Migration (backend/alembic/versions/j0k1l2m3n4o5_add_retraining_runs_table.py)
**Fixed**: Database-agnostic type handling
```python
# Use appropriate types based on database
bind = op.get_bind()
is_postgresql = bind.dialect.name == 'postgresql'
uuid_type = postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(36)
json_type = postgresql.JSONB(astext_type=sa.Text()) if is_postgresql else sa.JSON()
```

### 5. Environment Configuration (backend/.env)
**Changed**: Commented out TEST_DATABASE_URL to let fixtures handle it
```properties
# Test Database (leave empty to use in-memory SQLite for tests)
# TEST_DATABASE_URL=
```

## Current Status

### ✅ Fixed
- PostgreSQL "relation already exists" errors
- Test database isolation
- Alembic migration execution in tests
- SQLite compatibility for migrations

### ⚠️ Remaining Issues
1. **Model-Migration Mismatch**: The Resource model has columns (e.g., `search_vector`) that don't exist in migrations
   - Error: `table resources has no column named search_vector`
   - Solution: Create migration to add missing columns OR update model to match migrations

2. **Standalone Test Scripts**: Some tests (e.g., `test_active_learning.py`) create their own database without using fixtures
   - These bypass the migration system
   - Solution: Convert to use pytest fixtures OR ensure they run migrations

## Recommendations

### Immediate Actions
1. **Audit Model vs Migrations**: Compare `backend/app/database/models.py` with latest migration to identify missing columns
2. **Create Missing Migrations**: Generate migrations for any columns added to models but not in database schema
3. **Convert Standalone Tests**: Update standalone test scripts to use pytest fixtures

### Long-term Improvements
1. **CI/CD Integration**: Add PostgreSQL service to GitHub Actions for testing against both SQLite and PostgreSQL
2. **Migration Testing**: Add tests that verify migrations work on both SQLite and PostgreSQL
3. **Schema Validation**: Add pre-commit hook to ensure models match migrations

## Testing Commands

### Run Single Test (SQLite)
```bash
cd backend
python -m pytest tests/integration/phase8_classification/test_phase8_api_endpoints.py::test_compare_methods_invalid_limit -xvs
```

### Run Full Test Suite
```bash
cd backend
python -m pytest tests/ -x --tb=line -q
```

### Run with PostgreSQL (if configured)
```bash
cd backend
export TEST_DATABASE_URL="postgresql://postgres:password@localhost:5432/test_db"
python -m pytest tests/ -x
```

## Files Modified
1. `backend/app/__init__.py` - Skip DB init during tests
2. `backend/alembic/env.py` - Use test-provided connection
3. `backend/tests/conftest.py` - Add PostgreSQL cleanup
4. `backend/alembic/versions/20250912_add_classification_codes.py` - Fix SQLite JSON binding
5. `backend/alembic/versions/j0k1l2m3n4o5_add_retraining_runs_table.py` - Database-agnostic types
6. `backend/.env` - Comment out TEST_DATABASE_URL

## Next Steps
1. Run migration audit to find missing columns
2. Generate and test new migrations
3. Re-run full test suite
4. Update CI/CD configuration
