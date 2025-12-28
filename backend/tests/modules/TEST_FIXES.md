# Module Tests - Comprehensive Fix Plan

**Date**: December 25, 2024
**Status**: In Progress

## Overview

This document outlines the fixes needed for the module endpoint tests based on the initial test run. The tests were generated programmatically and need adjustments to match actual API schemas and behaviors.

## Critical Issues Identified

### 1. Schema Mismatches (Priority 1)

#### Collections Module
**Issue**: `CollectionCreate` schema requires `owner_id` field
**Location**: `backend/tests/modules/test_collections_endpoints.py`
**Fix**: Add `owner_id` to all test fixtures

```python
# Current (BROKEN)
@pytest.fixture
def sample_collection_data():
    return {
        "name": "Test Collection",
        "description": "A test collection",
        "tags": ["test", "example"]  # tags field doesn't exist in schema
    }

# Fixed
@pytest.fixture
def sample_collection_data():
    return {
        "name": "Test Collection",
        "description": "A test collection",
        "owner_id": "test-user-123",  # Required field
        "visibility": "private"  # Optional but good to include
    }
```

#### Resources Module  
**Issue**: Missing `ResourceStatus` import
**Location**: `backend/tests/modules/test_collections_endpoints.py` line 62
**Fix**: Add import statement

```python
from app.database.models import Collection, Resource, ResourceStatus
```

### 2. Missing Fixtures (Priority 1)

#### Database Session Fixture
**Issue**: Tests use `db: Session` fixture but it's not defined in the module conftest
**Location**: All test files
**Fix**: Create `backend/tests/modules/conftest.py` with proper fixtures

```python
"""
Shared fixtures for module endpoint tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.database.base import Base
from app.main import app


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Create a fresh database session for each test.
    Uses in-memory SQLite for fast, isolated tests.
    """
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session):
    """
    Create test client with database session override.
    """
    from app.shared.database import get_db
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
```

### 3. Router Registration Issues (Priority 2)

**Status**: ✅ VERIFIED - All routers are properly registered in `app/__init__.py`

The following modules are correctly registered:
- collections
- resources  
- search
- annotations
- scholarly
- authority
- curation
- quality
- taxonomy
- graph
- recommendations
- monitoring

No router registration fixes needed.

### 4. Health Check Response Format (Priority 2)

#### Issue
Health checks return different formats than tests expect:
- Tests expect: `{"status": "healthy"}`
- Some modules return: `{"status": "unhealthy"}` or different structures

#### Fix Locations
1. `backend/app/modules/collections/router.py` - Health check endpoint
2. `backend/app/modules/search/router.py` - Health check endpoint
3. All other module routers

#### Standard Health Check Format
```python
@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Check module health status.
    
    Returns:
        HealthCheckResponse with status and optional details
    """
    try:
        # Test database connectivity
        db.execute(text("SELECT 1"))
        
        return HealthCheckResponse(
            status="healthy",
            module="collections",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            module="collections",
            timestamp=datetime.utcnow(),
            error=str(e)
        )
```

### 5. Test Data Factory Improvements (Priority 3)

#### Current Issues
- Factory fixtures don't handle all required fields
- No proper cleanup between tests
- Missing relationship setup

#### Improved Factory Pattern
```python
@pytest.fixture
def create_test_collection(db: Session):
    """Factory fixture to create test collections with proper cleanup."""
    created_collections = []
    
    def _create_collection(**kwargs):
        defaults = {
            "name": f"Collection-{uuid.uuid4()}",
            "description": "Test collection",
            "owner_id": "test-user-123",
            "visibility": "private"
        }
        defaults.update(kwargs)
        
        collection = Collection(**defaults)
        db.add(collection)
        db.commit()
        db.refresh(collection)
        
        created_collections.append(collection)
        return collection
    
    yield _create_collection
    
    # Cleanup
    for collection in created_collections:
        db.delete(collection)
    db.commit()
```

## Fix Implementation Plan

### Phase 1: Core Fixtures (Immediate)
1. ✅ Create `backend/tests/modules/conftest.py` with db and client fixtures
2. ✅ Add ResourceStatus import to test files
3. ✅ Update sample_collection_data fixture with owner_id

### Phase 2: Schema Fixes (High Priority)
1. Update all test data to match actual Pydantic schemas
2. Remove non-existent fields (like `tags` in collections)
3. Add all required fields

### Phase 3: Health Check Standardization (Medium Priority)
1. Review all module health check implementations
2. Standardize response format
3. Update tests to match actual responses

### Phase 4: Test Refinement (Lower Priority)
1. Improve factory fixtures with cleanup
2. Add proper relationship testing
3. Add integration workflow tests

## Files to Modify

### Immediate Changes
- [ ] `backend/tests/modules/conftest.py` (CREATE)
- [ ] `backend/tests/modules/test_collections_endpoints.py` (FIX)
- [ ] `backend/tests/modules/test_resources_endpoints.py` (VERIFY)
- [ ] `backend/tests/modules/test_search_endpoints.py` (FIX)

### Schema Review Needed
- [ ] All test files - verify test data matches schemas
- [ ] All module schemas - document required vs optional fields

### Health Check Review
- [ ] All module routers - standardize health check format
- [ ] All health check tests - update expectations

## Success Criteria

- [ ] All 99 tests can be collected without import errors
- [ ] At least 80% of tests pass (79+ tests)
- [ ] No 422 validation errors due to missing required fields
- [ ] Health checks return consistent format
- [ ] Database fixtures properly isolate tests

## Next Steps

1. Create the conftest.py file with proper fixtures
2. Fix the collections test file as a template
3. Apply same fixes to other test files
4. Run full test suite and iterate

## Notes

- Tests were generated programmatically, so some assumptions about API behavior may be incorrect
- Actual API may have evolved since test generation
- Some endpoints may not be fully implemented yet (expected failures)
- Focus on getting infrastructure right first, then refine individual tests
