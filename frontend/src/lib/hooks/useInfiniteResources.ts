/**
 * useInfiniteResources hook
 * Implements infinite scroll data fetching with React Query
 */

import { useInfiniteQuery } from '@tanstack/react-query';
import { resourcesApi } from '../api/resources';
import type { ResourceListParams, ResourceRead } from '../api/types';

export interface UseInfiniteResourcesOptions extends Omit<ResourceListParams, 'offset' | 'limit'> {
  /** Number of items per page */
  pageSize?: number;
  /** Whether the query is enabled */
  enabled?: boolean;
}

/**
 * Hook for fetching resources with infinite scroll support
 * 
 * @example
 * ```tsx
 * const {
 *   data,
 *   fetchNextPage,
 *   hasNextPage,
 *   isFetchingNextPage,
 *   isLoading,
 *   error,
 * } = useInfiniteResources({
 *   q: searchQuery,
 *   classification_code: selectedClassification,
 *   pageSize: 20,
 * });
 * 
 * const resources = data?.pages.flatMap(page => page.items) ?? [];
 * ```
 */
export function useInfiniteResources({
  pageSize = 20,
  enabled = true,
  ...filters
}: UseInfiniteResourcesOptions = {}) {
  const query = useInfiniteQuery({
    queryKey: ['resources', 'infinite', filters, pageSize],
    
    queryFn: async ({ pageParam = 0 }) => {
      const response = await resourcesApi.list({
        ...filters,
        offset: pageParam,
        limit: pageSize,
      });
      
      return response;
    },
    
    // Determine if there are more pages to fetch
    getNextPageParam: (lastPage, allPages) => {
      // If the last page has fewer items than the page size, we've reached the end
      if (lastPage.items.length < pageSize) {
        return undefined;
      }
      
      // Calculate the next offset
      const nextOffset = allPages.length * pageSize;
      
      // If we've fetched all items, return undefined
      if (nextOffset >= lastPage.total) {
        return undefined;
      }
      
      return nextOffset;
    },
    
    // Initial page param
    initialPageParam: 0,
    
    // Enable/disable the query
    enabled,
    
    // Stale time: 5 minutes
    staleTime: 5 * 60 * 1000,
    
    // Cache time: 10 minutes
    gcTime: 10 * 60 * 1000,
  });

  return {
    ...query,
    
    /**
     * Flattened array of all resources from all pages
     */
    resources: query.data?.pages.flatMap(page => page.items) ?? [],
    
    /**
     * Total number of resources available
     */
    total: query.data?.pages[0]?.total ?? 0,
  };
}

export type UseInfiniteResourcesResult = ReturnType<typeof useInfiniteResources>;
