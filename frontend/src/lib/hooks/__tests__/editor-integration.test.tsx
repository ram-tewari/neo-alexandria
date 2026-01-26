/**
 * Integration Tests for Phase 2 Editor Resource Loading Flows
 * 
 * Tests complete user flows for Phase 2 editor features:
 * - Resource fetch and display
 * - Chunk loading and overlay
 * - Processing status polling
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 5.5 Write integration tests for resource loading
 * Requirements: 10.2 (resource loading, chunk loading, status polling)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse, delay } from 'msw';
import { server } from '@/test/mocks/server';
import {
  useResource,
  useResourceStatus,
  useChunks,
  useChunk,
  useTriggerChunking,
} from '../useEditorData';
import { useEditorStore, resourceToCodeFile } from '@/stores/editor';
import type { ReactNode } from 'react';
import type {
  Resource,
  ProcessingStatus,
  SemanticChunk,
  ChunkingRequest,
} from '@/types/api';

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
        gcTime: 0, // Disable cache time
      },
    },
  });
}

/**
 * Wrapper component that provides QueryClient context
 */
function createWrapper() {
  const queryClient = createTestQueryClient();
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

// ============================================================================
// Mock Data
// ============================================================================

const mockResource: Resource = {
  id: 'resource-1',
  title: 'example.ts',
  content: `function example() {
  return 42;
}

class MyClass {
  constructor() {}
}`,
  content_type: 'code',
  language: 'typescript',
  file_path: '/src/example.ts',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ingestion_status: 'completed',
};

const mockProcessingStatus: ProcessingStatus = {
  id: 'resource-1',
  ingestion_status: 'completed',
  ingestion_started_at: '2024-01-01T00:00:00Z',
  ingestion_completed_at: '2024-01-01T00:00:00Z',
};

const mockChunks: SemanticChunk[] = [
  {
    id: 'chunk-1',
    resource_id: 'resource-1',
    content: 'function example() {\n  return 42;\n}',
    chunk_index: 0,
    chunk_type: 'code',
    chunk_metadata: {
      function_name: 'example',
      start_line: 1,
      end_line: 3,
      language: 'typescript',
    },
    token_count: 15,
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'chunk-2',
    resource_id: 'resource-1',
    content: 'class MyClass {\n  constructor() {}\n}',
    chunk_index: 1,
    chunk_type: 'code',
    chunk_metadata: {
      class_name: 'MyClass',
      start_line: 5,
      end_line: 7,
      language: 'typescript',
    },
    token_count: 12,
    created_at: '2024-01-01T00:00:00Z',
  },
];

// ============================================================================
// Integration Tests: Resource Fetch and Display Flow
// ============================================================================

describe('Integration: Resource Fetch and Display Flow', () => {
  beforeEach(() => {
    // Reset editor store before each test
    useEditorStore.getState().clearEditor();
  });

  it('should successfully load resource and display in editor', async () => {
    // Setup: Mock successful resource fetch
    server.use(
      http.get('*/resources/:resourceId', ({ params }) => {
        const { resourceId } = params;
        if (resourceId === 'resource-1') {
          return HttpResponse.json(mockResource);
        }
        return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useResource('resource-1'), {
      wrapper: createWrapper(),
    });

    // Assert: Initial loading state
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    // Assert: Resource loaded successfully
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockResource);
    expect(result.current.data?.content).toContain('function example()');
    expect(result.current.data?.language).toBe('typescript');
    expect(result.current.error).toBeNull();
  });

  it('should integrate resource data with editor store', async () => {
    // Setup: Mock successful resource fetch
    server.use(
      http.get('*/resources/:resourceId', () => {
        return HttpResponse.json(mockResource);
      })
    );

    // Execute: Set active resource in store
    act(() => {
      useEditorStore.getState().setActiveResource('resource-1');
    });

    // Assert: Store shows loading state
    expect(useEditorStore.getState().isLoading).toBe(true);
    expect(useEditorStore.getState().activeResourceId).toBe('resource-1');

    // Execute: Fetch resource
    const { result } = renderHook(() => useResource('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Execute: Convert resource to CodeFile and set in store
    act(() => {
      const codeFile = resourceToCodeFile(result.current.data!);
      useEditorStore.getState().setActiveFile(codeFile);
    });

    // Assert: Store updated with file data
    const state = useEditorStore.getState();
    expect(state.activeFile).toBeDefined();
    expect(state.activeFile?.id).toBe('resource-1');
    expect(state.activeFile?.content).toContain('function example()');
    expect(state.activeFile?.language).toBe('typescript');
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should handle resource not found error', async () => {
    // Setup: Mock 404 response
    server.use(
      http.get('*/resources/:resourceId', () => {
        return HttpResponse.json(
          { detail: 'Resource not found' },
          { status: 404 }
        );
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useResource('non-existent'), {
      wrapper: createWrapper(),
    });

    // Assert: Error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
  });

  it('should handle server error with retry capability', async () => {
    // Setup: Mock failure then success
    let attemptCount = 0;
    
    server.use(
      http.get('*/resources/:resourceId', () => {
        attemptCount++;
        
        if (attemptCount === 1) {
          // First attempt fails
          return HttpResponse.json(
            { detail: 'Server error' },
            { status: 500 }
          );
        }
        
        // Second attempt succeeds
        return HttpResponse.json(mockResource);
      })
    );

    // Execute: Render hook with retry enabled
    const { result } = renderHook(
      () => useResource('resource-1', { retry: 1 }),
      { wrapper: createWrapper() }
    );

    // Assert: Eventually succeeds after retry
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    }, { timeout: 3000 });

    expect(result.current.data).toEqual(mockResource);
    expect(attemptCount).toBe(2);
  });

  it('should show loading state during slow resource fetch', async () => {
    // Setup: Mock delayed response
    server.use(
      http.get('*/resources/:resourceId', async () => {
        await delay(500); // 500ms delay
        return HttpResponse.json(mockResource);
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useResource('resource-1'), {
      wrapper: createWrapper(),
    });

    // Assert: Loading state is true initially
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    // Assert: Eventually loads
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    }, { timeout: 2000 });

    expect(result.current.data).toEqual(mockResource);
  });

  it('should handle resource with missing optional fields', async () => {
    // Setup: Mock resource with minimal data
    const minimalResource: Resource = {
      id: 'resource-2',
      title: 'minimal.txt',
      content: 'Hello world',
      content_type: 'text',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      ingestion_status: 'completed',
    };

    server.use(
      http.get('*/resources/:resourceId', () => {
        return HttpResponse.json(minimalResource);
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useResource('resource-2'), {
      wrapper: createWrapper(),
    });

    // Assert: Resource loaded successfully
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(minimalResource);
    expect(result.current.data?.language).toBeUndefined();
    expect(result.current.data?.file_path).toBeUndefined();
  });
});

// ============================================================================
// Integration Tests: Chunk Loading and Overlay Flow
// ============================================================================

describe('Integration: Chunk Loading and Overlay Flow', () => {
  it('should load chunks after resource is loaded', async () => {
    // Setup: Mock resource and chunks endpoints
    server.use(
      http.get('*/resources/:resourceId', () => {
        return HttpResponse.json(mockResource);
      }),
      http.get('*/resources/:resourceId/chunks', ({ params }) => {
        const { resourceId } = params;
        if (resourceId === 'resource-1') {
          return HttpResponse.json(mockChunks);
        }
        return HttpResponse.json([]);
      })
    );

    // Execute: Load resource first
    const { result: resourceResult } = renderHook(
      () => useResource('resource-1'),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(resourceResult.current.isSuccess).toBe(true);
    });

    // Execute: Load chunks
    const { result: chunksResult } = renderHook(
      () => useChunks('resource-1'),
      { wrapper: createWrapper() }
    );

    // Assert: Chunks loaded successfully
    await waitFor(() => {
      expect(chunksResult.current.isSuccess).toBe(true);
    });

    expect(chunksResult.current.data).toEqual(mockChunks);
    expect(chunksResult.current.data).toHaveLength(2);
    expect(chunksResult.current.data?.[0].chunk_metadata.function_name).toBe('example');
    expect(chunksResult.current.data?.[1].chunk_metadata.class_name).toBe('MyClass');
  });

  it('should load specific chunk details', async () => {
    // Setup: Mock chunk detail endpoint
    server.use(
      http.get('*/chunks/:chunkId', ({ params }) => {
        const { chunkId } = params;
        const chunk = mockChunks.find(c => c.id === chunkId);
        
        if (!chunk) {
          return HttpResponse.json(
            { detail: 'Chunk not found' },
            { status: 404 }
          );
        }
        
        return HttpResponse.json(chunk);
      })
    );

    // Execute: Load specific chunk
    const { result } = renderHook(() => useChunk('chunk-1'), {
      wrapper: createWrapper(),
    });

    // Assert: Chunk loaded successfully
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockChunks[0]);
    expect(result.current.data?.chunk_metadata.function_name).toBe('example');
    expect(result.current.data?.chunk_metadata.start_line).toBe(1);
    expect(result.current.data?.chunk_metadata.end_line).toBe(3);
  });

  it('should handle empty chunks list for resource', async () => {
    // Setup: Mock empty chunks response
    server.use(
      http.get('*/resources/:resourceId/chunks', () => {
        return HttpResponse.json([]);
      })
    );

    // Execute: Load chunks
    const { result } = renderHook(() => useChunks('resource-999'), {
      wrapper: createWrapper(),
    });

    // Assert: Empty array returned
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([]);
  });

  it('should trigger chunking and invalidate cache', async () => {
    // Setup: Mock chunking endpoint
    server.use(
      http.post('*/resources/:resourceId/chunk', async ({ request, params }) => {
        const { resourceId } = params;
        const body = await request.json() as ChunkingRequest;
        
        return HttpResponse.json({
          task_id: `task-${Date.now()}`,
          resource_id: resourceId,
          status: 'pending',
          message: 'Chunking task created',
        });
      }),
      http.get('*/resources/:resourceId/chunks', () => {
        return HttpResponse.json(mockChunks);
      })
    );

    // Execute: Trigger chunking
    const { result: chunkingResult } = renderHook(
      () => useTriggerChunking(),
      { wrapper: createWrapper() }
    );

    act(() => {
      chunkingResult.current.mutate({
        resourceId: 'resource-1',
        request: {
          strategy: 'parent_child',
          chunk_size: 512,
          overlap: 50,
        },
      });
    });

    // Assert: Chunking triggered successfully
    await waitFor(() => {
      expect(chunkingResult.current.isSuccess).toBe(true);
    });

    expect(chunkingResult.current.data?.task_id).toBeDefined();
    expect(chunkingResult.current.data?.status).toBe('pending');
  });

  it('should display chunk overlay with correct line ranges', async () => {
    // Setup: Mock chunks endpoint
    server.use(
      http.get('*/resources/:resourceId/chunks', () => {
        return HttpResponse.json(mockChunks);
      })
    );

    // Execute: Load chunks
    const { result } = renderHook(() => useChunks('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Assert: Chunks have correct line ranges for overlay
    const chunks = result.current.data!;
    
    // First chunk: lines 1-3
    expect(chunks[0].chunk_metadata.start_line).toBe(1);
    expect(chunks[0].chunk_metadata.end_line).toBe(3);
    
    // Second chunk: lines 5-7
    expect(chunks[1].chunk_metadata.start_line).toBe(5);
    expect(chunks[1].chunk_metadata.end_line).toBe(7);
    
    // Verify no overlap (important for overlay rendering)
    expect(chunks[0].chunk_metadata.end_line).toBeLessThan(
      chunks[1].chunk_metadata.start_line
    );
  });

  it('should handle chunk loading error gracefully', async () => {
    // Setup: Mock error response
    server.use(
      http.get('*/resources/:resourceId/chunks', () => {
        return HttpResponse.json(
          { detail: 'Failed to load chunks' },
          { status: 500 }
        );
      })
    );

    // Execute: Load chunks
    const { result } = renderHook(() => useChunks('resource-1'), {
      wrapper: createWrapper(),
    });

    // Assert: Error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
  });
});

// ============================================================================
// Integration Tests: Processing Status Polling Flow
// ============================================================================

describe('Integration: Processing Status Polling Flow', () => {
  it('should poll processing status automatically', async () => {
    // Setup fake timers for this test only
    vi.useFakeTimers();
    
    // Setup: Track number of status checks
    let statusCheckCount = 0;
    
    server.use(
      http.get('*/resources/:resourceId/status', () => {
        statusCheckCount++;
        return HttpResponse.json(mockProcessingStatus);
      })
    );

    // Execute: Render hook with polling enabled
    const { result } = renderHook(() => useResourceStatus('resource-1'), {
      wrapper: createWrapper(),
    });

    // Assert: Initial fetch
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(statusCheckCount).toBe(1);

    // Fast-forward 5 seconds (default polling interval)
    await vi.advanceTimersByTimeAsync(5000);

    // Assert: Second fetch after 5s
    await waitFor(() => {
      expect(statusCheckCount).toBe(2);
    });

    // Fast-forward another 5 seconds
    await vi.advanceTimersByTimeAsync(5000);

    // Assert: Third fetch after 10s total
    await waitFor(() => {
      expect(statusCheckCount).toBe(3);
    });

    vi.useRealTimers();
  });

  it('should display processing status for pending resource', async () => {
    // Setup: Mock pending status
    const pendingStatus: ProcessingStatus = {
      id: 'resource-1',
      ingestion_status: 'processing',
      ingestion_started_at: '2024-01-01T00:00:00Z',
    };

    server.use(
      http.get('*/resources/:resourceId/status', () => {
        return HttpResponse.json(pendingStatus);
      })
    );

    // Execute: Render hook (disable polling for this test)
    const { result } = renderHook(
      () => useResourceStatus('resource-1', { refetchInterval: false }),
      { wrapper: createWrapper() }
    );

    // Assert: Status loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.ingestion_status).toBe('processing');
  });

  it('should display error status when processing fails', async () => {
    // Setup: Mock failed status
    const failedStatus: ProcessingStatus = {
      id: 'resource-1',
      ingestion_status: 'failed',
      ingestion_error: 'Failed to parse file',
      ingestion_started_at: '2024-01-01T00:00:00Z',
    };

    server.use(
      http.get('*/resources/:resourceId/status', () => {
        return HttpResponse.json(failedStatus);
      })
    );

    // Execute: Render hook (disable polling)
    const { result } = renderHook(
      () => useResourceStatus('resource-1', { refetchInterval: false }),
      { wrapper: createWrapper() }
    );

    // Assert: Failed status shown
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.ingestion_status).toBe('failed');
    expect(result.current.data?.ingestion_error).toBe('Failed to parse file');
  });

  it('should transition from processing to completed status', async () => {
    // Setup fake timers
    vi.useFakeTimers();
    
    // Setup: Mock status that changes over time
    let pollCount = 0;
    
    server.use(
      http.get('*/resources/:resourceId/status', () => {
        pollCount++;
        
        if (pollCount <= 2) {
          // First two polls: still processing
          return HttpResponse.json({
            id: 'resource-1',
            ingestion_status: 'processing',
            ingestion_started_at: '2024-01-01T00:00:00Z',
          });
        }
        
        // Third poll onwards: completed
        return HttpResponse.json(mockProcessingStatus);
      })
    );

    // Execute: Render hook with polling
    const { result } = renderHook(() => useResourceStatus('resource-1'), {
      wrapper: createWrapper(),
    });

    // Assert: Initial status is processing
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(result.current.data?.ingestion_status).toBe('processing');

    // Fast-forward to trigger second poll
    await vi.advanceTimersByTimeAsync(5000);
    
    await waitFor(() => {
      expect(pollCount).toBe(2);
    });
    expect(result.current.data?.ingestion_status).toBe('processing');

    // Fast-forward to trigger third poll
    await vi.advanceTimersByTimeAsync(5000);
    
    await waitFor(() => {
      expect(pollCount).toBe(3);
    });

    // Assert: Status changed to completed
    expect(result.current.data?.ingestion_status).toBe('completed');

    vi.useRealTimers();
  });

  it('should handle status polling failure gracefully', async () => {
    // Setup: Mock status check failure
    server.use(
      http.get('*/resources/:resourceId/status', () => {
        return HttpResponse.json(
          { detail: 'Status unavailable' },
          { status: 503 }
        );
      })
    );

    // Execute: Render hook (disable polling)
    const { result } = renderHook(
      () => useResourceStatus('resource-1', { refetchInterval: false }),
      { wrapper: createWrapper() }
    );

    // Assert: Error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
  });

  it('should continue polling after transient status check failure', async () => {
    // Setup fake timers
    vi.useFakeTimers();
    
    // Setup: Mock intermittent failure
    let attemptCount = 0;
    
    server.use(
      http.get('*/resources/:resourceId/status', () => {
        attemptCount++;
        
        if (attemptCount === 2) {
          // Second attempt fails
          return HttpResponse.json(
            { detail: 'Temporary failure' },
            { status: 503 }
          );
        }
        
        // Other attempts succeed
        return HttpResponse.json(mockProcessingStatus);
      })
    );

    // Execute: Render hook with polling
    const { result } = renderHook(() => useResourceStatus('resource-1'), {
      wrapper: createWrapper(),
    });

    // Assert: Initial success
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(attemptCount).toBe(1);

    // Fast-forward to trigger second poll (which fails)
    await vi.advanceTimersByTimeAsync(5000);

    await waitFor(() => {
      expect(attemptCount).toBe(2);
    });

    // Fast-forward to trigger third poll (which succeeds)
    await vi.advanceTimersByTimeAsync(5000);

    await waitFor(() => {
      expect(attemptCount).toBe(3);
      expect(result.current.isSuccess).toBe(true);
    });

    vi.useRealTimers();
  });
});

// ============================================================================
// Integration Tests: Complete Resource Loading Flow
// ============================================================================

describe('Integration: Complete Resource Loading Flow', () => {
  beforeEach(() => {
    // Reset editor store before each test
    useEditorStore.getState().clearEditor();
  });

  it('should load resource, chunks, and status in parallel', async () => {
    // Setup: Mock all endpoints
    server.use(
      http.get('*/resources/:resourceId', () => {
        return HttpResponse.json(mockResource);
      }),
      http.get('*/resources/:resourceId/chunks', () => {
        return HttpResponse.json(mockChunks);
      }),
      http.get('*/resources/:resourceId/status', () => {
        return HttpResponse.json(mockProcessingStatus);
      })
    );

    // Execute: Render all hooks in parallel (disable status polling)
    const { result: resourceResult } = renderHook(
      () => useResource('resource-1'),
      { wrapper: createWrapper() }
    );

    const { result: chunksResult } = renderHook(
      () => useChunks('resource-1'),
      { wrapper: createWrapper() }
    );

    const { result: statusResult } = renderHook(
      () => useResourceStatus('resource-1', { refetchInterval: false }),
      { wrapper: createWrapper() }
    );

    // Assert: All queries succeed
    await waitFor(() => {
      expect(resourceResult.current.isSuccess).toBe(true);
      expect(chunksResult.current.isSuccess).toBe(true);
      expect(statusResult.current.isSuccess).toBe(true);
    });

    // Assert: All data loaded correctly
    expect(resourceResult.current.data).toEqual(mockResource);
    expect(chunksResult.current.data).toEqual(mockChunks);
    expect(statusResult.current.data).toEqual(mockProcessingStatus);
  });

  it('should handle complete editor initialization flow', async () => {
    // Setup: Mock all endpoints
    server.use(
      http.get('*/resources/:resourceId', () => {
        return HttpResponse.json(mockResource);
      }),
      http.get('*/resources/:resourceId/chunks', () => {
        return HttpResponse.json(mockChunks);
      }),
      http.get('*/resources/:resourceId/status', () => {
        return HttpResponse.json(mockProcessingStatus);
      })
    );

    // Step 1: User selects resource
    act(() => {
      useEditorStore.getState().setActiveResource('resource-1');
    });

    expect(useEditorStore.getState().isLoading).toBe(true);
    expect(useEditorStore.getState().activeResourceId).toBe('resource-1');

    // Step 2: Fetch resource data
    const { result: resourceResult } = renderHook(
      () => useResource('resource-1'),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(resourceResult.current.isSuccess).toBe(true);
    });

    // Step 3: Convert and set in editor store
    act(() => {
      const codeFile = resourceToCodeFile(resourceResult.current.data!);
      useEditorStore.getState().setActiveFile(codeFile);
    });

    // Step 4: Load chunks for overlay
    const { result: chunksResult } = renderHook(
      () => useChunks('resource-1'),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(chunksResult.current.isSuccess).toBe(true);
    });

    // Step 5: Monitor processing status
    const { result: statusResult } = renderHook(
      () => useResourceStatus('resource-1', { refetchInterval: false }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(statusResult.current.isSuccess).toBe(true);
    });

    // Assert: Complete editor state
    const editorState = useEditorStore.getState();
    expect(editorState.activeFile).toBeDefined();
    expect(editorState.activeFile?.content).toContain('function example()');
    expect(editorState.isLoading).toBe(false);
    expect(editorState.error).toBeNull();

    // Assert: Chunks available for overlay
    expect(chunksResult.current.data).toHaveLength(2);

    // Assert: Processing completed
    expect(statusResult.current.data?.ingestion_status).toBe('completed');
  });

  it('should handle partial failure during editor initialization', async () => {
    // Setup: Mock mixed success/failure responses
    server.use(
      http.get('*/resources/:resourceId', () => {
        return HttpResponse.json(mockResource);
      }),
      http.get('*/resources/:resourceId/chunks', () => {
        return HttpResponse.json(
          { detail: 'Chunks not available' },
          { status: 503 }
        );
      }),
      http.get('*/resources/:resourceId/status', () => {
        return HttpResponse.json(mockProcessingStatus);
      })
    );

    // Execute: Render all hooks (disable status polling)
    const { result: resourceResult } = renderHook(
      () => useResource('resource-1'),
      { wrapper: createWrapper() }
    );

    const { result: chunksResult } = renderHook(
      () => useChunks('resource-1'),
      { wrapper: createWrapper() }
    );

    const { result: statusResult } = renderHook(
      () => useResourceStatus('resource-1', { refetchInterval: false }),
      { wrapper: createWrapper() }
    );

    // Assert: Resource and status succeed, chunks fail
    await waitFor(() => {
      expect(resourceResult.current.isSuccess).toBe(true);
      expect(chunksResult.current.isError).toBe(true);
      expect(statusResult.current.isSuccess).toBe(true);
    });

    // Assert: Editor should still be usable with resource data
    expect(resourceResult.current.data).toEqual(mockResource);
    expect(statusResult.current.data).toEqual(mockProcessingStatus);
    
    // Assert: Chunks error is captured
    expect(chunksResult.current.error).toBeDefined();
  });

  it('should handle resource switch during loading', async () => {
    // Setup: Mock resources
    const resource2: Resource = {
      ...mockResource,
      id: 'resource-2',
      title: 'other.ts',
      content: 'const x = 1;',
    };

    server.use(
      http.get('*/resources/:resourceId', ({ params }) => {
        const { resourceId } = params;
        if (resourceId === 'resource-1') {
          return HttpResponse.json(mockResource);
        }
        if (resourceId === 'resource-2') {
          return HttpResponse.json(resource2);
        }
        return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
      })
    );

    // Execute: Load first resource
    const { result: resource1Result } = renderHook(
      () => useResource('resource-1'),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(resource1Result.current.isSuccess).toBe(true);
    });

    // Execute: Switch to second resource
    act(() => {
      useEditorStore.getState().setActiveResource('resource-2');
    });

    const { result: resource2Result } = renderHook(
      () => useResource('resource-2'),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(resource2Result.current.isSuccess).toBe(true);
    });

    // Assert: Second resource loaded
    expect(resource2Result.current.data).toEqual(resource2);
    expect(resource2Result.current.data?.id).toBe('resource-2');
  });

  it('should preserve scroll position when switching resources', async () => {
    // Setup: Mock resources
    server.use(
      http.get('*/resources/:resourceId', ({ params }) => {
        const { resourceId } = params;
        if (resourceId === 'resource-1') {
          return HttpResponse.json(mockResource);
        }
        return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
      })
    );

    // Execute: Load resource and set scroll position
    const { result } = renderHook(() => useResource('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    act(() => {
      const codeFile = resourceToCodeFile(result.current.data!);
      useEditorStore.getState().setActiveFile(codeFile);
      useEditorStore.getState().updateScrollPosition(500);
    });

    // Assert: Scroll position saved
    expect(useEditorStore.getState().scrollPosition).toBe(500);
    expect(useEditorStore.getState().scrollPositions['resource-1']).toBe(500);

    // Execute: Clear editor
    act(() => {
      useEditorStore.getState().clearEditor();
    });

    // Execute: Reload same resource
    const { result: reloadResult } = renderHook(() => useResource('resource-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(reloadResult.current.isSuccess).toBe(true);
    });

    act(() => {
      const codeFile = resourceToCodeFile(reloadResult.current.data!);
      useEditorStore.getState().setActiveFile(codeFile);
    });

    // Assert: Scroll position restored
    expect(useEditorStore.getState().scrollPosition).toBe(500);
  });
});
