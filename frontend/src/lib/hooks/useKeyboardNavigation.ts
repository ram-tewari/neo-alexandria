/**
 * useKeyboardNavigation hook
 * Provides keyboard navigation utilities for lists and grids
 */

import { useEffect, useCallback, useRef } from 'react';

export interface KeyboardNavigationOptions {
  /** Enable arrow key navigation */
  enableArrowKeys?: boolean;
  /** Enable Enter/Space for selection */
  enableSelection?: boolean;
  /** Enable Home/End keys */
  enableHomeEnd?: boolean;
  /** Callback when item is selected */
  onSelect?: (index: number) => void;
  /** Callback when navigation occurs */
  onNavigate?: (index: number) => void;
  /** Total number of items */
  itemCount: number;
  /** Current focused index */
  currentIndex?: number;
  /** Grid columns (for 2D navigation) */
  columns?: number;
  /** Whether navigation is enabled */
  enabled?: boolean;
}

/**
 * Hook for keyboard navigation in lists and grids
 * Supports arrow keys, Home/End, Enter/Space
 */
export const useKeyboardNavigation = ({
  enableArrowKeys = true,
  enableSelection = true,
  enableHomeEnd = true,
  onSelect,
  onNavigate,
  itemCount,
  currentIndex = 0,
  columns = 1,
  enabled = true,
}: KeyboardNavigationOptions) => {
  const containerRef = useRef<HTMLElement | null>(null);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled || itemCount === 0) return;

      // Check if focus is within the container
      if (containerRef.current && !containerRef.current.contains(document.activeElement)) {
        return;
      }

      let newIndex = currentIndex;
      let handled = false;

      // Arrow key navigation
      if (enableArrowKeys) {
        switch (e.key) {
          case 'ArrowDown':
            e.preventDefault();
            newIndex = Math.min(currentIndex + columns, itemCount - 1);
            handled = true;
            break;
          case 'ArrowUp':
            e.preventDefault();
            newIndex = Math.max(currentIndex - columns, 0);
            handled = true;
            break;
          case 'ArrowRight':
            e.preventDefault();
            newIndex = Math.min(currentIndex + 1, itemCount - 1);
            handled = true;
            break;
          case 'ArrowLeft':
            e.preventDefault();
            newIndex = Math.max(currentIndex - 1, 0);
            handled = true;
            break;
        }
      }

      // Home/End navigation
      if (enableHomeEnd) {
        switch (e.key) {
          case 'Home':
            e.preventDefault();
            newIndex = 0;
            handled = true;
            break;
          case 'End':
            e.preventDefault();
            newIndex = itemCount - 1;
            handled = true;
            break;
        }
      }

      // Selection with Enter/Space
      if (enableSelection && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        onSelect?.(currentIndex);
        handled = true;
      }

      // Trigger navigation callback if index changed
      if (handled && newIndex !== currentIndex) {
        onNavigate?.(newIndex);
      }
    },
    [
      enabled,
      itemCount,
      currentIndex,
      columns,
      enableArrowKeys,
      enableHomeEnd,
      enableSelection,
      onSelect,
      onNavigate,
    ]
  );

  useEffect(() => {
    if (!enabled) return;

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [enabled, handleKeyDown]);

  return containerRef;
};
