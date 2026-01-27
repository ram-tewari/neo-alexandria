/**
 * Library Store
 * 
 * Zustand store for managing library state including resources, filters, and sorting.
 * Provides actions for CRUD operations and filter management.
 * 
 * Phase: 3 Living Library
 * Epic: 2 State Management
 * Task: 2.1
 */

import { create } from 'zustand';
import type { Resource } from '@/types/library';

// ============================================================================
// State Interface
// ============================================================================

/**
 * Library store state and actions
 */
interface LibraryState {
  // ========================================================================
  // State
  // ========================================================================
  
  /** All resources in the library */
  resources: Resource[];
  
  /** Currently selected resource for detail view */
  selectedResource: Resource | null;
  
  /** Active filters */
  filters: {
    /** Filter by resource type (pdf, html, code, etc.) */
    type?: string;
    /** Minimum quality score (0-1) */
    qualityMin?: number;
    /** Maximum quality score (0-1) */
    qualityMax?: number;
    /** Search query for title/content */
    search?: string;
    /** Filter by date range */
    dateFrom?: string;
    dateTo?: string;
  };
  
  /** Sort field */
  sortBy: 'date' | 'title' | 'quality';
  
  /** Sort order */
  sortOrder: 'asc' | 'desc';
  
  // ========================================================================
  // Actions
  // ========================================================================
  
  /**
   * Set all resources (replaces existing)
   * Used when fetching fresh data from API
   */
  setResources: (resources: Resource[]) => void;
  
  /**
   * Add a single resource to the list
   * Used for optimistic updates after upload
   */
  addResource: (resource: Resource) => void;
  
  /**
   * Update a resource by ID
   * Used for optimistic updates after edit
   */
  updateResource: (id: string, updates: Partial<Resource>) => void;
  
  /**
   * Remove a resource by ID
   * Used for optimistic updates after delete
   */
  removeResource: (id: string) => void;
  
  /**
   * Select a resource for detail view
   * Pass null to deselect
   */
  selectResource: (resource: Resource | null) => void;
  
  /**
   * Update filters (partial update)
   * Merges with existing filters
   */
  setFilters: (filters: Partial<LibraryState['filters']>) => void;
  
  /**
   * Set sorting configuration
   */
  setSorting: (sortBy: LibraryState['sortBy'], sortOrder: LibraryState['sortOrder']) => void;
  
  /**
   * Clear all filters
   * Resets to default empty state
   */
  clearFilters: () => void;
}

// ============================================================================
// Store Implementation
// ============================================================================

/**
 * Library store instance
 * 
 * @example
 * ```typescript
 * // In a component
 * const { resources, filters, setFilters } = useLibraryStore();
 * 
 * // Update filters
 * setFilters({ type: 'pdf', qualityMin: 0.7 });
 * 
 * // Clear filters
 * clearFilters();
 * ```
 */
export const useLibraryStore = create<LibraryState>((set) => ({
  // Initial state
  resources: [],
  selectedResource: null,
  filters: {},
  sortBy: 'date',
  sortOrder: 'desc',
  
  // Actions
  setResources: (resources) => set({ resources }),
  
  addResource: (resource) => set((state) => ({
    resources: [resource, ...state.resources]
  })),
  
  updateResource: (id, updates) => set((state) => ({
    resources: state.resources.map((r) =>
      r.id === id ? { ...r, ...updates } : r
    ),
    // Update selected resource if it's the one being updated
    selectedResource: state.selectedResource?.id === id
      ? { ...state.selectedResource, ...updates }
      : state.selectedResource
  })),
  
  removeResource: (id) => set((state) => ({
    resources: state.resources.filter((r) => r.id !== id),
    // Clear selection if the removed resource was selected
    selectedResource: state.selectedResource?.id === id
      ? null
      : state.selectedResource
  })),
  
  selectResource: (resource) => set({ selectedResource: resource }),
  
  setFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters }
  })),
  
  setSorting: (sortBy, sortOrder) => set({ sortBy, sortOrder }),
  
  clearFilters: () => set({ filters: {} })
}));

// ============================================================================
// Selectors
// ============================================================================

/**
 * Selector: Get filtered and sorted resources
 * 
 * Applies current filters and sorting to the resource list.
 * Use this instead of accessing resources directly for consistent filtering.
 * 
 * @example
 * ```typescript
 * const filteredResources = useLibraryStore(selectFilteredResources);
 * ```
 */
export const selectFilteredResources = (state: LibraryState): Resource[] => {
  let filtered = [...state.resources];
  
  // Apply type filter
  if (state.filters.type) {
    filtered = filtered.filter((r) => r.type === state.filters.type);
  }
  
  // Apply quality range filter
  if (state.filters.qualityMin !== undefined) {
    filtered = filtered.filter((r) => 
      (r.quality_score ?? 0) >= state.filters.qualityMin!
    );
  }
  
  if (state.filters.qualityMax !== undefined) {
    filtered = filtered.filter((r) => 
      (r.quality_score ?? 1) <= state.filters.qualityMax!
    );
  }
  
  // Apply search filter
  if (state.filters.search) {
    const searchLower = state.filters.search.toLowerCase();
    filtered = filtered.filter((r) =>
      r.title?.toLowerCase().includes(searchLower) ||
      r.description?.toLowerCase().includes(searchLower) ||
      r.content?.toLowerCase().includes(searchLower)
    );
  }
  
  // Apply date range filter
  if (state.filters.dateFrom) {
    filtered = filtered.filter((r) => 
      r.created_at >= state.filters.dateFrom!
    );
  }
  
  if (state.filters.dateTo) {
    filtered = filtered.filter((r) => 
      r.created_at <= state.filters.dateTo!
    );
  }
  
  // Apply sorting
  filtered.sort((a, b) => {
    let comparison = 0;
    
    switch (state.sortBy) {
      case 'date':
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        break;
      case 'title':
        comparison = (a.title || '').localeCompare(b.title || '');
        break;
      case 'quality':
        comparison = (a.quality_score ?? 0) - (b.quality_score ?? 0);
        break;
    }
    
    return state.sortOrder === 'asc' ? comparison : -comparison;
  });
  
  return filtered;
};

/**
 * Selector: Check if any filters are active
 * 
 * @example
 * ```typescript
 * const hasFilters = useLibraryStore(selectHasActiveFilters);
 * if (hasFilters) {
 *   // Show "Clear Filters" button
 * }
 * ```
 */
export const selectHasActiveFilters = (state: LibraryState): boolean => {
  return Object.keys(state.filters).length > 0;
};

/**
 * Selector: Get resource count by type
 * 
 * @example
 * ```typescript
 * const counts = useLibraryStore(selectResourceCountsByType);
 * console.log(`PDFs: ${counts.pdf}, HTML: ${counts.html}`);
 * ```
 */
export const selectResourceCountsByType = (state: LibraryState): Record<string, number> => {
  return state.resources.reduce((acc, resource) => {
    const type = resource.type || 'unknown';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
};
