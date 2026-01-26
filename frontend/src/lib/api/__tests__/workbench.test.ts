/**
 * Workbench API Client Tests
 * 
 * Tests for Phase 1 workbench API endpoints:
 * - Authentication (getCurrentUser, getRateLimit)
 * - Resources (getResources)
 * - Health monitoring (getSystemHealth, getAuthHealth, getResourcesHealth)
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 3.1 Create workbench API client module
 * Requirements: 2.1, 2.2, 2.3, 2.4
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { workbenchApi, workbenchQueryKeys, workbenchCacheConfig } from '../workbench';
import { apiClient } from '@/core/api/client';
import type {
  User,
  RateLimitStatus,
  Resource,
  HealthStatus,
  ModuleHealth,
} from '@/types/api';

// Mock the API client
vi.mock('@/core/api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

// Mock the validation module
vi.mock('@/core/api/validation', () => ({
  validateResponseStrict: vi.fn((data) => data),
}));

describe('workbenchApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ==========================================================================
  // Authentication Endpoints
  // ==========================================================================

  describe('getCurrentUser', () => {
    it('should fetch current user from /api/auth/me', async () => {
      const mockUser: User = {
        id: 'user-1',
        username: 'testuser',
        email: 'test@example.com',
        tier: 'free',
        is_active: true,
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockUser });

      const result = await workbenchApi.getCurrentUser();

      expect(apiClient.get).toHaveBeenCalledWith('/api/auth/me');
      expect(result).toEqual(mockUser);
    });

    it('should handle errors when fetching current user', async () => {
      const mockError = new Error('Unauthorized');
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      await expect(workbenchApi.getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('getRateLimit', () => {
    it('should fetch rate limit status from /api/auth/rate-limit', async () => {
      const mockRateLimit: RateLimitStatus = {
        tier: 'free',
        limit: 100,
        remaining: 95,
        reset: 1704067200,
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockRateLimit });

      const result = await workbenchApi.getRateLimit();

      expect(apiClient.get).toHaveBeenCalledWith('/api/auth/rate-limit');
      expect(result).toEqual(mockRateLimit);
    });

    it('should handle errors when fetching rate limit', async () => {
      const mockError = new Error('Service unavailable');
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      await expect(workbenchApi.getRateLimit()).rejects.toThrow('Service unavailable');
    });
  });

  // ==========================================================================
  // Resource Endpoints
  // ==========================================================================

  describe('getResources', () => {
    it('should fetch resources from /resources without params', async () => {
      const mockResources: Resource[] = [
        {
          id: 'resource-1',
          title: 'Test Resource 1',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          ingestion_status: 'completed',
        },
        {
          id: 'resource-2',
          title: 'Test Resource 2',
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
          ingestion_status: 'completed',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: { items: mockResources, total: 2 },
      });

      const result = await workbenchApi.getResources();

      expect(apiClient.get).toHaveBeenCalledWith('/resources', { params: undefined });
      expect(result).toEqual(mockResources);
    });

    it('should fetch resources with query parameters', async () => {
      const mockResources: Resource[] = [
        {
          id: 'resource-1',
          title: 'Python Resource',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          ingestion_status: 'completed',
          language: 'python',
        },
      ];

      const params = {
        language: 'python',
        limit: 10,
        offset: 0,
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: { items: mockResources, total: 1 },
      });

      const result = await workbenchApi.getResources(params);

      expect(apiClient.get).toHaveBeenCalledWith('/resources', { params });
      expect(result).toEqual(mockResources);
    });

    it('should handle empty resource list', async () => {
      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: { items: [], total: 0 },
      });

      const result = await workbenchApi.getResources();

      expect(result).toEqual([]);
    });

    it('should handle errors when fetching resources', async () => {
      const mockError = new Error('Network error');
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      await expect(workbenchApi.getResources()).rejects.toThrow('Network error');
    });
  });

  // ==========================================================================
  // Health Monitoring Endpoints
  // ==========================================================================

  describe('getSystemHealth', () => {
    it('should fetch system health from /api/monitoring/health', async () => {
      const mockHealth: HealthStatus = {
        status: 'healthy',
        message: 'All systems operational',
        timestamp: '2024-01-01T00:00:00Z',
        components: {
          database: { status: 'healthy' },
          cache: { status: 'healthy' },
          event_bus: { status: 'healthy' },
        },
        modules: {
          auth: 'healthy',
          resources: 'healthy',
          search: 'healthy',
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockHealth });

      const result = await workbenchApi.getSystemHealth();

      expect(apiClient.get).toHaveBeenCalledWith('/api/monitoring/health');
      expect(result).toEqual(mockHealth);
    });

    it('should handle degraded system health', async () => {
      const mockHealth: HealthStatus = {
        status: 'degraded',
        message: 'Some components degraded',
        timestamp: '2024-01-01T00:00:00Z',
        components: {
          database: { status: 'healthy' },
          cache: { status: 'degraded', details: 'High latency' },
          event_bus: { status: 'healthy' },
        },
        modules: {
          auth: 'healthy',
          resources: 'degraded',
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockHealth });

      const result = await workbenchApi.getSystemHealth();

      expect(result.status).toBe('degraded');
      expect(result.components.cache.status).toBe('degraded');
    });

    it('should handle errors when fetching system health', async () => {
      const mockError = new Error('Service unavailable');
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      await expect(workbenchApi.getSystemHealth()).rejects.toThrow('Service unavailable');
    });
  });

  describe('getAuthHealth', () => {
    it('should fetch auth module health from /api/monitoring/health/auth', async () => {
      const mockHealth: ModuleHealth = 'healthy';

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockHealth });

      const result = await workbenchApi.getAuthHealth();

      expect(apiClient.get).toHaveBeenCalledWith('/api/monitoring/health/auth');
      expect(result).toBe('healthy');
    });

    it('should handle degraded auth health', async () => {
      const mockHealth: ModuleHealth = 'degraded';

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockHealth });

      const result = await workbenchApi.getAuthHealth();

      expect(result).toBe('degraded');
    });

    it('should handle errors when fetching auth health', async () => {
      const mockError = new Error('Service unavailable');
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      await expect(workbenchApi.getAuthHealth()).rejects.toThrow('Service unavailable');
    });
  });

  describe('getResourcesHealth', () => {
    it('should fetch resources module health from /api/monitoring/health/resources', async () => {
      const mockHealth: ModuleHealth = 'healthy';

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockHealth });

      const result = await workbenchApi.getResourcesHealth();

      expect(apiClient.get).toHaveBeenCalledWith('/api/monitoring/health/resources');
      expect(result).toBe('healthy');
    });

    it('should handle unhealthy resources health', async () => {
      const mockHealth: ModuleHealth = 'unhealthy';

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockHealth });

      const result = await workbenchApi.getResourcesHealth();

      expect(result).toBe('unhealthy');
    });

    it('should handle errors when fetching resources health', async () => {
      const mockError = new Error('Service unavailable');
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      await expect(workbenchApi.getResourcesHealth()).rejects.toThrow('Service unavailable');
    });
  });
});

// ============================================================================
// Query Key Factories Tests
// ============================================================================

describe('workbenchQueryKeys', () => {
  it('should generate correct user query keys', () => {
    expect(workbenchQueryKeys.user.current()).toEqual(['user', 'current']);
    expect(workbenchQueryKeys.user.rateLimit()).toEqual(['user', 'rateLimit']);
  });

  it('should generate correct resource query keys', () => {
    expect(workbenchQueryKeys.resources.all()).toEqual(['resources']);
    expect(workbenchQueryKeys.resources.list()).toEqual(['resources', 'list', undefined]);
    expect(workbenchQueryKeys.resources.list({ language: 'python' })).toEqual([
      'resources',
      'list',
      { language: 'python' },
    ]);
  });

  it('should generate correct health query keys', () => {
    expect(workbenchQueryKeys.health.system()).toEqual(['health', 'system']);
    expect(workbenchQueryKeys.health.auth()).toEqual(['health', 'auth']);
    expect(workbenchQueryKeys.health.resources()).toEqual(['health', 'resources']);
  });
});

// ============================================================================
// Cache Configuration Tests
// ============================================================================

describe('workbenchCacheConfig', () => {
  it('should have correct user cache times', () => {
    expect(workbenchCacheConfig.user.staleTime).toBe(5 * 60 * 1000); // 5 minutes
    expect(workbenchCacheConfig.user.cacheTime).toBe(10 * 60 * 1000); // 10 minutes
  });

  it('should have correct resources cache times', () => {
    expect(workbenchCacheConfig.resources.staleTime).toBe(2 * 60 * 1000); // 2 minutes
    expect(workbenchCacheConfig.resources.cacheTime).toBe(5 * 60 * 1000); // 5 minutes
  });

  it('should have correct health cache times', () => {
    expect(workbenchCacheConfig.health.staleTime).toBe(30 * 1000); // 30 seconds
    expect(workbenchCacheConfig.health.cacheTime).toBe(60 * 1000); // 1 minute
    expect(workbenchCacheConfig.health.refetchInterval).toBe(30 * 1000); // 30 seconds
  });
});
