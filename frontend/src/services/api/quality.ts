import { apiClient } from './client';
import {
  QualityMetrics,
  QualityDistribution,
  QualityTrend,
  QualityOutlier,
  ReviewQueueItem,
  BulkEditOperation,
  DuplicateGroup,
} from '@/types/quality';

export const qualityApi = {
  // Get quality metrics
  getMetrics: async (): Promise<QualityMetrics> => {
    const response = await apiClient.get<QualityMetrics>('/quality/metrics');
    return response.data;
  },

  // Get quality distribution
  getDistribution: async (): Promise<QualityDistribution> => {
    const response = await apiClient.get<QualityDistribution>('/quality/distribution');
    return response.data;
  },

  // Get quality trends
  getTrends: async (dimension?: string): Promise<QualityTrend[]> => {
    const params = dimension ? `?dimension=${dimension}` : '';
    const response = await apiClient.get<QualityTrend[]>(`/quality/trends${params}`);
    return response.data;
  },

  // Get outliers
  getOutliers: async (threshold: number = 0.5): Promise<QualityOutlier[]> => {
    const response = await apiClient.get<QualityOutlier[]>(
      `/quality/outliers?threshold=${threshold}`
    );
    return response.data;
  },

  // Recalculate quality scores
  recalculateScores: async (resourceIds?: string[]): Promise<void> => {
    await apiClient.post('/quality/recalculate', { resourceIds });
  },

  // Get review queue
  getReviewQueue: async (
    sortBy: 'priority' | 'date' = 'priority'
  ): Promise<ReviewQueueItem[]> => {
    const response = await apiClient.get<ReviewQueueItem[]>(
      `/quality/review-queue?sortBy=${sortBy}`
    );
    return response.data;
  },

  // Update review status
  updateReviewStatus: async (
    resourceId: string,
    status: 'pending' | 'in_progress' | 'completed'
  ): Promise<ReviewQueueItem> => {
    const response = await apiClient.patch<ReviewQueueItem>(
      `/quality/review-queue/${resourceId}`,
      { status }
    );
    return response.data;
  },

  // Bulk edit resources
  bulkEdit: async (
    resourceIds: string[],
    operations: BulkEditOperation[]
  ): Promise<void> => {
    await apiClient.post('/quality/bulk-edit', { resourceIds, operations });
  },

  // Find duplicates
  findDuplicates: async (threshold: number = 0.9): Promise<DuplicateGroup[]> => {
    const response = await apiClient.get<DuplicateGroup[]>(
      `/quality/duplicates?threshold=${threshold}`
    );
    return response.data;
  },

  // Merge duplicates
  mergeDuplicates: async (
    groupId: string,
    primaryId: string,
    duplicateIds: string[]
  ): Promise<void> => {
    await apiClient.post('/quality/duplicates/merge', {
      groupId,
      primaryId,
      duplicateIds,
    });
  },

  // Get improvement suggestions
  getSuggestions: async (resourceId: string): Promise<string[]> => {
    const response = await apiClient.get<string[]>(
      `/quality/suggestions/${resourceId}`
    );
    return response.data;
  },

  // Apply suggestion
  applySuggestion: async (resourceId: string, suggestionId: string): Promise<void> => {
    await apiClient.post(`/quality/suggestions/${resourceId}/apply`, {
      suggestionId,
    });
  },
};
