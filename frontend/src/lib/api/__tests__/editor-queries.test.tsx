/**
 * Tests for TanStack Query Editor Hooks
 * 
 * Tests caching, prefetching, request deduplication, and optimistic updates
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import {
  useAnnotations,
  useCreateAnnotation,
  useUpdateAnnotation,
  useDeleteAnnotation,
  useChunks,
  useQualityDetails,
  usePrefetchChunks,
  usePrefetchQualityDetails,
  usePrefetchEditorData,
  useInvalidateEditorData,
} from '../editor-queries';
import { editorApi } from '../editor';
import type { Annotation, SemanticChunk, QualityDetails } from '../editor';

// Mock the editor API
vi.mock('../editor', () => ({
  editorApi: {
    getAnnotations: vi.fn(),
    createAnnotation: vi.fn(),
    updateAnnotation: vi.fn(),
    deleteAnnotation: vi.fn(),
    getChunks: vi.fn(),
    getQualityDetails: vi.fn(),
  },
  editorQueryKeys: {
    annotations: (resourceId: string) => ['annotations', resourceId],
    annotation: (annotationId: string) => ['annotation', annotationId],
    chunks: (resourceId: string) => ['chunks', resourceId],
    chunk: (chunkId: string) => ['chunk', chunkId],
    quality: (resourceId: string) => ['quality', resourceId],
  },
  editorCacheConfig: {
    annotations: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    },
    chunks: {
      staleTime: 10 * 60 * 1000,
      cacheTime: 30 * 60 * 1000,
    },
    quality: {
      staleTime: 15 * 60 * 1000,
      cacheTime: 30 * 60 * 1000,
    },
  },
}));

// Test data
const mockAnnotation: Annotation = {
  id: 'ann-1',
  resource_id: 'res-1',
  user_id: 'user-1',
  start_offset: 0,
  end_offset: 10,
  highlighted_text: 'test text',
  note: 'test note',
  color: '#3b82f6',
  is_shared: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockChunk: SemanticChunk = {
  id: 'chunk-1',
  resource_id: 'res-1',
  content: 'function test() {}',
  chunk_index: 0,
  chunk_metadata: {
    function_name: 'test',
    start_line: 1,
    end_line: 3,
    language: 'typescript',
  },
  created_at: '2024-01-01T00:00:00Z',
};

const mockQuality: QualityDetails = {
  resource_id: 'res-1',
  quality_dimensions: {
    accuracy: 0.9,
    completeness: 0.8,
    consistency: 0.85,
    timeliness: 0.95,
    relevance: 0.88,
  },
  quality_overall: 0.876,
  quality_weights: {
    accuracy: 0.3,
    completeness: 0.2,
    consistency: 0.2,
    timeliness: 0.15,
    relevance: 0.15,
  },
  quality_last_computed: '2024-01-01T00:00:00Z',
  is_quality_outlier: false,
  needs_quality_review: false,
};

// Helper to create a fresh QueryClient for each test
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Disable retries in tests
        gcTime: Infinity, // Keep cache during tests
      },
      mutations: {
        retry: false,
      },
    },
  });
}

// Wrapper component for hooks
function createWrapper(queryClient: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

describe('Editor Query Hooks - Caching', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useAnnotations', () => {
    it('should fetch and cache annotations', async () => {
      const queryClient = createTestQueryClient();
      const mockResponse = { data: [mockAnnotation] };
      vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockResponse as any);

      const { result } = renderHook(
        () => useAnnotations('res-1'),
        { wrapper: createWrapper(queryClient) }
      );

      // Initially loading
      expect(result.current.isLoading).toBe(true);

      // Wait for data
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Check data
      expect(result.current.data).toEqual([mockAnnotation]);
      expect(editorApi.getAnnotations).toHaveBeenCalledTimes(1);
      expect(editorApi.getAnnotations).toHaveBeenCalledWith('res-1');
    });

    it('should deduplicate requests for same resource', async () => {
      const queryClient = createTestQueryClient();
      const mockResponse = { data: [mockAnnotation] };
      vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockResponse as any);

      // Render two hooks with same resourceId
      const { result: result1 } = renderHook(
        () => useAnnotations('res-1'),
        { wrapper: createWrapper(queryClient) }
      );

      const { result: result2 } = renderHook(
        () => useAnnotations('res-1'),
        { wrapper: createWrapper(queryClient) }
      );

      // Wait for both to complete
      await waitFor(() => {
        expect(result1.current.isSuccess).toBe(true);
        expect(result2.current.isSuccess).toBe(true);
      });

      // Should only call API once (request deduplication)
      expect(editorApi.getAnnotations).toHaveBeenCalledTimes(1);

      // Both should have same data
      expect(result1.current.data).toEqual([mockAnnotation]);
      expect(result2.current.data).toEqual([mockAnnotation]);
    });

    it('should use cached data on subsequent renders', async () => {
      const queryClient = createTestQueryClient();
      const mockResponse = { data: [mockAnnotation] };
      vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockResponse as any);

      // First render
      const { result: result1, unmount } = renderHook(
        () => useAnnotations('res-1'),
        { wrapper: createWrapper(queryClient) }
      );

      await waitFor(() => {
        expect(result1.current.isSuccess).toBe(true);
      });

      unmount();

      // Second render - should use cache
      const { result: result2 } = renderHook(
        () => useAnnotations('res-1'),
        { wrapper: createWrapper(queryClient) }
      );

      // Should immediately have data from cache
      expect(result2.current.data).toEqual([mockAnnotation]);
      expect(result2.current.isLoading).toBe(false);

      // Should still only have called API once
      expect(editorApi.getAnnotations).toHaveBeenCalledTimes(1);
    });
  });

  describe('useChunks', () => {
    it('should fetch and cache chunks', async () => {
      const queryClient = createTestQueryClient();
      const mockResponse = { data: [mockChunk] };
      vi.mocked(editorApi.getChunks).mockResolvedValue(mockResponse as any);

      const { result } = renderHook(
        () => useChunks('res-1'),
        { wrapper: createWrapper(queryClient) }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual([mockChunk]);
      expect(editorApi.getChunks).toHaveBeenCalledTimes(1);
    });

    it('should cache chunks longer than annotations', async () => {
      const queryClient = createTestQueryClient();
      const mockResponse = { data: [mockChunk] };
      vi.mocked(editorApi.getChunks).mockResolvedValue(mockResponse as any);

      const { result } = renderHook(
        () => useChunks('res-1'),
        { wrapper: createWrapper(queryClient) }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Check that staleTime is set correctly (10 minutes for chunks)
      const queryState = queryClient.getQueryState(['chunks', 'res-1']);
      expect(queryState?.dataUpdatedAt).toBeDefined();
    });
  });

  describe('useQualityDetails', () => {
    it('should fetch and cache quality details', async () => {
      const queryClient = createTestQueryClient();
      const mockResponse = { data: mockQuality };
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue(mockResponse as any);

      const { result } = renderHook(
        () => useQualityDetails('res-1'),
        { wrapper: createWrapper(queryClient) }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockQuality);
      expect(editorApi.getQualityDetails).toHaveBeenCalledTimes(1);
    });
  });
});

describe('Editor Query Hooks - Mutations', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useCreateAnnotation', () => {
    it('should create annotation with optimistic update', async () => {
      const queryClient = createTestQueryClient();
      
      // Pre-populate cache with existing annotations
      queryClient.setQueryData(['annotations', 'res-1'], []);

      const newAnnotation = { ...mockAnnotation, id: 'ann-2' };
      const mockResponse = { data: newAnnotation };
      vi.mocked(editorApi.createAnnotation).mockResolvedValue(mockResponse as any);

      const { result } = renderHook(
        () => useCreateAnnotation(),
        { wrapper: createWrapper(queryClient) }
      );

      // Create annotation
      result.current.mutate({
        resourceId: 'res-1',
        data: {
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'test',
        },
      });

      // Should immediately update cache (optimistic)
      await waitFor(() => {
        const cachedData = queryClient.getQueryData<Annotation[]>(['annotations', 'res-1']);
        expect(cachedData?.length).toBe(1);
      });

      // Wait for mutation to complete
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Should have real annotation in cache
      const finalData = queryClient.getQueryData<Annotation[]>(['annotations', 'res-1']);
      expect(finalData).toEqual([newAnnotation]);
    });

    it('should rollback on error', async () => {
      const queryClient = createTestQueryClient();
      
      // Pre-populate cache
      queryClient.setQueryData(['annotations', 'res-1'], [mockAnnotation]);

      // Mock API error
      vi.mocked(editorApi.createAnnotation).mockRejectedValue(
        new Error('API Error')
      );

      const { result } = renderHook(
        () => useCreateAnnotation(),
        { wrapper: createWrapper(queryClient) }
      );

      // Attempt to create annotation
      result.current.mutate({
        resourceId: 'res-1',
        data: {
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'test',
        },
      });

      // Wait for error
      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      // Should rollback to original data
      const cachedData = queryClient.getQueryData<Annotation[]>(['annotations', 'res-1']);
      expect(cachedData).toEqual([mockAnnotation]);
    });
  });

  describe('useUpdateAnnotation', () => {
    it('should update annotation with optimistic update', async () => {
      const queryClient = createTestQueryClient();
      
      // Pre-populate cache
      queryClient.setQueryData(['annotations', 'res-1'], [mockAnnotation]);

      const updatedAnnotation = { ...mockAnnotation, note: 'updated note' };
      const mockResponse = { data: updatedAnnotation };
      vi.mocked(editorApi.updateAnnotation).mockResolvedValue(mockResponse as any);

      const { result } = renderHook(
        () => useUpdateAnnotation(),
        { wrapper: createWrapper(queryClient) }
      );

      // Update annotation
      result.current.mutate({
        annotationId: 'ann-1',
        data: { note: 'updated note' },
      });

      // Wait for mutation to complete
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Should have updated annotation in cache
      const cachedData = queryClient.getQueryData<Annotation[]>(['annotations', 'res-1']);
      expect(cachedData?.[0].note).toBe('updated note');
    });
  });

  describe('useDeleteAnnotation', () => {
    it('should delete annotation with optimistic update', async () => {
      const queryClient = createTestQueryClient();
      
      // Pre-populate cache
      queryClient.setQueryData(['annotations', 'res-1'], [mockAnnotation]);

      vi.mocked(editorApi.deleteAnnotation).mockResolvedValue({} as any);

      const { result } = renderHook(
        () => useDeleteAnnotation(),
        { wrapper: createWrapper(queryClient) }
      );

      // Delete annotation
      result.current.mutate('ann-1');

      // Wait for mutation to complete
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Should be removed from cache
      const cachedData = queryClient.getQueryData<Annotation[]>(['annotations', 'res-1']);
      expect(cachedData).toEqual([]);
    });
  });
});

describe('Editor Query Hooks - Prefetching', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('usePrefetchChunks', () => {
    it('should prefetch chunks into cache', async () => {
      const queryClient = createTestQueryClient();
      const mockResponse = { data: [mockChunk] };
      vi.mocked(editorApi.getChunks).mockResolvedValue(mockResponse as any);

      const { result } = renderHook(
        () => usePrefetchChunks(),
        { wrapper: createWrapper(queryClient) }
      );

      // Prefetch chunks
      result.current('res-1');

      // Wait for prefetch to complete
      await waitFor(() => {
        const cachedData = queryClient.getQueryData(['chunks', 'res-1']);
        expect(cachedData).toBeDefined();
      });

      // Should have chunks in cache
      const cachedData = queryClient.getQueryData<SemanticChunk[]>(['chunks', 'res-1']);
      expect(cachedData).toEqual([mockChunk]);
    });
  });

  describe('usePrefetchQualityDetails', () => {
    it('should prefetch quality details into cache', async () => {
      const queryClient = createTestQueryClient();
      const mockResponse = { data: mockQuality };
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue(mockResponse as any);

      const { result } = renderHook(
        () => usePrefetchQualityDetails(),
        { wrapper: createWrapper(queryClient) }
      );

      // Prefetch quality
      result.current('res-1');

      // Wait for prefetch to complete
      await waitFor(() => {
        const cachedData = queryClient.getQueryData(['quality', 'res-1']);
        expect(cachedData).toBeDefined();
      });

      // Should have quality in cache
      const cachedData = queryClient.getQueryData<QualityDetails>(['quality', 'res-1']);
      expect(cachedData).toEqual(mockQuality);
    });
  });

  describe('usePrefetchEditorData', () => {
    it('should prefetch all editor data in parallel', async () => {
      const queryClient = createTestQueryClient();
      
      vi.mocked(editorApi.getAnnotations).mockResolvedValue({ data: [mockAnnotation] } as any);
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [mockChunk] } as any);
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: mockQuality } as any);

      const { result } = renderHook(
        () => usePrefetchEditorData(),
        { wrapper: createWrapper(queryClient) }
      );

      // Prefetch all data
      result.current('res-1');

      // Wait for all prefetches to complete
      await waitFor(() => {
        const annotations = queryClient.getQueryData(['annotations', 'res-1']);
        const chunks = queryClient.getQueryData(['chunks', 'res-1']);
        const quality = queryClient.getQueryData(['quality', 'res-1']);
        
        expect(annotations).toBeDefined();
        expect(chunks).toBeDefined();
        expect(quality).toBeDefined();
      });

      // All three API calls should have been made
      expect(editorApi.getAnnotations).toHaveBeenCalledTimes(1);
      expect(editorApi.getChunks).toHaveBeenCalledTimes(1);
      expect(editorApi.getQualityDetails).toHaveBeenCalledTimes(1);
    });
  });
});

describe('Editor Query Hooks - Cache Invalidation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useInvalidateEditorData', () => {
    it('should invalidate all editor data for a resource', async () => {
      const queryClient = createTestQueryClient();
      
      // Pre-populate cache
      queryClient.setQueryData(['annotations', 'res-1'], [mockAnnotation]);
      queryClient.setQueryData(['chunks', 'res-1'], [mockChunk]);
      queryClient.setQueryData(['quality', 'res-1'], mockQuality);

      const { result } = renderHook(
        () => useInvalidateEditorData(),
        { wrapper: createWrapper(queryClient) }
      );

      // Invalidate all data
      result.current('res-1');

      // Wait for invalidation
      await waitFor(() => {
        const annotationsState = queryClient.getQueryState(['annotations', 'res-1']);
        expect(annotationsState?.isInvalidated).toBe(true);
      });

      // All queries should be marked as invalidated
      const chunksState = queryClient.getQueryState(['chunks', 'res-1']);
      const qualityState = queryClient.getQueryState(['quality', 'res-1']);
      
      expect(chunksState?.isInvalidated).toBe(true);
      expect(qualityState?.isInvalidated).toBe(true);
    });
  });
});

describe('Editor Query Hooks - Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle API errors gracefully', async () => {
    const queryClient = createTestQueryClient();
    const error = new Error('API Error');
    vi.mocked(editorApi.getAnnotations).mockRejectedValue(error);

    const { result } = renderHook(
      () => useAnnotations('res-1'),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(error);
  });

  it('should keep stale data during errors', async () => {
    const queryClient = createTestQueryClient();
    
    // First successful fetch
    vi.mocked(editorApi.getAnnotations).mockResolvedValue({ 
      data: [mockAnnotation] 
    } as any);

    const { result, rerender } = renderHook(
      () => useAnnotations('res-1'),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Second fetch fails
    vi.mocked(editorApi.getAnnotations).mockRejectedValue(new Error('API Error'));

    // Invalidate to trigger refetch
    queryClient.invalidateQueries({ queryKey: ['annotations', 'res-1'] });
    rerender();

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    // Should still have stale data
    expect(result.current.data).toEqual([mockAnnotation]);
  });
});
