/**
 * useIngestResource hook
 * 
 * Mutation hook for ingesting new resources with automatic cache invalidation.
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ingestResource } from '../api';
import type { IngestResourcePayload } from '@/core/types/resource';

/**
 * Hook for ingesting a new resource
 * 
 * Automatically invalidates the resource list query on success to refresh the table.
 * 
 * @returns Mutation object with mutate function and status
 * 
 * @example
 * ```tsx
 * const { mutate, isPending } = useIngestResource();
 * 
 * const handleSubmit = (data) => {
 *   mutate(data, {
 *     onSuccess: (result) => {
 *       toast.success('Ingestion started!');
 *       console.log('Resource ID:', result.id);
 *     },
 *     onError: (error) => {
 *       toast.error('Failed to ingest resource');
 *     },
 *   });
 * };
 * ```
 */
export function useIngestResource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: IngestResourcePayload) => ingestResource(payload),
    onSuccess: () => {
      // Invalidate resource list to refresh table
      queryClient.invalidateQueries({ queryKey: ['resources', 'list'] });
    },
  });
}
