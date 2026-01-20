/**
 * Resource Types
 * 
 * Type definitions for resources matching backend schema
 */

import type { ReadStatus, IngestionStatus } from './api';

// Re-export types for convenience
export type { ReadStatus, IngestionStatus };

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
  language: string | null;
  coverage: string | null;
  rights: string | null;
  subject: string[];
  relation: string[];
  classification_code: string | null;
  read_status: ReadStatus;
  quality_score: number;
  url: string | null;
  created_at: string;
  updated_at: string;
  ingestion_status: IngestionStatus;
  ingestion_error: string | null;
  ingestion_started_at: string | null;
  ingestion_completed_at: string | null;
}

export interface ResourceCreate {
  title: string;
  description?: string;
  creator?: string;
  publisher?: string;
  contributor?: string;
  source?: string;
  subject?: string[];
  classification_code?: string;
  type?: string;
  format?: string;
}

export interface ResourceUpdate {
  title?: string;
  description?: string;
  creator?: string;
  publisher?: string;
  read_status?: ReadStatus;
  subject?: string[];
  classification_code?: string;
  type?: string;
}

export interface ResourceListParams {
  page?: number;
  limit?: number;
  sort_by?: 'created_at' | 'updated_at' | 'quality_score' | 'title';
  sort_order?: 'asc' | 'desc';
  read_status?: ReadStatus;
  quality_min?: number;
  quality_max?: number;
  search?: string;
  tags?: string[];
}

export interface ResourceSummary {
  id: string;
  title: string;
  quality_score: number;
  classification_code: string | null;
  type?: string | null;
  subject?: string[];
  creator?: string | null;
  read_status?: ReadStatus;
  description?: string | null;
}
