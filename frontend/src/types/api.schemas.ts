/**
 * Zod Runtime Validation Schemas for API Types
 * 
 * This file contains zod schemas that mirror the TypeScript interfaces in api.ts
 * Used for runtime validation in development mode to catch type mismatches
 * between frontend and backend.
 * 
 * @see frontend/src/types/api.ts for TypeScript type definitions
 */

import { z } from 'zod';

// ============================================================================
// User and Authentication Schemas
// ============================================================================

export const UserSchema = z.object({
  id: z.string(),
  username: z.string(),
  email: z.string().email(),
  tier: z.enum(['free', 'premium', 'admin']),
  is_active: z.boolean(),
});

export const TokenResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.literal('bearer'),
});

export const LoginRequestSchema = z.object({
  username: z.string(),
  password: z.string(),
  scopes: z.string().optional(),
});

export const RefreshTokenRequestSchema = z.object({
  refresh_token: z.string(),
});

export const RateLimitStatusSchema = z.object({
  tier: z.enum(['free', 'premium', 'admin']),
  limit: z.number(),
  remaining: z.number(),
  reset: z.number(),
});

// ============================================================================
// Resource Schemas
// ============================================================================

export const ResourceContentTypeSchema = z.enum(['code', 'pdf', 'markdown', 'text']);
export const IngestionStatusSchema = z.enum(['pending', 'processing', 'completed', 'failed']);
export const ReadStatusSchema = z.enum(['unread', 'in_progress', 'completed', 'archived']);

export const QualityDimensionsSchema = z.object({
  accuracy: z.number(),
  completeness: z.number(),
  consistency: z.number(),
  timeliness: z.number(),
  relevance: z.number(),
});

export const ResourceSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  creator: z.string().optional(),
  publisher: z.string().optional(),
  contributor: z.string().optional(),
  source: z.string().optional(),
  language: z.string().optional(),
  type: z.string().optional(),
  format: z.string().optional(),
  identifier: z.string().optional(),
  subject: z.array(z.string()).optional(),
  relation: z.array(z.string()).optional(),
  coverage: z.string().optional(),
  rights: z.string().optional(),
  classification_code: z.string().optional(),
  read_status: ReadStatusSchema.optional(),
  quality_score: z.number().optional(),
  quality_dimensions: QualityDimensionsSchema.optional(),
  created_at: z.string(),
  updated_at: z.string(),
  ingestion_status: IngestionStatusSchema,
  ingestion_error: z.string().optional(),
  ingestion_started_at: z.string().optional(),
  ingestion_completed_at: z.string().optional(),
  content: z.string().optional(),
  content_type: ResourceContentTypeSchema.optional(),
  file_path: z.string().optional(),
  url: z.string().optional(),
});

export const ResourceCreateSchema = z.object({
  url: z.string(),
  title: z.string().optional(),
  description: z.string().optional(),
  creator: z.string().optional(),
  language: z.string().optional(),
  type: z.string().optional(),
  source: z.string().optional(),
});

export const ResourceUpdateSchema = z.object({
  title: z.string().optional(),
  description: z.string().optional(),
  read_status: ReadStatusSchema.optional(),
  subject: z.array(z.string()).optional(),
  creator: z.string().optional(),
  publisher: z.string().optional(),
  language: z.string().optional(),
  type: z.string().optional(),
});

export const ResourceListParamsSchema = z.object({
  q: z.string().optional(),
  classification_code: z.string().optional(),
  type: z.string().optional(),
  format: z.string().optional(),
  language: z.string().optional(),
  read_status: ReadStatusSchema.optional(),
  min_quality: z.number().optional(),
  created_from: z.string().optional(),
  created_to: z.string().optional(),
  updated_from: z.string().optional(),
  updated_to: z.string().optional(),
  subject_any: z.array(z.string()).optional(),
  subject_all: z.array(z.string()).optional(),
  creator: z.string().optional(),
  limit: z.number().optional(),
  offset: z.number().optional(),
  sort_by: z.string().optional(),
  sort_dir: z.enum(['asc', 'desc']).optional(),
});

export const ResourceListResponseSchema = z.object({
  items: z.array(ResourceSchema),
  total: z.number(),
});

