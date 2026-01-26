/**
 * TanStack Query Hooks for Workbench Data
 * 
 * React Query hooks for Phase 1 workbench features:
 * - User authentication and rate limits
 * - Resource listing
 * - System health monitoring
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 3.2 Create TanStack Query hooks for Phase 1
 * Requirements: 2.1, 2.2, 2.3, 2.4
 */

import { useQuery, type UseQueryOptions } from '@tanstack/react-query';
import {
  workbenchApi,
  workbenchQueryKeys,
  workbenchCacheConfig,
} from '@/lib/api/workbench';
import type {
  User,
  RateLimitStatus,
  Resource,
  ResourceListParams,
  HealthStatus,
  ModuleHealth,
} from '@/types/api';

// ============================================================================
// Authentication Hooks
// ============================================================================

/**
 * Hook to fetch current authenticated user information
 * 
 * @returns Query result with current user data
 * @requirement 2.1 - Fetch current user info from /api/auth/me
 * 
 * @example
 * ```tsx
 * function UserProfile() {
 *   const { data: user, isLoading, error } = useCurrentUser();
 *   
 *   if (isLoading) return <Spinner />;
 *   if (error) return <ErrorMessage error={error} />;
 *   
 *   return <div>Welcome, {user.username}!</div>;
 * }
 * ```
 */
export function useCurrentUser(
  options?: Omit<UseQueryOptions<User, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<User, Error>({
    queryKey: workbenchQueryKeys.user.current(),
    queryFn: workbenchApi.getCurrentUser,
    staleTime: workbenchCacheConfig.user.staleTime,
    gcTime: workbenchCacheConfig.user.cacheTime,
    ...options,
  });
}

/**
 * Hook to fetch current user's rate limit status
 * 
 * @returns Query result with rate limit information
 * @requirement 2.4 - Fetch rate limit from /api/auth/rate-limit
 * 
 * @example
 * ```tsx
 * function RateLimitIndicator() {
 *   const { data: rateLimit, isLoading } = useRateLimit();
 *   
 *   if (isLoading) return null;
 *   
 *   return (
 *     <div>
 *       {rateLimit.remaining} / {rateLimit.limit} requests remaining
 *     </div>
 *   );
 * }
 * ```
 */
export function useRateLimit(
  options?: Omit<UseQueryOptions<RateLimitStatus, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<RateLimitStatus, Error>({
    queryKey: workbenchQueryKeys.user.rateLimit(),
    queryFn: workbenchApi.getRateLimit,
    staleTime: workbenchCacheConfig.user.staleTime,
    gcTime: workbenchCacheConfig.user.cacheTime,
    ...options,
  });
}

// ============================================================================
// Resource Hooks
// ============================================================================

/**
 * Hook to fetch list of resources with optional filtering and pagination
 * 
 * @param params - Query parameters for filtering and pagination
 * @returns Query result with resources array
 * @requirement 2.2 - Fetch resource list from /resources
 * 
 * @example
 * ```tsx
 * function ResourceList() {
 *   const { data: resources, isLoading, error } = useResources({
 *     skip: 0,
 *     limit: 25,
 *     content_type: 'code',
 *   });
 *   
 *   if (isLoading) return <Skeleton />;
 *   if (error) return <ErrorMessage error={error} />;
 *   
 *   return (
 *     <ul>
 *       {resources.map(resource => (
 *         <li key={resource.id}>{resource.title}</li>
 *       ))}
 *     </ul>
 *   );
 * }
 * ```
 */
export function useResources(
  params?: ResourceListParams,
  options?: Omit<UseQueryOptions<Resource[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Resource[], Error>({
    queryKey: workbenchQueryKeys.resources.list(params),
    queryFn: () => workbenchApi.getResources(params),
    staleTime: workbenchCacheConfig.resources.staleTime,
    gcTime: workbenchCacheConfig.resources.cacheTime,
    ...options,
  });
}

// ============================================================================
// Health Monitoring Hooks
// ============================================================================

/**
 * Hook to fetch overall system health status with automatic polling
 * 
 * @returns Query result with system health data
 * @requirement 2.3 - Display health status from /api/monitoring/health
 * 
 * @example
 * ```tsx
 * function SystemHealthIndicator() {
 *   const { data: health, isLoading } = useSystemHealth();
 *   
 *   if (isLoading) return <Spinner />;
 *   
 *   return (
 *     <div className={health.status === 'healthy' ? 'text-green-500' : 'text-red-500'}>
 *       System: {health.status}
 *     </div>
 *   );
 * }
 * ```
 */
export function useSystemHealth(
  options?: Omit<UseQueryOptions<HealthStatus, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<HealthStatus, Error>({
    queryKey: workbenchQueryKeys.health.system(),
    queryFn: workbenchApi.getSystemHealth,
    staleTime: workbenchCacheConfig.health.staleTime,
    gcTime: workbenchCacheConfig.health.cacheTime,
    refetchInterval: workbenchCacheConfig.health.refetchInterval,
    ...options,
  });
}

/**
 * Hook to fetch authentication module health status
 * 
 * @returns Query result with auth module health data
 * @requirement 2.3 - Display module health status
 * 
 * @example
 * ```tsx
 * function AuthHealthIndicator() {
 *   const { data: authHealth } = useAuthHealth();
 *   
 *   return (
 *     <div>
 *       Auth Module: {authHealth?.status || 'unknown'}
 *     </div>
 *   );
 * }
 * ```
 */
export function useAuthHealth(
  options?: Omit<UseQueryOptions<ModuleHealth, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<ModuleHealth, Error>({
    queryKey: workbenchQueryKeys.health.auth(),
    queryFn: workbenchApi.getAuthHealth,
    staleTime: workbenchCacheConfig.health.staleTime,
    gcTime: workbenchCacheConfig.health.cacheTime,
    refetchInterval: workbenchCacheConfig.health.refetchInterval,
    ...options,
  });
}

/**
 * Hook to fetch resources module health status
 * 
 * @returns Query result with resources module health data
 * @requirement 2.3 - Display module health status
 * 
 * @example
 * ```tsx
 * function ResourcesHealthIndicator() {
 *   const { data: resourcesHealth } = useResourcesHealth();
 *   
 *   return (
 *     <div>
 *       Resources Module: {resourcesHealth?.status || 'unknown'}
 *     </div>
 *   );
 * }
 * ```
 */
export function useResourcesHealth(
  options?: Omit<UseQueryOptions<ModuleHealth, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<ModuleHealth, Error>({
    queryKey: workbenchQueryKeys.health.resources(),
    queryFn: workbenchApi.getResourcesHealth,
    staleTime: workbenchCacheConfig.health.staleTime,
    gcTime: workbenchCacheConfig.health.cacheTime,
    refetchInterval: workbenchCacheConfig.health.refetchInterval,
    ...options,
  });
}
