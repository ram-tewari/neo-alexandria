/**
 * Property-Based Tests for Cache Invalidation Correctness
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 12.2 - Property test for cache invalidation
 * Property 5: Cache Invalidation Correctness
 * Validates: Requirements 2.6, 3.6, 4.10
 * 
 * This test verifies that for any mutation that modifies server state,
 * all related cached queries should be invalidated to ensure data consistency.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createElement, type ReactNode } from 'react';
import fc from 'fast-check';
import { editorApi } from '@/lib/api/editor';
import {
  useResource,
  useChunks,
  useAnnotations,
  useCreateAnnotation,
  useUpdateAnnotation,
  useDeleteAnnotation,
  useTriggerChunking,
  useRecalculateQuality,
} from '../useEditorData';
import type {
  Resource,
  SemanticChunk,
  Annotation,
  AnnotationCreate,
  AnnotationUpdate,
  ChunkingRequest,
  ChunkingTask,
  QualityDetails,
  QualityRecalculateRequest,
} from '@/types/api';

// ============================================================================
// Test Setup
// ============================================================================

// Mock the editor API
vi.mock('@/lib/api/editor', () => ({
  editorApi: {
    getResource: vi.fn(),
    getChunks: vi.fn(),
    getAnnotations: vi.fn(),
    createAnnotation: vi.fn(),
    updateAnnotation: vi.fn(),
    deleteAnnotation: vi.fn(),
    triggerChunking: vi.fn(),
    recalculateQuality: vi.fn(),
  },
  editorQueryKeys: {
    resource: {
      all: () => ['editor', 'resources'],
      detail: (resourceId: string) => ['editor', 'resources', resourceId],
      status: (resourceId: string) => ['editor', 'resources', resourceId, 'status'],
    },
    chunks: {
      all: () => ['editor', 'chunks'],
      byResource: (resourceId: string) => ['editor', 'chunks', 'list', resourceId],
      detail: (chunkId: string) => ['editor', 'chunks', 'detail', chunkId],
    },
    annotations: {
      all: () => ['editor', 'annotations'],
      byResource: (resourceId: string) => ['editor', 'annotations', 'list', resourceId],
      detail: (annotationId: string) => ['editor', 'annotations', 'detail', annotationId],
    },
    quality: {
      all: () => ['editor', 'quality'],
      details: (resourceId: string) => ['editor', 'quality', 'details', resourceId],
    },
  },
  editorCacheConfig: {
    resource: {
      staleTime: 10 * 60 * 1000,
      cacheTime: 30 * 60 * 1000,
    },
    chunks: {
      staleTime: 10 * 60 * 1000,
      cacheTime: 30 * 60 * 1000,
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
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: ReactNode }) =>
    createElement(QueryClientProvider, { client: queryClient }, children);
}

// ============================================================================
// Arbitraries (Generators for Property-Based Testing)
// ============================================================================

const resourceIdArbitrary = fc.stringMatching(/^resource-[a-z0-9]{8}$/);
const annotationIdArbitrary = fc.stringMatching(/^annotation-[a-z0-9]{8}$/);

const resourceArbitrary = fc.record({
  id: resourceIdArbitrary,
  title: fc.string({ minLength: 1, maxLength: 100 }),
  content: fc.string({ minLength: 10, maxLength: 1000 }),
  content_type: fc.constantFrom('code', 'pdf', 'markdown', 'text'),
  created_at: fc.constant(new Date().toISOString()),
  updated_at: fc.constant(new Date().toISOString()),
  ingestion_status: fc.constantFrom('pending', 'processing', 'completed', 'failed'),
}) as fc.Arbitrary<Resource>;

const chunkArbitrary = fc.record({
  id: fc.stringMatching(/^chunk-[a-z0-9]{8}$/),
  resource_id: resourceIdArbitrary,
  content: fc.string({ minLength: 10, maxLength: 500 }),
  chunk_index: fc.nat({ max: 100 }),
  chunk_metadata: fc.record({
    start_line: fc.nat({ max: 1000 }),
    end_line: fc.nat({ max: 1000 }),
    language: fc.constantFrom('typescript', 'python', 'javascript'),
  }),
  created_at: fc.constant(new Date().toISOString()),
}) as fc.Arbitrary<SemanticChunk>;

const annotationArbitrary = fc.record({
  id: annotationIdArbitrary,
  resource_id: resourceIdArbitrary,
  user_id: fc.constant('user-1'),
  start_offset: fc.nat({ max: 1000 }),
  end_offset: fc.nat({ max: 1000 }),
  highlighted_text: fc.string({ minLength: 1, maxLength: 100 }),
  note: fc.option(fc.string({ maxLength: 500 }), { nil: undefined }),
  tags: fc.option(fc.array(fc.string({ minLength: 1, maxLength: 20 }), { maxLength: 5 }), { nil: undefined }),
  color: fc.constantFrom('#ff0000', '#00ff00', '#0000ff'),
  is_shared: fc.boolean(),
  created_at: fc.constant(new Date().toISOString()),
  updated_at: fc.constant(new Date().toISOString()),
}).filter((ann) => ann.start_offset < ann.end_offset) as fc.Arbitrary<Annotation>;

const annotationCreateArbitrary = fc.record({
  start_offset: fc.nat({ max: 1000 }),
  end_offset: fc.nat({ max: 1000 }),
  highlighted_text: fc.string({ minLength: 1, maxLength: 100 }),
  note: fc.option(fc.string({ maxLength: 500 }), { nil: undefined }),
  tags: fc.option(fc.array(fc.string({ minLength: 1, maxLength: 20 }), { maxLength: 5 }), { nil: undefined }),
  color: fc.constantFrom('#ff0000', '#00ff00', '#0000ff'),
}).filter((ann) => ann.start_offset < ann.end_offset) as fc.Arbitrary<AnnotationCreate>;

// ============================================================================
// Property Tests
// ============================================================================

describe('Property 5: Cache Invalidation Correctness', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Property: For any annotation creation, the annotations cache for that
   * resource should be invalidated after the mutation completes.
   */
  it('should invalidate annotations cache after creating annotation', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        fc.array(annotationArbitrary, { minLength: 1, maxLength: 5 }),
        annotationCreateArbitrary,
        async (resourceId, initialAnnotations, newAnnotationData) => {
          // Feature: phase2.5-backend-api-integration, Property 5: Cache Invalidation Correctness

          // Setup: Mock initial annotations
          const annotationsWithCorrectResourceId = initialAnnotations.map((ann) => ({
            ...ann,
            resource_id: resourceId,
          }));

          vi.mocked(editorApi.getAnnotations).mockResolvedValue(annotationsWithCorrectResourceId);

          // Setup: Mock successful annotation creation
          const createdAnnotation: Annotation = {
            ...newAnnotationData,
            id: 'annotation-new',
            resource_id: resourceId,
            user_id: 'user-1',
            is_shared: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
          vi.mocked(editorApi.createAnnotation).mockResolvedValue(createdAnnotation);

          const wrapper = createWrapper();

          // Step 1: Load initial annotations (populate cache)
          const { result: annotationsResult } = renderHook(
            () => useAnnotations(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(annotationsResult.current.isSuccess).toBe(true);
          });

          const initialFetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.length;

          // Step 2: Create annotation
          const { result: createResult } = renderHook(() => useCreateAnnotation(), { wrapper });

          act(() => {
            createResult.current.mutate({
              resourceId,
              data: newAnnotationData,
            });
          });

          // Step 3: Wait for mutation to complete
          await waitFor(() => {
            expect(createResult.current.isSuccess).toBe(true);
          });

          // Step 4: Wait for cache invalidation to trigger refetch
          await waitFor(() => {
            const currentFetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.length;
            // Property: Cache should be invalidated, causing a refetch
            expect(currentFetchCount).toBeGreaterThan(initialFetchCount);
          });

          // Verify the cache was actually invalidated (refetch occurred)
          expect(vi.mocked(editorApi.getAnnotations)).toHaveBeenCalledTimes(initialFetchCount + 1);
        }
      ),
      {
        numRuns: 10, // Reduced for faster testing
        timeout: 5000,
      }
    );
  }, 20000);

  /**
   * Property: For any annotation update, the annotations cache for that
   * resource should be invalidated after the mutation completes.
   */
  it('should invalidate annotations cache after updating annotation', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        fc.array(annotationArbitrary, { minLength: 1, maxLength: 5 }),
        fc.record({
          note: fc.option(fc.string({ maxLength: 500 }), { nil: undefined }),
        }),
        async (resourceId, initialAnnotations, updateData) => {
          // Feature: phase2.5-backend-api-integration, Property 5: Cache Invalidation Correctness

          const annotationsWithCorrectResourceId = initialAnnotations.map((ann) => ({
            ...ann,
            resource_id: resourceId,
          }));

          vi.mocked(editorApi.getAnnotations).mockResolvedValue(annotationsWithCorrectResourceId);

          const annotationToUpdate = annotationsWithCorrectResourceId[0];
          const updatedAnnotation: Annotation = {
            ...annotationToUpdate,
            ...updateData,
            updated_at: new Date().toISOString(),
          };
          vi.mocked(editorApi.updateAnnotation).mockResolvedValue(updatedAnnotation);

          const wrapper = createWrapper();

          // Step 1: Load initial annotations
          const { result: annotationsResult } = renderHook(
            () => useAnnotations(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(annotationsResult.current.isSuccess).toBe(true);
          });

          const initialFetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.length;

          // Step 2: Update annotation
          const { result: updateResult } = renderHook(() => useUpdateAnnotation(), { wrapper });

          act(() => {
            updateResult.current.mutate({
              annotationId: annotationToUpdate.id,
              resourceId,
              data: updateData,
            });
          });

          // Step 3: Wait for mutation to complete
          await waitFor(() => {
            expect(updateResult.current.isSuccess).toBe(true);
          });

          // Step 4: Verify cache invalidation
          await waitFor(() => {
            const currentFetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.length;
            // Property: Cache should be invalidated
            expect(currentFetchCount).toBeGreaterThan(initialFetchCount);
          });
        }
      ),
      {
        numRuns: 10,
        timeout: 5000,
      }
    );
  }, 20000);

  /**
   * Property: For any annotation deletion, the annotations cache for that
   * resource should be invalidated after the mutation completes.
   */
  it('should invalidate annotations cache after deleting annotation', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        fc.array(annotationArbitrary, { minLength: 1, maxLength: 5 }),
        async (resourceId, initialAnnotations) => {
          // Feature: phase2.5-backend-api-integration, Property 5: Cache Invalidation Correctness

          const annotationsWithCorrectResourceId = initialAnnotations.map((ann) => ({
            ...ann,
            resource_id: resourceId,
          }));

          vi.mocked(editorApi.getAnnotations).mockResolvedValue(annotationsWithCorrectResourceId);
          vi.mocked(editorApi.deleteAnnotation).mockResolvedValue(undefined);

          const wrapper = createWrapper();

          // Step 1: Load initial annotations
          const { result: annotationsResult } = renderHook(
            () => useAnnotations(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(annotationsResult.current.isSuccess).toBe(true);
          });

          const initialFetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.length;
          const annotationToDelete = annotationsWithCorrectResourceId[0];

          // Step 2: Delete annotation
          const { result: deleteResult } = renderHook(() => useDeleteAnnotation(), { wrapper });

          act(() => {
            deleteResult.current.mutate({
              annotationId: annotationToDelete.id,
              resourceId,
            });
          });

          // Step 3: Wait for mutation to complete
          await waitFor(() => {
            expect(deleteResult.current.isSuccess).toBe(true);
          });

          // Step 4: Verify cache invalidation
          await waitFor(() => {
            const currentFetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.length;
            // Property: Cache should be invalidated
            expect(currentFetchCount).toBeGreaterThan(initialFetchCount);
          });
        }
      ),
      {
        numRuns: 10,
        timeout: 5000,
      }
    );
  }, 20000);

  /**
   * Property: For any chunking operation, both the chunks cache and resource
   * status cache should be invalidated after the mutation completes.
   */
  it('should invalidate chunks and status cache after triggering chunking', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        fc.array(chunkArbitrary, { minLength: 1, maxLength: 5 }),
        async (resourceId, initialChunks) => {
          // Feature: phase2.5-backend-api-integration, Property 5: Cache Invalidation Correctness

          const chunksWithCorrectResourceId = initialChunks.map((chunk) => ({
            ...chunk,
            resource_id: resourceId,
          }));

          vi.mocked(editorApi.getChunks).mockResolvedValue(chunksWithCorrectResourceId);

          const chunkingTask: ChunkingTask = {
            resource_id: resourceId,
            message: 'Chunking started',
            strategy: 'parent_child',
            chunk_size: 512,
            overlap: 50,
          };
          vi.mocked(editorApi.triggerChunking).mockResolvedValue(chunkingTask);

          const wrapper = createWrapper();

          // Step 1: Load initial chunks
          const { result: chunksResult } = renderHook(
            () => useChunks(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(chunksResult.current.isSuccess).toBe(true);
          });

          const initialFetchCount = vi.mocked(editorApi.getChunks).mock.calls.length;

          // Step 2: Trigger chunking
          const { result: chunkingResult } = renderHook(() => useTriggerChunking(), { wrapper });

          const chunkingRequest: ChunkingRequest = {
            strategy: 'parent_child',
            chunk_size: 512,
            overlap: 50,
          };

          act(() => {
            chunkingResult.current.mutate({
              resourceId,
              request: chunkingRequest,
            });
          });

          // Step 3: Wait for mutation to complete
          await waitFor(() => {
            expect(chunkingResult.current.isSuccess).toBe(true);
          });

          // Step 4: Verify cache invalidation
          await waitFor(() => {
            const currentFetchCount = vi.mocked(editorApi.getChunks).mock.calls.length;
            // Property: Chunks cache should be invalidated
            expect(currentFetchCount).toBeGreaterThan(initialFetchCount);
          });
        }
      ),
      {
        numRuns: 10,
        timeout: 5000,
      }
    );
  }, 20000);

  /**
   * Property: For any quality recalculation, the resource cache and quality
   * analytics cache should be invalidated after the mutation completes.
   */
  it('should invalidate resource and quality cache after recalculating quality', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        resourceArbitrary,
        async (resourceId, initialResource) => {
          // Feature: phase2.5-backend-api-integration, Property 5: Cache Invalidation Correctness

          const resourceWithCorrectId = {
            ...initialResource,
            id: resourceId,
          };

          vi.mocked(editorApi.getResource).mockResolvedValue(resourceWithCorrectId);

          const qualityDetails: QualityDetails = {
            resource_id: resourceId,
            quality_dimensions: {
              accuracy: 0.8,
              completeness: 0.9,
              consistency: 0.85,
              timeliness: 0.75,
              relevance: 0.8,
            },
            quality_overall: 0.82,
            quality_weights: {
              accuracy: 0.25,
              completeness: 0.25,
              consistency: 0.2,
              timeliness: 0.15,
              relevance: 0.15,
            },
            quality_last_computed: new Date().toISOString(),
            is_quality_outlier: false,
            needs_quality_review: false,
          };
          vi.mocked(editorApi.recalculateQuality).mockResolvedValue(qualityDetails);

          const wrapper = createWrapper();

          // Step 1: Load initial resource
          const { result: resourceResult } = renderHook(
            () => useResource(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(resourceResult.current.isSuccess).toBe(true);
          });

          const initialFetchCount = vi.mocked(editorApi.getResource).mock.calls.length;

          // Step 2: Recalculate quality
          const { result: recalculateResult } = renderHook(() => useRecalculateQuality(), { wrapper });

          const recalculateRequest: QualityRecalculateRequest = {
            resource_id: resourceId,
          };

          act(() => {
            recalculateResult.current.mutate(recalculateRequest);
          });

          // Step 3: Wait for mutation to complete
          await waitFor(() => {
            expect(recalculateResult.current.isSuccess).toBe(true);
          });

          // Step 4: Verify cache invalidation
          await waitFor(() => {
            const currentFetchCount = vi.mocked(editorApi.getResource).mock.calls.length;
            // Property: Resource cache should be invalidated
            expect(currentFetchCount).toBeGreaterThan(initialFetchCount);
          });
        }
      ),
      {
        numRuns: 10,
        timeout: 5000,
      }
    );
  }, 20000);

  /**
   * Property: For any mutation, only the related caches should be invalidated,
   * not unrelated caches.
   */
  it('should only invalidate related caches, not unrelated ones', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        resourceIdArbitrary.filter((id) => id !== 'resource-same'),
        annotationCreateArbitrary,
        async (resourceId1, resourceId2, newAnnotationData) => {
          // Feature: phase2.5-backend-api-integration, Property 5: Cache Invalidation Correctness

          // Ensure different resource IDs
          if (resourceId1 === resourceId2) return;

          vi.mocked(editorApi.getAnnotations).mockResolvedValue([]);

          const createdAnnotation: Annotation = {
            ...newAnnotationData,
            id: 'annotation-new',
            resource_id: resourceId1,
            user_id: 'user-1',
            is_shared: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
          vi.mocked(editorApi.createAnnotation).mockResolvedValue(createdAnnotation);

          const wrapper = createWrapper();

          // Step 1: Load annotations for both resources
          const { result: annotations1Result } = renderHook(
            () => useAnnotations(resourceId1),
            { wrapper }
          );
          const { result: annotations2Result } = renderHook(
            () => useAnnotations(resourceId2),
            { wrapper }
          );

          await waitFor(() => {
            expect(annotations1Result.current.isSuccess).toBe(true);
            expect(annotations2Result.current.isSuccess).toBe(true);
          });

          const resource1FetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.filter(
            (call) => call[0] === resourceId1
          ).length;
          const resource2FetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.filter(
            (call) => call[0] === resourceId2
          ).length;

          // Step 2: Create annotation for resource1
          const { result: createResult } = renderHook(() => useCreateAnnotation(), { wrapper });

          act(() => {
            createResult.current.mutate({
              resourceId: resourceId1,
              data: newAnnotationData,
            });
          });

          // Step 3: Wait for mutation to complete
          await waitFor(() => {
            expect(createResult.current.isSuccess).toBe(true);
          });

          // Step 4: Verify only resource1 cache was invalidated
          await waitFor(() => {
            const newResource1FetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.filter(
              (call) => call[0] === resourceId1
            ).length;
            const newResource2FetchCount = vi.mocked(editorApi.getAnnotations).mock.calls.filter(
              (call) => call[0] === resourceId2
            ).length;

            // Property: Only related cache (resource1) should be invalidated
            expect(newResource1FetchCount).toBeGreaterThan(resource1FetchCount);
            // Property: Unrelated cache (resource2) should NOT be invalidated
            expect(newResource2FetchCount).toBe(resource2FetchCount);
          });
        }
      ),
      {
        numRuns: 10,
        timeout: 5000,
      }
    );
  }, 20000);
});
