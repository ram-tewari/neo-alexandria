/**
 * TanStack Query Hooks for Editor Data
 * 
 * React Query hooks for Phase 2 editor features:
 * - Resources (content, status with polling)
 * - Chunks (semantic chunks, chunking operations)
 * - Annotations (CRUD, search, export with optimistic updates)
 * 
 * Phase: 2.5 Backend API Integration
 * Tasks: 5.2 (resources & chunks), 6.2 (annotations)
 * Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8
 */

import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from '@tanstack/react-query';
import { useDebounce } from './useDebounce.js';
import {
  editorApi,
  editorQueryKeys,
  editorCacheConfig,
} from '@/lib/api/editor';
import type {
  Resource,
  ProcessingStatus,
  SemanticChunk,
  ChunkingRequest,
  ChunkingTask,
  Annotation,
  AnnotationCreate,
  AnnotationUpdate,
  AnnotationSearchParams,
  TagSearchParams,
  AnnotationExport,
  QualityDetails,
  QualityRecalculateRequest,
  QualityOutliersParams,
  QualityOutlier,
  QualityDegradation,
  QualityDistribution,
  QualityTrend,
  QualityDimensionScores,
  ReviewQueueParams,
  ReviewQueueItem,
  HoverParams,
  HoverInfo,
} from '@/types/api';

// ============================================================================
// Resource Hooks
// ============================================================================

/**
 * Hook to fetch a resource by ID with full content
 * 
 * @param resourceId - Resource ID to fetch
 * @returns Query result with resource data
 * @requirement 3.1 - Fetch resource content from /resources/{resource_id}
 * 
 * @example
 * ```tsx
 * function EditorView({ resourceId }: { resourceId: string }) {
 *   const { data: resource, isLoading, error } = useResource(resourceId);
 *   
 *   if (isLoading) return <EditorSkeleton />;
 *   if (error) return <ErrorMessage error={error} />;
 *   
 *   return <MonacoEditor content={resource.content} />;
 * }
 * ```
 */
export function useResource(
  resourceId: string,
  options?: Omit<UseQueryOptions<Resource, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Resource, Error>({
    queryKey: editorQueryKeys.resource.detail(resourceId),
    queryFn: () => editorApi.getResource(resourceId),
    staleTime: editorCacheConfig.resource.staleTime,
    gcTime: editorCacheConfig.resource.cacheTime,
    enabled: !!resourceId,
    ...options,
  });
}

/**
 * Hook to fetch resource processing status with automatic polling
 * 
 * @param resourceId - Resource ID to check status for
 * @param options - Query options (can override polling interval)
 * @returns Query result with processing status
 * @requirement 3.4 - Poll processing status from /resources/{resource_id}/status
 * 
 * @example
 * ```tsx
 * function ProcessingStatusIndicator({ resourceId }: { resourceId: string }) {
 *   const { data: status, isLoading } = useResourceStatus(resourceId);
 *   
 *   if (isLoading) return <Spinner />;
 *   
 *   return (
 *     <div className={status.ingestion_status === 'completed' ? 'text-green-500' : 'text-yellow-500'}>
 *       Status: {status.ingestion_status}
 *       {status.error_message && <p className="text-red-500">{status.error_message}</p>}
 *     </div>
 *   );
 * }
 * ```
 */
export function useResourceStatus(
  resourceId: string,
  options?: Omit<UseQueryOptions<ProcessingStatus, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<ProcessingStatus, Error>({
    queryKey: editorQueryKeys.resource.status(resourceId),
    queryFn: () => editorApi.getResourceStatus(resourceId),
    staleTime: editorCacheConfig.resourceStatus.staleTime,
    gcTime: editorCacheConfig.resourceStatus.cacheTime,
    refetchInterval: editorCacheConfig.resourceStatus.refetchInterval,
    enabled: !!resourceId,
    ...options,
  });
}

// ============================================================================
// Chunk Hooks
// ============================================================================

/**
 * Hook to fetch all semantic chunks for a resource
 * 
 * @param resourceId - Resource ID to fetch chunks for
 * @returns Query result with array of semantic chunks
 * @requirement 3.2 - Fetch chunks from /resources/{resource_id}/chunks
 * 
 * @example
 * ```tsx
 * function ChunkList({ resourceId }: { resourceId: string }) {
 *   const { data: chunks, isLoading, error } = useChunks(resourceId);
 *   
 *   if (isLoading) return <Skeleton />;
 *   if (error) return <ErrorMessage error={error} />;
 *   
 *   return (
 *     <ul>
 *       {chunks.map(chunk => (
 *         <li key={chunk.id}>
 *           Chunk {chunk.chunk_index}: {chunk.chunk_type}
 *         </li>
 *       ))}
 *     </ul>
 *   );
 * }
 * ```
 */
