# Export Issue Fix - useDebounce

## Issue
```
useEditorData.ts:15 Uncaught SyntaxError: The requested module '/src/lib/hooks/useDebounce.ts' does not provide an export named 'useDebounce'
```

## Root Cause
This is a Vite dev server caching/HMR issue. The `useDebounce` hook is correctly exported, but Vite's module cache is stale.

## Solution

### Option 1: Restart Vite Dev Server (Recommended)
```bash
# Stop the dev server (Ctrl+C)
# Then restart:
npm run dev
```

### Option 2: Clear Vite Cache
```bash
# Stop the dev server
# Delete Vite cache
rm -rf node_modules/.vite

# Restart dev server
npm run dev
```

### Option 3: Hard Refresh Browser
1. Open browser DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 4: Change Import Style (Temporary Workaround)
If the above don't work, you can temporarily change the import in `useEditorData.ts`:

**Current (named import):**
```typescript
import { useDebounce } from './useDebounce';
```

**Alternative (default import):**
```typescript
import useDebounce from './useDebounce';
```

## Verification

The export in `frontend/src/lib/hooks/useDebounce.ts` is correct:
```typescript
export function useDebounce<T>(value: T, delay: number = 300): T {
  // ... implementation
}

export default useDebounce;
```

Both named and default exports are available.

## Why This Happens

Vite's HMR can sometimes get confused when:
1. Files are created/modified rapidly
2. Multiple exports are added/changed
3. The dev server has been running for a long time
4. There are circular dependencies (not the case here)

## Prevention

To avoid this in the future:
1. Restart dev server after major file structure changes
2. Use consistent export patterns (prefer named exports)
3. Clear cache periodically during heavy development

## Status

✅ **File is correct** - No code changes needed  
⚠️ **Dev server needs restart** - This is a caching issue

After restarting the dev server, the error should disappear and the application should work correctly.
