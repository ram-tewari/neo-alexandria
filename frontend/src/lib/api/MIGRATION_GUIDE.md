# Migration Guide: Zustand Stores to TanStack Query Hooks

## Overview

This guide helps migrate from manual caching in Zustand stores to automatic caching with TanStack Query hooks. The new approach provides better performance through automatic request deduplication, smart caching, and prefetching.

## Benefits of Migration

### Before (Zustand Stores)
- ❌ Manual cache management
- ❌ Manual request deduplication
- ❌ Manual error handling and retries
- ❌ Manual optimistic updates with rollback logic
- ❌ No automatic background refetching
- ❌ No prefetching support

### After (TanStack Query Hooks)
- ✅ Automatic cache management
- ✅ Automatic request deduplication
- ✅ Built-in error handling and retries
- ✅ Built-in optimistic updates with rollback
- ✅ Automatic background refetching
- ✅ Built-in prefetching support

## Migration Steps

### Step 1: Replace Fetch Operations

#### Before (Zustand Store)
```typescript
import { useAnnotationStore } from '@/stores/annotation';

function AnnotationList({ resourceId }: { resourceId: string }) {
  const { annotations, isLoading, error, fetchAnnotations } = useAnnotationStore();

  useEffect(() => {
    fetchAnnotations(resourceId);
  }, [resourceId, fetchAnnotations]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return <ul>{annotations.map(...)}</ul>;
}
```

#### After (TanStack Query)
```typescript
import { useAnnotations } from '@/lib/api/editor-queries';

function AnnotationList({ resourceId }: { resourceId: string }) {
  const { data: annotations, isLoading, error } = useAnnotations(resourceId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <ul>{annotations?.map(...)}</ul>;
}
```

**Benefits:**
- No manual `useEffect` needed
- Automatic caching and deduplication
- Cleaner, more declarative code

---

### Step 2: Replace Create Operations

#### Before (Zustand Store)
```typescript
import { useAnnotationStore } from '@/stores/annotation';

function CreateButton({ resourceId }: { resourceId: string }) {
  const { createAnnotation, isLoading } = useAnnotationStore();

  const handleCreate = async () => {
    try {
      await createAnnotation(resourceId, {
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'text',
      });
    } catch (error) {
      console.error('Failed:', error);
    }
  };

  return (
    <button onClick={handleCreate} disabled={isLoading}>
      Create
    </button>
  );
}
```

#### After (TanStack Query)
```typescript
import { useCreateAnnotation } from '@/lib/api/editor-queries';

function CreateButton({ resourceId }: { resourceId: string }) {
  const createAnnotation = useCreateAnnotation();

  const handleCreate = async () => {
    try {
      await createAnnotation.mutateAsync({
        resourceId,
        data: {
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'text',
        },
      });
    } catch (error) {
      console.error('Failed:', error);
    }
  };

  return (
    <button onClick={handleCreate} disabled={createAnnotation.isPending}>
      Create
    </button>
  );
}
```

**Benefits:**
- Automatic optimistic updates
- Automatic rollback on error
- Better loading state management

---

### Step 3: Replace Update Operations

#### Before (Zustand Store)
```typescript
import { useAnnotationStore } from '@/stores/annotation';

function EditButton({ annotationId }: { annotationId: string }) {
  const { updateAnnotation } = useAnnotationStore();

  const handleUpdate = async () => {
    await updateAnnotation(annotationId, { note: 'Updated' });
  };

  return <button onClick={handleUpdate}>Update</button>;
}
```

#### After (TanStack Query)
```typescript
import { useUpdateAnnotation } from '@/lib/api/editor-queries';

function EditButton({ annotationId }: { annotationId: string }) {
  const updateAnnotation = useUpdateAnnotation();

  const handleUpdate = async () => {
    await updateAnnotation.mutateAsync({
      annotationId,
      data: { note: 'Updated' },
    });
  };

  return <button onClick={handleUpdate}>Update</button>;
}
```

---

### Step 4: Replace Delete Operations

#### Before (Zustand Store)
```typescript
import { useAnnotationStore } from '@/stores/annotation';

function DeleteButton({ annotationId }: { annotationId: string }) {
  const { deleteAnnotation } = useAnnotationStore();

  return (
    <button onClick={() => deleteAnnotation(annotationId)}>
      Delete
    </button>
  );
}
```

