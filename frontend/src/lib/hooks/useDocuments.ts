import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { libraryApi } from '@/lib/api/library';
import { useLibraryStore } from '@/stores/library';
import type { Resource } from '@/types/library';

interface UseDocumentsParams {
  type?: string;
  quality_min?: number;
  quality_max?: number;
  limit?: number;
  offset?: number;
}

/**
 * Custom hook for managing documents with TanStack Query
 * Provides document fetching, upload, update, and delete operations
 * with optimistic updates and cache management
 */
export function useDocuments(params?: UseDocumentsParams) {
  const queryClient = useQueryClient();
  const { setResources, addResource, updateResource: updateResourceInStore, removeResource } = useLibraryStore();

  // Fetch documents
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['documents', params],
    queryFn: async () => {
      const result = await libraryApi.listResources(params);
      setResources(result.resources);
      return result;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Upload mutation with optimistic updates
  const uploadMutation = useMutation({
    mutationFn: ({ file, metadata }: { file: File; metadata?: Partial<Resource> }) =>
      libraryApi.uploadResource(file, metadata),
    onMutate: async ({ file }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['documents'] });

      // Optimistic update
      const tempResource: Partial<Resource> = {
        id: `temp-${Date.now()}`,
        title: file.name,
        type: 'pdf',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      addResource(tempResource as Resource);

      return { tempResource };
    },
    onSuccess: (data, variables, context) => {
      // Replace temp with real resource
      if (context?.tempResource) {
        removeResource(context.tempResource.id!);
      }
      addResource(data);
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: (error, variables, context) => {
      // Remove temp resource on error
      if (context?.tempResource) {
        removeResource(context.tempResource.id!);
      }
    },
  });

  // Update mutation with optimistic updates
  const updateMutation = useMutation({
    mutationFn: ({ resourceId, updates }: { resourceId: string; updates: Partial<Resource> }) =>
      libraryApi.updateResource(resourceId, updates),
    onMutate: async ({ resourceId, updates }) => {
      await queryClient.cancelQueries({ queryKey: ['documents'] });

      // Snapshot previous value
      const previousResources = queryClient.getQueryData(['documents', params]);

      // Optimistic update
      updateResourceInStore(resourceId, updates);

      return { previousResources };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousResources) {
        setResources((context.previousResources as any).resources);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  // Delete mutation with optimistic updates
  const deleteMutation = useMutation({
    mutationFn: (resourceId: string) => libraryApi.deleteResource(resourceId),
    onMutate: async (resourceId) => {
      await queryClient.cancelQueries({ queryKey: ['documents'] });

      // Snapshot previous value
      const previousResources = queryClient.getQueryData(['documents', params]);

      // Optimistic update
      removeResource(resourceId);

      return { previousResources };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousResources) {
        setResources((context.previousResources as any).resources);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  return {
    // Data
    documents: data?.resources || [],
    total: data?.total || 0,

    // Loading states
    isLoading,
    isUploading: uploadMutation.isLoading,
    isUpdating: updateMutation.isLoading,
    isDeleting: deleteMutation.isLoading,

    // Error states
    error,
    uploadError: uploadMutation.error,
    updateError: updateMutation.error,
    deleteError: deleteMutation.error,

    // Actions
    uploadDocument: uploadMutation.mutate,
    updateDocument: updateMutation.mutate,
    deleteDocument: deleteMutation.mutate,
    refetch,
  };
}
