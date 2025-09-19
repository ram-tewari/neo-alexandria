// Neo Alexandria 2.0 Frontend - API Hooks
// Custom React hooks for API integration with React Query

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { apiService, ApiService, pollResourceStatus } from '@/services/api';
import { useAppStore } from '@/store';
import type {
  UpdateResourceRequest,
  SearchQuery,
  ResourceQueryParams,
  ProcessingResource,
} from '@/types/api';

// Query keys for consistent cache management
export const queryKeys = {
  resources: ['resources'] as const,
  resource: (id: string) => ['resource', id] as const,
  resourceStatus: (id: string) => ['resource-status', id] as const,
  search: (query: SearchQuery) => ['search', query] as const,
  recommendations: (limit: number) => ['recommendations', limit] as const,
  graphNeighbors: (id: string, limit: number) => ['graph-neighbors', id, limit] as const,
  graphOverview: (limit: number, threshold: number) => ['graph-overview', limit, threshold] as const,
  classificationTree: ['classification-tree'] as const,
  subjects: (query: string) => ['subjects', query] as const,
  reviewQueue: (threshold?: number, unreadOnly?: boolean) => ['review-queue', threshold, unreadOnly] as const,
  qualityAnalysis: (id: string) => ['quality-analysis', id] as const,
};

// Resources API Hooks

export function useResources(params: ResourceQueryParams = {}) {
  return useQuery({
    queryKey: [
      ...queryKeys.resources, 
      params.q,
      params.sort_by,
      params.sort_dir,
      params.limit,
      params.offset,
      params.classification_code,
      params.type,
      params.language,
      params.read_status,
      params.min_quality,
      params.created_from,
      params.created_to
    ],
    queryFn: () => apiService.listResources(params),
  });
}

export function useResource(resourceId: string) {
  return useQuery({
    queryKey: queryKeys.resource(resourceId),
    queryFn: () => apiService.getResource(resourceId),
    enabled: !!resourceId,
  });
}

export function useCreateResource() {
  const queryClient = useQueryClient();
  const addNotification = useAppStore(state => state.addNotification);
  const addProcessingResource = useAppStore(state => state.addProcessingResource);
  const updateProcessingResource = useAppStore(state => state.updateProcessingResource);
  const addLibraryResource = useAppStore(state => state.addLibraryResource);

  return useMutation({
    mutationFn: (request) => apiService.ingestResource(request),
    onSuccess: async (data, variables) => {
      // Add to processing queue
      const processingResource: ProcessingResource = {
        id: data.id,
        url: variables.url,
        title: variables.title || variables.url,
        status: 'pending',
        startedAt: new Date(),
      };
      addProcessingResource(processingResource);

      // Start polling for status
      try {
        const finalStatus = await pollResourceStatus(
          data.id,
          (status) => {
            updateProcessingResource(data.id, {
              status: status.ingestion_status,
              error: status.ingestion_error || undefined,
            });
          }
        );

        if (finalStatus.ingestion_status === 'completed') {
          // Fetch the complete resource and add to library
          const resource = await apiService.getResource(data.id);
          addLibraryResource(resource);
          
          addNotification({
            type: 'success',
            title: 'Resource Added',
            message: `Successfully processed: ${resource.title}`,
          });
        } else {
          addNotification({
            type: 'error',
            title: 'Processing Failed',
            message: finalStatus.ingestion_error || 'Unknown error occurred',
          });
        }
      } catch (error) {
        addNotification({
          type: 'error',
          title: 'Processing Error',
          message: ApiService.handleApiError(error),
        });
      }

      // Invalidate resources list
      queryClient.invalidateQueries({ queryKey: queryKeys.resources });
    },
    onError: (error) => {
      addNotification({
        type: 'error',
        title: 'Ingestion Failed',
        message: ApiService.handleApiError(error),
      });
    },
  });
}

export function useUpdateResource() {
  const queryClient = useQueryClient();
  const addNotification = useAppStore(state => state.addNotification);
  const updateResource = useAppStore(state => state.updateLibraryResource);

  return useMutation({
    mutationFn: ({ resourceId, updates }: { resourceId: string; updates: UpdateResourceRequest }) =>
      apiService.updateResource(resourceId, updates),
    onSuccess: (data) => {
      updateResource(data.id, data);
      addNotification({
        type: 'success',
        title: 'Resource Updated',
        message: 'Resource has been successfully updated',
      });
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.resource(data.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.resources });
    },
    onError: (error) => {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: ApiService.handleApiError(error),
      });
    },
  });
}

export function useDeleteResource() {
  const queryClient = useQueryClient();
  const addNotification = useAppStore(state => state.addNotification);
  const removeResource = useAppStore(state => state.removeLibraryResource);

  return useMutation({
    mutationFn: (resourceId) => apiService.deleteResource(resourceId),
    onSuccess: (_, resourceId) => {
      removeResource(resourceId);
      addNotification({
        type: 'success',
        title: 'Resource Deleted',
        message: 'Resource has been successfully deleted',
      });
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.resources });
    },
    onError: (error) => {
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: ApiService.handleApiError(error),
      });
    },
  });
}

