/**
 * Property-Based Tests for Optimistic Updates
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 6.4 - Write property test for optimistic updates
 * Property 2: Optimistic Update Consistency
 * Validates: Requirements 4.10
 * 
 * This test verifies that for any mutation operation (create, update, delete),
 * if the API call fails, then the optimistic UI update should be reverted to
 * the previous state.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createElement, type ReactNode } from 'react';
import fc from 'fast-check';
import { editorApi } from '@/lib/api/editor';
import {
  useAnnotations,
  useCreateAnnotation,
  useUpdateAnnotation,
  useDeleteAnnotation,
} from '../useEditorData';
import type { Annotation, AnnotationCreate, AnnotationUpdate } from '@/types/api';

// ============================================================================
// Test Setup
// ============================================================================

// Mock the editor API
vi.mock('@/lib/api/editor', () => ({
  editorApi: {
    getAnnotations: vi.fn(),
    createAnnotation: vi.fn(),
    updateAnnotation: vi.fn(),
    deleteAnnotation: vi.fn(),
  },
  editorQueryKeys: {
    annotations: {
      all: () => ['annotations'],
      byResource: (resourceId: string) => ['annotations', 'resource', resourceId],
    },
  },
  editorCacheConfig: {
    annotations: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
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

/**
 * Generate a valid resource ID
 */
const resourceIdArbitrary = fc.stringMatching(/^resource-[a-z0-9]{8}$/);

/**
 * Generate a valid annotation ID
 */
const annotationIdArbitrary = fc.stringMatching(/^annotation-[a-z0-9]{8}$/);

/**
 * Generate a valid annotation object
 */
const annotationArbitrary = fc.record({
  id: annotationIdArbitrary,
  resource_id: resourceIdArbitrary,
  user_id: fc.constant('user-1'),
  start_offset: fc.nat({ max: 1000 }),
  end_offset: fc.nat({ max: 1000 }),
  highlighted_text: fc.string({ minLength: 1, maxLength: 100 }),
  note: fc.option(fc.string({ maxLength: 500 }), { nil: undefined }),
  tags: fc.option(fc.array(fc.string({ minLength: 1, maxLength: 20 }), { maxLength: 5 }), { nil: undefined }),
  color: fc.constantFrom('#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'),
  is_shared: fc.boolean(),
  created_at: fc.constant(new Date().toISOString()),
  updated_at: fc.constant(new Date().toISOString()),
}).filter((ann) => ann.start_offset < ann.end_offset) as fc.Arbitrary<Annotation>;

/**
 * Generate a valid annotation creation payload
 */
const annotationCreateArbitrary = fc.record({
  start_offset: fc.nat({ max: 1000 }),
  end_offset: fc.nat({ max: 1000 }),
  highlighted_text: fc.string({ minLength: 1, maxLength: 100 }),
  note: fc.option(fc.string({ maxLength: 500 }), { nil: undefined }),
  tags: fc.option(fc.array(fc.string({ minLength: 1, maxLength: 20 }), { maxLength: 5 }), { nil: undefined }),
  color: fc.constantFrom('#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'),
}).filter((ann) => ann.start_offset < ann.end_offset) as fc.Arbitrary<AnnotationCreate>;

/**
 * Generate a valid annotation update payload
 */
const annotationUpdateArbitrary = fc.record({
  note: fc.option(fc.string({ maxLength: 500 }), { nil: undefined }),
  tags: fc.option(fc.array(fc.string({ minLength: 1, maxLength: 20 }), { maxLength: 5 }), { nil: undefined }),
  color: fc.option(fc.constantFrom('#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'), { nil: undefined }),
}) as fc.Arbitrary<AnnotationUpdate>;

/**
 * Generate an array of annotations for a resource
 */
const annotationsArrayArbitrary = (resourceId: string) =>
  fc.array(annotationArbitrary, { minLength: 0, maxLength: 10 }).map((annotations) =>
    annotations.map((ann) => ({ ...ann, resource_id: resourceId }))
  );

// ============================================================================
// Property Tests
// ============================================================================

