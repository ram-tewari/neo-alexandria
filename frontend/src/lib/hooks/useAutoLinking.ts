import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/core/api/client';
import type { Resource } from '@/types/library';

interface RelatedResource {
  resource: Resource;
  similarity: number;
  relationship_type: 'citation' | 'semantic' | 'code_reference';
}

interface AutoLinkingResult {
  relatedCode: RelatedResource[];
  relatedPapers: RelatedResource[];
}

/**
 * Custom hook for auto-linking related resources
 * Fetches related code files and papers based on embeddings and citations
 */
export function useAutoLinking(resourceId: string) {
  // Fetch related code files
  const relatedCodeQuery = useQuery({
    queryKey: ['related-code', resourceId],
    queryFn: async () => {
      const response = await apiClient.get<RelatedResource[]>(
        `/resources/${resourceId}/related-code`,
        { params: { limit: 10 } }
      );
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!resourceId,
  });

  // Fetch related papers
  const relatedPapersQuery = useQuery({
    queryKey: ['related-papers', resourceId],
    queryFn: async () => {
      const response = await apiClient.get<RelatedResource[]>(
        `/resources/${resourceId}/related-papers`,
        { params: { limit: 10 } }
      );
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!resourceId,
  });

  // Refresh suggestions
  const refreshSuggestions = async () => {
    await Promise.all([
      relatedCodeQuery.refetch(),
      relatedPapersQuery.refetch(),
    ]);
  };

  // Calculate similarity scores
  const getTopRelatedCode = (limit: number = 5) => {
    return (relatedCodeQuery.data || [])
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit);
  };

  const getTopRelatedPapers = (limit: number = 5) => {
    return (relatedPapersQuery.data || [])
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit);
  };

  return {
    // Data
    relatedCode: relatedCodeQuery.data || [],
    relatedPapers: relatedPapersQuery.data || [],

    // Loading states
    isLoadingCode: relatedCodeQuery.isLoading,
    isLoadingPapers: relatedPapersQuery.isLoading,
    isLoading: relatedCodeQuery.isLoading || relatedPapersQuery.isLoading,

    // Error states
    codeError: relatedCodeQuery.error,
    papersError: relatedPapersQuery.error,
    hasError: !!relatedCodeQuery.error || !!relatedPapersQuery.error,

    // Derived states
    hasRelatedCode: (relatedCodeQuery.data?.length || 0) > 0,
    hasRelatedPapers: (relatedPapersQuery.data?.length || 0) > 0,
    hasAnySuggestions: (relatedCodeQuery.data?.length || 0) > 0 || (relatedPapersQuery.data?.length || 0) > 0,

    // Actions
    refreshSuggestions,
    getTopRelatedCode,
    getTopRelatedPapers,
  };
}
