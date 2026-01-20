/**
 * Tags API
 * 
 * API endpoints for tag management
 * Matches backend format (no /api prefix)
 */

import { apiClient } from './client';
import type { Resource } from '@/types/resource';

interface Tag {
  name: string;
  count: number;
}

export const tagsAPI = {
  /**
   * List all tags with usage counts
   * Note: Backend may not have this endpoint yet
   */
  async list(): Promise<Tag[]> {
    return apiClient.get<Tag[]>('/tags');
  },

  /**
   * Get resources by tag
   * Note: Backend may not have this endpoint yet
   */
  async getResources(tag: string): Promise<Resource[]> {
    return apiClient.get<Resource[]>(`/tags/${encodeURIComponent(tag)}/resources`);
  },
};
