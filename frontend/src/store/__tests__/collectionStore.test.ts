/**
 * Collection Store Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useCollectionStore } from '../collectionStore';
import { collectionsAPI } from '@/services/api';

// Mock the API
vi.mock('@/services/api', () => ({
  collectionsAPI: {
    list: vi.fn(),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    addResources: vi.fn(),
    removeResources: vi.fn(),
  },
}));

describe('CollectionStore', () => {
  beforeEach(() => {
    useCollectionStore.getState().reset();
    vi.clearAllMocks();
  });

  describe('fetchCollections', () => {
    it('should fetch collections and build tree', async () => {
      const mockCollections = [
        { id: '1', name: 'Collection 1', parent_id: null },
        { id: '2', name: 'Collection 2', parent_id: '1' },
      ];

      vi.mocked(collectionsAPI.list).mockResolvedValueOnce({
        data: mockCollections,
        meta: { page: 1, limit: 100, total: 2, pages: 1 },
      } as any);

      await useCollectionStore.getState().fetchCollections();

      const state = useCollectionStore.getState();
      expect(state.collections).toEqual(mockCollections);
      expect(state.collectionTree).toHaveLength(1);
      expect(state.collectionTree[0].children).toHaveLength(1);
    });
  });

  describe('selectCollection', () => {
    it('should select a collection', async () => {
      const mockCollection = {
        id: '1',
        name: 'Collection 1',
        resources: [],
        subcollections: [],
      };

      vi.mocked(collectionsAPI.get).mockResolvedValueOnce(mockCollection as any);

      await useCollectionStore.getState().selectCollection('1');

      const state = useCollectionStore.getState();
      expect(state.activeCollection).toEqual(mockCollection);
    });
  });

  describe('createCollection', () => {
    it('should create a collection', async () => {
      const newCollection = { id: '3', name: 'New Collection', parent_id: null };

      vi.mocked(collectionsAPI.create).mockResolvedValueOnce(newCollection as any);

      const result = await useCollectionStore.getState().createCollection({
        name: 'New Collection',
      });

      expect(result).toEqual(newCollection);
      expect(useCollectionStore.getState().collections).toContainEqual(newCollection);
    });
  });

  describe('updateCollection', () => {
    it('should update a collection', async () => {
      const mockCollection = { id: '1', name: 'Old Name', parent_id: null };
      useCollectionStore.setState({ collections: [mockCollection as any] });

      const updated = { ...mockCollection, name: 'New Name' };
      vi.mocked(collectionsAPI.update).mockResolvedValueOnce(updated as any);

      await useCollectionStore.getState().updateCollection('1', { name: 'New Name' });

      const state = useCollectionStore.getState();
      expect(state.collections[0].name).toBe('New Name');
    });
  });

  describe('deleteCollection', () => {
    it('should delete a collection', async () => {
      const mockCollections = [
        { id: '1', name: 'Collection 1' },
        { id: '2', name: 'Collection 2' },
      ];
      useCollectionStore.setState({ collections: mockCollections as any });

      vi.mocked(collectionsAPI.delete).mockResolvedValueOnce(undefined as any);

      await useCollectionStore.getState().deleteCollection('1');

      const state = useCollectionStore.getState();
      expect(state.collections).toHaveLength(1);
      expect(state.collections[0].id).toBe('2');
    });
  });

  describe('toggleCollectionExpanded', () => {
    it('should toggle collection expanded state', () => {
      const tree = [
        {
          id: '1',
          name: 'Collection 1',
          isExpanded: false,
          children: [],
          depth: 0,
        },
      ];
      useCollectionStore.setState({ collectionTree: tree as any });

      useCollectionStore.getState().toggleCollectionExpanded('1');

      const state = useCollectionStore.getState();
      expect(state.collectionTree[0].isExpanded).toBe(true);
    });
  });
});
