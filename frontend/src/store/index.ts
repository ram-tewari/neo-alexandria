// Neo Alexandria 2.0 Frontend - Global State Management
// Using Zustand for lightweight, type-safe state management

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  Resource,
  ProcessingResource,
  SearchState,
  LibraryState,
  ResourceQueryParams,
  SearchResults,
} from '@/types/api';

// Application State Interface
interface AppState {
  // UI State
  isLoading: boolean;
  error: string | null;
  notifications: Notification[];
  
  // Theme and preferences
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;
  
  // Library State
  library: LibraryState;
  
  // Search State
  search: SearchState;
  
  // Processing Resources
  processingResources: ProcessingResource[];
  
  // Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // Theme actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  
  // Library actions
  setLibraryResources: (resources: Resource[], total: number) => void;
  addLibraryResource: (resource: Resource) => void;
  updateLibraryResource: (resourceId: string, updates: Partial<Resource>) => void;
  removeLibraryResource: (resourceId: string) => void;
  setLibraryLoading: (loading: boolean) => void;
  setLibraryError: (error: string | null) => void;
  setLibraryFilters: (filters: ResourceQueryParams) => void;
  toggleResourceSelection: (resourceId: string) => void;
  selectAllResources: () => void;
  clearResourceSelection: () => void;
  
  // Search actions
  setSearchQuery: (query: string) => void;
  setSearchFilters: (filters: SearchState['filters']) => void;
  setSearchResults: (results: SearchResults) => void;
  setSearchLoading: (loading: boolean) => void;
  setSearchError: (error: string | null) => void;
  clearSearchResults: () => void;
  setHybridWeight: (weight: number) => void;
  
  // Processing actions
  addProcessingResource: (resource: ProcessingResource) => void;
  updateProcessingResource: (id: string, updates: Partial<ProcessingResource>) => void;
  removeProcessingResource: (id: string) => void;
  clearProcessingResources: () => void;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Initial states
const initialLibraryState: LibraryState = {
  resources: [],
  total: 0,
  isLoading: false,
  error: null,
  filters: {
    limit: 25,
    offset: 0,
    sort_by: 'updated_at',
    sort_dir: 'desc',
  },
  selectedResources: [],
};

const initialSearchState: SearchState = {
  query: '',
  filters: {},
  results: null,
  isLoading: false,
  error: null,
  hybridWeight: 0.5,
};

// Main store
export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        isLoading: false,
        error: null,
        notifications: [],
        theme: 'system',
        sidebarOpen: true,
        library: initialLibraryState,
        search: initialSearchState,
        processingResources: [],

        // Global actions
        setLoading: (loading) => set({ isLoading: loading }),

        setError: (error) => set({ error }),

        addNotification: (notification) => set((state) => {
          const id = Math.random().toString(36).substring(2);
          return {
            notifications: [...state.notifications, {
              ...notification,
              id,
              duration: notification.duration ?? 5000,
            }]
          };
        }),

        removeNotification: (id) => set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id)
        })),

        clearNotifications: () => set({ notifications: [] }),

        // Theme actions
        setTheme: (theme) => set({ theme }),

        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

        setSidebarOpen: (open) => set({ sidebarOpen: open }),

        // Library actions
        setLibraryResources: (resources, total) => set((state) => ({
          library: { ...state.library, resources, total }
        })),

        addLibraryResource: (resource) => set((state) => ({
          library: {
            ...state.library,
            resources: [resource, ...state.library.resources],
            total: state.library.total + 1
          }
        })),

        updateLibraryResource: (resourceId, updates) => set((state) => ({
          library: {
            ...state.library,
            resources: state.library.resources.map(r => 
              r.id === resourceId ? { ...r, ...updates } : r
            )
          }
        })),

        removeLibraryResource: (resourceId) => set((state) => ({
          library: {
            ...state.library,
            resources: state.library.resources.filter(r => r.id !== resourceId),
            total: Math.max(0, state.library.total - 1),
            selectedResources: state.library.selectedResources.filter(id => id !== resourceId)
          }
        })),

        setLibraryLoading: (loading) => set((state) => ({
          library: { ...state.library, isLoading: loading }
        })),

        setLibraryError: (error) => set((state) => ({
          library: { ...state.library, error }
        })),

        setLibraryFilters: (filters) => set((state) => ({
          library: { ...state.library, filters: { ...state.library.filters, ...filters } }
        })),

        toggleResourceSelection: (resourceId) => set((state) => {
          const selected = state.library.selectedResources;
          const index = selected.indexOf(resourceId);
          const newSelected = index === -1 
            ? [...selected, resourceId]
            : selected.filter(id => id !== resourceId);
          return {
            library: { ...state.library, selectedResources: newSelected }
          };
        }),

        selectAllResources: () => set((state) => ({
          library: { 
            ...state.library, 
            selectedResources: state.library.resources.map(r => r.id) 
          }
        })),

        clearResourceSelection: () => set((state) => ({
          library: { ...state.library, selectedResources: [] }
        })),

        // Search actions
        setSearchQuery: (query) => set((state) => ({
          search: { ...state.search, query }
        })),

        setSearchFilters: (filters) => set((state) => ({
          search: { ...state.search, filters }
        })),

        setSearchResults: (results) => set((state) => ({
          search: { ...state.search, results }
        })),

        setSearchLoading: (loading) => set((state) => ({
          search: { ...state.search, isLoading: loading }
        })),

        setSearchError: (error) => set((state) => ({
          search: { ...state.search, error }
        })),

        clearSearchResults: () => set((state) => ({
          search: { ...state.search, results: null, error: null }
        })),

        setHybridWeight: (weight) => set((state) => ({
          search: { ...state.search, hybridWeight: weight }
        })),

        // Processing actions
        addProcessingResource: (resource) => set((state) => ({
          processingResources: [...state.processingResources, resource]
        })),

        updateProcessingResource: (id, updates) => set((state) => ({
          processingResources: state.processingResources.map(r => 
            r.id === id ? { ...r, ...updates } : r
          )
        })),

        removeProcessingResource: (id) => set((state) => ({
          processingResources: state.processingResources.filter(r => r.id !== id)
        })),

        clearProcessingResources: () => set({ processingResources: [] }),
      }),
      {
        name: 'neo-alexandria-store',
        partialize: (state: AppState) => ({
          // Only persist theme and sidebar preferences
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    ),
    { name: 'neo-alexandria' }
  )
);

