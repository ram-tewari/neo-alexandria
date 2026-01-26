/**
 * Complete User Workflow Integration Tests
 * 
 * Tests end-to-end user workflows across multiple features:
 * - Login → Browse Repositories → Open File → Annotate
 * - Quality Recalculation Workflow
 * - Annotation Search and Export Workflow
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 13.1 - Test complete user workflows
 * Requirements: 10.1, 10.2, 10.3, 10.5
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/mocks/server';
import { ReactNode } from 'react';

// Hooks
import { useCurrentUser, useResources } from '../useWorkbenchData';
import { useResource, useAnnotations, useCreateAnnotation, useUpdateAnnotation, useDeleteAnnotation } from '../useEditorData';
import { useSearchAnnotations, useExportAnnotations } from '../useEditorData';
import { useQualityDetails, useRecalculateQuality } from '../useEditorData';

// Types
import type { User, Resource, Annotation, QualityDetails } from '../../../types/api';

// ============================================================================
// Test Setup
// ============================================================================

const mockUser: User = {
  id: 'user-1',
  email: 'test@example.com',
  username: 'testuser',
  is_active: true,
  is_premium: false,
  tier: 'free',
  created_at: '2024-01-01T00:00:00Z',
};

const mockResources: Resource[] = [
  {
    id: 'resource-1',
    title: 'main.ts',
    content: 'function main() { console.log("Hello"); }',
    content_type: 'code',
    language: 'typescript',
    file_path: '/src/main.ts',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    quality_overall: 0.85,
  },
  {
    id: 'resource-2',
    title: 'utils.ts',
    content: 'export function add(a: number, b: number) { return a + b; }',
    content_type: 'code',
    language: 'typescript',
    file_path: '/src/utils.ts',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    quality_overall: 0.92,
  },
];

const mockAnnotation: Annotation = {
  id: 'annotation-1',
  resource_id: 'resource-1',
  user_id: 'user-1',
  start_offset: 0,
  end_offset: 8,
  highlighted_text: 'function',
  note: 'Main entry point',
  tags: ['important', 'entry-point'],
  color: '#FFD700',
  is_shared: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockQualityDetails: QualityDetails = {
  resource_id: 'resource-1',
  quality_dimensions: {
    accuracy: 0.9,
    completeness: 0.8,
    consistency: 0.85,
    timeliness: 0.9,
    relevance: 0.85,
  },
  quality_overall: 0.86,
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

beforeEach(() => {
  // Server is already listening from test setup
});

afterEach(() => {
  server.resetHandlers();
});

// Test wrapper with QueryClient
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

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

// ============================================================================
// Workflow 1: Login → Browse Repositories → Open File → Annotate
// ============================================================================

describe('Complete User Workflow: Login → Browse → Open → Annotate', () => {
  it('should complete the full workflow successfully', async () => {
    /**
     * Requirements: 10.1, 10.2, 10.5
     * 
     * This test verifies the complete user workflow:
     * 1. User logs in and fetches user info
     * 2. User browses repository list
     * 3. User opens a file
     * 4. User creates an annotation
     * 5. User updates the annotation
     * 6. User deletes the annotation
     */

    const wrapper = createWrapper();

    // Setup mock handlers
    server.use(
      http.get('*/api/auth/me', () => HttpResponse.json(mockUser)),
      http.get('*/resources', () => HttpResponse.json(mockResources)),
      http.get('*/resources/:id', ({ params }) => {
        const resource = mockResources.find((r) => r.id === params.id);
        if (!resource) {
          return HttpResponse.json({ detail: 'Resource not found' }, { status: 404 });
        }
        return HttpResponse.json(resource);
      }),
      http.get('*/annotations', ({ request }) => {
        const url = new URL(request.url);
        const resourceId = url.searchParams.get('resource_id');
        if (resourceId === 'resource-1') {
          return HttpResponse.json([mockAnnotation]);
        }
        return HttpResponse.json([]);
      }),
      http.post('*/annotations', async ({ request }) => {
        const body = await request.json() as Partial<Annotation>;
        const newAnnotation: Annotation = {
          ...mockAnnotation,
          ...body,
          id: 'annotation-' + Date.now(),
          user_id: 'user-1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        return HttpResponse.json(newAnnotation);
      }),
      http.put('*/annotations/:id', async ({ params, request }) => {
        const body = await request.json() as Partial<Annotation>;
        const updatedAnnotation: Annotation = {
          ...mockAnnotation,
          ...body,
          id: params.id as string,
          updated_at: new Date().toISOString(),
        };
        return HttpResponse.json(updatedAnnotation);
      }),
      http.delete('*/annotations/:id', () => new HttpResponse(null, { status: 204 }))
    );

    // Step 1: Login - Fetch current user
    const { result: userResult } = renderHook(() => useCurrentUser(), { wrapper });

    await waitFor(() => {
      expect(userResult.current.isSuccess).toBe(true);
    });

    expect(userResult.current.data).toEqual(mockUser);

    // Step 2: Browse repositories - Fetch resource list
    const { result: resourcesResult } = renderHook(() => useResources(), { wrapper });

    await waitFor(() => {
      expect(resourcesResult.current.isSuccess).toBe(true);
    });

    expect(resourcesResult.current.data).toHaveLength(2);

    // Step 3: Open file - Fetch resource content
    const { result: resourceResult } = renderHook(() => useResource('resource-1'), { wrapper });

    await waitFor(() => {
      expect(resourceResult.current.isSuccess).toBe(true);
    });

    expect(resourceResult.current.data?.content).toContain('function main()');

    // Step 4: Create annotation
    const { result: createResult } = renderHook(() => useCreateAnnotation(), { wrapper });
    const { result: annotationsResult } = renderHook(() => useAnnotations('resource-1'), { wrapper });

    await waitFor(() => {
      expect(annotationsResult.current.isSuccess).toBe(true);
    });

    const initialCount = annotationsResult.current.data?.length || 0;

    act(() => {
      createResult.current.mutate({
        resourceId: 'resource-1',
        data: {
          start_offset: 20,
          end_offset: 30,
          highlighted_text: 'console.log',
          note: 'Debug statement',
          tags: ['debug'],
          color: '#FF0000',
        },
      });
    });

    await waitFor(() => {
      expect(createResult.current.isSuccess).toBe(true);
    });

    // Step 5: Update annotation
    const { result: updateResult } = renderHook(() => useUpdateAnnotation(), { wrapper });

    act(() => {
      updateResult.current.mutate({
        annotationId: createResult.current.data!.id,
        data: {
          note: 'Updated debug statement',
          tags: ['debug', 'updated'],
        },
      });
    });

    await waitFor(() => {
      expect(updateResult.current.isSuccess).toBe(true);
    });

    // Step 6: Delete annotation
    const { result: deleteResult } = renderHook(() => useDeleteAnnotation(), { wrapper });

    act(() => {
      deleteResult.current.mutate(createResult.current.data!.id);
    });

    await waitFor(() => {
      expect(deleteResult.current.isSuccess).toBe(true);
    });
  });

  it('should handle errors gracefully during workflow', async () => {
    /**
     * Requirements: 10.1, 10.4
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/resources/nonexistent', () => {
        return HttpResponse.json({ detail: 'Resource not found' }, { status: 404 });
      })
    );

    const { result } = renderHook(() => useResource('nonexistent'), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});

// ============================================================================
// Workflow 2: Quality Recalculation Workflow
// ============================================================================

describe('Quality Recalculation Workflow', () => {
  it('should complete quality recalculation workflow', async () => {
    /**
     * Requirements: 10.3
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/quality/:resourceId', () => HttpResponse.json(mockQualityDetails)),
      http.post('*/quality/recalculate', async ({ request }) => {
        const body = await request.json() as { resource_id: string };
        return HttpResponse.json({
          ...mockQualityDetails,
          resource_id: body.resource_id,
          quality_overall: 0.88,
          quality_last_computed: new Date().toISOString(),
        });
      })
    );

    // Step 1: Fetch initial quality data
    const { result: qualityResult } = renderHook(() => useQualityDetails('resource-1'), { wrapper });

    await waitFor(() => {
      expect(qualityResult.current.isSuccess).toBe(true);
    });

    expect(qualityResult.current.data?.quality_overall).toBe(0.86);

    // Step 2: Trigger recalculation
    const { result: recalcResult } = renderHook(() => useRecalculateQuality(), { wrapper });

    act(() => {
      recalcResult.current.mutate({
        resourceId: 'resource-1',
        weights: {
          accuracy: 0.4,
          completeness: 0.2,
          consistency: 0.2,
          timeliness: 0.1,
          relevance: 0.1,
        },
      });
    });

    await waitFor(() => {
      expect(recalcResult.current.isSuccess).toBe(true);
    });

    expect(recalcResult.current.data?.quality_overall).toBe(0.88);
  });

  it('should handle recalculation errors', async () => {
    /**
     * Requirements: 10.3, 10.4
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/quality/:resourceId', () => HttpResponse.json(mockQualityDetails)),
      http.post('*/quality/recalculate', () => {
        return HttpResponse.json({ detail: 'Internal server error' }, { status: 500 });
      })
    );

    const { result: qualityResult } = renderHook(() => useQualityDetails('resource-1'), { wrapper });

    await waitFor(() => {
      expect(qualityResult.current.isSuccess).toBe(true);
    });

    const initialQuality = qualityResult.current.data?.quality_overall;

    const { result: recalcResult } = renderHook(() => useRecalculateQuality(), { wrapper });

    act(() => {
      recalcResult.current.mutate({
        resourceId: 'resource-1',
      });
    });

    await waitFor(() => {
      expect(recalcResult.current.isError).toBe(true);
    });

    expect(qualityResult.current.data?.quality_overall).toBe(initialQuality);
  });
});

