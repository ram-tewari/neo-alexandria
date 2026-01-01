# Recommendation Router Fix Summary

## Problem
All 13 recommendation router tests were failing with 500 errors because the authentication dependency was querying the database directly instead of being properly overridable by test fixtures.

## Root Cause
The `_get_current_user_id()` function was being called directly in endpoint bodies:
```python
user_id = _get_current_user_id(db)
```

This prevented test fixtures from overriding authentication because:
1. The function was called manually, not as a FastAPI dependency
2. FastAPI dependency overrides only work when functions are used with `Depends()`

## Solution Applied

### Step 1: Convert to Dependency Injection ✅
Changed all 7 endpoints to use `_get_current_user_id` as a dependency parameter:

**Before:**
```python
async def get_recommendations_hybrid(
    db: Session = Depends(get_sync_db),
):
    user_id = _get_current_user_id(db)  # Manual call
```

**After:**
```python
async def get_recommendations_hybrid(
    db: Session = Depends(get_sync_db),
    user_id: UUID = Depends(_get_current_user_id),  # Dependency injection
):
    # user_id is now injected, no manual call needed
```

### Endpoints Fixed:
1. ✅ `get_recommendations_hybrid` - Main recommendation endpoint
2. ✅ `track_interaction` - Track user interactions
3. ✅ `get_profile` - Get user profile
4. ✅ `get_user_interactions` - Get interaction history
5. ✅ `update_profile` - Update user preferences
6. ✅ `submit_feedback` - Submit recommendation feedback
7. ✅ `refresh_recommendations` - Trigger recommendation refresh

### Step 2: Update Test Fixture Override ⚠️ IN PROGRESS
Updated `conftest.py` to override the dependency:
```python
app.dependency_overrides[_get_current_user_id] = lambda db=None: test_user.id
```

## Current Status

### What Works ✅
- All endpoints now use dependency injection properly
- Code structure is correct for FastAPI best practices
- Endpoints no longer call `_get_current_user_id(db)` directly

### What's Still Failing ⚠️
- Tests still get "no such table: users" error
- The dependency override isn't preventing the database query

### Why It's Still Failing
FastAPI is still trying to resolve the `db` dependency for `_get_current_user_id` even though we override the function. The issue is that `_get_current_user_id` has this signature:

```python
def _get_current_user_id(db: Session = Depends(get_sync_db)) -> UUID:
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    # ...
```

When FastAPI sees `Depends(_get_current_user_id)`, it:
1. Checks if `_get_current_user_id` is overridden → YES, use override
2. But the override is a lambda that doesn't match the signature
3. FastAPI gets confused about dependency resolution

## Next Steps

### Option A: Simplify _get_current_user_id (RECOMMENDED)
Remove the database dependency from `_get_current_user_id` entirely:

```python
def _get_current_user_id() -> UUID:
    """Get current user ID from request context (JWT token, session, etc.)"""
    # In production: extract from JWT token
    # For now: return a fixed test UUID
    return UUID("00000000-0000-0000-0000-000000000001")
```

Then create a separate startup function to ensure test user exists.

### Option B: Create Separate Test Dependency
Create a test-specific dependency that doesn't query the database:

```python
# In conftest.py
def get_test_user_id() -> UUID:
    return test_user.id

# Override
app.dependency_overrides[_get_current_user_id] = get_test_user_id
```

### Option C: Mock at Service Level
Instead of overriding the dependency, mock the database query itself.

## Recommendation
**Use Option A** - Simplify `_get_current_user_id` to not query the database. Authentication should come from request headers/tokens, not database queries. The current implementation is a temporary placeholder that's causing test issues.

## Files Modified
1. ✅ `backend/app/modules/recommendations/router.py` - All 7 endpoints updated
2. ✅ `backend/tests/conftest.py` - Dependency override added
3. ✅ `backend/pytest.ini` - Added `asyncio_mode = auto`

## Impact
- **Monitoring tests**: 33 tests now passing (pytest-asyncio fix)
- **Recommendation router tests**: 0/13 passing (dependency issue remains)
- **Other recommendation tests**: Not yet tested

## Time Spent
- Analysis: 15 minutes
- Implementation: 20 minutes
- Debugging: 25 minutes
- **Total**: ~60 minutes

## Lessons Learned
1. FastAPI dependency overrides require exact signature matching
2. Dependencies with their own dependencies are hard to override
3. Authentication logic should be simple and not query databases
4. Test fixtures need to be set up before app initialization
