# Task 5.3 Complete: Update Editor Store to Use Real Resource Data

**Status**: ✅ Complete  
**Date**: 2024-01-08  
**Task**: Update editor store to use real resource data  
**Requirements**: 3.1, 3.5, 3.6

## Summary

Successfully updated the editor store to integrate with the `useResource` hook from Task 5.2. Removed all mock data and added proper loading and error state management. The store now follows a clean separation of concerns where:
- The store manages UI state (active resource ID, loading, errors)
- TanStack Query hooks handle data fetching
- Components orchestrate the interaction between store and hooks

## Changes Made

### 1. Updated `frontend/src/stores/editor.ts`

**New State Properties**:
- ✅ `activeResourceId: string | null` - Tracks which resource to load
- ✅ `isLoading: boolean` - Loading state for resource fetching
- ✅ `error: Error | null` - Error state for failed requests

**New Actions**:
- ✅ `setActiveResource(resourceId)` - Set resource ID and trigger loading
- ✅ `setLoading(loading)` - Manually control loading state
- ✅ `setError(error)` - Set error state and clear loading
- ✅ `clearEditor()` - Reset all editor state

**Helper Function**:
- ✅ `resourceToCodeFile(resource)` - Convert backend Resource to frontend CodeFile

**Key Design Decisions**:
1. **Separation of Concerns**: Store manages UI state, hooks manage data fetching
2. **Two-Step Loading**: `setActiveResource()` sets ID + loading, then component uses `useResource()` hook
3. **Backward Compatible**: Existing `setActiveFile()` still works for direct file setting
4. **Error Handling**: Errors clear loading state automatically

### 2. Updated `frontend/src/stores/__tests__/editor.test.ts`

**New Test Suites**: 19 tests total (all passing ✅)
- ✅ Resource to CodeFile Conversion (3 tests)
- ✅ Active Resource Management (2 tests)
- ✅ Loading and Error States (3 tests)
- ✅ Clear Editor (1 test)
- ✅ Active File Management (2 tests) - existing
- ✅ Cursor Position (2 tests) - existing
- ✅ Selection (2 tests) - existing
- ✅ Scroll Position Persistence (4 tests) - existing

**Test Coverage**:
- Resource to CodeFile conversion with various edge cases
- Loading state management
- Error state management with automatic loading clear
- Clear editor functionality
- All existing tests still passing

## Requirements Validation

### ✅ Requirement 3.1: Resource Content Fetching
**Implementation**: Store provides `activeResourceId` that components use with `useResource()` hook
```typescript
// Component usage
const { activeResourceId } = useEditorStore();
const { data: resource, isLoading, error } = useResource(activeResourceId || '');
```

### ✅ Requirement 3.5: Loading States
**Implementation**: Store tracks loading state, components display loading indicators
```typescript
// Store provides loading state
const { isLoading, setLoading } = useEditorStore();

// Components can also use hook loading state
const { isLoading: hookLoading } = useResource(resourceId);
```

### ✅ Requirement 3.6: Error States
**Implementation**: Store tracks errors, components display error messages
```typescript
// Store provides error state
const { error, setError } = useEditorStore();

// Components can also use hook error state
const { error: hookError } = useResource(resourceId);
```

## Integration Pattern

### Pattern 1: Component-Driven Loading (Recommended)

```tsx
function EditorView() {
  const { activeResourceId, setActiveFile, setLoading, setError } = useEditorStore();
  
  // Use TanStack Query hook for data fetching
  const { data: resource, isLoading, error } = useResource(activeResourceId || '');
  
  // Sync hook state to store
  useEffect(() => {
    setLoading(isLoading);
  }, [isLoading, setLoading]);
  
  useEffect(() => {
    setError(error);
  }, [error, setError]);
  
  // Convert resource to CodeFile when loaded
  useEffect(() => {
    if (resource) {
      const codeFile = resourceToCodeFile(resource);
      setActiveFile(codeFile);
    }
  }, [resource, setActiveFile]);
  
  if (isLoading) return <EditorSkeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!resource) return <EmptyState />;
  
  return <MonacoEditor content={resource.content} />;
}
```

### Pattern 2: Store-Driven Loading (Alternative)

```tsx
function ResourceSelector({ resourceId }: { resourceId: string }) {
  const { setActiveResource } = useEditorStore();
  
  const handleSelect = () => {
    // Store sets loading state automatically
    setActiveResource(resourceId);
  };
  
  return <button onClick={handleSelect}>Open Resource</button>;
}

function EditorView() {
  const { activeResourceId, activeFile, isLoading, error } = useEditorStore();
  
  // Hook fetches data based on store's activeResourceId
  const { data: resource } = useResource(activeResourceId || '');
  
  // Another component syncs resource to store
  // (see ResourceSyncEffect component)
  
  if (isLoading) return <EditorSkeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!activeFile) return <EmptyState />;
  
  return <MonacoEditor content={activeFile.content} />;
}
```

## Usage Examples

### Example 1: Basic Resource Loading

