/**
 * Annotation CRUD Integration Tests
 * 
 * Tests the complete annotation lifecycle with real API interactions:
 * - Create annotation with optimistic updates
 * - Read annotations from backend
 * - Update annotation with optimistic updates
 * - Delete annotation with optimistic updates
 * - Search functionality (fulltext, semantic, tags)
 * - Export functionality (markdown, JSON)
 * - Error recovery and rollback
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 6.5 - Write integration tests for annotation CRUD
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse, delay } from 'msw';
import { server } from '@/test/mocks/server';
import {
  useAnnotations,
  useCreateAnnotation,
  useUpdateAnnotation,
  useDeleteAnnotation,
  useSearchAnnotationsFulltext,
  useSearchAnnotationsSemantic,
  useSearchAnnotationsByTags,
  useExportAnnotationsMarkdown,
  useExportAnnotationsJSON,
} from '../useEditorData';
import type { Annotation, AnnotationCreate, AnnotationUpdate } from '@/types/api';
import React from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ============================================================================
// Test Utilities
// ============================================================================

/**
 * Create a fresh QueryClient for each test to avoid cache pollution
 */
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Disable retries in tests
        gcTime: 0, // Disable cache persistence
      },
      mutations: {
        retry: false,
      },
    },
  });
}

/**
 * Wrapper component that provides QueryClient context
 */