// ============================================================================
// Workflow 3: Annotation Search and Export Workflow
// ============================================================================

describe('Annotation Search and Export Workflow', () => {
  it('should complete search and export workflow', async () => {
    /**
     * Requirements: 10.1
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/annotations/search/fulltext', ({ request }) => {
        const url = new URL(request.url);
        const query = url.searchParams.get('query');
        if (query === 'entry') {
          return HttpResponse.json([mockAnnotation]);
        }
        return HttpResponse.json([]);
      }),
      http.get('*/annotations/search/tags', ({ request }) => {
        const url = new URL(request.url);
        const tags = url.searchParams.get('tags');
        if (tags?.includes('important')) {
          return HttpResponse.json([mockAnnotation]);
        }
        return HttpResponse.json([]);
      }),
      http.get('*/annotations/export/markdown', () => {
        return HttpResponse.text(`# Annotations\n\n## ${mockAnnotation.highlighted_text}\n\n${mockAnnotation.note}`);
      }),
      http.get('*/annotations/export/json', () => {
        return HttpResponse.json({
          annotations: [mockAnnotation],
          exported_at: new Date().toISOString(),
          total_count: 1,
        });
      })
    );

    // Step 1: Search by fulltext
    const { result: fulltextResult } = renderHook(
      () => useSearchAnnotations({ query: 'entry', searchType: 'fulltext' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(fulltextResult.current.isSuccess).toBe(true);
    });

    expect(fulltextResult.current.data).toHaveLength(1);

    // Step 2: Search by tags
    const { result: tagsResult } = renderHook(
      () => useSearchAnnotations({ tags: ['important'], searchType: 'tags' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(tagsResult.current.isSuccess).toBe(true);
    });

    expect(tagsResult.current.data).toHaveLength(1);

    // Step 3: Export to markdown
    const { result: markdownResult } = renderHook(
      () => useExportAnnotations({ format: 'markdown', resourceId: 'resource-1' }),
      { wrapper }
    );

    act(() => {
      markdownResult.current.refetch();
    });

    await waitFor(() => {
      expect(markdownResult.current.isSuccess).toBe(true);
    });

    expect(markdownResult.current.data).toContain('# Annotations');

    // Step 4: Export to JSON
    const { result: jsonResult } = renderHook(
      () => useExportAnnotations({ format: 'json', resourceId: 'resource-1' }),
      { wrapper }
    );

    act(() => {
      jsonResult.current.refetch();
    });

    await waitFor(() => {
      expect(jsonResult.current.isSuccess).toBe(true);
    });

    expect(jsonResult.current.data).toHaveProperty('annotations');
    expect(jsonResult.current.data?.total_count).toBe(1);
  });

  it('should handle empty search results', async () => {
    /**
     * Requirements: 10.1
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/annotations/search/fulltext', () => HttpResponse.json([]))
    );

    const { result } = renderHook(
      () => useSearchAnnotations({ query: 'nonexistent', searchType: 'fulltext' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([]);
  });

  it('should handle export errors', async () => {
    /**
     * Requirements: 10.1, 10.4
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/annotations/export/markdown', () => {
        return HttpResponse.json({ detail: 'Export failed' }, { status: 500 });
      })
    );

    const { result } = renderHook(
      () => useExportAnnotations({ format: 'markdown', resourceId: 'resource-1' }),
      { wrapper }
    );

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});

// ============================================================================
// Workflow 4: Multi-Step Error Recovery
// ============================================================================

describe('Multi-Step Error Recovery Workflow', () => {
  it('should recover from multiple sequential errors', async () => {
    /**
     * Requirements: 10.4
     */

    const wrapper = createWrapper();

    let userAttempts = 0;
    server.use(
      http.get('*/api/auth/me', () => {
        userAttempts++;
        if (userAttempts === 1) {
          return HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 });
        }
        return HttpResponse.json(mockUser);
      })
    );

    const { result: userResult } = renderHook(() => useCurrentUser(), { wrapper });

    await waitFor(() => {
      expect(userResult.current.isError).toBe(true);
    });

    act(() => {
      userResult.current.refetch();
    });

    await waitFor(() => {
      expect(userResult.current.isSuccess).toBe(true);
    });

    expect(userResult.current.data).toEqual(mockUser);
  });
});
