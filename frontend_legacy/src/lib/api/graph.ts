/**
 * Graph API Client
 * Provides typed methods for knowledge graph operations
 */

import { GraphNeighborsResponse } from './types';
import { apiRequest } from './apiUtils';

/**
 * Graph API Client
 */
export const graphApi = {
  /**
   * Get neighboring resources in the knowledge graph
   */
  async getNeighbors(
    resourceId: string,
    limit: number = 10
  ): Promise<GraphNeighborsResponse> {
    return apiRequest<GraphNeighborsResponse>(
      `/graph/resource/${resourceId}/neighbors?limit=${limit}`
    );
  },
};

export default graphApi;
