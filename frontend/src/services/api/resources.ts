/**
 * Resources API
 * 
 * API endpoints for resource management
 * Matches backend format (no /api prefix, offset-based pagination)
 */

import { apiClient } from './client';
import type { APIListResponse } from '@/types/api';
import type {
  Resource,
  ResourceCreate,
  ResourceUpdate,
  ResourceListParams,
  ReadStatus,
} from '@/types/resource';

interface BackendResourceListResponse {
  items: Resource[];
  total: number;
}

export const resourcesAPI = {
  /**
   * List resources with pagination and filters
   * Backend uses offset-based pagination and returns {items, total}
   */
  async list(params?: ResourceListParams): Promise<APIListResponse<Resource>> {
    const { page = 1, limit = 20, sort_by, sort_order, ...filters } = params || {};
    
    // Convert page to offset
    const offset = (page - 1) * limit;
    
    // Convert sort_order to sort_dir
    const sort_dir = sort_order === 'asc' ? 'asc' : 'desc';
    
    const backendParams = {
      offset,
      limit,
      sort_by: sort_by || 'created_at',
      sort_dir,
      ...filters,
    };
    
    const response = await apiClient.get<BackendResourceListResponse>('/resources', backendParams);
    
    // Convert backend format to frontend format
    const pages = Math.ceil(response.total / limit);
    
    return {
      data: response.items,
      meta: {
        page,
        limit,
        total: response.total,
        pages,
      },
    };
  },

  /**
   * Get a single resource by ID
   */
  async get(id: string): Promise<Resource> {
    return apiClient.get<Resource>(`/resources/${id}`);
  },

  /**
   * Create a new resource (async ingestion)
   * Returns 202 with {id, status: "pending"}
   */
  async create(data: ResourceCreate): Promise<{ id: string; status: string }> {
    return apiClient.post<{ id: string; status: string }>('/resources', data);
  },

  /**
   * Update an existing resource
   */
  async update(id: string, data: ResourceUpdate): Promise<Resource> {
    return apiClient.put<Resource>(`/resources/${id}`, data);
  },

  /**
   * Delete a resource
   */
  async delete(id: string): Promise<void> {
    return apiClient.delete<void>(`/resources/${id}`);
  },

  /**
   * Update resource read status
   * Uses PUT since backend doesn't have PATCH endpoint
   */
  async updateStatus(id: string, status: ReadStatus): Promise<Resource> {
    return apiClient.put<Resource>(`/resources/${id}`, { read_status: status });
  },

  /**
   * Archive a resource (sets read_status to 'archived')
   * Uses PUT since backend doesn't have dedicated archive endpoint
   */
  async archive(id: string): Promise<Resource> {
    return apiClient.put<Resource>(`/resources/${id}`, { read_status: 'archived' });
  },

  /**
   * Get resource ingestion status
   */
  async getStatus(id: string): Promise<{ ingestion_status: string; ingestion_error?: string }> {
    return apiClient.get(`/resources/${id}/status`);
  },
};
