/**
 * API Type Definitions for Neo Alexandria 2.0
 * 
 * This file contains TypeScript interfaces matching the backend API schemas
 * from https://pharos.onrender.com
 * 
 * Generated from backend API documentation:
 * - backend/docs/api/overview.md
 * - backend/docs/api/resources.md
 * - backend/docs/api/annotations.md
 * - backend/docs/api/quality.md
 * - backend/docs/api/auth.md
 * - backend/docs/api/monitoring.md
 */

// ============================================================================
// User and Authentication Types
// ============================================================================

/**
 * User account information
 */
export interface User {
  id: string;
  username: string;
  email: string;
  tier: 'free' | 'premium' | 'admin';
  is_active: boolean;
}

/**
 * OAuth2 token response
 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
}

/**
 * Login request payload
 */
export interface LoginRequest {
  username: string;
  password: string;
  scopes?: string;
}

/**
 * Token refresh request
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * Rate limit status
 */
export interface RateLimitStatus {
  tier: 'free' | 'premium' | 'admin';
  limit: number;
  remaining: number;
  reset: number; // Unix timestamp
}

// ============================================================================
// Resource Types
// ============================================================================

/**
 * Resource content types
 */
export type ResourceContentType = 'code' | 'pdf' | 'markdown' | 'text';

/**
 * Resource ingestion status
 */
export type IngestionStatus = 'pending' | 'processing' | 'completed' | 'failed';

/**
 * Resource read status
 */
export type ReadStatus = 'unread' | 'in_progress' | 'completed' | 'archived';

/**
 * Complete resource model
 */
export interface Resource {
  id: string;
  title: string;
  description?: string;
  creator?: string;
  publisher?: string;
  contributor?: string;
  source?: string;
  language?: string;
  type?: string;
  format?: string;
  identifier?: string;
  subject?: string[];
  relation?: string[];
  coverage?: string;
  rights?: string;
  classification_code?: string;
  read_status?: ReadStatus;
  quality_score?: number;
  quality_dimensions?: QualityDimensions;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  ingestion_status: IngestionStatus;
  ingestion_error?: string;
  ingestion_started_at?: string;
  ingestion_completed_at?: string;
  content?: string; // Full content (only in detail view)
  content_type?: ResourceContentType;
  file_path?: string;
  url?: string;
}

/**
 * Resource creation request
 */
export interface ResourceCreate {
  url: string;
  title?: string;
  description?: string;
  creator?: string;
  language?: string;
  type?: string;
  source?: string;
}

/**
 * Resource update request (partial)
 */
export interface ResourceUpdate {
  title?: string;
  description?: string;
  read_status?: ReadStatus;
  subject?: string[];
  creator?: string;
  publisher?: string;
  language?: string;
  type?: string;
}

/**
 * Resource list query parameters
 */
export interface ResourceListParams {
  q?: string;
  classification_code?: string;
  type?: string;
  format?: string;
  language?: string;
  read_status?: ReadStatus;
  min_quality?: number;
  created_from?: string;
  created_to?: string;
  updated_from?: string;
  updated_to?: string;
  subject_any?: string[];
  subject_all?: string[];
  creator?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}

/**
 * Resource list response
 */
export interface ResourceListResponse {
  items: Resource[];
  total: number;
}

/**
 * Processing status response
 */
export interface ProcessingStatus {
  id: string;
  ingestion_status: IngestionStatus;
  ingestion_error?: string;
  ingestion_started_at?: string;
  ingestion_completed_at?: string;
}

/**
 * Classification override request
 */
export interface ClassificationOverride {
  code: string;
}

// ============================================================================
// Chunk Types (Phase 17.5)
// ============================================================================

/**
 * Chunk metadata
 */
export interface ChunkMetadata {
  function_name?: string;
  class_name?: string;
  start_line: number;
  end_line: number;
  language: string;
  node_type?: string;
  page?: number;
  coordinates?: number[];
}

/**
 * Semantic chunk
 */
export interface SemanticChunk {
  id: string;
  resource_id: string;
  content: string;
  chunk_index: number;
  chunk_metadata: ChunkMetadata;
  embedding_id?: string;
  created_at: string;
}

/**
 * Chunking request
 */
export interface ChunkingRequest {
  strategy: 'semantic' | 'fixed';
  chunk_size: number;
  overlap: number;
  parser_type?: string;
}

/**
 * Chunking task response
 */
export interface ChunkingTask {
  resource_id: string;
  message: string;
  strategy: string;
  chunk_size: number;
  overlap: number;
}

/**
 * Chunk list response
 */
export interface ChunkListResponse {
  items: SemanticChunk[];
  total: number;
}

// ============================================================================
// Annotation Types
// ============================================================================

/**
 * Annotation model
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

/**
 * Annotation creation request
 */