export const ProcessingStatusSchema = z.object({
  id: z.string(),
  ingestion_status: IngestionStatusSchema,
  ingestion_error: z.string().optional(),
  ingestion_started_at: z.string().optional(),
  ingestion_completed_at: z.string().optional(),
});

export const ClassificationOverrideSchema = z.object({
  code: z.string(),
});

// ============================================================================
// Chunk Schemas
// ============================================================================

export const ChunkMetadataSchema = z.object({
  function_name: z.string().optional(),
  class_name: z.string().optional(),
  start_line: z.number(),
  end_line: z.number(),
  language: z.string(),
  node_type: z.string().optional(),
  page: z.number().optional(),
  coordinates: z.array(z.number()).optional(),
});

export const SemanticChunkSchema = z.object({
  id: z.string(),
  resource_id: z.string(),
  content: z.string(),
  chunk_index: z.number(),
  chunk_metadata: ChunkMetadataSchema,
  embedding_id: z.string().optional(),
  created_at: z.string(),
});

export const ChunkingRequestSchema = z.object({
  strategy: z.enum(['semantic', 'fixed']),
  chunk_size: z.number(),
  overlap: z.number(),
  parser_type: z.string().optional(),
});

export const ChunkingTaskSchema = z.object({
  resource_id: z.string(),
  message: z.string(),
  strategy: z.string(),
  chunk_size: z.number(),
  overlap: z.number(),
});

export const ChunkListResponseSchema = z.object({
  items: z.array(SemanticChunkSchema),
  total: z.number(),
});

// ============================================================================
// Annotation Schemas
// ============================================================================

