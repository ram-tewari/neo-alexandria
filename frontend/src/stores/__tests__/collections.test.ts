/**
 * Collections Store Tests
 * 
 * Tests for the collections Zustand store including collection management,
 * resource selection, and batch operations.
 * 
 * Phase: 3 Living Library
 * Epic: 2 State Management
 * Task: 2.4
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  useCollectionsStore,
  selectSelectedCount,
  selectSelectedResourceIdsArray,
  selectHasSelection,
  selectCollectionById,
  selectCollectionsSortedByName,
  selectCollectionsByResourceCount,
  selectCollectionsByDate,
  selectPublicCollections,
  selectPrivateCollections,
  selectTotalResourceCount
} from '../collections';
import type { Collection } from '@/types/library';

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Create a mock collection for testing
 */
const createMockCollection = (overrides?: Partial<Collection>): Collection => ({
  id: `col_${Math.random().toString(36).substr(2, 9)}`,
  name: 'Test Collection',
  description: 'Test description',
  tags: [],
  resource_count: 0,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  is_public: false,
  ...overrides
});

/**
 * Reset store to initial state before each test
 */
const resetStore = () => {
  useCollectionsStore.setState({
    collections: [],
    selectedCollection: null,
    selectedResourceIds: new Set(),
    batchMode: false
  });
};

// ============================================================================
// Tests
// ============================================================================

