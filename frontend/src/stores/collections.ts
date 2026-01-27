/**
 * Collections Store
 * 
 * Zustand store for managing collection state including collection list,
 * selected collection, and multi-select for batch operations.
 * 
 * Phase: 3 Living Library
 * Epic: 2 State Management
 * Task: 2.3
 */

import { create } from 'zustand';
import type { Collection } from '@/types/library';

// ============================================================================
// State Interface
// ============================================================================

/**
 * Collections store state and actions
 */
interface CollectionsState {
  // ========================================================================
  // State
  // ========================================================================
  
  /** All collections */
  collections: Collection[];
  
  /** Currently selected collection for detail view */
  selectedCollection: Collection | null;
  
  /** Set of selected resource IDs for batch operations */
  selectedResourceIds: Set<string>;
  
  /** Whether batch mode is active */
  batchMode: boolean;
  
  // ========================================================================
  // Actions
  // ========================================================================
  
  /**
   * Set all collections (replaces existing)
   * Used when fetching fresh data from API
   */
  setCollections: (collections: Collection[]) => void;
  
  /**
   * Add a single collection to the list
   * Used for optimistic updates after create
   */
  addCollection: (collection: Collection) => void;
  
  /**
   * Update a collection by ID
   * Used for optimistic updates after edit
   */
  updateCollection: (id: string, updates: Partial<Collection>) => void;
  
  /**
   * Remove a collection by ID
   * Used for optimistic updates after delete
   */
  removeCollection: (id: string) => void;
  
  /**
   * Select a collection for detail view
   * Pass null to deselect
   */
  selectCollection: (collection: Collection | null) => void;
  
  /**
   * Toggle resource selection for batch operations
   * Adds if not selected, removes if already selected
   */
  toggleResourceSelection: (resourceId: string) => void;
  
  /**
   * Clear all resource selections
   */
  clearSelection: () => void;
  
  /**
   * Select all resources
   * Used for "Select All" functionality
   */
  selectAll: (resourceIds: string[]) => void;
  
  /**
   * Check if a resource is selected
   */
  isResourceSelected: (resourceId: string) => boolean;
  
  /**
   * Enable batch mode
   */
  enableBatchMode: () => void;
  
  /**
   * Disable batch mode and clear selections
   */
  disableBatchMode: () => void;
  
  /**
   * Toggle batch mode
   */
  toggleBatchMode: () => void;
}

// ============================================================================
// Store Implementation
// ============================================================================

/**
 * Collections store instance
 * 
 * @example
 * ```typescript
 * // In a component
 * const { collections, selectedResourceIds, toggleResourceSelection } = useCollectionsStore();
 * 
 * // Toggle resource selection
 * <Checkbox
 *   checked={selectedResourceIds.has(resource.id)}
 *   onChange={() => toggleResourceSelection(resource.id)}
 * />
 * 
 * // Batch operations
 * if (selectedResourceIds.size > 0) {
 *   // Show batch action toolbar
 * }
 * ```
 */
export const useCollectionsStore = create<CollectionsState>((set, get) => ({
  // Initial state
  collections: [],
  selectedCollection: null,
  selectedResourceIds: new Set(),
  batchMode: false,
  
  // Collection CRUD actions
  setCollections: (collections) => set({ collections }),
  
  addCollection: (collection) => set((state) => ({
    collections: [collection, ...state.collections]
  })),
  
  updateCollection: (id, updates) => set((state) => ({
    collections: state.collections.map((c) =>
      c.id === id ? { ...c, ...updates } : c
    ),
    // Update selected collection if it's the one being updated
    selectedCollection: state.selectedCollection?.id === id
      ? { ...state.selectedCollection, ...updates }
      : state.selectedCollection
  })),
  
  removeCollection: (id) => set((state) => ({
    collections: state.collections.filter((c) => c.id !== id),
    // Clear selection if the removed collection was selected
    selectedCollection: state.selectedCollection?.id === id
      ? null
      : state.selectedCollection
  })),
  
  selectCollection: (collection) => set({ selectedCollection: collection }),
  
  // Resource selection actions
  toggleResourceSelection: (resourceId) => set((state) => {
    const newSelection = new Set(state.selectedResourceIds);
    if (newSelection.has(resourceId)) {
      newSelection.delete(resourceId);
    } else {
      newSelection.add(resourceId);
    }
    return { selectedResourceIds: newSelection };
  }),
  
  clearSelection: () => set({ selectedResourceIds: new Set() }),
  
  selectAll: (resourceIds) => set({ selectedResourceIds: new Set(resourceIds) }),
  
  isResourceSelected: (resourceId) => {
    return get().selectedResourceIds.has(resourceId);
  },
  
  // Batch mode actions
  enableBatchMode: () => set({ batchMode: true }),
  
  disableBatchMode: () => set({
    batchMode: false,
    selectedResourceIds: new Set()
  }),
  
  toggleBatchMode: () => set((state) => ({
    batchMode: !state.batchMode,
    // Clear selections when disabling batch mode
    selectedResourceIds: state.batchMode ? new Set() : state.selectedResourceIds
  }))
}));

