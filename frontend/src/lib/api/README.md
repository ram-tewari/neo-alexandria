# Editor API Client with TanStack Query

## Overview

This directory contains the API client for editor features with automatic caching, prefetching, and request deduplication powered by TanStack Query.

## Files

- **`editor.ts`** - Raw API client with Axios calls and type definitions
- **`editor-queries.ts`** - TanStack Query hooks with automatic caching
- **`editor-queries.example.tsx`** - Usage examples and patterns
- **`editor-queries.test.tsx`** - Comprehensive tests for caching behavior
- **`MIGRATION_GUIDE.md`** - Guide for migrating from Zustand stores
- **`index.ts`** - Central export point

## Quick Start

### Basic Query

```typescript
import { useAnnotations } from '@/lib/api/editor-queries';

function AnnotationList({ resourceId }: { resourceId: string }) {
  const { data, isLoading, error } = useAnnotations(resourceId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <ul>{data?.map(...)}</ul>;
}
```

### Mutation with Optimistic Update

```typescript
import { useCreateAnnotation } from '@/lib/api/editor-queries';

function CreateButton({ resourceId }: { resourceId: string }) {
  const createAnnotation = useCreateAnnotation();

  const handleCreate = async () => {
    await createAnnotation.mutateAsync({
      resourceId,
      data: { /* annotation data */ },
    });
  };

  return (
    <button onClick={handleCreate} disabled={createAnnotation.isPending}>
      Create
    </button>
  );
}
```

### Prefetching

```typescript
import { usePrefetchEditorData } from '@/lib/api/editor-queries';

function FileTreeItem({ resourceId, fileName }: Props) {
  const prefetchEditorData = usePrefetchEditorData();

  return (
    <div onMouseEnter={() => prefetchEditorData(resourceId)}>
      {fileName}
    </div>
  );
}
```

## Features

### 1. Automatic Caching

Data is automatically cached with configurable stale and cache times:

| Data Type | Stale Time | Cache Time |
|-----------|------------|------------|
| Annotations | 5 minutes | 10 minutes |
| Chunks | 10 minutes | 30 minutes |
| Quality | 15 minutes | 30 minutes |
| Graph | 30 minutes | 60 minutes |

**Stale Time**: How long data is considered fresh (no background refetch)
**Cache Time**: How long unused data stays in memory

### 2. Request Deduplication

Multiple components requesting the same data share a single API call:

```typescript
// Both components share ONE API call
function ComponentA({ resourceId }: Props) {
  const { data } = useAnnotations(resourceId);
}

function ComponentB({ resourceId }: Props) {
  const { data } = useAnnotations(resourceId);
}
```

### 3. Optimistic Updates

Mutations update the UI immediately before the API responds:

```typescript
const createAnnotation = useCreateAnnotation();

// UI updates immediately, then syncs with server
await createAnnotation.mutateAsync({ resourceId, data });
```

If the API call fails, changes are automatically rolled back.

### 4. Prefetching

Load data before it's needed for instant UI:

```typescript
const prefetchEditorData = usePrefetchEditorData();

// Prefetch on hover
<div onMouseEnter={() => prefetchEditorData(resourceId)}>
```

### 5. Background Refetching

Stale data is automatically refetched in the background:

```typescript
// Shows cached data immediately
// Refetches in background if stale
const { data } = useAnnotations(resourceId);
```

### 6. Error Handling

Built-in retry logic and stale data fallback:

```typescript
const { data, error } = useAnnotations(resourceId, {
  retry: 1, // Retry once on failure
  staleTime: 5 * 60 * 1000, // Show stale data during errors
});

// Data is available even during errors (stale data)
if (error && data) {
  return <div>Showing cached data. {error.message}</div>;
}
```

## Available Hooks

### Queries (Read Operations)

- **`useAnnotations(resourceId)`** - Fetch all annotations for a resource
- **`useAnnotation(annotationId)`** - Fetch single annotation
- **`useAnnotationSearch(params)`** - Search annotations
- **`useChunks(resourceId)`** - Fetch semantic chunks
- **`useChunk(chunkId)`** - Fetch single chunk
- **`useQualityDetails(resourceId)`** - Fetch quality data
- **`useNode2VecSummary(resourceId, symbol)`** - Fetch Node2Vec summary
- **`useGraphConnections(symbol)`** - Fetch graph connections

### Mutations (Write Operations)

- **`useCreateAnnotation()`** - Create annotation with optimistic update
- **`useUpdateAnnotation()`** - Update annotation with optimistic update
- **`useDeleteAnnotation()`** - Delete annotation with optimistic update
- **`useRecalculateQuality()`** - Recalculate quality scores

### Utilities

