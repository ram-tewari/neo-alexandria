/**
 * Library Type Definitions for Neo Alexandria 2.0
 * 
 * This file contains TypeScript interfaces for the Living Library feature (Phase 3)
 * including document management, PDF viewing, scholarly assets, and collections.
 * 
 * Types match backend API schemas from:
 * - backend/docs/api/resources.md
 * - backend/docs/api/scholarly.md
 * - backend/docs/api/collections.md
 */

// ============================================================================
// Resource Types (Extended for Library)
// ============================================================================

/**
 * Complete resource model for library view
 * Extends the base Resource type with library-specific fields
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
  read_status?: 'unread' | 'in_progress' | 'completed' | 'archived';
  quality_score?: number;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  ingestion_status: 'pending' | 'processing' | 'completed' | 'failed';
  ingestion_error?: string;
  content?: string;
  content_type?: 'code' | 'pdf' | 'markdown' | 'text';
  file_path?: string;
  url?: string;
  thumbnail_url?: string; // Generated thumbnail for grid view
  page_count?: number; // For PDF documents
  file_size?: number; // In bytes
  authors?: string[]; // Parsed from creator field
  publication_date?: string; // ISO 8601
}

/**
 * Resource upload request
 * Used for multipart/form-data file uploads
 */
export interface ResourceUpload {
  file: File;
  metadata?: {
    title?: string;
    description?: string;
    creator?: string;
    language?: string;
    type?: string;
    source?: string;
  };
}

/**
 * Resource update request (partial)
 * Used for PATCH/PUT operations
 */
export interface ResourceUpdate {
  title?: string;
  description?: string;
  read_status?: 'unread' | 'in_progress' | 'completed' | 'archived';
  subject?: string[];
  creator?: string;
  publisher?: string;
  language?: string;
  type?: string;
}

/**
 * Repository ingestion request
 */
export interface RepositoryIngestRequest {
  repo_url: string;
  branch?: string;
}

/**
 * Repository ingestion response
 */
export interface RepositoryIngestResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}

// ============================================================================
// Scholarly Asset Types
// ============================================================================

/**
 * Mathematical equation extracted from document
 */
export interface Equation {
  id: string;
  resource_id: string;
  equation_number: number;
  latex_source: string;
  rendered_html?: string;
  page_number?: number;
  position?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  context_before?: string;
  context_after?: string;
  is_inline: boolean;
  created_at: string;
}

/**
 * Table extracted from document
 */
export interface Table {
  id: string;
  resource_id: string;
  table_number: number;
  caption?: string;
  headers: string[];
  rows: string[][];
  page_number?: number;
  position?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  format: 'csv' | 'json' | 'html';
  created_at: string;
}

/**
 * Document metadata with completeness tracking
 */
export interface Metadata {
  resource_id: string;
  title?: string;
  authors?: string[];
  publication_date?: string;
  publisher?: string;
  doi?: string;
  isbn?: string;
  abstract?: string;
  keywords?: string[];
  citations?: string[];
  references?: string[];
  completeness_score: number; // 0-100
  missing_fields: string[];
  last_updated: string;
}

/**
 * Metadata completeness statistics
 */
export interface CompletenessStats {
  total_resources: number;
  avg_completeness: number;
  completeness_distribution: {
    range: string; // e.g., "0-20", "20-40"
    count: number;
  }[];
  most_missing_fields: {
    field: string;
    missing_count: number;
  }[];
}

// ============================================================================
// Collection Types
// ============================================================================

/**
 * Collection model
 */
export interface Collection {
  id: string;
  name: string;
  description?: string;
  tags?: string[];
  resource_count: number;
  created_at: string;
  updated_at: string;
  thumbnail_url?: string; // Generated from first resource
  owner_id?: string;
  is_public: boolean;
}

/**
 * Collection creation request
 */
export interface CollectionCreate {
  name: string;
  description?: string;
  tags?: string[];
  is_public?: boolean;
}

/**
 * Collection update request (partial)
 */
export interface CollectionUpdate {
  name?: string;
  description?: string;
  tags?: string[];
  is_public?: boolean;
}

/**
 * Collection with resources
 */
export interface CollectionWithResources extends Collection {
  resources: Resource[];
}

/**
 * Similar collection result
 */
export interface SimilarCollection {
  collection: Collection;
  similarity: number;
  common_resources: number;
  common_tags: string[];
}

/**
 * Batch operation result
 */
export interface BatchOperationResult {
  added?: number;
  removed?: number;
  failed: string[]; // Resource IDs that failed
  errors?: {
    resource_id: string;
    error: string;
  }[];
}

/**
 * Collection statistics
 */
export interface CollectionStats {
  collection_id: string;
  total_documents: number;
  document_types: {
    type: string;
    count: number;
  }[];
  avg_quality_score: number;
  date_range: {
    earliest: string;
    latest: string;
  };
  top_tags: {
    tag: string;
    count: number;
  }[];
  top_authors: {
    author: string;
    count: number;
  }[];
}

// ============================================================================
// PDF Viewer Types
// ============================================================================

/**
 * PDF highlight
 */
