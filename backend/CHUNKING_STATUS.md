# Chunking Status Report

**Date**: 2026-01-13  
**Issue**: Chunks not being created when resources are added via API

## Root Cause Analysis

### ✅ What's Working
1. **Chunking algorithm** - Verified functional
2. **Event emission code** - Present in `create_pending_resource()` (line 137-148)
3. **Event handler** - `handle_resource_created()` exists and is correct
4. **Handler registration** - `register_handlers()` function exists
5. **Configuration** - `CHUNK_ON_RESOURCE_CREATE=true`

### ❌ What's NOT Working
**Event handlers are not being registered when the app starts**

## The Problem

The event flow should be:
```
1. App starts → register_all_modules() called
2. Resources module loaded → register_handlers() called  
3. Handler subscribed to "resource.created" event
4. Resource created → event emitted
5. Handler receives event → triggers chunking
```

**But**: Step 3 is not happening reliably.

## Evidence

From `test_event_emission.py`:
```
Handlers registered for 'resource.created': 0
⚠️  NO HANDLERS REGISTERED!
```

This means when you create a resource:
- ✅ Event IS emitted (code exists)
- ❌ No handler listening (not registered)
- ❌ Chunking never triggered

## The Fix Applied

Added fallback registration in `service.py` (line 137-143):
```python
# Ensure handlers are registered (in case app didn't initialize them)
from .handlers import register_handlers
if "resource.created" not in event_bus._handlers or len(event_bus._handlers.get("resource.created", [])) == 0:
    logger.info("Registering resource handlers (not initialized by app)")
    register_handlers()
```

This ensures handlers are registered on first resource creation if they weren't registered during app startup.

## Next Steps

### To Verify the Fix:

1. **Restart the server** (to load the new code):
   ```bash
   # Stop current server (Ctrl+C or kill process)
   # Start fresh:
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Create a test resource**:
   ```bash
   curl -X POST http://localhost:8000/api/resources/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "url": "https://example.com/chunking-test",
       "title": "Chunking Test",
       "description": "This is a long description that should trigger chunking. It needs to be substantial enough to create multiple chunks for testing purposes. The chunking system should automatically process this content and store it in the document_chunks table with proper metadata."
     }'
   ```

3. **Check the logs** for:
   ```
   "Registering resource handlers (not initialized by app)"
   "Emitted resource.created event for <resource_id>"
   "Triggering automatic chunking for resource <resource_id>"
   "Successfully chunked resource <resource_id> into X chunks"
   ```

4. **Query the database**:
   ```sql
   SELECT COUNT(*) FROM document_chunks WHERE resource_id = '<resource_id>';
   ```

### Alternative: Check App Initialization

The proper fix is to ensure `register_handlers()` is called during app startup. Check:

1. **Is the resources module being loaded?**
   - Look in `app/__init__.py` line 118-126
   - Should see: "✓ Registered event handlers for module: resources"

2. **Check server startup logs** for:
   ```
   "Resources module event handlers registered"
   ```

If you don't see this message, the module isn't being initialized properly.

## Summary

The chunking code is correct, but the event handler registration isn't happening. The fix I applied adds a fallback that will register handlers on first use. After restarting the server, chunking should work.

**Status**: ⚠️  NEEDS SERVER RESTART TO VERIFY
