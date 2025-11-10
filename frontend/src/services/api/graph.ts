// Neo Alexandria 2.0 Frontend - Knowledge Graph API Service
// Knowledge graph visualization data

import apiClient from './client';
import type { GraphResponse } from '@/types/api';

export const graphApi = {
  /**
   * Get neighbors for a resource (knowledge graph visualization)
   */
  getNeighbors: async (resourceId: string, limit?: number): Promise<GraphResponse> => {
    const response = await apiClient.get<GraphResponse>(
      `/graph/resource/${resourceId}/neighbors`,
      { params: { limit } }
    );
    return response.data;
  },

  /**
   * Get global graph overview
   */
  getOverview: async (limit?: number, threshold?: number): Promise<GraphResponse> => {
    const response = await apiClient.get<GraphResponse>('/graph/overview', {
      params: { limit, vector_threshold: threshold },
    });
    return response.data;
  },
};
