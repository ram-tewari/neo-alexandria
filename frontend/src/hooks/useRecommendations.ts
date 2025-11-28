import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recommendationsApi } from '@/services/api/recommendations';
import { UserPreferences, RecommendationFeedback } from '@/types/recommendation';
import { useToastStore } from '@/store/toastStore';

export const useRecommendations = (category?: 'fresh' | 'similar' | 'hidden') => {
  return useQuery({
    queryKey: ['recommendations', category],
    queryFn: () => recommendationsApi.getRecommendations(category),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useUserPreferences = () => {
  return useQuery({
    queryKey: ['user-preferences'],
    queryFn: recommendationsApi.getUserPreferences,
  });
};

export const useUpdatePreferences = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (preferences: Partial<UserPreferences>) =>
      recommendationsApi.updateUserPreferences(preferences),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-preferences'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      addToast({
        type: 'success',
        message: 'Preferences updated successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to update preferences',
      });
    },
  });
};

export const useSubmitFeedback = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (feedback: Omit<RecommendationFeedback, 'timestamp'>) =>
      recommendationsApi.submitFeedback(feedback),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['recommendation-metrics'] });
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

export const useRecommendationMetrics = () => {
  return useQuery({
    queryKey: ['recommendation-metrics'],
    queryFn: recommendationsApi.getMetrics,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useRefreshRecommendations = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: recommendationsApi.refreshRecommendations,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      addToast({
        type: 'success',
        message: 'Recommendations refreshed',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to refresh recommendations',
      });
    },
  });
};
