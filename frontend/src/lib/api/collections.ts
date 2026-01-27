/**
 * Collections API Client
 * 
 * Provides API endpoints for Phase 3 Living Library collection features:
 * - Collection management (create, list, get, update, delete)
 * - Resource management within collections
 * - Batch operations for adding/removing resources
 * - Similar collection discovery
 * 
 * Phase: 3 Living Library
 * Requirements: US-3.7, US-3.8
 */

import { apiClient } from '@/core/api/client';
import type {
  Collection,
  CollectionCreate,
  CollectionUpdate,
  CollectionWithResources,
  SimilarCollection,
  BatchOperationResult,
  Resource,
} from '@/types/library';

// ============================================================================
// Collections API Client Interface
// ============================================================================

/**
 * Collections API client with all Phase 3 collection-related endpoints
 */
export const collectionsApi = {
  // ==========================================================================
  // Collection Management Endpoints
  // ==========================================================================

  /**
   * Create a new collection
   * 
   * Creates a new collection for organizing resources. Collections can be
   * private, shared, or public, and can optionally have a parent collection
   * for hierarchical organization.
   * 
   * @param data - Collection creation data
   * @returns Created collection with ID
   * @endpoint POST /collections
   * 
   * @example
   * ```typescript
   * const collection = await collectionsApi.createCollection({
   *   name: 'Machine Learning Papers',
   *   description: 'Collection of ML research papers',
   *   tags: ['ml', 'research'],
   *   is_public: false
   * });
   * console.log(`Created collection: ${collection.id}`);
   * ```
   */
  createCollection: async (data: CollectionCreate): Promise<Collection> => {
    const response = await apiClient.post<Collection>('/collections', data);
    return response.data;
  },

  /**
   * List collections with optional filtering
   * 
   * Fetches all collections accessible to the user, with optional filtering
   * by owner, parent, visibility, and pagination support.
   * 
   * @param params - Query parameters for filtering and pagination
   * @returns Array of collections
   * @endpoint GET /collections
   * 
   * @example
   * ```typescript
   * // Get first 20 public collections
   * const collections = await collectionsApi.listCollections({
   *   include_public: true,
   *   limit: 20,
   *   offset: 0
   * });
   * console.log(`Found ${collections.length} collections`);
   * ```
   */
  listCollections: async (params?: {
    owner_id?: string;
    parent_id?: string;
    include_public?: boolean;
    visibility?: 'private' | 'shared' | 'public';
    limit?: number;
    offset?: number;
  }): Promise<Collection[]> => {
    const response = await apiClient.get<Collection[]>('/collections', {
      params,
    });
    
    return response.data;
  },

  /**
   * Get a single collection with its resources
   * 
   * Fetches complete collection details including metadata and paginated
   * list of resources. Supports access control via owner_id parameter.
   * 
   * @param collectionId - Collection ID
   * @param params - Query parameters for pagination and access control
   * @returns Collection with resources
   * @endpoint GET /collections/{collection_id}
   * 
   * @example
   * ```typescript
   * const collection = await collectionsApi.getCollection('col_123', {
   *   limit: 50,
   *   offset: 0
   * });
   * console.log(`${collection.name}: ${collection.resources.length} resources`);
   * ```
   */
  getCollection: async (
    collectionId: string,
    params?: {
      owner_id?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<CollectionWithResources> => {
    const response = await apiClient.get<CollectionWithResources>(
      `/collections/${collectionId}`,
      { params }
    );
    
    return response.data;
  },

  /**
   * Update a collection (partial update)
   * 
   * Updates one or more fields of an existing collection.
   * Only provided fields are updated; others remain unchanged.
   * 
   * @param collectionId - Collection ID
   * @param updates - Partial collection object with fields to update
   * @returns Updated collection
   * @endpoint PUT /collections/{collection_id}
   * 
   * @example
   * ```typescript
   * // Update name and visibility
   * const updated = await collectionsApi.updateCollection('col_123', {
   *   name: 'Updated Collection Name',
   *   is_public: true
   * });
   * ```
   */
  updateCollection: async (
    collectionId: string,
    updates: CollectionUpdate
  ): Promise<Collection> => {
    const response = await apiClient.put<Collection>(
      `/collections/${collectionId}`,
      updates
    );
    
    return response.data;
  },

  /**
   * Delete a collection
   * 
   * Permanently deletes a collection. Resources in the collection are not
   * deleted, only the collection itself and its associations.
   * 
   * @param collectionId - Collection ID
   * @param ownerId - Optional owner ID for access control
   * @returns void (204 No Content)
   * @endpoint DELETE /collections/{collection_id}
   * 
   * @example
   * ```typescript
   * await collectionsApi.deleteCollection('col_123');
   * console.log('Collection deleted');
   * ```
   */
  deleteCollection: async (
    collectionId: string,
    ownerId?: string
  ): Promise<void> => {
    await apiClient.delete(`/collections/${collectionId}`, {
      params: ownerId ? { owner_id: ownerId } : undefined,
    });
  },

  // ==========================================================================
  // Resource Management Endpoints
  // ==========================================================================

  /**
   * Get resources in a collection
   * 
   * Fetches paginated list of resources in a collection. This is an
   * alternative to getCollection() when you only need the resources
   * without collection metadata.
   * 
   * @param collectionId - Collection ID
   * @param params - Query parameters for pagination and access control
   * @returns Array of resources
   * @endpoint GET /collections/{collection_id}/resources
   * 
   * @example
   * ```typescript
   * const resources = await collectionsApi.getCollectionResources('col_123', {
   *   limit: 100,
   *   offset: 0
   * });
   * console.log(`Found ${resources.length} resources`);
   * ```
   */
  getCollectionResources: async (
    collectionId: string,
    params?: {
      owner_id?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<Resource[]> => {
    const response = await apiClient.get<Resource[]>(
      `/collections/${collectionId}/resources`,
      { params }
    );
    
    return response.data;
  },

  /**
   * Add a resource to a collection
   * 
   * Adds a single resource to a collection. If the resource is already
   * in the collection, the operation is idempotent and returns success.
   * 
   * @param collectionId - Collection ID
   * @param resourceId - Resource ID to add
   * @returns Operation result
   * @endpoint POST /collections/{collection_id}/resources
   * 
   * @example
   * ```typescript
   * const result = await collectionsApi.addResourceToCollection(
   *   'col_123',
   *   'res_456'
   * );
   * console.log(result.message);
   * ```
   */
  addResourceToCollection: async (
    collectionId: string,
    resourceId: string
  ): Promise<{
    collection_id: string;
    resource_id: string;
    added: boolean;
    message: string;
  }> => {
    const response = await apiClient.post(
      `/collections/${collectionId}/resources`,
      { resource_id: resourceId }
    );
    
    return response.data;
  },

  /**
   * Remove a resource from a collection
   * 
   * Removes a single resource from a collection. The resource itself is
   * not deleted, only the association with the collection.
   * 
   * @param collectionId - Collection ID
   * @param resourceId - Resource ID to remove
   * @param ownerId - Optional owner ID for access control
   * @returns void (204 No Content)
   * @endpoint DELETE /collections/{collection_id}/resources/{resource_id}
   * 
   * @example
   * ```typescript
   * await collectionsApi.removeResourceFromCollection('col_123', 'res_456');
   * console.log('Resource removed from collection');
   * ```
   */
  removeResourceFromCollection: async (
    collectionId: string,
    resourceId: string,
    ownerId?: string
  ): Promise<void> => {
    await apiClient.delete(
      `/collections/${collectionId}/resources/${resourceId}`,
      {
        params: ownerId ? { owner_id: ownerId } : undefined,
      }
    );
  },

  // ==========================================================================
  // Batch Operations Endpoints
  // ==========================================================================

  /**
   * Batch add resources to a collection
   * 
   * Adds multiple resources to a collection in a single operation.
   * More efficient than adding resources one at a time. Supports up to
   * 100 resources per batch. Handles partial failures gracefully.
   * 
   * @param collectionId - Collection ID
   * @param resourceIds - Array of resource IDs to add (max 100)
   * @returns Batch operation result with counts and errors
   * @endpoint POST /collections/{collection_id}/resources/batch
   * 
   * @example
   * ```typescript
   * const result = await collectionsApi.batchAddResources('col_123', [
   *   'res_1', 'res_2', 'res_3', 'res_4', 'res_5'
   * ]);
   * console.log(`Added ${result.added} resources`);
   * if (result.failed.length > 0) {
   *   console.error(`Failed: ${result.failed.join(', ')}`);
   * }
   * ```
   */
  batchAddResources: async (
    collectionId: string,
    resourceIds: string[]
  ): Promise<BatchOperationResult> => {
    const response = await apiClient.post<{
      collection_id: string;
      added: number;
      skipped: number;
      invalid: number;
      message: string;
    }>(`/collections/${collectionId}/resources/batch`, {
      resource_ids: resourceIds,
    });
    
    // Transform backend response to match BatchOperationResult type
    const data = response.data;
    return {
      added: data.added,
      failed: [], // Backend doesn't return failed IDs for add operation
      errors: data.invalid > 0 ? [{
        resource_id: 'unknown',
        error: `${data.invalid} invalid resource IDs`
      }] : undefined,
    };
  },

  /**
   * Batch remove resources from a collection
   * 
   * Removes multiple resources from a collection in a single operation.
   * More efficient than removing resources one at a time. Supports up to
   * 100 resources per batch. Handles partial failures gracefully.
   * 
   * @param collectionId - Collection ID
   * @param resourceIds - Array of resource IDs to remove (max 100)
   * @returns Batch operation result with counts and errors
   * @endpoint DELETE /collections/{collection_id}/resources/batch
   * 
   * @example
   * ```typescript
   * const result = await collectionsApi.batchRemoveResources('col_123', [
   *   'res_1', 'res_2', 'res_3'
   * ]);
   * console.log(`Removed ${result.removed} resources`);
   * if (result.failed.length > 0) {
   *   console.error(`Failed: ${result.failed.join(', ')}`);
   * }
   * ```
   */
  batchRemoveResources: async (
    collectionId: string,
    resourceIds: string[]
  ): Promise<BatchOperationResult> => {
    const response = await apiClient.delete<{
      collection_id: string;
      removed: number;
      not_found: number;
      message: string;
    }>(`/collections/${collectionId}/resources/batch`, {
      data: {
        resource_ids: resourceIds,
      },
    });
    
    // Transform backend response to match BatchOperationResult type
    const data = response.data;
    return {
      removed: data.removed,
      failed: [], // Backend doesn't return failed IDs for remove operation
      errors: data.not_found > 0 ? [{
        resource_id: 'unknown',
        error: `${data.not_found} resources not found in collection`
      }] : undefined,
    };
  },

  // ==========================================================================
  // Discovery Endpoints
  // ==========================================================================

  /**
   * Find similar collections
   * 
   * Uses semantic similarity between collection embeddings to find related
   * collections that might be of interest. Useful for discovering related
   * content and connecting with other users' collections.
   * 
   * @param collectionId - Collection ID
   * @param params - Query parameters for filtering and pagination
   * @returns Array of similar collections with similarity scores
   * @endpoint GET /collections/{collection_id}/similar-collections
   * 
   * @example
   * ```typescript
   * const similar = await collectionsApi.findSimilarCollections('col_123', {
   *   limit: 10,
   *   min_similarity: 0.7
   * });
   * similar.forEach(col => {
   *   console.log(`${col.collection.name}: ${col.similarity.toFixed(2)} similarity`);
   * });
   * ```
   */
  findSimilarCollections: async (
    collectionId: string,
    params?: {
      owner_id?: string;
      limit?: number;
      min_similarity?: number;
    }
  ): Promise<SimilarCollection[]> => {
    const response = await apiClient.get<Array<{
      collection_id: string;
      name: string;
      description?: string;
      similarity_score: number;
      owner_id?: string;
      visibility?: string;
      resource_count: number;
    }>>(`/collections/${collectionId}/similar-collections`, {
      params,
    });
    
    // Transform backend response to match SimilarCollection type
    return response.data.map(item => ({
      collection: {
        id: item.collection_id,
        name: item.name,
        description: item.description,
        tags: [],
        resource_count: item.resource_count,
        created_at: new Date().toISOString(), // Backend doesn't return these
        updated_at: new Date().toISOString(),
        owner_id: item.owner_id,
        is_public: item.visibility === 'public',
      },
      similarity: item.similarity_score,
      common_resources: 0, // Backend doesn't return this
      common_tags: [], // Backend doesn't return this
    }));
  },

  // ==========================================================================
  // Health Check Endpoint
  // ==========================================================================

  /**
   * Health check for collections module
   * 
   * Checks if the collections module is operational and can process requests.
   * Used for connection testing and monitoring.
   * 
   * @returns Health status
   * @endpoint GET /collections/health
   * 
   * @example
   * ```typescript
   * try {
   *   const health = await collectionsApi.health();
   *   console.log('Collections module is healthy:', health);
   * } catch (error) {
   *   console.error('Collections module is down:', error);
   * }
   * ```
   */
  health: async (): Promise<{
    status: string;
    module?: {
      name: string;
      version: string;
      domain: string;
    };
    database?: {
      healthy: boolean;
      message: string;
    };
    event_handlers?: {
      registered: boolean;
      count: number;
      events: string[];
    };
    timestamp?: string;
  }> => {
    const response = await apiClient.get('/collections/health');
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
 *   queryKey: collectionsQueryKeys.collections.list({ owner_id: 'user_123' }),
 *   queryFn: () => collectionsApi.listCollections({ owner_id: 'user_123' }),
 * });
 * ```
 */
export const collectionsQueryKeys = {
  /**
   * Collection-related query keys
   */
  collections: {
    /** All collections query keys */
    all: () => ['collections'] as const,
    /** Collections list with optional filters */
    list: (params?: Parameters<typeof collectionsApi.listCollections>[0]) =>
      ['collections', 'list', params] as const,
    /** Single collection by ID */
    detail: (collectionId: string, params?: Parameters<typeof collectionsApi.getCollection>[1]) =>
      ['collections', 'detail', collectionId, params] as const,
  },

  /**
   * Resource-related query keys within collections
   */
  resources: {
    /** Resources in a collection */
    list: (collectionId: string, params?: Parameters<typeof collectionsApi.getCollectionResources>[1]) =>
      ['collections', collectionId, 'resources', params] as const,
  },

  /**
   * Discovery-related query keys
   */
  discovery: {
    /** Similar collections */
    similar: (collectionId: string, params?: Parameters<typeof collectionsApi.findSimilarCollections>[1]) =>
      ['collections', collectionId, 'similar', params] as const,
  },

  /**
   * Health check query key
   */
  health: () => ['collections', 'health'] as const,
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
export const collectionsCacheConfig = {
  collections: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
  resources: {
    staleTime: 2 * 60 * 1000, // 2 minutes (resources may be added/removed frequently)
    cacheTime: 5 * 60 * 1000, // 5 minutes
  },
  discovery: {
    staleTime: 30 * 60 * 1000, // 30 minutes (similarity doesn't change often)
    cacheTime: 60 * 60 * 1000, // 1 hour
  },
  health: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  },
};
