import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { collectionsApi } from '@/services/api/collections';
import { Collection, CollectionRule } from '@/types/collection';
import { useToastStore } from '@/store/toastStore';

export const useCollections = () => {
  return useQuery({
    queryKey: ['collections'],
    queryFn: collectionsApi.getCollections,
  });
};

export const useCollection = (id: string) => {
  return useQuery({
    queryKey: ['collection', id],
    queryFn: () => collectionsApi.getCollection(id),
    enabled: !!id,
  });
};

export const useCreateCollection = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: collectionsApi.createCollection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] });
      addToast({
        type: 'success',
        message: 'Collection created successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to create collection',
      });
    },
  });
};

export const useUpdateCollection = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Collection> }) =>
      collectionsApi.updateCollection(id, updates),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['collections'] });
      queryClient.invalidateQueries({ queryKey: ['collection', data.id] });
      addToast({
        type: 'success',
        message: 'Collection updated successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to update collection',
      });
    },
  });
};

export const useDeleteCollection = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: collectionsApi.deleteCollection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] });
      addToast({
        type: 'success',
        message: 'Collection deleted successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to delete collection',
      });
    },
  });
};

export const useEvaluateRules = (rules: CollectionRule[]) => {
  return useQuery({
    queryKey: ['evaluate-rules', rules],
    queryFn: () => collectionsApi.evaluateRules(rules),
    enabled: rules.length > 0,
  });
};
