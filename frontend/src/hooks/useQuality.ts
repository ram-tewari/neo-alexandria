import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { qualityApi } from '@/services/api/quality';
import { BulkEditOperation } from '@/types/quality';
import { useToastStore } from '@/store/toastStore';

export const useQualityMetrics = () => {
  return useQuery({
    queryKey: ['quality', 'metrics'],
    queryFn: qualityApi.getMetrics,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useQualityDistribution = () => {
  return useQuery({
    queryKey: ['quality', 'distribution'],
    queryFn: qualityApi.getDistribution,
    staleTime: 5 * 60 * 1000,
  });
};

export const useQualityTrends = (dimension?: string) => {
  return useQuery({
    queryKey: ['quality', 'trends', dimension],
    queryFn: () => qualityApi.getTrends(dimension),
    staleTime: 5 * 60 * 1000,
  });
};

export const useQualityOutliers = (threshold: number = 0.5) => {
  return useQuery({
    queryKey: ['quality', 'outliers', threshold],
    queryFn: () => qualityApi.getOutliers(threshold),
    staleTime: 5 * 60 * 1000,
  });
};

export const useRecalculateScores = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (resourceIds?: string[]) => qualityApi.recalculateScores(resourceIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quality'] });
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addToast({
        type: 'success',
        message: 'Quality scores recalculated',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to recalculate scores',
      });
    },
  });
};

export const useReviewQueue = (sortBy: 'priority' | 'date' = 'priority') => {
  return useQuery({
    queryKey: ['quality', 'review-queue', sortBy],
    queryFn: () => qualityApi.getReviewQueue(sortBy),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useUpdateReviewStatus = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({
      resourceId,
      status,
    }: {
      resourceId: string;
      status: 'pending' | 'in_progress' | 'completed';
    }) => qualityApi.updateReviewStatus(resourceId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quality', 'review-queue'] });
      addToast({
        type: 'success',
        message: 'Review status updated',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to update status',
      });
    },
  });
};

export const useBulkEdit = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({
      resourceIds,
      operations,
    }: {
      resourceIds: string[];
      operations: BulkEditOperation[];
    }) => qualityApi.bulkEdit(resourceIds, operations),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      queryClient.invalidateQueries({ queryKey: ['quality'] });
      addToast({
        type: 'success',
        message: `Updated ${variables.resourceIds.length} resources`,
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to bulk edit',
      });
    },
  });
};

export const useDuplicates = (threshold: number = 0.9) => {
  return useQuery({
    queryKey: ['quality', 'duplicates', threshold],
    queryFn: () => qualityApi.findDuplicates(threshold),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useMergeDuplicates = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({
      groupId,
      primaryId,
      duplicateIds,
    }: {
      groupId: string;
      primaryId: string;
      duplicateIds: string[];
    }) => qualityApi.mergeDuplicates(groupId, primaryId, duplicateIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quality', 'duplicates'] });
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addToast({
        type: 'success',
        message: 'Duplicates merged successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to merge duplicates',
      });
    },
  });
};

export const useSuggestions = (resourceId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['quality', 'suggestions', resourceId],
    queryFn: () => qualityApi.getSuggestions(resourceId),
    enabled,
    staleTime: 5 * 60 * 1000,
  });
};

export const useApplySuggestion = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ resourceId, suggestionId }: { resourceId: string; suggestionId: string }) =>
      qualityApi.applySuggestion(resourceId, suggestionId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['resources', variables.resourceId] });
      queryClient.invalidateQueries({ queryKey: ['quality'] });
      addToast({
        type: 'success',
        message: 'Suggestion applied',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to apply suggestion',
      });
    },
  });
};
