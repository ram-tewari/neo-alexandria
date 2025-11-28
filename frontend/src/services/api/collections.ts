import { apiClient } from './client';
import { Collection, CollectionRule } from '@/types/collection';

export const collectionsApi = {
  // Get all collections
  getCollections: async (): Promise<Collection[]> => {
    const response = await apiClient.get<Collection[]>('/collections');
    return response.data;
  },

  // Get single collection
  getCollection: async (id: string): Promise<Collection> => {
    const response = await apiClient.get<Collection>(`/collections/${id}`);
    return response.data;
  },

  // Create collection
  createCollection: async (
    data: Partial<Collection>
  ): Promise<Collection> => {
    const response = await apiClient.post<Collection>('/collections', data);
    return response.data;
  },

  // Update collection
  updateCollection: async (
    id: string,
    updates: Partial<Collection>
  ): Promise<Collection> => {
    const response = await apiClient.patch<Collection>(
      `/collections/${id}`,
      updates
    );
    return response.data;
  },

  // Delete collection
  deleteCollection: async (id: string): Promise<void> => {
    await apiClient.delete(`/collections/${id}`);
  },

  // Add resources to collection
  addResources: async (
    collectionId: string,
    resourceIds: string[]
  ): Promise<void> => {
    await apiClient.post(`/collections/${collectionId}/resources`, {
      resourceIds,
    });
  },

  // Remove resources from collection
  removeResources: async (
    collectionId: string,
    resourceIds: string[]
  ): Promise<void> => {
    await apiClient.delete(`/collections/${collectionId}/resources`, {
      data: { resourceIds },
    });
  },

  // Evaluate smart collection rules
  evaluateRules: async (rules: CollectionRule[]): Promise<number> => {
    const response = await apiClient.post<{ count: number }>(
      '/collections/evaluate-rules',
      { rules }
    );
    return response.data.count;
  },
};
