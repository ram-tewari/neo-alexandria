/**
 * Search Types
 * 
 * Type definitions for search functionality
 */

import type { Resource } from './resource';
import type { ReadStatus } from './api';

export interface SearchFilters {
  quality_min?: number;
  quality_max?: number;
  date_from?: string;
  date_to?: string;
  types?: string[];
  tags?: string[];
  read_status?: ReadStatus[];
}

export interface SearchFacets {
  types: { value: string; count: number }[];
  tags: { value: string; count: number }[];
  quality_ranges: { range: string; count: number }[];
}

export interface SearchResults {
  resources: Resource[];
  total: number;
  page: number;
  limit: number;
  facets: SearchFacets;
}