export interface AnnotationCreate {
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color?: string;
  collection_ids?: string[];
}

/**
 * Annotation update request
 */
export interface AnnotationUpdate {
  note?: string;
  tags?: string[];
  color?: string;
  is_shared?: boolean;
}

/**
 * Annotation list response
 */
export interface AnnotationListResponse {
  items: Annotation[];
  total: number;
  page?: number;
  limit?: number;
}

/**
 * Annotation search result
 */
export interface AnnotationSearchResult {
  id: string;
  resource_id: string;
  resource_title: string;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  similarity_score?: number;
  created_at: string;
}

/**
 * Annotation search response
 */
export interface AnnotationSearchResponse {
  items: AnnotationSearchResult[];
  total: number;
  query: string;
}

/**
 * Annotation search parameters
 */
export interface AnnotationSearchParams {
  query: string;
  limit?: number;
}

/**
 * Tag search parameters
 */
export interface TagSearchParams {
  tags: string[];
  match_all?: boolean;
}

/**
 * Annotation export (JSON format)
 */
export type AnnotationExport = Annotation[];

// ============================================================================
// Quality Types
// ============================================================================

/**
 * Quality dimensions
 */
export interface QualityDimensions {
  accuracy: number;
  completeness: number;
  consistency: number;
  timeliness: number;
  relevance: number;
}

/**
 * Quality details response
 */
export interface QualityDetails {
  resource_id: string;
  quality_dimensions: QualityDimensions;
  quality_overall: number;
  quality_weights: QualityDimensions;
  quality_last_computed: string;
  quality_computation_version?: string;
  is_quality_outlier: boolean;
  needs_quality_review: boolean;
  outlier_score?: number;
  outlier_reasons?: string[];
}

/**
 * Quality recalculation request
 */
export interface QualityRecalculateRequest {
  resource_id?: string;
  resource_ids?: string[];
  weights?: QualityDimensions;
}

/**
 * Quality recalculation response
 */
export interface QualityRecalculateResponse {
  status: 'accepted';
  message: string;
}

/**
 * Quality outlier
 */
export interface QualityOutlier {
  resource_id: string;
  title: string;
  quality_overall: number;
  outlier_score: number;
  outlier_reasons: string[];
  needs_quality_review: boolean;
}

/**
 * Quality outliers response
 */
export interface QualityOutliersResponse {
  total: number;
  page: number;
  limit: number;
  outliers: QualityOutlier[];
}

/**
 * Quality outliers query parameters
 */
export interface QualityOutliersParams {
  page?: number;
  limit?: number;
  min_outlier_score?: number;
  reason?: string;
}

/**
 * Quality degradation item
 */
export interface QualityDegradationItem {
  resource_id: string;
  title: string;
  old_quality: number;
  new_quality: number;
  degradation_pct: number;
}

/**
 * Quality degradation response
 */
export interface QualityDegradation {
  time_window_days: number;
  degraded_count: number;
  degraded_resources: QualityDegradationItem[];
}

/**
 * Quality distribution bin
 */
export interface QualityDistributionBin {
  range: string;
  count: number;
}

/**
 * Quality distribution statistics
 */
export interface QualityStatistics {
  mean: number;
  median: number;
  std_dev: number;
}

/**
 * Quality distribution response
 */
export interface QualityDistribution {
  dimension: string;
  bins: number;
  distribution: QualityDistributionBin[];
  statistics: QualityStatistics;
}

/**
 * Quality trend data point
 */
export interface QualityTrendPoint {
  period: string;
  avg_quality: number;
  resource_count: number;
}

/**
 * Quality trends response
 */
export interface QualityTrend {
  dimension: string;
  granularity: 'daily' | 'weekly' | 'monthly';
  data_points: QualityTrendPoint[];
}

/**
 * Quality dimension score
 */
export interface QualityDimensionScore {
  avg: number;
  min: number;
  max: number;
}

/**
 * Quality dimensions response
 */
export interface QualityDimensionScores {
  dimensions: {
    accuracy: QualityDimensionScore;
    completeness: QualityDimensionScore;
    consistency: QualityDimensionScore;
    timeliness: QualityDimensionScore;
    relevance: QualityDimensionScore;
  };
  overall: QualityDimensionScore;
  total_resources: number;
}

/**
 * Review queue item
 */
export interface ReviewQueueItem {
  resource_id: string;
  title: string;
  quality_overall: number;
  is_quality_outlier: boolean;
  outlier_score: number;
  outlier_reasons: string[];
  quality_last_computed: string;
}

/**
 * Review queue response
 */
export interface ReviewQueueResponse {
  total: number;
  page: number;
  limit: number;
  review_queue: ReviewQueueItem[];
}

/**
 * Review queue query parameters
 */
