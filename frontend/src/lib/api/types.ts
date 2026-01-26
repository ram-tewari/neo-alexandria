/**
 * API Client Type Definitions
 * 
 * This file exports TypeScript interfaces for API client modules,
 * query key factories, and cache configurations.
 * 
 * Phase: 2.5 Backend API Integration
 * Requirements: 7.1, 7.4
 */

import type { AxiosResponse } from 'axios';
import type {
  User,
  TokenResponse,
  LoginRequest,
  RefreshTokenRequest,
  RateLimitStatus,
  Resource,
  ResourceCreate,
  ResourceUpdate,
  ResourceListParams,
  ProcessingStatus,
  ClassificationOverride,
  Annotation,
  AnnotationCreate,
  AnnotationUpdate,
  AnnotationSearchParams,
  AnnotationExport,
  SemanticChunk,
  ChunkingTask,
  QualityDetails,
  QualityOutlier,
  QualityDegradation,
  QualityDistribution,
  QualityTrend,
  QualityDimensionScores,
  ReviewQueueItem,
  PaginationParams,
  HoverParams,
  HoverInfo,
  HealthStatus,
  ModuleHealth,
  SystemMetrics,
} from '@/types/api';

// ============================================================================
// Workbench API Interface
// ============================================================================

/**
 * Workbench API client interface for Phase 1 features
 * 
 * Includes:
 * - Authentication (login, token refresh, user info, rate limits)
 * - Resources (CRUD operations)
 * - Health monitoring (system health, module health, metrics)
 */
export interface WorkbenchApi {
  // Authentication
  getCurrentUser: () => Promise<AxiosResponse<User>>;
  login: (credentials: LoginRequest) => Promise<AxiosResponse<TokenResponse>>;
  refreshToken: (request: RefreshTokenRequest) => Promise<AxiosResponse<TokenResponse>>;
  getRateLimit: () => Promise<AxiosResponse<RateLimitStatus>>;

  // Resources
  getResources: (params?: ResourceListParams) => Promise<AxiosResponse<Resource[]>>;
  createResource: (data: ResourceCreate) => Promise<AxiosResponse<Resource>>;
  updateResource: (resourceId: string, data: ResourceUpdate) => Promise<AxiosResponse<Resource>>;
  deleteResource: (resourceId: string) => Promise<AxiosResponse<void>>;

  // Health Monitoring
  getSystemHealth: () => Promise<AxiosResponse<HealthStatus>>;
  getAuthHealth: () => Promise<AxiosResponse<ModuleHealth>>;
  getResourcesHealth: () => Promise<AxiosResponse<ModuleHealth>>;
  getSystemMetrics: () => Promise<AxiosResponse<SystemMetrics>>;
}

// ============================================================================
// Editor API Interface
// ============================================================================

/**
 * Editor API client interface for Phase 2 features
 * 
 * Includes:
 * - Resource content (fetch, status, classification)
 * - Chunks (fetch, trigger chunking)
 * - Annotations (CRUD, search, export)
 * - Quality (fetch, recalculate, analytics)
 * - Graph/Hover (hover information)
 */
export interface EditorApi {
  // Resource Content
  getResource: (resourceId: string) => Promise<AxiosResponse<Resource>>;
  getResourceStatus: (resourceId: string) => Promise<AxiosResponse<ProcessingStatus>>;
  overrideClassification: (resourceId: string, data: ClassificationOverride) => Promise<AxiosResponse<Resource>>;

  // Chunks
  getChunks: (resourceId: string) => Promise<AxiosResponse<SemanticChunk[]>>;
  getChunk: (chunkId: string) => Promise<AxiosResponse<SemanticChunk>>;
  triggerChunking: (resourceId: string) => Promise<AxiosResponse<ChunkingTask>>;

  // Annotations
  createAnnotation: (resourceId: string, data: AnnotationCreate) => Promise<AxiosResponse<Annotation>>;
  getAnnotations: (resourceId: string, params?: PaginationParams) => Promise<AxiosResponse<Annotation[]>>;
  getAnnotation: (annotationId: string) => Promise<AxiosResponse<Annotation>>;
  updateAnnotation: (annotationId: string, data: AnnotationUpdate) => Promise<AxiosResponse<Annotation>>;
  deleteAnnotation: (annotationId: string) => Promise<AxiosResponse<void>>;
  searchAnnotationsFulltext: (params: AnnotationSearchParams) => Promise<AxiosResponse<Annotation[]>>;
  searchAnnotationsSemantic: (params: AnnotationSearchParams) => Promise<AxiosResponse<Annotation[]>>;
  searchAnnotationsByTags: (params: { tags: string[] }) => Promise<AxiosResponse<Annotation[]>>;
  exportAnnotationsMarkdown: (resourceId?: string) => Promise<AxiosResponse<string>>;
  exportAnnotationsJSON: (resourceId?: string) => Promise<AxiosResponse<AnnotationExport>>;

  // Quality
  getQualityDetails: (resourceId: string) => Promise<AxiosResponse<QualityDetails>>;
  recalculateQuality: (resourceId: string) => Promise<AxiosResponse<QualityDetails>>;
  getQualityOutliers: (params?: PaginationParams) => Promise<AxiosResponse<QualityOutlier[]>>;
  getQualityDegradation: (days: number) => Promise<AxiosResponse<QualityDegradation>>;
  getQualityDistribution: (dimension: string, bins: number) => Promise<AxiosResponse<QualityDistribution>>;
  getQualityTrends: (dimension: string, granularity: 'daily' | 'weekly' | 'monthly') => Promise<AxiosResponse<QualityTrend>>;
  getQualityDimensions: () => Promise<AxiosResponse<QualityDimensionScores>>;
  getQualityReviewQueue: (params?: PaginationParams) => Promise<AxiosResponse<ReviewQueueItem[]>>;

