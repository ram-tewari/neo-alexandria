/**
 * Library API Client
 * 
 * Provides API endpoints for Phase 3 Living Library features:
 * - Resource management (upload, list, get, update, delete)
 * - Repository ingestion
 * 
 * Phase: 3 Living Library
 * Requirements: US-3.1, US-3.2, US-3.3, US-3.4
 */

import { apiClient } from '@/core/api/client';
import type {
  Resource,
  ResourceUpload,
  ResourceUpdate,
  ResourceListResponse,
  RepositoryIngestRequest,
  RepositoryIngestResponse,
} from '@/types/library';

// ============================================================================
// Upload Progress Callback Type
// ============================================================================

/**
 * Upload progress callback function
 * Called periodically during file upload to report progress
 */
export type UploadProgressCallback = (progress: {
  loaded: number;
  total: number;
  percentage: number;
}) => void;

// ============================================================================
// Library API Client Interface
// ============================================================================

/**
 * Library API client with all Phase 3 library-related endpoints
 */
export const libraryApi = {
  // ==========================================================================
  // Resource Management Endpoints
  // ==========================================================================

  /**
   * Upload a resource file (PDF, HTML, TXT, etc.)
   * 
   * Supports multipart/form-data upload with progress tracking.
   * Optionally accepts metadata to be attached to the resource.
   * 
   * @param file - File to upload
   * @param metadata - Optional metadata (title, description, creator, etc.)
   * @param onProgress - Optional callback for upload progress
   * @returns Created resource with ID
   * @endpoint POST /resources
   * 
   * @example
   * ```typescript
   * const file = new File(['content'], 'document.pdf', { type: 'application/pdf' });
   * const resource = await libraryApi.uploadResource(
   *   file,
   *   { title: 'My Document', creator: 'John Doe' },
   *   (progress) => console.log(`${progress.percentage}% uploaded`)
   * );
   * ```
   */
  uploadResource: async (
    file: File,
    metadata?: Partial<Resource>,
    onProgress?: UploadProgressCallback
  ): Promise<Resource> => {
    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('file', file);
    
    // Attach metadata if provided
    if (metadata) {
      // Serialize metadata as JSON string
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    // Make request with progress tracking
    const response = await apiClient.post<Resource>('/resources', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const loaded = progressEvent.loaded;
          const total = progressEvent.total;
          const percentage = Math.round((loaded / total) * 100);
          
          onProgress({ loaded, total, percentage });
        }
      },
    });
    
    return response.data;
  },

  /**
   * List resources with optional filtering and pagination
   * 
   * Supports filtering by type, quality score range, and pagination.
   * Returns paginated list of resources with total count.
   * 
   * @param params - Query parameters for filtering and pagination
   * @returns Paginated list of resources
   * @endpoint GET /resources
   * 
   * @example
   * ```typescript
   * // Get first 20 PDF resources with quality >= 0.7
   * const result = await libraryApi.listResources({
   *   type: 'pdf',
   *   quality_min: 0.7,
   *   limit: 20,
   *   offset: 0
   * });
   * console.log(`Found ${result.total} resources, showing ${result.resources.length}`);
   * ```
   */
  listResources: async (params?: {
    type?: string;
    quality_min?: number;
    quality_max?: number;
    limit?: number;
    offset?: number;
  }): Promise<ResourceListResponse> => {
    const response = await apiClient.get<ResourceListResponse>('/resources', {
      params,
    });
    
    return response.data;
  },

  /**
   * Get a single resource by ID
   * 
   * Fetches complete resource details including metadata, content,
   * and ingestion status.
   * 
   * @param resourceId - Resource ID
   * @returns Full resource object
   * @endpoint GET /resources/{resource_id}
   * 
   * @example
   * ```typescript
   * const resource = await libraryApi.getResource('res_123');
   * console.log(`Title: ${resource.title}`);
   * console.log(`Quality: ${resource.quality_score}`);
   * ```
   */
  getResource: async (resourceId: string): Promise<Resource> => {
    const response = await apiClient.get<Resource>(`/resources/${resourceId}`);
    return response.data;
  },

  /**
   * Update a resource (partial update)
   * 
   * Updates one or more fields of an existing resource.
   * Only provided fields are updated; others remain unchanged.
   * 
   * @param resourceId - Resource ID
   * @param updates - Partial resource object with fields to update
   * @returns Updated resource
   * @endpoint PUT /resources/{resource_id}
   * 
   * @example
   * ```typescript
   * // Update title and read status
   * const updated = await libraryApi.updateResource('res_123', {
   *   title: 'New Title',
   *   read_status: 'completed'
   * });
   * ```
   */
  updateResource: async (
    resourceId: string,
    updates: ResourceUpdate
  ): Promise<Resource> => {
    const response = await apiClient.put<Resource>(
      `/resources/${resourceId}`,
      updates
    );
    return response.data;
  },

  /**
   * Delete a resource
   * 
   * Permanently deletes a resource and all associated data
   * (annotations, highlights, embeddings, etc.).
   * 
   * @param resourceId - Resource ID
   * @returns void (204 No Content)
   * @endpoint DELETE /resources/{resource_id}
   * 
   * @example
   * ```typescript
   * await libraryApi.deleteResource('res_123');
   * console.log('Resource deleted');
   * ```
   */
  deleteResource: async (resourceId: string): Promise<void> => {
    await apiClient.delete(`/resources/${resourceId}`);
  },

  // ==========================================================================
  // Repository Ingestion Endpoints
  // ==========================================================================

  /**
   * Ingest a code repository
   * 
   * Submits a repository URL for asynchronous processing by the edge worker.
   * The repository is cloned, parsed, and analyzed to generate embeddings.
   * 
   * Returns a job ID that can be used to track ingestion progress.
   * Poll the worker status endpoint to monitor progress.
   * 
   * @param repoUrl - Repository URL (e.g., 'github.com/user/repo')
   * @param branch - Optional branch name (defaults to main/master)
   * @returns Job ID and status
   * @endpoint POST /api/v1/ingestion/ingest/{repo_url}
   * 
   * @example
   * ```typescript
   * // Ingest a repository
   * const result = await libraryApi.ingestRepository(
   *   'github.com/facebook/react',
   *   'main'
   * );
   * console.log(`Job ${result.job_id} queued at position ${result.queue_position}`);
   * 
   * // Poll for status
   * const interval = setInterval(async () => {
   *   const status = await libraryApi.getWorkerStatus();
   *   console.log(status.status);
   *   if (status.status === 'Idle') {
   *     clearInterval(interval);
   *   }
   * }, 2000);
   * ```
   */
  ingestRepository: async (
    repoUrl: string,
    branch?: string
  ): Promise<RepositoryIngestResponse> => {
    // Construct endpoint with repo URL as path parameter
    const endpoint = `/api/v1/ingestion/ingest/${repoUrl}`;
    
    // Make POST request (no body needed, branch is optional query param)
    const response = await apiClient.post<RepositoryIngestResponse>(
      endpoint,
      null,
      {
        params: branch ? { branch } : undefined,
      }
    );
    
    return response.data;
  },

  /**
   * Get edge worker status
   * 
   * Returns the current status of the edge worker processing repositories.
   * Poll this endpoint every 2-5 seconds to show real-time status in UI.
   * 
   * @returns Worker status
   * @endpoint GET /api/v1/ingestion/worker/status
   * 
   * @example
   * ```typescript
   * const status = await libraryApi.getWorkerStatus();
   * if (status.status === 'Idle') {
   *   console.log('Worker is ready');
   * } else if (status.status.startsWith('Training')) {
   *   console.log('Worker is processing a repository');
   * }
   * ```
   */
  getWorkerStatus: async (): Promise<{ status: string }> => {
    const response = await apiClient.get<{ status: string }>(
      '/api/v1/ingestion/worker/status'
    );
    return response.data;
  },

  /**
   * Get job history
   * 
   * Returns recent ingestion job history with metrics.
   * Useful for displaying processing statistics and debugging failures.
   * 
   * @param limit - Number of jobs to return (default: 10, max: 100)
   * @returns Job history with metrics
   * @endpoint GET /api/v1/ingestion/jobs/history
   * 
   * @example
   * ```typescript
   * const history = await libraryApi.getJobHistory(20);
   * history.jobs.forEach(job => {
   *   if (job.status === 'complete') {
   *     console.log(`${job.repo_url}: ${job.files_processed} files in ${job.duration_seconds}s`);
   *   } else if (job.status === 'failed') {
   *     console.error(`${job.repo_url}: ${job.error}`);
   *   }
   * });
   * ```
   */
  getJobHistory: async (limit?: number): Promise<{
    jobs: Array<{
      repo_url: string;
      status: 'complete' | 'failed' | 'skipped';
      duration_seconds?: number;
      files_processed?: number;
      embeddings_generated?: number;
      error?: string;
      reason?: string;
      age_seconds?: number;
      timestamp: string;
    }>;
  }> => {
    const response = await apiClient.get('/api/v1/ingestion/jobs/history', {
      params: { limit },
    });
    return response.data;
  },
};

