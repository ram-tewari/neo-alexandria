// Neo Alexandria 2.0 Frontend - API Service Layer
// Provides typed HTTP client for all backend API endpoints

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  Resource,
  ResourceStatus,
  CreateResourceRequest,
  CreateResourceResponse,
  UpdateResourceRequest,
  SearchQuery,
  SearchResults,
  ResourceListResponse,
  RecommendationResponse,
  GraphResponse,
  ClassificationTree,
  QualityAnalysis,
  BatchUpdateRequest,
  BatchUpdateResponse,
  ResourceQueryParams,
  ApiError,
} from '@/types/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for future authentication
    this.api.interceptors.request.use(
      (config) => {
        // Future: Add API key authentication here
        // const apiKey = localStorage.getItem('apiKey');
        // if (apiKey) {
        //   config.headers.Authorization = `Bearer ${apiKey}`;
        // }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail);
        }
        throw error;
      }
    );
  }

  // Resource Management API

  /**
   * Ingest a new resource from a URL
   */
  async ingestResource(request: CreateResourceRequest): Promise<CreateResourceResponse> {
    const response: AxiosResponse<CreateResourceResponse> = await this.api.post('/resources', request);
    return response.data;
  }

  /**
   * Get ingestion status for a resource
   */
  async getResourceStatus(resourceId: string): Promise<ResourceStatus> {
    const response: AxiosResponse<ResourceStatus> = await this.api.get(`/resources/${resourceId}/status`);
    return response.data;
  }

  /**
   * List resources with filtering and pagination
   */
  async listResources(params: ResourceQueryParams = {}): Promise<ResourceListResponse> {
    const response: AxiosResponse<ResourceListResponse> = await this.api.get('/resources', { params });
    return response.data;
  }

  /**
   * Get a specific resource by ID
   */
  async getResource(resourceId: string): Promise<Resource> {
    const response: AxiosResponse<Resource> = await this.api.get(`/resources/${resourceId}`);
    return response.data;
  }

  /**
   * Update a resource
   */
  async updateResource(resourceId: string, updates: UpdateResourceRequest): Promise<Resource> {
    const response: AxiosResponse<Resource> = await this.api.put(`/resources/${resourceId}`, updates);
    return response.data;
  }

  /**
   * Delete a resource
   */
  async deleteResource(resourceId: string): Promise<void> {
    await this.api.delete(`/resources/${resourceId}`);
  }

  /**
   * Override classification for a resource
   */
  async classifyResource(resourceId: string, code: string): Promise<Resource> {
    const response: AxiosResponse<Resource> = await this.api.put(`/resources/${resourceId}/classify`, { code });
    return response.data;
  }

  // Search API

  /**
   * Perform advanced search with hybrid capabilities
   */
  async search(query: SearchQuery): Promise<SearchResults> {
    const response: AxiosResponse<SearchResults> = await this.api.post('/search', query);
    return response.data;
  }

  // Recommendations API

  /**
   * Get personalized recommendations
   */
  async getRecommendations(limit: number = 10): Promise<RecommendationResponse> {
    const response: AxiosResponse<RecommendationResponse> = await this.api.get('/recommendations', {
      params: { limit },
    });
    return response.data;
  }

  // Knowledge Graph API

  /**
   * Get neighbors for a resource (mind-map visualization)
   */
  async getResourceNeighbors(resourceId: string, limit: number = 7): Promise<GraphResponse> {
    const response: AxiosResponse<GraphResponse> = await this.api.get(
      `/graph/resource/${resourceId}/neighbors`,
      { params: { limit } }
    );
    return response.data;
  }

  /**
   * Get global graph overview
   */
  async getGraphOverview(limit: number = 50, vectorThreshold: number = 0.85): Promise<GraphResponse> {
    const response: AxiosResponse<GraphResponse> = await this.api.get('/graph/overview', {
      params: { limit, vector_threshold: vectorThreshold },
    });
    return response.data;
  }

  // Authority and Classification API

  /**
   * Get subject suggestions for autocomplete
   */
  async getSubjectSuggestions(query: string): Promise<string[]> {
    const response: AxiosResponse<string[]> = await this.api.get('/authority/subjects/suggest', {
      params: { q: query },
    });
    return response.data;
  }

  /**
   * Get classification tree
   */
  async getClassificationTree(): Promise<ClassificationTree> {
    const response: AxiosResponse<ClassificationTree> = await this.api.get('/authority/classification/tree');
    return response.data;
  }

  // Curation API

  /**
   * Get resources in review queue
   */
  async getReviewQueue(threshold?: number, includeUnreadOnly: boolean = false, limit: number = 25, offset: number = 0): Promise<ResourceListResponse> {
    const params: any = { limit, offset, include_unread_only: includeUnreadOnly };
    if (threshold !== undefined) {
      params.threshold = threshold;
    }
    const response: AxiosResponse<ResourceListResponse> = await this.api.get('/curation/review-queue', { params });
    return response.data;
  }

  /**
   * Get low-quality resources
   */
  async getLowQualityResources(threshold: number = 0.5, limit: number = 25, offset: number = 0): Promise<ResourceListResponse> {
    const response: AxiosResponse<ResourceListResponse> = await this.api.get('/curation/low-quality', {
      params: { threshold, limit, offset },
    });
    return response.data;
  }

  /**
   * Get detailed quality analysis for a resource
   */
  async getQualityAnalysis(resourceId: string): Promise<QualityAnalysis> {
    const response: AxiosResponse<QualityAnalysis> = await this.api.get(`/curation/quality-analysis/${resourceId}`);
    return response.data;
  }

  /**
   * Batch update multiple resources
   */
  async batchUpdate(request: BatchUpdateRequest): Promise<BatchUpdateResponse> {
    const response: AxiosResponse<BatchUpdateResponse> = await this.api.post('/curation/batch-update', request);
    return response.data;
  }

  /**
   * Perform bulk quality check on resources
   */
  async bulkQualityCheck(resourceIds: string[]): Promise<BatchUpdateResponse> {
    const response: AxiosResponse<BatchUpdateResponse> = await this.api.post('/curation/bulk-quality-check', {
      resource_ids: resourceIds,
    });
    return response.data;
  }

  // Health check and utilities

  /**
   * Check if the API is available
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Use a simple endpoint to check connectivity
      await this.api.get('/resources?limit=1');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Generic error handler for UI components
   */
  static handleApiError(error: unknown): string {
    if (error instanceof Error) {
      return error.message;
    }
    if (typeof error === 'string') {
      return error;
    }
    return 'An unexpected error occurred';
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export the class for testing
export { ApiService };

// Helper functions for common operations

/**
 * Poll resource status until completion or failure
 */
export async function pollResourceStatus(
  resourceId: string,
  onProgress?: (status: ResourceStatus) => void,
  maxAttempts: number = 30,
  interval: number = 2000
): Promise<ResourceStatus> {
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    try {
      const status = await apiService.getResourceStatus(resourceId);
      
      if (onProgress) {
        onProgress(status);
      }
      
      if (status.ingestion_status === 'completed' || status.ingestion_status === 'failed') {
        return status;
      }
      
      attempts++;
      await new Promise(resolve => setTimeout(resolve, interval));
    } catch (error) {
      console.error('Error polling resource status:', error);
      throw error;
    }
  }
  
  throw new Error('Polling timeout: Resource status check exceeded maximum attempts');
}

/**
 * Batch process resources with progress tracking
 */
export async function batchProcessResources<T>(
  items: T[],
  processor: (item: T) => Promise<void>,
  onProgress?: (completed: number, total: number) => void,
  concurrency: number = 3
): Promise<void> {
  const total = items.length;
  let completed = 0;
  
  const semaphore = Array(concurrency).fill(null);
  const processItem = async (item: T) => {
    try {
      await processor(item);
    } finally {
      completed++;
      if (onProgress) {
        onProgress(completed, total);
      }
    }
  };
  
  const workers = semaphore.map(async () => {
    while (items.length > 0) {
      const item = items.shift();
      if (item) {
        await processItem(item);
      }
    }
  });
  
  await Promise.all(workers);
}
