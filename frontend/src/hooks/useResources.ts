// Neo Alexandria 2.0 Frontend - Resources Hooks
// Custom React hooks for resource data fetching

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { resourcesApi } from '@/services/api';
import type {
  ResourceQueryParams,
  CreateResourceRequest,
  UpdateResourceRequest,
} from '@/types/api';

// Query keys for cache management
export const resourceKeys = {
  all: ['resources'] as const,
  lists: () => [...resourceKeys.all, 'list'] as const,
  list: (params: ResourceQueryParams) => [...resourceKeys.lists(), params] as const,
  details: () => [...resourceKeys.all, 'detail'] as const,
  detail: (id: string) => [...resourceKeys.details(), id] as const,
  status: (id: string) => [...resourceKeys.all, 'status', id] as const,
};

/**
 * Hook to fetch all resources with filtering and pagination
 */
export function useResources(params: ResourceQueryParams = {}) {
  return useQuery({
    queryKey: resourceKeys.list(params),
    queryFn: () => resourcesApi.getAll(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch a single resource by ID
 */
export function useResource(id: string) {
  return useQuery({
    queryKey: resourceKeys.detail(id),
    queryFn: () => resourcesApi.getById(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch resource ingestion status
 */
export function useResourceStatus(id: string) {
  return useQuery({
    queryKey: resourceKeys.status(id),
    queryFn: () => resourcesApi.getStatus(id),
    enabled: !!id,
    refetchInterval: (data) => {
      // Poll every 2 seconds if status is pending or processing
      if (data?.ingestion_status === 'pending' || !data) {
        return 2000;
      }
      return false;
    },
  });
}

/**
 * Hook to create a new resource
 */
export function useCreateResource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateResourceRequest) => resourcesApi.create(data),
    onSuccess: () => {
      // Invalidate resources list to refetch
      queryClient.invalidateQueries({ queryKey: resourceKeys.lists() });
    },
  });
}

/**
 * Hook to update a resource
 */
export function useUpdateResource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateResourceRequest }) =>
      resourcesApi.update(id, data),
    onSuccess: (updatedResource) => {
      // Update the cache for this specific resource
      queryClient.setQueryData(resourceKeys.detail(updatedResource.id), updatedResource);
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: resourceKeys.lists() });
    },
  });
}

/**
 * Hook to delete a resource
 */
export function useDeleteResource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => resourcesApi.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: resourceKeys.detail(deletedId) });
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: resourceKeys.lists() });
    },
  });
}

/**
 * Hook to classify a resource
 */
export function useClassifyResource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, code }: { id: string; code: string }) =>
      resourcesApi.classify(id, code),
    onSuccess: (updatedResource) => {
      // Update the cache for this specific resource
      queryClient.setQueryData(resourceKeys.detail(updatedResource.id), updatedResource);
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: resourceKeys.lists() });
    },
  });
}
