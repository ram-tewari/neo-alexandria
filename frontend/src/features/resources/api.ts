/**
 * Resource API client
 * 
 * Provides functions for interacting with the resources API endpoints.
 * Uses the configured apiClient from Phase 0 with automatic token management.
 */
import { apiClient } from '@/core/api/client';
import type {
  Resource,
  ResourceListResponse,
  ResourceAccepted,
  ResourceStatusResponse,
  IngestResourcePayload,
  ResourceListParams,
} from '@/core/types/resource';

/**
 * Fetch paginated list of resources
 * 
 * @param params - Query parameters for filtering, sorting, and pagination
 * @returns Promise resolving to paginated resource list
 * 
 * @example
 * ```ts
 * const resources = await fetchResources({ page: 1, limit: 25, sort: 'created_at:desc' });
 * ```
 */
export async function fetchResources(
  params: ResourceListParams = {}
): Promise<ResourceListResponse> {
  const {
    page = 1,
    limit = 25,
    sort,
    ...filters
  } = params;

  // Calculate offset from page and limit
  const offset = (page - 1) * limit;

  // Parse sort parameter: "created_at:desc" → sort_by="created_at", sort_dir="desc"
  let sort_by: string | undefined;
  let sort_dir: string | undefined;

  if (sort) {
    const [field, direction] = sort.split(':');
    sort_by = field;
    sort_dir = direction || 'desc';
  }

  // Build query parameters
  const queryParams = new URLSearchParams();
  queryParams.append('offset', offset.toString());
  queryParams.append('limit', limit.toString());

  if (sort_by) {
    queryParams.append('sort_by', sort_by);
  }
  if (sort_dir) {
    queryParams.append('sort_dir', sort_dir);
  }

  // Add filter parameters
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      queryParams.append(key, String(value));
    }
  });

  const response = await apiClient.get<ResourceListResponse>(
    `/resources?${queryParams.toString()}`
  );

  return response.data;
}

/**
 * Ingest a new resource
 * 
 * @param payload - Resource data to ingest
 * @returns Promise resolving to accepted response with resource ID
 * 
 * @example
 * ```ts
 * const result = await ingestResource({
 *   title: 'My Article',
 *   url: 'https://example.com/article'
 * });
 * console.log(result.id); // Resource UUID
 * ```
 */
export async function ingestResource(
  payload: IngestResourcePayload
): Promise<ResourceAccepted> {
  const response = await apiClient.post<ResourceAccepted>('/resources', payload);
  return response.data;
}

/**
 * Get resource ingestion status (lightweight polling endpoint)
 * 
 * @param id - Resource UUID
 * @returns Promise resolving to resource status
 * 
 * @example
 * ```ts
 * const status = await getResourceStatus('123e4567-e89b-12d3-a456-426614174000');
 * console.log(status.ingestion_status); // 'pending' | 'processing' | 'completed' | 'failed'
 * ```
 */
export async function getResourceStatus(id: string): Promise<ResourceStatusResponse> {
  const response = await apiClient.get<ResourceStatusResponse>(`/resources/${id}/status`);
  return response.data;
}

/**
 * Get full resource details
 * 
 * @param id - Resource UUID
 * @returns Promise resolving to complete resource object
 * 
 * @example
 * ```ts
 * const resource = await getResource('123e4567-e89b-12d3-a456-426614174000');
 * console.log(resource.title);
 * ```
 */
export async function getResource(id: string): Promise<Resource> {
  const response = await apiClient.get<Resource>(`/resources/${id}`);
  return response.data;
}
