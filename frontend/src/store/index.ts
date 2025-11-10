// Neo Alexandria 2.0 Frontend - Global State Management
// Using Zustand for lightweight, type-safe state management

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// User Preferences Interface
export interface UserPreferences {
  subjects: string[];
  languages: string[];
  notifications: {
    ingestion_complete: boolean;
    quality_updates: boolean;
    recommendations: boolean;
  };
  display: {
    theme: 'dark' | 'light';
    defaultView: 'grid' | 'list';
    itemsPerPage: number;
  };
}

// Default preferences
const defaultPreferences: UserPreferences = {
  subjects: [],
  languages: ['en'],
  notifications: {
    ingestion_complete: true,
    quality_updates: true,
    recommendations: true,
  },
  display: {
    theme: 'dark',
    defaultView: 'grid',
    itemsPerPage: 25,
  },
};

// Notification Interface
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
}

// Application State Interface
export interface AppState {
  // UI State
  isSidebarOpen: boolean;
  theme: 'dark' | 'light';
  
  // User State
  userId: string | null;
  preferences: UserPreferences;
  
  // Selection State
  selectedResources: string[];
  
  // Notifications
  notifications: Notification[];
  
  // Actions
  toggleSidebar: () => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setUserId: (id: string | null) => void;
  updatePreferences: (prefs: Partial<UserPreferences>) => void;
  toggleResourceSelection: (id: string) => void;
  clearSelection: () => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  addProcessingResource: (resource: any) => void;
  updateProcessingResource: (id: string, updates: any) => void;
  addLibraryResource: (resource: any) => void;
  updateLibraryResource: (id: string, updates: any) => void;
  removeLibraryResource: (id: string) => void;
  setLibraryFilters: (filters: any) => void;
  setSearchQuery: (query: string) => void;
  setSearchFilters: (filters: any) => void;
  setSearchLoading: (loading: boolean) => void;
  setSearchError: (error: string | null) => void;
  setSearchResults: (results: any[]) => void;
  clearSearchResults: () => void;
  search: any;
}

// Main store with persistence
export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        isSidebarOpen: true,
        theme: 'dark',
        userId: null,
        preferences: defaultPreferences,
        selectedResources: [],
        notifications: [],
        
        // Actions
        toggleSidebar: () => set((state) => ({ 
          isSidebarOpen: !state.isSidebarOpen 
        })),
        
        setTheme: (theme) => set({ theme }),
        
        setUserId: (userId) => set({ userId }),
        
        updatePreferences: (prefs) => set((state) => ({
          preferences: { 
            ...state.preferences, 
            ...prefs,
            notifications: prefs.notifications 
              ? { ...state.preferences.notifications, ...prefs.notifications }
              : state.preferences.notifications,
            display: prefs.display
              ? { ...state.preferences.display, ...prefs.display }
              : state.preferences.display,
          }
        })),
        
        toggleResourceSelection: (id) => set((state) => ({
          selectedResources: state.selectedResources.includes(id)
            ? state.selectedResources.filter(rid => rid !== id)
            : [...state.selectedResources, id]
        })),
        
        clearSelection: () => set({ selectedResources: [] }),
        
        addNotification: (notification) => set((state) => ({
          notifications: [
            ...state.notifications,
            {
              ...notification,
              id: Math.random().toString(36).substr(2, 9),
              timestamp: new Date(),
            },
          ],
        })),
        
        removeNotification: (id) => set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),
        
        // Stub implementations for resource management
        addProcessingResource: () => {},
        updateProcessingResource: () => {},
        addLibraryResource: () => {},
        updateLibraryResource: () => {},
        removeLibraryResource: () => {},
        setLibraryFilters: () => {},
        setSearchQuery: () => {},
        setSearchFilters: () => {},
        setSearchLoading: () => {},
        setSearchError: () => {},
        setSearchResults: () => {},
        clearSearchResults: () => {},
        search: {},
      }),
      {
        name: 'neo-alexandria-storage',
        partialize: (state) => ({
          theme: state.theme,
          userId: state.userId,
          preferences: state.preferences,
          isSidebarOpen: state.isSidebarOpen,
        }),
      }
    ),
    { name: 'neo-alexandria' }
  )
);

// Convenience selectors
export const useSelectedResources = () => useAppStore((state) => state.selectedResources);
export const useNotifications = () => useAppStore((state) => state.notifications);
export const useProcessingResources = () => useAppStore((state) => []);
export const useLibraryFilters = () => ({
  resourceTypes: [],
  subjects: [],
  languages: [],
  qualityRange: [0, 100] as [number, number],
  dateRange: null as [Date, Date] | null,
  limit: 25,
  sort_by: 'updated_at' as const,
  sort_dir: 'desc' as const,
});

