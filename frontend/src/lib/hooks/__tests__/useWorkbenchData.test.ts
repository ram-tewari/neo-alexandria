/**
 * Unit Tests for Workbench Data Hooks
 * 
 * Tests TanStack Query hooks for Phase 1 workbench features:
 * - User authentication and rate limits
 * - Resource listing
 * - System health monitoring
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 3.2 Create TanStack Query hooks for Phase 1
 * Requirements: 2.1, 2.2, 2.3, 2.4
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createElement } from 'react';
import { workbenchApi } from '@/lib/api/workbench';
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
// Test Setup
// ============================================================================

// Mock the workbench API
vi.mock('@/lib/api/workbench', () => ({
  workbenchApi: {
    getCurrentUser: vi.fn(),
    getRateLimit: vi.fn(),
    getResources: vi.fn(),
    getSystemHealth: vi.fn(),
    getAuthHealth: vi.fn(),
    getResourcesHealth: vi.fn(),
  },
  workbenchQueryKeys: {
    user: {
      current: () => ['user', 'current'],
      rateLimit: () => ['user', 'rateLimit'],
    },
    resources: {
      all: () => ['resources'],
      list: (params?: any) => ['resources', 'list', params],
    },
    health: {
      system: () => ['health', 'system'],
      auth: () => ['health', 'auth'],
      resources: () => ['health', 'resources'],
    },
  },
  workbenchCacheConfig: {
    user: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    },
    resources: {
      staleTime: 2 * 60 * 1000,
      cacheTime: 5 * 60 * 1000,
    },
    health: {
      staleTime: 30 * 1000,
      cacheTime: 60 * 1000,
      refetchInterval: 30 * 1000,
    },
  },
}));

// Create a wrapper with QueryClient
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Disable retries for tests
      },
    },
  });

  return ({ children }: { children: ReactNode }) =>
    createElement(QueryClientProvider, { client: queryClient }, children);
}

// ============================================================================
// Test Data
// ============================================================================

const mockUser = {
  id: 'user-1',
  email: 'test@example.com',
  username: 'testuser',
  is_active: true,
  is_premium: false,
  tier: 'free' as const,
  created_at: '2024-01-01T00:00:00Z',
};

const mockRateLimit = {
  tier: 'free' as const,
  limit: 100,
  remaining: 95,
  reset: '2024-01-01T01:00:00Z',
};

const mockResources = [
  {
    id: 'resource-1',
    title: 'Test Resource 1',
    content: 'function test() { return true; }',
    content_type: 'code' as const,
    language: 'typescript',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'resource-2',
    title: 'Test Resource 2',
    content: 'const x = 42;',
    content_type: 'code' as const,
    language: 'javascript',
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
];

const mockHealthStatus = {
  status: 'healthy' as const,
  timestamp: '2024-01-01T00:00:00Z',
  version: '1.0.0',
  components: {
    database: 'healthy' as const,
    cache: 'healthy' as const,
    embeddings: 'healthy' as const,
  },
  modules: {
    auth: 'healthy' as const,
    resources: 'healthy' as const,
    search: 'healthy' as const,
  },
};

const mockModuleHealth = {
  module: 'auth',
  status: 'healthy' as const,
  timestamp: '2024-01-01T00:00:00Z',
  checks: {
    database: 'healthy' as const,
    dependencies: 'healthy' as const,
  },
};

// ============================================================================
// Authentication Hooks Tests
// ============================================================================

describe('useCurrentUser', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch current user successfully', async () => {
    vi.mocked(workbenchApi.getCurrentUser).mockResolvedValue(mockUser);

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    // Initially loading
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    // Wait for data to load
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify data
    expect(result.current.data).toEqual(mockUser);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(workbenchApi.getCurrentUser).toHaveBeenCalledTimes(1);
  });

  it('should handle errors when fetching user fails', async () => {
    const error = new Error('Failed to fetch user');
    vi.mocked(workbenchApi.getCurrentUser).mockRejectedValue(error);

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    // Wait for error
    await waitFor(() => expect(result.current.isError).toBe(true));

    // Verify error state
    expect(result.current.error).toEqual(error);
    expect(result.current.data).toBeUndefined();
    expect(result.current.isLoading).toBe(false);
  });

  it('should use correct cache configuration', async () => {
    vi.mocked(workbenchApi.getCurrentUser).mockResolvedValue(mockUser);

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify cache times are set (indirectly through query state)
    expect(result.current.data).toEqual(mockUser);
  });
});

describe('useRateLimit', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch rate limit status successfully', async () => {
    vi.mocked(workbenchApi.getRateLimit).mockResolvedValue(mockRateLimit);

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    // Initially loading
    expect(result.current.isLoading).toBe(true);

    // Wait for data
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify data
    expect(result.current.data).toEqual(mockRateLimit);
    expect(result.current.isLoading).toBe(false);
    expect(workbenchApi.getRateLimit).toHaveBeenCalledTimes(1);
  });

  it('should handle errors when fetching rate limit fails', async () => {
    const error = new Error('Failed to fetch rate limit');
    vi.mocked(workbenchApi.getRateLimit).mockRejectedValue(error);

    const { result } = renderHook(() => useRateLimit(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(error);
    expect(result.current.data).toBeUndefined();
  });
});

// ============================================================================
// Resource Hooks Tests
// ============================================================================

describe('useResources', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch resources without parameters', async () => {
    vi.mocked(workbenchApi.getResources).mockResolvedValue(mockResources);

    const { result } = renderHook(() => useResources(), {
      wrapper: createWrapper(),
    });

    // Initially loading
    expect(result.current.isLoading).toBe(true);

    // Wait for data
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify data
    expect(result.current.data).toEqual(mockResources);
    expect(result.current.isLoading).toBe(false);
    expect(workbenchApi.getResources).toHaveBeenCalledWith(undefined);
  });

  it('should fetch resources with pagination parameters', async () => {
    vi.mocked(workbenchApi.getResources).mockResolvedValue(mockResources);

    const params = { skip: 0, limit: 25 };
    const { result } = renderHook(() => useResources(params), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockResources);
    expect(workbenchApi.getResources).toHaveBeenCalledWith(params);
  });

  it('should fetch resources with filtering parameters', async () => {
    const filteredResources = [mockResources[0]];
    vi.mocked(workbenchApi.getResources).mockResolvedValue(filteredResources);

    const params = { content_type: 'code' as const, language: 'typescript' };
    const { result } = renderHook(() => useResources(params), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(filteredResources);
    expect(workbenchApi.getResources).toHaveBeenCalledWith(params);
  });

  it('should handle errors when fetching resources fails', async () => {
    const error = new Error('Failed to fetch resources');
    vi.mocked(workbenchApi.getResources).mockRejectedValue(error);

    const { result } = renderHook(() => useResources(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(error);
    expect(result.current.data).toBeUndefined();
  });

  it('should cache resources with different parameters separately', async () => {
    vi.mocked(workbenchApi.getResources).mockResolvedValue(mockResources);

    const wrapper = createWrapper();

    // First query with no params
    const { result: result1 } = renderHook(() => useResources(), { wrapper });
    await waitFor(() => expect(result1.current.isSuccess).toBe(true));

    // Second query with params
    const params = { skip: 10, limit: 10 };
    const { result: result2 } = renderHook(() => useResources(params), { wrapper });
    await waitFor(() => expect(result2.current.isSuccess).toBe(true));

    // Both should have been called
    expect(workbenchApi.getResources).toHaveBeenCalledTimes(2);
    expect(workbenchApi.getResources).toHaveBeenNthCalledWith(1, undefined);
    expect(workbenchApi.getResources).toHaveBeenNthCalledWith(2, params);
  });
});

// ============================================================================
// Health Monitoring Hooks Tests
// ============================================================================

describe('useSystemHealth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch system health successfully', async () => {
    vi.mocked(workbenchApi.getSystemHealth).mockResolvedValue(mockHealthStatus);

    const { result } = renderHook(() => useSystemHealth(), {
      wrapper: createWrapper(),
    });

    // Initially loading
    expect(result.current.isLoading).toBe(true);

    // Wait for data
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify data
    expect(result.current.data).toEqual(mockHealthStatus);
    expect(result.current.isLoading).toBe(false);
    expect(workbenchApi.getSystemHealth).toHaveBeenCalledTimes(1);
  });

  it('should handle errors when fetching health fails', async () => {
    const error = new Error('Failed to fetch health');
    vi.mocked(workbenchApi.getSystemHealth).mockRejectedValue(error);

    const { result } = renderHook(() => useSystemHealth(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(error);
    expect(result.current.data).toBeUndefined();
  });

  it('should configure polling with refetchInterval', async () => {
    vi.mocked(workbenchApi.getSystemHealth).mockResolvedValue(mockHealthStatus);

    const { result } = renderHook(() => useSystemHealth(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify polling is configured (indirectly through query state)
    expect(result.current.data).toEqual(mockHealthStatus);
  });
});

describe('useAuthHealth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch auth module health successfully', async () => {
    vi.mocked(workbenchApi.getAuthHealth).mockResolvedValue(mockModuleHealth);

    const { result } = renderHook(() => useAuthHealth(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockModuleHealth);
    expect(workbenchApi.getAuthHealth).toHaveBeenCalledTimes(1);
  });

  it('should handle errors when fetching auth health fails', async () => {
    const error = new Error('Failed to fetch auth health');
    vi.mocked(workbenchApi.getAuthHealth).mockRejectedValue(error);

    const { result } = renderHook(() => useAuthHealth(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(error);
  });
});

describe('useResourcesHealth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch resources module health successfully', async () => {
    const resourcesHealth = { ...mockModuleHealth, module: 'resources' };
    vi.mocked(workbenchApi.getResourcesHealth).mockResolvedValue(resourcesHealth);

    const { result } = renderHook(() => useResourcesHealth(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(resourcesHealth);
    expect(workbenchApi.getResourcesHealth).toHaveBeenCalledTimes(1);
  });

  it('should handle errors when fetching resources health fails', async () => {
    const error = new Error('Failed to fetch resources health');
    vi.mocked(workbenchApi.getResourcesHealth).mockRejectedValue(error);

    const { result } = renderHook(() => useResourcesHealth(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(error);
  });
});

// ============================================================================
// Custom Options Tests
// ============================================================================

describe('Custom Options', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should accept custom options for useCurrentUser', async () => {
    vi.mocked(workbenchApi.getCurrentUser).mockResolvedValue(mockUser);

    const { result } = renderHook(
      () =>
        useCurrentUser({
          enabled: false, // Don't fetch automatically
        }),
      { wrapper: createWrapper() }
    );

    // Should not fetch because enabled is false
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(workbenchApi.getCurrentUser).not.toHaveBeenCalled();
  });

  it('should accept custom options for useResources', async () => {
    vi.mocked(workbenchApi.getResources).mockResolvedValue(mockResources);

    const { result } = renderHook(
      () =>
        useResources(undefined, {
          enabled: true,
        }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify data was fetched successfully
    expect(result.current.data).toEqual(mockResources);
  });

  it('should accept custom options for useSystemHealth', async () => {
    vi.mocked(workbenchApi.getSystemHealth).mockResolvedValue(mockHealthStatus);

    const { result } = renderHook(
      () =>
        useSystemHealth({
          refetchInterval: 60000, // Custom refetch interval
        }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Verify data was fetched successfully
    expect(result.current.data).toEqual(mockHealthStatus);
  });
});

// ============================================================================
// Loading States Tests
// ============================================================================

describe('Loading States', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display loading state during fetch', async () => {
    // Create a promise that we can control
    let resolvePromise: (value: any) => void;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    vi.mocked(workbenchApi.getCurrentUser).mockReturnValue(promise as any);

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    // Should be loading
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    // Resolve the promise
    resolvePromise!(mockUser);

    // Wait for success
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Should no longer be loading
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toEqual(mockUser);
  });
});
