/**
 * Resource Store
 * 
 * Zustand store for resource state management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { resourcesAPI } from '@/services/api';
import type { Resource, ResourceListParams, ResourceUpdate, ReadStatus } from '@/types/resource';
import type { ViewMode, APIListResponse } from '@/types/api';

interface ResourceFilters {
  search?: string;
  read_status?: ReadStatus;
  quality_min?: number;
  quality_max?: number;
  tags?: string[];
  sort_by?: 'created_at' | 'updated_at' | 'quality_score' | 'title';
  sort_order?: 'asc' | 'desc';
}

interface ResourceStore {
  // State
  resources: Resource[];
  selectedResource: Resource | null;
  viewMode: ViewMode;
  filters: ResourceFilters;
  isLoading: boolean;
  error: string | null;
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };

  // Actions
  fetchResources: (params?: ResourceListParams) => Promise<void>;
  selectResource: (id: string) => Promise<void>;
  setViewMode: (mode: ViewMode) => void;
  updateFilters: (filters: Partial<ResourceFilters>) => void;
  clearFilters: () => void;
  updateResourceStatus: (id: string, status: ReadStatus) => Promise<void>;
  archiveResource: (id: string) => Promise<void>;
  updateResource: (id: string, data: ResourceUpdate) => Promise<void>;
  deleteResource: (id: string) => Promise<void>;
  setPage: (page: number) => void;
  reset: () => void;
}

const initialState = {
  resources: [],
  selectedResource: null,
  viewMode: 'grid' as ViewMode,
  filters: {},
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    pages: 0,
  },
};

export const useResourceStore = create<ResourceStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      fetchResources: async (params?: ResourceListParams) => {
        set({ isLoading: true, error: null });

        try {
          const { filters, pagination } = get();
          const response: APIListResponse<Resource> = await resourcesAPI.list({
            page: pagination.page,
            limit: pagination.limit,
            ...filters,
            ...params,
          });

          set({
            resources: response.data,
            pagination: {
              page: response.meta.page,
              limit: response.meta.limit,
              total: response.meta.total,
              pages: response.meta.pages,
            },
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to fetch resources',
            isLoading: false,
          });
        }
      },

      selectResource: async (id: string) => {
        set({ isLoading: true, error: null });

        try {
          const resource = await resourcesAPI.get(id);
          set({ selectedResource: resource, isLoading: false });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to fetch resource',
            isLoading: false,
          });
        }
      },

      setViewMode: (mode: ViewMode) => {
        set({ viewMode: mode });
      },

      updateFilters: (newFilters: Partial<ResourceFilters>) => {
        const { filters } = get();
        set({
          filters: { ...filters, ...newFilters },
          pagination: { ...get().pagination, page: 1 }, // Reset to first page
        });
        // Automatically fetch with new filters
        get().fetchResources();
      },

      clearFilters: () => {
        set({
          filters: {},
          pagination: { ...get().pagination, page: 1 },
        });
        get().fetchResources();
      },

      updateResourceStatus: async (id: string, status: ReadStatus) => {
        const { resources, selectedResource } = get();

        // Optimistic update
        const updatedResources = resources.map((r) =>
          r.id === id ? { ...r, read_status: status } : r
        );
        set({ resources: updatedResources });

        if (selectedResource?.id === id) {
          set({ selectedResource: { ...selectedResource, read_status: status } });
        }

        try {
          const updated = await resourcesAPI.updateStatus(id, status);

          // Update with server response
          const finalResources = resources.map((r) =>
            r.id === id ? updated : r
          );
          set({ resources: finalResources });

          if (selectedResource?.id === id) {
            set({ selectedResource: updated });
          }
        } catch (error: any) {
          // Rollback on error
          set({ resources, selectedResource });
          set({ error: error.message || 'Failed to update resource status' });
          throw error;
        }
      },

      archiveResource: async (id: string) => {
        const { resources, selectedResource } = get();

        // Optimistic update
        const updatedResources = resources.map((r) =>
          r.id === id ? { ...r, read_status: 'archived' as ReadStatus } : r
        );
        set({ resources: updatedResources });

        try {
          const updated = await resourcesAPI.archive(id);

          // Update with server response
          const finalResources = resources.map((r) =>
            r.id === id ? updated : r
          );
          set({ resources: finalResources });

          if (selectedResource?.id === id) {
            set({ selectedResource: updated });
          }
        } catch (error: any) {
          // Rollback on error
          set({ resources, selectedResource });
          set({ error: error.message || 'Failed to archive resource' });
          throw error;
        }
      },

      updateResource: async (id: string, data: ResourceUpdate) => {
        const { resources, selectedResource } = get();

        try {
          const updated = await resourcesAPI.update(id, data);

          const updatedResources = resources.map((r) =>
            r.id === id ? updated : r
          );
          set({ resources: updatedResources });

          if (selectedResource?.id === id) {
            set({ selectedResource: updated });
          }
        } catch (error: any) {
          set({ error: error.message || 'Failed to update resource' });
          throw error;
        }
      },

      deleteResource: async (id: string) => {
        const { resources, selectedResource } = get();

        try {
          await resourcesAPI.delete(id);

          const updatedResources = resources.filter((r) => r.id !== id);
          set({ resources: updatedResources });

          if (selectedResource?.id === id) {
            set({ selectedResource: null });
          }
        } catch (error: any) {
          set({ error: error.message || 'Failed to delete resource' });
          throw error;
        }
      },

      setPage: (page: number) => {
        set({ pagination: { ...get().pagination, page } });
        get().fetchResources();
      },

      reset: () => {
        set(initialState);
      },
    }),
    {
      name: 'resource-store',
      partialize: (state) => ({
        viewMode: state.viewMode,
        filters: state.filters,
        pagination: {
          ...state.pagination,
          page: 1, // Reset page on reload
        },
      }),
    }
  )
);
