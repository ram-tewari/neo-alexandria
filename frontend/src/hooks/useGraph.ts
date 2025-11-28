import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { graphApi } from '@/services/api/graph';
import { GraphFilters, DiscoveryQuery } from '@/types/graph';
import { useToastStore } from '@/store/toastStore';

export const useGraph = (filters?: GraphFilters) => {
  return useQuery({
    queryKey: ['graph', filters],
    queryFn: () => graphApi.getGraph(filters),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useSubgraph = (nodeId: string, depth: number = 2, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['graph', 'subgraph', nodeId, depth],
    queryFn: () => graphApi.getSubgraph(nodeId, depth),
    enabled,
    staleTime: 5 * 60 * 1000,
  });
};

export const useNodeDetails = (nodeId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['graph', 'node', nodeId],
    queryFn: () => graphApi.getNodeDetails(nodeId),
    enabled,
    staleTime: 5 * 60 * 1000,
  });
};

export const useFindPaths = () => {
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (query: DiscoveryQuery) => graphApi.findPaths(query),
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to find paths',
      });
    },
  });
};

export const useGenerateHypotheses = () => {
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ sourceNodeId, targetNodeId }: { sourceNodeId: string; targetNodeId: string }) =>
      graphApi.generateHypotheses(sourceNodeId, targetNodeId),
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to generate hypotheses',
      });
    },
  });
};

export const useValidateHypothesis = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: ({ hypothesisId, valid }: { hypothesisId: string; valid: boolean }) =>
      graphApi.validateHypothesis(hypothesisId, valid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['graph', 'discovery'] });
      addToast({
        type: 'success',
        message: 'Hypothesis updated',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to validate hypothesis',
      });
    },
  });
};

export const useDiscoveryHistory = () => {
  return useQuery({
    queryKey: ['graph', 'discovery', 'history'],
    queryFn: graphApi.getDiscoveryHistory,
    staleTime: 5 * 60 * 1000,
  });
};

export const useCitationNetwork = (resourceId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['graph', 'citations', resourceId],
    queryFn: () => graphApi.getCitationNetwork(resourceId),
    enabled,
    staleTime: 10 * 60 * 1000,
  });
};

export const useCitationMetrics = (nodeId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['graph', 'citations', nodeId, 'metrics'],
    queryFn: () => graphApi.getCitationMetrics(nodeId),
    enabled,
    staleTime: 10 * 60 * 1000,
  });
};

export const useExportGraph = () => {
  const { addToast } = useToastStore();

  return useMutation({
    mutationFn: (format: 'json' | 'graphml' | 'png') => graphApi.exportGraph(format),
    onSuccess: (blob, format) => {
      // Download the file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge-graph.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      addToast({
        type: 'success',
        message: 'Graph exported successfully',
      });
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.response?.data?.message || 'Failed to export graph',
      });
    },
  });
};

export const useClusters = () => {
  return useQuery({
    queryKey: ['graph', 'clusters'],
    queryFn: graphApi.getClusters,
    staleTime: 10 * 60 * 1000,
  });
};