export interface ReviewQueueParams {
  page?: number;
  limit?: number;
  sort_by?: 'outlier_score' | 'quality_overall' | 'updated_at';
}

// ============================================================================
// Graph/Hover Types
// ============================================================================

/**
 * Hover request parameters
 */
export interface HoverParams {
  resource_id: string;
  file_path: string;
  line: number;
  column: number;
}

/**
 * Location information for symbol definition
 */
export interface LocationInfo {
  file_path: string;
  line: number;
  column: number;
}

/**
 * Chunk reference for related chunks
 */
export interface ChunkReference {
  chunk_id: string;
  similarity_score: number;
  preview: string;
}

/**
 * Hover information response
 */
export interface HoverInfo {
  symbol_name: string | null;
  symbol_type: string | null;
  definition_location: LocationInfo | null;
  documentation: string | null;
  related_chunks: ChunkReference[];
  context_lines: string[];
}

// ============================================================================
// Health and Monitoring Types
// ============================================================================

/**
 * Component health status
 */
export interface ComponentHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  details?: string;
}

/**
 * Module health status
 */
export type ModuleHealth = 'healthy' | 'degraded' | 'unhealthy';

/**
 * System health response
 */
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  message: string;
  timestamp: string;
  components: {
    database: ComponentHealth;
    cache: ComponentHealth;
    event_bus: ComponentHealth;
  };
  modules: Record<string, ModuleHealth>;
}

/**
 * System metrics
 */
export interface SystemMetrics {
  status: 'success';
  timestamp: string;
  metrics: {
    resources: {
      total: number;
      by_status: Record<IngestionStatus, number>;
    };
    search: {
      queries_last_hour: number;
      avg_latency_ms: number;
    };
    quality: {
      avg_score: number;
    };
  };
}

// ============================================================================
// Error Types (Discriminated Unions)
// ============================================================================

/**
 * API error codes
 */
export type ApiErrorCode =
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'RATE_LIMITED'
  | 'SERVER_ERROR'
  | 'NETWORK_ERROR'
  | 'VALIDATION_ERROR'
  | 'INVALID_TOKEN';

/**
 * Base API error
 */
interface BaseApiError {
  code: ApiErrorCode;
  message: string;
  timestamp: string;
}

/**
 * Unauthorized error (401)
 */
export interface UnauthorizedError extends BaseApiError {
  code: 'UNAUTHORIZED' | 'INVALID_TOKEN';
}

/**
 * Forbidden error (403)
 */
export interface ForbiddenError extends BaseApiError {
  code: 'FORBIDDEN';
}

/**
 * Not found error (404)
 */
export interface NotFoundError extends BaseApiError {
  code: 'NOT_FOUND';
}

/**
 * Rate limit error (429)
 */
export interface RateLimitError extends BaseApiError {
  code: 'RATE_LIMITED';
  details: {
    retry_after: number; // Seconds until rate limit resets
    limit: number;
    reset: number; // Unix timestamp
  };
}

/**
 * Server error (500)
 */
export interface ServerError extends BaseApiError {
  code: 'SERVER_ERROR';
  details?: {
    error_id?: string;
  };
}

/**
 * Network error (connection failed)
 */
export interface NetworkError extends BaseApiError {
  code: 'NETWORK_ERROR';
}

/**
 * Validation error (400, 422)
 */
export interface ValidationError extends BaseApiError {
  code: 'VALIDATION_ERROR';
  details: {
    field: string;
    message: string;
  }[];
}

/**
 * Discriminated union of all API errors
 */
export type ApiError =
  | UnauthorizedError
  | ForbiddenError
  | NotFoundError
  | RateLimitError
  | ServerError
  | NetworkError
  | ValidationError;

/**
 * Type guard for API errors
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    'message' in error &&
    'timestamp' in error
  );
}

/**
 * Type guard for rate limit errors
 */
export function isRateLimitError(error: ApiError): error is RateLimitError {
  return error.code === 'RATE_LIMITED';
}

/**
 * Type guard for validation errors
 */
export function isValidationError(error: ApiError): error is ValidationError {
  return error.code === 'VALIDATION_ERROR';
}

/**
 * Type guard for network errors
 */
export function isNetworkError(error: ApiError): error is NetworkError {
  return error.code === 'NETWORK_ERROR';
}

// ============================================================================
// Pagination Types
// ============================================================================

/**
 * Generic pagination parameters
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

/**
 * Generic paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page?: number;
  limit?: number;
  offset?: number;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  meta?: {
    total?: number;
    page?: number;
    per_page?: number;
  };
}

/**
 * Generic success response
 */
export interface SuccessResponse {
  status: 'success' | 'accepted';
  message: string;
}

/**
 * Generic deletion response (204 No Content)
 */
export type DeleteResponse = void;
