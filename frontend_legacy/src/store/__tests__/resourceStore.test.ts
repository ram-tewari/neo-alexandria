/**
 * Resource Store Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useResourceStore } from '../resourceStore';
import { resourcesAPI } from '@/services/api';

// Mock the API
vi.mock('@/services/api', () => ({
  resourcesAPI: {
    list: vi.fn(),
    get: vi.fn(),
    updateStatus: vi.fn(),
    archive: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('ResourceStore', () => {
  beforeEach(() => {
    // Reset store
    useResourceStore.getState().reset();
    vi.clearAllMocks();
  });

  describe('fetchResources', () => {
    it('should fetch resources successfully', async () => {
      const mockResources = [
        { id: '1', title: 'Resource 1', quality_score: 0.8 },
        { id: '2', title: 'Resource 2', quality_score: 0.9 },
      ];

      vi.mocked(resourcesAPI.list).mockResolvedValueOnce({
        data: mockResources,
        meta: { page: 1, limit: 20, total: 2, pages: 1 },
      } as any);

      await useResourceStore.getState().fetchResources();

      const state = useResourceStore.getState();
      expect(state.resources).toEqual(mockResources);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle fetch errors', async () => {
      vi.mocked(resourcesAPI.list).mockRejectedValueOnce(new Error('Network error'));

      await useResourceStore.getState().fetchResources();

      const state = useResourceStore.getState();
      expect(state.error).toBeTruthy();
      expect(state.isLoading).toBe(false);
    });
  });

  describe('selectResource', () => {
    it('should select a resource', async () => {
      const mockResource = { id: '1', title: 'Resource 1', quality_score: 0.8 };

      vi.mocked(resourcesAPI.get).mockResolvedValueOnce(mockResource as any);

      await useResourceStore.getState().selectResource('1');

      const state = useResourceStore.getState();
      expect(state.selectedResource).toEqual(mockResource);
    });
  });

  describe('setViewMode', () => {
    it('should update view mode', () => {
      useResourceStore.getState().setViewMode('list');
      expect(useResourceStore.getState().viewMode).toBe('list');

      useResourceStore.getState().setViewMode('grid');
      expect(useResourceStore.getState().viewMode).toBe('grid');
    });
  });

  describe('updateFilters', () => {
    it('should update filters', () => {
      useResourceStore.getState().updateFilters({ search: 'test' });
      expect(useResourceStore.getState().filters.search).toBe('test');
    });

    it('should reset page when updating filters', () => {
      useResourceStore.setState({ pagination: { page: 3, limit: 20, total: 100, pages: 5 } });
      useResourceStore.getState().updateFilters({ search: 'test' });
      expect(useResourceStore.getState().pagination.page).toBe(1);
    });
  });

  describe('updateResourceStatus', () => {
    it('should update resource status optimistically', async () => {
      const mockResource = { id: '1', title: 'Resource 1', read_status: 'unread' as const };
      useResourceStore.setState({ resources: [mockResource as any] });

      vi.mocked(resourcesAPI.updateStatus).mockResolvedValueOnce({
        ...mockResource,
        read_status: 'completed',
      } as any);

      await useResourceStore.getState().updateResourceStatus('1', 'completed');

      const state = useResourceStore.getState();
      expect(state.resources[0].read_status).toBe('completed');
    });

    it('should rollback on error', async () => {
      const mockResource = { id: '1', title: 'Resource 1', read_status: 'unread' as const };
      useResourceStore.setState({ resources: [mockResource as any] });

      vi.mocked(resourcesAPI.updateStatus).mockRejectedValueOnce(new Error('Failed'));

      await expect(
        useResourceStore.getState().updateResourceStatus('1', 'completed')
      ).rejects.toThrow();

      const state = useResourceStore.getState();
      expect(state.resources[0].read_status).toBe('unread');
    });
  });

  describe('archiveResource', () => {
    it('should archive resource', async () => {
      const mockResource = { id: '1', title: 'Resource 1', read_status: 'unread' as const };
      useResourceStore.setState({ resources: [mockResource as any] });

      vi.mocked(resourcesAPI.archive).mockResolvedValueOnce({
        ...mockResource,
        read_status: 'archived',
      } as any);

      await useResourceStore.getState().archiveResource('1');

      const state = useResourceStore.getState();
      expect(state.resources[0].read_status).toBe('archived');
    });
  });

  describe('deleteResource', () => {
    it('should delete resource', async () => {
      const mockResources = [
        { id: '1', title: 'Resource 1' },
        { id: '2', title: 'Resource 2' },
      ];
      useResourceStore.setState({ resources: mockResources as any });

      vi.mocked(resourcesAPI.delete).mockResolvedValueOnce(undefined as any);

      await useResourceStore.getState().deleteResource('1');

      const state = useResourceStore.getState();
      expect(state.resources).toHaveLength(1);
      expect(state.resources[0].id).toBe('2');
    });
  });

  describe('setPage', () => {
    it('should update page', () => {
      useResourceStore.getState().setPage(2);
      expect(useResourceStore.getState().pagination.page).toBe(2);
    });
  });
});
