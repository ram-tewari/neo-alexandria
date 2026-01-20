/**
 * Search API Client
 * Handles communication with the backend search API
 */

import type { SearchRequest, SearchResult } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Search resources using hybrid search
 * @param payload - Search request parameters
 * @returns Promise resolving to array of search results
 * @throws Error if search fails
 */
export async function searchResources(
  payload: SearchRequest
): Promise<SearchResult[]> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status === 400) {
        throw new Error('Invalid search query. Please try different terms.');
      }
      if (response.status === 500) {
        throw new Error('Search service is currently unavailable. Please try again later.');
      }
      throw new Error(`Search failed with status: ${response.status}`);
    }

    const data = await response.json();
    return data.results || data; // Handle both {results: []} and [] formats
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Search request timed out. Please try again.');
      }
      throw error;
    }
    throw new Error('An unexpected error occurred during search.');
  }
}
