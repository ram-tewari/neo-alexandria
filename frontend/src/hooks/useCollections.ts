// Neo Alexandria 2.0 Frontend - Collections Hooks
// Custom React hooks for collection management

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { collectionsApi } from '@/services/api';
import type {
  CreateCollectionRequest,
  GetCollectionsParams,
} from '@/services/api';

// Query keys for cache management
export const collectionKeys = {
  all: ['collections'] as const,
  lists: () => [...collectionKeys.all, 'list'] as const,
  list: (params: GetCollectionsParams) => [...collectionKeys.lists(), params] as const,
  details: () => [...collectionKeys.all, 'detail'] as const,
  detail: (id: string, userId?: string) => [...collectionKeys.details(), id, userId] as const,
  recommendations: (id: string, userId?: string, limit?: number) => 
    [...collectionKeys.all, 'recommendations', id, userId, limit] as const,
};

/**
 * Hook to fetch all collections
 */
export function useCollections(params: GetCollectionsParams = {}) {
  return useQuery({
    queryKey: collectionKeys.list(params),
    queryFn: () => collectionsApi.getAll(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch a single collection by ID
 */
export function useCollection(id: string, userId?: string) {
  return useQuery({
    queryKey: collectionKeys.detail(id, userId),
    queryFn: () => collectionsApi.getById(id, userId),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch collection recommendations
 */
export function useCollectionRecommendations(id: string, userId?: string, limit?: number) {
  return useQuery({
    queryKey: collectionKeys.recommendations(id, userId, limit),
    queryFn: () => collectionsApi.getRecommendations(id, userId, limit),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to create a new collection
 */
export function useCreateCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ data, userId }: { data: CreateCollectionRequest; userId: string }) =>
      collectionsApi.create(data, userId),
    onSuccess: () => {
      // Invalidate collections list to refetch
      queryClient.invalidateQueries({ queryKey: collectionKeys.lists() });
    },
  });
}

/**
 * Hook to update a collection
 */
export function useUpdateCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
      userId,
    }: {
      id: string;
      data: Partial<CreateCollectionRequest>;
      userId: string;
    }) => collectionsApi.update(id, data, userId),
    onSuccess: (updatedCollection, variables) => {
      // Update the cache for this specific collection
      queryClient.setQueryData(
        collectionKeys.detail(updatedCollection.id, variables.userId),
        updatedCollection
      );
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: collectionKeys.lists() });
    },
  });
}

/**
 * Hook to delete a collection
 */
export function useDeleteCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId }: { id: string; userId: string }) =>
      collectionsApi.delete(id, userId),
    onSuccess: (_, variables) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: collectionKeys.detail(variables.id, variables.userId) });
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: collectionKeys.lists() });
    },
  });
}

/**
 * Hook to add resources to a collection
 */
export function useAddResourcesToCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      collectionId,
      resourceIds,
      userId,
    }: {
      collectionId: string;
      resourceIds: string[];
      userId: string;
    }) => collectionsApi.addResources(collectionId, resourceIds, userId),
    onSuccess: (_, variables) => {
      // Invalidate the collection detail to refetch with updated resources
      queryClient.invalidateQueries({
        queryKey: collectionKeys.detail(variables.collectionId, variables.userId),
      });
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: collectionKeys.lists() });
    },
  });
}

/**
 * Hook to remove resources from a collection
 */
export function useRemoveResourcesFromCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      collectionId,
      resourceIds,
      userId,
    }: {
      collectionId: string;
      resourceIds: string[];
      userId: string;
    }) => collectionsApi.removeResources(collectionId, resourceIds, userId),
    onSuccess: (_, variables) => {
      // Invalidate the collection detail to refetch with updated resources
      queryClient.invalidateQueries({
        queryKey: collectionKeys.detail(variables.collectionId, variables.userId),
      });
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: collectionKeys.lists() });
    },
  });
}
