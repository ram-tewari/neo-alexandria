/**
 * Editor API Client
 * 
 * Provides API endpoints for Phase 2 editor features:
 * - Resources (content, status)
 * - Chunks (semantic chunks, chunking operations)
 * - Annotations (CRUD, search, export)
 * - Quality (recalculation, analytics)
 * - Graph/Hover (symbol information)
 * 
 * Phase: 2.5 Backend API Integration
 * Requirements: 3.1, 3.2, 3.3, 3.4, 4.1-4.8, 5.1-5.8, 6.1, 7.5 (runtime validation)
 */

import { apiClient } from '@/core/api/client';
import { validateResponseStrict } from '@/core/api/validation';
import {
  ResourceSchema,
  ProcessingStatusSchema,
  SemanticChunkSchema,
  ChunkListResponseSchema,
  ChunkingTaskSchema,
  AnnotationSchema,
  AnnotationListResponseSchema,
  AnnotationSearchResponseSchema,
  AnnotationExportSchema,
  QualityDetailsSchema,
  QualityRecalculateResponseSchema,
  QualityOutliersResponseSchema,
  QualityDegradationSchema,
  QualityDistributionSchema,
  QualityTrendSchema,
  QualityDimensionScoresSchema,
  ReviewQueueResponseSchema,
  HoverInfoSchema,
} from '@/types/api.schemas';
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
// Editor API Client Interface
// ============================================================================

/**
 * Editor API client with all Phase 2 editor-related endpoints
 */
