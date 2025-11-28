import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taxonomyApi } from '@/services/api/taxonomy';
import { ClassificationFeedback } from '@/types/taxonomy';
import { useToastStore } from '@/store/toastStore';

export const useTaxonomy = () => {
  return useQuery({
    queryKey: ['taxonomy'],
    queryFn: taxonomyApi.getTaxonomy,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useTaxonomyNode = (nodeId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['taxonomy', 'node', nodeId],
    queryFn: () => taxonomyApi.getNode(nodeId),
    enabled,
    staleTime: 5 * 60 * 1000,
  });
};

export const useCreateNode = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ parentId, name }: { parentId: string | null; name: string }) =>
      taxonomyApi.createNode(parentId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy'] });
      addToast({
        type: 'success',
        message: 'Category created',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to create category',
      });
    },
  });
};

export const useUpdateNode = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ nodeId, name }: { nodeId: string; name: string }) =>
      taxonomyApi.updateNode(nodeId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy'] });
      addToast({
        type: 'success',
        message: 'Category updated',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to update category',
      });
    },
  });
};

export const useMoveNode = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ nodeId, newParentId }: { nodeId: string; newParentId: string | null }) =>
      taxonomyApi.moveNode(nodeId, newParentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy'] });
      addToast({
        type: 'success',
        message: 'Category moved',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to move category',
      });
    },
  });
};

export const useDeleteNode = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (nodeId: string) => taxonomyApi.deleteNode(nodeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy'] });
      addToast({
        type: 'success',
        message: 'Category deleted',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to delete category',
      });
    },
  });
};

export const useTaxonomyStats = () => {
  return useQuery({
    queryKey: ['taxonomy', 'stats'],
    queryFn: taxonomyApi.getStats,
    staleTime: 5 * 60 * 1000,
  });
};

export const useClassificationSuggestions = (resourceId?: string) => {
  return useQuery({
    queryKey: ['taxonomy', 'suggestions', resourceId],
    queryFn: () => taxonomyApi.getSuggestions(resourceId),
    staleTime: 2 * 60 * 1000,
  });
};

export const useAcceptSuggestion = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (suggestionId: string) => taxonomyApi.acceptSuggestion(suggestionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy', 'suggestions'] });
      queryClient.invalidateQueries({ queryKey: ['taxonomy', 'active-learning'] });
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addToast({
        type: 'success',
        message: 'Suggestion accepted',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to accept suggestion',
      });
    },
  });
};

export const useRejectSuggestion = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ suggestionId, correctCategory }: { suggestionId: string; correctCategory?: string }) =>
      taxonomyApi.rejectSuggestion(suggestionId, correctCategory),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy', 'suggestions'] });
      queryClient.invalidateQueries({ queryKey: ['taxonomy', 'active-learning'] });
      addToast({
        type: 'success',
        message: 'Suggestion rejected',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to reject suggestion',
      });
    },
  });
};

export const useActiveLearningQueue = () => {
  return useQuery({
    queryKey: ['taxonomy', 'active-learning'],
    queryFn: taxonomyApi.getActiveLearningQueue,
    staleTime: 2 * 60 * 1000,
  });
};

export const useSubmitFeedback = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (feedback: Omit<ClassificationFeedback, 'timestamp'>) =>
      taxonomyApi.submitFeedback(feedback),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy'] });
      addToast({
        type: 'success',
        message: 'Feedback submitted',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to submit feedback',
      });
    },
  });
};

export const useTrainModel = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: taxonomyApi.trainModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy', 'training'] });
      addToast({
        type: 'success',
        message: 'Model training started',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to start training',
      });
    },
  });
};

export const useTrainingStatus = () => {
  return useQuery({
    queryKey: ['taxonomy', 'training', 'status'],
    queryFn: taxonomyApi.getTrainingStatus,
    refetchInterval: (query) => {
      // Poll every 2 seconds while training
      const data = query.state.data;
      return data?.status === 'training' ? 2000 : false;
    },
    staleTime: 0,
  });
};

export const useClassificationMetrics = () => {
  return useQuery({
    queryKey: ['taxonomy', 'metrics'],
    queryFn: taxonomyApi.getMetrics,
    staleTime: 5 * 60 * 1000,
  });
};

export const useClassifyResource = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (resourceId: string) => taxonomyApi.classifyResource(resourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy', 'suggestions'] });
      addToast({
        type: 'success',
        message: 'Classification complete',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to classify resource',
      });
    },
  });
};

export const useBulkClassify = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (resourceIds: string[]) => taxonomyApi.bulkClassify(resourceIds),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['taxonomy', 'suggestions'] });
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addToast({
        type: 'success',
        message: `Classified ${variables.length} resources`,
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to bulk classify',
      });
    },
  });
};
