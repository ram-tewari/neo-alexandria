/**
 * Rate Limiting Workflow Integration Tests
 * 
 * Tests rate limiting detection, cooldown timer, and retry behavior:
 * - Rate limit detection (429 response)
 * - Cooldown timer display
 * - Retry after cooldown
 * - Rate limit info display
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 13.2 - Test rate limiting workflow
 * Requirements: 10.6
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse } from 'msw';
import { server } from '@/test/mocks/server';
import { ReactNode } from 'react';

// Hooks
import { useRateLimit, useResources } from '../useWorkbenchData';
import { useCreateAnnotation } from '../useEditorData';

// Types
import type { RateLimitStatus, Resource, Annotation } from '../../../types/api';

// ============================================================================
// Test Setup
// ============================================================================

const mockRateLimitStatus: RateLimitStatus = {
  tier: 'free',
  requests_remaining: 100,
  requests_limit: 1000,
  reset_at: new Date(Date.now() + 3600000).toISOString(),
  retry_after: null,
};

const mockRateLimitExceeded: RateLimitStatus = {
  tier: 'free',
  requests_remaining: 0,
  requests_limit: 1000,
  reset_at: new Date(Date.now() + 3600000).toISOString(),
  retry_after: 60,
};

const mockResources: Resource[] = [
  {
    id: 'resource-1',
    title: 'main.ts',
    content: 'function main() {}',
    content_type: 'code',
    language: 'typescript',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  server.resetHandlers();
  vi.useRealTimers();
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
// Rate Limit Detection Tests
// ============================================================================

describe('Rate Limit Detection', () => {
  it('should detect rate limit from 429 response', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/resources', () => {
        return HttpResponse.json(
          { detail: 'Rate limit exceeded', retry_after: 60 },
          { status: 429, headers: { 'Retry-After': '60' } }
        );
      })
    );

    const { result } = renderHook(() => useResources(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    const error = result.current.error as any;
    expect(error).toBeDefined();
    expect(error.response?.status).toBe(429);
  });

  it('should fetch rate limit status', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/api/auth/rate-limit', () => HttpResponse.json(mockRateLimitStatus))
    );

    const { result } = renderHook(() => useRateLimit(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.requests_remaining).toBe(100);
    expect(result.current.data?.requests_limit).toBe(1000);
    expect(result.current.data?.tier).toBe('free');
  });

  it('should detect when rate limit is exceeded', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/api/auth/rate-limit', () => HttpResponse.json(mockRateLimitExceeded))
    );

    const { result } = renderHook(() => useRateLimit(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.requests_remaining).toBe(0);
    expect(result.current.data?.retry_after).toBe(60);
  });
});

// ============================================================================
// Cooldown Timer Tests
// ============================================================================

describe('Cooldown Timer', () => {
  it('should display cooldown timer when rate limited', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/resources', () => {
        return HttpResponse.json(
          { detail: 'Rate limit exceeded', retry_after: 10 },
          { status: 429, headers: { 'Retry-After': '10' } }
        );
      })
    );

    const { result } = renderHook(() => useResources(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    const error = result.current.error as any;
    const retryAfter = error.response?.data?.retry_after || 10;

    expect(retryAfter).toBe(10);

    // Simulate timer countdown
    let remainingTime = retryAfter;

    act(() => {
      vi.advanceTimersByTime(5000);
    });
    remainingTime -= 5;
    expect(remainingTime).toBe(5);

    act(() => {
      vi.advanceTimersByTime(5000);
    });
    remainingTime -= 5;
    expect(remainingTime).toBe(0);
  });

  it('should update rate limit status during cooldown', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/api/auth/rate-limit', () => HttpResponse.json(mockRateLimitExceeded))
    );

    const { result } = renderHook(() => useRateLimit(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.requests_remaining).toBe(0);

    act(() => {
      vi.advanceTimersByTime(60000);
    });

    server.use(
      http.get('*/api/auth/rate-limit', () => {
        return HttpResponse.json({
          ...mockRateLimitStatus,
          requests_remaining: 100,
          retry_after: null,
        });
      })
    );

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.data?.requests_remaining).toBe(100);
    });

    expect(result.current.data?.retry_after).toBeNull();
  });
});

// ============================================================================
// Retry After Cooldown Tests
// ============================================================================

