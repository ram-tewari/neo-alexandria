/**
 * Search Feature Types
 * Defines interfaces for hybrid search functionality
 */

export interface SearchFilters {
  min_quality?: number; // 0.0 - 1.0
  resource_type?: string[];
  tags?: string[];
}

export type SearchMethod = 'hybrid' | 'semantic' | 'keyword';

export interface SearchRequest {
  text: string;
  hybrid_weight?: number; // 0.0 - 1.0, default 0.7
  filters?: SearchFilters;
  limit?: number;
  offset?: number;
}

export interface ScoreBreakdown {
  semantic_score?: number;
  keyword_score?: number;
  content_match?: number;
  metadata_match?: number;
}

export interface SearchResult {
  id: number;
  title: string;
  description: string;
  content?: string;
  url?: string;
  resource_type: string;
  score: number; // Composite hybrid score
  scores_breakdown?: ScoreBreakdown;
  quality_score?: number;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  page: number;
  per_page: number;
  query_time_ms?: number;
}

export interface SearchState {
  query: string;
  filters: SearchFilters;
  method: SearchMethod;
  hybridWeight: number;
}