describe('Collections Store', () => {
  beforeEach(() => {
    resetStore();
  });

  // ==========================================================================
  // Initial State
  // ==========================================================================

  describe('Initial State', () => {
    it('should have empty collections array', () => {
      const { collections } = useCollectionsStore.getState();
      expect(collections).toEqual([]);
    });

    it('should have no selected collection', () => {
      const { selectedCollection } = useCollectionsStore.getState();
      expect(selectedCollection).toBeNull();
    });

    it('should have empty resource selection', () => {
      const { selectedResourceIds } = useCollectionsStore.getState();
      expect(selectedResourceIds.size).toBe(0);
    });

    it('should have batch mode disabled', () => {
      const { batchMode } = useCollectionsStore.getState();
      expect(batchMode).toBe(false);
    });
  });

  // ==========================================================================
  // setCollections Action
  // ==========================================================================

  describe('setCollections', () => {
    it('should set collections', () => {
      const collections = [
        createMockCollection({ id: 'col_1' }),
        createMockCollection({ id: 'col_2' })
      ];

      useCollectionsStore.getState().setCollections(collections);

      expect(useCollectionsStore.getState().collections).toEqual(collections);
    });

    it('should replace existing collections', () => {
      const initial = [createMockCollection({ id: 'col_1' })];
      const updated = [createMockCollection({ id: 'col_2' })];

      useCollectionsStore.getState().setCollections(initial);
      useCollectionsStore.getState().setCollections(updated);

      expect(useCollectionsStore.getState().collections).toEqual(updated);
    });
  });

  // ==========================================================================
  // addCollection Action
  // ==========================================================================

  describe('addCollection', () => {
    it('should add collection to beginning of list', () => {
      const existing = createMockCollection({ id: 'col_1' });
      const newCollection = createMockCollection({ id: 'col_2' });

      useCollectionsStore.getState().setCollections([existing]);
      useCollectionsStore.getState().addCollection(newCollection);

      const { collections } = useCollectionsStore.getState();
      expect(collections).toHaveLength(2);
      expect(collections[0]).toEqual(newCollection);
      expect(collections[1]).toEqual(existing);
    });

    it('should work with empty list', () => {
      const collection = createMockCollection();
      useCollectionsStore.getState().addCollection(collection);

      expect(useCollectionsStore.getState().collections).toEqual([collection]);
    });
  });

  // ==========================================================================
  // updateCollection Action
  // ==========================================================================

  describe('updateCollection', () => {
    it('should update collection by ID', () => {
      const collection = createMockCollection({ id: 'col_1', name: 'Original' });
      useCollectionsStore.getState().setCollections([collection]);

      useCollectionsStore.getState().updateCollection('col_1', { name: 'Updated' });

      const updated = useCollectionsStore.getState().collections[0];
      expect(updated.name).toBe('Updated');
      expect(updated.id).toBe('col_1');
    });

    it('should not affect other collections', () => {
      const collections = [
        createMockCollection({ id: 'col_1', name: 'First' }),
        createMockCollection({ id: 'col_2', name: 'Second' })
      ];
      useCollectionsStore.getState().setCollections(collections);

      useCollectionsStore.getState().updateCollection('col_1', { name: 'Updated' });

      const { collections: updated } = useCollectionsStore.getState();
      expect(updated[0].name).toBe('Updated');
      expect(updated[1].name).toBe('Second');
    });

    it('should update selected collection if it matches', () => {
      const collection = createMockCollection({ id: 'col_1', name: 'Original' });
      useCollectionsStore.getState().setCollections([collection]);
      useCollectionsStore.getState().selectCollection(collection);

      useCollectionsStore.getState().updateCollection('col_1', { name: 'Updated' });

      const { selectedCollection } = useCollectionsStore.getState();
      expect(selectedCollection?.name).toBe('Updated');
    });

    it('should not update selected collection if ID does not match', () => {
      const collection1 = createMockCollection({ id: 'col_1', name: 'First' });
      const collection2 = createMockCollection({ id: 'col_2', name: 'Second' });
      useCollectionsStore.getState().setCollections([collection1, collection2]);
      useCollectionsStore.getState().selectCollection(collection1);

      useCollectionsStore.getState().updateCollection('col_2', { name: 'Updated' });

      const { selectedCollection } = useCollectionsStore.getState();
      expect(selectedCollection?.name).toBe('First');
    });
  });

  // ==========================================================================
  // removeCollection Action
  // ==========================================================================

  describe('removeCollection', () => {
    it('should remove collection by ID', () => {
      const collections = [
        createMockCollection({ id: 'col_1' }),
        createMockCollection({ id: 'col_2' })
      ];
      useCollectionsStore.getState().setCollections(collections);

      useCollectionsStore.getState().removeCollection('col_1');

      const { collections: updated } = useCollectionsStore.getState();
      expect(updated).toHaveLength(1);
      expect(updated[0].id).toBe('col_2');
    });

    it('should clear selected collection if it matches removed ID', () => {
      const collection = createMockCollection({ id: 'col_1' });
      useCollectionsStore.getState().setCollections([collection]);
      useCollectionsStore.getState().selectCollection(collection);

      useCollectionsStore.getState().removeCollection('col_1');

      expect(useCollectionsStore.getState().selectedCollection).toBeNull();
    });

    it('should not clear selected collection if ID does not match', () => {
      const collection1 = createMockCollection({ id: 'col_1' });
      const collection2 = createMockCollection({ id: 'col_2' });
      useCollectionsStore.getState().setCollections([collection1, collection2]);
      useCollectionsStore.getState().selectCollection(collection1);

      useCollectionsStore.getState().removeCollection('col_2');

      expect(useCollectionsStore.getState().selectedCollection).toEqual(collection1);
    });
  });

  // ==========================================================================
  // selectCollection Action
  // ==========================================================================

  describe('selectCollection', () => {
    it('should select a collection', () => {
      const collection = createMockCollection();
      useCollectionsStore.getState().selectCollection(collection);

      expect(useCollectionsStore.getState().selectedCollection).toEqual(collection);
    });

    it('should deselect when passed null', () => {
      const collection = createMockCollection();
      useCollectionsStore.getState().selectCollection(collection);
      useCollectionsStore.getState().selectCollection(null);

      expect(useCollectionsStore.getState().selectedCollection).toBeNull();
    });
  });

  // ==========================================================================
  // Resource Selection Actions
  // ==========================================================================

  describe('Resource Selection', () => {
    it('should toggle resource selection (add)', () => {
      useCollectionsStore.getState().toggleResourceSelection('res_1');

      const { selectedResourceIds } = useCollectionsStore.getState();
      expect(selectedResourceIds.has('res_1')).toBe(true);
    });

    it('should toggle resource selection (remove)', () => {
      useCollectionsStore.getState().toggleResourceSelection('res_1');
      useCollectionsStore.getState().toggleResourceSelection('res_1');

      const { selectedResourceIds } = useCollectionsStore.getState();
      expect(selectedResourceIds.has('res_1')).toBe(false);
    });

    it('should handle multiple selections', () => {
      useCollectionsStore.getState().toggleResourceSelection('res_1');
      useCollectionsStore.getState().toggleResourceSelection('res_2');
      useCollectionsStore.getState().toggleResourceSelection('res_3');

      const { selectedResourceIds } = useCollectionsStore.getState();
      expect(selectedResourceIds.size).toBe(3);
      expect(selectedResourceIds.has('res_1')).toBe(true);
      expect(selectedResourceIds.has('res_2')).toBe(true);
      expect(selectedResourceIds.has('res_3')).toBe(true);
    });

    it('should clear all selections', () => {
      useCollectionsStore.getState().toggleResourceSelection('res_1');
      useCollectionsStore.getState().toggleResourceSelection('res_2');
      useCollectionsStore.getState().clearSelection();

      const { selectedResourceIds } = useCollectionsStore.getState();
      expect(selectedResourceIds.size).toBe(0);
    });

    it('should select all resources', () => {
      const resourceIds = ['res_1', 'res_2', 'res_3'];
      useCollectionsStore.getState().selectAll(resourceIds);

      const { selectedResourceIds } = useCollectionsStore.getState();
      expect(selectedResourceIds.size).toBe(3);
      resourceIds.forEach(id => {
        expect(selectedResourceIds.has(id)).toBe(true);
      });
    });

    it('should check if resource is selected', () => {
      useCollectionsStore.getState().toggleResourceSelection('res_1');

      expect(useCollectionsStore.getState().isResourceSelected('res_1')).toBe(true);
      expect(useCollectionsStore.getState().isResourceSelected('res_2')).toBe(false);
    });
  });

  // ==========================================================================
  // Batch Mode Actions
  // ==========================================================================

  describe('Batch Mode', () => {
    it('should enable batch mode', () => {
      useCollectionsStore.getState().enableBatchMode();
      expect(useCollectionsStore.getState().batchMode).toBe(true);
    });

    it('should disable batch mode', () => {
      useCollectionsStore.getState().enableBatchMode();
      useCollectionsStore.getState().disableBatchMode();
      expect(useCollectionsStore.getState().batchMode).toBe(false);
    });

    it('should clear selections when disabling batch mode', () => {
      useCollectionsStore.getState().enableBatchMode();
      useCollectionsStore.getState().toggleResourceSelection('res_1');
      useCollectionsStore.getState().disableBatchMode();

      expect(useCollectionsStore.getState().selectedResourceIds.size).toBe(0);
    });

    it('should toggle batch mode', () => {
      useCollectionsStore.getState().toggleBatchMode();
      expect(useCollectionsStore.getState().batchMode).toBe(true);

      useCollectionsStore.getState().toggleBatchMode();
      expect(useCollectionsStore.getState().batchMode).toBe(false);
    });

    it('should clear selections when toggling batch mode off', () => {
      useCollectionsStore.getState().toggleBatchMode();
      useCollectionsStore.getState().toggleResourceSelection('res_1');
      useCollectionsStore.getState().toggleBatchMode();

      expect(useCollectionsStore.getState().selectedResourceIds.size).toBe(0);
    });
  });

  // ==========================================================================
  // Selectors
  // ==========================================================================

  describe('Selectors', () => {
    describe('selectSelectedCount', () => {
      it('should return number of selected resources', () => {
        useCollectionsStore.getState().toggleResourceSelection('res_1');
        useCollectionsStore.getState().toggleResourceSelection('res_2');

        const count = selectSelectedCount(useCollectionsStore.getState());
        expect(count).toBe(2);
      });

      it('should return 0 when no selections', () => {
        const count = selectSelectedCount(useCollectionsStore.getState());
        expect(count).toBe(0);
      });
    });

    describe('selectSelectedResourceIdsArray', () => {
      it('should convert Set to Array', () => {
        useCollectionsStore.getState().toggleResourceSelection('res_1');
        useCollectionsStore.getState().toggleResourceSelection('res_2');

        const ids = selectSelectedResourceIdsArray(useCollectionsStore.getState());
        expect(Array.isArray(ids)).toBe(true);
        expect(ids).toHaveLength(2);
        expect(ids).toContain('res_1');
        expect(ids).toContain('res_2');
      });
    });

    describe('selectHasSelection', () => {
      it('should return true when resources are selected', () => {
        useCollectionsStore.getState().toggleResourceSelection('res_1');
        expect(selectHasSelection(useCollectionsStore.getState())).toBe(true);
      });

      it('should return false when no selections', () => {
        expect(selectHasSelection(useCollectionsStore.getState())).toBe(false);
      });
    });

    describe('selectCollectionById', () => {
      it('should find collection by ID', () => {
        const collection = createMockCollection({ id: 'col_1', name: 'Test' });
        useCollectionsStore.getState().setCollections([collection]);

        const getCollection = selectCollectionById(useCollectionsStore.getState());
        const found = getCollection('col_1');

        expect(found).toEqual(collection);
      });

      it('should return undefined for non-existent ID', () => {
        const getCollection = selectCollectionById(useCollectionsStore.getState());
        const found = getCollection('col_999');

        expect(found).toBeUndefined();
      });
    });

    describe('selectCollectionsSortedByName', () => {
      it('should sort collections alphabetically', () => {
        const collections = [
          createMockCollection({ name: 'Zebra' }),
          createMockCollection({ name: 'Apple' }),
          createMockCollection({ name: 'Mango' })
        ];
        useCollectionsStore.getState().setCollections(collections);

        const sorted = selectCollectionsSortedByName(useCollectionsStore.getState());
        expect(sorted[0].name).toBe('Apple');
        expect(sorted[1].name).toBe('Mango');
        expect(sorted[2].name).toBe('Zebra');
      });
    });

    describe('selectCollectionsByResourceCount', () => {
      it('should sort by resource count descending', () => {
        const collections = [
          createMockCollection({ resource_count: 5 }),
          createMockCollection({ resource_count: 15 }),
          createMockCollection({ resource_count: 10 })
        ];
        useCollectionsStore.getState().setCollections(collections);

        const sorted = selectCollectionsByResourceCount(useCollectionsStore.getState());
        expect(sorted[0].resource_count).toBe(15);
        expect(sorted[1].resource_count).toBe(10);
        expect(sorted[2].resource_count).toBe(5);
      });
    });

    describe('selectCollectionsByDate', () => {
      it('should sort by creation date descending', () => {
        const collections = [
          createMockCollection({ created_at: '2024-01-01T00:00:00Z' }),
          createMockCollection({ created_at: '2024-01-03T00:00:00Z' }),
          createMockCollection({ created_at: '2024-01-02T00:00:00Z' })
        ];
        useCollectionsStore.getState().setCollections(collections);

        const sorted = selectCollectionsByDate(useCollectionsStore.getState());
        expect(sorted[0].created_at).toBe('2024-01-03T00:00:00Z');
        expect(sorted[1].created_at).toBe('2024-01-02T00:00:00Z');
        expect(sorted[2].created_at).toBe('2024-01-01T00:00:00Z');
      });
    });

    describe('selectPublicCollections', () => {
      it('should filter public collections', () => {
        const collections = [
          createMockCollection({ is_public: true }),
          createMockCollection({ is_public: false }),
          createMockCollection({ is_public: true })
        ];
        useCollectionsStore.getState().setCollections(collections);

        const publicCollections = selectPublicCollections(useCollectionsStore.getState());
        expect(publicCollections).toHaveLength(2);
        expect(publicCollections.every(c => c.is_public)).toBe(true);
      });
    });

    describe('selectPrivateCollections', () => {
      it('should filter private collections', () => {
        const collections = [
          createMockCollection({ is_public: true }),
          createMockCollection({ is_public: false }),
          createMockCollection({ is_public: false })
        ];
        useCollectionsStore.getState().setCollections(collections);

        const privateCollections = selectPrivateCollections(useCollectionsStore.getState());
        expect(privateCollections).toHaveLength(2);
        expect(privateCollections.every(c => !c.is_public)).toBe(true);
      });
    });

    describe('selectTotalResourceCount', () => {
      it('should sum resource counts across all collections', () => {
        const collections = [
          createMockCollection({ resource_count: 5 }),
          createMockCollection({ resource_count: 10 }),
          createMockCollection({ resource_count: 15 })
        ];
        useCollectionsStore.getState().setCollections(collections);

        const total = selectTotalResourceCount(useCollectionsStore.getState());
        expect(total).toBe(30);
      });

      it('should return 0 for empty collections', () => {
        const total = selectTotalResourceCount(useCollectionsStore.getState());
        expect(total).toBe(0);
      });
    });
  });
});