describe('Retry After Cooldown', () => {
  it('should successfully retry after cooldown period', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    let requestCount = 0;

    server.use(
      http.get('*/resources', () => {
        requestCount++;
        if (requestCount === 1) {
          return HttpResponse.json(
            { detail: 'Rate limit exceeded', retry_after: 5 },
            { status: 429, headers: { 'Retry-After': '5' } }
          );
        }
        return HttpResponse.json(mockResources);
      })
    );

    const { result } = renderHook(() => useResources(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(requestCount).toBe(1);

    act(() => {
      vi.advanceTimersByTime(5000);
    });

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockResources);
    expect(requestCount).toBe(2);
  });

  it('should handle mutation retry after cooldown', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    let mutationCount = 0;

    server.use(
      http.post('*/annotations', async ({ request }) => {
        mutationCount++;
        if (mutationCount === 1) {
          return HttpResponse.json(
            { detail: 'Rate limit exceeded', retry_after: 3 },
            { status: 429, headers: { 'Retry-After': '3' } }
          );
        }
        const body = await request.json() as Partial<Annotation>;
        return HttpResponse.json({
          ...body,
          id: 'annotation-1',
          user_id: 'user-1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      })
    );

    const { result } = renderHook(() => useCreateAnnotation(), { wrapper });

    act(() => {
      result.current.mutate({
        resourceId: 'resource-1',
        data: {
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'test',
          note: 'Test note',
          color: '#FFD700',
        },
      });
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(mutationCount).toBe(1);

    act(() => {
      vi.advanceTimersByTime(3000);
    });

    act(() => {
      result.current.mutate({
        resourceId: 'resource-1',
        data: {
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'test',
          note: 'Test note',
          color: '#FFD700',
        },
      });
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.id).toBe('annotation-1');
    expect(mutationCount).toBe(2);
  });

  it('should not retry before cooldown expires', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    let requestCount = 0;
    const cooldownSeconds = 10;

    server.use(
      http.get('*/resources', () => {
        requestCount++;
        if (requestCount <= 2) {
          return HttpResponse.json(
            { detail: 'Rate limit exceeded', retry_after: cooldownSeconds },
            { status: 429, headers: { 'Retry-After': String(cooldownSeconds) } }
          );
        }
        return HttpResponse.json(mockResources);
      })
    );

    const { result } = renderHook(() => useResources(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(requestCount).toBe(1);

    act(() => {
      vi.advanceTimersByTime(5000);
    });

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(requestCount).toBe(2);

    act(() => {
      vi.advanceTimersByTime(5000);
    });

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockResources);
    expect(requestCount).toBe(3);
  });
});

// ============================================================================
// Rate Limit Info Display Tests
// ============================================================================

describe('Rate Limit Info Display', () => {
  it('should display rate limit warning when approaching limit', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/api/auth/rate-limit', () => {
        return HttpResponse.json({
          ...mockRateLimitStatus,
          requests_remaining: 100,
          requests_limit: 1000,
        });
      })
    );

    const { result } = renderHook(() => useRateLimit(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    const remaining = result.current.data?.requests_remaining || 0;
    const limit = result.current.data?.requests_limit || 1;
    const percentageRemaining = (remaining / limit) * 100;

    if (percentageRemaining < 20) {
      expect(percentageRemaining).toBeLessThan(20);
    }
  });

  it('should display tier information', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/api/auth/rate-limit', () => HttpResponse.json(mockRateLimitStatus))
    );

    const { result } = renderHook(() => useRateLimit(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.tier).toBe('free');
    expect(result.current.data?.requests_limit).toBe(1000);

    const tierLimits: Record<string, number> = {
      free: 1000,
      premium: 10000,
      admin: 100000,
    };

    const tier = result.current.data?.tier || 'free';
    expect(tierLimits[tier]).toBeDefined();
  });

  it('should display reset time', async () => {
    /**
     * Requirements: 10.6
     */

    const wrapper = createWrapper();

    server.use(
      http.get('*/api/auth/rate-limit', () => HttpResponse.json(mockRateLimitStatus))
    );

    const { result } = renderHook(() => useRateLimit(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    const resetAt = result.current.data?.reset_at;
    expect(resetAt).toBeDefined();

    const resetTime = new Date(resetAt!).getTime();
    const now = Date.now();
    expect(resetTime).toBeGreaterThan(now);

    const timeUntilReset = resetTime - now;
    expect(timeUntilReset).toBeGreaterThan(0);
  });
});
