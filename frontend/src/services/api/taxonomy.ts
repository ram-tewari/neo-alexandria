import { apiClient } from './client';
import {
  TaxonomyNode,
  ClassificationSuggestion,
  ActiveLearningItem,
  ClassificationFeedback,
  ModelTrainingStatus,
  TaxonomyStats,
  ClassificationMetrics,
} from '@/types/taxonomy';

export const taxonomyApi = {
  // Get taxonomy tree
  getTaxonomy: async (): Promise<TaxonomyNode[]> => {
    const response = await apiClient.get<TaxonomyNode[]>('/taxonomy');
    return response.data;
  },

  // Get node details
  getNode: async (nodeId: string): Promise<TaxonomyNode> => {
    const response = await apiClient.get<TaxonomyNode>(`/taxonomy/nodes/${nodeId}`);
    return response.data;
  },

  // Create node
  createNode: async (
    parentId: string | null,
    name: string
  ): Promise<TaxonomyNode> => {
    const response = await apiClient.post<TaxonomyNode>('/taxonomy/nodes', {
      parentId,
      name,
    });
    return response.data;
  },

  // Update node
  updateNode: async (nodeId: string, name: string): Promise<TaxonomyNode> => {
    const response = await apiClient.patch<TaxonomyNode>(
      `/taxonomy/nodes/${nodeId}`,
      { name }
    );
    return response.data;
  },

  // Move node
  moveNode: async (nodeId: string, newParentId: string | null): Promise<void> => {
    await apiClient.patch(`/taxonomy/nodes/${nodeId}/move`, { newParentId });
  },

  // Delete node
  deleteNode: async (nodeId: string): Promise<void> => {
    await apiClient.delete(`/taxonomy/nodes/${nodeId}`);
  },

  // Get taxonomy stats
  getStats: async (): Promise<TaxonomyStats> => {
    const response = await apiClient.get<TaxonomyStats>('/taxonomy/stats');
    return response.data;
  },

  // Get classification suggestions
  getSuggestions: async (
    resourceId?: string
  ): Promise<ClassificationSuggestion[]> => {
    const url = resourceId
      ? `/taxonomy/suggestions?resourceId=${resourceId}`
      : '/taxonomy/suggestions';
    const response = await apiClient.get<ClassificationSuggestion[]>(url);
    return response.data;
  },

  // Accept suggestion
  acceptSuggestion: async (suggestionId: string): Promise<void> => {
    await apiClient.post(`/taxonomy/suggestions/${suggestionId}/accept`);
  },

  // Reject suggestion
  rejectSuggestion: async (
    suggestionId: string,
    correctCategory?: string
  ): Promise<void> => {
    await apiClient.post(`/taxonomy/suggestions/${suggestionId}/reject`, {
      correctCategory,
    });
  },

  // Get active learning queue
  getActiveLearningQueue: async (): Promise<ActiveLearningItem[]> => {
    const response = await apiClient.get<ActiveLearningItem[]>(
      '/taxonomy/active-learning'
    );
    return response.data;
  },

  // Submit feedback
  submitFeedback: async (
    feedback: Omit<ClassificationFeedback, 'timestamp'>
  ): Promise<void> => {
    await apiClient.post('/taxonomy/feedback', {
      ...feedback,
      timestamp: new Date(),
    });
  },

  // Train model
  trainModel: async (): Promise<void> => {
    await apiClient.post('/taxonomy/train');
  },

  // Get training status
  getTrainingStatus: async (): Promise<ModelTrainingStatus> => {
    const response = await apiClient.get<ModelTrainingStatus>(
      '/taxonomy/training/status'
    );
    return response.data;
  },

  // Get classification metrics
  getMetrics: async (): Promise<ClassificationMetrics> => {
    const response = await apiClient.get<ClassificationMetrics>(
      '/taxonomy/metrics'
    );
    return response.data;
  },

  // Auto-classify resource
  classifyResource: async (resourceId: string): Promise<ClassificationSuggestion[]> => {
    const response = await apiClient.post<ClassificationSuggestion[]>(
      `/taxonomy/classify/${resourceId}`
    );
    return response.data;
  },

  // Bulk classify
  bulkClassify: async (resourceIds: string[]): Promise<void> => {
    await apiClient.post('/taxonomy/classify/bulk', { resourceIds });
  },
};
