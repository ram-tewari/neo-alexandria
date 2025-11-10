import { QueryClient } from '@tanstack/react-query';

/**
 * Configure TanStack Query client with caching strategies
 * and stale-while-revalidate behavior
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Data is considered fresh for 5 minutes
      staleTime: 5 * 60 * 1000, // 5 minutes
      
      // Cache data for 10 minutes before garbage collection
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      
      // Don't refetch on window focus by default
      refetchOnWindowFocus: false,
      
      // Retry failed requests once
      retry: 1,
      
      // Retry delay with exponential backoff
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      
      // Don't refetch on mount if data is fresh
      refetchOnMount: false,
      
      // Refetch on reconnect
      refetchOnReconnect: true,
    },
    mutations: {
      // Retry mutations once on failure
      retry: 1,
      
      // Retry delay for mutations
      retryDelay: 1000,
    },
  },
});

/**
 * Clear all cached queries
 */
export function clearQueryCache(): void {
  queryClient.clear();
}

/**
 * Invalidate specific query keys
 */
export function invalidateQueries(queryKey: string[]): void {
  queryClient.invalidateQueries({ queryKey });
}

/**
 * Prefetch a query
 */
export async function prefetchQuery<T>(
  queryKey: string[],
  queryFn: () => Promise<T>
): Promise<void> {
  await queryClient.prefetchQuery({
    queryKey,
    queryFn,
  });
}
