/**
 * Collections API Client Tests
 * 
 * Tests for the collections API client endpoints including:
 * - Collection CRUD operations
 * - Resource management within collections
 * - Batch operations
 * - Similar collection discovery
 * - Error handling
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { collectionsApi } from '../collections';
import { apiClient } from '@/core/api/client';
import type {
  Collection,
  CollectionCreate,
  CollectionUpdate,
  CollectionWithResources,
  Resource,
} from '@/types/library';

// Mock the API client
vi.mock('@/core/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('collectionsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ==========================================================================
  // Collection Management Tests
  // ==========================================================================

  describe('createCollection', () => {
    it('should create a new collection', async () => {
      const createData: CollectionCreate = {
        name: 'Test Collection',
        description: 'A test collection',
        tags: ['test', 'demo'],
        is_public: false,
      };

      const mockResponse: Collection = {
        id: 'col_123',
        name: 'Test Collection',
        description: 'A test collection',
        tags: ['test', 'demo'],
        resource_count: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        is_public: false,
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await collectionsApi.createCollection(createData);

      expect(apiClient.post).toHaveBeenCalledWith('/collections', createData);
      expect(result).toEqual(mockResponse);
    });

    it('should handle creation errors', async () => {
      const createData: CollectionCreate = {
        name: 'Test Collection',
      };

      vi.mocked(apiClient.post).mockRejectedValue(new Error('Network error'));

      await expect(collectionsApi.createCollection(createData)).rejects.toThrow('Network error');
    });
  });

  describe('listCollections', () => {
    it('should list collections without filters', async () => {
      const mockCollections: Collection[] = [
        {
          id: 'col_1',
          name: 'Collection 1',
          resource_count: 5,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          is_public: false,
        },
        {
          id: 'col_2',
          name: 'Collection 2',
          resource_count: 10,
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
          is_public: true,
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockCollections });

      const result = await collectionsApi.listCollections();

      expect(apiClient.get).toHaveBeenCalledWith('/collections', { params: undefined });
      expect(result).toEqual(mockCollections);
    });

    it('should list collections with filters', async () => {
      const params = {
        owner_id: 'user_123',
        include_public: true,
        limit: 20,
        offset: 0,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      await collectionsApi.listCollections(params);

      expect(apiClient.get).toHaveBeenCalledWith('/collections', { params });
    });
  });

  describe('getCollection', () => {
    it('should get a collection with resources', async () => {
      const mockCollection: CollectionWithResources = {
        id: 'col_123',
        name: 'Test Collection',
        description: 'A test collection',
        resource_count: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        is_public: false,
        resources: [
          {
            id: 'res_1',
            title: 'Resource 1',
            ingestion_status: 'completed',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
          {
            id: 'res_2',
            title: 'Resource 2',
            ingestion_status: 'completed',
            created_at: '2024-01-02T00:00:00Z',
            updated_at: '2024-01-02T00:00:00Z',
          },
        ] as Resource[],
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockCollection });

      const result = await collectionsApi.getCollection('col_123');

      expect(apiClient.get).toHaveBeenCalledWith('/collections/col_123', { params: undefined });
      expect(result).toEqual(mockCollection);
      expect(result.resources).toHaveLength(2);
    });

    it('should get a collection with pagination params', async () => {
      const params = { limit: 50, offset: 0 };

      vi.mocked(apiClient.get).mockResolvedValue({
        data: {
          id: 'col_123',
          name: 'Test',
          resource_count: 0,
          resources: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          is_public: false,
        },
      });

      await collectionsApi.getCollection('col_123', params);

      expect(apiClient.get).toHaveBeenCalledWith('/collections/col_123', { params });
    });
  });

  describe('updateCollection', () => {
    it('should update a collection', async () => {
      const updates: CollectionUpdate = {
        name: 'Updated Name',
        is_public: true,
      };

      const mockResponse: Collection = {
        id: 'col_123',
        name: 'Updated Name',
        resource_count: 5,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        is_public: true,
      };

      vi.mocked(apiClient.put).mockResolvedValue({ data: mockResponse });

      const result = await collectionsApi.updateCollection('col_123', updates);

      expect(apiClient.put).toHaveBeenCalledWith('/collections/col_123', updates);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('deleteCollection', () => {
    it('should delete a collection without owner_id', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: null });

      await collectionsApi.deleteCollection('col_123');

      expect(apiClient.delete).toHaveBeenCalledWith('/collections/col_123', {
        params: undefined,
      });
    });

    it('should delete a collection with owner_id', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: null });

      await collectionsApi.deleteCollection('col_123', 'user_123');

      expect(apiClient.delete).toHaveBeenCalledWith('/collections/col_123', {
        params: { owner_id: 'user_123' },
      });
    });
  });

  // ==========================================================================
  // Resource Management Tests
  // ==========================================================================

  describe('getCollectionResources', () => {
    it('should get resources in a collection', async () => {
      const mockResources: Resource[] = [
        {
          id: 'res_1',
          title: 'Resource 1',
          ingestion_status: 'completed',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ] as Resource[];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResources });

      const result = await collectionsApi.getCollectionResources('col_123');

      expect(apiClient.get).toHaveBeenCalledWith('/collections/col_123/resources', {
        params: undefined,
      });
      expect(result).toEqual(mockResources);
    });

    it('should get resources with pagination', async () => {
      const params = { limit: 100, offset: 0 };

      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      await collectionsApi.getCollectionResources('col_123', params);

      expect(apiClient.get).toHaveBeenCalledWith('/collections/col_123/resources', {
        params,
      });
    });
  });

  describe('addResourceToCollection', () => {
    it('should add a resource to a collection', async () => {
      const mockResponse = {
        collection_id: 'col_123',
        resource_id: 'res_456',
        added: true,
        message: 'Resource added to collection',
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await collectionsApi.addResourceToCollection('col_123', 'res_456');

      expect(apiClient.post).toHaveBeenCalledWith('/collections/col_123/resources', {
        resource_id: 'res_456',
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('removeResourceFromCollection', () => {
    it('should remove a resource from a collection', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: null });

      await collectionsApi.removeResourceFromCollection('col_123', 'res_456');

      expect(apiClient.delete).toHaveBeenCalledWith('/collections/col_123/resources/res_456', {
        params: undefined,
      });
    });

    it('should remove a resource with owner_id', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: null });

      await collectionsApi.removeResourceFromCollection('col_123', 'res_456', 'user_123');

      expect(apiClient.delete).toHaveBeenCalledWith('/collections/col_123/resources/res_456', {
        params: { owner_id: 'user_123' },
      });
    });
  });

  // ==========================================================================
  // Batch Operations Tests
  // ==========================================================================

  describe('batchAddResources', () => {
    it('should batch add resources successfully', async () => {
      const resourceIds = ['res_1', 'res_2', 'res_3'];
      const mockResponse = {
        collection_id: 'col_123',
        added: 3,
        skipped: 0,
        invalid: 0,
        message: 'Added 3 resources',
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await collectionsApi.batchAddResources('col_123', resourceIds);

      expect(apiClient.post).toHaveBeenCalledWith('/collections/col_123/resources/batch', {
        resource_ids: resourceIds,
      });
      expect(result.added).toBe(3);
      expect(result.failed).toEqual([]);
    });

    it('should handle partial failures in batch add', async () => {
      const resourceIds = ['res_1', 'res_2', 'invalid'];
      const mockResponse = {
        collection_id: 'col_123',
        added: 2,
        skipped: 0,
        invalid: 1,
        message: 'Added 2 resources, 1 invalid',
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await collectionsApi.batchAddResources('col_123', resourceIds);

      expect(result.added).toBe(2);
      expect(result.errors).toBeDefined();
      expect(result.errors?.[0].error).toContain('1 invalid');
    });
  });

  describe('batchRemoveResources', () => {
    it('should batch remove resources successfully', async () => {
      const resourceIds = ['res_1', 'res_2'];
      const mockResponse = {
        collection_id: 'col_123',
        removed: 2,
        not_found: 0,
        message: 'Removed 2 resources',
      };

      vi.mocked(apiClient.delete).mockResolvedValue({ data: mockResponse });

      const result = await collectionsApi.batchRemoveResources('col_123', resourceIds);

      expect(apiClient.delete).toHaveBeenCalledWith('/collections/col_123/resources/batch', {
        data: { resource_ids: resourceIds },
      });
      expect(result.removed).toBe(2);
      expect(result.failed).toEqual([]);
    });

    it('should handle not found resources in batch remove', async () => {
      const resourceIds = ['res_1', 'res_2', 'res_3'];
      const mockResponse = {
        collection_id: 'col_123',
        removed: 2,
        not_found: 1,
        message: 'Removed 2 resources, 1 not found',
      };

      vi.mocked(apiClient.delete).mockResolvedValue({ data: mockResponse });

      const result = await collectionsApi.batchRemoveResources('col_123', resourceIds);

      expect(result.removed).toBe(2);
      expect(result.errors).toBeDefined();
      expect(result.errors?.[0].error).toContain('1 resources not found');
    });
  });

  // ==========================================================================
  // Discovery Tests
  // ==========================================================================

  describe('findSimilarCollections', () => {
    it('should find similar collections', async () => {
      const mockResponse = [
        {
          collection_id: 'col_456',
          name: 'Similar Collection',
          description: 'A similar collection',
          similarity_score: 0.85,
          owner_id: 'user_456',
          visibility: 'public',
          resource_count: 10,
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await collectionsApi.findSimilarCollections('col_123');

      expect(apiClient.get).toHaveBeenCalledWith('/collections/col_123/similar-collections', {
        params: undefined,
      });
      expect(result).toHaveLength(1);
      expect(result[0].collection.id).toBe('col_456');
      expect(result[0].similarity).toBe(0.85);
    });

    it('should find similar collections with filters', async () => {
      const params = {
        limit: 10,
        min_similarity: 0.7,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      await collectionsApi.findSimilarCollections('col_123', params);

      expect(apiClient.get).toHaveBeenCalledWith('/collections/col_123/similar-collections', {
        params,
      });
    });
  });

  // ==========================================================================
  // Health Check Tests
  // ==========================================================================

  describe('health', () => {
    it('should check health status', async () => {
      const mockHealth = {
        status: 'healthy',
        module: {
          name: 'collections',
          version: '1.0.0',
          domain: 'collections',
        },
        database: {
          healthy: true,
          message: 'Database connection healthy',
        },
        timestamp: '2024-01-01T00:00:00Z',
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockHealth });

      const result = await collectionsApi.health();

      expect(apiClient.get).toHaveBeenCalledWith('/collections/health');
      expect(result.status).toBe('healthy');
      expect(result.module?.name).toBe('collections');
    });

    it('should handle health check errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Service unavailable'));

      await expect(collectionsApi.health()).rejects.toThrow('Service unavailable');
    });
  });
});
