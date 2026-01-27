# Epic 3 Custom Hooks - Test Fixes Complete ✅

## Problem Summary

All 12 tests in `useCollections.test.tsx` were failing with the error:
```
Error: Failed to load url /src/lib/hooks/useCollections.ts (resolved id: /src/lib/hooks/useCollections.ts). Does the file exist?
```

This was a Vitest module resolution issue caused by mocking the Zustand store, which created a circular dependency or module resolution conflict.

## Root Cause

The test file was mocking both:
1. `@/lib/api/collections` (API layer) ✅ Correct
2. `@/stores/collections` (Zustand store) ❌ Problematic

When Vitest tried to mock the store, it broke the import chain for `useCollections` because:
- The hook imports from the store
- The store was being mocked
- Vitest couldn't resolve the module graph

## Solution

**Remove store mocking** - Only mock the API layer, not the store.

### Before (Broken)
```typescript
// Mock both API and store
vi.mock('@/lib/api/collections', () => ({ ... }));
vi.mock('@/stores/collections', () => ({ ... })); // ❌ Causes issues
```

### After (Fixed)
```typescript
// Only mock the API layer
vi.mock('@/lib/api/collections', () => ({
  collectionsApi: {
    listCollections: vi.fn(),
    createCollection: vi.fn(),
    updateCollection: vi.fn(),
    deleteCollection: vi.fn(),
    batchAddResources: vi.fn(),
    batchRemoveResources: vi.fn(),
  },
}));
// No store mocking needed - let it work naturally
```

## Test Results

### Before Fix
```
❌ FAIL  src/lib/hooks/__tests__/useCollections.test.tsx
Error: Failed to load url /src/lib/hooks/useCollections.ts
Tests: 0 passed, 12 failed
```

### After Fix
```
✅ PASS  src/lib/hooks/__tests__/useCollections.test.tsx
Tests: 12 passed (12)
  ✓ fetching collections (2)
  ✓ creating collections (2)
  ✓ updating collections (2)
  ✓ deleting collections (2)
  ✓ batch operations (3)
  ✓ refetch (1)
```

### Full Test Suite Results
```
✅ Test Files  5 passed (5)
✅ Tests  68 passed (68)
   - useDocuments: 10/10 ✅
   - usePDFViewer: 25/25 ✅
   - useScholarlyAssets: 10/10 ✅
   - useCollections: 12/12 ✅
   - useAutoLinking: 11/11 ✅
```

## Key Learnings

### 1. Mock Only External Dependencies
- ✅ Mock API clients (external HTTP calls)
- ✅ Mock third-party services
- ❌ Don't mock internal stores (Zustand, Redux, etc.)
- ❌ Don't mock hooks being tested

### 2. Vitest Module Resolution
- Mocking creates a new module graph
- Circular dependencies break resolution
- Keep mocking minimal and targeted

### 3. Store Integration Testing
- Stores should work naturally in tests
- Use real store instances with test data
- Clean up store state between tests if needed

### 4. Test Isolation Strategy
```typescript
// Good: Mock external API
vi.mock('@/lib/api/collections', () => ({ ... }));

// Good: Use real store
import { useCollectionsStore } from '@/stores/collections';

// Good: Clean up between tests
beforeEach(() => {
  queryClient = new QueryClient({ ... });
  vi.clearAllMocks();
});

afterEach(() => {
  queryClient.clear();
});
```

## Files Modified

### Test File
- `frontend/src/lib/hooks/__tests__/useCollections.test.tsx` (320 lines)
  - Removed store mocking
  - Kept API mocking
  - All 12 tests now passing

### Temporary Files Cleaned Up
- `frontend/src/lib/hooks/__tests__/useCollections.simple.test.tsx` (deleted)

## Impact

### Before
- 56/68 tests passing (82%)
- useCollections completely broken
- Blocking Epic 3 completion

### After
- 68/68 tests passing (100%) ✅
- All hooks fully tested
- Epic 3 complete and ready for Epic 4

## Verification Steps

1. Run all hook tests:
   ```bash
   npm test -- src/lib/hooks/__tests__/ --run
   ```

2. Verify useCollections specifically:
   ```bash
   npm test -- src/lib/hooks/__tests__/useCollections.test.tsx --run
   ```

3. Check test coverage:
   ```bash
   npm test -- --coverage src/lib/hooks/
   ```

## Related Documentation

- [Epic 3 Complete Summary](./EPIC_3_CUSTOM_HOOKS_COMPLETE.md)
- [Phase 3 Tasks](./.kiro/specs/frontend/phase3-living-library/tasks.md)
- [Vitest Mocking Guide](https://vitest.dev/guide/mocking.html)

## Recommendations for Future Tests

### Do's ✅
1. Mock external APIs and services
2. Use real stores with test data
3. Clean up between tests
4. Test one concern at a time
5. Use `vi.clearAllMocks()` in `beforeEach`

### Don'ts ❌
1. Don't mock internal stores
2. Don't mock the hook being tested
3. Don't create circular mock dependencies
4. Don't share state between tests
5. Don't mock everything "just in case"

## Timeline

- **Issue Discovered**: During Epic 3 implementation
- **Root Cause Identified**: Store mocking causing module resolution failure
- **Fix Applied**: Removed store mocking, kept API mocking only
- **Verification**: All 68 tests passing
- **Status**: ✅ RESOLVED

---

**Status**: ✅ COMPLETE  
**Date**: January 27, 2026  
**Tests Fixed**: 12/12 useCollections tests  
**Total Tests Passing**: 68/68 (100%)  
**Epic 3 Status**: ✅ COMPLETE
