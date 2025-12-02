/**
 * Resources API Client
 * Provides typed methods for all resource operations
 */

import {
  ResourceRead,
  ResourceIngestRequest,
  ResourceUpdate,
  ResourceAccepted,
  ResourceStatus,
  ResourceListParams,
  ResourceListResponse,
  ApiError,
} from './types';
import { apiRequest, handleApiError, API_BASE_URL } from './apiUtils';

/**
 * Resources API Client
 */
export const resourcesApi = {
  /**
   * List resources with pagination and filtering
   */
  async list(params: ResourceListParams = {}): Promise<ResourceListResponse> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    const endpoint = `/resources${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<ResourceListResponse>(endpoint);
  },

  /**
   * Get a single resource by ID
   */
  async get(id: string): Promise<ResourceRead> {
    return apiRequest<ResourceRead>(`/resources/${id}`);
  },

  /**
   * Create a new resource (file or URL ingestion)
   */
  async create(
    data: ResourceIngestRequest,
    options?: { onUploadProgress?: (progress: ProgressEvent) => void }
  ): Promise<ResourceAccepted> {
    try {
      const formData = new FormData();

      if (data.file) {
        formData.append('file', data.file);
      }
      if (data.url) {
        formData.append('url', data.url);
      }
      if (data.title) {
        formData.append('title', data.title);
      }
      if (data.creator) {
        formData.append('creator', data.creator);
      }
      if (data.description) {
        formData.append('description', data.description);
      }
      if (data.language) {
        formData.append('language', data.language);
      }
      if (data.type) {
        formData.append('type', data.type);
      }
      if (data.subject && data.subject.length > 0) {
        data.subject.forEach(s => formData.append('subject', s));
      }

      // Use XMLHttpRequest for upload progress tracking
      if (options?.onUploadProgress) {
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          
          const progressHandler = (e: ProgressEvent) => {
            options.onUploadProgress?.(e);
          };
          
          xhr.upload.addEventListener('progress', progressHandler);
          
          xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                resolve(JSON.parse(xhr.responseText));
              } catch (error) {
                reject(new ApiError('Failed to parse response', xhr.status));
              }
            } else {
              // Try to parse error response
              try {
                const errorData = JSON.parse(xhr.responseText);
                const message = errorData.detail || `Upload failed: ${xhr.statusText}`;
                reject(new ApiError(message, xhr.status, errorData));
              } catch {
                reject(new ApiError(`Upload failed: ${xhr.statusText}`, xhr.status));
              }
            }
          });
          
          xhr.addEventListener('error', () => {
            reject(new ApiError('Network error during upload', 0));
          });
          
          xhr.addEventListener('abort', () => {
            reject(new ApiError('Upload cancelled', 0));
          });
          
          xhr.open('POST', `${API_BASE_URL}/resources`);
          xhr.send(formData);
        });
      }

      // Standard fetch for requests without progress tracking
      const response = await fetch(`${API_BASE_URL}/resources`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        await handleApiError(response);
      }

      return response.json();
    } catch (error) {
      // Re-throw ApiError instances
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Wrap other errors
      if (error instanceof Error) {
        throw new ApiError(`Upload failed: ${error.message}`, 0);
      }
      
      throw new ApiError('Upload failed: Unknown error', 0);
    }
  },

  /**
   * Update an existing resource
   */
  async update(id: string, data: ResourceUpdate): Promise<ResourceRead> {
    return apiRequest<ResourceRead>(`/resources/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a resource
   */
  async delete(id: string): Promise<void> {
    return apiRequest<void>(`/resources/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Get resource ingestion status
   */
  async getStatus(id: string): Promise<ResourceStatus> {
    return apiRequest<ResourceStatus>(`/resources/${id}/status`);
  },

  /**
   * Batch update multiple resources
   */
  async batchUpdate(ids: string[], data: ResourceUpdate): Promise<void> {
    // Note: Backend may not have a dedicated batch endpoint yet
    // This implementation updates resources sequentially
    // TODO: Replace with actual batch endpoint when available
    await Promise.all(ids.map(id => this.update(id, data)));
  },
};

export default resourcesApi;
