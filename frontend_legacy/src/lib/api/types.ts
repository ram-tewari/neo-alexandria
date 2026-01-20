/**
 * API type definitions matching backend Pydantic models
 */

// ============================================================================
// Resource Types
// ============================================================================

export type IngestionStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ReadStatus = 'unread' | 'in_progress' | 'completed' | 'archived';

export interface ResourceRead {
  id: string;
  title: string;
  creator?: string;
  subject?: string[];
  description?: string;
  publisher?: string;
  contributor?: string;
  date?: string;
  type?: string;
  format?: string;
  identifier?: string;
  source?: string;
  language?: string;
  relation?: string;
  coverage?: string;
  rights?: string;
  
  // Neo Alexandria specific fields
  url?: string;
  content_text?: string;
  content_html?: string;
  classification_code?: string;
  quality_score?: number;
  embedding_model?: string;
  has_embedding: boolean;
  ingestion_status: IngestionStatus;
  ingestion_error?: string;
  read_status?: ReadStatus;
  
  // Timestamps
  date_created: string;
  date_modified: string;
  date_ingested?: string;
}

export interface ResourceIngestRequest {
  url?: string;
  file?: File;
  title?: string;
  creator?: string;
  subject?: string[];
  description?: string;
  language?: string;
  type?: string;
}

export interface ResourceUpdate {
  title?: string;
  creator?: string;
  subject?: string[];
  description?: string;
  publisher?: string;
  contributor?: string;
  date?: string;
  type?: string;
  format?: string;
  identifier?: string;
  source?: string;
  language?: string;
  relation?: string;
  coverage?: string;
  rights?: string;
  classification_code?: string;
  read_status?: ReadStatus;
}

export interface ResourceAccepted {
  id: string;
  message: string;
  status: IngestionStatus;
}

export interface ResourceStatus {
  id: string;
  ingestion_status: IngestionStatus;
  ingestion_error?: string;
  date_ingested?: string;
  has_embedding: boolean;
}

export interface ResourceListParams {
  limit?: number;
  offset?: number;
  q?: string;
  classification_code?: string;
  language?: string;
  min_quality?: number;
  max_quality?: number;
  subject?: string;
  type?: string;
  read_status?: ReadStatus;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface ResourceListResponse {
  items: ResourceRead[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================================
// Quality Types
// ============================================================================

export interface QualityDimension {
  name: string;
  score: number;
  weight: number;
}

export interface QualityDetails {
  resource_id: string;
  overall_score: number;
  dimensions: QualityDimension[];
  is_outlier: boolean;
  calculated_at: string;
}

// ============================================================================
// Graph Types
// ============================================================================

export interface GraphNeighbor {
  resource_id: string;
  title: string;
  similarity_score: number;
  relationship_type: 'semantic' | 'classification' | 'subject';
}

export interface GraphNeighborsResponse {
  resource_id: string;
  neighbors: GraphNeighbor[];
}

// ============================================================================
// Collection Types (Legacy - keeping for compatibility)
// ============================================================================

export interface Collection {
  id: string;
  name: string;
  description?: string;
  resource_count: number;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Error Types
// ============================================================================

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// ============================================================================
// Pagination Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================================
// Legacy Types (for backward compatibility)
// ============================================================================

export interface Resource {
  id: string;
  title: string;
  url: string;
  resource_type: 'article' | 'video' | 'book' | 'paper';
  description?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  metadata?: Record<string, unknown>;
}

export interface SearchResult {
  resources: Resource[];
  total: number;
  page: number;
  page_size: number;
}

export interface ListParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface CreateResourceDto {
  title: string;
  url: string;
  resource_type: Resource['resource_type'];
  description?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface UpdateResourceDto extends Partial<CreateResourceDto> {}

/**
 * API client interface
 */
export interface ApiClient {
  resources: {
    list: (params?: ListParams) => Promise<SearchResult>;
    get: (id: string) => Promise<Resource>;
    create: (data: CreateResourceDto) => Promise<Resource>;
    update: (id: string, data: UpdateResourceDto) => Promise<Resource>;
    delete: (id: string) => Promise<void>;
  };
  collections: {
    list: () => Promise<Collection[]>;
    get: (id: string) => Promise<Collection>;
  };
  search: (query: string) => Promise<SearchResult>;
}