// ============================================================================
// Selectors
// ============================================================================

/**
 * Selector: Get number of selected resources
 * 
 * @example
 * ```typescript
 * const selectedCount = useCollectionsStore(selectSelectedCount);
 * console.log(`${selectedCount} resources selected`);
 * ```
 */
export const selectSelectedCount = (state: CollectionsState): number => {
  return state.selectedResourceIds.size;
};

/**
 * Selector: Get array of selected resource IDs
 * 
 * Converts Set to Array for easier iteration
 * 
 * @example
 * ```typescript
 * const selectedIds = useCollectionsStore(selectSelectedResourceIdsArray);
 * await batchAddResources(collectionId, selectedIds);
 * ```
 */
export const selectSelectedResourceIdsArray = (state: CollectionsState): string[] => {
  return Array.from(state.selectedResourceIds);
};

/**
 * Selector: Check if any resources are selected
 * 
 * @example
 * ```typescript
 * const hasSelection = useCollectionsStore(selectHasSelection);
 * if (hasSelection) {
 *   // Show batch action toolbar
 * }
 * ```
 */
export const selectHasSelection = (state: CollectionsState): boolean => {
  return state.selectedResourceIds.size > 0;
};

/**
 * Selector: Get collection by ID
 * 
 * @example
 * ```typescript
 * const getCollection = useCollectionsStore(selectCollectionById);
 * const collection = getCollection('col_123');
 * ```
 */
export const selectCollectionById = (state: CollectionsState) => {
  return (id: string): Collection | undefined => {
    return state.collections.find((c) => c.id === id);
  };
};

/**
 * Selector: Get collections sorted by name
 * 
 * @example
 * ```typescript
 * const sortedCollections = useCollectionsStore(selectCollectionsSortedByName);
 * ```
 */
export const selectCollectionsSortedByName = (state: CollectionsState): Collection[] => {
  return [...state.collections].sort((a, b) => 
    a.name.localeCompare(b.name)
  );
};

/**
 * Selector: Get collections sorted by resource count
 * 
 * @example
 * ```typescript
 * const popularCollections = useCollectionsStore(selectCollectionsByResourceCount);
 * ```
 */
export const selectCollectionsByResourceCount = (state: CollectionsState): Collection[] => {
  return [...state.collections].sort((a, b) => 
    (b.resource_count || 0) - (a.resource_count || 0)
  );
};

/**
 * Selector: Get collections sorted by creation date (newest first)
 * 
 * @example
 * ```typescript
 * const recentCollections = useCollectionsStore(selectCollectionsByDate);
 * ```
 */
export const selectCollectionsByDate = (state: CollectionsState): Collection[] => {
  return [...state.collections].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
};

/**
 * Selector: Get public collections
 * 
 * @example
 * ```typescript
 * const publicCollections = useCollectionsStore(selectPublicCollections);
 * ```
 */
export const selectPublicCollections = (state: CollectionsState): Collection[] => {
  return state.collections.filter((c) => c.is_public);
};

/**
 * Selector: Get private collections
 * 
 * @example
 * ```typescript
 * const privateCollections = useCollectionsStore(selectPrivateCollections);
 * ```
 */
export const selectPrivateCollections = (state: CollectionsState): Collection[] => {
  return state.collections.filter((c) => !c.is_public);
};

/**
 * Selector: Get total resource count across all collections
 * 
 * @example
 * ```typescript
 * const totalResources = useCollectionsStore(selectTotalResourceCount);
 * console.log(`${totalResources} resources across all collections`);
 * ```
 */
export const selectTotalResourceCount = (state: CollectionsState): number => {
  return state.collections.reduce((sum, c) => sum + (c.resource_count || 0), 0);
};
