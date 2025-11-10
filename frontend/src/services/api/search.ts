// Neo Alexandria 2.0 Frontend - Search API Service
// Search and autocomplete functionality

import apiClient from './client';
import type { SearchQuery, SearchResults } from '@/types/api';

export const searchApi = {
  /**
   * Perform advanced search with hybrid capabilities
   */
  search: async (request: SearchQuery): Promise<SearchResults> => {
    const response = await apiClient.post<SearchResults>('/search', request);
    return response.data;
  },

  /**
   * Get subject suggestions for autocomplete
   */
  getSuggestions: async (query: string): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/authority/subjects/suggest', {
      params: { q: query },
    });
    return response.data;
  },
};
