// Neo Alexandria 2.0 Frontend - Citations API Service
// Citation network data and visualization

import apiClient from './client';
import type { GraphResponse } from '@/types/api';

// Citation types
export interface Citation {
  id: string;
  source_resource_id: string;
  target_resource_id?: string;
  target_url: string;
  citation_type: 'reference' | 'dataset' | 'code' | 'general';
  context_snippet?: string;
  importance_score?: number;
}

export interface CitationResponse {
  inbound: Citation[];
  outbound: Citation[];
}

export interface CitationGraphParams {
  resource_ids?: string[];
  limit?: number;
  min_importance?: number;
}

export const citationsApi = {
  /**
   * Get citations for a resource
   */
  getCitations: async (resourceId: string, direction?: 'inbound' | 'outbound'): Promise<CitationResponse> => {
    const response = await apiClient.get<CitationResponse>(
      `/citations/resources/${resourceId}/citations`,
      { params: { direction } }
    );
    return response.data;
  },

  /**
   * Get citation network graph
   */
  getGraph: async (params: CitationGraphParams): Promise<GraphResponse> => {
    const response = await apiClient.get<GraphResponse>('/citations/graph/citations', { params });
    return response.data;
  },
};
