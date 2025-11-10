// Neo Alexandria 2.0 Frontend - Search Hooks
// Custom React hooks for search functionality with debouncing

import { useQuery } from '@tanstack/react-query';
import { useState, useEffect, useCallback } from 'react';
import { searchApi } from '@/services/api';
import type { SearchQuery } from '@/types/api';

// Query keys for cache management
export const searchKeys = {
  all: ['search'] as const,
  searches: () => [...searchKeys.all, 'query'] as const,
  search: (query: SearchQuery) => [...searchKeys.searches(), query] as const,
  suggestions: (query: string) => [...searchKeys.all, 'suggestions', query] as const,
};

/**
 * Hook to perform search with automatic query execution
 */
export function useSearch(query: SearchQuery, enabled: boolean = true) {
  return useQuery({
    queryKey: searchKeys.search(query),
    queryFn: () => searchApi.search(query),
    enabled: enabled && (!!query.text || Object.keys(query.filters || {}).length > 0),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to get subject suggestions for autocomplete
 */
export function useSubjectSuggestions(query: string) {
  return useQuery({
    queryKey: searchKeys.suggestions(query),
    queryFn: () => searchApi.getSuggestions(query),
    enabled: query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook with debounced search functionality
 * Useful for search-as-you-type experiences
 */
export function useDebouncedSearch(initialQuery: SearchQuery, debounceMs: number = 500) {
  const [debouncedQuery, setDebouncedQuery] = useState<SearchQuery>(initialQuery);
  const [isDebouncing, setIsDebouncing] = useState(false);

  useEffect(() => {
    setIsDebouncing(true);
    const timer = setTimeout(() => {
      setDebouncedQuery(initialQuery);
      setIsDebouncing(false);
    }, debounceMs);

    return () => {
      clearTimeout(timer);
    };
  }, [initialQuery, debounceMs]);

  const searchResult = useSearch(debouncedQuery, !isDebouncing);

  return {
    ...searchResult,
    isDebouncing,
  };
}

/**
 * Hook for managing search state with debouncing
 */
export function useSearchManager(debounceMs: number = 500) {
  const [query, setQuery] = useState<SearchQuery>({
    text: '',
    filters: {},
    limit: 25,
    offset: 0,
    sort_by: 'relevance',
    sort_dir: 'desc',
    hybrid_weight: 0.5,
  });

  const updateQuery = useCallback((updates: Partial<SearchQuery>) => {
    setQuery((prev) => ({ ...prev, ...updates }));
  }, []);

  const updateText = useCallback((text: string) => {
    setQuery((prev) => ({ ...prev, text, offset: 0 }));
  }, []);

  const updateFilters = useCallback((filters: SearchQuery['filters']) => {
    setQuery((prev) => ({ ...prev, filters, offset: 0 }));
  }, []);

  const updateHybridWeight = useCallback((weight: number) => {
    setQuery((prev) => ({ ...prev, hybrid_weight: weight, offset: 0 }));
  }, []);

  const clearSearch = useCallback(() => {
    setQuery({
      text: '',
      filters: {},
      limit: 25,
      offset: 0,
      sort_by: 'relevance',
      sort_dir: 'desc',
      hybrid_weight: 0.5,
    });
  }, []);

  const searchResult = useDebouncedSearch(query, debounceMs);

  return {
    query,
    updateQuery,
    updateText,
    updateFilters,
    updateHybridWeight,
    clearSearch,
    ...searchResult,
  };
}