  // Graph/Hover
  getHoverInfo: (params: HoverParams) => Promise<AxiosResponse<HoverInfo>>;
}

// ============================================================================
// Query Key Factories
// ============================================================================

/**
 * Workbench query key factory
 * 
 * Generates consistent cache keys for TanStack Query.
 * Supports hierarchical invalidation (e.g., invalidating 'workbench' invalidates all workbench queries).
 */
export const workbenchQueryKeys = {
  /** Base key for all workbench queries */
  all: ['workbench'] as const,

  /** User-related queries */
  user: () => ['workbench', 'user'] as const,
  currentUser: () => ['workbench', 'user', 'current'] as const,
  rateLimit: () => ['workbench', 'user', 'rateLimit'] as const,

  /** Resource-related queries */
  resources: () => ['workbench', 'resources'] as const,
  resourceList: (params?: ResourceListParams) => ['workbench', 'resources', 'list', params] as const,
  resource: (resourceId: string) => ['workbench', 'resources', 'detail', resourceId] as const,

  /** Health monitoring queries */
  health: () => ['workbench', 'health'] as const,
  systemHealth: () => ['workbench', 'health', 'system'] as const,
  authHealth: () => ['workbench', 'health', 'auth'] as const,
  resourcesHealth: () => ['workbench', 'health', 'resources'] as const,
  systemMetrics: () => ['workbench', 'health', 'metrics'] as const,
};

/**
 * Editor query key factory
 * 
 * Generates consistent cache keys for TanStack Query.
 * Supports hierarchical invalidation (e.g., invalidating 'editor' invalidates all editor queries).
 */
export const editorQueryKeys = {
  /** Base key for all editor queries */
  all: ['editor'] as const,

  /** Resource-related queries */
  resources: () => ['editor', 'resources'] as const,
  resource: (resourceId: string) => ['editor', 'resources', resourceId] as const,
  resourceStatus: (resourceId: string) => ['editor', 'resources', resourceId, 'status'] as const,

  /** Chunk-related queries */
  chunks: () => ['editor', 'chunks'] as const,
  chunkList: (resourceId: string) => ['editor', 'chunks', 'list', resourceId] as const,
  chunk: (chunkId: string) => ['editor', 'chunks', 'detail', chunkId] as const,

  /** Annotation-related queries */
  annotations: () => ['editor', 'annotations'] as const,
  annotationList: (resourceId: string, params?: PaginationParams) => 
    ['editor', 'annotations', 'list', resourceId, params] as const,
  annotation: (annotationId: string) => ['editor', 'annotations', 'detail', annotationId] as const,
  annotationSearch: (params: AnnotationSearchParams) => 
    ['editor', 'annotations', 'search', params] as const,
  annotationSearchSemantic: (params: AnnotationSearchParams) => 
    ['editor', 'annotations', 'search', 'semantic', params] as const,
  annotationSearchTags: (params: { tags: string[] }) => 
    ['editor', 'annotations', 'search', 'tags', params] as const,

  /** Quality-related queries */
  quality: () => ['editor', 'quality'] as const,
  qualityDetails: (resourceId: string) => ['editor', 'quality', 'details', resourceId] as const,
  qualityOutliers: (params?: PaginationParams) => ['editor', 'quality', 'outliers', params] as const,
  qualityDegradation: (days: number) => ['editor', 'quality', 'degradation', days] as const,
  qualityDistribution: (dimension: string, bins: number) => 
    ['editor', 'quality', 'distribution', dimension, bins] as const,
  qualityTrends: (dimension: string, granularity: 'daily' | 'weekly' | 'monthly') => 
    ['editor', 'quality', 'trends', dimension, granularity] as const,
  qualityDimensions: () => ['editor', 'quality', 'dimensions'] as const,
  qualityReviewQueue: (params?: PaginationParams) => 
    ['editor', 'quality', 'reviewQueue', params] as const,

  /** Graph/Hover queries */
  graph: () => ['editor', 'graph'] as const,
  hover: (params: HoverParams) => ['editor', 'graph', 'hover', params] as const,
};

// ============================================================================
// Cache Configuration
// ============================================================================

/**
 * Workbench cache configuration
 * 
 * Defines staleTime, cacheTime, and refetchInterval for workbench queries.
 * - staleTime: How long data is considered fresh (no refetch)
 * - cacheTime: How long unused data stays in cache
 * - refetchInterval: How often to poll for updates (optional)
 */
export const workbenchCacheConfig = {
  user: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  resources: {
    staleTime: 2 * 60 * 1000, // 2 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  health: {
    staleTime: 30 * 1000, // 30 seconds
    cacheTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 30 * 1000, // Poll every 30 seconds
  },
};

/**
 * Editor cache configuration
 * 
 * Defines staleTime, cacheTime, and debounceMs for editor queries.
 * - staleTime: How long data is considered fresh (no refetch)
 * - cacheTime: How long unused data stays in cache
 * - debounceMs: Debounce delay for rapid requests (e.g., hover)
 */
export const editorCacheConfig = {
  resources: {
    staleTime: 10 * 60 * 1000, // 10 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  },
  chunks: {
    staleTime: 10 * 60 * 1000, // 10 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  },
  annotations: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  quality: {
    staleTime: 15 * 60 * 1000, // 15 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  },
  graph: {
    staleTime: 30 * 60 * 1000, // 30 minutes
    cacheTime: 60 * 60 * 1000, // 60 minutes
  },
  hover: {
    staleTime: 30 * 60 * 1000, // 30 minutes
    cacheTime: 60 * 60 * 1000, // 60 minutes
    debounceMs: 300, // 300ms debounce
  },
};
