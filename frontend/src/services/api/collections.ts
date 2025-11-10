// Neo Alexandria 2.0 Frontend - Collections API Service
// Collection management and recommendations

import apiClient from './client';

// Collection types
export interface Collection {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  visibility: 'private' | 'shared' | 'public';
  parent_id?: string;
  created_at: string;
  updated_at: string;
  resource_count: number;
  resources?: any[];
  subcollections?: Collection[];
}

export interface CreateCollectionRequest {
  name: string;
  description?: string;
  visibility?: 'private' | 'shared' | 'public';
  parent_id?: string;
}

export interface CollectionListResponse {
  items: Collection[];
  total: number;
}

export interface CollectionRecommendations {
  resource_recommendations: any[];
  collection_recommendations: any[];
}

export interface GetCollectionsParams {
  user_id?: string;
  limit?: number;
  offset?: number;
}

export const collectionsApi = {
  /**
   * Get all collections
   */
  getAll: async (params: GetCollectionsParams = {}): Promise<CollectionListResponse> => {
    const response = await apiClient.get<CollectionListResponse>('/collections', { params });
    return response.data;
  },

  /**
   * Get a specific collection by ID
   */
  getById: async (id: string, userId?: string): Promise<Collection> => {
    const response = await apiClient.get<Collection>(`/collections/${id}`, {
      params: { user_id: userId },
    });
    return response.data;
  },

  /**
   * Create a new collection
   */
  create: async (data: CreateCollectionRequest, userId: string): Promise<Collection> => {
    const response = await apiClient.post<Collection>('/collections', data, {
      params: { user_id: userId },
    });
    return response.data;
  },

  /**
   * Update a collection
   */
  update: async (id: string, data: Partial<CreateCollectionRequest>, userId: string): Promise<Collection> => {
    const response = await apiClient.put<Collection>(`/collections/${id}`, data, {
      params: { user_id: userId },
    });
    return response.data;
  },

  /**
   * Delete a collection
   */
  delete: async (id: string, userId: string): Promise<void> => {
    await apiClient.delete(`/collections/${id}`, {
      params: { user_id: userId },
    });
  },

  /**
   * Add resources to a collection
   */
  addResources: async (id: string, resourceIds: string[], userId: string): Promise<void> => {
    await apiClient.post(
      `/collections/${id}/resources`,
      { resource_ids: resourceIds },
      { params: { user_id: userId } }
    );
  },

  /**
   * Remove resources from a collection
   */
  removeResources: async (id: string, resourceIds: string[], userId: string): Promise<void> => {
    await apiClient.delete(`/collections/${id}/resources`, {
      data: { resource_ids: resourceIds },
      params: { user_id: userId },
    });
  },

  /**
   * Get recommendations for a collection
   */
  getRecommendations: async (
    id: string,
    userId?: string,
    limit?: number
  ): Promise<CollectionRecommendations> => {
    const response = await apiClient.get<CollectionRecommendations>(
      `/collections/${id}/recommendations`,
      { params: { user_id: userId, limit } }
    );
    return response.data;
  },
};
