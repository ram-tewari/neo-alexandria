import { apiClient } from './client';
import {
  GraphData,
  GraphFilters,
  DiscoveryQuery,
  DiscoveryPath,
  Hypothesis,
  CitationMetrics,
} from '@/types/graph';

export const graphApi = {
  // Get full knowledge graph
  getGraph: async (filters?: GraphFilters): Promise<GraphData> => {
    const params = new URLSearchParams();
    
    if (filters?.nodeTypes) {
      filters.nodeTypes.forEach(type => params.append('nodeType', type));
    }
    if (filters?.edgeTypes) {
      filters.edgeTypes.forEach(type => params.append('edgeType', type));
    }
    if (filters?.clusters) {
      filters.clusters.forEach(cluster => params.append('cluster', cluster));
    }
    if (filters?.minWeight !== undefined) {
      params.append('minWeight', filters.minWeight.toString());
    }

    const response = await apiClient.get<GraphData>(
      `/graph?${params.toString()}`
    );
    return response.data;
  },

  // Get subgraph around a node
  getSubgraph: async (nodeId: string, depth: number = 2): Promise<GraphData> => {
    const response = await apiClient.get<GraphData>(
      `/graph/subgraph/${nodeId}?depth=${depth}`
    );
    return response.data;
  },

  // Get node details
  getNodeDetails: async (nodeId: string): Promise<any> => {
    const response = await apiClient.get(`/graph/nodes/${nodeId}`);
    return response.data;
  },

  // Open discovery - find paths between nodes
  findPaths: async (query: DiscoveryQuery): Promise<DiscoveryPath[]> => {
    const response = await apiClient.post<DiscoveryPath[]>(
      '/graph/discovery/paths',
      query
    );
    return response.data;
  },

  // Generate hypotheses
  generateHypotheses: async (
    sourceNodeId: string,
    targetNodeId: string
  ): Promise<Hypothesis[]> => {
    const response = await apiClient.post<Hypothesis[]>(
      '/graph/discovery/hypotheses',
      { sourceNodeId, targetNodeId }
    );
    return response.data;
  },

  // Validate hypothesis
  validateHypothesis: async (
    hypothesisId: string,
    valid: boolean
  ): Promise<Hypothesis> => {
    const response = await apiClient.patch<Hypothesis>(
      `/graph/discovery/hypotheses/${hypothesisId}`,
      { status: valid ? 'validated' : 'rejected' }
    );
    return response.data;
  },

  // Get discovery history
  getDiscoveryHistory: async (): Promise<any[]> => {
    const response = await apiClient.get('/graph/discovery/history');
    return response.data;
  },

  // Get citation network
  getCitationNetwork: async (resourceId: string): Promise<GraphData> => {
    const response = await apiClient.get<GraphData>(
      `/graph/citations/${resourceId}`
    );
    return response.data;
  },

  // Get citation metrics
  getCitationMetrics: async (nodeId: string): Promise<CitationMetrics> => {
    const response = await apiClient.get<CitationMetrics>(
      `/graph/citations/${nodeId}/metrics`
    );
    return response.data;
  },

  // Export graph
  exportGraph: async (format: 'json' | 'graphml' | 'png'): Promise<Blob> => {
    const response = await apiClient.get(
      `/graph/export?format=${format}`,
      { responseType: 'blob' }
    );
    return response.data;
  },

  // Get clusters
  getClusters: async (): Promise<{ id: string; label: string; nodeIds: string[] }[]> => {
    const response = await apiClient.get('/graph/clusters');
    return response.data;
  },
};
