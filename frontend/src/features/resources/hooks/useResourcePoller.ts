/**
 * useResourcePoller hook
 * 
 * Polls resource ingestion status at 2-second intervals until completion or failure.
 * Automatically invalidates resource list query on completion.
 */
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getResourceStatus } from '../api';
import { ResourceStatus } from '@/core/types/resource';

interface UseResourcePollerOptions {
  resourceId: string | null;
  onComplete?: () => void;
  onError?: (error: string) => void;
}

/**
 * Hook for polling resource ingestion status
 * 
 * @param options - Configuration options
 * @param options.resourceId - Resource UUID to poll (null to disable)
 * @param options.onComplete - Callback invoked when ingestion completes successfully
 * @param options.onError - Callback invoked when ingestion fails
 * 
 * @returns Query result with resource status data
 * 
 * @example
 * ```tsx
 * const { data: status } = useResourcePoller({
 *   resourceId: '123e4567-e89b-12d3-a456-426614174000',
 *   onComplete: () => toast.success('Ingestion complete!'),
 *   onError: (error) => toast.error(error),
 * });
 * ```
 */
export function useResourcePoller({
  resourceId,
  onComplete,
  onError,
}: UseResourcePollerOptions) {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: ['resources', 'status', resourceId],
    queryFn: async () => {
      if (!resourceId) {
        throw new Error('Resource ID is required');
      }
      try {
        return await getResourceStatus(resourceId);
      } catch (error: any) {
        // Handle 404 - resource was deleted
        if (error.response?.status === 404) {
          console.error('Resource not found during polling:', resourceId);
          if (onError) {
            onError('Resource no longer exists');
          }
          throw error;
        }
        throw error;
      }
    },
    enabled: !!resourceId,
    staleTime: 0, // Always fetch fresh data
    retry: (failureCount, error: any) => {
      // Don't retry on 404 (resource deleted)
      if (error.response?.status === 404) {
        return false;
      }
      // Retry up to 3 times with exponential backoff for other errors
      return failureCount < 3;
    },
    retryDelay: (attemptIndex) => {
      // Exponential backoff: 1s, 2s, 4s
      return Math.min(1000 * 2 ** attemptIndex, 4000);
    },
    refetchInterval: (query) => {
      const status = query.state.data?.ingestion_status;

      // Stop polling if completed or failed
      if (status === ResourceStatus.COMPLETED || status === ResourceStatus.FAILED) {
        // Trigger callbacks on status change
        if (status === ResourceStatus.COMPLETED && onComplete) {
          onComplete();
        }
        if (status === ResourceStatus.FAILED && onError && query.state.data?.ingestion_error) {
          console.error('Ingestion failed:', query.state.data.ingestion_error);
          onError(query.state.data.ingestion_error);
        }

        // Invalidate resource list to refresh table
        queryClient.invalidateQueries({ queryKey: ['resources', 'list'] });

        return false; // Stop polling
      }

      // Continue polling for pending/processing status
      if (status === ResourceStatus.PENDING || status === ResourceStatus.PROCESSING) {
        return 2000; // Poll every 2 seconds
      }

      return false; // Stop polling for unknown status
    },
  });
}
