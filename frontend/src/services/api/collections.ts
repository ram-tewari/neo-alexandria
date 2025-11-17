/**
 * Collections API
 * 
 * API endpoints for collection management
 * Matches backend format (no /api prefix, requires user_id)
 */

import { apiClient } from './client';
import type { APIListResponse } from '@/types/api';
import type {
  Collection,
  CollectionDetail,
  CollectionCreate,
  CollectionUpdate,
  CollectionListParams,
} from '@/types/collection';

interface RecommendationItem {
  id: string;
  title: string;
  type: 'resource' | 'collection';
  relevance_score: number;
  description?: string;
  quality_score?: number;
}

interface CollectionRecommendations {
  collection_id: string;
  resource_recommendations: RecommendationItem[];
  collection_recommendations: RecommendationItem[];
}

interface BackendCollectionListResponse {
  items: Collection[];
  total: number;
  page: number;
  limit: number;
}

// TODO: Replace with actual user authentication
const DEFAULT_USER_ID = 'default-user';

export const collectionsAPI = {
  /**
   * List all collections
   * Backend uses page-based pagination and returns {items, total, page, limit}
   */
  async list(params?: CollectionListParams): Promise<APIListResponse<Collection>> {
    const { page = 1, limit = 50, ...filters } = params || {};
    
    const backendParams = {
      page,
      limit,
      user_id: DEFAULT_USER_ID,
      ...filters,
    };
    
    const response = await apiClient.get<BackendCollectionListResponse>('/collections', backendParams);
    
    // Convert backend format to frontend format
    const pages = Math.ceil(response.total / limit);
    
    return {
      data: response.items,
      meta: {
        page: response.page,
        limit: response.limit,
        total: response.total,
        pages,
      },
    };
  },

  /**
   * Get a single collection with resources and subcollections
   */
  async get(id: string): Promise<CollectionDetail> {
    return apiClient.get<CollectionDetail>(`/collections/${id}`, {
      user_id: DEFAULT_USER_ID,
    });
  },

  /**
   * Create a new collection
   */
  async create(data: CollectionCreate): Promise<Collection> {
    return apiClient.post<Collection>('/collections', data, {
      user_id: DEFAULT_USER_ID,
    });
  },

  /**
   * Update an existing collection
   */
  async update(id: string, data: CollectionUpdate): Promise<Collection> {
    return apiClient.put<Collection>(`/collections/${id}`, data, {
      user_id: DEFAULT_USER_ID,
    });
  },

  /**
   * Delete a collection
   */
  async delete(id: string): Promise<void> {
    return apiClient.delete<void>(`/collections/${id}`, {
      user_id: DEFAULT_USER_ID,
    });
  },

  /**
   * Add resources to a collection
   */
  async addResources(id: string, resourceIds: string[]): Promise<void> {
    return apiClient.post<void>(
      `/collections/${id}/resources`,
      { resource_ids: resourceIds },
      { user_id: DEFAULT_USER_ID }
    );
  },

  /**
   * Remove resources from a collection
   */
  async removeResources(id: string, resourceIds: string[]): Promise<void> {
    // Backend expects body in DELETE request
    const response = await fetch(`${apiClient['baseURL']}/collections/${id}/resources?user_id=${DEFAULT_USER_ID}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ resource_ids: resourceIds }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to remove resources');
    }
  },

  /**
   * Get recommendations for a collection
   */
  async getRecommendations(id: string): Promise<CollectionRecommendations> {
    return apiClient.get<CollectionRecommendations>(`/collections/${id}/recommendations`, {
      user_id: DEFAULT_USER_ID,
    });
  },
};
