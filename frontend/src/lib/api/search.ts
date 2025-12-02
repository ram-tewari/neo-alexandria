/**
 * Search API Client
 * Provides typed methods for all search operations
 */

import { apiRequest, API_BASE_URL } from './apiUtils';
import type { ResourceRead } from './types';

// --- Types ---

export type SearchMethod = 'fts5' | 'vector' | 'hybrid';

export interface SearchFilters {
  classification?: string;
  min_quality?: number;
  max_quality?: number;
  date_from?: string; // ISO date string
  date_to?: string;   // ISO date string
  [key: string]: any;
}

export interface BooleanClause {
  operator: 'AND' | 'OR' | 'NOT';
  field: string;
  value: string;
}

export interface SearchWeights {
  keyword: number;  // 0-100
  semantic: number; // 0-100
}

export interface SearchRequest {
  query: string;
  filters?: SearchFilters;
  method?: SearchMethod;
  limit?: number;
  offset?: number;
  boolean_clauses?: BooleanClause[];
  weights?: SearchWeights;
}

export interface SearchExplanation {
  score: number;
  matched_fields: string[];
  vector_similarity?: number;
  keyword_score?: number;
  description?: string;
}

export interface SearchResultItem {
  resource: ResourceRead;
  score: number;
  explanation?: SearchExplanation;
  highlights?: Record<string, string[]>; // field -> matched fragments
}

export interface SearchResponse {
  items: SearchResultItem[];
  total: number;
  page: number;
  pages: number;
  took_ms: number;
}

export interface SearchHistoryItem {
  id: string;
  query: string;
  timestamp: number;
  filters?: SearchFilters;
}

export interface SavedSearch {
  id: string;
  name: string;
  description?: string;
  request: SearchRequest;
  createdAt: number;
}

// --- API Client ---

export const searchApi = {
  /**
   * Perform a global search (quick search)
   */
  async globalSearch(query: string, filters?: SearchFilters, limit: number = 5): Promise<SearchResponse> {
    return apiRequest<SearchResponse>('/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        filters,
        limit,
        method: 'hybrid', // Default to hybrid for global search
      }),
    });
  },

  /**
   * Perform an advanced search
   */
  async search(request: SearchRequest): Promise<SearchResponse> {
    return apiRequest<SearchResponse>('/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Compare search methods (FTS5 vs Vector vs Hybrid)
   */
  async compareMethods(query: string): Promise<Record<SearchMethod, SearchResponse>> {
    const searchParams = new URLSearchParams({ query });
    return apiRequest<Record<SearchMethod, SearchResponse>>(`/search/compare-methods?${searchParams.toString()}`);
  },

  /**
   * Get three-way hybrid results (experimental)
   */
  async threeWayHybrid(query: string): Promise<SearchResponse> {
    const searchParams = new URLSearchParams({ query });
    return apiRequest<SearchResponse>(`/search/three-way-hybrid?${searchParams.toString()}`);
  },
};

export default searchApi;
