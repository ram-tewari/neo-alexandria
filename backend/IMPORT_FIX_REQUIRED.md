# Import Fixes Required for Modular Architecture

## Issue

The modular refactoring has created new modules under `app/modules/`, but many files still use absolute imports with `backend.app.` prefix instead of relative imports. This prevents the application from starting.

## Files That Need Fixing

### Module Files (High Priority - Blocking App Start)
These files are in the new modules and MUST use relative imports:

1. `app/modules/collections/handlers.py` - Lines 15-16
2. `app/modules/collections/model.py` - Line 18
3. `app/modules/collections/router.py` - Lines 32-33
4. `app/modules/collections/service.py` - Line 32
5. `app/modules/search/router.py` - Lines 25-26

### Service Files (High Priority - Blocking App Start)
6. `app/services/curation_service.py` - Line 32

### Cache Files
7. `app/cache/redis_cache.py` - Line 25
8. `app/cache/__init__.py` - Line 8

### Domain Files
9. `app/domain/classification.py` - Line 11
10. `app/domain/quality.py` - Line 11
11. `app/domain/recommendation.py` - Line 11
12. `app/domain/search.py` - Line 11
13. `app/domain/__init__.py` - Lines 8, 18, 23, 29, 33

### Model Files
14. `app/models/__init__.py` - Line 3

## Fix Pattern

Replace:
```python
from backend.app.{module} import {item}
```

With:
```python
from ..{module} import {item}  # For files in subdirectories
from .{module} import {item}   # For files in same directory
```

## Already Fixed

✅ `app/routers/curation.py`
✅ `app/routers/taxonomy.py`
✅ `app/routers/scholarly.py`
✅ `app/routers/recommendation.py`
✅ `app/routers/monitoring.py`
✅ `app/routers/graph.py`
✅ `app/routers/discovery.py`
✅ `app/routers/classification.py`
✅ `app/routers/citations.py`
✅ `app/routers/annotations.py`
✅ `app/schemas/resource.py`
✅ `app/schemas/collection.py`
✅ `app/schemas/search.py`

## Testing

After fixing all imports, run:
```bash
python test_endpoints.py
```

This will verify:
1. All modules can be imported
2. The FastAPI app can be created
3. All endpoints are registered
4. Critical endpoints are present

## Expected Outcome

When all imports are fixed:
- ✓ Collections Module - 6 routes
- ✓ Resources Module - 7 routes  
- ✓ Search Module - 4 routes
- ✓ Application created successfully
- ✓ All critical endpoints registered

## Priority

**CRITICAL**: The module files (items 1-5) MUST be fixed first as they prevent the new modular architecture from working.

**HIGH**: Service and cache files (items 6-8) should be fixed next as they're imported during app initialization.

**MEDIUM**: Domain and model files (items 9-14) can be fixed after the app starts successfully.
