/**
 * useBatchSelection hook
 * Manages batch selection state for resources
 * Uses Set-based state for efficient lookups and updates
 */

import { useState, useCallback } from 'react';

export interface UseBatchSelectionReturn {
  /** Set of selected resource IDs */
  selectedIds: Set<string>;
  /** Toggle selection for a single resource */
  toggleSelection: (id: string) => void;
  /** Select all resources from provided list */
  selectAll: (ids: string[]) => void;
  /** Clear all selections */
  clearSelection: () => void;
  /** Check if a resource is selected */
  isSelected: (id: string) => boolean;
  /** Get count of selected items */
  selectedCount: number;
}

/**
 * Hook for managing batch selection state
 * 
 * @example
 * ```tsx
 * const { selectedIds, toggleSelection, selectAll, clearSelection } = useBatchSelection();
 * 
 * // Toggle single item
 * toggleSelection('resource-123');
 * 
 * // Select all visible items
 * selectAll(resources.map(r => r.id));
 * 
 * // Clear selection
 * clearSelection();
 * ```
 */
export const useBatchSelection = (): UseBatchSelectionReturn => {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  /**
   * Toggle selection for a single resource
   * If selected, removes it; if not selected, adds it
   */
  const toggleSelection = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  /**
   * Select all resources from the provided list
   * Replaces current selection with new set
   */
  const selectAll = useCallback((ids: string[]) => {
    setSelectedIds(new Set(ids));
  }, []);

  /**
   * Clear all selections
   */
  const clearSelection = useCallback(() => {
    setSelectedIds(new Set());
  }, []);

  /**
   * Check if a resource is selected
   */
  const isSelected = useCallback(
    (id: string) => selectedIds.has(id),
    [selectedIds]
  );

  return {
    selectedIds,
    toggleSelection,
    selectAll,
    clearSelection,
    isSelected,
    selectedCount: selectedIds.size,
  };
};