- **`usePrefetchChunks()`** - Prefetch chunks for a resource
- **`usePrefetchQualityDetails()`** - Prefetch quality data
- **`usePrefetchEditorData()`** - Prefetch all editor data (annotations, chunks, quality)
- **`useInvalidateEditorData()`** - Force refetch of all editor data

## Cache Configuration

### Default Configuration

```typescript
export const editorCacheConfig = {
  annotations: {
    staleTime: 5 * 60 * 1000,  // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  chunks: {
    staleTime: 10 * 60 * 1000,  // 10 minutes
    cacheTime: 30 * 60 * 1000,  // 30 minutes
  },
  quality: {
    staleTime: 15 * 60 * 1000,  // 15 minutes
    cacheTime: 30 * 60 * 1000,  // 30 minutes
  },
  graph: {
    staleTime: 30 * 60 * 1000,  // 30 minutes
    cacheTime: 60 * 60 * 1000,  // 60 minutes
  },
};
```

### Custom Configuration

Override defaults per query:

```typescript
const { data } = useAnnotations(resourceId, {
  staleTime: 1 * 60 * 1000, // 1 minute
  gcTime: 5 * 60 * 1000,    // 5 minutes
  refetchOnWindowFocus: true,
});
```

## Query Keys

Query keys are used for caching and invalidation:

```typescript
export const editorQueryKeys = {
  annotations: (resourceId: string) => ['annotations', resourceId],
  annotation: (annotationId: string) => ['annotation', annotationId],
  chunks: (resourceId: string) => ['chunks', resourceId],
  chunk: (chunkId: string) => ['chunk', chunkId],
  quality: (resourceId: string) => ['quality', resourceId],
  node2vec: (symbol: string) => ['node2vec', symbol],
  connections: (symbol: string) => ['connections', symbol],
};
```

## Performance Benefits

### 1. Reduced API Calls

**Before (Zustand):**
- 3 components fetch annotations = 3 API calls
- No caching between page navigations
- Manual cache management

**After (TanStack Query):**
- 3 components fetch annotations = 1 API call (deduplication)
- Automatic caching between page navigations
- Automatic cache management

### 2. Faster Perceived Performance

**Before:**
- User clicks file → Loading spinner → Data appears
- ~500ms perceived latency

**After:**
- User hovers file → Prefetch starts
- User clicks file → Data appears instantly (from cache)
- ~0ms perceived latency

### 3. Better UX During Errors

**Before:**
- API fails → Error message → No data shown
- User loses context

**After:**
- API fails → Stale data shown with warning
- User keeps context, can retry

## Testing

### Test Setup

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

const { result } = renderHook(
  () => useAnnotations('res-1'),
  { wrapper }
);
```

### Test Examples

See `editor-queries.test.tsx` for comprehensive test examples covering:
- Caching behavior
- Request deduplication
- Optimistic updates
- Prefetching
- Error handling
- Cache invalidation

## Migration from Zustand

See `MIGRATION_GUIDE.md` for detailed migration instructions.

### Quick Migration

1. Replace `fetchAnnotations` with `useAnnotations`
2. Replace `createAnnotation` with `useCreateAnnotation`
3. Remove manual `useEffect` calls
4. Add prefetching where appropriate

## Troubleshooting

### Data not updating

```typescript
// Force refetch
const { refetch } = useAnnotations(resourceId);
refetch();

// Or invalidate cache
const invalidate = useInvalidateEditorData();
invalidate(resourceId);
```

### Too many API calls

Check query keys - different keys = different requests:

```typescript
// ✅ Same key, one request
useAnnotations('res-1');
useAnnotations('res-1');

// ❌ Different keys, two requests
useAnnotations('res-1');
useAnnotations('res-2');
```

### Stale data showing

Adjust stale time or force refetch:

```typescript
// Shorter stale time
useAnnotations(resourceId, {
  staleTime: 1 * 60 * 1000, // 1 minute
});
```

## Resources

- [TanStack Query Docs](https://tanstack.com/query/latest)
- [Usage Examples](./editor-queries.example.tsx)
- [Migration Guide](./MIGRATION_GUIDE.md)
- [Tests](./editor-queries.test.tsx)

## Requirements Satisfied

This implementation satisfies Phase 2 requirements:

- **7.3**: Lazy-loading for quality badges (conditional queries)
- **7.4**: Debounced hover requests (300ms debounce in hover card component)
- **16.3**: API caching with TanStack Query
  - Configured cache times (5-30 minutes)
  - Prefetching for active file chunks
  - Request deduplication

## Next Steps

1. Migrate existing components from Zustand stores
2. Add prefetching to file tree navigation
3. Implement debounced hover cards with Node2Vec queries
4. Monitor cache hit rates in production
