// Neo Alexandria 2.0 Frontend - Citations Hooks
// Custom React hooks for citation network data

import { useQuery } from '@tanstack/react-query';
import { citationsApi } from '@/services/api';
import type { CitationGraphParams } from '@/services/api';

// Query keys for cache management
export const citationKeys = {
  all: ['citations'] as const,
  resource: (resourceId: string, direction?: 'inbound' | 'outbound') => 
    [...citationKeys.all, 'resource', resourceId, direction] as const,
  graph: (params: CitationGraphParams) => 
    [...citationKeys.all, 'graph', params] as const,
};

/**
 * Hook to fetch citations for a resource
 */
export function useCitations(resourceId: string, direction?: 'inbound' | 'outbound') {
  return useQuery({
    queryKey: citationKeys.resource(resourceId, direction),
    queryFn: () => citationsApi.getCitations(resourceId, direction),
    enabled: !!resourceId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to fetch citation network graph
 */
export function useCitationGraph(params: CitationGraphParams) {
  return useQuery({
    queryKey: citationKeys.graph(params),
    queryFn: () => citationsApi.getGraph(params),
    enabled: !!params.resource_ids && params.resource_ids.length > 0,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
