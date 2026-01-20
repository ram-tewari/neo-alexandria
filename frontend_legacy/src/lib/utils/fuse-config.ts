/**
 * Fuse.js configuration for fuzzy search
 * Used primarily for command palette search functionality
 */

import Fuse, { IFuseOptions, FuseResult } from 'fuse.js';

/**
 * Default Fuse.js options for command palette search
 * Configured for optimal performance and relevance
 */
export const defaultFuseOptions: IFuseOptions<any> = {
  // Threshold of 0.3 provides good balance between fuzzy and exact matching
  // 0.0 = exact match, 1.0 = match anything
  threshold: 0.3,
  
  // Location and distance for positional matching
  location: 0,
  distance: 100,
  
  // Include score and matches in results
  includeScore: true,
  includeMatches: true,
  
  // Minimum match character length
  minMatchCharLength: 1,
  
  // Use extended search for more powerful queries
  useExtendedSearch: false,
  
  // Ignore location for better fuzzy matching
  ignoreLocation: true,
};

/**
 * Create a Fuse instance with custom options
 * @param items - Array of items to search
 * @param keys - Keys to search within items
 * @param options - Optional Fuse.js options to override defaults
 */
export function createFuseInstance<T>(
  items: T[],
  keys: string[],
  options?: Partial<IFuseOptions<T>>
): Fuse<T> {
  return new Fuse(items, {
    ...defaultFuseOptions,
    keys,
    ...options,
  });
}

/**
 * Search with Fuse and return formatted results
 * @param fuse - Fuse instance
 * @param query - Search query
 * @param maxResults - Maximum number of results to return
 */
export function searchWithFuse<T>(
  fuse: Fuse<T>,
  query: string,
  maxResults: number = 50
): FuseResult<T>[] {
  if (!query.trim()) {
    // Return empty array when query is empty - let the caller handle showing all items
    return [];
  }

  const results = fuse.search(query, { limit: maxResults });
  return results;
}
