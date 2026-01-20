/**
 * Resource type definitions
 * 
 * Matches backend schema from backend/app/modules/resources/schema.py
 */

/**
 * Resource ingestion status enum
 */
export enum ResourceStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

/**
 * Resource read status enum
 */
export enum ReadStatus {
  UNREAD = 'unread',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

/**
 * Main resource interface
 */
export interface Resource {
  id: string;
  title: string;
  description: string | null;
  creator: string | null;
  publisher: string | null;
  contributor: string | null;
  date_created: string | null;
  date_modified: string | null;
  type: string | null;
  format: string | null;
  identifier: string | null;
  source: string | null;
  url: string | null;
  language: string | null;
  coverage: string | null;
  rights: string | null;
  subject: string[];
  relation: string[];
  classification_code: string | null;
  read_status: ReadStatus;
  quality_score: number;
  created_at: string;
  updated_at: string;
  
  // Ingestion workflow fields
  ingestion_status: ResourceStatus;
  ingestion_error: string | null;
  ingestion_started_at: string | null;
  ingestion_completed_at: string | null;
}

/**
 * Paginated resource list response
 */
export interface ResourceListResponse {
  items: Resource[];
  total: number;
}

/**
 * Resource creation accepted response (202)
 */
export interface ResourceAccepted {
  id: string;
  status: string;
  title: string;
  ingestion_status: string;
}

/**
 * Lightweight resource status response for polling
 */
export interface ResourceStatusResponse {
  id: string;
  ingestion_status: ResourceStatus;
  ingestion_error: string | null;
  ingestion_started_at: string | null;
  ingestion_completed_at: string | null;
}

/**
 * Payload for ingesting a new resource
 */
export interface IngestResourcePayload {
  url: string; // Required - matches backend HttpUrl field
  title?: string;
  description?: string;
  type?: string;
  format?: string;
  language?: string;
  subject?: string[];
  creator?: string;
  publisher?: string;
  contributor?: string;
  source?: string;
}

/**
 * Query parameters for fetching resources
 */
export interface ResourceListParams {
  page?: number;
  limit?: number;
  sort?: string; // Format: "field:direction" e.g. "created_at:desc"
  q?: string;
  classification_code?: string;
  type?: string;
  format?: string;
  language?: string;
  read_status?: ReadStatus;
  min_quality?: number;
}
