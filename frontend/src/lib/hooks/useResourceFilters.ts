/**
 * Hook for managing resource filter state with URL synchronization
 * 
 * This hook provides a centralized way to manage filter state that:
 * - Syncs with URL search parameters for shareable/bookmarkable filters
 * - Parses filters from URL on mount
 * - Updates URL when filters change
 * - Provides type-safe filter state
 */

import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { ResourceListParams, ReadStatus } from '../api/types';

export interface ResourceFilters extends Omit<ResourceListParams, 'limit' | 'offset' | 'sort_by' | 'order'> {
  q?: string;
  classification_code?: string;
  type?: string;
  language?: string;
  read_status?: ReadStatus;
  min_quality?: number;
  max_quality?: number;
  subject?: string;
}

/**
 * Custom hook for managing resource filters with URL synchronization
 * 
 * @param initialFilters - Optional initial filter values
 * @returns Tuple of [filters, setFilters] similar to useState
 * 
 * @example
 * ```tsx
 * const [filters, setFilters] = useResourceFilters();
 * 
 * // Update a single filter
 * setFilters({ ...filters, type: 'article' });
 * 
 * // Clear all filters
 * setFilters({});
 * ```
 */
export const useResourceFilters = (initialFilters?: ResourceFilters) => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse filters from URL search parameters
  const filters = useMemo<ResourceFilters>(() => {
    const urlFilters: ResourceFilters = {};

    // Text search query
    const q = searchParams.get('q');
    if (q) urlFilters.q = q;

    // Classification filter
    const classification = searchParams.get('classification');
    if (classification) urlFilters.classification_code = classification;

    // Type filter
    const type = searchParams.get('type');
    if (type) urlFilters.type = type;

    // Language filter
    const language = searchParams.get('language');
    if (language) urlFilters.language = language;

    // Read status filter
    const status = searchParams.get('status');
    if (status && isValidReadStatus(status)) {
      urlFilters.read_status = status as ReadStatus;
    }

    // Quality range filters
    const minQuality = searchParams.get('min_quality');
    if (minQuality) {
      const parsed = parseFloat(minQuality);
      if (!isNaN(parsed) && parsed >= 0 && parsed <= 1) {
        urlFilters.min_quality = parsed;
      }
    }

    const maxQuality = searchParams.get('max_quality');
    if (maxQuality) {
      const parsed = parseFloat(maxQuality);
      if (!isNaN(parsed) && parsed >= 0 && parsed <= 1) {
        urlFilters.max_quality = parsed;
      }
    }

    // Subject filter
    const subject = searchParams.get('subject');
    if (subject) urlFilters.subject = subject;

    // Merge with initial filters (URL params take precedence)
    return { ...initialFilters, ...urlFilters };
  }, [searchParams, initialFilters]);

  // Update URL when filters change
  const setFilters = useCallback(
    (newFilters: ResourceFilters) => {
      const params = new URLSearchParams();

      // Add each filter to URL params if it has a value
      if (newFilters.q) {
        params.set('q', newFilters.q);
      }

      if (newFilters.classification_code) {
        params.set('classification', newFilters.classification_code);
      }

      if (newFilters.type) {
        params.set('type', newFilters.type);
      }

      if (newFilters.language) {
        params.set('language', newFilters.language);
      }

      if (newFilters.read_status) {
        params.set('status', newFilters.read_status);
      }

      if (newFilters.min_quality !== undefined && newFilters.min_quality !== null) {
        params.set('min_quality', newFilters.min_quality.toString());
      }

      if (newFilters.max_quality !== undefined && newFilters.max_quality !== null) {
        params.set('max_quality', newFilters.max_quality.toString());
      }

      if (newFilters.subject) {
        params.set('subject', newFilters.subject);
      }

      // Update URL without causing a page reload
      setSearchParams(params, { replace: true });
    },
    [setSearchParams]
  );

  return [filters, setFilters] as const;
};

/**
 * Helper function to validate read status values
 */
function isValidReadStatus(value: string): value is ReadStatus {
  return ['unread', 'in_progress', 'completed', 'archived'].includes(value);
}

/**
 * Helper hook to check if any filters are active
 */
export const useHasActiveFilters = (filters: ResourceFilters): boolean => {
  return useMemo(() => {
    return Object.keys(filters).length > 0;
  }, [filters]);
};

/**
 * Helper hook to get a count of active filters
 */
export const useActiveFilterCount = (filters: ResourceFilters): number => {
  return useMemo(() => {
    return Object.values(filters).filter(value => value !== undefined && value !== null).length;
  }, [filters]);
};