export const AnnotationSchema = z.object({
  id: z.string(),
  resource_id: z.string(),
  user_id: z.string(),
  start_offset: z.number(),
  end_offset: z.number(),
  highlighted_text: z.string(),
  note: z.string().optional(),
  tags: z.array(z.string()).optional(),
  color: z.string(),
  context_before: z.string().optional(),
  context_after: z.string().optional(),
  is_shared: z.boolean(),
  collection_ids: z.array(z.string()).optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const AnnotationCreateSchema = z.object({
  start_offset: z.number(),
  end_offset: z.number(),
  highlighted_text: z.string(),
  note: z.string().optional(),
  tags: z.array(z.string()).optional(),
  color: z.string().optional(),
  collection_ids: z.array(z.string()).optional(),
});

export const AnnotationUpdateSchema = z.object({
  note: z.string().optional(),
  tags: z.array(z.string()).optional(),
  color: z.string().optional(),
  is_shared: z.boolean().optional(),
});

export const AnnotationListResponseSchema = z.object({
  items: z.array(AnnotationSchema),
  total: z.number(),
  page: z.number().optional(),
  limit: z.number().optional(),
});

export const AnnotationSearchResultSchema = z.object({
  id: z.string(),
  resource_id: z.string(),
  resource_title: z.string(),
  highlighted_text: z.string(),
  note: z.string().optional(),
  tags: z.array(z.string()).optional(),
  similarity_score: z.number().optional(),
  created_at: z.string(),
});

export const AnnotationSearchResponseSchema = z.object({
  items: z.array(AnnotationSearchResultSchema),
  total: z.number(),
  query: z.string(),
});

export const AnnotationSearchParamsSchema = z.object({
  query: z.string(),
  limit: z.number().optional(),
});

export const TagSearchParamsSchema = z.object({
  tags: z.array(z.string()),
  match_all: z.boolean().optional(),
});

export const AnnotationExportSchema = z.array(AnnotationSchema);

// ============================================================================
// Quality Schemas
// ============================================================================

export const QualityDetailsSchema = z.object({
  resource_id: z.string(),
  quality_dimensions: QualityDimensionsSchema,
  quality_overall: z.number(),
  quality_weights: QualityDimensionsSchema,
  quality_last_computed: z.string(),
  quality_computation_version: z.string().optional(),
  is_quality_outlier: z.boolean(),
  needs_quality_review: z.boolean(),
  outlier_score: z.number().optional(),
  outlier_reasons: z.array(z.string()).optional(),
});

export const QualityRecalculateRequestSchema = z.object({
  resource_id: z.string().optional(),
  resource_ids: z.array(z.string()).optional(),
  weights: QualityDimensionsSchema.optional(),
});

export const QualityRecalculateResponseSchema = z.object({
  status: z.literal('accepted'),
  message: z.string(),
});

export const QualityOutlierSchema = z.object({
  resource_id: z.string(),
  title: z.string(),
  quality_overall: z.number(),
  outlier_score: z.number(),
  outlier_reasons: z.array(z.string()),
  needs_quality_review: z.boolean(),
});

export const QualityOutliersResponseSchema = z.object({
  total: z.number(),
  page: z.number(),
  limit: z.number(),
  outliers: z.array(QualityOutlierSchema),
});

export const QualityOutliersParamsSchema = z.object({
  page: z.number().optional(),
  limit: z.number().optional(),
  min_outlier_score: z.number().optional(),
  reason: z.string().optional(),
});

export const QualityDegradationItemSchema = z.object({
  resource_id: z.string(),
  title: z.string(),
  old_quality: z.number(),
  new_quality: z.number(),
  degradation_pct: z.number(),
});

export const QualityDegradationSchema = z.object({
  time_window_days: z.number(),
  degraded_count: z.number(),
  degraded_resources: z.array(QualityDegradationItemSchema),
});

export const QualityDistributionBinSchema = z.object({
  range: z.string(),
  count: z.number(),
});

export const QualityStatisticsSchema = z.object({
  mean: z.number(),
  median: z.number(),
  std_dev: z.number(),
});

export const QualityDistributionSchema = z.object({
  dimension: z.string(),
  bins: z.number(),
  distribution: z.array(QualityDistributionBinSchema),
  statistics: QualityStatisticsSchema,
});

export const QualityTrendPointSchema = z.object({
  period: z.string(),
  avg_quality: z.number(),
  resource_count: z.number(),
});

export const QualityTrendSchema = z.object({
  dimension: z.string(),
  granularity: z.enum(['daily', 'weekly', 'monthly']),
  data_points: z.array(QualityTrendPointSchema),
});

export const QualityDimensionScoreSchema = z.object({
  avg: z.number(),
  min: z.number(),
  max: z.number(),
});

export const QualityDimensionScoresSchema = z.object({
  dimensions: z.object({
    accuracy: QualityDimensionScoreSchema,
    completeness: QualityDimensionScoreSchema,
    consistency: QualityDimensionScoreSchema,
    timeliness: QualityDimensionScoreSchema,
    relevance: QualityDimensionScoreSchema,
  }),
  overall: QualityDimensionScoreSchema,
  total_resources: z.number(),
});

export const ReviewQueueItemSchema = z.object({
  resource_id: z.string(),
  title: z.string(),
  quality_overall: z.number(),
  is_quality_outlier: z.boolean(),
  outlier_score: z.number(),
  outlier_reasons: z.array(z.string()),
  quality_last_computed: z.string(),
});

export const ReviewQueueResponseSchema = z.object({
  total: z.number(),
  page: z.number(),
  limit: z.number(),
  review_queue: z.array(ReviewQueueItemSchema),
});

export const ReviewQueueParamsSchema = z.object({
  page: z.number().optional(),
  limit: z.number().optional(),
  sort_by: z.enum(['outlier_score', 'quality_overall', 'updated_at']).optional(),
});

// ============================================================================
// Graph/Hover Schemas
// ============================================================================

export const HoverParamsSchema = z.object({
  resource_id: z.string(),
  symbol: z.string(),
  line: z.number().optional(),
  column: z.number().optional(),
  language: z.string().optional(),
});

export const LocationInfoSchema = z.object({
  file_path: z.string(),
  line: z.number(),
  column: z.number(),
});

export const ChunkReferenceSchema = z.object({
  chunk_id: z.string(),
  similarity_score: z.number(),
  preview: z.string(),
});

export const HoverInfoSchema = z.object({
  symbol_name: z.string().nullable(),
  symbol_type: z.string().nullable(),
  definition_location: LocationInfoSchema.nullable(),
  documentation: z.string().nullable(),
  related_chunks: z.array(ChunkReferenceSchema),
  context_lines: z.array(z.string()),
});

// ============================================================================
// Health and Monitoring Schemas
// ============================================================================

export const ComponentHealthSchema = z.object({
  status: z.enum(['healthy', 'degraded', 'unhealthy']),
  details: z.string().optional(),
});

export const ModuleHealthSchema = z.enum(['healthy', 'degraded', 'unhealthy']);

export const HealthStatusSchema = z.object({
  status: z.enum(['healthy', 'degraded', 'unhealthy']),
  message: z.string(),
  timestamp: z.string(),
  components: z.object({
    database: ComponentHealthSchema,
    cache: ComponentHealthSchema,
    event_bus: ComponentHealthSchema,
  }),
  modules: z.record(z.string(), ModuleHealthSchema),
});

export const SystemMetricsSchema = z.object({
  status: z.literal('success'),
  timestamp: z.string(),
  metrics: z.object({
    resources: z.object({
      total: z.number(),
      by_status: z.record(IngestionStatusSchema, z.number()),
    }),
    search: z.object({
      queries_last_hour: z.number(),
      avg_latency_ms: z.number(),
    }),
    quality: z.object({
      avg_score: z.number(),
    }),
  }),
});

// ============================================================================
// Error Schemas
// ============================================================================

export const ApiErrorCodeSchema = z.enum([
  'UNAUTHORIZED',
  'FORBIDDEN',
  'NOT_FOUND',
  'RATE_LIMITED',
  'SERVER_ERROR',
  'NETWORK_ERROR',
  'VALIDATION_ERROR',
  'INVALID_TOKEN',
]);

export const BaseApiErrorSchema = z.object({
  code: ApiErrorCodeSchema,
  message: z.string(),
  timestamp: z.string(),
});

export const UnauthorizedErrorSchema = BaseApiErrorSchema.extend({
  code: z.enum(['UNAUTHORIZED', 'INVALID_TOKEN']),
});

export const ForbiddenErrorSchema = BaseApiErrorSchema.extend({
  code: z.literal('FORBIDDEN'),
});

export const NotFoundErrorSchema = BaseApiErrorSchema.extend({
  code: z.literal('NOT_FOUND'),
});

export const RateLimitErrorSchema = BaseApiErrorSchema.extend({
  code: z.literal('RATE_LIMITED'),
  details: z.object({
    retry_after: z.number(),
    limit: z.number(),
    reset: z.number(),
  }),
});

export const ServerErrorSchema = BaseApiErrorSchema.extend({
  code: z.literal('SERVER_ERROR'),
  details: z.object({
    error_id: z.string().optional(),
  }).optional(),
});

export const NetworkErrorSchema = BaseApiErrorSchema.extend({
  code: z.literal('NETWORK_ERROR'),
});

export const ValidationErrorSchema = BaseApiErrorSchema.extend({
  code: z.literal('VALIDATION_ERROR'),
  details: z.array(z.object({
    field: z.string(),
    message: z.string(),
  })),
});

export const ApiErrorSchema = z.discriminatedUnion('code', [
  UnauthorizedErrorSchema,
  ForbiddenErrorSchema,
  NotFoundErrorSchema,
  RateLimitErrorSchema,
  ServerErrorSchema,
  NetworkErrorSchema,
  ValidationErrorSchema,
]);

// ============================================================================
// Pagination Schemas
// ============================================================================

export const PaginationParamsSchema = z.object({
  page: z.number().optional(),
  limit: z.number().optional(),
  offset: z.number().optional(),
});

export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    items: z.array(itemSchema),
    total: z.number(),
    page: z.number().optional(),
    limit: z.number().optional(),
    offset: z.number().optional(),
  });

// ============================================================================
// Utility Schemas
// ============================================================================

export const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    data: dataSchema,
    meta: z.object({
      total: z.number().optional(),
      page: z.number().optional(),
      per_page: z.number().optional(),
    }).optional(),
  });

export const SuccessResponseSchema = z.object({
  status: z.enum(['success', 'accepted']),
  message: z.string(),
});

// DeleteResponse is void, no schema needed