#### After (TanStack Query)
```typescript
import { useDeleteAnnotation } from '@/lib/api/editor-queries';

function DeleteButton({ annotationId }: { annotationId: string }) {
  const deleteAnnotation = useDeleteAnnotation();

  return (
    <button onClick={() => deleteAnnotation.mutate(annotationId)}>
      Delete
    </button>
  );
}
```

---

### Step 5: Add Prefetching

#### New Feature (Not Available in Zustand)
```typescript
import { usePrefetchEditorData } from '@/lib/api/editor-queries';

function FileTreeItem({ resourceId, fileName }: Props) {
  const prefetchEditorData = usePrefetchEditorData();

  // Prefetch data on hover for instant loading
  const handleMouseEnter = () => {
    prefetchEditorData(resourceId);
  };

  return (
    <div onMouseEnter={handleMouseEnter}>
      {fileName}
    </div>
  );
}
```

**Benefits:**
- Data loads before user clicks
- Makes UI feel instant
- Parallel data loading

---

### Step 6: Handle Request Deduplication

#### Before (Zustand Store)
```typescript
// Multiple components calling fetchAnnotations
// Results in multiple API calls

function ComponentA({ resourceId }: Props) {
  const { fetchAnnotations } = useAnnotationStore();
  useEffect(() => {
    fetchAnnotations(resourceId); // API call 1
  }, [resourceId]);
}

function ComponentB({ resourceId }: Props) {
  const { fetchAnnotations } = useAnnotationStore();
  useEffect(() => {
    fetchAnnotations(resourceId); // API call 2 (duplicate!)
  }, [resourceId]);
}
```

#### After (TanStack Query)
```typescript
// Multiple components using same query
// Results in ONE API call (automatic deduplication)

function ComponentA({ resourceId }: Props) {
  const { data } = useAnnotations(resourceId); // Shares request
}

function ComponentB({ resourceId }: Props) {
  const { data } = useAnnotations(resourceId); // Shares request
}
```

**Benefits:**
- Automatic request deduplication
- Reduced server load
- Better performance

---

## Complete Migration Example

### Before: Zustand Store Component

```typescript
import { useEffect } from 'react';
import { useAnnotationStore } from '@/stores/annotation';
import { useChunkStore } from '@/stores/chunk';
import { useQualityStore } from '@/stores/quality';

function EditorView({ resourceId }: { resourceId: string }) {
  const {
    annotations,
    isLoading: annotationsLoading,
    error: annotationsError,
    fetchAnnotations,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
  } = useAnnotationStore();

  const {
    chunks,
    isLoading: chunksLoading,
    fetchChunks,
  } = useChunkStore();

  const {
    qualityData,
    isLoading: qualityLoading,
    fetchQualityData,
  } = useQualityStore();

  // Manual fetching
  useEffect(() => {
    fetchAnnotations(resourceId);
    fetchChunks(resourceId);
    fetchQualityData(resourceId);
  }, [resourceId]);

  const handleCreate = async () => {
    await createAnnotation(resourceId, {
      start_offset: 0,
      end_offset: 10,
      highlighted_text: 'text',
    });
  };

  const isLoading = annotationsLoading || chunksLoading || qualityLoading;

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <div>Annotations: {annotations.length}</div>
      <div>Chunks: {chunks.length}</div>
      <div>Quality: {qualityData?.quality_overall}</div>
      <button onClick={handleCreate}>Create</button>
    </div>
  );
}
```

### After: TanStack Query Component

```typescript
import {
  useAnnotations,
  useChunks,
  useQualityDetails,
  useCreateAnnotation,
} from '@/lib/api/editor-queries';

function EditorView({ resourceId }: { resourceId: string }) {
  // Automatic fetching, caching, and deduplication
  const annotationsQuery = useAnnotations(resourceId);
  const chunksQuery = useChunks(resourceId);
  const qualityQuery = useQualityDetails(resourceId);
  const createAnnotation = useCreateAnnotation();

  const handleCreate = async () => {
    await createAnnotation.mutateAsync({
      resourceId,
      data: {
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'text',
      },
    });
  };

  const isLoading =
    annotationsQuery.isLoading ||
    chunksQuery.isLoading ||
    qualityQuery.isLoading;

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <div>Annotations: {annotationsQuery.data?.length}</div>
      <div>Chunks: {chunksQuery.data?.length}</div>
      <div>Quality: {qualityQuery.data?.quality_overall}</div>
      <button onClick={handleCreate}>Create</button>
    </div>
  );
}
```

