/**
 * Library Store Tests
 * 
 * Tests for the library Zustand store including state management,
 * actions, and selectors.
 * 
 * Phase: 3 Living Library
 * Epic: 2 State Management
 * Task: 2.4
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { 
  useLibraryStore,
  selectFilteredResources,
  selectHasActiveFilters,
  selectResourceCountsByType
} from '../library';
import type { Resource } from '@/types/library';

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Create a mock resource for testing
 */
const createMockResource = (overrides?: Partial<Resource>): Resource => ({
  id: `res_${Math.random().toString(36).substr(2, 9)}`,
  title: 'Test Resource',
  type: 'pdf',
  url: 'https://example.com/test.pdf',
  quality_score: 0.8,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides
});

/**
 * Reset store to initial state before each test
 */
const resetStore = () => {
  useLibraryStore.setState({
    resources: [],
    selectedResource: null,
    filters: {},
    sortBy: 'date',
    sortOrder: 'desc'
  });
};

// ============================================================================
// Tests
// ============================================================================

describe('Library Store', () => {
  beforeEach(() => {
    resetStore();
  });

  // ==========================================================================
  // Initial State
  // ==========================================================================

  describe('Initial State', () => {
    it('should have empty resources array', () => {
      const { resources } = useLibraryStore.getState();
      expect(resources).toEqual([]);
    });

    it('should have no selected resource', () => {
      const { selectedResource } = useLibraryStore.getState();
      expect(selectedResource).toBeNull();
    });

    it('should have empty filters', () => {
      const { filters } = useLibraryStore.getState();
      expect(filters).toEqual({});
    });

    it('should have default sorting (date desc)', () => {
      const { sortBy, sortOrder } = useLibraryStore.getState();
      expect(sortBy).toBe('date');
      expect(sortOrder).toBe('desc');
    });
  });

  // ==========================================================================
  // setResources Action
  // ==========================================================================

  describe('setResources', () => {
    it('should set resources', () => {
      const resources = [
        createMockResource({ id: 'res_1' }),
        createMockResource({ id: 'res_2' })
      ];

      useLibraryStore.getState().setResources(resources);

      expect(useLibraryStore.getState().resources).toEqual(resources);
    });

    it('should replace existing resources', () => {
      const initial = [createMockResource({ id: 'res_1' })];
      const updated = [createMockResource({ id: 'res_2' })];

      useLibraryStore.getState().setResources(initial);
      useLibraryStore.getState().setResources(updated);

      expect(useLibraryStore.getState().resources).toEqual(updated);
    });
  });

  // ==========================================================================
  // addResource Action
  // ==========================================================================

  describe('addResource', () => {
    it('should add resource to beginning of list', () => {
      const existing = createMockResource({ id: 'res_1' });
      const newResource = createMockResource({ id: 'res_2' });

      useLibraryStore.getState().setResources([existing]);
      useLibraryStore.getState().addResource(newResource);

      const { resources } = useLibraryStore.getState();
      expect(resources).toHaveLength(2);
      expect(resources[0]).toEqual(newResource);
      expect(resources[1]).toEqual(existing);
    });

    it('should work with empty list', () => {
      const resource = createMockResource();
      useLibraryStore.getState().addResource(resource);

      expect(useLibraryStore.getState().resources).toEqual([resource]);
    });
  });

  // ==========================================================================
  // updateResource Action
  // ==========================================================================

  describe('updateResource', () => {
    it('should update resource by ID', () => {
      const resource = createMockResource({ id: 'res_1', title: 'Original' });
      useLibraryStore.getState().setResources([resource]);

      useLibraryStore.getState().updateResource('res_1', { title: 'Updated' });

      const updated = useLibraryStore.getState().resources[0];
      expect(updated.title).toBe('Updated');
      expect(updated.id).toBe('res_1');
    });

    it('should not affect other resources', () => {
      const resources = [
        createMockResource({ id: 'res_1', title: 'First' }),
        createMockResource({ id: 'res_2', title: 'Second' })
      ];
      useLibraryStore.getState().setResources(resources);

      useLibraryStore.getState().updateResource('res_1', { title: 'Updated' });

      const { resources: updated } = useLibraryStore.getState();
      expect(updated[0].title).toBe('Updated');
      expect(updated[1].title).toBe('Second');
    });

    it('should update selected resource if it matches', () => {
      const resource = createMockResource({ id: 'res_1', title: 'Original' });
      useLibraryStore.getState().setResources([resource]);
      useLibraryStore.getState().selectResource(resource);

      useLibraryStore.getState().updateResource('res_1', { title: 'Updated' });

      const { selectedResource } = useLibraryStore.getState();
      expect(selectedResource?.title).toBe('Updated');
    });

    it('should not update selected resource if ID does not match', () => {
      const resource1 = createMockResource({ id: 'res_1', title: 'First' });
      const resource2 = createMockResource({ id: 'res_2', title: 'Second' });
      useLibraryStore.getState().setResources([resource1, resource2]);
      useLibraryStore.getState().selectResource(resource1);

      useLibraryStore.getState().updateResource('res_2', { title: 'Updated' });

      const { selectedResource } = useLibraryStore.getState();
      expect(selectedResource?.title).toBe('First');
    });
  });

  // ==========================================================================
  // removeResource Action
  // ==========================================================================

  describe('removeResource', () => {
    it('should remove resource by ID', () => {
      const resources = [
        createMockResource({ id: 'res_1' }),
        createMockResource({ id: 'res_2' })
      ];
      useLibraryStore.getState().setResources(resources);

      useLibraryStore.getState().removeResource('res_1');

      const { resources: updated } = useLibraryStore.getState();
      expect(updated).toHaveLength(1);
      expect(updated[0].id).toBe('res_2');
    });

    it('should clear selected resource if it matches removed ID', () => {
      const resource = createMockResource({ id: 'res_1' });
      useLibraryStore.getState().setResources([resource]);
      useLibraryStore.getState().selectResource(resource);

      useLibraryStore.getState().removeResource('res_1');

      expect(useLibraryStore.getState().selectedResource).toBeNull();
    });

    it('should not clear selected resource if ID does not match', () => {
      const resource1 = createMockResource({ id: 'res_1' });
      const resource2 = createMockResource({ id: 'res_2' });
      useLibraryStore.getState().setResources([resource1, resource2]);
      useLibraryStore.getState().selectResource(resource1);

      useLibraryStore.getState().removeResource('res_2');

      expect(useLibraryStore.getState().selectedResource).toEqual(resource1);
    });
  });

  // ==========================================================================
  // selectResource Action
  // ==========================================================================

  describe('selectResource', () => {
    it('should select a resource', () => {
      const resource = createMockResource();
      useLibraryStore.getState().selectResource(resource);

      expect(useLibraryStore.getState().selectedResource).toEqual(resource);
    });

    it('should deselect when passed null', () => {
      const resource = createMockResource();
      useLibraryStore.getState().selectResource(resource);
      useLibraryStore.getState().selectResource(null);

      expect(useLibraryStore.getState().selectedResource).toBeNull();
    });
  });

  // ==========================================================================
  // Filter Actions
  // ==========================================================================

  describe('Filter Actions', () => {
    it('should set filters', () => {
      useLibraryStore.getState().setFilters({ type: 'pdf', qualityMin: 0.7 });

      const { filters } = useLibraryStore.getState();
      expect(filters.type).toBe('pdf');
      expect(filters.qualityMin).toBe(0.7);
    });

    it('should merge with existing filters', () => {
      useLibraryStore.getState().setFilters({ type: 'pdf' });
      useLibraryStore.getState().setFilters({ qualityMin: 0.7 });

      const { filters } = useLibraryStore.getState();
      expect(filters.type).toBe('pdf');
      expect(filters.qualityMin).toBe(0.7);
    });

    it('should clear all filters', () => {
      useLibraryStore.getState().setFilters({ type: 'pdf', qualityMin: 0.7 });
      useLibraryStore.getState().clearFilters();

      expect(useLibraryStore.getState().filters).toEqual({});
    });
  });

  // ==========================================================================
  // Sorting Actions
  // ==========================================================================

  describe('Sorting Actions', () => {
    it('should set sorting', () => {
      useLibraryStore.getState().setSorting('title', 'asc');

      const { sortBy, sortOrder } = useLibraryStore.getState();
      expect(sortBy).toBe('title');
      expect(sortOrder).toBe('asc');
    });
  });

  // ==========================================================================
  // Selectors
  // ==========================================================================

  describe('Selectors', () => {
    describe('selectFilteredResources', () => {
      it('should return all resources when no filters', () => {
        const resources = [
          createMockResource({ id: 'res_1' }),
          createMockResource({ id: 'res_2' })
        ];
        useLibraryStore.getState().setResources(resources);

        const filtered = selectFilteredResources(useLibraryStore.getState());
        expect(filtered).toHaveLength(2);
      });

      it('should filter by type', () => {
        const resources = [
          createMockResource({ id: 'res_1', type: 'pdf' }),
          createMockResource({ id: 'res_2', type: 'html' })
        ];
        useLibraryStore.getState().setResources(resources);
        useLibraryStore.getState().setFilters({ type: 'pdf' });

        const filtered = selectFilteredResources(useLibraryStore.getState());
        expect(filtered).toHaveLength(1);
        expect(filtered[0].type).toBe('pdf');
      });

      it('should filter by quality range', () => {
        const resources = [
          createMockResource({ id: 'res_1', quality_score: 0.5 }),
          createMockResource({ id: 'res_2', quality_score: 0.8 }),
          createMockResource({ id: 'res_3', quality_score: 0.9 })
        ];
        useLibraryStore.getState().setResources(resources);
        useLibraryStore.getState().setFilters({ qualityMin: 0.7, qualityMax: 0.85 });

        const filtered = selectFilteredResources(useLibraryStore.getState());
        expect(filtered).toHaveLength(1);
        expect(filtered[0].id).toBe('res_2');
      });

      it('should filter by search query', () => {
        const resources = [
          createMockResource({ id: 'res_1', title: 'Machine Learning Paper' }),
          createMockResource({ id: 'res_2', title: 'Deep Learning Tutorial' }),
          createMockResource({ id: 'res_3', title: 'Python Guide' })
        ];
        useLibraryStore.getState().setResources(resources);
        useLibraryStore.getState().setFilters({ search: 'learning' });

        const filtered = selectFilteredResources(useLibraryStore.getState());
        expect(filtered).toHaveLength(2);
      });

      it('should sort by date descending', () => {
        const resources = [
          createMockResource({ id: 'res_1', created_at: '2024-01-01T00:00:00Z' }),
          createMockResource({ id: 'res_2', created_at: '2024-01-03T00:00:00Z' }),
          createMockResource({ id: 'res_3', created_at: '2024-01-02T00:00:00Z' })
        ];
        useLibraryStore.getState().setResources(resources);
        useLibraryStore.getState().setSorting('date', 'desc');

        const filtered = selectFilteredResources(useLibraryStore.getState());
        expect(filtered[0].id).toBe('res_2');
        expect(filtered[1].id).toBe('res_3');
        expect(filtered[2].id).toBe('res_1');
      });

      it('should sort by title ascending', () => {
        const resources = [
          createMockResource({ id: 'res_1', title: 'Zebra' }),
          createMockResource({ id: 'res_2', title: 'Apple' }),
          createMockResource({ id: 'res_3', title: 'Mango' })
        ];
        useLibraryStore.getState().setResources(resources);
        useLibraryStore.getState().setSorting('title', 'asc');

        const filtered = selectFilteredResources(useLibraryStore.getState());
        expect(filtered[0].title).toBe('Apple');
        expect(filtered[1].title).toBe('Mango');
        expect(filtered[2].title).toBe('Zebra');
      });

      it('should sort by quality descending', () => {
        const resources = [
          createMockResource({ id: 'res_1', quality_score: 0.5 }),
          createMockResource({ id: 'res_2', quality_score: 0.9 }),
          createMockResource({ id: 'res_3', quality_score: 0.7 })
        ];
        useLibraryStore.getState().setResources(resources);
        useLibraryStore.getState().setSorting('quality', 'desc');

        const filtered = selectFilteredResources(useLibraryStore.getState());
        expect(filtered[0].quality_score).toBe(0.9);
        expect(filtered[1].quality_score).toBe(0.7);
        expect(filtered[2].quality_score).toBe(0.5);
      });
    });

    describe('selectHasActiveFilters', () => {
      it('should return false when no filters', () => {
        const hasFilters = selectHasActiveFilters(useLibraryStore.getState());
        expect(hasFilters).toBe(false);
      });

      it('should return true when filters are set', () => {
        useLibraryStore.getState().setFilters({ type: 'pdf' });
        const hasFilters = selectHasActiveFilters(useLibraryStore.getState());
        expect(hasFilters).toBe(true);
      });
    });

    describe('selectResourceCountsByType', () => {
      it('should count resources by type', () => {
        const resources = [
          createMockResource({ type: 'pdf' }),
          createMockResource({ type: 'pdf' }),
          createMockResource({ type: 'html' }),
          createMockResource({ type: 'code' })
        ];
        useLibraryStore.getState().setResources(resources);

        const counts = selectResourceCountsByType(useLibraryStore.getState());
        expect(counts.pdf).toBe(2);
        expect(counts.html).toBe(1);
        expect(counts.code).toBe(1);
      });

      it('should return empty object for no resources', () => {
        const counts = selectResourceCountsByType(useLibraryStore.getState());
        expect(counts).toEqual({});
      });
    });
  });
});
