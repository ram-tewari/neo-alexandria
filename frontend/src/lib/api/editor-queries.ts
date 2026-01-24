/**
 * TanStack Query Hooks for Editor API
 * 
 * Provides React Query hooks with automatic caching, prefetching, and request deduplication.
 * These hooks replace manual caching in Zustand stores with TanStack Query's built-in caching.
 */

import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  type UseQueryOptions,
  type UseMutationOptions,
} from '@tanstack/react-query';
import { 
  editorApi, 
  editorQueryKeys, 
  editorCacheConfig,
  type Annotation,
  type AnnotationCreate,
  type AnnotationUpdate,
  type AnnotationSearchParams,
  type SemanticChunk,
  type QualityDetails,
  type GraphConnection,
} from './editor';

// ============================================================================
// Annotation Queries
// ============================================================================

/**
 * Fetch all annotations for a resource
 * 
 * Features:
 * - Automatic caching (5 minutes stale time, 10 minutes cache time)
 * - Request deduplication (multiple calls with same resourceId share one request)
 * - Automatic refetching on window focus
 * - Background refetching when stale
 */
export function useAnnotations(
  resourceId: string,
  options?: Omit<UseQueryOptions<Annotation[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: editorQueryKeys.annotations(resourceId),
    queryFn: async () => {
      const response = await editorApi.getAnnotations(resourceId);
      return response.data;
    },
    staleTime: editorCacheConfig.annotations.staleTime,
    gcTime: editorCacheConfig.annotations.cacheTime,
    ...options,
  });
}

/**
 * Fetch a single annotation by ID
 */
export function useAnnotation(
  annotationId: string,
  options?: Omit<UseQueryOptions<Annotation, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: editorQueryKeys.annotation(annotationId),
    queryFn: async () => {
      const response = await editorApi.getAnnotation(annotationId);
      return response.data;
    },
    staleTime: editorCacheConfig.annotations.staleTime,
    gcTime: editorCacheConfig.annotations.cacheTime,
    ...options,
  });
}

/**
 * Search annotations with full-text search
 */
export function useAnnotationSearch(
  params: AnnotationSearchParams,
  options?: Omit<UseQueryOptions<Annotation[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: editorQueryKeys.annotationSearch(params),
    queryFn: async () => {
      const response = await editorApi.searchAnnotationsFulltext(params);
      return response.data;
    },
    staleTime: editorCacheConfig.annotations.staleTime,
    gcTime: editorCacheConfig.annotations.cacheTime,
    enabled: !!params.query, // Only run if query is provided
    ...options,
  });
}

/**
 * Create annotation mutation with optimistic updates
 */
export function useCreateAnnotation(
  options?: UseMutationOptions<
    Annotation,
    Error,
    { resourceId: string; data: AnnotationCreate }
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ resourceId, data }) => {
      const response = await editorApi.createAnnotation(resourceId, data);
      return response.data;
    },
    onMutate: async ({ resourceId, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ 
        queryKey: editorQueryKeys.annotations(resourceId) 
      });

      // Snapshot previous value
      const previousAnnotations = queryClient.getQueryData<Annotation[]>(
        editorQueryKeys.annotations(resourceId)
      );

      // Optimistically update cache
      const optimisticAnnotation: Annotation = {
        id: `temp-${Date.now()}`,
        resource_id: resourceId,
        user_id: 'current-user',
        ...data,
        color: data.color || '#3b82f6',
        is_shared: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      queryClient.setQueryData<Annotation[]>(
        editorQueryKeys.annotations(resourceId),
        (old) => [...(old || []), optimisticAnnotation]
      );

      return { previousAnnotations };
    },
    onError: (err, { resourceId }, context) => {
      // Rollback on error
      if (context?.previousAnnotations) {
        queryClient.setQueryData(
          editorQueryKeys.annotations(resourceId),
          context.previousAnnotations
        );
      }
    },
    onSuccess: (newAnnotation, { resourceId }) => {
      // Update cache with real annotation
      queryClient.setQueryData<Annotation[]>(
        editorQueryKeys.annotations(resourceId),
        (old) => {
          if (!old) return [newAnnotation];
          // Replace optimistic annotation with real one
          return old.map((a) => 
            a.id.startsWith('temp-') ? newAnnotation : a
          );
        }
      );
    },
    ...options,
  });
}

/**
 * Update annotation mutation with optimistic updates
 */
