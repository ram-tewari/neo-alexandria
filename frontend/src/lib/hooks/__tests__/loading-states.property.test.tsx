/**
 * Property-Based Tests for Loading State Visibility
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 12.4 - Property test for loading states
 * Property 7: Loading State Visibility
 * Validates: Requirements 8.1
 * 
 * This test verifies that for any API request in progress, the UI should
 * display a loading indicator until the request completes or fails.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createElement, type ReactNode } from 'react';
import fc from 'fast-check';
import { editorApi } from '@/lib/api/editor';
import { workbenchApi } from '@/lib/api/workbench';
import {
  useResource,
  useChunks,
  useAnnotations,
} from '../useEditorData';
import {
  useCurrentUser,
  useResources,
  useSystemHealth,
} from '../useWorkbenchData';
import type {
  Resource,
  SemanticChunk,
  Annotation,
  User,
  HealthStatus,
} from '@/types/api';

// ============================================================================
// Test Setup
// ============================================================================

// Mock the APIs
vi.mock('@/lib/api/editor', () => ({
  editorApi: {
    getResource: vi.fn(),
    getChunks: vi.fn(),
    getAnnotations: vi.fn(),
  },
  editorQueryKeys: {
    resource: {
      detail: (resourceId: string) => ['editor', 'resources', resourceId],
    },
    chunks: {
      byResource: (resourceId: string) => ['editor', 'chunks', 'list', resourceId],
    },
    annotations: {
      byResource: (resourceId: string) => ['editor', 'annotations', 'list', resourceId],
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
  },
}));

vi.mock('@/lib/api/workbench', () => ({
  workbenchApi: {
    getCurrentUser: vi.fn(),
    getResources: vi.fn(),
    getSystemHealth: vi.fn(),
  },
  workbenchQueryKeys: {
    user: {
      current: () => ['workbench', 'user', 'current'],
    },
    resources: {
      list: (params?: any) => ['workbench', 'resources', 'list', params],
    },
    health: {
      system: () => ['workbench', 'health', 'system'],
    },
  },
  workbenchCacheConfig: {
    user: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    },
    resources: {
      staleTime: 2 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    },
    health: {
      staleTime: 30 * 1000,
      cacheTime: 2 * 60 * 1000,
      refetchInterval: 30 * 1000,
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
    },
  });

  return ({ children }: { children: ReactNode }) =>
    createElement(QueryClientProvider, { client: queryClient }, children);
}

// ============================================================================
// Arbitraries (Generators for Property-Based Testing)
// ============================================================================

const resourceIdArbitrary = fc.stringMatching(/^resource-[a-z0-9]{8}$/);

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
  id: fc.stringMatching(/^annotation-[a-z0-9]{8}$/),
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

const userArbitrary = fc.record({
  id: fc.string({ minLength: 1 }),
  username: fc.string({ minLength: 1 }),
  email: fc.emailAddress(),
  tier: fc.constantFrom('free', 'premium', 'admin'),
  is_active: fc.boolean(),
}) as fc.Arbitrary<User>;

const healthStatusArbitrary = fc.record({
  status: fc.constantFrom('healthy', 'degraded', 'unhealthy'),
  message: fc.string({ minLength: 1 }),
  timestamp: fc.constant(new Date().toISOString()),
  components: fc.record({
    database: fc.record({
      status: fc.constantFrom('healthy', 'degraded', 'unhealthy'),
    }),
    cache: fc.record({
      status: fc.constantFrom('healthy', 'degraded', 'unhealthy'),
    }),
    event_bus: fc.record({
      status: fc.constantFrom('healthy', 'degraded', 'unhealthy'),
    }),
  }),
  modules: fc.dictionary(fc.string(), fc.constantFrom('healthy', 'degraded', 'unhealthy')),
}) as fc.Arbitrary<HealthStatus>;

// ============================================================================
// Property Tests
// ============================================================================

describe('Property 7: Loading State Visibility', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Property: For any resource fetch, the loading state should be true
   * while the request is in progress and false after completion.
   */
  it('should show loading state during resource fetch', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        resourceArbitrary,
        fc.nat({ min: 10, max: 100 }),
        async (resourceId, resource, delayMs) => {
          // Feature: phase2.5-backend-api-integration, Property 7: Loading State Visibility

          // Setup: Mock API with delay
          const resourceWithCorrectId = { ...resource, id: resourceId };
          vi.mocked(editorApi.getResource).mockImplementation(
            () =>
              new Promise((resolve) => {
                setTimeout(() => resolve(resourceWithCorrectId), delayMs);
              })
          );

          const wrapper = createWrapper();

          // Execute: Start fetching resource
          const { result } = renderHook(() => useResource(resourceId), { wrapper });

          // Verify: Loading state is true initially
          expect(result.current.isLoading).toBe(true);
          expect(result.current.data).toBeUndefined();
          expect(result.current.isSuccess).toBe(false);

          // Wait for request to complete
          await waitFor(
            () => {
              expect(result.current.isSuccess).toBe(true);
            },
            { timeout: delayMs + 1000 }
          );

          // Verify: Loading state is false after completion
          expect(result.current.isLoading).toBe(false);
          expect(result.current.data).toEqual(resourceWithCorrectId);
        }
      ),
      {
        numRuns: 20,
        timeout: 5000,
      }
    );
  }, 30000);

  /**
   * Property: For any chunks fetch, the loading state should be true
   * while the request is in progress and false after completion.
   */
  it('should show loading state during chunks fetch', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        fc.array(chunkArbitrary, { minLength: 1, maxLength: 5 }),
        fc.nat({ min: 10, max: 100 }),
        async (resourceId, chunks, delayMs) => {
          // Feature: phase2.5-backend-api-integration, Property 7: Loading State Visibility

          const chunksWithCorrectResourceId = chunks.map((chunk) => ({
            ...chunk,
            resource_id: resourceId,
          }));

          vi.mocked(editorApi.getChunks).mockImplementation(
            () =>
              new Promise((resolve) => {
                setTimeout(() => resolve(chunksWithCorrectResourceId), delayMs);
              })
          );

          const wrapper = createWrapper();

          // Execute: Start fetching chunks
          const { result } = renderHook(() => useChunks(resourceId), { wrapper });

          // Verify: Loading state is true initially
          expect(result.current.isLoading).toBe(true);
          expect(result.current.data).toBeUndefined();

          // Wait for request to complete
          await waitFor(
            () => {
              expect(result.current.isSuccess).toBe(true);
            },
            { timeout: delayMs + 1000 }
          );

          // Verify: Loading state is false after completion
          expect(result.current.isLoading).toBe(false);
          expect(result.current.data).toEqual(chunksWithCorrectResourceId);
        }
      ),
      {
        numRuns: 20,
        timeout: 5000,
      }
    );
  }, 30000);

  /**
   * Property: For any annotations fetch, the loading state should be true
   * while the request is in progress and false after completion.
   */
  it('should show loading state during annotations fetch', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        fc.array(annotationArbitrary, { minLength: 0, maxLength: 5 }),
        fc.nat({ min: 10, max: 100 }),
        async (resourceId, annotations, delayMs) => {
          // Feature: phase2.5-backend-api-integration, Property 7: Loading State Visibility

          const annotationsWithCorrectResourceId = annotations.map((ann) => ({
            ...ann,
            resource_id: resourceId,
          }));

          vi.mocked(editorApi.getAnnotations).mockImplementation(
            () =>
              new Promise((resolve) => {
                setTimeout(() => resolve(annotationsWithCorrectResourceId), delayMs);
              })
          );

          const wrapper = createWrapper();

          // Execute: Start fetching annotations
          const { result } = renderHook(() => useAnnotations(resourceId), { wrapper });

          // Verify: Loading state is true initially
          expect(result.current.isLoading).toBe(true);
          expect(result.current.data).toBeUndefined();

          // Wait for request to complete
          await waitFor(
            () => {
              expect(result.current.isSuccess).toBe(true);
            },
            { timeout: delayMs + 1000 }
          );

          // Verify: Loading state is false after completion
          expect(result.current.isLoading).toBe(false);
          expect(result.current.data).toEqual(annotationsWithCorrectResourceId);
        }
      ),
      {
        numRuns: 20,
        timeout: 5000,
      }
    );
  }, 30000);

  /**
   * Property: For any user fetch, the loading state should be true
   * while the request is in progress and false after completion.
   */
  it('should show loading state during user fetch', async () => {
    await fc.assert(
      fc.asyncProperty(
        userArbitrary,
        fc.nat({ min: 10, max: 100 }),
        async (user, delayMs) => {
          // Feature: phase2.5-backend-api-integration, Property 7: Loading State Visibility

          vi.mocked(workbenchApi.getCurrentUser).mockImplementation(
            () =>
              new Promise((resolve) => {
                setTimeout(() => resolve(user), delayMs);
              })
          );

          const wrapper = createWrapper();

          // Execute: Start fetching user
          const { result } = renderHook(() => useCurrentUser(), { wrapper });

          // Verify: Loading state is true initially
          expect(result.current.isLoading).toBe(true);
          expect(result.current.data).toBeUndefined();

          // Wait for request to complete
          await waitFor(
            () => {
              expect(result.current.isSuccess).toBe(true);
            },
            { timeout: delayMs + 1000 }
          );

          // Verify: Loading state is false after completion
          expect(result.current.isLoading).toBe(false);
          expect(result.current.data).toEqual(user);
        }
      ),
      {
        numRuns: 20,
        timeout: 5000,
      }
    );
  }, 30000);

  /**
   * Property: For any resources list fetch, the loading state should be true
   * while the request is in progress and false after completion.
   */
  it('should show loading state during resources list fetch', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(resourceArbitrary, { minLength: 0, maxLength: 10 }),
        fc.nat({ min: 10, max: 100 }),
        async (resources, delayMs) => {
          // Feature: phase2.5-backend-api-integration, Property 7: Loading State Visibility

          vi.mocked(workbenchApi.getResources).mockImplementation(
            () =>
              new Promise((resolve) => {
                setTimeout(() => resolve(resources), delayMs);
              })
          );

          const wrapper = createWrapper();

          // Execute: Start fetching resources
          const { result } = renderHook(() => useResources(), { wrapper });

          // Verify: Loading state is true initially
          expect(result.current.isLoading).toBe(true);
          expect(result.current.data).toBeUndefined();

          // Wait for request to complete
          await waitFor(
            () => {
              expect(result.current.isSuccess).toBe(true);
            },
            { timeout: delayMs + 1000 }
          );

          // Verify: Loading state is false after completion
          expect(result.current.isLoading).toBe(false);
          expect(result.current.data).toEqual(resources);
        }
      ),
      {
        numRuns: 20,
        timeout: 5000,
      }
    );
  }, 30000);

  /**
   * Property: For any health status fetch, the loading state should be true
   * while the request is in progress and false after completion.
   */
  it('should show loading state during health status fetch', async () => {
    await fc.assert(
      fc.asyncProperty(
        healthStatusArbitrary,
        fc.nat({ min: 10, max: 100 }),
        async (healthStatus, delayMs) => {
          // Feature: phase2.5-backend-api-integration, Property 7: Loading State Visibility

          vi.mocked(workbenchApi.getSystemHealth).mockImplementation(
            () =>
              new Promise((resolve) => {
                setTimeout(() => resolve(healthStatus), delayMs);
              })
          );

          const wrapper = createWrapper();

          // Execute: Start fetching health status
          const { result } = renderHook(() => useSystemHealth(), { wrapper });

          // Verify: Loading state is true initially
          expect(result.current.isLoading).toBe(true);
          expect(result.current.data).toBeUndefined();

          // Wait for request to complete
          await waitFor(
            () => {
              expect(result.current.isSuccess).toBe(true);
            },
            { timeout: delayMs + 1000 }
          );

          // Verify: Loading state is false after completion
          expect(result.current.isLoading).toBe(false);
          expect(result.current.data).toEqual(healthStatus);
        }
      ),
      {
        numRuns: 20,
        timeout: 5000,
      }
    );
  }, 30000);

  /**
   * Property: For any failed request, the loading state should be true
   * during the request and false after the error occurs.
   */
  it('should show loading state during failed requests', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.nat({ min: 10, max: 100 }),
        async (resourceId, errorMessage, delayMs) => {
          // Feature: phase2.5-backend-api-integration, Property 7: Loading State Visibility

          vi.mocked(editorApi.getResource).mockImplementation(
            () =>
              new Promise((_, reject) => {
                setTimeout(() => reject(new Error(errorMessage)), delayMs);
              })
          );

          const wrapper = createWrapper();

          // Execute: Start fetching resource (will fail)
          const { result } = renderHook(() => useResource(resourceId), { wrapper });

          // Verify: Loading state is true initially
          expect(result.current.isLoading).toBe(true);
          expect(result.current.data).toBeUndefined();
          expect(result.current.isError).toBe(false);

          // Wait for request to fail
          await waitFor(
            () => {
              expect(result.current.isError).toBe(true);
            },
            { timeout: delayMs + 1000 }
          );

          // Verify: Loading state is false after error
          expect(result.current.isLoading).toBe(false);
          expect(result.current.error).toBeDefined();
          expect(result.current.data).toBeUndefined();
        }
      ),
      {
        numRuns: 20,
        timeout: 5000,
      }
    );
  }, 30000);

  /**
   * Property: For any request, the loading state should never be true
   * at the same time as success or error states.
   */
  it('should never have loading state true with success or error states', async () => {
    await fc.assert(
      fc.asyncProperty(
        resourceIdArbitrary,
        fc.oneof(
          resourceArbitrary,
          fc.constant(new Error('Test error'))
        ),
        fc.nat({ min: 10, max: 100 }),
        async (resourceId, result, delayMs) => {
          // Feature: phase2.5-backend-api-integration, Property 7: Loading State Visibility

          if (result instanceof Error) {
            vi.mocked(editorApi.getResource).mockImplementation(
              () =>
                new Promise((_, reject) => {
                  setTimeout(() => reject(result), delayMs);
                })
            );
          } else {
            const resourceWithCorrectId = { ...result, id: resourceId };
            vi.mocked(editorApi.getResource).mockImplementation(
              () =>
                new Promise((resolve) => {
                  setTimeout(() => resolve(resourceWithCorrectId), delayMs);
                })
            );
          }

          const wrapper = createWrapper();

          // Execute: Start fetching resource
          const { result: hookResult } = renderHook(() => useResource(resourceId), { wrapper });

          // Verify: Loading state is true initially
          expect(hookResult.current.isLoading).toBe(true);

          // Wait for request to complete or fail
          await waitFor(
            () => {
              expect(hookResult.current.isLoading).toBe(false);
            },
            { timeout: delayMs + 1000 }
          );

          // Property: Loading should never be true when success or error is true
          if (hookResult.current.isSuccess) {
            expect(hookResult.current.isLoading).toBe(false);
            expect(hookResult.current.isError).toBe(false);
          }
          if (hookResult.current.isError) {
            expect(hookResult.current.isLoading).toBe(false);
            expect(hookResult.current.isSuccess).toBe(false);
          }
        }
      ),
      {
        numRuns: 20,
        timeout: 5000,
      }
    );
  }, 30000);
});
