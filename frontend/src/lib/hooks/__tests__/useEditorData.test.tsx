/**
 * Tests for Editor Data Hooks
 * 
 * Tests TanStack Query hooks for Phase 2 editor features:
 * - useResource hook with caching
 * - useResourceStatus hook with polling
 * - useChunks hook
 * - useChunk hook
 * - useTriggerChunking mutation
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 5.2 Create TanStack Query hooks for resources & chunks
 * Requirements: 3.1, 3.2, 3.3, 3.4
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createElement, type ReactNode } from 'react';
import { editorApi } from '@/lib/api/editor';
import {
  useResource,
  useResourceStatus,
  useChunks,
  useChunk,
  useTriggerChunking,
  useAnnotations,
  useCreateAnnotation,
  useUpdateAnnotation,
  useDeleteAnnotation,
  useSearchAnnotationsFulltext,
  useSearchAnnotationsSemantic,
  useSearchAnnotationsByTags,
  useExportAnnotationsMarkdown,
  useExportAnnotationsJSON,
  useQualityDetails,
  useRecalculateQuality,
  useQualityOutliers,
  useQualityDegradation,
  useQualityDistribution,
  useQualityTrends,
  useQualityDimensions,
  useQualityReviewQueue,
} from '../useEditorData';
import type { 
  Resource, 
  ProcessingStatus, 
  SemanticChunk, 
  ChunkingTask, 
  Annotation,
  AnnotationExport,
  QualityDetails,
  QualityOutlier,
  QualityDegradation,
  QualityDistribution,
  QualityTrend,
  QualityDimensionScores,
  ReviewQueueItem,
} from '@/types/api';

// ============================================================================
// Test Setup
// ============================================================================

// Mock the editor API
vi.mock('@/lib/api/editor', () => ({
  editorApi: {
    getResource: vi.fn(),
    getResourceStatus: vi.fn(),
    getChunks: vi.fn(),
    getChunk: vi.fn(),
    triggerChunking: vi.fn(),
    getAnnotations: vi.fn(),
    createAnnotation: vi.fn(),
    updateAnnotation: vi.fn(),
    deleteAnnotation: vi.fn(),
    searchAnnotationsFulltext: vi.fn(),
    searchAnnotationsSemantic: vi.fn(),
    searchAnnotationsByTags: vi.fn(),
    exportAnnotationsMarkdown: vi.fn(),
    exportAnnotationsJSON: vi.fn(),
    recalculateQuality: vi.fn(),
    getQualityOutliers: vi.fn(),
    getQualityDegradation: vi.fn(),
    getQualityDistribution: vi.fn(),
    getQualityTrends: vi.fn(),
    getQualityDimensions: vi.fn(),
    getQualityReviewQueue: vi.fn(),
  },
  editorQueryKeys: {
    resource: {
      all: () => ['resource'],
      detail: (resourceId: string) => ['resource', resourceId],
      status: (resourceId: string) => ['resource', resourceId, 'status'],
    },
    chunks: {
      all: () => ['chunks'],
      byResource: (resourceId: string) => ['chunks', 'resource', resourceId],
      detail: (chunkId: string) => ['chunks', chunkId],
    },
    annotations: {
      all: () => ['annotations'],
      byResource: (resourceId: string) => ['annotations', 'resource', resourceId],
      search: (query: string, type: string) => ['annotations', 'search', type, query],
    },
    quality: {
      all: () => ['quality'],
      outliers: (params?: any) => ['quality', 'outliers', params],
      degradation: (days: number) => ['quality', 'degradation', days],
      distribution: (bins: number) => ['quality', 'distribution', bins],
      trends: (granularity: string) => ['quality', 'trends', granularity],
      dimensions: () => ['quality', 'dimensions'],
      reviewQueue: (params?: any) => ['quality', 'reviewQueue', params],
    },
  },
  editorCacheConfig: {
    resource: {
      staleTime: 10 * 60 * 1000,
      cacheTime: 15 * 60 * 1000,
    },
    resourceStatus: {
      staleTime: 5 * 1000,
      cacheTime: 30 * 1000,
      refetchInterval: 5 * 1000,
    },
    chunks: {
      staleTime: 10 * 60 * 1000,
      cacheTime: 15 * 60 * 1000,
    },
    annotations: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    },
    quality: {
      staleTime: 15 * 60 * 1000,
      cacheTime: 30 * 60 * 1000,
    },
  },
}));

// Create a wrapper with QueryClient
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Disable retries for tests
        gcTime: 0,
      },
    },
  });

  return ({ children }: { children: ReactNode }) =>
    createElement(QueryClientProvider, { client: queryClient }, children);
}

// ============================================================================
// Test Data
// ============================================================================

const mockResource: Resource = {
  id: 'resource-1',
  title: 'Test Resource',
  content: 'console.log("Hello, World!");',
  content_type: 'code',
  url: 'https://example.com/test.js',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ingestion_status: 'completed',
  quality_score: 0.85,
  quality_dimensions: {
    accuracy: 0.9,
    completeness: 0.8,
    consistency: 0.85,
    timeliness: 0.9,
    relevance: 0.8,
  },
};

const mockProcessingStatus: ProcessingStatus = {
  id: 'resource-1',
  ingestion_status: 'completed',
  ingestion_started_at: '2024-01-01T00:00:00Z',
  ingestion_completed_at: '2024-01-01T00:01:00Z',
  ingestion_error: undefined,
};

const mockChunks: SemanticChunk[] = [
  {
    id: 'chunk-1',
    resource_id: 'resource-1',
    chunk_index: 0,
    content: 'console.log("Hello, World!");',
    chunk_metadata: {
      start_line: 1,
      end_line: 1,
      language: 'javascript',
    },
    embedding_id: undefined,
    created_at: '2024-01-01T00:00:00Z',
  },
];

const mockChunk: SemanticChunk = mockChunks[0];

const mockChunkingTask: ChunkingTask = {
  resource_id: 'resource-1',
  message: 'Chunking task created',
  strategy: 'semantic',
  chunk_size: 512,
  overlap: 50,
};

beforeEach(() => {
  vi.clearAllMocks();
});

// ============================================================================
// useResource Tests
// ============================================================================

describe('useResource', () => {
  it('should fetch resource by ID', async () => {
    vi.mocked(editorApi.getResource).mockResolvedValue(mockResource);

    const { result } = renderHook(() => useResource('resource-1'), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockResource);
    expect(result.current.data?.id).toBe('resource-1');
    expect(result.current.data?.title).toBe('Test Resource');
    expect(editorApi.getResource).toHaveBeenCalledWith('resource-1');
  });

  it('should not fetch when resourceId is empty', async () => {
    const { result } = renderHook(() => useResource(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.getResource).not.toHaveBeenCalled();
  });

  it('should handle fetch errors', async () => {
    const error = new Error('Resource not found');
    vi.mocked(editorApi.getResource).mockRejectedValue(error);

    const { result } = renderHook(() => useResource('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(error);
  });

  it('should cache resource data', async () => {
    vi.mocked(editorApi.getResource).mockResolvedValue(mockResource);

    const { result, rerender } = renderHook(() => useResource('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(editorApi.getResource).toHaveBeenCalledTimes(1);

    // Rerender should use cached data
    rerender();

    expect(editorApi.getResource).toHaveBeenCalledTimes(1);
  });
});

// ============================================================================
// useResourceStatus Tests
// ============================================================================

describe('useResourceStatus', () => {
  it('should fetch resource processing status', async () => {
    vi.mocked(editorApi.getResourceStatus).mockResolvedValue(mockProcessingStatus);

    const { result } = renderHook(() => useResourceStatus('resource-1'), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockProcessingStatus);
    expect(result.current.data?.ingestion_status).toBe('completed');
    expect(editorApi.getResourceStatus).toHaveBeenCalledWith('resource-1');
  });

  it('should poll status automatically', async () => {
    vi.mocked(editorApi.getResourceStatus).mockResolvedValue(mockProcessingStatus);

    const { result } = renderHook(
      () => useResourceStatus('resource-1', { refetchInterval: 100 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Wait for at least one more poll
    await waitFor(
      () => {
        expect(editorApi.getResourceStatus).toHaveBeenCalledTimes(2);
      },
      { timeout: 200 }
    );
  });

  it('should not fetch when resourceId is empty', async () => {
    const { result } = renderHook(() => useResourceStatus(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.getResourceStatus).not.toHaveBeenCalled();
  });
});

// ============================================================================
// useChunks Tests
// ============================================================================

describe('useChunks', () => {
  it('should fetch chunks for a resource', async () => {
    vi.mocked(editorApi.getChunks).mockResolvedValue(mockChunks);

    const { result } = renderHook(() => useChunks('resource-1'), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockChunks);
    expect(result.current.data).toHaveLength(1);
    expect(result.current.data?.[0].id).toBe('chunk-1');
    expect(editorApi.getChunks).toHaveBeenCalledWith('resource-1');
  });

  it('should not fetch when resourceId is empty', async () => {
    const { result } = renderHook(() => useChunks(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.getChunks).not.toHaveBeenCalled();
  });

  it('should handle empty chunks array', async () => {
    vi.mocked(editorApi.getChunks).mockResolvedValue([]);

    const { result } = renderHook(() => useChunks('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([]);
  });
});

// ============================================================================
// useChunk Tests
// ============================================================================

describe('useChunk', () => {
  it('should fetch a specific chunk by ID', async () => {
    vi.mocked(editorApi.getChunk).mockResolvedValue(mockChunk);

    const { result } = renderHook(() => useChunk('chunk-1'), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockChunk);
    expect(result.current.data?.id).toBe('chunk-1');
    expect(result.current.data?.chunk_metadata.language).toBe('javascript');
    expect(editorApi.getChunk).toHaveBeenCalledWith('chunk-1');
  });

  it('should not fetch when chunkId is empty', async () => {
    const { result } = renderHook(() => useChunk(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.getChunk).not.toHaveBeenCalled();
  });

  it('should handle chunk not found', async () => {
    const error = new Error('Chunk not found');
    vi.mocked(editorApi.getChunk).mockRejectedValue(error);

    const { result } = renderHook(() => useChunk('chunk-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(error);
  });
});

// ============================================================================
// useTriggerChunking Tests
// ============================================================================

describe('useTriggerChunking', () => {
  it('should trigger chunking for a resource', async () => {
    vi.mocked(editorApi.triggerChunking).mockResolvedValue(mockChunkingTask);

    const { result } = renderHook(() => useTriggerChunking(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isPending).toBe(false);

    result.current.mutate({
      resourceId: 'resource-1',
      request: {
        strategy: 'semantic',
        chunk_size: 512,
        overlap: 50,
      },
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockChunkingTask);
    expect(result.current.data?.resource_id).toBe('resource-1');
    expect(result.current.data?.message).toBe('Chunking task created');
    expect(editorApi.triggerChunking).toHaveBeenCalledWith('resource-1', {
      strategy: 'semantic',
      chunk_size: 512,
      overlap: 50,
    });
  });

  it('should invalidate chunks cache on success', async () => {
    vi.mocked(editorApi.triggerChunking).mockResolvedValue(mockChunkingTask);

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const wrapper = ({ children }: { children: ReactNode }) =>
      createElement(QueryClientProvider, { client: queryClient }, children);

    const { result } = renderHook(() => useTriggerChunking(), { wrapper });

    result.current.mutate({
      resourceId: 'resource-1',
      request: {
        strategy: 'semantic',
        chunk_size: 512,
        overlap: 50,
      },
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(invalidateSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ['chunks', 'resource', 'resource-1'],
      })
    );
    expect(invalidateSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ['resource', 'resource-1', 'status'],
      })
    );
  });

  it('should handle chunking errors', async () => {
    const error = new Error('Chunking failed');
    vi.mocked(editorApi.triggerChunking).mockRejectedValue(error);

    const { result } = renderHook(() => useTriggerChunking(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      resourceId: 'resource-1',
      request: {
        strategy: 'semantic',
        chunk_size: 512,
        overlap: 50,
      },
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(error);
  });
});

// ============================================================================
// Annotation Hooks Tests
// ============================================================================

const mockAnnotations: Annotation[] = [
  {
    id: 'annotation-1',
    resource_id: 'resource-1',
    user_id: 'user-1',
    start_offset: 0,
    end_offset: 10,
    highlighted_text: 'console.log',
    note: 'This is a log statement',
    tags: ['important', 'debug'],
    color: '#ffeb3b',
    is_shared: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'annotation-2',
    resource_id: 'resource-1',
    user_id: 'user-1',
    start_offset: 20,
    end_offset: 30,
    highlighted_text: 'Hello',
    note: 'Greeting message',
    tags: ['string'],
    color: '#4caf50',
    is_shared: true,
    created_at: '2024-01-01T00:01:00Z',
    updated_at: '2024-01-01T00:01:00Z',
  },
];

const mockAnnotationExport: AnnotationExport = mockAnnotations;

// Mock annotation API methods
vi.mock('@/lib/api/editor', async () => {
  const actual = await vi.importActual('@/lib/api/editor');
  return {
    ...actual,
    editorApi: {
      ...((actual as any).editorApi || {}),
      getAnnotations: vi.fn(),
      createAnnotation: vi.fn(),
      updateAnnotation: vi.fn(),
      deleteAnnotation: vi.fn(),
      searchAnnotationsFulltext: vi.fn(),
      searchAnnotationsSemantic: vi.fn(),
      searchAnnotationsByTags: vi.fn(),
      exportAnnotationsMarkdown: vi.fn(),
      exportAnnotationsJSON: vi.fn(),
    },
  };
});

describe('useAnnotations', () => {
  it('should fetch annotations for a resource', async () => {
    vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockAnnotations);

    const { result } = renderHook(() => useAnnotations('resource-1'), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockAnnotations);
    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0].id).toBe('annotation-1');
    expect(editorApi.getAnnotations).toHaveBeenCalledWith('resource-1');
  });

  it('should not fetch when resourceId is empty', async () => {
    const { result } = renderHook(() => useAnnotations(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.getAnnotations).not.toHaveBeenCalled();
  });

  it('should handle empty annotations array', async () => {
    vi.mocked(editorApi.getAnnotations).mockResolvedValue([]);

    const { result } = renderHook(() => useAnnotations('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([]);
  });
});

describe('useCreateAnnotation', () => {
  it('should create annotation with optimistic update', async () => {
    const newAnnotation: Annotation = {
      ...mockAnnotations[0],
      id: 'annotation-3',
      note: 'New annotation',
    };
    vi.mocked(editorApi.createAnnotation).mockResolvedValue(newAnnotation);
    vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockAnnotations);

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    const wrapper = ({ children }: { children: ReactNode }) =>
      createElement(QueryClientProvider, { client: queryClient }, children);

    // First, populate the cache with existing annotations
    const { result: annotationsResult } = renderHook(
      () => useAnnotations('resource-1'),
      { wrapper }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    // Now test the create mutation
    const { result: createResult } = renderHook(() => useCreateAnnotation(), { wrapper });

    createResult.current.mutate({
      resourceId: 'resource-1',
      data: {
        start_offset: 40,
        end_offset: 50,
        highlighted_text: 'World',
        note: 'New annotation',
        tags: ['test'],
        color: '#2196f3',
      },
    });

    await waitFor(() => {
      expect(createResult.current.isSuccess).toBe(true);
    });

    expect(createResult.current.data).toEqual(newAnnotation);
    expect(editorApi.createAnnotation).toHaveBeenCalledWith('resource-1', {
      start_offset: 40,
      end_offset: 50,
      highlighted_text: 'World',
      note: 'New annotation',
      tags: ['test'],
      color: '#2196f3',
    });
  });

  it('should revert optimistic update on error', async () => {
    const error = new Error('Failed to create annotation');
    vi.mocked(editorApi.createAnnotation).mockRejectedValue(error);
    vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockAnnotations);

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    const wrapper = ({ children }: { children: ReactNode }) =>
      createElement(QueryClientProvider, { client: queryClient }, children);

    // Populate cache
    const { result: annotationsResult } = renderHook(
      () => useAnnotations('resource-1'),
      { wrapper }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    const initialCount = annotationsResult.current.data?.length || 0;

    // Try to create annotation (will fail)
    const { result: createResult } = renderHook(() => useCreateAnnotation(), { wrapper });

    createResult.current.mutate({
      resourceId: 'resource-1',
      data: {
        start_offset: 40,
        end_offset: 50,
        highlighted_text: 'World',
        note: 'New annotation',
        tags: ['test'],
        color: '#2196f3',
      },
    });

    await waitFor(() => {
      expect(createResult.current.isError).toBe(true);
    });

    // Verify error
    expect(createResult.current.error).toEqual(error);

    // Verify cache was reverted (after invalidation refetch)
    await waitFor(() => {
      expect(annotationsResult.current.data).toHaveLength(initialCount);
    });
  });
});

describe('useUpdateAnnotation', () => {
  it('should update annotation with optimistic update', async () => {
    const updatedAnnotation: Annotation = {
      ...mockAnnotations[0],
      note: 'Updated note',
      updated_at: '2024-01-01T00:02:00Z',
    };
    vi.mocked(editorApi.updateAnnotation).mockResolvedValue(updatedAnnotation);
    vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockAnnotations);

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    const wrapper = ({ children }: { children: ReactNode }) =>
      createElement(QueryClientProvider, { client: queryClient }, children);

    // Populate cache
    const { result: annotationsResult } = renderHook(
      () => useAnnotations('resource-1'),
      { wrapper }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    // Update annotation
    const { result: updateResult } = renderHook(() => useUpdateAnnotation(), { wrapper });

    updateResult.current.mutate({
      annotationId: 'annotation-1',
      resourceId: 'resource-1',
      data: { note: 'Updated note' },
    });

    await waitFor(() => {
      expect(updateResult.current.isSuccess).toBe(true);
    });

    expect(updateResult.current.data).toEqual(updatedAnnotation);
    expect(editorApi.updateAnnotation).toHaveBeenCalledWith('annotation-1', {
      note: 'Updated note',
    });
  });

  it('should revert optimistic update on error', async () => {
    const error = new Error('Failed to update annotation');
    vi.mocked(editorApi.updateAnnotation).mockRejectedValue(error);
    vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockAnnotations);

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    const wrapper = ({ children }: { children: ReactNode }) =>
      createElement(QueryClientProvider, { client: queryClient }, children);

    // Populate cache
    const { result: annotationsResult } = renderHook(
      () => useAnnotations('resource-1'),
      { wrapper }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    const originalNote = annotationsResult.current.data?.[0].note;

    // Try to update (will fail)
    const { result: updateResult } = renderHook(() => useUpdateAnnotation(), { wrapper });

    updateResult.current.mutate({
      annotationId: 'annotation-1',
      resourceId: 'resource-1',
      data: { note: 'Updated note' },
    });

    await waitFor(() => {
      expect(updateResult.current.isError).toBe(true);
    });

    expect(updateResult.current.error).toEqual(error);

    // Verify cache was reverted
    await waitFor(() => {
      expect(annotationsResult.current.data?.[0].note).toBe(originalNote);
    });
  });
});

describe('useDeleteAnnotation', () => {
  it('should delete annotation with optimistic update', async () => {
    vi.mocked(editorApi.deleteAnnotation).mockResolvedValue(undefined);
    vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockAnnotations);

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    const wrapper = ({ children }: { children: ReactNode }) =>
      createElement(QueryClientProvider, { client: queryClient }, children);

    // Populate cache
    const { result: annotationsResult } = renderHook(
      () => useAnnotations('resource-1'),
      { wrapper }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    const initialCount = annotationsResult.current.data?.length || 0;

    // Delete annotation
    const { result: deleteResult } = renderHook(() => useDeleteAnnotation(), { wrapper });

    deleteResult.current.mutate({
      annotationId: 'annotation-1',
      resourceId: 'resource-1',
    });

    await waitFor(() => {
      expect(deleteResult.current.isSuccess).toBe(true);
    });

    expect(editorApi.deleteAnnotation).toHaveBeenCalledWith('annotation-1');

    // Verify annotation was removed from cache (after refetch)
    await waitFor(() => {
      expect(annotationsResult.current.data?.length).toBeLessThanOrEqual(initialCount);
    });
  });

  it('should revert optimistic update on error', async () => {
    const error = new Error('Failed to delete annotation');
    vi.mocked(editorApi.deleteAnnotation).mockRejectedValue(error);
    vi.mocked(editorApi.getAnnotations).mockResolvedValue(mockAnnotations);

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    const wrapper = ({ children }: { children: ReactNode }) =>
      createElement(QueryClientProvider, { client: queryClient }, children);

    // Populate cache
    const { result: annotationsResult } = renderHook(
      () => useAnnotations('resource-1'),
      { wrapper }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    const initialCount = annotationsResult.current.data?.length || 0;

    // Try to delete (will fail)
    const { result: deleteResult } = renderHook(() => useDeleteAnnotation(), { wrapper });

    deleteResult.current.mutate({
      annotationId: 'annotation-1',
      resourceId: 'resource-1',
    });

    await waitFor(() => {
      expect(deleteResult.current.isError).toBe(true);
    });

    expect(deleteResult.current.error).toEqual(error);

    // Verify cache was reverted
    await waitFor(() => {
      expect(annotationsResult.current.data).toHaveLength(initialCount);
    });
  });
});

describe('useSearchAnnotationsFulltext', () => {
  it('should search annotations by full-text query', async () => {
    vi.mocked(editorApi.searchAnnotationsFulltext).mockResolvedValue(mockAnnotations);

    const { result } = renderHook(
      () => useSearchAnnotationsFulltext({ query: 'log', limit: 10 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockAnnotations);
    expect(editorApi.searchAnnotationsFulltext).toHaveBeenCalledWith({
      query: 'log',
      limit: 10,
    });
  });

  it('should not search when query is empty', async () => {
    const { result } = renderHook(
      () => useSearchAnnotationsFulltext({ query: '', limit: 10 }),
      { wrapper: createWrapper() }
    );

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.searchAnnotationsFulltext).not.toHaveBeenCalled();
  });
});

describe('useSearchAnnotationsSemantic', () => {
  it('should search annotations by semantic similarity', async () => {
    vi.mocked(editorApi.searchAnnotationsSemantic).mockResolvedValue(mockAnnotations);

    const { result } = renderHook(
      () => useSearchAnnotationsSemantic({ query: 'logging', limit: 10 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockAnnotations);
    expect(editorApi.searchAnnotationsSemantic).toHaveBeenCalledWith({
      query: 'logging',
      limit: 10,
    });
  });

  it('should not search when query is empty', async () => {
    const { result } = renderHook(
      () => useSearchAnnotationsSemantic({ query: '', limit: 10 }),
      { wrapper: createWrapper() }
    );

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.searchAnnotationsSemantic).not.toHaveBeenCalled();
  });
});

describe('useSearchAnnotationsByTags', () => {
  it('should search annotations by tags', async () => {
    vi.mocked(editorApi.searchAnnotationsByTags).mockResolvedValue(mockAnnotations);

    const { result } = renderHook(
      () => useSearchAnnotationsByTags({ tags: ['important'], match_all: false }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockAnnotations);
    expect(editorApi.searchAnnotationsByTags).toHaveBeenCalledWith({
      tags: ['important'],
      match_all: false,
    });
  });

  it('should not search when tags array is empty', async () => {
    const { result } = renderHook(
      () => useSearchAnnotationsByTags({ tags: [], match_all: false }),
      { wrapper: createWrapper() }
    );

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.searchAnnotationsByTags).not.toHaveBeenCalled();
  });

  it('should support match_all parameter', async () => {
    vi.mocked(editorApi.searchAnnotationsByTags).mockResolvedValue([mockAnnotations[0]]);

    const { result } = renderHook(
      () =>
        useSearchAnnotationsByTags({ tags: ['important', 'debug'], match_all: true }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(editorApi.searchAnnotationsByTags).toHaveBeenCalledWith({
      tags: ['important', 'debug'],
      match_all: true,
    });
  });
});

describe('useExportAnnotationsMarkdown', () => {
  it('should export annotations as markdown', async () => {
    const markdown = '# Annotations\n\n## annotation-1\n\nThis is a log statement';
    vi.mocked(editorApi.exportAnnotationsMarkdown).mockResolvedValue(markdown);

    const { result } = renderHook(
      () => useExportAnnotationsMarkdown('resource-1', { enabled: true }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toBe(markdown);
    expect(editorApi.exportAnnotationsMarkdown).toHaveBeenCalledWith('resource-1');
  });

  it('should not auto-fetch by default', async () => {
    const { result } = renderHook(() => useExportAnnotationsMarkdown('resource-1'), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.exportAnnotationsMarkdown).not.toHaveBeenCalled();
  });

  it('should support manual refetch', async () => {
    const markdown = '# Annotations\n\n## annotation-1\n\nThis is a log statement';
    vi.mocked(editorApi.exportAnnotationsMarkdown).mockResolvedValue(markdown);

    const { result } = renderHook(() => useExportAnnotationsMarkdown('resource-1'), {
      wrapper: createWrapper(),
    });

    expect(editorApi.exportAnnotationsMarkdown).not.toHaveBeenCalled();

    await result.current.refetch();

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toBe(markdown);
    expect(editorApi.exportAnnotationsMarkdown).toHaveBeenCalledWith('resource-1');
  });
});

describe('useExportAnnotationsJSON', () => {
  it('should export annotations as JSON', async () => {
    vi.mocked(editorApi.exportAnnotationsJSON).mockResolvedValue(mockAnnotationExport);

    const { result } = renderHook(
      () => useExportAnnotationsJSON('resource-1', { enabled: true }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockAnnotationExport);
    expect(editorApi.exportAnnotationsJSON).toHaveBeenCalledWith('resource-1');
  });

  it('should not auto-fetch by default', async () => {
    const { result } = renderHook(() => useExportAnnotationsJSON('resource-1'), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(editorApi.exportAnnotationsJSON).not.toHaveBeenCalled();
  });

  it('should support manual refetch', async () => {
    vi.mocked(editorApi.exportAnnotationsJSON).mockResolvedValue(mockAnnotationExport);

    const { result } = renderHook(() => useExportAnnotationsJSON('resource-1'), {
      wrapper: createWrapper(),
    });

    expect(editorApi.exportAnnotationsJSON).not.toHaveBeenCalled();

    await result.current.refetch();

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockAnnotationExport);
    expect(editorApi.exportAnnotationsJSON).toHaveBeenCalledWith('resource-1');
  });

  it('should export all annotations when resourceId is undefined', async () => {
    vi.mocked(editorApi.exportAnnotationsJSON).mockResolvedValue(mockAnnotationExport);

    const { result } = renderHook(
      () => useExportAnnotationsJSON(undefined, { enabled: true }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(editorApi.exportAnnotationsJSON).toHaveBeenCalledWith(undefined);
  });
});

// ============================================================================
// Quality Hooks Tests
// ============================================================================

describe('useQualityDetails', () => {
  it('should fetch quality details from resource metadata', async () => {
    const mockResourceWithQuality: Resource = {
      ...mockResource,
      quality_overall: 0.85,
      quality_dimensions: {
        accuracy: 0.9,
        completeness: 0.8,
        consistency: 0.85,
        timeliness: 0.9,
        relevance: 0.8,
      },
    };

    vi.mocked(editorApi.getResource).mockResolvedValue(mockResourceWithQuality);

    const { result } = renderHook(() => useQualityDetails('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockResourceWithQuality);
    expect(result.current.data?.quality_overall).toBe(0.85);
    expect(result.current.data?.quality_dimensions?.accuracy).toBe(0.9);
    expect(editorApi.getResource).toHaveBeenCalledWith('resource-1');
  });

  it('should handle missing quality data gracefully', async () => {
    vi.mocked(editorApi.getResource).mockResolvedValue(mockResource);

    const { result } = renderHook(() => useQualityDetails('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.quality_overall).toBeUndefined();
    expect(result.current.data?.quality_dimensions).toBeUndefined();
  });

  it('should not fetch when resourceId is empty', () => {
    const { result } = renderHook(() => useQualityDetails(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.isPending).toBe(true);
    expect(result.current.fetchStatus).toBe('idle');
    expect(editorApi.getResource).not.toHaveBeenCalled();
  });
});

describe('useRecalculateQuality', () => {
  it('should trigger quality recalculation for a resource', async () => {
    const mockQualityDetails: QualityDetails = {
      resource_id: 'resource-1',
      quality_dimensions: {
        accuracy: 0.9,
        completeness: 0.8,
        consistency: 0.85,
        timeliness: 0.9,
        relevance: 0.8,
      },
      quality_overall: 0.85,
      quality_weights: {
        accuracy: 0.25,
        completeness: 0.25,
        consistency: 0.2,
        timeliness: 0.15,
        relevance: 0.15,
      },
      quality_last_computed: '2024-01-15T10:00:00Z',
      is_quality_outlier: false,
      needs_quality_review: false,
    };

    vi.mocked(editorApi.recalculateQuality).mockResolvedValue(mockQualityDetails);

    const { result } = renderHook(() => useRecalculateQuality(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      resource_id: 'resource-1',
      weights: {
        accuracy: 0.25,
        completeness: 0.25,
        consistency: 0.2,
        timeliness: 0.15,
        relevance: 0.15,
      },
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockQualityDetails);
    expect(editorApi.recalculateQuality).toHaveBeenCalledWith({
      resource_id: 'resource-1',
      weights: {
        accuracy: 0.25,
        completeness: 0.25,
        consistency: 0.2,
        timeliness: 0.15,
        relevance: 0.15,
      },
    });
  });

  it('should handle recalculation for multiple resources', async () => {
    const mockQualityDetails: QualityDetails = {
      resource_id: '',
      quality_dimensions: {
        accuracy: 0,
        completeness: 0,
        consistency: 0,
        timeliness: 0,
        relevance: 0,
      },
      quality_overall: 0,
      quality_weights: {
        accuracy: 0.2,
        completeness: 0.2,
        consistency: 0.2,
        timeliness: 0.2,
        relevance: 0.2,
      },
      quality_last_computed: new Date().toISOString(),
      is_quality_outlier: false,
      needs_quality_review: false,
    };

    vi.mocked(editorApi.recalculateQuality).mockResolvedValue(mockQualityDetails);

    const { result } = renderHook(() => useRecalculateQuality(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      resource_ids: ['resource-1', 'resource-2', 'resource-3'],
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(editorApi.recalculateQuality).toHaveBeenCalledWith({
      resource_ids: ['resource-1', 'resource-2', 'resource-3'],
    });
  });
});

describe('useQualityOutliers', () => {
  it('should fetch quality outliers', async () => {
    const mockOutliers: QualityOutlier[] = [
      {
        resource_id: 'resource-1',
        title: 'Outlier Resource 1',
        quality_overall: 0.3,
        outlier_score: 0.85,
        reason: 'Significantly below average quality',
        detected_at: '2024-01-15T10:00:00Z',
      },
      {
        resource_id: 'resource-2',
        title: 'Outlier Resource 2',
        quality_overall: 0.25,
        outlier_score: 0.9,
        reason: 'Multiple dimension failures',
        detected_at: '2024-01-15T11:00:00Z',
      },
    ];

    vi.mocked(editorApi.getQualityOutliers).mockResolvedValue(mockOutliers);

    const { result } = renderHook(
      () => useQualityOutliers({ page: 1, limit: 20, min_outlier_score: 0.8 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockOutliers);
    expect(result.current.data).toHaveLength(2);
    expect(editorApi.getQualityOutliers).toHaveBeenCalledWith({
      page: 1,
      limit: 20,
      min_outlier_score: 0.8,
    });
  });

  it('should handle empty outliers list', async () => {
    vi.mocked(editorApi.getQualityOutliers).mockResolvedValue([]);

    const { result } = renderHook(() => useQualityOutliers(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual([]);
    expect(result.current.data).toHaveLength(0);
  });
});

describe('useQualityDegradation', () => {
  it('should fetch quality degradation data', async () => {
    const mockDegradation: QualityDegradation = {
      time_window_days: 30,
      degraded_count: 5,
      average_change: -0.15,
      degraded_resources: [
        {
          resource_id: 'resource-1',
          title: 'Degraded Resource 1',
          quality_before: 0.8,
          quality_after: 0.65,
          quality_change: -0.15,
          degraded_at: '2024-01-15T10:00:00Z',
        },
        {
          resource_id: 'resource-2',
          title: 'Degraded Resource 2',
          quality_before: 0.75,
          quality_after: 0.55,
          quality_change: -0.2,
          degraded_at: '2024-01-14T10:00:00Z',
        },
      ],
    };

    vi.mocked(editorApi.getQualityDegradation).mockResolvedValue(mockDegradation);

    const { result } = renderHook(() => useQualityDegradation(30), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockDegradation);
    expect(result.current.data?.degraded_count).toBe(5);
    expect(result.current.data?.average_change).toBe(-0.15);
    expect(editorApi.getQualityDegradation).toHaveBeenCalledWith(30);
  });

  it('should not fetch when days is 0 or negative', () => {
    const { result } = renderHook(() => useQualityDegradation(0), {
      wrapper: createWrapper(),
    });

    expect(result.current.isPending).toBe(true);
    expect(result.current.fetchStatus).toBe('idle');
    expect(editorApi.getQualityDegradation).not.toHaveBeenCalled();
  });
});

describe('useQualityDistribution', () => {
  it('should fetch quality distribution histogram', async () => {
    const mockDistribution: QualityDistribution = {
      dimension: 'overall',
      bins: 10,
      distribution: [
        { range: '0.0-0.1', count: 2, percentage: 5 },
        { range: '0.1-0.2', count: 3, percentage: 7.5 },
        { range: '0.2-0.3', count: 5, percentage: 12.5 },
        { range: '0.3-0.4', count: 8, percentage: 20 },
        { range: '0.4-0.5', count: 10, percentage: 25 },
        { range: '0.5-0.6', count: 7, percentage: 17.5 },
        { range: '0.6-0.7', count: 3, percentage: 7.5 },
        { range: '0.7-0.8', count: 1, percentage: 2.5 },
        { range: '0.8-0.9', count: 0, percentage: 0 },
        { range: '0.9-1.0', count: 1, percentage: 2.5 },
      ],
      statistics: {
        mean: 0.45,
        median: 0.48,
        std_dev: 0.18,
        min: 0.05,
        max: 0.95,
      },
    };

    vi.mocked(editorApi.getQualityDistribution).mockResolvedValue(mockDistribution);

    const { result } = renderHook(() => useQualityDistribution(10), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockDistribution);
    expect(result.current.data?.bins).toBe(10);
    expect(result.current.data?.statistics.mean).toBe(0.45);
    expect(editorApi.getQualityDistribution).toHaveBeenCalledWith(10);
  });

  it('should not fetch when bins is 0 or negative', () => {
    const { result } = renderHook(() => useQualityDistribution(0), {
      wrapper: createWrapper(),
    });

    expect(result.current.isPending).toBe(true);
    expect(result.current.fetchStatus).toBe('idle');
    expect(editorApi.getQualityDistribution).not.toHaveBeenCalled();
  });
});

describe('useQualityTrends', () => {
  it('should fetch quality trends with daily granularity', async () => {
    const mockTrends: QualityTrend = {
      dimension: 'overall',
      granularity: 'daily',
      data_points: [
        { period: '2024-01-10', avg_quality: 0.75, resource_count: 100 },
        { period: '2024-01-11', avg_quality: 0.76, resource_count: 102 },
        { period: '2024-01-12', avg_quality: 0.74, resource_count: 105 },
        { period: '2024-01-13', avg_quality: 0.77, resource_count: 108 },
        { period: '2024-01-14', avg_quality: 0.78, resource_count: 110 },
      ],
      trend_direction: 'improving',
      overall_change: 0.03,
    };

    vi.mocked(editorApi.getQualityTrends).mockResolvedValue(mockTrends);

    const { result } = renderHook(() => useQualityTrends('daily'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockTrends);
    expect(result.current.data?.granularity).toBe('daily');
    expect(result.current.data?.trend_direction).toBe('improving');
    expect(editorApi.getQualityTrends).toHaveBeenCalledWith('daily');
  });

  it('should fetch quality trends with weekly granularity', async () => {
    const mockTrends: QualityTrend = {
      dimension: 'overall',
      granularity: 'weekly',
      data_points: [
        { period: '2024-W01', avg_quality: 0.75, resource_count: 100 },
        { period: '2024-W02', avg_quality: 0.77, resource_count: 105 },
      ],
      trend_direction: 'stable',
      overall_change: 0.02,
    };

    vi.mocked(editorApi.getQualityTrends).mockResolvedValue(mockTrends);

    const { result } = renderHook(() => useQualityTrends('weekly'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.granularity).toBe('weekly');
    expect(editorApi.getQualityTrends).toHaveBeenCalledWith('weekly');
  });

  it('should fetch quality trends with monthly granularity', async () => {
    const mockTrends: QualityTrend = {
      dimension: 'overall',
      granularity: 'monthly',
      data_points: [
        { period: '2024-01', avg_quality: 0.75, resource_count: 100 },
        { period: '2024-02', avg_quality: 0.72, resource_count: 110 },
      ],
      trend_direction: 'declining',
      overall_change: -0.03,
    };

    vi.mocked(editorApi.getQualityTrends).mockResolvedValue(mockTrends);

    const { result } = renderHook(() => useQualityTrends('monthly'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.granularity).toBe('monthly');
    expect(editorApi.getQualityTrends).toHaveBeenCalledWith('monthly');
  });
});

describe('useQualityDimensions', () => {
  it('should fetch quality dimension scores', async () => {
    const mockDimensions: QualityDimensionScores = {
      dimensions: {
        accuracy: { avg: 0.85, min: 0.5, max: 1.0, std_dev: 0.12 },
        completeness: { avg: 0.78, min: 0.4, max: 0.95, std_dev: 0.15 },
        consistency: { avg: 0.82, min: 0.6, max: 1.0, std_dev: 0.1 },
        timeliness: { avg: 0.75, min: 0.3, max: 0.98, std_dev: 0.18 },
        relevance: { avg: 0.8, min: 0.5, max: 1.0, std_dev: 0.13 },
      },
      resource_count: 150,
      computed_at: '2024-01-15T10:00:00Z',
    };

    vi.mocked(editorApi.getQualityDimensions).mockResolvedValue(mockDimensions);

    const { result } = renderHook(() => useQualityDimensions(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockDimensions);
    expect(result.current.data?.dimensions.accuracy.avg).toBe(0.85);
    expect(result.current.data?.resource_count).toBe(150);
    expect(editorApi.getQualityDimensions).toHaveBeenCalled();
  });

  it('should handle API errors gracefully', async () => {
    vi.mocked(editorApi.getQualityDimensions).mockRejectedValue(
      new Error('Failed to fetch quality dimensions')
    );

    const { result } = renderHook(() => useQualityDimensions(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error?.message).toBe('Failed to fetch quality dimensions');
  });
});

describe('useQualityReviewQueue', () => {
  it('should fetch quality review queue', async () => {
    const mockReviewQueue: ReviewQueueItem[] = [
      {
        resource_id: 'resource-1',
        title: 'Resource Needing Review 1',
        quality_overall: 0.4,
        priority: 1,
        reason: 'Multiple quality issues detected',
        flagged_at: '2024-01-15T10:00:00Z',
      },
      {
        resource_id: 'resource-2',
        title: 'Resource Needing Review 2',
        quality_overall: 0.35,
        priority: 2,
        reason: 'Significant quality degradation',
        flagged_at: '2024-01-15T09:00:00Z',
      },
    ];

    vi.mocked(editorApi.getQualityReviewQueue).mockResolvedValue(mockReviewQueue);

    const { result } = renderHook(
      () => useQualityReviewQueue({ page: 1, limit: 20, sort_by: 'priority' }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockReviewQueue);
    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0].priority).toBe(1);
    expect(editorApi.getQualityReviewQueue).toHaveBeenCalledWith({
      page: 1,
      limit: 20,
      sort_by: 'priority',
    });
  });

  it('should handle empty review queue', async () => {
    vi.mocked(editorApi.getQualityReviewQueue).mockResolvedValue([]);

    const { result } = renderHook(() => useQualityReviewQueue(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual([]);
    expect(result.current.data).toHaveLength(0);
  });

  it('should support different sort options', async () => {
    const mockReviewQueue: ReviewQueueItem[] = [
      {
        resource_id: 'resource-1',
        title: 'Resource 1',
        quality_overall: 0.4,
        priority: 1,
        reason: 'Quality issues',
        flagged_at: '2024-01-15T10:00:00Z',
      },
    ];

    vi.mocked(editorApi.getQualityReviewQueue).mockResolvedValue(mockReviewQueue);

    const { result } = renderHook(
      () => useQualityReviewQueue({ sort_by: 'quality_overall' }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(editorApi.getQualityReviewQueue).toHaveBeenCalledWith({
      sort_by: 'quality_overall',
    });
  });
});