export function useUpdateAnnotation(
  options?: UseMutationOptions<
    Annotation,
    Error,
    { annotationId: string; data: AnnotationUpdate }
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ annotationId, data }) => {
      const response = await editorApi.updateAnnotation(annotationId, data);
      return response.data;
    },
    onMutate: async ({ annotationId, data }) => {
      // Find the annotation in cache to get resourceId
      const queries = queryClient.getQueriesData<Annotation[]>({ 
        queryKey: ['annotations'] 
      });
      
      let resourceId: string | null = null;
      let previousAnnotations: Annotation[] | undefined;

      for (const [queryKey, annotations] of queries) {
        if (annotations) {
          const annotation = annotations.find((a) => a.id === annotationId);
          if (annotation) {
            resourceId = annotation.resource_id;
            previousAnnotations = annotations;
            
            // Cancel outgoing refetches
            await queryClient.cancelQueries({ queryKey });

            // Optimistically update
            queryClient.setQueryData<Annotation[]>(
              queryKey,
              annotations.map((a) =>
                a.id === annotationId
                  ? { ...a, ...data, updated_at: new Date().toISOString() }
                  : a
              )
            );
            break;
          }
        }
      }

      return { resourceId, previousAnnotations, queryKey: queries[0]?.[0] };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.queryKey && context?.previousAnnotations) {
        queryClient.setQueryData(context.queryKey, context.previousAnnotations);
      }
    },
    onSuccess: (updatedAnnotation, variables, context) => {
      // Update cache with server response
      if (context?.queryKey) {
        queryClient.setQueryData<Annotation[]>(
          context.queryKey,
          (old) => old?.map((a) => 
            a.id === updatedAnnotation.id ? updatedAnnotation : a
          )
        );
      }
    },
    ...options,
  });
}

/**
 * Delete annotation mutation with optimistic updates
 */
export function useDeleteAnnotation(
  options?: UseMutationOptions<void, Error, string>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (annotationId: string) => {
      await editorApi.deleteAnnotation(annotationId);
    },
    onMutate: async (annotationId) => {
      // Find the annotation in cache
      const queries = queryClient.getQueriesData<Annotation[]>({ 
        queryKey: ['annotations'] 
      });
      
      let previousAnnotations: Annotation[] | undefined;
      let queryKey: unknown[] | undefined;

      for (const [key, annotations] of queries) {
        if (annotations?.some((a) => a.id === annotationId)) {
          queryKey = key as unknown[];
          previousAnnotations = annotations;
          
          // Cancel outgoing refetches
          await queryClient.cancelQueries({ queryKey: key });

          // Optimistically remove
          queryClient.setQueryData<Annotation[]>(
            key,
            annotations.filter((a) => a.id !== annotationId)
          );
          break;
        }
      }

      return { previousAnnotations, queryKey };
    },
    onError: (err, annotationId, context) => {
      // Rollback on error
      if (context?.queryKey && context?.previousAnnotations) {
        queryClient.setQueryData(context.queryKey, context.previousAnnotations);
      }
    },
    ...options,
  });
}

// ============================================================================
// Chunk Queries
// ============================================================================

/**
 * Fetch all semantic chunks for a resource
 * 
 * Features:
 * - Automatic caching (10 minutes stale time, 30 minutes cache time)
 * - Request deduplication
 * - Longer cache time since chunks change less frequently
 */
export function useChunks(
  resourceId: string,
  options?: Omit<UseQueryOptions<SemanticChunk[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: editorQueryKeys.chunks(resourceId),
    queryFn: async () => {
      const response = await editorApi.getChunks(resourceId);
      return response.data;
    },
    staleTime: editorCacheConfig.chunks.staleTime,
    gcTime: editorCacheConfig.chunks.cacheTime,
    ...options,
  });
}

/**
 * Fetch a single chunk by ID
 */
export function useChunk(
  chunkId: string,
  options?: Omit<UseQueryOptions<SemanticChunk, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: editorQueryKeys.chunk(chunkId),
    queryFn: async () => {
      const response = await editorApi.getChunk(chunkId);
      return response.data;
    },
    staleTime: editorCacheConfig.chunks.staleTime,
    gcTime: editorCacheConfig.chunks.cacheTime,
    ...options,
  });
}

/**
 * Prefetch chunks for a resource
 * 
 * Use this to prefetch chunks before they're needed (e.g., when hovering over a file)
 */
export function usePrefetchChunks() {
  const queryClient = useQueryClient();

  return (resourceId: string) => {
    queryClient.prefetchQuery({
      queryKey: editorQueryKeys.chunks(resourceId),
      queryFn: async () => {
        const response = await editorApi.getChunks(resourceId);
        return response.data;
      },
      staleTime: editorCacheConfig.chunks.staleTime,
    });
  };
}

// ============================================================================
// Quality Queries
// ============================================================================

/**
 * Fetch quality details for a resource
 * 
 * Features:
 * - Automatic caching (15 minutes stale time, 30 minutes cache time)
 * - Request deduplication
 * - Longest cache time since quality scores change infrequently
 */
