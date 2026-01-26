/**
 * Workbench API Client
 * 
 * Provides API endpoints for Phase 1 workbench features:
 * - Authentication (user info, rate limits)
 * - Resources (list, search)
 * - Health monitoring (system health, module health)
 * 
 * Phase: 2.5 Backend API Integration
 * Requirements: 2.1, 2.2, 2.3, 2.4, 7.5 (runtime validation)
 */

import { apiClient } from '@/core/api/client';
import { validateResponseStrict } from '@/core/api/validation';
import {
  UserSchema,
  RateLimitStatusSchema,
  ResourceListResponseSchema,
  HealthStatusSchema,
  ModuleHealthSchema,
} from '@/types/api.schemas';
import type {
  User,
  RateLimitStatus,
  Resource,
  ResourceListParams,
  ResourceListResponse,
  HealthStatus,
  ModuleHealth,
} from '@/types/api';

// ============================================================================
// Workbench API Client Interface
// ============================================================================

/**
 * Workbench API client with all Phase 1 workbench-related endpoints
 */
export const workbenchApi = {
  // ==========================================================================
  // Authentication Endpoints
  // ==========================================================================

  /**
   * Get current authenticated user information
   * @returns Current user details
   * @endpoint GET /api/auth/me
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/api/auth/me');
    return validateResponseStrict(response.data, UserSchema, 'GET /api/auth/me');
  },

  /**
   * Get current user's rate limit status
   * @returns Rate limit information (tier, limit, remaining, reset)
   * @endpoint GET /api/auth/rate-limit
   */
  getRateLimit: async (): Promise<RateLimitStatus> => {
    const response = await apiClient.get('/api/auth/rate-limit');
    return validateResponseStrict(response.data, RateLimitStatusSchema, 'GET /api/auth/rate-limit');
  },

  // ==========================================================================
  // Resource Endpoints
  // ==========================================================================

  /**
   * Get list of resources with optional filtering and pagination
   * @param params - Query parameters for filtering and pagination
   * @returns Paginated list of resources
   * @endpoint GET /resources
   */
  getResources: async (params?: ResourceListParams): Promise<Resource[]> => {
    const response = await apiClient.get('/resources', { params });
    const validated = validateResponseStrict(response.data, ResourceListResponseSchema, 'GET /resources');
    return validated.items;
  },

  // ==========================================================================
  // Health Monitoring Endpoints
  // ==========================================================================

  /**
   * Get overall system health status
   * @returns System health with component and module statuses
   * @endpoint GET /api/monitoring/health
   */
  getSystemHealth: async (): Promise<HealthStatus> => {
    const response = await apiClient.get('/api/monitoring/health');
    return validateResponseStrict(response.data, HealthStatusSchema, 'GET /api/monitoring/health');
  },

  /**
   * Get health status for authentication module
   * @returns Auth module health status
   * @endpoint GET /api/monitoring/health/auth
   */
  getAuthHealth: async (): Promise<ModuleHealth> => {
    const response = await apiClient.get('/api/monitoring/health/auth');
    const validated = validateResponseStrict(
      response.data,
      ModuleHealthSchema,
      'GET /api/monitoring/health/auth'
    );
    return validated;
  },

  /**
   * Get health status for resources module
   * @returns Resources module health status
   * @endpoint GET /api/monitoring/health/resources
   */
  getResourcesHealth: async (): Promise<ModuleHealth> => {
    const response = await apiClient.get('/api/monitoring/health/resources');
    const validated = validateResponseStrict(
      response.data,
      ModuleHealthSchema,
      'GET /api/monitoring/health/resources'
    );
    return validated;
  },
};

// ============================================================================
// TanStack Query Key Factories
// ============================================================================

/**
 * Query key factories for TanStack Query caching
 * 
 * These factories generate consistent cache keys for React Query.
 * Use these keys in useQuery and useMutation hooks to ensure proper
 * cache invalidation and data consistency.
 * 
 * @example
 * ```typescript
 * const { data } = useQuery({
 *   queryKey: workbenchQueryKeys.user.current(),
 *   queryFn: workbenchApi.getCurrentUser,
 * });
 * ```
 */
export const workbenchQueryKeys = {
  /**
   * User-related query keys
   */
  user: {
    /** Current authenticated user */
    current: () => ['user', 'current'] as const,
    /** User rate limit status */
    rateLimit: () => ['user', 'rateLimit'] as const,
  },

  /**
   * Resource-related query keys
   */
  resources: {
    /** All resources query keys */
    all: () => ['resources'] as const,
    /** Resources list with optional filters */
    list: (params?: ResourceListParams) => ['resources', 'list', params] as const,
  },

  /**
   * Health monitoring query keys
   */
  health: {
    /** System health status */
    system: () => ['health', 'system'] as const,
    /** Auth module health */
    auth: () => ['health', 'auth'] as const,
    /** Resources module health */
    resources: () => ['health', 'resources'] as const,
  },
};

// ============================================================================
// Cache Configuration
// ============================================================================

/**
 * Default cache times for TanStack Query (in milliseconds)
 * 
 * - staleTime: How long data is considered fresh (no refetch)
 * - cacheTime: How long unused data stays in cache
 */
export const workbenchCacheConfig = {
  user: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  resources: {
    staleTime: 2 * 60 * 1000, // 2 minutes
    cacheTime: 5 * 60 * 1000, // 5 minutes
  },
  health: {
    staleTime: 30 * 1000, // 30 seconds
    cacheTime: 60 * 1000, // 1 minute
    refetchInterval: 30 * 1000, // Poll every 30 seconds
  },
};
