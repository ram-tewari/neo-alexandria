import { apiClient } from './client';
import { Recommendation, UserPreferences, RecommendationMetrics, RecommendationFeedback } from '@/types/recommendation';

export const recommendationsApi = {
  // Get personalized recommendations
  getRecommendations: async (
    category?: 'fresh' | 'similar' | 'hidden',
    limit: number = 20
  ): Promise<Recommendation[]> => {
    const params = new URLSearchParams({
      limit: limit.toString(),
    });
    
    if (category) {
      params.append('category', category);
    }

    const response = await apiClient.get<Recommendation[]>(
      `/recommendations?${params.toString()}`
    );
    return response.data;
  },

  // Get user preferences
  getUserPreferences: async (): Promise<UserPreferences> => {
    const response = await apiClient.get<UserPreferences>('/user/preferences');
    return response.data;
  },

  // Update user preferences
  updateUserPreferences: async (preferences: Partial<UserPreferences>): Promise<UserPreferences> => {
    const response = await apiClient.patch<UserPreferences>('/user/preferences', preferences);
    return response.data;
  },

  // Submit recommendation feedback
  submitFeedback: async (feedback: Omit<RecommendationFeedback, 'timestamp'>): Promise<void> => {
    await apiClient.post('/recommendations/feedback', {
      ...feedback,
      timestamp: new Date(),
    });
  },

  // Get recommendation metrics
  getMetrics: async (): Promise<RecommendationMetrics> => {
    const response = await apiClient.get<RecommendationMetrics>('/recommendations/metrics');
    return response.data;
  },

  // Refresh recommendations (trigger re-computation)
  refreshRecommendations: async (): Promise<void> => {
    await apiClient.post('/recommendations/refresh');
  },
};