export function useQualityDetails(
  resourceId: string,
  options?: Omit<UseQueryOptions<QualityDetails, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: editorQueryKeys.quality(resourceId),
    queryFn: async () => {
      const response = await editorApi.getQualityDetails(resourceId);
      return response.data;
    },
    staleTime: editorCacheConfig.quality.staleTime,
    gcTime: editorCacheConfig.quality.cacheTime,
    ...options,
  });
}

/**
 * Recalculate quality scores mutation
 */
export function useRecalculateQuality(
  options?: UseMutationOptions<QualityDetails, Error, string>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (resourceId: string) => {
      const response = await editorApi.recalculateQuality(resourceId);
      return response.data;
    },
    onSuccess: (data, resourceId) => {
      // Update cache with new quality data
      queryClient.setQueryData(
        editorQueryKeys.quality(resourceId),
        data
      );
    },
    ...options,
  });
}

/**
 * Prefetch quality details for a resource
 * 
 * Use this to prefetch quality data before it's needed
 */
export function usePrefetchQualityDetails() {
  const queryClient = useQueryClient();

  return (resourceId: string) => {
    queryClient.prefetchQuery({
      queryKey: editorQueryKeys.quality(resourceId),
      queryFn: async () => {
        const response = await editorApi.getQualityDetails(resourceId);
        return response.data;
      },
      staleTime: editorCacheConfig.quality.staleTime,
    });
  };
}

// ============================================================================
// Graph/Node2Vec Queries (Placeholder)
// ============================================================================

/**
 * Fetch Node2Vec summary for a symbol
 * 
 * Features:
 * - Automatic caching (30 minutes stale time, 60 minutes cache time)
 * - Request deduplication
 * - Debounced by default (use with useDebounce hook)
 */
export function useNode2VecSummary(
  resourceId: string,
  symbol: string,
  options?: Omit<
    UseQueryOptions<{ summary: string; connections: GraphConnection[] }, Error>,
    'queryKey' | 'queryFn'
  >
) {
  return useQuery({
    queryKey: editorQueryKeys.node2vec(symbol),
    queryFn: async () => {
      return await editorApi.getNode2VecSummary(resourceId, symbol);
    },
    staleTime: editorCacheConfig.graph.staleTime,
    gcTime: editorCacheConfig.graph.cacheTime,
    enabled: !!symbol, // Only run if symbol is provided
    ...options,
  });
}

/**
 * Fetch graph connections for a symbol
 */
export function useGraphConnections(
  symbol: string,
  options?: Omit<UseQueryOptions<GraphConnection[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: editorQueryKeys.connections(symbol),
    queryFn: async () => {
      const response = await editorApi.getConnections(symbol);
      return response.data;
    },
    staleTime: editorCacheConfig.graph.staleTime,
    gcTime: editorCacheConfig.graph.cacheTime,
    enabled: !!symbol,
    ...options,
  });
}

// ============================================================================
// Utility Hooks
// ============================================================================

/**
 * Prefetch all editor data for a resource
 * 
 * Use this when opening a file to prefetch all related data in parallel:
 * - Annotations
 * - Chunks
 * - Quality details
 * 
 * This improves perceived performance by loading data before it's needed.
 */
export function usePrefetchEditorData() {
  const queryClient = useQueryClient();

  return (resourceId: string) => {
    // Prefetch all data in parallel
    Promise.all([
      queryClient.prefetchQuery({
        queryKey: editorQueryKeys.annotations(resourceId),
        queryFn: async () => {
          const response = await editorApi.getAnnotations(resourceId);
          return response.data;
        },
        staleTime: editorCacheConfig.annotations.staleTime,
      }),
      queryClient.prefetchQuery({
        queryKey: editorQueryKeys.chunks(resourceId),
        queryFn: async () => {
          const response = await editorApi.getChunks(resourceId);
          return response.data;
        },
        staleTime: editorCacheConfig.chunks.staleTime,
      }),
      queryClient.prefetchQuery({
        queryKey: editorQueryKeys.quality(resourceId),
        queryFn: async () => {
          const response = await editorApi.getQualityDetails(resourceId);
          return response.data;
        },
        staleTime: editorCacheConfig.quality.staleTime,
      }),
    ]);
  };
}

/**
 * Invalidate all editor data for a resource
 * 
 * Use this when you want to force a refetch of all editor data
 * (e.g., after a major update or when switching files)
 */
export function useInvalidateEditorData() {
  const queryClient = useQueryClient();

  return (resourceId: string) => {
    queryClient.invalidateQueries({ 
      queryKey: editorQueryKeys.annotations(resourceId) 
    });
    queryClient.invalidateQueries({ 
      queryKey: editorQueryKeys.chunks(resourceId) 
    });
    queryClient.invalidateQueries({ 
      queryKey: editorQueryKeys.quality(resourceId) 
    });
  };
}