export const editorApi = {
  // ==========================================================================
  // Resource Content Endpoints
  // ==========================================================================

  /**
   * Get resource by ID with full content
   * @param resourceId - Resource ID
   * @returns Resource with full content
   * @endpoint GET /resources/{resource_id}
   */
  getResource: async (resourceId: string): Promise<Resource> => {
    const response = await apiClient.get(`/resources/${resourceId}`);
    return validateResponseStrict(response.data, ResourceSchema, `GET /resources/${resourceId}`);
  },

  /**
   * Get resource processing status
   * @param resourceId - Resource ID
   * @returns Processing status (ingestion status, errors, timestamps)
   * @endpoint GET /resources/{resource_id}/status
   */
  getResourceStatus: async (resourceId: string): Promise<ProcessingStatus> => {
    const response = await apiClient.get(`/resources/${resourceId}/status`);
    return validateResponseStrict(
      response.data,
      ProcessingStatusSchema,
      `GET /resources/${resourceId}/status`
    );
  },

  // ==========================================================================
  // Chunk Endpoints
  // ==========================================================================

  /**
   * Get all semantic chunks for a resource
   * @param resourceId - Resource ID
   * @returns Array of semantic chunks
   * @endpoint GET /resources/{resource_id}/chunks
   */
  getChunks: async (resourceId: string): Promise<SemanticChunk[]> => {
    const response = await apiClient.get(`/resources/${resourceId}/chunks`);
    const validated = validateResponseStrict(
      response.data,
      ChunkListResponseSchema,
      `GET /resources/${resourceId}/chunks`
    );
    return validated.items;
  },

  /**
   * Get a specific chunk by ID
   * @param chunkId - Chunk ID
   * @returns Semantic chunk details
   * @endpoint GET /chunks/{chunk_id}
   */
  getChunk: async (chunkId: string): Promise<SemanticChunk> => {
    const response = await apiClient.get(`/chunks/${chunkId}`);
    return validateResponseStrict(response.data, SemanticChunkSchema, `GET /chunks/${chunkId}`);
  },

  /**
   * Trigger chunking for a resource
   * @param resourceId - Resource ID
   * @param request - Chunking configuration (strategy, chunk_size, overlap)
   * @returns Chunking task information
   * @endpoint POST /resources/{resource_id}/chunk
   */
  triggerChunking: async (
    resourceId: string,
    request: ChunkingRequest
  ): Promise<ChunkingTask> => {
    const response = await apiClient.post(`/resources/${resourceId}/chunk`, request);
    return validateResponseStrict(
      response.data,
      ChunkingTaskSchema,
      `POST /resources/${resourceId}/chunk`
    );
  },

  // ==========================================================================
  // Annotation Endpoints
  // ==========================================================================

  /**
   * Create a new annotation
   * @param resourceId - Resource ID
   * @param data - Annotation data (offsets, text, note, tags, color)
   * @returns Created annotation with ID
   * @endpoint POST /annotations
   */
  createAnnotation: async (resourceId: string, data: AnnotationCreate): Promise<Annotation> => {
    const response = await apiClient.post('/annotations', {
      resource_id: resourceId,
      ...data,
    });
    return validateResponseStrict(response.data, AnnotationSchema, 'POST /annotations');
  },

  /**
   * Get all annotations for a resource
   * @param resourceId - Resource ID
   * @returns Array of annotations
   * @endpoint GET /annotations?resource_id={resource_id}
   */
  getAnnotations: async (resourceId: string): Promise<Annotation[]> => {
    const response = await apiClient.get('/annotations', {
      params: { resource_id: resourceId },
    });
    const validated = validateResponseStrict(
      response.data,
      AnnotationListResponseSchema,
      'GET /annotations'
    );
    return validated.items;
  },

  /**
   * Update an annotation
   * @param annotationId - Annotation ID
   * @param data - Updated annotation data (note, tags, color, is_shared)
   * @returns Updated annotation
   * @endpoint PUT /annotations/{annotation_id}
   */
  updateAnnotation: async (annotationId: string, data: AnnotationUpdate): Promise<Annotation> => {
    const response = await apiClient.put(`/annotations/${annotationId}`, data);
    return validateResponseStrict(
      response.data,
      AnnotationSchema,
      `PUT /annotations/${annotationId}`
    );
  },

  /**
   * Delete an annotation
   * @param annotationId - Annotation ID
   * @endpoint DELETE /annotations/{annotation_id}
   */
  deleteAnnotation: async (annotationId: string): Promise<void> => {
    await apiClient.delete(`/annotations/${annotationId}`);
  },

  /**
   * Search annotations by full-text query
   * @param params - Search parameters (query, limit)
   * @returns Array of matching annotations with similarity scores
   * @endpoint GET /annotations/search/fulltext
   */
  searchAnnotationsFulltext: async (params: AnnotationSearchParams): Promise<Annotation[]> => {
    const response = await apiClient.get('/annotations/search/fulltext', { params });
    const validated = validateResponseStrict(
      response.data,
      AnnotationSearchResponseSchema,
      'GET /annotations/search/fulltext'
    );
    // Map search results to annotations (search results have extra fields)
    return validated.items.map((item) => ({
      id: item.id,
      resource_id: item.resource_id,
      user_id: '', // Not included in search results
      start_offset: 0, // Not included in search results
      end_offset: 0, // Not included in search results
      highlighted_text: item.highlighted_text,
      note: item.note,
      tags: item.tags,
      color: '', // Not included in search results
      is_shared: false, // Not included in search results
      created_at: item.created_at,
      updated_at: item.created_at, // Use created_at as fallback
    }));
  },

  /**
   * Search annotations by semantic similarity
   * @param params - Search parameters (query, limit)
   * @returns Array of matching annotations with similarity scores
   * @endpoint GET /annotations/search/semantic
   */
  searchAnnotationsSemantic: async (params: AnnotationSearchParams): Promise<Annotation[]> => {
    const response = await apiClient.get('/annotations/search/semantic', { params });
    const validated = validateResponseStrict(
      response.data,
      AnnotationSearchResponseSchema,
      'GET /annotations/search/semantic'
    );
    // Map search results to annotations
    return validated.items.map((item) => ({
      id: item.id,
      resource_id: item.resource_id,
      user_id: '',
      start_offset: 0,
      end_offset: 0,
      highlighted_text: item.highlighted_text,
      note: item.note,
      tags: item.tags,
      color: '',
      is_shared: false,
      created_at: item.created_at,
      updated_at: item.created_at,
    }));
  },

  /**
   * Search annotations by tags
   * @param params - Tag search parameters (tags, match_all)
   * @returns Array of matching annotations
   * @endpoint GET /annotations/search/tags
   */
  searchAnnotationsByTags: async (params: TagSearchParams): Promise<Annotation[]> => {
    const response = await apiClient.get('/annotations/search/tags', {
      params: {
        tags: params.tags.join(','),
        match_all: params.match_all,
      },
    });
    const validated = validateResponseStrict(
      response.data,
      AnnotationListResponseSchema,
      'GET /annotations/search/tags'
    );
    return validated.items;
  },

  /**
   * Export annotations as Markdown
   * @param resourceId - Optional resource ID to filter annotations
   * @returns Markdown string with all annotations
   * @endpoint GET /annotations/export/markdown
   */
  exportAnnotationsMarkdown: async (resourceId?: string): Promise<string> => {
    const response = await apiClient.get('/annotations/export/markdown', {
      params: resourceId ? { resource_id: resourceId } : undefined,
    });
    // Response is plain text, no validation needed
    return response.data;
  },

  /**
   * Export annotations as JSON
   * @param resourceId - Optional resource ID to filter annotations
   * @returns Array of annotations in JSON format
   * @endpoint GET /annotations/export/json
   */
  exportAnnotationsJSON: async (resourceId?: string): Promise<AnnotationExport> => {
    const response = await apiClient.get('/annotations/export/json', {
      params: resourceId ? { resource_id: resourceId } : undefined,
    });
    return validateResponseStrict(
      response.data,
      AnnotationExportSchema,
      'GET /annotations/export/json'
    );
  },

  // ==========================================================================
  // Quality Endpoints
  // ==========================================================================

  /**
   * Recalculate quality scores for one or more resources
   * @param request - Recalculation request (resource_id, resource_ids, weights)
   * @returns Recalculation status
   * @endpoint POST /quality/recalculate
   */
  recalculateQuality: async (request: QualityRecalculateRequest): Promise<QualityDetails> => {
    const response = await apiClient.post('/quality/recalculate', request);
    // Backend returns { status: 'accepted', message: '...' }
    // For now, return a placeholder QualityDetails (actual data comes from polling)
    const validated = validateResponseStrict(
      response.data,
      QualityRecalculateResponseSchema,
      'POST /quality/recalculate'
    );
    // Return a placeholder - caller should poll getResource for updated quality
    return {
      resource_id: request.resource_id || '',
      quality_dimensions: {
        accuracy: 0,
        completeness: 0,
        consistency: 0,
        timeliness: 0,
        relevance: 0,
      },
      quality_overall: 0,
      quality_weights: {
        accuracy: 0.2,
        completeness: 0.2,
        consistency: 0.2,
        timeliness: 0.2,
        relevance: 0.2,
      },
      quality_last_computed: new Date().toISOString(),
      is_quality_outlier: false,
      needs_quality_review: false,
    };
  },

  /**
   * Get quality outliers (resources with unusual quality scores)
   * @param params - Query parameters (page, limit, min_outlier_score, reason)
   * @returns Array of quality outliers
   * @endpoint GET /quality/outliers
   */
  getQualityOutliers: async (params?: QualityOutliersParams): Promise<QualityOutlier[]> => {
    const response = await apiClient.get('/quality/outliers', { params });
    const validated = validateResponseStrict(
      response.data,
      QualityOutliersResponseSchema,
      'GET /quality/outliers'
    );
    return validated.outliers;
  },

  /**
   * Get quality degradation over time
   * @param days - Number of days to look back
   * @returns Quality degradation data
   * @endpoint GET /quality/degradation
   */
  getQualityDegradation: async (days: number): Promise<QualityDegradation> => {
    const response = await apiClient.get('/quality/degradation', {
      params: { days },
    });
    return validateResponseStrict(
      response.data,
      QualityDegradationSchema,
      'GET /quality/degradation'
    );
  },

  /**
   * Get quality distribution histogram
   * @param bins - Number of bins for histogram
   * @returns Quality distribution data
   * @endpoint GET /quality/distribution
   */
  getQualityDistribution: async (bins: number): Promise<QualityDistribution> => {
    const response = await apiClient.get('/quality/distribution', {
      params: { bins },
    });
    return validateResponseStrict(
      response.data,
      QualityDistributionSchema,
      'GET /quality/distribution'
    );
  },

  /**
   * Get quality trends over time
   * @param granularity - Time granularity (daily, weekly, monthly)
   * @returns Quality trend data
   * @endpoint GET /quality/trends
   */
  getQualityTrends: async (
    granularity: 'daily' | 'weekly' | 'monthly'
  ): Promise<QualityTrend> => {
    const response = await apiClient.get('/quality/trends', {
      params: { granularity },
    });
    return validateResponseStrict(response.data, QualityTrendSchema, 'GET /quality/trends');
  },

  /**
   * Get quality dimension scores across all resources
   * @returns Quality dimension statistics
   * @endpoint GET /quality/dimensions
   */
  getQualityDimensions: async (): Promise<QualityDimensionScores> => {
    const response = await apiClient.get('/quality/dimensions');
    return validateResponseStrict(
      response.data,
      QualityDimensionScoresSchema,
      'GET /quality/dimensions'
    );
  },

  /**
   * Get quality review queue (resources needing review)
   * @param params - Query parameters (page, limit, sort_by)
   * @returns Array of resources needing review
   * @endpoint GET /quality/review-queue
   */
  getQualityReviewQueue: async (params?: ReviewQueueParams): Promise<ReviewQueueItem[]> => {
    const response = await apiClient.get('/quality/review-queue', { params });
    const validated = validateResponseStrict(
      response.data,
      ReviewQueueResponseSchema,
      'GET /quality/review-queue'
    );
    return validated.review_queue;
  },

  // ==========================================================================
  // Graph/Hover Endpoints
  // ==========================================================================

  /**
   * Get hover information for a code symbol
   * @param params - Hover parameters (resource_id, file_path, line, column)
   * @returns Hover information (symbol name, type, definition, documentation, related chunks, context)
   * @endpoint GET /api/graph/code/hover
   * @note This method is NOT debounced. Use the useHoverInfo hook for debounced requests.
   */
  getHoverInfo: async (params: HoverParams): Promise<HoverInfo> => {
    const response = await apiClient.get('/api/graph/code/hover', { params });
    return validateResponseStrict(response.data, HoverInfoSchema, 'GET /api/graph/code/hover');
  },
};