// ============================================================================
// TanStack Query Key Factories
// ============================================================================

/**
 * Query key factories for TanStack Query caching
 * 
 * These factories generate consistent cache keys for React Query.
 * Use these keys in useQuery and useMutation hooks to ensure proper
 * cache invalidation and data consistency.
 * 
 * @example
 * ```typescript
 * const { data } = useQuery({
 *   queryKey: libraryQueryKeys.resources.list({ type: 'pdf' }),
 *   queryFn: () => libraryApi.listResources({ type: 'pdf' }),
 * });
 * ```
 */
export const libraryQueryKeys = {
  /**
   * Resource-related query keys
   */
  resources: {
    /** All resources query keys */
    all: () => ['library', 'resources'] as const,
    /** Resources list with optional filters */
    list: (params?: Parameters<typeof libraryApi.listResources>[0]) =>
      ['library', 'resources', 'list', params] as const,
    /** Single resource by ID */
    detail: (resourceId: string) =>
      ['library', 'resources', 'detail', resourceId] as const,
  },

  /**
   * Ingestion-related query keys
   */
  ingestion: {
    /** Worker status */
    workerStatus: () => ['library', 'ingestion', 'worker-status'] as const,
    /** Job history */
    jobHistory: (limit?: number) =>
      ['library', 'ingestion', 'job-history', limit] as const,
  },
};

// ============================================================================
// Cache Configuration
// ============================================================================

/**
 * Default cache times for TanStack Query (in milliseconds)
 * 
 * - staleTime: How long data is considered fresh (no refetch)
 * - cacheTime: How long unused data stays in cache
 */
export const libraryCacheConfig = {
  resources: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  ingestion: {
    workerStatus: {
      staleTime: 0, // Always refetch (real-time status)
      cacheTime: 30 * 1000, // 30 seconds
      refetchInterval: 2000, // Poll every 2 seconds
    },
    jobHistory: {
      staleTime: 30 * 1000, // 30 seconds
      cacheTime: 5 * 60 * 1000, // 5 minutes
    },
  },
};
