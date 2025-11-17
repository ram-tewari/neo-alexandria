/**
 * Search API
 * 
 * API endpoints for search functionality
 * Matches backend format (no /api prefix)
 */

import { apiClient } from './client';
import type { SearchResults, SearchFilters } from '@/types/search';

export const searchAPI = {
  /**
   * Search resources with filters
   */
  async search(query: string, filters?: SearchFilters): Promise<SearchResults> {
    return apiClient.get<SearchResults>('/search', {
      q: query,
      ...filters,
    });
  },

  /**
   * Get search suggestions/autocomplete
   */
  async suggestions(query: string): Promise<string[]> {
    return apiClient.get<string[]>('/search/suggestions', { q: query });
  },
};
