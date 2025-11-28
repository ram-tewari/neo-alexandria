import { apiClient, PaginatedResponse } from './client';
import { SearchQuery, SearchResult, SearchSuggestion, SavedSearch } from '@/types/search';

export const searchApi = {
  // Perform search
  search: async (
    query: SearchQuery,
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResponse<SearchResult>> => {
    const response = await apiClient.post<PaginatedResponse<SearchResult>>(
      '/search',
      {
        ...query,
        page,
        pageSize,
      }
    );
    return response.data;
  },

  // Get search suggestions
  getSuggestions: async (query: string): Promise<SearchSuggestion[]> => {
    const response = await apiClient.get<SearchSuggestion[]>(
      `/search/suggestions?q=${encodeURIComponent(query)}`
    );
    return response.data;
  },

  // Get search history
  getHistory: async (): Promise<string[]> => {
    const history = localStorage.getItem('search_history');
    return history ? JSON.parse(history) : [];
  },

  // Add to search history
  addToHistory: async (query: string): Promise<void> => {
    const history = await searchApi.getHistory();
    const updated = [query, ...history.filter((q) => q !== query)].slice(0, 10);
    localStorage.setItem('search_history', JSON.stringify(updated));
  },

  // Clear search history
  clearHistory: async (): Promise<void> => {
    localStorage.removeItem('search_history');
  },

  // Save search
  saveSearch: async (name: string, query: SearchQuery): Promise<SavedSearch> => {
    const response = await apiClient.post<SavedSearch>('/search/saved', {
      name,
      query,
    });
    return response.data;
  },

  // Get saved searches
  getSavedSearches: async (): Promise<SavedSearch[]> => {
    const response = await apiClient.get<SavedSearch[]>('/search/saved');
    return response.data;
  },

  // Delete saved search
  deleteSavedSearch: async (id: string): Promise<void> => {
    await apiClient.delete(`/search/saved/${id}`);
  },
};