// ============================================================================
// TanStack Query Key Factories
// ============================================================================

/**
 * Query key factories for TanStack Query caching
 * 
 * These factories generate consistent cache keys for React Query.
 * Use these keys in useQuery and useMutation hooks to ensure proper
 * cache invalidation and data consistency.
 * 
 * @example
 * ```typescript
 * const { data } = useQuery({
 *   queryKey: editorQueryKeys.resource.detail(resourceId),
 *   queryFn: () => editorApi.getResource(resourceId),
 * });
 * ```
 */
export const editorQueryKeys = {
  /**
   * Resource-related query keys
   */
  resource: {
    /** All resource query keys */
    all: () => ['resource'] as const,
    /** Resource detail with full content */
    detail: (resourceId: string) => ['resource', resourceId] as const,
    /** Resource processing status */
    status: (resourceId: string) => ['resource', resourceId, 'status'] as const,
  },

  /**
   * Chunk-related query keys
   */
  chunks: {
    /** All chunks query keys */
    all: () => ['chunks'] as const,
    /** Chunks for a specific resource */
    byResource: (resourceId: string) => ['chunks', 'resource', resourceId] as const,
    /** Single chunk detail */
    detail: (chunkId: string) => ['chunks', chunkId] as const,
  },

  /**
   * Annotation-related query keys
   */
  annotations: {
    /** All annotations query keys */
    all: () => ['annotations'] as const,
    /** Annotations for a specific resource */
    byResource: (resourceId: string) => ['annotations', 'resource', resourceId] as const,
    /** Annotation search results */
    search: (query: string, type: 'fulltext' | 'semantic' | 'tags') =>
      ['annotations', 'search', type, query] as const,
  },

  /**
   * Quality-related query keys
   */
  quality: {
    /** All quality query keys */
    all: () => ['quality'] as const,
    /** Quality outliers */
    outliers: (params?: QualityOutliersParams) => ['quality', 'outliers', params] as const,
    /** Quality degradation */
    degradation: (days: number) => ['quality', 'degradation', days] as const,
    /** Quality distribution */
    distribution: (bins: number) => ['quality', 'distribution', bins] as const,
    /** Quality trends */
    trends: (granularity: 'daily' | 'weekly' | 'monthly') =>
      ['quality', 'trends', granularity] as const,
    /** Quality dimensions */
    dimensions: () => ['quality', 'dimensions'] as const,
    /** Quality review queue */
    reviewQueue: (params?: ReviewQueueParams) => ['quality', 'reviewQueue', params] as const,
  },

  /**
   * Hover-related query keys
   */
  hover: {
    /** All hover query keys */
    all: () => ['hover'] as const,
    /** Hover info for a specific symbol */
    info: (resourceId: string, symbol: string) => ['hover', resourceId, symbol] as const,
  },
};

// ============================================================================
// Cache Configuration
// ============================================================================

/**
 * Default cache times for TanStack Query (in milliseconds)
 * 
 * - staleTime: How long data is considered fresh (no refetch)
 * - cacheTime: How long unused data stays in cache
 */
export const editorCacheConfig = {
  resource: {
    staleTime: 10 * 60 * 1000, // 10 minutes
    cacheTime: 15 * 60 * 1000, // 15 minutes
  },
  resourceStatus: {
    staleTime: 5 * 1000, // 5 seconds (poll frequently)
    cacheTime: 30 * 1000, // 30 seconds
    refetchInterval: 5 * 1000, // Poll every 5 seconds
  },
  chunks: {
    staleTime: 10 * 60 * 1000, // 10 minutes
    cacheTime: 15 * 60 * 1000, // 15 minutes
  },
  annotations: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  quality: {
    staleTime: 15 * 60 * 1000, // 15 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  },
  hover: {
    staleTime: 30 * 60 * 1000, // 30 minutes
    cacheTime: 60 * 60 * 1000, // 60 minutes
  },
};
