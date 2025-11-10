// Neo Alexandria 2.0 Frontend - Resources API Service
// CRUD operations for resource management

import apiClient from './client';
import type {
  Resource,
  ResourceStatus,
  CreateResourceRequest,
  CreateResourceResponse,
  UpdateResourceRequest,
  ResourceListResponse,
  ResourceQueryParams,
} from '@/types/api';

export const resourcesApi = {
  /**
   * Get all resources with filtering and pagination
   */
  getAll: async (params: ResourceQueryParams = {}): Promise<ResourceListResponse> => {
    const response = await apiClient.get<ResourceListResponse>('/resources', { params });
    return response.data;
  },

  /**
   * Get a specific resource by ID
   */
  getById: async (id: string): Promise<Resource> => {
    const response = await apiClient.get<Resource>(`/resources/${id}`);
    return response.data;
  },

  /**
   * Create a new resource (ingest from URL)
   */
  create: async (data: CreateResourceRequest): Promise<CreateResourceResponse> => {
    const response = await apiClient.post<CreateResourceResponse>('/resources', data);
    return response.data;
  },

  /**
   * Update an existing resource
   */
  update: async (id: string, data: UpdateResourceRequest): Promise<Resource> => {
    const response = await apiClient.put<Resource>(`/resources/${id}`, data);
    return response.data;
  },

  /**
   * Delete a resource
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/resources/${id}`);
  },

  /**
   * Get ingestion status for a resource
   */
  getStatus: async (id: string): Promise<ResourceStatus> => {
    const response = await apiClient.get<ResourceStatus>(`/resources/${id}/status`);
    return response.data;
  },

  /**
   * Classify a resource
   */
  classify: async (id: string, code: string): Promise<Resource> => {
    const response = await apiClient.put<Resource>(`/resources/${id}/classify`, { code });
    return response.data;
  },
};
