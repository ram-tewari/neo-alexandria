import { apiClient, PaginatedResponse } from './client';
import { Resource, UploadStatus, ResourceFilters } from '@/types/resource';

export const resourcesApi = {
  // Get paginated resources
  getResources: async (
    page: number = 1,
    pageSize: number = 20,
    filters?: ResourceFilters
  ): Promise<PaginatedResponse<Resource>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (filters?.type?.length) {
      params.append('type', filters.type.join(','));
    }
    if (filters?.qualityMin !== undefined) {
      params.append('quality_min', filters.qualityMin.toString());
    }
    if (filters?.qualityMax !== undefined) {
      params.append('quality_max', filters.qualityMax.toString());
    }
    if (filters?.classification?.length) {
      params.append('classification', filters.classification.join(','));
    }
    if (filters?.tags?.length) {
      params.append('tags', filters.tags.join(','));
    }
    if (filters?.searchQuery) {
      params.append('q', filters.searchQuery);
    }

    const response = await apiClient.get<PaginatedResponse<Resource>>(
      `/resources?${params.toString()}`
    );
    return response.data;
  },

  // Get single resource by ID
  getResource: async (id: string): Promise<Resource> => {
    const response = await apiClient.get<Resource>(`/resources/${id}`);
    return response.data;
  },

  // Upload file
  uploadFile: async (file: File): Promise<{ uploadId: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<{ uploadId: string }>(
      '/resources/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Upload from URL
  uploadUrl: async (url: string): Promise<{ uploadId: string }> => {
    const response = await apiClient.post<{ uploadId: string }>(
      '/resources/upload-url',
      { url }
    );
    return response.data;
  },

  // Get upload status
  getUploadStatus: async (uploadId: string): Promise<UploadStatus> => {
    const response = await apiClient.get<UploadStatus>(
      `/resources/upload/${uploadId}/status`
    );
    return response.data;
  },

  // Update resource
  updateResource: async (
    id: string,
    updates: Partial<Resource>
  ): Promise<Resource> => {
    const response = await apiClient.patch<Resource>(
      `/resources/${id}`,
      updates
    );
    return response.data;
  },

  // Delete resource
  deleteResource: async (id: string): Promise<void> => {
    await apiClient.delete(`/resources/${id}`);
  },

  // Batch delete resources
  batchDeleteResources: async (ids: string[]): Promise<void> => {
    await apiClient.post('/resources/batch-delete', { ids });
  },

  // Get filter options (for faceted filtering)
  getFilterOptions: async (): Promise<{
    types: { value: string; count: number }[];
    classifications: { value: string; count: number }[];
    tags: { value: string; count: number }[];
  }> => {
    const response = await apiClient.get('/resources/filter-options');
    return response.data;
  },
};