**Improvements:**
- ✅ No manual `useEffect` needed
- ✅ Automatic caching (5-15 minutes depending on data type)
- ✅ Automatic request deduplication
- ✅ Automatic optimistic updates
- ✅ Automatic error handling and retries
- ✅ Cleaner, more maintainable code

---

## Cache Configuration

### Cache Times by Data Type

| Data Type | Stale Time | Cache Time | Rationale |
|-----------|------------|------------|-----------|
| Annotations | 5 minutes | 10 minutes | Changes frequently |
| Chunks | 10 minutes | 30 minutes | Changes less frequently |
| Quality | 15 minutes | 30 minutes | Changes infrequently |
| Graph/Node2Vec | 30 minutes | 60 minutes | Rarely changes |

### What These Mean

- **Stale Time**: How long data is considered fresh (no refetch)
- **Cache Time**: How long unused data stays in memory

---

## Advanced Patterns

### Pattern 1: Conditional Queries

```typescript
function QualityBadges({ resourceId, visible }: Props) {
  // Only fetch when visible
  const { data } = useQualityDetails(resourceId, {
    enabled: visible,
  });

  if (!visible) return null;
  return <div>{data?.quality_overall}</div>;
}
```

### Pattern 2: Prefetching on Hover

```typescript
function FileTree({ files }: Props) {
  const prefetchEditorData = usePrefetchEditorData();

  return (
    <ul>
      {files.map((file) => (
        <li
          key={file.id}
          onMouseEnter={() => prefetchEditorData(file.resourceId)}
        >
          {file.name}
        </li>
      ))}
    </ul>
  );
}
```

### Pattern 3: Manual Cache Invalidation

```typescript
function RefreshButton({ resourceId }: Props) {
  const invalidateEditorData = useInvalidateEditorData();

  return (
    <button onClick={() => invalidateEditorData(resourceId)}>
      Refresh
    </button>
  );
}
```

---

## Troubleshooting

### Issue: Data not updating after mutation

**Solution:** Mutations automatically update the cache. If you need manual control:

```typescript
const queryClient = useQueryClient();

// Invalidate specific query
queryClient.invalidateQueries({ 
  queryKey: ['annotations', resourceId] 
});

// Or use the helper
const invalidate = useInvalidateEditorData();
invalidate(resourceId);
```

### Issue: Too many API calls

**Solution:** Check if you're using the same query key. TanStack Query deduplicates by query key.

```typescript
// ✅ Good - same query key, one request
useAnnotations('res-1');
useAnnotations('res-1');

// ❌ Bad - different query keys, two requests
useAnnotations('res-1');
useAnnotations('res-2');
```

### Issue: Stale data showing

**Solution:** Adjust stale time or invalidate manually:

```typescript
// Shorter stale time
useAnnotations(resourceId, {
  staleTime: 1 * 60 * 1000, // 1 minute
});

// Or force refetch
const { refetch } = useAnnotations(resourceId);
refetch();
```

---

## Testing

### Before (Zustand Store)
```typescript
// Mock Zustand store
vi.mock('@/stores/annotation', () => ({
  useAnnotationStore: () => ({
    annotations: [mockAnnotation],
    fetchAnnotations: vi.fn(),
  }),
}));
```

### After (TanStack Query)
```typescript
// Wrap with QueryClientProvider
const queryClient = new QueryClient();

render(
  <QueryClientProvider client={queryClient}>
    <Component />
  </QueryClientProvider>
);
```

---

## Checklist

- [ ] Replace `fetchAnnotations` with `useAnnotations`
- [ ] Replace `createAnnotation` with `useCreateAnnotation`
- [ ] Replace `updateAnnotation` with `useUpdateAnnotation`
- [ ] Replace `deleteAnnotation` with `useDeleteAnnotation`
- [ ] Replace `fetchChunks` with `useChunks`
- [ ] Replace `fetchQualityData` with `useQualityDetails`
- [ ] Add prefetching where appropriate
- [ ] Remove manual `useEffect` calls
- [ ] Update tests to use QueryClientProvider
- [ ] Remove Zustand stores (optional, can keep for UI state)

---

## Next Steps

1. Start with read-only queries (useAnnotations, useChunks, useQualityDetails)
2. Migrate mutations (create, update, delete)
3. Add prefetching for better UX
4. Remove old Zustand store code
5. Update tests

---

## Questions?

See:
- [TanStack Query Hooks](./editor-queries.ts)
- [Usage Examples](./editor-queries.example.tsx)
- [Tests](./editor-queries.test.tsx)
