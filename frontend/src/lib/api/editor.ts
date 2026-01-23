/**
 * Editor API Client
 * 
 * Provides API endpoints for editor features:
 * - Annotations (create, read, update, delete, search)
 * - Semantic chunks (fetch, get details)
 * - Quality data (fetch quality scores)
 * - Node2Vec/graph (placeholder for future implementation)
 */

import { apiClient } from '@/core/api/client';
import type { AxiosResponse } from 'axios';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Annotation types
 */
export interface Annotation {
  id: string;
  resource_id: string;
  user_id: string;
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color: string;
  context_before?: string;
  context_after?: string;
  is_shared: boolean;
  collection_ids?: string[];
  created_at: string;
  updated_at: string;
}

export interface AnnotationCreate {
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color?: string;
  collection_ids?: string[];
}

export interface AnnotationUpdate {
  note?: string;
  tags?: string[];
  color?: string;
  is_shared?: boolean;
}

export interface AnnotationSearchParams {
  query: string;
  resource_id?: string;
  tags?: string[];
  limit?: number;
  offset?: number;
}

/**
 * Semantic chunk types
 */
export interface SemanticChunk {
  id: string;
  resource_id: string;
  content: string;
  chunk_index: number;
  chunk_metadata: {
    function_name?: string;
    class_name?: string;
    start_line: number;
    end_line: number;
    language: string;
  };
  embedding_id?: string;
  created_at: string;
}

/**
 * Quality data types
 */
export interface QualityDetails {
  resource_id: string;
  quality_dimensions: {
    accuracy: number;
    completeness: number;
    consistency: number;
    timeliness: number;
    relevance: number;
  };
  quality_overall: number;
  quality_weights: {
    accuracy: number;
    completeness: number;
    consistency: number;
    timeliness: number;
    relevance: number;
  };
  quality_last_computed: string;
  is_quality_outlier: boolean;
  needs_quality_review: boolean;
}

/**
 * Node2Vec/Graph types (placeholder)
 */
export interface Node2VecSummary {
  symbol: string;
  summary: string;
  embedding?: number[];
  metadata?: Record<string, unknown>;
}

export interface GraphConnection {
  name: string;
  type: 'function' | 'class' | 'variable' | 'module';
  relationship: 'calls' | 'imports' | 'defines' | 'uses';
  file: string;
  line?: number;
}

// ============================================================================
// API Client
// ============================================================================

/**
 * Editor API client with all editor-related endpoints
 */
