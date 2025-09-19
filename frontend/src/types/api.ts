// Neo Alexandria 2.0 Frontend - API Type Definitions
// Based on the backend API schemas and endpoints

export interface Resource {
  id: string;
  title: string;
  description?: string;
  creator?: string;
  publisher?: string;
  contributor?: string;
  date_created?: string;
  date_modified?: string;
  type?: string;
  format?: string;
  identifier?: string;
  source?: string;
  url?: string;
  language?: string;
  coverage?: string;
  rights?: string;
  subject: string[];
  relation: string[];
  classification_code?: string;
  read_status: 'unread' | 'in_progress' | 'completed' | 'archived';
  quality_score: number;
  created_at: string;
  updated_at: string;
  ingestion_status: 'pending' | 'completed' | 'failed';
  ingestion_error?: string;
  ingestion_started_at?: string;
  ingestion_completed_at?: string;
}

export interface ResourceStatus {
  id: string;
  ingestion_status: 'pending' | 'completed' | 'failed';
  ingestion_error?: string;
  ingestion_started_at?: string;
  ingestion_completed_at?: string;
}

export interface CreateResourceRequest {
  url: string;
  title?: string;
  description?: string;
  language?: string;
  type?: string;
  source?: string;
}

export interface CreateResourceResponse {
  id: string;
  status: string;
}

export interface UpdateResourceRequest {
  title?: string;
  description?: string;
  creator?: string;
  publisher?: string;
  contributor?: string;
  type?: string;
  format?: string;
  identifier?: string;
  source?: string;
  language?: string;
  coverage?: string;
  rights?: string;
  subject?: string[];
  relation?: string[];
  classification_code?: string;
  read_status?: 'unread' | 'in_progress' | 'completed' | 'archived';
  quality_score?: number;
}

export interface SearchFilters {
  classification_code?: string[];
  type?: string[];
  language?: string[];
  read_status?: ('unread' | 'in_progress' | 'completed' | 'archived')[];
  created_from?: string;
  created_to?: string;
  updated_from?: string;
  updated_to?: string;
  subject_any?: string[];
  subject_all?: string[];
  min_quality?: number;
}

export interface SearchQuery {
  text?: string;
  filters?: SearchFilters;
  limit?: number;
  offset?: number;
  sort_by?: 'relevance' | 'updated_at' | 'created_at' | 'quality_score' | 'title';
  sort_dir?: 'asc' | 'desc';
  hybrid_weight?: number; // 0.0 = keyword only, 1.0 = semantic only
}

export interface FacetBucket {
  key: string;
  count: number;
}

export interface Facets {
  classification_code: FacetBucket[];
  type: FacetBucket[];
  language: FacetBucket[];
  read_status: FacetBucket[];
  subject: FacetBucket[];
}

export interface SearchResults {
  total: number;
  items: Resource[];
  facets: Facets;
  snippets: Record<string, string>;
}

export interface ResourceListResponse {
  items: Resource[];
  total: number;
}

export interface RecommendedResource {
  url: string;
  title: string;
  snippet: string;
  relevance_score: number;
  reasoning: string[];
}

export interface RecommendationResponse {
  items: RecommendedResource[];
}

export interface GraphNode {
  id: string;
  title: string;
  type: string;
  classification_code?: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  details: {
    connection_type: 'vector' | 'subject' | 'classification' | 'hybrid';
    vector_similarity?: number;
    shared_subjects?: string[];
    classification_match?: boolean;
  };
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ClassificationNode {
  code: string;
  name: string;
  description: string;
  children: ClassificationNode[];
}

export interface ClassificationTree {
  tree: ClassificationNode[];
}

export interface QualityAnalysis {
  resource_id: string;
  metadata_completeness: number;
  readability: {
    flesch_kincaid: number;
    gunning_fog: number;
    automated_readability: number;
  };
  source_credibility: number;
  content_depth: number;
  overall_quality: number;
  quality_level: string;
  suggestions: string[];
}

export interface BatchUpdateRequest {
  resource_ids: string[];
  updates: UpdateResourceRequest;
}

export interface BatchUpdateResponse {
  updated_count: number;
  updated_resources: string[];
}

// Error response structure
export interface ApiError {
  detail: string;
  error_code?: string;
  timestamp?: string;
}

// Common response wrapper for API calls
export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

// Pagination parameters
export interface PaginationParams {
  limit?: number;
  offset?: number;
}

// Query parameters for resource listing
export interface ResourceQueryParams extends PaginationParams {
  q?: string;
  classification_code?: string;
  type?: string;
  language?: string;
  read_status?: string;
  min_quality?: number;
  created_from?: string;
  created_to?: string;
  updated_from?: string;
  updated_to?: string;
  subject_any?: string[];
  subject_all?: string[];
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}

// Ingestion status for UI state management
export type IngestionStatus = 'pending' | 'processing' | 'completed' | 'failed';

// UI-specific types
export interface ProcessingResource {
  id: string;
  url: string;
  title?: string;
  status: IngestionStatus;
  progress?: number;
  error?: string;
  startedAt: Date;
}

export interface FilterOption {
  value: string;
  label: string;
  count?: number;
}

export interface SearchState {
  query: string;
  filters: SearchFilters;
  results: SearchResults | null;
  isLoading: boolean;
  error: string | null;
  hybridWeight: number;
}

export interface LibraryState {
  resources: Resource[];
  total: number;
  isLoading: boolean;
  error: string | null;
  filters: ResourceQueryParams;
  selectedResources: string[];
}
