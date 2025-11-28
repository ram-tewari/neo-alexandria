import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { resourcesApi } from '@/services/api/resources';
import { Resource, ResourceFilters } from '@/types/resource';
import { useToastStore } from '@/store/toastStore';

export const useResources = (filters?: ResourceFilters) => {
  return useInfiniteQuery({
    queryKey: ['resources', filters],
    queryFn: ({ pageParam = 1 }) => resourcesApi.getResources(pageParam, 20, filters),
    getNextPageParam: (lastPage) => {
      return lastPage.hasMore ? lastPage.page + 1 : undefined;
    },
    initialPageParam: 1,
  });
};

export const useResource = (id: string) => {
  return useQuery({
    queryKey: ['resource', id],
    queryFn: () => resourcesApi.getResource(id),
    enabled: !!id,
  });
};

export const useUploadFile = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: resourcesApi.uploadFile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addToast({
        type: 'success',
        message: 'File uploaded successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to upload file',
      });
    },
  });
};

export const useUploadUrl = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: resourcesApi.uploadUrl,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addToast({
        type: 'success',
        message: 'URL submitted for processing',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to process URL',
      });
    },
  });
};

export const useUploadStatus = (uploadId: string) => {
  return useQuery({
    queryKey: ['upload-status', uploadId],
    queryFn: () => resourcesApi.getUploadStatus(uploadId),
    enabled: !!uploadId,
    refetchInterval: (query) => {
      // Stop polling when complete or error
      const data = query.state.data;
      if (data?.status === 'complete' || data?.status === 'error') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });
};

export const useUpdateResource = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Resource> }) =>
      resourcesApi.updateResource(id, updates),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      queryClient.invalidateQueries({ queryKey: ['resource', data.id] });
      addToast({
        type: 'success',
        message: 'Resource updated successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to update resource',
      });
    },
  });
};

export const useDeleteResource = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: resourcesApi.deleteResource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addToast({
        type: 'success',
        message: 'Resource deleted successfully',
        action: {
          label: 'Undo',
          onClick: () => {
            // TODO: Implement undo functionality
          },
        },
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to delete resource',
      });
    },
  });
};

export const useBatchDeleteResources = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: resourcesApi.batchDeleteResources,
    onSuccess: (_, ids) => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addToast({
        type: 'success',
        message: `${ids.length} resources deleted successfully`,
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to delete resources',
      });
    },
  });
};

export const useFilterOptions = () => {
  return useQuery({
    queryKey: ['filter-options'],
    queryFn: resourcesApi.getFilterOptions,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