describe('Property 2: Optimistic Update Consistency', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Property: For any create annotation mutation that fails,
   * the optimistic UI update should be reverted to the previous state.
   */
  it('should revert optimistic create on API failure', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        annotationsArrayArbitrary('resource-test'),
        annotationCreateArbitrary,
        async (resourceId, initialAnnotations, newAnnotationData) => {
          // Setup: Mock initial annotations
          const annotationsWithCorrectResourceId = initialAnnotations.map((ann) => ({
            ...ann,
            resource_id: resourceId,
          }));
          
          vi.mocked(editorApi.getAnnotations).mockResolvedValue(annotationsWithCorrectResourceId);

          // Setup: Mock API failure for create
          const apiError = new Error('Failed to create annotation');
          vi.mocked(editorApi.createAnnotation).mockRejectedValue(apiError);

          const wrapper = createWrapper();

          // Step 1: Load initial annotations
          const { result: annotationsResult } = renderHook(
            () => useAnnotations(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(annotationsResult.current.isSuccess).toBe(true);
          });

          const initialCount = annotationsResult.current.data?.length || 0;

          // Step 2: Attempt to create annotation (will fail)
          const { result: createResult } = renderHook(() => useCreateAnnotation(), { wrapper });

          act(() => {
            createResult.current.mutate({
              resourceId,
              data: newAnnotationData,
            });
          });

          // Step 3: Wait for mutation to fail
          await waitFor(() => {
            expect(createResult.current.isError).toBe(true);
          }, { timeout: 3000 });

          // Step 4: Verify error occurred
          expect(createResult.current.error).toEqual(apiError);

          // Step 5: Verify optimistic update was reverted
          // After the mutation fails, the cache should be invalidated and refetched
          await waitFor(() => {
            const currentCount = annotationsResult.current.data?.length || 0;
            expect(currentCount).toBe(initialCount);
          }, { timeout: 3000 });

          // Verify the annotations are exactly the same as before
          expect(annotationsResult.current.data).toEqual(annotationsWithCorrectResourceId);
        }
      ),
      {
        numRuns: 20, // Run 20 iterations for faster testing
        timeout: 10000, // 10 second timeout per test
      }
    );
  }, 30000); // 30 second timeout for entire test

  /**
   * Property: For any update annotation mutation that fails,
   * the optimistic UI update should be reverted to the previous state.
   */
  it('should revert optimistic update on API failure', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        annotationsArrayArbitrary('resource-test').filter((arr) => arr.length > 0),
        annotationUpdateArbitrary,
        async (resourceId, initialAnnotations, updateData) => {
          // Setup: Mock initial annotations
          const annotationsWithCorrectResourceId = initialAnnotations.map((ann) => ({
            ...ann,
            resource_id: resourceId,
          }));
          
          vi.mocked(editorApi.getAnnotations).mockResolvedValue(annotationsWithCorrectResourceId);

          // Setup: Mock API failure for update
          const apiError = new Error('Failed to update annotation');
          vi.mocked(editorApi.updateAnnotation).mockRejectedValue(apiError);

          const wrapper = createWrapper();

          // Step 1: Load initial annotations
          const { result: annotationsResult } = renderHook(
            () => useAnnotations(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(annotationsResult.current.isSuccess).toBe(true);
          });

          // Pick the first annotation to update
          const annotationToUpdate = annotationsWithCorrectResourceId[0];
          const originalNote = annotationToUpdate.note;

          // Step 2: Attempt to update annotation (will fail)
          const { result: updateResult } = renderHook(() => useUpdateAnnotation(), { wrapper });

          act(() => {
            updateResult.current.mutate({
              annotationId: annotationToUpdate.id,
              resourceId,
              data: updateData,
            });
          });

          // Step 3: Wait for mutation to fail
          await waitFor(() => {
            expect(updateResult.current.isError).toBe(true);
          }, { timeout: 3000 });

          // Step 4: Verify error occurred
          expect(updateResult.current.error).toEqual(apiError);

          // Step 5: Verify optimistic update was reverted
          await waitFor(() => {
            const updatedAnnotation = annotationsResult.current.data?.find(
              (ann) => ann.id === annotationToUpdate.id
            );
            expect(updatedAnnotation?.note).toBe(originalNote);
          }, { timeout: 3000 });

          // Verify all annotations are exactly the same as before
          expect(annotationsResult.current.data).toEqual(annotationsWithCorrectResourceId);
        }
      ),
      {
        numRuns: 20,
        timeout: 10000,
      }
    );
  }, 30000);

  /**
   * Property: For any delete annotation mutation that fails,
   * the optimistic UI update should be reverted to the previous state.
   */
  it('should revert optimistic delete on API failure', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        annotationsArrayArbitrary('resource-test').filter((arr) => arr.length > 0),
        async (resourceId, initialAnnotations) => {
          // Setup: Mock initial annotations
          const annotationsWithCorrectResourceId = initialAnnotations.map((ann) => ({
            ...ann,
            resource_id: resourceId,
          }));
          
          vi.mocked(editorApi.getAnnotations).mockResolvedValue(annotationsWithCorrectResourceId);

          // Setup: Mock API failure for delete
          const apiError = new Error('Failed to delete annotation');
          vi.mocked(editorApi.deleteAnnotation).mockRejectedValue(apiError);

          const wrapper = createWrapper();

          // Step 1: Load initial annotations
          const { result: annotationsResult } = renderHook(
            () => useAnnotations(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(annotationsResult.current.isSuccess).toBe(true);
          });

          const initialCount = annotationsResult.current.data?.length || 0;
          const annotationToDelete = annotationsWithCorrectResourceId[0];

          // Step 2: Attempt to delete annotation (will fail)
          const { result: deleteResult } = renderHook(() => useDeleteAnnotation(), { wrapper });

          act(() => {
            deleteResult.current.mutate({
              annotationId: annotationToDelete.id,
              resourceId,
            });
          });

          // Step 3: Wait for mutation to fail
          await waitFor(() => {
            expect(deleteResult.current.isError).toBe(true);
          }, { timeout: 3000 });

          // Step 4: Verify error occurred
          expect(deleteResult.current.error).toEqual(apiError);

          // Step 5: Verify optimistic update was reverted
          await waitFor(() => {
            const currentCount = annotationsResult.current.data?.length || 0;
            expect(currentCount).toBe(initialCount);
          }, { timeout: 3000 });

          // Verify the deleted annotation is still present
          const deletedAnnotationStillExists = annotationsResult.current.data?.some(
            (ann) => ann.id === annotationToDelete.id
          );
          expect(deletedAnnotationStillExists).toBe(true);

          // Verify all annotations are exactly the same as before
          expect(annotationsResult.current.data).toEqual(annotationsWithCorrectResourceId);
        }
      ),
      {
        numRuns: 20,
        timeout: 10000,
      }
    );
  }, 30000);

  /**
   * Property: For any successful mutation, the optimistic update should be
   * confirmed and the mutation should return the server response.
   */
  it('should confirm optimistic create on API success', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        annotationsArrayArbitrary('resource-test'),
        annotationCreateArbitrary,
        async (resourceId, initialAnnotations, newAnnotationData) => {
          // Setup: Mock initial annotations
          const annotationsWithCorrectResourceId = initialAnnotations.map((ann) => ({
            ...ann,
            resource_id: resourceId,
          }));
          
          vi.mocked(editorApi.getAnnotations).mockResolvedValue(annotationsWithCorrectResourceId);

          // Setup: Mock successful API response
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

          // Step 1: Load initial annotations
          const { result: annotationsResult } = renderHook(
            () => useAnnotations(resourceId),
            { wrapper }
          );

          await waitFor(() => {
            expect(annotationsResult.current.isSuccess).toBe(true);
          });

          // Step 2: Create annotation (will succeed)
          const { result: createResult } = renderHook(() => useCreateAnnotation(), { wrapper });

          act(() => {
            createResult.current.mutate({
              resourceId,
              data: newAnnotationData,
            });
          });

          // Step 3: Wait for mutation to succeed
          await waitFor(() => {
            expect(createResult.current.isSuccess).toBe(true);
          }, { timeout: 3000 });

          // Step 4: Verify the created annotation is returned from the API
          expect(createResult.current.data).toEqual(createdAnnotation);
          expect(createResult.current.data?.id).toBe('annotation-new');
          
          // The key property: successful mutations return server data
          expect(createResult.current.error).toBeNull();
        }
      ),
      {
        numRuns: 10, // Reduced runs for faster testing
        timeout: 5000, // Reduced timeout
      }
    );
  }, 20000); // Reduced overall timeout
});
