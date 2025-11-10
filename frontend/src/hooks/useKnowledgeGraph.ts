// Neo Alexandria 2.0 Frontend - Knowledge Graph Hooks
// Custom React hooks for knowledge graph data

import { useQuery } from '@tanstack/react-query';
import { graphApi } from '@/services/api';

// Query keys for cache management
export const graphKeys = {
  all: ['graph'] as const,
  neighbors: (resourceId: string, limit?: number) => 
    [...graphKeys.all, 'neighbors', resourceId, limit] as const,
  overview: (limit?: number, threshold?: number) => 
    [...graphKeys.all, 'overview', limit, threshold] as const,
};

/**
 * Hook to fetch knowledge graph neighbors for a resource
 */
export function useKnowledgeGraph(resourceId: string, limit?: number) {
  return useQuery({
    queryKey: graphKeys.neighbors(resourceId, limit),
    queryFn: () => graphApi.getNeighbors(resourceId, limit),
    enabled: !!resourceId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to fetch global knowledge graph overview
 */
export function useGraphOverview(limit: number = 50, threshold: number = 0.85) {
  return useQuery({
    queryKey: graphKeys.overview(limit, threshold),
    queryFn: () => graphApi.getOverview(limit, threshold),
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
}