// Selectors for common state access patterns
export const useLibraryResources = () => useAppStore(state => state.library.resources);
export const useLibraryLoading = () => useAppStore(state => state.library.isLoading);
export const useLibraryError = () => useAppStore(state => state.library.error);
export const useLibraryFilters = () => useAppStore(state => state.library.filters);
export const useSelectedResources = () => useAppStore(state => state.library.selectedResources);

export const useSearchQuery = () => useAppStore(state => state.search.query);
export const useSearchResults = () => useAppStore(state => state.search.results);
export const useSearchLoading = () => useAppStore(state => state.search.isLoading);
export const useSearchError = () => useAppStore(state => state.search.error);
export const useHybridWeight = () => useAppStore(state => state.search.hybridWeight);

export const useProcessingResources = () => useAppStore(state => state.processingResources);
export const useNotifications = () => useAppStore(state => state.notifications);
export const useTheme = () => useAppStore(state => state.theme);
export const useSidebarOpen = () => useAppStore(state => state.sidebarOpen);

// Action selectors using shallow equality to prevent re-renders
const libraryActionsSelector = (state: AppState) => ({
  setResources: state.setLibraryResources,
  addResource: state.addLibraryResource,
  updateResource: state.updateLibraryResource,
  removeResource: state.removeLibraryResource,
  setLoading: state.setLibraryLoading,
  setError: state.setLibraryError,
  setFilters: state.setLibraryFilters,
  toggleSelection: state.toggleResourceSelection,
  selectAll: state.selectAllResources,
  clearSelection: state.clearResourceSelection,
});

const searchActionsSelector = (state: AppState) => ({
  setQuery: state.setSearchQuery,
  setFilters: state.setSearchFilters,
  setResults: state.setSearchResults,
  setLoading: state.setSearchLoading,
  setError: state.setSearchError,
  clearResults: state.clearSearchResults,
  setHybridWeight: state.setHybridWeight,
});

const processingActionsSelector = (state: AppState) => ({
  addResource: state.addProcessingResource,
  updateResource: state.updateProcessingResource,
  removeResource: state.removeProcessingResource,
  clearResources: state.clearProcessingResources,
});

const globalActionsSelector = (state: AppState) => ({
  setLoading: state.setLoading,
  setError: state.setError,
  addNotification: state.addNotification,
  removeNotification: state.removeNotification,
  clearNotifications: state.clearNotifications,
  setTheme: state.setTheme,
  toggleSidebar: state.toggleSidebar,
  setSidebarOpen: state.setSidebarOpen,
});

export const useLibraryActions = () => useAppStore(libraryActionsSelector);
export const useSearchActions = () => useAppStore(searchActionsSelector);
export const useProcessingActions = () => useAppStore(processingActionsSelector);
export const useGlobalActions = () => useAppStore(globalActionsSelector);

// Computed selectors
export const useHasSelectedResources = () => useAppStore(state => state.library.selectedResources.length > 0);
export const useSelectedResourcesCount = () => useAppStore(state => state.library.selectedResources.length);
export const useHasSearchResults = () => useAppStore(state => state.search.results !== null);
export const useActiveProcessingCount = () => useAppStore(state => 
  state.processingResources.filter(r => r.status === 'pending' || r.status === 'processing').length
);

export type { AppState, Notification };
