/**
 * useSearch Hook
 * Core state machine for search functionality
 * Manages query, filters, debouncing, and API integration
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDebounce } from '@/lib/hooks/useDebounce';
import { searchResources } from '../api';
import type { SearchFilters, SearchMethod, SearchResult } from '../types';

export interface UseSearchReturn {
  query: string;
  filters: SearchFilters;
  method: SearchMethod;
  hybridWeight: number;
  results: SearchResult[] | null;
  isLoading: boolean;
  error: Error | null;
  setQuery: (query: string) => void;
  setFilter: (key: keyof SearchFilters, value: any) => void;
  setMethod: (method: SearchMethod) => void;
  setHybridWeight: (weight: number) => void;
  clearFilters: () => void;
}

const DEFAULT_FILTERS: SearchFilters = {
  min_quality: 0,
};

/**
 * Hook for managing search state and API calls
 * - Debounces query input (300ms)
 * - Triggers immediate search on filter changes
 * - Keeps previous data during refetch
 * - Only searches when query is non-empty
 */
export function useSearch(): UseSearchReturn {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS);
  const [method, setMethod] = useState<SearchMethod>('hybrid');
  const [hybridWeight, setHybridWeight] = useState(0.7);

  // Debounce query to avoid excessive API calls
  const debouncedQuery = useDebounce(query, 300);

  // TanStack Query for API integration
  const { data, isLoading, error } = useQuery({
    queryKey: ['search', debouncedQuery, filters, method, hybridWeight],
    queryFn: () =>
      searchResources({
        text: debouncedQuery,
        hybrid_weight: method === 'hybrid' ? hybridWeight : method === 'semantic' ? 1.0 : 0.0,
        filters,
        limit: 20,
      }),
    enabled: debouncedQuery.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  const setFilter = (key: keyof SearchFilters, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters(DEFAULT_FILTERS);
    setMethod('hybrid');
    setHybridWeight(0.7);
  };

  return {
    query,
    filters,
    method,
    hybridWeight,
    results: data ?? null,
    isLoading,
    error: error as Error | null,
    setQuery,
    setFilter,
    setMethod,
    setHybridWeight,
    clearFilters,
  };
}
