# Library API Integration Guide

## Overview

This guide covers the API integration patterns used in the Living Library feature, including error handling, caching strategies, optimistic updates, and best practices.

---

## Architecture

### Tech Stack

- **React Query (TanStack Query)**: Server state management
- **Zustand**: Client state management
- **Axios**: HTTP client
- **React**: UI framework

### Data Flow

```
Component → Custom Hook → API Client → Backend
     ↓           ↓            ↓
  Zustand ← React Query ← Response
```

---

## API Clients

### Base Configuration

```typescript
// src/lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Library API Client

```typescript
// src/lib/api/library.ts
import { apiClient } from './client';
import type { Resource, ResourceCreate, ResourceUpdate } from '@/types/library';

export const libraryApi = {
  // Get all documents
  getDocuments: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    type?: string;
  }): Promise<Resource[]> => {
    const { data } = await apiClient.get('/resources', { params });
    return data;
  },

  // Get single document
  getDocument: async (id: string): Promise<Resource> => {
    const { data } = await apiClient.get(`/resources/${id}`);
    return data;
  },

  // Create document
  createDocument: async (document: ResourceCreate): Promise<Resource> => {
    const { data } = await apiClient.post('/resources', document);
    return data;
  },

  // Update document
  updateDocument: async (id: string, updates: ResourceUpdate): Promise<Resource> => {
    const { data } = await apiClient.put(`/resources/${id}`, updates);
    return data;
  },

  // Delete document
  deleteDocument: async (id: string): Promise<void> => {
    await apiClient.delete(`/resources/${id}`);
  },

  // Upload file
  uploadFile: async (file: File, onProgress?: (progress: number) => void): Promise<Resource> => {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await apiClient.post('/resources/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          onProgress?.(progress);
        }
      },
    });

    return data;
  },
};
```

---

## Custom Hooks

### useDocuments Hook

```typescript
// src/lib/hooks/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { libraryApi } from '@/lib/api/library';
import type { Resource, ResourceCreate, ResourceUpdate } from '@/types/library';

