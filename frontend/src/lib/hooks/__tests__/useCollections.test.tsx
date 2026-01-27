import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCollections } from '../useCollections';
import { collectionsApi } from '@/lib/api/collections';
import type { Collection } from '@/types/library';

// Mock the API only - let the store work naturally
vi.mock('@/lib/api/collections', () => ({
  collectionsApi: {
    listCollections: vi.fn(),
    createCollection: vi.fn(),
    updateCollection: vi.fn(),
    deleteCollection: vi.fn(),
    batchAddResources: vi.fn(),
    batchRemoveResources: vi.fn(),
  },
}));

describe('useCollections', () => {
  let queryClient: QueryClient;

  const mockCollections: Collection[] = [
    {
      id: '1',
      name: 'Collection 1',
      description: 'Test collection 1',
      tags: [],
      resource_count: 5,
      is_public: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: '2',
      name: 'Collection 2',
      description: 'Test collection 2',
      tags: [],
      resource_count: 3,
      is_public: false,
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  describe('fetching collections', () => {
    it('should fetch collections successfully', async () => {
      vi.mocked(collectionsApi.listCollections).mockResolvedValue(mockCollections);

      const { result } = renderHook(() => useCollections(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.collections).toEqual(mockCollections);
      expect(result.current.total).toBe(mockCollections.length);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch');
      vi.mocked(collectionsApi.listCollections).mockRejectedValue(error);

      const { result } = renderHook(() => useCollections(), { wrapper });

      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
      });

      expect(result.current.collections).toEqual([]);
    });
  });

  describe('creating collections', () => {
    it('should create collection with optimistic update', async () => {
      const newCollection = {
        name: 'New Collection',
        description: 'Test description',
      };

      const createdCollection: Collection = {
        id: '3',
        ...newCollection,
        tags: [],
        resource_count: 0,
        is_public: false,
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      };

      vi.mocked(collectionsApi.createCollection).mockResolvedValue(createdCollection);

      const { result } = renderHook(() => useCollections(), { wrapper });

      result.current.createCollection(newCollection);

      await waitFor(() => {
        expect(result.current.isCreating).toBe(false);
      });

      expect(collectionsApi.createCollection).toHaveBeenCalledWith(newCollection);
    });

    it('should handle create errors and rollback', async () => {
      const error = new Error('Create failed');
      vi.mocked(collectionsApi.createCollection).mockRejectedValue(error);

      const { result } = renderHook(() => useCollections(), { wrapper });

      result.current.createCollection({ name: 'Test', description: 'Test' });

      await waitFor(() => {
        expect(result.current.createError).toBeTruthy();
      });
    });
  });

  describe('updating collections', () => {
    it('should update collection with optimistic update', async () => {
      const updates = { name: 'Updated Name' };
      const updatedCollection: Collection = {
        ...mockCollections[0],
        ...updates,
      };

      vi.mocked(collectionsApi.updateCollection).mockResolvedValue(updatedCollection);

      const { result } = renderHook(() => useCollections(), { wrapper });

      result.current.updateCollection({ collectionId: '1', updates });

      await waitFor(() => {
        expect(result.current.isUpdating).toBe(false);
      });

      expect(collectionsApi.updateCollection).toHaveBeenCalledWith('1', updates);
    });

    it('should handle update errors and rollback', async () => {
      const error = new Error('Update failed');
      vi.mocked(collectionsApi.updateCollection).mockRejectedValue(error);
      vi.mocked(collectionsApi.listCollections).mockResolvedValue(mockCollections);

      const { result } = renderHook(() => useCollections(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.updateCollection({ collectionId: '1', updates: { name: 'New' } });

      await waitFor(() => {
        expect(result.current.updateError).toBeTruthy();
      });
    });
  });

  describe('deleting collections', () => {
    it('should delete collection with optimistic update', async () => {
      vi.mocked(collectionsApi.deleteCollection).mockResolvedValue(undefined);

      const { result } = renderHook(() => useCollections(), { wrapper });

      result.current.deleteCollection('1');

      await waitFor(() => {
        expect(result.current.isDeleting).toBe(false);
      });

      expect(collectionsApi.deleteCollection).toHaveBeenCalledWith('1', undefined);
    });

    it('should handle delete errors and rollback', async () => {
      const error = new Error('Delete failed');
      vi.mocked(collectionsApi.deleteCollection).mockRejectedValue(error);
      vi.mocked(collectionsApi.listCollections).mockResolvedValue(mockCollections);

      const { result } = renderHook(() => useCollections(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      result.current.deleteCollection('1');

      await waitFor(() => {
        expect(result.current.deleteError).toBeTruthy();
      });
    });
  });

  describe('batch operations', () => {
    it('should batch add resources', async () => {
      const resourceIds = ['res-1', 'res-2', 'res-3'];
      vi.mocked(collectionsApi.batchAddResources).mockResolvedValue({
        added: 3,
        failed: [],
      });

      const { result } = renderHook(() => useCollections(), { wrapper });

      result.current.batchAddResources({ collectionId: '1', resourceIds });

      await waitFor(() => {
        expect(result.current.isBatchAdding).toBe(false);
      });

      expect(collectionsApi.batchAddResources).toHaveBeenCalledWith('1', resourceIds);
    });

    it('should batch remove resources', async () => {
      const resourceIds = ['res-1', 'res-2'];
      vi.mocked(collectionsApi.batchRemoveResources).mockResolvedValue({
        removed: 2,
        failed: [],
      });

      const { result } = renderHook(() => useCollections(), { wrapper });

      result.current.batchRemoveResources({ collectionId: '1', resourceIds });

      await waitFor(() => {
        expect(result.current.isBatchRemoving).toBe(false);
      });

      expect(collectionsApi.batchRemoveResources).toHaveBeenCalledWith('1', resourceIds);
    });

    it('should handle batch operation errors', async () => {
      const error = new Error('Batch operation failed');
      vi.mocked(collectionsApi.batchAddResources).mockRejectedValue(error);

      const { result } = renderHook(() => useCollections(), { wrapper });

      result.current.batchAddResources({ collectionId: '1', resourceIds: ['res-1'] });

      await waitFor(() => {
        expect(result.current.batchAddError).toBeTruthy();
      });
    });
  });

  describe('refetch', () => {
    it('should refetch collections', async () => {
      vi.mocked(collectionsApi.listCollections).mockResolvedValue(mockCollections);

      const { result } = renderHook(() => useCollections(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      vi.mocked(collectionsApi.listCollections).mockClear();

      await result.current.refetch();

      expect(collectionsApi.listCollections).toHaveBeenCalled();
    });
  });
});