```tsx
import { useEditorStore, resourceToCodeFile } from '@/stores/editor';
import { useResource } from '@/lib/hooks/useEditorData';

function EditorContainer({ resourceId }: { resourceId: string }) {
  const { setActiveResource, activeFile, isLoading, error } = useEditorStore();
  
  // Fetch resource data
  const { data: resource } = useResource(resourceId);
  
  // Set active resource on mount
  useEffect(() => {
    setActiveResource(resourceId);
  }, [resourceId, setActiveResource]);
  
  // Convert and set file when resource loads
  useEffect(() => {
    if (resource) {
      const codeFile = resourceToCodeFile(resource);
      setActiveFile(codeFile);
    }
  }, [resource]);
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!activeFile) return <div>No file loaded</div>;
  
  return <MonacoEditorWrapper file={activeFile} />;
}
```

### Example 2: Error Handling

```tsx
import { useEditorStore } from '@/stores/editor';
import { useResource } from '@/lib/hooks/useEditorData';

function EditorWithErrorHandling({ resourceId }: { resourceId: string }) {
  const { setError, error } = useEditorStore();
  const { data, error: hookError, refetch } = useResource(resourceId);
  
  // Sync hook error to store
  useEffect(() => {
    setError(hookError);
  }, [hookError, setError]);
  
  if (error) {
    return (
      <div className="error-container">
        <p>Failed to load resource: {error.message}</p>
        <button onClick={() => refetch()}>Retry</button>
      </div>
    );
  }
  
  return <MonacoEditorWrapper resource={data} />;
}
```

### Example 3: Loading States

```tsx
import { useEditorStore } from '@/stores/editor';
import { useResource } from '@/lib/hooks/useEditorData';

function EditorWithLoadingStates({ resourceId }: { resourceId: string }) {
  const { isLoading, setLoading } = useEditorStore();
  const { data, isLoading: hookLoading } = useResource(resourceId);
  
  // Sync hook loading to store
  useEffect(() => {
    setLoading(hookLoading);
  }, [hookLoading, setLoading]);
  
  return (
    <div>
      {isLoading && <LoadingSpinner />}
      {!isLoading && data && <MonacoEditorWrapper resource={data} />}
    </div>
  );
}
```

### Example 4: Clear Editor on Unmount

```tsx
import { useEditorStore } from '@/stores/editor';

function EditorPage() {
  const { clearEditor } = useEditorStore();
  
  // Clear editor when leaving page
  useEffect(() => {
    return () => {
      clearEditor();
    };
  }, [clearEditor]);
  
  return <EditorContainer />;
}
```

## Test Results

```
✓ src/stores/__tests__/editor.test.ts (19 tests) 259ms
  ✓ Editor Store (19)
    ✓ Resource to CodeFile Conversion (3)
      ✓ should convert Resource to CodeFile 9ms
      ✓ should handle Resource without file_path 3ms
      ✓ should handle Resource with no content 1ms
    ✓ Active Resource Management (2)
      ✓ should set active resource ID and loading state 2ms
      ✓ should clear loading state when resource ID is null 1ms
    ✓ Active File Management (2)
      ✓ should set active file 1ms
      ✓ should clear active file 1ms
    ✓ Loading and Error States (3)
      ✓ should set loading state 1ms
      ✓ should set error state and clear loading 1ms
      ✓ should clear error state 1ms
    ✓ Clear Editor (1)
      ✓ should clear all editor state 1ms
    ✓ Cursor Position (2)
      ✓ should update cursor position 1ms
      ✓ should handle multiple cursor position updates 1ms
    ✓ Selection (2)
      ✓ should update selection 0ms
      ✓ should clear selection 1ms
    ✓ Scroll Position Persistence (4)
      ✓ should update scroll position for active file 1ms
      ✓ should restore scroll position when switching files 108ms
      ✓ should persist scroll positions to localStorage 109ms
      ✓ should restore scroll position using restoreScrollPosition 2ms

Test Files  1 passed (1)
Tests  19 passed (19)
```

## Design Patterns

### 1. Separation of Concerns
- **Store**: Manages UI state (active resource, loading, errors)
- **Hooks**: Manage data fetching and caching
- **Components**: Orchestrate store + hooks

### 2. Two-Phase Loading
```
Phase 1: setActiveResource(id) → sets ID + loading state
Phase 2: useResource(id) → fetches data from API
```

### 3. Error Handling
- Errors automatically clear loading state
- Components can use store error OR hook error
- Store error persists across re-renders

### 4. Backward Compatibility
- Existing `setActiveFile()` still works
- Scroll position persistence unchanged
- Cursor/selection management unchanged

## Migration Guide

### Before (Mock Data)
```typescript
// Old pattern - direct file setting
const mockFile = { id: '1', content: 'mock' };
setActiveFile(mockFile);
```

### After (Real Data)
```typescript
// New pattern - resource ID + hook
setActiveResource('resource-1');
const { data: resource } = useResource('resource-1');
const codeFile = resourceToCodeFile(resource);
setActiveFile(codeFile);
```

## Next Steps

Task 5.3 is complete. Ready to proceed with:
- **Task 5.4**: Update annotation store to use annotation hooks
- **Task 5.5**: Update quality store to use quality hooks
- **Task 5.6**: Update chunk store to use chunk hooks
- **Task 6.x**: Integrate stores with actual editor components

## Notes

- All 19 tests passing with comprehensive coverage
- Store now ready for real backend integration
- Helper function `resourceToCodeFile()` exported for component use
- Loading and error states properly managed
- Backward compatible with existing editor functionality
- Clear separation between store state and data fetching

