/**
 * useResourceList hook
 * 
 * Fetches paginated list of resources with caching and smooth pagination.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchResources } from '../api';
import type { ResourceListParams } from '@/core/types/resource';

interface UseResourceListOptions extends ResourceListParams {
  // Additional options can be added here
}

/**
 * Hook for fetching paginated resource list
 * 
 * @param options - Query parameters for filtering, sorting, and pagination
 * @returns Query result with resource list data
 * 
 * @example
 * ```tsx
 * const { data, isLoading } = useResourceList({
 *   page: 1,
 *   limit: 25,
 *   sort: 'created_at:desc',
 * });
 * ```
 */
export function useResourceList(options: UseResourceListOptions = {}) {
  const {
    page = 1,
    limit = 25,
    sort = 'created_at:desc',
    ...filters
  } = options;

  return useQuery({
    queryKey: ['resources', 'list', { page, limit, sort, ...filters }],
    queryFn: () => fetchResources({ page, limit, sort, ...filters }),
    placeholderData: (previousData) => previousData, // Keep previous data during refetch (replaces keepPreviousData)
    staleTime: 30000, // Cache for 30 seconds
  });
}