export const editorApi = {
  // ==========================================================================
  // Annotations API
  // ==========================================================================

  /**
   * Create a new annotation for a resource
   * @param resourceId - Resource ID
   * @param data - Annotation creation data
   * @returns Created annotation
   */
  createAnnotation: async (
    resourceId: string,
    data: AnnotationCreate
  ): Promise<AxiosResponse<Annotation>> => {
    return apiClient.post(`/resources/${resourceId}/annotations`, data);
  },

  /**
   * Get all annotations for a resource
   * @param resourceId - Resource ID
   * @returns List of annotations
   */
  getAnnotations: async (
    resourceId: string
  ): Promise<AxiosResponse<Annotation[]>> => {
    return apiClient.get(`/resources/${resourceId}/annotations`);
  },

  /**
   * Get a specific annotation by ID
   * @param annotationId - Annotation ID
   * @returns Annotation details
   */
  getAnnotation: async (
    annotationId: string
  ): Promise<AxiosResponse<Annotation>> => {
    return apiClient.get(`/annotations/${annotationId}`);
  },

  /**
   * Update an existing annotation
   * @param annotationId - Annotation ID
   * @param data - Annotation update data
   * @returns Updated annotation
   */
  updateAnnotation: async (
    annotationId: string,
    data: AnnotationUpdate
  ): Promise<AxiosResponse<Annotation>> => {
    return apiClient.put(`/annotations/${annotationId}`, data);
  },

  /**
   * Delete an annotation
   * @param annotationId - Annotation ID
   * @returns Success response
   */
  deleteAnnotation: async (
    annotationId: string
  ): Promise<AxiosResponse<void>> => {
    return apiClient.delete(`/annotations/${annotationId}`);
  },

  /**
   * Search annotations using full-text search
   * @param params - Search parameters
   * @returns Matching annotations
   */
  searchAnnotationsFulltext: async (
    params: AnnotationSearchParams
  ): Promise<AxiosResponse<Annotation[]>> => {
    return apiClient.get('/annotations/search/fulltext', { params });
  },

  /**
   * Search annotations using semantic search
   * @param params - Search parameters
   * @returns Matching annotations
   */
  searchAnnotationsSemantic: async (
    params: AnnotationSearchParams
  ): Promise<AxiosResponse<Annotation[]>> => {
    return apiClient.get('/annotations/search/semantic', { params });
  },

  // ==========================================================================
  // Chunks API
  // ==========================================================================

  /**
   * Get all semantic chunks for a resource
   * @param resourceId - Resource ID
   * @returns List of semantic chunks
   */
  getChunks: async (
    resourceId: string
  ): Promise<AxiosResponse<SemanticChunk[]>> => {
    return apiClient.get(`/resources/${resourceId}/chunks`);
  },

  /**
   * Get a specific chunk by ID
   * @param chunkId - Chunk ID
   * @returns Chunk details
   */
  getChunk: async (
    chunkId: string
  ): Promise<AxiosResponse<SemanticChunk>> => {
    return apiClient.get(`/chunks/${chunkId}`);
  },

  /**
   * Trigger chunking for a resource
   * @param resourceId - Resource ID
   * @returns Success response
   */
  triggerChunking: async (
    resourceId: string
  ): Promise<AxiosResponse<{ message: string; task_id?: string }>> => {
    return apiClient.post(`/resources/${resourceId}/chunks`);
  },

  // ==========================================================================
  // Quality API
  // ==========================================================================

  /**
   * Get quality details for a resource
   * @param resourceId - Resource ID
   * @returns Quality details
   */
  getQualityDetails: async (
    resourceId: string
  ): Promise<AxiosResponse<QualityDetails>> => {
    return apiClient.get(`/resources/${resourceId}/quality-details`);
  },

  /**
   * Recalculate quality scores for a resource
   * @param resourceId - Resource ID
   * @returns Updated quality details
   */
  recalculateQuality: async (
    resourceId: string
  ): Promise<AxiosResponse<QualityDetails>> => {
    return apiClient.post('/quality/recalculate', { resource_id: resourceId });
  },

  // ==========================================================================
  // Node2Vec/Graph API (Placeholder)
  // ==========================================================================

  /**
   * Get Node2Vec summary for a symbol
   * @param resourceId - Resource ID
   * @param symbol - Symbol name (function, class, etc.)
   * @returns Node2Vec summary with connections
   * @note This is a placeholder - backend endpoint not yet implemented
   */
  getNode2VecSummary: async (
    resourceId: string,
    symbol: string
  ): Promise<{ summary: string; connections: GraphConnection[] }> => {
    // TODO: Implement when backend endpoint is ready
    // For now, return a placeholder response
    const response = await apiClient.get(
      `/graph/node2vec/${encodeURIComponent(symbol)}`,
      { params: { resource_id: resourceId } }
    );
    return response.data;
  },

  /**
   * Get 1-hop graph connections for a symbol
   * @param symbol - Symbol name
   * @returns List of connected symbols
   * @note This is a placeholder - backend endpoint not yet implemented
   */
  getConnections: async (
    symbol: string
  ): Promise<AxiosResponse<GraphConnection[]>> => {
    // TODO: Implement when backend endpoint is ready
    return apiClient.get(`/graph/connections/${encodeURIComponent(symbol)}`);
  },
};

// ============================================================================
// TanStack Query Hooks Configuration
// ============================================================================

/**
 * Query keys for TanStack Query caching
 */
export const editorQueryKeys = {
  // Annotations
  annotations: (resourceId: string) => ['annotations', resourceId] as const,
  annotation: (annotationId: string) => ['annotation', annotationId] as const,
  annotationSearch: (params: AnnotationSearchParams) => 
    ['annotations', 'search', params] as const,
  
  // Chunks
  chunks: (resourceId: string) => ['chunks', resourceId] as const,
  chunk: (chunkId: string) => ['chunk', chunkId] as const,
  
  // Quality
  quality: (resourceId: string) => ['quality', resourceId] as const,
  
  // Graph
  node2vec: (symbol: string) => ['node2vec', symbol] as const,
  connections: (symbol: string) => ['connections', symbol] as const,
};

/**
 * Default cache times for TanStack Query (in milliseconds)
 */
export const editorCacheConfig = {
  annotations: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  chunks: {
    staleTime: 10 * 60 * 1000, // 10 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  },
  quality: {
    staleTime: 15 * 60 * 1000, // 15 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  },
  graph: {
    staleTime: 30 * 60 * 1000, // 30 minutes
    cacheTime: 60 * 60 * 1000, // 60 minutes
  },
};