export function useChunks(
  resourceId: string,
  options?: Omit<UseQueryOptions<SemanticChunk[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<SemanticChunk[], Error>({
    queryKey: editorQueryKeys.chunks.byResource(resourceId),
    queryFn: () => editorApi.getChunks(resourceId),
    staleTime: editorCacheConfig.chunks.staleTime,
    gcTime: editorCacheConfig.chunks.cacheTime,
    enabled: !!resourceId,
    ...options,
  });
}

/**
 * Hook to fetch a specific chunk by ID
 * 
 * @param chunkId - Chunk ID to fetch
 * @returns Query result with chunk details
 * @requirement 3.3 - Fetch chunk details from /chunks/{chunk_id}
 * 
 * @example
 * ```tsx
 * function ChunkDetail({ chunkId }: { chunkId: string }) {
 *   const { data: chunk, isLoading, error } = useChunk(chunkId);
 *   
 *   if (isLoading) return <Spinner />;
 *   if (error) return <ErrorMessage error={error} />;
 *   
 *   return (
 *     <div>
 *       <h3>Chunk {chunk.chunk_index}</h3>
 *       <p>Type: {chunk.chunk_type}</p>
 *       <p>Tokens: {chunk.token_count}</p>
 *       <pre>{chunk.content}</pre>
 *     </div>
 *   );
 * }
 * ```
 */
export function useChunk(
  chunkId: string,
  options?: Omit<UseQueryOptions<SemanticChunk, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<SemanticChunk, Error>({
    queryKey: editorQueryKeys.chunks.detail(chunkId),
    queryFn: () => editorApi.getChunk(chunkId),
    staleTime: editorCacheConfig.chunks.staleTime,
    gcTime: editorCacheConfig.chunks.cacheTime,
    enabled: !!chunkId,
    ...options,
  });
}

/**
 * Hook to trigger chunking for a resource
 * 
 * @returns Mutation object for triggering chunking
 * @requirement 3.4 - Trigger chunking via POST /resources/{resource_id}/chunk
 * 
 * @example
 * ```tsx
 * function ChunkingControls({ resourceId }: { resourceId: string }) {
 *   const triggerChunking = useTriggerChunking();
 *   
 *   const handleChunk = () => {
 *     triggerChunking.mutate({
 *       resourceId,
 *       request: {
 *         strategy: 'parent_child',
 *         chunk_size: 512,
 *         overlap: 50,
 *       },
 *     });
 *   };
 *   
 *   return (
 *     <button 
 *       onClick={handleChunk}
 *       disabled={triggerChunking.isPending}
 *     >
 *       {triggerChunking.isPending ? 'Chunking...' : 'Trigger Chunking'}
 *     </button>
 *   );
 * }
 * ```
 */
export function useTriggerChunking(
  options?: UseMutationOptions<
    ChunkingTask,
    Error,
    { resourceId: string; request: ChunkingRequest }
  >
) {
  const queryClient = useQueryClient();

  return useMutation<
    ChunkingTask,
    Error,
    { resourceId: string; request: ChunkingRequest }
  >({
    mutationFn: ({ resourceId, request }) => editorApi.triggerChunking(resourceId, request),
    onSuccess: (data, variables) => {
      // Invalidate chunks cache to refetch after chunking completes
      queryClient.invalidateQueries({
        queryKey: editorQueryKeys.chunks.byResource(variables.resourceId),
      });
      // Also invalidate resource status to show updated processing state
      queryClient.invalidateQueries({
        queryKey: editorQueryKeys.resource.status(variables.resourceId),
      });
    },
    ...options,
  });
}

// ============================================================================
// Annotation Hooks
// ============================================================================

/**
 * Hook to fetch all annotations for a resource
 * 
 * @param resourceId - Resource ID to fetch annotations for
 * @returns Query result with array of annotations
 * @requirement 4.2 - Fetch annotations from /annotations filtered by resource
 * 
 * @example
 * ```tsx
 * function AnnotationList({ resourceId }: { resourceId: string }) {
 *   const { data: annotations, isLoading, error } = useAnnotations(resourceId);
 *   
 *   if (isLoading) return <Skeleton />;
 *   if (error) return <ErrorMessage error={error} />;
 *   
 *   return (
 *     <ul>
 *       {annotations.map(annotation => (
 *         <li key={annotation.id}>
 *           {annotation.highlighted_text}
 *           {annotation.note && <p>{annotation.note}</p>}
 *         </li>
 *       ))}
 *     </ul>
 *   );
 * }
 * ```
 */
export function useAnnotations(
  resourceId: string,
  options?: Omit<UseQueryOptions<Annotation[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Annotation[], Error>({
    queryKey: editorQueryKeys.annotations.byResource(resourceId),
    queryFn: () => editorApi.getAnnotations(resourceId),
    staleTime: editorCacheConfig.annotations.staleTime,
    gcTime: editorCacheConfig.annotations.cacheTime,
    enabled: !!resourceId,
    ...options,
  });
}

/**
 * Hook to create a new annotation with optimistic updates
 * 
 * @returns Mutation object for creating annotations
 * @requirement 4.1 - POST to /annotations with annotation data
 * @requirement 4.9 - Optimistically update UI before API confirmation
 * @requirement 4.10 - Revert optimistic updates on failure
 * 
 * @example
 * ```tsx
 * function AnnotationCreator({ resourceId }: { resourceId: string }) {
 *   const createAnnotation = useCreateAnnotation();
 *   
 *   const handleCreate = () => {
 *     createAnnotation.mutate({
 *       resourceId,
 *       data: {
 *         start_offset: 0,
 *         end_offset: 10,
 *         highlighted_text: 'selected text',
 *         note: 'My note',
 *         tags: ['important'],
 *         color: '#ffeb3b',
 *       },
 *     });
 *   };
 *   
 *   return (
 *     <button 
 *       onClick={handleCreate}
 *       disabled={createAnnotation.isPending}
 *     >
 *       {createAnnotation.isPending ? 'Creating...' : 'Create Annotation'}
 *     </button>
 *   );
 * }
 * ```
 */
export function useCreateAnnotation(
  options?: UseMutationOptions<
    Annotation,
    Error,
    { resourceId: string; data: AnnotationCreate }
  >
) {
  const queryClient = useQueryClient();

  return useMutation<
    Annotation,
    Error,
    { resourceId: string; data: AnnotationCreate }
  >({
    mutationFn: ({ resourceId, data }) => editorApi.createAnnotation(resourceId, data),
    
    // Optimistic update: Add annotation immediately to UI
    onMutate: async ({ resourceId, data }) => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({
        queryKey: editorQueryKeys.annotations.byResource(resourceId),
      });

      // Snapshot the previous value
      const previousAnnotations = queryClient.getQueryData<Annotation[]>(
        editorQueryKeys.annotations.byResource(resourceId)
      );

      // Optimistically update to the new value
      queryClient.setQueryData<Annotation[]>(
        editorQueryKeys.annotations.byResource(resourceId),
        (old = []) => [
          ...old,
          {
            ...data,
            id: `temp-${Date.now()}`, // Temporary ID until backend confirms
            user_id: '', // Will be filled by backend
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          } as Annotation,
        ]
      );

      // Return context with previous value for rollback
      return { previousAnnotations };
    },

    // Revert optimistic update on error
    onError: (err, variables, context) => {
      if (context?.previousAnnotations) {
        queryClient.setQueryData(
          editorQueryKeys.annotations.byResource(variables.resourceId),
          context.previousAnnotations
        );
      }
    },

    // Refetch to ensure consistency after success or error
    onSettled: (data, error, variables) => {
      queryClient.invalidateQueries({
        queryKey: editorQueryKeys.annotations.byResource(variables.resourceId),
      });
    },

    ...options,
  });
}

/**
 * Hook to update an existing annotation with optimistic updates
 * 
 * @returns Mutation object for updating annotations
 * @requirement 4.3 - PUT to /annotations/{annotation_id}
 * @requirement 4.9 - Optimistically update UI before API confirmation
 * @requirement 4.10 - Revert optimistic updates on failure
 * 
 * @example
 * ```tsx
 * function AnnotationEditor({ annotation }: { annotation: Annotation }) {
 *   const updateAnnotation = useUpdateAnnotation();
 *   
 *   const handleUpdate = (note: string) => {
 *     updateAnnotation.mutate({
 *       annotationId: annotation.id,
 *       resourceId: annotation.resource_id,
 *       data: { note },
 *     });
 *   };
 *   
 *   return (
 *     <input
 *       defaultValue={annotation.note}
 *       onBlur={(e) => handleUpdate(e.target.value)}
 *       disabled={updateAnnotation.isPending}
 *     />
 *   );
 * }
 * ```
 */
export function useUpdateAnnotation(
  options?: UseMutationOptions<
    Annotation,
    Error,
    { annotationId: string; resourceId: string; data: AnnotationUpdate }
  >
) {
  const queryClient = useQueryClient();

  return useMutation<
    Annotation,
    Error,
    { annotationId: string; resourceId: string; data: AnnotationUpdate }
  >({
    mutationFn: ({ annotationId, data }) => editorApi.updateAnnotation(annotationId, data),

    // Optimistic update: Update annotation immediately in UI
    onMutate: async ({ annotationId, resourceId, data }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({
        queryKey: editorQueryKeys.annotations.byResource(resourceId),
      });

      // Snapshot the previous value
      const previousAnnotations = queryClient.getQueryData<Annotation[]>(
        editorQueryKeys.annotations.byResource(resourceId)
      );

      // Optimistically update the annotation
      queryClient.setQueryData<Annotation[]>(
        editorQueryKeys.annotations.byResource(resourceId),
        (old = []) =>
          old.map((annotation) =>
            annotation.id === annotationId
              ? { ...annotation, ...data, updated_at: new Date().toISOString() }
              : annotation
          )
      );

      return { previousAnnotations };
    },

    // Revert optimistic update on error
    onError: (err, variables, context) => {
      if (context?.previousAnnotations) {
        queryClient.setQueryData(
          editorQueryKeys.annotations.byResource(variables.resourceId),
          context.previousAnnotations
        );
      }
    },

    // Refetch to ensure consistency
    onSettled: (data, error, variables) => {
      queryClient.invalidateQueries({
        queryKey: editorQueryKeys.annotations.byResource(variables.resourceId),
      });
    },

    ...options,
  });
}

/**
 * Hook to delete an annotation with optimistic updates
 * 
 * @returns Mutation object for deleting annotations
 * @requirement 4.4 - DELETE /annotations/{annotation_id}
 * @requirement 4.9 - Optimistically update UI before API confirmation
 * @requirement 4.10 - Revert optimistic updates on failure
 * 
 * @example
 * ```tsx
 * function AnnotationDeleteButton({ annotation }: { annotation: Annotation }) {
 *   const deleteAnnotation = useDeleteAnnotation();
 *   
 *   const handleDelete = () => {
 *     if (confirm('Delete this annotation?')) {
 *       deleteAnnotation.mutate({
 *         annotationId: annotation.id,
 *         resourceId: annotation.resource_id,
 *       });
 *     }
 *   };
 *   
 *   return (
 *     <button 
 *       onClick={handleDelete}
 *       disabled={deleteAnnotation.isPending}
 *     >
 *       Delete
 *     </button>
 *   );
 * }
 * ```
 */
export function useDeleteAnnotation(
  options?: UseMutationOptions<
    void,
    Error,
    { annotationId: string; resourceId: string }
  >
) {
  const queryClient = useQueryClient();

  return useMutation<void, Error, { annotationId: string; resourceId: string }>({
    mutationFn: ({ annotationId }) => editorApi.deleteAnnotation(annotationId),

    // Optimistic update: Remove annotation immediately from UI
    onMutate: async ({ annotationId, resourceId }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({
        queryKey: editorQueryKeys.annotations.byResource(resourceId),
      });

      // Snapshot the previous value
      const previousAnnotations = queryClient.getQueryData<Annotation[]>(
        editorQueryKeys.annotations.byResource(resourceId)
      );

      // Optimistically remove the annotation
      queryClient.setQueryData<Annotation[]>(
        editorQueryKeys.annotations.byResource(resourceId),
        (old = []) => old.filter((annotation) => annotation.id !== annotationId)
      );

      return { previousAnnotations };
    },

    // Revert optimistic update on error
    onError: (err, variables, context) => {
      if (context?.previousAnnotations) {
        queryClient.setQueryData(
          editorQueryKeys.annotations.byResource(variables.resourceId),
          context.previousAnnotations
        );
      }
    },

    // Refetch to ensure consistency
    onSettled: (data, error, variables) => {
      queryClient.invalidateQueries({
        queryKey: editorQueryKeys.annotations.byResource(variables.resourceId),
      });
    },

    ...options,
  });
}

/**
 * Hook to search annotations by full-text query
 * 
 * @param params - Search parameters (query, limit)
 * @returns Query result with matching annotations
 * @requirement 4.5 - GET from /annotations/search/fulltext
 * 
 * @example
 * ```tsx
 * function AnnotationSearch() {
 *   const [query, setQuery] = useState('');
 *   const { data: results, isLoading } = useSearchAnnotationsFulltext({
 *     query,
 *     limit: 20,
 *   });
 *   
 *   return (
 *     <div>
 *       <input
 *         value={query}
 *         onChange={(e) => setQuery(e.target.value)}
 *         placeholder="Search annotations..."
 *       />
 *       {isLoading && <Spinner />}
 *       {results?.map(annotation => (
 *         <div key={annotation.id}>{annotation.highlighted_text}</div>
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useSearchAnnotationsFulltext(
  params: AnnotationSearchParams,
  options?: Omit<UseQueryOptions<Annotation[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Annotation[], Error>({
    queryKey: editorQueryKeys.annotations.search(params.query, 'fulltext'),
    queryFn: () => editorApi.searchAnnotationsFulltext(params),
    staleTime: editorCacheConfig.annotations.staleTime,
    gcTime: editorCacheConfig.annotations.cacheTime,
    enabled: !!params.query && params.query.length > 0,
    ...options,
  });
}

/**
 * Hook to search annotations by semantic similarity
 * 
 * @param params - Search parameters (query, limit)
 * @returns Query result with matching annotations
 * @requirement 4.6 - GET from /annotations/search/semantic
 * 
 * @example
 * ```tsx
 * function SemanticAnnotationSearch() {
 *   const [query, setQuery] = useState('');
 *   const { data: results, isLoading } = useSearchAnnotationsSemantic({
 *     query,
 *     limit: 20,
 *   });
 *   
 *   return (
 *     <div>
 *       <input
 *         value={query}
 *         onChange={(e) => setQuery(e.target.value)}
 *         placeholder="Semantic search..."
 *       />
 *       {isLoading && <Spinner />}
 *       {results?.map(annotation => (
 *         <div key={annotation.id}>{annotation.highlighted_text}</div>
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useSearchAnnotationsSemantic(
  params: AnnotationSearchParams,
  options?: Omit<UseQueryOptions<Annotation[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Annotation[], Error>({
    queryKey: editorQueryKeys.annotations.search(params.query, 'semantic'),
    queryFn: () => editorApi.searchAnnotationsSemantic(params),
    staleTime: editorCacheConfig.annotations.staleTime,
    gcTime: editorCacheConfig.annotations.cacheTime,
    enabled: !!params.query && params.query.length > 0,
    ...options,
  });
}

/**
 * Hook to search annotations by tags
 * 
 * @param params - Tag search parameters (tags, match_all)
 * @returns Query result with matching annotations
 * @requirement 4.7 - GET from /annotations/search/tags
 * 
 * @example
 * ```tsx
 * function TagAnnotationSearch() {
 *   const [tags, setTags] = useState<string[]>(['important']);
 *   const { data: results, isLoading } = useSearchAnnotationsByTags({
 *     tags,
 *     match_all: false,
 *   });
 *   
 *   return (
 *     <div>
 *       <TagSelector tags={tags} onChange={setTags} />
 *       {isLoading && <Spinner />}
 *       {results?.map(annotation => (
 *         <div key={annotation.id}>{annotation.highlighted_text}</div>
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useSearchAnnotationsByTags(
  params: TagSearchParams,
  options?: Omit<UseQueryOptions<Annotation[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Annotation[], Error>({
    queryKey: editorQueryKeys.annotations.search(params.tags.join(','), 'tags'),
    queryFn: () => editorApi.searchAnnotationsByTags(params),
    staleTime: editorCacheConfig.annotations.staleTime,
    gcTime: editorCacheConfig.annotations.cacheTime,
    enabled: params.tags.length > 0,
    ...options,
  });
}

/**
 * Hook to export annotations as Markdown
 * 
 * @param resourceId - Optional resource ID to filter annotations
 * @returns Query result with Markdown string
 * @requirement 4.8 - GET from /annotations/export/markdown
 * 
 * @example
 * ```tsx
 * function AnnotationExportButton({ resourceId }: { resourceId?: string }) {
 *   const { data: markdown, refetch, isLoading } = useExportAnnotationsMarkdown(resourceId, {
 *     enabled: false, // Don't auto-fetch, only on button click
 *   });
 *   
 *   const handleExport = async () => {
 *     const result = await refetch();
 *     if (result.data) {
 *       // Download or copy to clipboard
 *       navigator.clipboard.writeText(result.data);
 *     }
 *   };
 *   
 *   return (
 *     <button onClick={handleExport} disabled={isLoading}>
 *       Export as Markdown
 *     </button>
 *   );
 * }
 * ```
 */
export function useExportAnnotationsMarkdown(
  resourceId?: string,
  options?: Omit<UseQueryOptions<string, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<string, Error>({
    queryKey: ['annotations', 'export', 'markdown', resourceId] as const,
    queryFn: () => editorApi.exportAnnotationsMarkdown(resourceId),
    staleTime: 0, // Always fetch fresh export
    gcTime: 0, // Don't cache exports
    enabled: false, // Manual trigger only
    ...options,
  });
}

/**
 * Hook to export annotations as JSON
 * 
 * @param resourceId - Optional resource ID to filter annotations
 * @returns Query result with annotation export data
 * @requirement 4.8 - GET from /annotations/export/json
 * 
 * @example
 * ```tsx
 * function AnnotationExportJSONButton({ resourceId }: { resourceId?: string }) {
 *   const { data: exportData, refetch, isLoading } = useExportAnnotationsJSON(resourceId, {
 *     enabled: false, // Don't auto-fetch, only on button click
 *   });
 *   
 *   const handleExport = async () => {
 *     const result = await refetch();
 *     if (result.data) {
 *       // Download as JSON file
 *       const blob = new Blob([JSON.stringify(result.data, null, 2)], {
 *         type: 'application/json',
 *       });
 *       const url = URL.createObjectURL(blob);
 *       const a = document.createElement('a');
 *       a.href = url;
 *       a.download = 'annotations.json';
 *       a.click();
 *     }
 *   };
 *   
 *   return (
 *     <button onClick={handleExport} disabled={isLoading}>
 *       Export as JSON
 *     </button>
 *   );
 * }
 * ```
 */
export function useExportAnnotationsJSON(
  resourceId?: string,
  options?: Omit<UseQueryOptions<AnnotationExport, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<AnnotationExport, Error>({
    queryKey: ['annotations', 'export', 'json', resourceId] as const,
    queryFn: () => editorApi.exportAnnotationsJSON(resourceId),
    staleTime: 0, // Always fetch fresh export
    gcTime: 0, // Don't cache exports
    enabled: false, // Manual trigger only
    ...options,
  });
}

// ============================================================================
// Quality Hooks
// ============================================================================

/**
 * Hook to get quality details from resource metadata
 * 
 * @param resourceId - Resource ID to fetch quality data for
 * @returns Query result with quality details from resource
 * @requirement 5.1 - Fetch quality data from resource metadata
 * 
 * @example
 * ```tsx
 * function QualityBadge({ resourceId }: { resourceId: string }) {
 *   const { data: resource, isLoading } = useQualityDetails(resourceId);
 *   
 *   if (isLoading) return <Skeleton />;
 *   if (!resource?.quality_overall) return null;
 *   
 *   return (
 *     <div className={resource.quality_overall > 0.7 ? 'text-green-500' : 'text-yellow-500'}>
 *       Quality: {(resource.quality_overall * 100).toFixed(0)}%
 *     </div>
 *   );
 * }
 * ```
 */
export function useQualityDetails(
  resourceId: string,
  options?: Omit<UseQueryOptions<Resource, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<Resource, Error>({
    queryKey: editorQueryKeys.resource.detail(resourceId),
    queryFn: () => editorApi.getResource(resourceId),
    staleTime: editorCacheConfig.quality.staleTime,
    gcTime: editorCacheConfig.quality.cacheTime,
    enabled: !!resourceId,
    select: (data) => data, // Return full resource with quality_overall and quality_dimensions
    ...options,
  });
}

/**
 * Hook to trigger quality recalculation for a resource
 * 
 * @returns Mutation object for recalculating quality
 * @requirement 5.2 - POST to /quality/recalculate
 * 
 * @example
 * ```tsx
 * function RecalculateQualityButton({ resourceId }: { resourceId: string }) {
 *   const recalculate = useRecalculateQuality();
 *   
 *   const handleRecalculate = () => {
 *     recalculate.mutate({
 *       resource_id: resourceId,
 *       weights: {
 *         accuracy: 0.25,
 *         completeness: 0.25,
 *         consistency: 0.2,
 *         timeliness: 0.15,
 *         relevance: 0.15,
 *       },
 *     });
 *   };
 *   
 *   return (
 *     <button 
 *       onClick={handleRecalculate}
 *       disabled={recalculate.isPending}
 *     >
 *       {recalculate.isPending ? 'Recalculating...' : 'Recalculate Quality'}
 *     </button>
 *   );
 * }
 * ```
 */
export function useRecalculateQuality(
  options?: UseMutationOptions<
    QualityDetails,
    Error,
    QualityRecalculateRequest
  >
) {
  const queryClient = useQueryClient();

  return useMutation<QualityDetails, Error, QualityRecalculateRequest>({
    mutationFn: (request) => editorApi.recalculateQuality(request),
    onSuccess: (data, variables) => {
      // Invalidate resource cache to refetch updated quality scores
      if (variables.resource_id) {
        queryClient.invalidateQueries({
          queryKey: editorQueryKeys.resource.detail(variables.resource_id),
        });
      }
      // If multiple resources, invalidate all resources
      if (variables.resource_ids) {
        variables.resource_ids.forEach((resourceId) => {
          queryClient.invalidateQueries({
            queryKey: editorQueryKeys.resource.detail(resourceId),
          });
        });
      }
      // Invalidate quality analytics
      queryClient.invalidateQueries({
        queryKey: editorQueryKeys.quality.all(),
      });
    },
    ...options,
  });
}

/**
 * Hook to fetch quality outliers
 * 
 * @param params - Query parameters (page, limit, min_outlier_score, reason)
 * @returns Query result with array of quality outliers
 * @requirement 5.3 - GET from /quality/outliers
 * 
 * @example
 * ```tsx
 * function QualityOutliersList() {
 *   const { data: outliers, isLoading, error } = useQualityOutliers({
 *     page: 1,
 *     limit: 20,
 *     min_outlier_score: 0.8,
 *   });
 *   
 *   if (isLoading) return <Skeleton />;
 *   if (error) return <ErrorMessage error={error} />;
 *   
 *   return (
 *     <ul>
 *       {outliers.map(outlier => (
 *         <li key={outlier.resource_id}>
 *           {outlier.resource_title} - Score: {outlier.outlier_score.toFixed(2)}
 *           <p>{outlier.reason}</p>
 *         </li>
 *       ))}
 *     </ul>
 *   );
 * }
 * ```
 */
export function useQualityOutliers(
  params?: QualityOutliersParams,
  options?: Omit<UseQueryOptions<QualityOutlier[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<QualityOutlier[], Error>({
    queryKey: editorQueryKeys.quality.outliers(params),
    queryFn: () => editorApi.getQualityOutliers(params),
    staleTime: editorCacheConfig.quality.staleTime,
    gcTime: editorCacheConfig.quality.cacheTime,
    ...options,
  });
}

/**
 * Hook to fetch quality degradation over time
 * 
 * @param days - Number of days to look back
 * @returns Query result with quality degradation data
 * @requirement 5.4 - GET from /quality/degradation
 * 
 * @example
 * ```tsx
 * function QualityDegradationChart() {
 *   const { data: degradation, isLoading } = useQualityDegradation(30);
 *   
 *   if (isLoading) return <Spinner />;
 *   
 *   return (
 *     <div>
 *       <h3>Quality Degradation (Last 30 Days)</h3>
 *       <p>Degraded Resources: {degradation.degraded_count}</p>
 *       <p>Average Change: {degradation.average_change.toFixed(2)}</p>
 *       <ul>
 *         {degradation.degraded_resources.map(resource => (
 *           <li key={resource.resource_id}>
 *             {resource.resource_title}: {resource.quality_change.toFixed(2)}
 *           </li>
 *         ))}
 *       </ul>
 *     </div>
 *   );
 * }
 * ```
 */
export function useQualityDegradation(
  days: number,
  options?: Omit<UseQueryOptions<QualityDegradation, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<QualityDegradation, Error>({
    queryKey: editorQueryKeys.quality.degradation(days),
    queryFn: () => editorApi.getQualityDegradation(days),
    staleTime: editorCacheConfig.quality.staleTime,
    gcTime: editorCacheConfig.quality.cacheTime,
    enabled: days > 0,
    ...options,
  });
}

/**
 * Hook to fetch quality distribution histogram
 * 
 * @param bins - Number of bins for histogram
 * @returns Query result with quality distribution data
 * @requirement 5.5 - GET from /quality/distribution
 * 
 * @example
 * ```tsx
 * function QualityDistributionChart() {
 *   const { data: distribution, isLoading } = useQualityDistribution(10);
 *   
 *   if (isLoading) return <Spinner />;
 *   
 *   return (
 *     <div>
 *       <h3>Quality Score Distribution</h3>
 *       <BarChart data={distribution.bins} />
 *       <p>Mean: {distribution.mean.toFixed(2)}</p>
 *       <p>Median: {distribution.median.toFixed(2)}</p>
 *       <p>Std Dev: {distribution.std_dev.toFixed(2)}</p>
 *     </div>
 *   );
 * }
 * ```
 */
export function useQualityDistribution(
  bins: number,
  options?: Omit<UseQueryOptions<QualityDistribution, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<QualityDistribution, Error>({
    queryKey: editorQueryKeys.quality.distribution(bins),
    queryFn: () => editorApi.getQualityDistribution(bins),
    staleTime: editorCacheConfig.quality.staleTime,
    gcTime: editorCacheConfig.quality.cacheTime,
    enabled: bins > 0,
    ...options,
  });
}

/**
 * Hook to fetch quality trends over time
 * 
 * @param granularity - Time granularity (daily, weekly, monthly)
 * @returns Query result with quality trend data
 * @requirement 5.6 - GET from /quality/trends
 * 
 * @example
 * ```tsx
 * function QualityTrendsChart() {
 *   const { data: trends, isLoading } = useQualityTrends('weekly');
 *   
 *   if (isLoading) return <Spinner />;
 *   
 *   return (
 *     <div>
 *       <h3>Quality Trends (Weekly)</h3>
 *       <LineChart data={trends.data_points} />
 *       <p>Trend: {trends.trend_direction}</p>
 *       <p>Change: {trends.overall_change.toFixed(2)}</p>
 *     </div>
 *   );
 * }
 * ```
 */
export function useQualityTrends(
  granularity: 'daily' | 'weekly' | 'monthly',
  options?: Omit<UseQueryOptions<QualityTrend, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<QualityTrend, Error>({
    queryKey: editorQueryKeys.quality.trends(granularity),
    queryFn: () => editorApi.getQualityTrends(granularity),
    staleTime: editorCacheConfig.quality.staleTime,
    gcTime: editorCacheConfig.quality.cacheTime,
    ...options,
  });
}

/**
 * Hook to fetch quality dimension scores across all resources
 * 
 * @returns Query result with quality dimension statistics
 * @requirement 5.7 - GET from /quality/dimensions
 * 
 * @example
 * ```tsx
 * function QualityDimensionsOverview() {
 *   const { data: dimensions, isLoading } = useQualityDimensions();
 *   
 *   if (isLoading) return <Spinner />;
 *   
 *   return (
 *     <div>
 *       <h3>Quality Dimensions</h3>
 *       <div>Accuracy: {dimensions.accuracy.mean.toFixed(2)}</div>
 *       <div>Completeness: {dimensions.completeness.mean.toFixed(2)}</div>
 *       <div>Consistency: {dimensions.consistency.mean.toFixed(2)}</div>
 *       <div>Timeliness: {dimensions.timeliness.mean.toFixed(2)}</div>
 *       <div>Relevance: {dimensions.relevance.mean.toFixed(2)}</div>
 *     </div>
 *   );
 * }
 * ```
 */
export function useQualityDimensions(
  options?: Omit<UseQueryOptions<QualityDimensionScores, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<QualityDimensionScores, Error>({
    queryKey: editorQueryKeys.quality.dimensions(),
    queryFn: () => editorApi.getQualityDimensions(),
    staleTime: editorCacheConfig.quality.staleTime,
    gcTime: editorCacheConfig.quality.cacheTime,
    ...options,
  });
}

/**
 * Hook to fetch quality review queue
 * 
 * @param params - Query parameters (page, limit, sort_by)
 * @returns Query result with array of resources needing review
 * @requirement 5.8 - GET from /quality/review-queue
 * 
 * @example
 * ```tsx
 * function QualityReviewQueue() {
 *   const { data: queue, isLoading, error } = useQualityReviewQueue({
 *     page: 1,
 *     limit: 20,
 *     sort_by: 'priority',
 *   });
 *   
 *   if (isLoading) return <Skeleton />;
 *   if (error) return <ErrorMessage error={error} />;
 *   
 *   return (
 *     <ul>
 *       {queue.map(item => (
 *         <li key={item.resource_id}>
 *           {item.resource_title}
 *           <span className="text-red-500">Priority: {item.priority}</span>
 *           <p>{item.reason}</p>
 *         </li>
 *       ))}
 *     </ul>
 *   );
 * }
 * ```
 */
export function useQualityReviewQueue(
  params?: ReviewQueueParams,
  options?: Omit<UseQueryOptions<ReviewQueueItem[], Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<ReviewQueueItem[], Error>({
    queryKey: editorQueryKeys.quality.reviewQueue(params),
    queryFn: () => editorApi.getQualityReviewQueue(params),
    staleTime: editorCacheConfig.quality.staleTime,
    gcTime: editorCacheConfig.quality.cacheTime,
    ...options,
  });
}

// ============================================================================
// Hover Hooks
// ============================================================================

/**
 * Hook to fetch hover information for a code symbol with debouncing
 * 
 * @param params - Hover parameters (resource_id, file_path, line, column)
 * @param debounceMs - Debounce delay in milliseconds (default: 300ms)
 * @param options - Query options
 * @returns Query result with hover information
 * @requirement 6.1 - Fetch hover info from /api/graph/code/hover
 * @requirement 6.2 - Debounce hover requests by 300ms
 * @requirement 6.3 - Display loading state while fetching
 * @requirement 6.4 - Cache hover responses for 30 minutes
 * 
 * @example
 * ```tsx
 * function HoverCard({ resourceId, filePath, line, column }: HoverCardProps) {
 *   const { data: hoverInfo, isLoading, error } = useHoverInfo({
 *     resource_id: resourceId,
 *     file_path: filePath,
 *     line,
 *     column,
 *   });
 *   
 *   if (isLoading) return <Skeleton />;
 *   if (error) return <ErrorMessage error={error} />;
 *   if (!hoverInfo?.symbol_name) return null;
 *   
 *   return (
 *     <div>
 *       <h3>{hoverInfo.symbol_name}</h3>
 *       <p>{hoverInfo.symbol_type}</p>
 *       {hoverInfo.documentation && <p>{hoverInfo.documentation}</p>}
 *     </div>
 *   );
 * }
 * ```
 */
export function useHoverInfo(
  params: HoverParams | null,
  debounceMs: number = 300,
  options?: Omit<UseQueryOptions<HoverInfo, Error>, 'queryKey' | 'queryFn'>
) {
  // Debounce the hover parameters to avoid excessive API calls
  // This ensures we only fetch hover info after the user has stopped moving the cursor for 300ms
  const debouncedParams = useDebounce(params, debounceMs);

  return useQuery<HoverInfo, Error>({
    queryKey: debouncedParams
      ? editorQueryKeys.hover.info(debouncedParams.resource_id, `${debouncedParams.file_path}:${debouncedParams.line}:${debouncedParams.column}`)
      : ['hover', 'disabled'],
    queryFn: () => {
      if (!debouncedParams) {
        throw new Error('Hover params are null');
      }
      return editorApi.getHoverInfo(debouncedParams);
    },
    staleTime: editorCacheConfig.hover.staleTime, // 30 minutes
    gcTime: editorCacheConfig.hover.cacheTime, // 60 minutes
    enabled: !!debouncedParams, // Only fetch when params are available
    retry: 1, // Only retry once for hover requests (they should be fast)
    ...options,
  });
}