function createWrapper(queryClient: QueryClient) {
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

/**
 * Create a mock annotation for testing
 */
function createMockAnnotation(overrides?: Partial<Annotation>): Annotation {
  return {
    id: `annotation-${Date.now()}`,
    resource_id: 'resource-1',
    user_id: 'user-1',
    start_offset: 0,
    end_offset: 10,
    highlighted_text: 'test code',
    note: 'Test annotation',
    tags: ['test'],
    color: '#ffeb3b',
    context_before: 'before ',
    context_after: ' after',
    is_shared: false,
    collection_ids: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
}

// ============================================================================
// Test Suite: Annotation CRUD Lifecycle
// ============================================================================

describe('Annotation CRUD Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = createTestQueryClient();
  });

  afterEach(() => {
    queryClient.clear();
  });

  // ==========================================================================
  // Test: Complete Annotation Lifecycle (Create → Read → Update → Delete)
  // ==========================================================================

  it('should complete full annotation lifecycle', async () => {
    /**
     * Requirements: 4.1, 4.2, 4.3, 4.4, 4.9, 4.10
     * 
     * This test verifies the complete annotation workflow:
     * 1. Create annotation with optimistic update
     * 2. Read annotations from backend
     * 3. Update annotation with optimistic update
     * 4. Delete annotation with optimistic update
     * 5. Verify optimistic updates and rollback on errors
     */

    const resourceId = 'resource-1';
    const mockAnnotation = createMockAnnotation({ resource_id: resourceId });

    // Setup: Mock backend responses
    server.use(
      // GET /annotations - Initially empty (paginated response)
      http.get(`${API_BASE_URL}/annotations`, () => {
        return HttpResponse.json({
          items: [],
          total: 0,
          page: 1,
          limit: 50,
        });
      }),

      // POST /annotations - Create annotation
      http.post(`${API_BASE_URL}/annotations`, async ({ request }) => {
        const body = await request.json() as AnnotationCreate;
        return HttpResponse.json({
          ...body,
          id: mockAnnotation.id,
          user_id: 'user-1',
          created_at: mockAnnotation.created_at,
          updated_at: mockAnnotation.updated_at,
        });
      }),

      // PUT /annotations/:id - Update annotation
      http.put(`${API_BASE_URL}/annotations/:id`, async ({ request, params }) => {
        const body = await request.json() as AnnotationUpdate;
        return HttpResponse.json({
          ...mockAnnotation,
          ...body,
          id: params.id as string,
          updated_at: new Date().toISOString(),
        });
      }),

      // DELETE /annotations/:id - Delete annotation
      http.delete(`${API_BASE_URL}/annotations/:id`, () => {
        return new HttpResponse(null, { status: 204 });
      })
    );

    // Step 1: Fetch initial annotations (should be empty)
    const { result: annotationsResult } = renderHook(
      () => useAnnotations(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    expect(annotationsResult.current.data).toEqual([]);

    // Step 2: Create annotation
    const { result: createResult } = renderHook(
      () => useCreateAnnotation(),
      { wrapper: createWrapper(queryClient) }
    );

    const createData: AnnotationCreate = {
      resource_id: resourceId,
      start_offset: mockAnnotation.start_offset,
      end_offset: mockAnnotation.end_offset,
      highlighted_text: mockAnnotation.highlighted_text,
      note: mockAnnotation.note,
      tags: mockAnnotation.tags,
      color: mockAnnotation.color,
    };

    act(() => {
      createResult.current.mutate({ resourceId, data: createData });
    });

    // Verify optimistic update (annotation appears immediately)
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations).toHaveLength(1);
      expect(annotations?.[0].highlighted_text).toBe(mockAnnotation.highlighted_text);
    });

    // Wait for API confirmation
    await waitFor(() => {
      expect(createResult.current.isSuccess).toBe(true);
    });

    // Verify annotation has real ID from backend
    const createdAnnotation = createResult.current.data!;
    expect(createdAnnotation.id).toBe(mockAnnotation.id);
    expect(createdAnnotation.id).not.toMatch(/^temp-/);

    // Step 3: Update annotation
    const { result: updateResult } = renderHook(
      () => useUpdateAnnotation(),
      { wrapper: createWrapper(queryClient) }
    );

    const updateData: AnnotationUpdate = {
      note: 'Updated note',
    };

    act(() => {
      updateResult.current.mutate({
        annotationId: createdAnnotation.id,
        resourceId,
        data: updateData,
      });
    });

    // Verify optimistic update
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations?.[0].note).toBe('Updated note');
    });

    // Wait for API confirmation
    await waitFor(() => {
      expect(updateResult.current.isSuccess).toBe(true);
    });

    // Step 4: Delete annotation
    const { result: deleteResult } = renderHook(
      () => useDeleteAnnotation(),
      { wrapper: createWrapper(queryClient) }
    );

    act(() => {
      deleteResult.current.mutate({
        annotationId: createdAnnotation.id,
        resourceId,
      });
    });

    // Verify optimistic update (annotation removed immediately)
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations).toHaveLength(0);
    });

    // Wait for API confirmation
    await waitFor(() => {
      expect(deleteResult.current.isSuccess).toBe(true);
    });
  });

  // ==========================================================================
  // Test: Optimistic Update Rollback on Create Error
  // ==========================================================================

  it('should rollback optimistic update when create fails', async () => {
    /**
     * Requirement: 4.10 - Revert optimistic updates on failure
     * 
     * This test verifies that when an annotation creation fails,
     * the optimistic update is rolled back and the UI returns to
     * the previous state.
     */

    const resourceId = 'resource-1';

    // Setup: Mock backend to return error
    server.use(
      http.get(`${API_BASE_URL}/annotations`, () => {
        return HttpResponse.json({
          items: [],
          total: 0,
          page: 1,
          limit: 50,
        });
      }),

      http.post(`${API_BASE_URL}/annotations`, () => {
        return HttpResponse.json(
          { detail: 'Failed to create annotation' },
          { status: 500 }
        );
      })
    );

    // Fetch initial annotations
    const { result: annotationsResult } = renderHook(
      () => useAnnotations(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    const initialCount = annotationsResult.current.data?.length || 0;

    // Attempt to create annotation
    const { result: createResult } = renderHook(
      () => useCreateAnnotation(),
      { wrapper: createWrapper(queryClient) }
    );

    const createData: AnnotationCreate = {
      resource_id: resourceId,
      start_offset: 0,
      end_offset: 10,
      highlighted_text: 'test',
      color: '#ffeb3b',
    };

    act(() => {
      createResult.current.mutate({ resourceId, data: createData });
    });

    // Verify optimistic update applied
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations).toHaveLength(initialCount + 1);
    });

    // Wait for API error
    await waitFor(() => {
      expect(createResult.current.isError).toBe(true);
    });

    // Verify rollback - annotations should be back to initial count
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations).toHaveLength(initialCount);
    });
  });

  // ==========================================================================
  // Test: Optimistic Update Rollback on Update Error
  // ==========================================================================

  it('should rollback optimistic update when update fails', async () => {
    /**
     * Requirement: 4.10 - Revert optimistic updates on failure
     */

    const resourceId = 'resource-1';
    const existingAnnotation = createMockAnnotation({ resource_id: resourceId });

    // Setup: Mock backend
    server.use(
      http.get(`${API_BASE_URL}/annotations`, () => {
        return HttpResponse.json({
          items: [existingAnnotation],
          total: 1,
          page: 1,
          limit: 50,
        });
      }),

      http.put(`${API_BASE_URL}/annotations/:id`, () => {
        return HttpResponse.json(
          { detail: 'Failed to update annotation' },
          { status: 500 }
        );
      })
    );

    // Fetch annotations
    const { result: annotationsResult } = renderHook(
      () => useAnnotations(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    const originalNote = annotationsResult.current.data?.[0].note;

    // Attempt to update annotation
    const { result: updateResult } = renderHook(
      () => useUpdateAnnotation(),
      { wrapper: createWrapper(queryClient) }
    );

    act(() => {
      updateResult.current.mutate({
        annotationId: existingAnnotation.id,
        resourceId,
        data: { note: 'This should be rolled back' },
      });
    });

    // Verify optimistic update applied
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations?.[0].note).toBe('This should be rolled back');
    });

    // Wait for API error
    await waitFor(() => {
      expect(updateResult.current.isError).toBe(true);
    });

    // Verify rollback - note should be back to original
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations?.[0].note).toBe(originalNote);
    });
  });

  // ==========================================================================
  // Test: Optimistic Update Rollback on Delete Error
  // ==========================================================================

  it('should rollback optimistic update when delete fails', async () => {
    /**
     * Requirement: 4.10 - Revert optimistic updates on failure
     */

    const resourceId = 'resource-1';
    const existingAnnotation = createMockAnnotation({ resource_id: resourceId });

    // Setup: Mock backend
    server.use(
      http.get(`${API_BASE_URL}/annotations`, () => {
        return HttpResponse.json({
          items: [existingAnnotation],
          total: 1,
          page: 1,
          limit: 50,
        });
      }),

      http.delete(`${API_BASE_URL}/annotations/:id`, () => {
        return HttpResponse.json(
          { detail: 'Failed to delete annotation' },
          { status: 500 }
        );
      })
    );

    // Fetch annotations
    const { result: annotationsResult } = renderHook(
      () => useAnnotations(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    expect(annotationsResult.current.data).toHaveLength(1);

    // Attempt to delete annotation
    const { result: deleteResult } = renderHook(
      () => useDeleteAnnotation(),
      { wrapper: createWrapper(queryClient) }
    );

    act(() => {
      deleteResult.current.mutate({
        annotationId: existingAnnotation.id,
        resourceId,
      });
    });

    // Verify optimistic update applied (annotation removed)
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations).toHaveLength(0);
    });

    // Wait for API error
    await waitFor(() => {
      expect(deleteResult.current.isError).toBe(true);
    });

    // Verify rollback - annotation should be restored
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations).toHaveLength(1);
      expect(annotations?.[0].id).toBe(existingAnnotation.id);
    });
  });

  // ==========================================================================
  // Test: Search Functionality - Fulltext
  // ==========================================================================

  it('should search annotations by fulltext query', async () => {
    /**
     * Requirement: 4.5 - Search annotations by text
     */

    const searchQuery = 'important note';
    const matchingAnnotations = [
      createMockAnnotation({
        id: 'annotation-1',
        note: 'This is an important note',
        highlighted_text: 'code snippet',
      }),
      createMockAnnotation({
        id: 'annotation-2',
        note: 'Another important annotation',
        highlighted_text: 'function test()',
      }),
    ];

    // Setup: Mock search endpoint
    server.use(
      http.get(`${API_BASE_URL}/annotations/search/fulltext`, ({ request }) => {
        const url = new URL(request.url);
        const query = url.searchParams.get('query');
        
        if (query === searchQuery) {
          return HttpResponse.json({
            items: matchingAnnotations,
            total: matchingAnnotations.length,
            query: searchQuery,
          });
        }
        
        return HttpResponse.json({
          items: [],
          total: 0,
          query: query || '',
        });
      })
    );

    // Execute search
    const { result } = renderHook(
      () => useSearchAnnotationsFulltext({ query: searchQuery, limit: 20 }),
      { wrapper: createWrapper(queryClient) }
    );

    // Verify results
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0].id).toBe('annotation-1');
    expect(result.current.data?.[1].id).toBe('annotation-2');
  });

  // ==========================================================================
  // Test: Search Functionality - Semantic
  // ==========================================================================

  it('should search annotations by semantic similarity', async () => {
    /**
     * Requirement: 4.6 - Search annotations semantically
     */

    const searchQuery = 'error handling';
    const matchingAnnotations = [
      createMockAnnotation({
        id: 'annotation-1',
        note: 'Exception handling pattern',
        highlighted_text: 'try { ... } catch',
      }),
      createMockAnnotation({
        id: 'annotation-2',
        note: 'Error recovery logic',
        highlighted_text: 'if (error) { ... }',
      }),
    ];

    // Setup: Mock semantic search endpoint
    server.use(
      http.get(`${API_BASE_URL}/annotations/search/semantic`, ({ request }) => {
        const url = new URL(request.url);
        const query = url.searchParams.get('query');
        
        if (query === searchQuery) {
          return HttpResponse.json({
            items: matchingAnnotations,
            total: matchingAnnotations.length,
            query: searchQuery,
          });
        }
        
        return HttpResponse.json({
          items: [],
          total: 0,
          query: query || '',
        });
      })
    );

    // Execute search
    const { result } = renderHook(
      () => useSearchAnnotationsSemantic({ query: searchQuery, limit: 20 }),
      { wrapper: createWrapper(queryClient) }
    );

    // Verify results
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0].note).toContain('Exception');
    expect(result.current.data?.[1].note).toContain('Error recovery');
  });

  // ==========================================================================
  // Test: Search Functionality - Tags
  // ==========================================================================

  it('should search annotations by tags', async () => {
    /**
     * Requirement: 4.7 - Search annotations by tags
     */

    const searchTags = ['important', 'bug'];
    const matchingAnnotations = [
      createMockAnnotation({
        id: 'annotation-1',
        tags: ['important', 'bug', 'critical'],
        note: 'Critical bug found',
      }),
      createMockAnnotation({
        id: 'annotation-2',
        tags: ['important', 'performance'],
        note: 'Performance issue',
      }),
    ];

    // Setup: Mock tag search endpoint
    server.use(
      http.get(`${API_BASE_URL}/annotations/search/tags`, ({ request }) => {
        const url = new URL(request.url);
        const tags = url.searchParams.get('tags')?.split(',') || [];
        
        if (tags.includes('important') && tags.includes('bug')) {
          return HttpResponse.json({
            items: matchingAnnotations,
            total: matchingAnnotations.length,
            page: 1,
            limit: 50,
          });
        }
        
        return HttpResponse.json({
          items: [],
          total: 0,
          page: 1,
          limit: 50,
        });
      })
    );

    // Execute search
    const { result } = renderHook(
      () => useSearchAnnotationsByTags({ tags: searchTags, match_all: false }),
      { wrapper: createWrapper(queryClient) }
    );

    // Verify results
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0].tags).toContain('important');
    expect(result.current.data?.[0].tags).toContain('bug');
  });

  // ==========================================================================
  // Test: Export Functionality - Markdown
  // ==========================================================================

  it('should export annotations as markdown', async () => {
    /**
     * Requirement: 4.8 - Export annotations to markdown
     */

    const resourceId = 'resource-1';
    const markdownContent = `# Annotations for Resource 1

## Annotation 1
- **Text**: \`test code\`
- **Note**: Test annotation
- **Tags**: test
- **Created**: 2024-01-01

## Annotation 2
- **Text**: \`another snippet\`
- **Note**: Another note
- **Tags**: important
- **Created**: 2024-01-02
`;

    // Setup: Mock export endpoint
    server.use(
      http.get(`${API_BASE_URL}/annotations/export/markdown`, ({ request }) => {
        const url = new URL(request.url);
        const rid = url.searchParams.get('resource_id');
        
        if (rid === resourceId) {
          return HttpResponse.text(markdownContent);
        }
        
        return HttpResponse.text('');
      })
    );

    // Execute export
    const { result } = renderHook(
      () => useExportAnnotationsMarkdown(resourceId, { enabled: true }),
      { wrapper: createWrapper(queryClient) }
    );

    // Verify export
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toBe(markdownContent);
    expect(result.current.data).toContain('# Annotations for Resource 1');
    expect(result.current.data).toContain('Test annotation');
  });

  // ==========================================================================
  // Test: Export Functionality - JSON
  // ==========================================================================

  it('should export annotations as JSON', async () => {
    /**
     * Requirement: 4.8 - Export annotations to JSON
     */

    const resourceId = 'resource-1';
    const annotations = [
      createMockAnnotation({ id: 'annotation-1', resource_id: resourceId }),
      createMockAnnotation({ id: 'annotation-2', resource_id: resourceId }),
    ];

    // Setup: Mock export endpoint - returns array of annotations
    server.use(
      http.get(`${API_BASE_URL}/annotations/export/json`, ({ request }) => {
        const url = new URL(request.url);
        const rid = url.searchParams.get('resource_id');
        
        if (rid === resourceId) {
          return HttpResponse.json(annotations);
        }
        
        return HttpResponse.json([]);
      })
    );

    // Execute export
    const { result } = renderHook(
      () => useExportAnnotationsJSON(resourceId, { enabled: true }),
      { wrapper: createWrapper(queryClient) }
    );

    // Verify export
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0].id).toBe('annotation-1');
    expect(result.current.data?.[1].id).toBe('annotation-2');
  });

  // ==========================================================================
  // Test: Concurrent Operations
  // ==========================================================================

  it('should handle concurrent annotation operations correctly', async () => {
    /**
     * Requirement: 4.9, 4.10 - Handle multiple optimistic updates
     * 
     * This test verifies that multiple concurrent operations
     * (create, update, delete) are handled correctly with proper
     * optimistic updates and rollback.
     */

    const resourceId = 'resource-1';
    const annotation1 = createMockAnnotation({ id: 'annotation-1', resource_id: resourceId });
    const annotation2 = createMockAnnotation({ id: 'annotation-2', resource_id: resourceId });

    // Setup: Mock backend
    server.use(
      http.get(`${API_BASE_URL}/annotations`, () => {
        return HttpResponse.json({
          items: [annotation1],
          total: 1,
          page: 1,
          limit: 50,
        });
      }),

      http.post(`${API_BASE_URL}/annotations`, async ({ request }) => {
        await delay(100); // Simulate network delay
        const body = await request.json() as AnnotationCreate;
        return HttpResponse.json({
          ...body,
          id: annotation2.id,
          user_id: 'user-1',
          created_at: annotation2.created_at,
          updated_at: annotation2.updated_at,
        });
      }),

      http.put(`${API_BASE_URL}/annotations/:id`, async ({ request, params }) => {
        await delay(100);
        const body = await request.json() as AnnotationUpdate;
        return HttpResponse.json({
          ...annotation1,
          ...body,
          id: params.id as string,
          updated_at: new Date().toISOString(),
        });
      })
    );

    // Fetch initial annotations
    const { result: annotationsResult } = renderHook(
      () => useAnnotations(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    // Execute concurrent operations
    const { result: createResult } = renderHook(
      () => useCreateAnnotation(),
      { wrapper: createWrapper(queryClient) }
    );

    const { result: updateResult } = renderHook(
      () => useUpdateAnnotation(),
      { wrapper: createWrapper(queryClient) }
    );

    // Trigger both operations simultaneously
    act(() => {
      createResult.current.mutate({
        resourceId,
        data: {
          resource_id: resourceId,
          start_offset: 20,
          end_offset: 30,
          highlighted_text: 'new annotation',
          color: '#4caf50',
        },
      });

      updateResult.current.mutate({
        annotationId: annotation1.id,
        resourceId,
        data: { note: 'Updated concurrently' },
      });
    });

    // Verify both optimistic updates applied
    await waitFor(() => {
      const annotations = queryClient.getQueryData<Annotation[]>(['annotations', resourceId]);
      expect(annotations).toHaveLength(2); // Original + new
      expect(annotations?.find(a => a.id === annotation1.id)?.note).toBe('Updated concurrently');
    });

    // Wait for both operations to complete
    await waitFor(() => {
      expect(createResult.current.isSuccess).toBe(true);
      expect(updateResult.current.isSuccess).toBe(true);
    });
  });

  // ==========================================================================
  // Test: Empty Search Results
  // ==========================================================================

  it('should handle empty search results gracefully', async () => {
    /**
     * Requirement: 4.5, 4.6, 4.7 - Handle empty search results
     */

    // Setup: Mock empty search results
    server.use(
      http.get(`${API_BASE_URL}/annotations/search/fulltext`, () => {
        return HttpResponse.json({
          items: [],
          total: 0,
          query: 'nonexistent',
        });
      })
    );

    // Execute search
    const { result } = renderHook(
      () => useSearchAnnotationsFulltext({ query: 'nonexistent', limit: 20 }),
      { wrapper: createWrapper(queryClient) }
    );

    // Verify empty results
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([]);
  });

  // ==========================================================================
  // Test: Network Error Recovery
  // ==========================================================================

  it('should handle network errors and allow retry', async () => {
    /**
     * Requirement: 4.10 - Error recovery
     */

    const resourceId = 'resource-1';
    let attemptCount = 0;

    // Setup: Mock network error then success
    server.use(
      http.get(`${API_BASE_URL}/annotations`, () => {
        attemptCount++;
        if (attemptCount === 1) {
          return HttpResponse.error();
        }
        return HttpResponse.json({
          items: [createMockAnnotation({ resource_id: resourceId })],
          total: 1,
          page: 1,
          limit: 50,
        });
      })
    );

    // First attempt - should fail
    const { result, rerender } = renderHook(
      () => useAnnotations(resourceId),
      { wrapper: createWrapper(queryClient) }
    );

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    // Retry - should succeed
    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(1);
    expect(attemptCount).toBe(2);
  });
});
