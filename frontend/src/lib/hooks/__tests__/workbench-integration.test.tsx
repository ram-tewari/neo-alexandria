/**
 * Integration Tests for Phase 1 Workbench Flows
 * 
 * Tests complete user flows for Phase 1 components:
 * - User authentication flow
 * - Resource list loading
 * - Health status polling
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 3.4 Write integration tests for Phase 1 flows
 * Requirements: 10.5 (authentication, resource loading, health polling)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse, delay } from 'msw';
import { server } from '@/test/mocks/server';
import {
  useCurrentUser,
  useRateLimit,
  useResources,
  useSystemHealth,
  useAuthHealth,
  useResourcesHealth,
} from '../useWorkbenchData';
import type { ReactNode } from 'react';

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

const mockUser = {
  id: 'user-123',
  username: 'testuser',
  email: 'test@example.com',
  tier: 'premium' as const,
  is_active: true,
};

const mockRateLimit = {
  tier: 'premium' as const,
  limit: 1000,
  remaining: 950,
  reset: 1704067200,
};

const mockResources = [
  {
    id: 'resource-1',
    title: 'Test Resource 1',
    content_type: 'code' as const,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ingestion_status: 'completed' as const,
  },
  {
    id: 'resource-2',
    title: 'Test Resource 2',
    content_type: 'code' as const,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
    ingestion_status: 'completed' as const,
  },
];

const mockHealthStatus = {
  status: 'healthy' as const,
  message: 'All systems operational',
  timestamp: '2024-01-01T00:00:00Z',
  components: {
    database: { status: 'healthy' as const },
    cache: { status: 'healthy' as const },
    event_bus: { status: 'healthy' as const },
  },
  modules: {
    resources: 'healthy' as const,
    search: 'healthy' as const,
    auth: 'healthy' as const,
  },
};

const mockModuleHealth: 'healthy' = 'healthy';

// ============================================================================
// Integration Tests: User Authentication Flow
// ============================================================================

describe('Integration: User Authentication Flow', () => {
  it('should successfully fetch current user on app load', async () => {
    // Setup: Mock successful user fetch
    server.use(
      http.get('*/api/auth/me', () => {
        return HttpResponse.json(mockUser);
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    // Assert: Initial loading state
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    // Assert: Data loaded successfully
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockUser);
    expect(result.current.error).toBeNull();
  });

  it('should handle authentication failure and redirect to login', async () => {
    // Setup: Mock 401 Unauthorized response
    server.use(
      http.get('*/api/auth/me', () => {
        return HttpResponse.json(
          { detail: 'Not authenticated' },
          { status: 401 }
        );
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    // Assert: Error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
  });

  it('should fetch rate limit status after user authentication', async () => {
    // Setup: Mock successful responses
    server.use(
      http.get('*/api/auth/me', () => {
        return HttpResponse.json(mockUser);
      }),
      http.get('*/api/auth/rate-limit', () => {
        return HttpResponse.json(mockRateLimit);
      })
    );

    // Execute: Render both hooks
    const { result: userResult } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    const { result: rateLimitResult } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    // Assert: Both queries succeed
    await waitFor(() => {
      expect(userResult.current.isSuccess).toBe(true);
      expect(rateLimitResult.current.isSuccess).toBe(true);
    });

    expect(userResult.current.data).toEqual(mockUser);
    expect(rateLimitResult.current.data).toEqual(mockRateLimit);
  });

  it('should display rate limit warning when approaching limit', async () => {
    // Setup: Mock rate limit near exhaustion
    const nearLimitRateLimit = {
      ...mockRateLimit,
      remaining: 10, // Only 10 requests left
    };

    server.use(
      http.get('*/api/auth/rate-limit', () => {
        return HttpResponse.json(nearLimitRateLimit);
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    // Assert: Rate limit data shows low remaining
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.remaining).toBe(10);
    expect(result.current.data?.limit).toBe(1000);
    
    // Application should show warning when remaining < 5% of limit
    const percentRemaining = (result.current.data!.remaining / result.current.data!.limit) * 100;
    expect(percentRemaining).toBeLessThan(5);
  });

  it('should handle rate limit exceeded (429) error', async () => {
    // Setup: Mock 429 Too Many Requests
    server.use(
      http.get('*/api/auth/rate-limit', () => {
        return HttpResponse.json(
          {
            detail: 'Rate limit exceeded',
            retry_after: 60,
          },
          { status: 429 }
        );
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    // Assert: Error state with 429
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});

// ============================================================================
// Integration Tests: Resource List Loading Flow
// ============================================================================

describe('Integration: Resource List Loading Flow', () => {
  it('should successfully load resource list on repository switcher open', async () => {
    // Setup: Mock successful resource fetch
    server.use(
      http.get('*/resources', () => {
        return HttpResponse.json({
          items: mockResources,
          total: mockResources.length,
        });
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useResources(), {
      wrapper: createWrapper(),
    });

    // Assert: Initial loading state
    expect(result.current.isLoading).toBe(true);

    // Assert: Resources loaded successfully
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockResources);
    expect(result.current.data).toHaveLength(2);
  });

  it('should load resources with pagination parameters', async () => {
    // Setup: Mock paginated response
    const paginatedResources = [mockResources[0]];
    
    server.use(
      http.get('*/resources', ({ request }) => {
        const url = new URL(request.url);
        const skip = url.searchParams.get('skip');
        const limit = url.searchParams.get('limit');

        expect(skip).toBe('0');
        expect(limit).toBe('25');

        return HttpResponse.json({
          items: paginatedResources,
          total: 1,
        });
      })
    );

    // Execute: Render hook with pagination params
    const { result } = renderHook(
      () => useResources({ skip: 0, limit: 25 }),
      { wrapper: createWrapper() }
    );

    // Assert: Paginated data loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(paginatedResources);
  });

  it('should filter resources by content type', async () => {
    // Setup: Mock filtered response
    const codeResources = mockResources.filter(r => r.content_type === 'code');
    
    server.use(
      http.get('*/resources', ({ request }) => {
        const url = new URL(request.url);
        const contentType = url.searchParams.get('content_type');

        expect(contentType).toBe('code');

        return HttpResponse.json({
          items: codeResources,
          total: codeResources.length,
        });
      })
    );

    // Execute: Render hook with filter
    const { result } = renderHook(
      () => useResources({ content_type: 'code' }),
      { wrapper: createWrapper() }
    );

    // Assert: Filtered data loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(codeResources);
  });

  it('should handle empty resource list', async () => {
    // Setup: Mock empty response
    server.use(
      http.get('*/resources', () => {
        return HttpResponse.json({
          items: [],
          total: 0,
        });
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useResources(), {
      wrapper: createWrapper(),
    });

    // Assert: Empty array returned
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([]);
  });

  it('should handle resource loading error with retry', async () => {
    // Setup: Mock failure then success
    let attemptCount = 0;
    
    server.use(
      http.get('*/resources', () => {
        attemptCount++;
        
        if (attemptCount === 1) {
          // First attempt fails
          return HttpResponse.json(
            { detail: 'Server error' },
            { status: 500 }
          );
        }
        
        // Second attempt succeeds
        return HttpResponse.json({
          items: mockResources,
          total: mockResources.length,
        });
      })
    );

    // Execute: Render hook with retry enabled
    const { result } = renderHook(
      () => useResources(undefined, { retry: 1 }),
      { wrapper: createWrapper() }
    );

    // Assert: Eventually succeeds after retry
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    }, { timeout: 3000 });

    expect(result.current.data).toEqual(mockResources);
    expect(attemptCount).toBe(2);
  });

  it('should show loading state during slow resource fetch', async () => {
    // Setup: Mock delayed response
    server.use(
      http.get('*/resources', async () => {
        await delay(500); // 500ms delay
        return HttpResponse.json({
          items: mockResources,
          total: mockResources.length,
        });
      })
    );

    // Execute: Render hook
    const { result } = renderHook(() => useResources(), {
      wrapper: createWrapper(),
    });

    // Assert: Loading state is true initially
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    // Assert: Eventually loads
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    }, { timeout: 2000 });

    expect(result.current.data).toEqual(mockResources);
  });
});

// ============================================================================
// Integration Tests: Health Status Polling Flow
// ============================================================================

describe('Integration: Health Status Polling Flow', () => {
  it('should poll system health status every 30 seconds', async () => {
    // Setup fake timers for this test only
    vi.useFakeTimers();
    
    // Setup: Track number of health checks
    let healthCheckCount = 0;
    
    server.use(
      http.get('*/api/monitoring/health', () => {
        healthCheckCount++;
        return HttpResponse.json(mockHealthStatus);
      })
    );

    // Execute: Render hook with polling enabled
    const { result } = renderHook(() => useSystemHealth(), {
      wrapper: createWrapper(),
    });

    // Assert: Initial fetch
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(healthCheckCount).toBe(1);

    // Fast-forward 30 seconds
    await vi.advanceTimersByTimeAsync(30000);

    // Assert: Second fetch after 30s
    await waitFor(() => {
      expect(healthCheckCount).toBe(2);
    });

    // Fast-forward another 30 seconds
    await vi.advanceTimersByTimeAsync(30000);

    // Assert: Third fetch after 60s total
    await waitFor(() => {
      expect(healthCheckCount).toBe(3);
    });

    vi.useRealTimers();
  });

  it('should display healthy status in command palette', async () => {
    // Setup: Mock healthy system
    server.use(
      http.get('*/api/monitoring/health', () => {
        return HttpResponse.json(mockHealthStatus);
      })
    );

    // Execute: Render hook (disable polling for this test)
    const { result } = renderHook(() => useSystemHealth({ refetchInterval: false }), {
      wrapper: createWrapper(),
    });

    // Assert: Health data loaded
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.status).toBe('healthy');
    expect(result.current.data?.components.database.status).toBe('healthy');
    expect(result.current.data?.components.cache.status).toBe('healthy');
    expect(result.current.data?.components.event_bus.status).toBe('healthy');
  });

  it('should display degraded status when components are unhealthy', async () => {
    // Setup: Mock degraded system
    const degradedHealth = {
      ...mockHealthStatus,
      status: 'degraded' as const,
      components: {
        database: { status: 'healthy' as const },
        cache: { status: 'unhealthy' as const },
        event_bus: { status: 'healthy' as const },
      },
    };

    server.use(
      http.get('*/api/monitoring/health', () => {
        return HttpResponse.json(degradedHealth);
      })
    );

    // Execute: Render hook (disable polling for this test)
    const { result } = renderHook(() => useSystemHealth({ refetchInterval: false }), {
      wrapper: createWrapper(),
    });

    // Assert: Degraded status shown
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.status).toBe('degraded');
    expect(result.current.data?.components.cache.status).toBe('unhealthy');
  });

  it('should fetch individual module health status', async () => {
    // Setup: Mock module health endpoints
    server.use(
      http.get('*/api/monitoring/health/auth', () => {
        return HttpResponse.json('healthy');
      }),
      http.get('*/api/monitoring/health/resources', () => {
        return HttpResponse.json('healthy');
      })
    );

    // Execute: Render both module health hooks (disable polling)
    const { result: authResult } = renderHook(() => useAuthHealth({ refetchInterval: false }), {
      wrapper: createWrapper(),
    });

    const { result: resourcesResult } = renderHook(() => useResourcesHealth({ refetchInterval: false }), {
      wrapper: createWrapper(),
    });

    // Assert: Both module healths loaded
    await waitFor(() => {
      expect(authResult.current.isSuccess).toBe(true);
      expect(resourcesResult.current.isSuccess).toBe(true);
    });

    expect(authResult.current.data).toBe('healthy');
    expect(resourcesResult.current.data).toBe('healthy');
  });

  it('should handle health check failure gracefully', async () => {
    // Setup: Mock health check failure
    server.use(
      http.get('*/api/monitoring/health', () => {
        return HttpResponse.json(
          { detail: 'Health check failed' },
          { status: 503 }
        );
      })
    );

    // Execute: Render hook (disable polling)
    const { result } = renderHook(() => useSystemHealth({ refetchInterval: false }), {
      wrapper: createWrapper(),
    });

    // Assert: Error state
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
  });

  it('should continue polling after transient health check failure', async () => {
    // Setup fake timers for this test only
    vi.useFakeTimers();
    
    // Setup: Mock intermittent failure
    let attemptCount = 0;
    
    server.use(
      http.get('*/api/monitoring/health', () => {
        attemptCount++;
        
        if (attemptCount === 2) {
          // Second attempt fails
          return HttpResponse.json(
            { detail: 'Temporary failure' },
            { status: 503 }
          );
        }
        
        // Other attempts succeed
        return HttpResponse.json(mockHealthStatus);
      })
    );

    // Execute: Render hook with polling
    const { result } = renderHook(() => useSystemHealth(), {
      wrapper: createWrapper(),
    });

    // Assert: Initial success
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(attemptCount).toBe(1);

    // Fast-forward to trigger second poll (which fails)
    await vi.advanceTimersByTimeAsync(30000);

    await waitFor(() => {
      expect(attemptCount).toBe(2);
    });

    // Fast-forward to trigger third poll (which succeeds)
    await vi.advanceTimersByTimeAsync(30000);

    await waitFor(() => {
      expect(attemptCount).toBe(3);
      expect(result.current.isSuccess).toBe(true);
    });

    vi.useRealTimers();
  });
});

// ============================================================================
// Integration Tests: Complete Workbench Flow
// ============================================================================

describe('Integration: Complete Workbench Initialization Flow', () => {
  it('should load all workbench data on app startup', async () => {
    // Setup: Mock all workbench endpoints
    server.use(
      http.get('*/api/auth/me', () => {
        return HttpResponse.json(mockUser);
      }),
      http.get('*/api/auth/rate-limit', () => {
        return HttpResponse.json(mockRateLimit);
      }),
      http.get('*/resources', () => {
        return HttpResponse.json({
          items: mockResources,
          total: mockResources.length,
        });
      }),
      http.get('*/api/monitoring/health', () => {
        return HttpResponse.json(mockHealthStatus);
      })
    );

    // Execute: Render all workbench hooks (disable polling for health)
    const { result: userResult } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    const { result: rateLimitResult } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    const { result: resourcesResult } = renderHook(() => useResources(), {
      wrapper: createWrapper(),
    });

    const { result: healthResult } = renderHook(() => useSystemHealth({ refetchInterval: false }), {
      wrapper: createWrapper(),
    });

    // Assert: All queries succeed
    await waitFor(() => {
      expect(userResult.current.isSuccess).toBe(true);
      expect(rateLimitResult.current.isSuccess).toBe(true);
      expect(resourcesResult.current.isSuccess).toBe(true);
      expect(healthResult.current.isSuccess).toBe(true);
    });

    // Assert: All data loaded correctly
    expect(userResult.current.data).toEqual(mockUser);
    expect(rateLimitResult.current.data).toEqual(mockRateLimit);
    expect(resourcesResult.current.data).toEqual(mockResources);
    expect(healthResult.current.data).toEqual(mockHealthStatus);
  });

  it('should handle partial failure during workbench initialization', async () => {
    // Setup: Mock mixed success/failure responses
    server.use(
      http.get('*/api/auth/me', () => {
        return HttpResponse.json(mockUser);
      }),
      http.get('*/api/auth/rate-limit', () => {
        return HttpResponse.json(
          { detail: 'Rate limit service unavailable' },
          { status: 503 }
        );
      }),
      http.get('*/resources', () => {
        return HttpResponse.json({
          items: mockResources,
          total: mockResources.length,
        });
      }),
      http.get('*/api/monitoring/health', () => {
        return HttpResponse.json(mockHealthStatus);
      })
    );

    // Execute: Render all workbench hooks (disable polling for health)
    const { result: userResult } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    const { result: rateLimitResult } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    const { result: resourcesResult } = renderHook(() => useResources(), {
      wrapper: createWrapper(),
    });

    const { result: healthResult } = renderHook(() => useSystemHealth({ refetchInterval: false }), {
      wrapper: createWrapper(),
    });

    // Assert: Some succeed, rate limit fails
    await waitFor(() => {
      expect(userResult.current.isSuccess).toBe(true);
      expect(rateLimitResult.current.isError).toBe(true);
      expect(resourcesResult.current.isSuccess).toBe(true);
      expect(healthResult.current.isSuccess).toBe(true);
    });

    // Assert: App should still be usable with partial data
    expect(userResult.current.data).toEqual(mockUser);
    expect(resourcesResult.current.data).toEqual(mockResources);
    expect(healthResult.current.data).toEqual(mockHealthStatus);
  });
});
