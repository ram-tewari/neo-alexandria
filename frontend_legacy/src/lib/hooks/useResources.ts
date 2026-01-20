/**
 * useResources hook
 * Fetches and manages resources data with loading and error states
 */

import { useState, useEffect } from 'react';
import { mockApiClient } from '../api/mock-data';
import type { Resource, ListParams } from '../api/types';

interface UseResourcesResult {
  data: Resource[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

/**
 * Hook for fetching resources with loading state
 */
export function useResources(params?: ListParams): UseResourcesResult {
  const [data, setData] = useState<Resource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchResources = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await mockApiClient.resources.list(params);
      setData(result.resources);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch resources'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, [params?.page, params?.page_size, params?.sort_by, params?.order]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchResources,
  };
}