export interface PDFHighlight {
  id: string;
  resource_id: string;
  page_number: number;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  color: string;
  text: string;
  note?: string;
  created_at: string;
}

/**
 * PDF annotation (extends highlight with more features)
 */
export interface PDFAnnotation extends PDFHighlight {
  tags?: string[];
  is_shared: boolean;
  collection_ids?: string[];
}

/**
 * PDF viewer state
 */
export interface PDFViewerState {
  currentPage: number;
  totalPages: number;
  zoom: number;
  rotation: number; // 0, 90, 180, 270
  viewMode: 'single' | 'continuous' | 'double';
  highlights: PDFHighlight[];
}

// ============================================================================
// Auto-Linking Types
// ============================================================================

/**
 * Related code file suggestion
 */
export interface RelatedCodeFile {
  resource_id: string;
  file_path: string;
  title: string;
  similarity_score: number;
  explanation: string;
  preview: string; // First few lines of code
  language: string;
}

/**
 * Related paper suggestion
 */
export interface RelatedPaper {
  resource_id: string;
  title: string;
  authors?: string[];
  similarity_score: number;
  relationship_type: 'cites' | 'cited_by' | 'similar' | 'extends';
  explanation: string;
  abstract?: string;
}

/**
 * Manual link creation request
 */
export interface LinkCreate {
  source_resource_id: string;
  target_resource_id: string;
  link_type: 'cites' | 'implements' | 'extends' | 'related';
  description?: string;
}

/**
 * Resource link
 */
export interface ResourceLink {
  id: string;
  source_resource_id: string;
  target_resource_id: string;
  link_type: 'cites' | 'implements' | 'extends' | 'related';
  description?: string;
  created_at: string;
  created_by?: string;
}

// ============================================================================
// Search Types
// ============================================================================

/**
 * Document search parameters
 */
export interface DocumentSearchParams {
  query: string;
  type?: 'pdf' | 'code' | 'markdown' | 'text';
  limit?: number;
  offset?: number;
  filters?: {
    quality_min?: number;
    quality_max?: number;
    date_from?: string;
    date_to?: string;
    authors?: string[];
    tags?: string[];
  };
}

/**
 * Document search result
 */
export interface DocumentSearchResult {
  resource: Resource;
  score: number;
  highlights: {
    field: string;
    snippets: string[];
  }[];
}

/**
 * Document search response
 */
export interface DocumentSearchResponse {
  results: DocumentSearchResult[];
  total: number;
  query: string;
  took_ms: number;
}

// ============================================================================
// Filter and Sort Types
// ============================================================================

/**
 * Document filter options
 */
export interface DocumentFilters {
  type?: 'pdf' | 'code' | 'markdown' | 'text';
  quality_min?: number;
  quality_max?: number;
  date_from?: string;
  date_to?: string;
  read_status?: 'unread' | 'in_progress' | 'completed' | 'archived';
  authors?: string[];
  tags?: string[];
  search?: string;
}

/**
 * Document sort options
 */
export interface DocumentSort {
  field: 'date' | 'title' | 'quality' | 'author';
  order: 'asc' | 'desc';
}

// ============================================================================
// Upload Progress Types
// ============================================================================

/**
 * Upload progress event
 */
export interface UploadProgress {
  resource_id?: string; // Temporary ID during upload
  file_name: string;
  loaded: number; // Bytes uploaded
  total: number; // Total bytes
  percentage: number; // 0-100
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  error?: string;
}

// ============================================================================
// List Response Types
// ============================================================================

/**
 * Resource list response
 */
export interface ResourceListResponse {
  resources: Resource[];
  total: number;
  page?: number;
  limit?: number;
}

/**
 * Collection list response
 */
export interface CollectionListResponse {
  collections: Collection[];
  total: number;
  page?: number;
  limit?: number;
}

/**
 * Equation list response
 */
export interface EquationListResponse {
  equations: Equation[];
  total: number;
}

/**
 * Table list response
 */
export interface TableListResponse {
  tables: Table[];
  total: number;
}

// ============================================================================
// Export Types
// ============================================================================

/**
 * Export format options
 */
export type ExportFormat = 'json' | 'csv' | 'markdown' | 'bibtex';

/**
 * Export request
 */
export interface ExportRequest {
  resource_ids: string[];
  format: ExportFormat;
  include_annotations?: boolean;
  include_metadata?: boolean;
}

/**
 * Export response
 */
export interface ExportResponse {
  download_url: string;
  format: ExportFormat;
  file_size: number;
  expires_at: string;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Type guard for Resource
 */
export function isResource(obj: unknown): obj is Resource {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'title' in obj &&
    'ingestion_status' in obj
  );
}

/**
 * Type guard for Collection
 */
export function isCollection(obj: unknown): obj is Collection {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    'resource_count' in obj
  );
}

/**
 * Type guard for Equation
 */
export function isEquation(obj: unknown): obj is Equation {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'latex_source' in obj &&
    'equation_number' in obj
  );
}

/**
 * Type guard for Table
 */
export function isTable(obj: unknown): obj is Table {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'headers' in obj &&
    'rows' in obj &&
    'table_number' in obj
  );
}