// Search API Hooks

export function useSearch() {
  const searchQuery = useAppStore(state => state.search.query);
  const searchFilters = useAppStore(state => state.search.filters);
  const hybridWeight = useAppStore(state => state.search.hybridWeight);
  
  const query: SearchQuery = {
    text: searchQuery || undefined,
    filters: searchFilters,
    hybrid_weight: hybridWeight,
    limit: 25,
    sort_by: 'relevance',
    sort_dir: 'desc',
  };

  return useQuery({
    queryKey: [
      'search',
      searchQuery,
      searchFilters,
      hybridWeight,
      25, // limit
      'relevance', // sort_by
      'desc' // sort_dir
    ],
    queryFn: () => apiService.search(query),
    enabled: !!searchQuery || Object.keys(searchFilters).length > 0,
  });
}

// Recommendations API Hooks

export function useRecommendations(limit: number = 10) {
  return useQuery({
    queryKey: queryKeys.recommendations(limit),
    queryFn: () => apiService.getRecommendations(limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Knowledge Graph API Hooks

export function useResourceNeighbors(resourceId: string, limit: number = 7) {
  return useQuery({
    queryKey: queryKeys.graphNeighbors(resourceId, limit),
    queryFn: () => apiService.getResourceNeighbors(resourceId, limit),
    enabled: !!resourceId,
  });
}

export function useGraphOverview(limit: number = 50, threshold: number = 0.85) {
  return useQuery({
    queryKey: queryKeys.graphOverview(limit, threshold),
    queryFn: () => apiService.getGraphOverview(limit, threshold),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Authority and Classification API Hooks

export function useClassificationTree() {
  return useQuery({
    queryKey: queryKeys.classificationTree,
    queryFn: () => apiService.getClassificationTree(),
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}

export function useSubjectSuggestions(query: string) {
  return useQuery({
    queryKey: queryKeys.subjects(query),
    queryFn: () => apiService.getSubjectSuggestions(query),
    enabled: query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Curation API Hooks

export function useReviewQueue(threshold?: number, includeUnreadOnly: boolean = false) {
  return useQuery({
    queryKey: queryKeys.reviewQueue(threshold, includeUnreadOnly),
    queryFn: () => apiService.getReviewQueue(threshold, includeUnreadOnly),
  });
}

export function useQualityAnalysis(resourceId: string) {
  return useQuery({
    queryKey: queryKeys.qualityAnalysis(resourceId),
    queryFn: () => apiService.getQualityAnalysis(resourceId),
    enabled: !!resourceId,
  });
}

export function useBatchUpdate() {
  const queryClient = useQueryClient();
  const addNotification = useAppStore(state => state.addNotification);

  return useMutation({
    mutationFn: (request) => apiService.batchUpdate(request),
    onSuccess: (data) => {
      addNotification({
        type: 'success',
        title: 'Batch Update Complete',
        message: `Successfully updated ${data.updated_count} resources`,
      });
      
      // Invalidate resources list
      queryClient.invalidateQueries({ queryKey: queryKeys.resources });
    },
    onError: (error) => {
      addNotification({
        type: 'error',
        title: 'Batch Update Failed',
        message: ApiService.handleApiError(error),
      });
    },
  });
}

// Custom hook for managing URL ingestion
export function useUrlIngestion() {
  const createResource = useCreateResource();
  
  const ingestUrl = useCallback(async (url: string, title?: string) => {
    if (!url.trim()) {
      throw new Error('URL is required');
    }
    
    // Basic URL validation
    try {
      new URL(url);
    } catch {
      throw new Error('Please enter a valid URL');
    }
    
    return createResource.mutateAsync({ url, title });
  }, [createResource]);
  
  return {
    ingestUrl,
    isLoading: createResource.isPending,
    error: createResource.error,
  };
}

// Custom hook for search management
export function useSearchManager() {
  const setQuery = useAppStore(state => state.setSearchQuery);
  const setFilters = useAppStore(state => state.setSearchFilters);
  const setLoading = useAppStore(state => state.setSearchLoading);
  const setError = useAppStore(state => state.setSearchError);
  const setResults = useAppStore(state => state.setSearchResults);
  const clearResults = useAppStore(state => state.clearSearchResults);
  
  const performSearch = useCallback(async (query: SearchQuery) => {
    setLoading(true);
    setError(null);
    
    try {
      const results = await apiService.search(query);
      setResults(results);
    } catch (error) {
      setError(ApiService.handleApiError(error));
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError, setResults]);
  
  return {
    performSearch,
    setQuery,
    setFilters,
    clearResults,
  };
}

// Health check hook
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiService.healthCheck(),
    refetchInterval: 30000, // Check every 30 seconds
    retry: false,
  });
}