export function useDocuments(params?: {
  skip?: number;
  limit?: number;
  search?: string;
  type?: string;
}) {
  const queryClient = useQueryClient();

  // Fetch documents
  const {
    data: documents = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['documents', params],
    queryFn: () => libraryApi.getDocuments(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });

  // Create document
  const createDocument = useMutation({
    mutationFn: (document: ResourceCreate) => libraryApi.createDocument(document),
    onSuccess: (newDocument) => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      
      // Optimistically add to cache
      queryClient.setQueryData<Resource[]>(['documents', params], (old = []) => [
        newDocument,
        ...old,
      ]);
    },
  });

  // Update document
  const updateDocument = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: ResourceUpdate }) =>
      libraryApi.updateDocument(id, updates),
    onMutate: async ({ id, updates }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['documents'] });

      // Snapshot previous value
      const previousDocuments = queryClient.getQueryData<Resource[]>(['documents', params]);

      // Optimistically update
      queryClient.setQueryData<Resource[]>(['documents', params], (old = []) =>
        old.map((doc) => (doc.id === id ? { ...doc, ...updates } : doc))
      );

      return { previousDocuments };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousDocuments) {
        queryClient.setQueryData(['documents', params], context.previousDocuments);
      }
    },
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  // Delete document
  const deleteDocument = useMutation({
    mutationFn: (id: string) => libraryApi.deleteDocument(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['documents'] });

      const previousDocuments = queryClient.getQueryData<Resource[]>(['documents', params]);

      queryClient.setQueryData<Resource[]>(['documents', params], (old = []) =>
        old.filter((doc) => doc.id !== id)
      );

      return { previousDocuments };
    },
    onError: (err, variables, context) => {
      if (context?.previousDocuments) {
        queryClient.setQueryData(['documents', params], context.previousDocuments);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  return {
    documents,
    isLoading,
    error,
    refetch,
    createDocument: createDocument.mutate,
    updateDocument: updateDocument.mutate,
    deleteDocument: deleteDocument.mutate,
    isCreating: createDocument.isPending,
    isUpdating: updateDocument.isPending,
    isDeleting: deleteDocument.isPending,
  };
}
```

---

## Caching Strategy

### Query Keys

Use hierarchical query keys for efficient invalidation:

```typescript
// Good: Hierarchical keys
['documents']                          // All documents
['documents', { search: 'react' }]     // Filtered documents
['documents', 'detail', id]            // Single document
['collections']                        // All collections
['collections', 'detail', id]          // Single collection
['collections', id, 'documents']       // Documents in collection

// Bad: Flat keys
['all-documents']
['filtered-documents-react']
['document-123']
```

### Stale Time vs Cache Time

```typescript
useQuery({
  queryKey: ['documents'],
  queryFn: fetchDocuments,
  staleTime: 5 * 60 * 1000,  // 5 minutes - data considered fresh
  cacheTime: 10 * 60 * 1000, // 10 minutes - cache kept in memory
});
```

**Stale Time**: How long data is considered fresh
- Short (1-2 min): Frequently changing data
- Medium (5-10 min): Moderately changing data
- Long (30+ min): Rarely changing data

**Cache Time**: How long unused data stays in memory
- Should be longer than stale time
- Prevents unnecessary refetches
- Balances memory usage

### Invalidation Patterns

```typescript
// Invalidate all documents
queryClient.invalidateQueries({ queryKey: ['documents'] });

// Invalidate specific document
queryClient.invalidateQueries({ queryKey: ['documents', 'detail', id] });

// Invalidate with predicate
queryClient.invalidateQueries({
  predicate: (query) => query.queryKey[0] === 'documents',
});

// Refetch immediately
queryClient.refetchQueries({ queryKey: ['documents'] });
```

---

## Optimistic Updates

### Pattern 1: Simple Optimistic Update

```typescript
const updateDocument = useMutation({
  mutationFn: ({ id, updates }) => api.updateDocument(id, updates),
  onMutate: async ({ id, updates }) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['documents'] });

    // Snapshot previous value
    const previous = queryClient.getQueryData(['documents']);

    // Optimistically update
    queryClient.setQueryData(['documents'], (old) =>
      old.map((doc) => (doc.id === id ? { ...doc, ...updates } : doc))
    );

    return { previous };
  },
  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(['documents'], context.previous);
  },
  onSettled: () => {
    // Refetch to ensure consistency
    queryClient.invalidateQueries({ queryKey: ['documents'] });
  },
});
```

### Pattern 2: Optimistic Create

```typescript
const createDocument = useMutation({
  mutationFn: (document) => api.createDocument(document),
  onMutate: async (newDocument) => {
    await queryClient.cancelQueries({ queryKey: ['documents'] });

    const previous = queryClient.getQueryData(['documents']);

    // Add temporary ID
    const optimisticDocument = {
      ...newDocument,
      id: `temp-${Date.now()}`,
      created_at: new Date().toISOString(),
    };

    queryClient.setQueryData(['documents'], (old) => [
      optimisticDocument,
      ...old,
    ]);

    return { previous, optimisticId: optimisticDocument.id };
  },
  onSuccess: (data, variables, context) => {
    // Replace temporary document with real one
    queryClient.setQueryData(['documents'], (old) =>
      old.map((doc) => (doc.id === context.optimisticId ? data : doc))
    );
  },
  onError: (err, variables, context) => {
    queryClient.setQueryData(['documents'], context.previous);
  },
});
```

### Pattern 3: Optimistic Delete

```typescript
const deleteDocument = useMutation({
  mutationFn: (id) => api.deleteDocument(id),
  onMutate: async (id) => {
    await queryClient.cancelQueries({ queryKey: ['documents'] });

    const previous = queryClient.getQueryData(['documents']);

    queryClient.setQueryData(['documents'], (old) =>
      old.filter((doc) => doc.id !== id)
    );

    return { previous };
  },
  onError: (err, variables, context) => {
    queryClient.setQueryData(['documents'], context.previous);
    toast.error('Failed to delete document');
  },
  onSuccess: () => {
    toast.success('Document deleted');
  },
});
```

---

## Error Handling

### Error Types

```typescript
// src/lib/errors/types.ts
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends Error {
  constructor(
    message: string,
    public fields: Record<string, string[]>
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}
```

### Error Handling in Hooks

```typescript
const { data, error, isError } = useQuery({
  queryKey: ['documents'],
  queryFn: fetchDocuments,
  retry: (failureCount, error) => {
    // Don't retry on 4xx errors
    if (error.response?.status >= 400 && error.response?.status < 500) {
      return false;
    }
    // Retry up to 3 times for 5xx errors
    return failureCount < 3;
  },
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
});

// Display error
if (isError) {
  return <ErrorAlert error={error} />;
}
```

### Global Error Handler

```typescript
// src/lib/api/client.ts
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;

      switch (status) {
        case 400:
          throw new ValidationError(data.message, data.fields);
        case 401:
          // Redirect to login
          window.location.href = '/login';
          break;
        case 403:
          throw new APIError('Access denied', status, 'FORBIDDEN');
        case 404:
          throw new APIError('Resource not found', status, 'NOT_FOUND');
        case 500:
          throw new APIError('Server error', status, 'SERVER_ERROR');
        default:
          throw new APIError(data.message || 'Unknown error', status);
      }
    } else if (error.request) {
      // Request made but no response
      throw new NetworkError('Network error. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message);
    }
  }
);
```

---

## Loading States

### Skeleton Loading

```typescript
function DocumentGrid() {
  const { documents, isLoading } = useDocuments();

  if (isLoading) {
    return (
      <div className="grid grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <DocumentCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-4 gap-4">
      {documents.map((doc) => (
        <DocumentCard key={doc.id} document={doc} />
      ))}
    </div>
  );
}
```

### Mutation Loading States

```typescript
function DocumentCard({ document }) {
  const { deleteDocument, isDeleting } = useDocuments();

  return (
    <Card>
      <CardContent>{document.title}</CardContent>
      <CardFooter>
        <Button
          onClick={() => deleteDocument(document.id)}
          disabled={isDeleting}
        >
          {isDeleting ? 'Deleting...' : 'Delete'}
        </Button>
      </CardFooter>
    </Card>
  );
}
```

---

## Best Practices

### 1. Use Query Keys Consistently

```typescript
// Define query keys in a central location
export const queryKeys = {
  documents: {
    all: ['documents'] as const,
    lists: () => [...queryKeys.documents.all, 'list'] as const,
    list: (filters: string) => [...queryKeys.documents.lists(), { filters }] as const,
    details: () => [...queryKeys.documents.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.documents.details(), id] as const,
  },
  collections: {
    all: ['collections'] as const,
    lists: () => [...queryKeys.collections.all, 'list'] as const,
    list: (filters: string) => [...queryKeys.collections.lists(), { filters }] as const,
    details: () => [...queryKeys.collections.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.collections.details(), id] as const,
  },
};
```

### 2. Handle Loading and Error States

```typescript
function Component() {
  const { data, isLoading, isError, error } = useQuery(...);

  if (isLoading) return <Skeleton />;
  if (isError) return <ErrorAlert error={error} />;
  if (!data) return <EmptyState />;

  return <Content data={data} />;
}
```

### 3. Use Optimistic Updates for Better UX

```typescript
// Good: Immediate feedback
const { mutate } = useMutation({
  mutationFn: updateDocument,
  onMutate: async (updates) => {
    // Optimistically update UI
    queryClient.setQueryData(['documents'], (old) => ({
      ...old,
      ...updates,
    }));
  },
});

// Bad: Wait for server response
const { mutate } = useMutation({
  mutationFn: updateDocument,
  onSuccess: () => {
    queryClient.invalidateQueries(['documents']);
  },
});
```

### 4. Debounce Search Queries

```typescript
function SearchInput() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);

  const { data } = useQuery({
    queryKey: ['documents', { search: debouncedSearch }],
    queryFn: () => fetchDocuments({ search: debouncedSearch }),
    enabled: debouncedSearch.length > 0,
  });

  return <input value={search} onChange={(e) => setSearch(e.target.value)} />;
}
```

### 5. Prefetch Data

```typescript
function DocumentList() {
  const queryClient = useQueryClient();

  const handleMouseEnter = (id: string) => {
    // Prefetch document details on hover
    queryClient.prefetchQuery({
      queryKey: ['documents', 'detail', id],
      queryFn: () => fetchDocument(id),
    });
  };

  return (
    <div>
      {documents.map((doc) => (
        <div key={doc.id} onMouseEnter={() => handleMouseEnter(doc.id)}>
          {doc.title}
        </div>
      ))}
    </div>
  );
}
```

### 6. Handle Pagination

```typescript
function DocumentList() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['documents', { page }],
    queryFn: () => fetchDocuments({ skip: (page - 1) * 20, limit: 20 }),
    keepPreviousData: true, // Keep old data while fetching new page
  });

  return (
    <>
      <DocumentGrid documents={data?.documents} />
      <Pagination
        page={page}
        totalPages={data?.totalPages}
        onPageChange={setPage}
      />
    </>
  );
}
```

### 7. Use Dependent Queries

```typescript
function DocumentDetails({ id }: { id: string }) {
  // First query: Get document
  const { data: document } = useQuery({
    queryKey: ['documents', 'detail', id],
    queryFn: () => fetchDocument(id),
  });

  // Second query: Get related documents (depends on first query)
  const { data: related } = useQuery({
    queryKey: ['documents', 'related', id],
    queryFn: () => fetchRelatedDocuments(id),
    enabled: !!document, // Only run if document exists
  });

  return (
    <div>
      <h1>{document?.title}</h1>
      {related && <RelatedList documents={related} />}
    </div>
  );
}
```

---

## Testing

### Mock API Responses

```typescript
// src/test/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/resources', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: '1', title: 'Document 1' },
        { id: '2', title: 'Document 2' },
      ])
    );
  }),

  rest.post('/api/resources', (req, res, ctx) => {
    const body = req.body as any;
    return res(
      ctx.status(201),
      ctx.json({ id: '3', ...body })
    );
  }),

  rest.delete('/api/resources/:id', (req, res, ctx) => {
    return res(ctx.status(204));
  }),
];
```

### Test Custom Hooks

```typescript
// src/lib/hooks/__tests__/useDocuments.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDocuments } from '../useDocuments';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useDocuments', () => {
  it('fetches documents', async () => {
    const { result } = renderHook(() => useDocuments(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.documents).toHaveLength(2);
  });

  it('creates document optimistically', async () => {
    const { result } = renderHook(() => useDocuments(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    act(() => {
      result.current.createDocument({ title: 'New Document' });
    });

    // Document should appear immediately (optimistic)
    expect(result.current.documents).toHaveLength(3);
  });
});
```

---

## Performance Optimization

### 1. Use React Query DevTools

```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### 2. Configure Query Client

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      retry: 1,
    },
  },
});
```

### 3. Use Suspense (Optional)

```typescript
const { data } = useQuery({
  queryKey: ['documents'],
  queryFn: fetchDocuments,
  suspense: true, // Enable suspense mode
});

// Wrap component in Suspense
<Suspense fallback={<Skeleton />}>
  <DocumentList />
</Suspense>
```

---

## Conclusion

This guide covers the essential patterns for integrating with the Library API. Key takeaways:

1. **Use React Query** for server state management
2. **Implement optimistic updates** for better UX
3. **Handle errors gracefully** with proper error boundaries
4. **Cache strategically** with appropriate stale/cache times
5. **Test thoroughly** with MSW and React Testing Library

For more information, see:
- [React Query Documentation](https://tanstack.com/query/latest)
- [Zustand Documentation](https://zustand-demo.pmnd.rs/)
- [API Reference](../api/library.md)
