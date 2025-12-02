/**
 * Custom React hooks
 * Central export point for all custom hooks
 */

// State management hooks
export { useLocalStorage } from './useLocalStorage';

// Keyboard interaction hooks
export { useKeyboardShortcut } from './useKeyboardShortcut';
export type { KeyboardModifiers, KeyboardShortcutOptions } from './useKeyboardShortcut';

// Focus management hooks
export { useFocusTrap } from './useFocusTrap';
export type { FocusTrapOptions } from './useFocusTrap';

// Data fetching hooks
export { useResources } from './useResources';
export { useInfiniteResources } from './useInfiniteResources';
export type { UseInfiniteResourcesOptions, UseInfiniteResourcesResult } from './useInfiniteResources';

// Scroll hooks
export { useInfiniteScroll } from './useInfiniteScroll';
export type { UseInfiniteScrollOptions } from './useInfiniteScroll';

// Filter management hooks
export { useResourceFilters, useHasActiveFilters, useActiveFilterCount } from './useResourceFilters';
export type { ResourceFilters } from './useResourceFilters';

// Batch selection hooks
export { useBatchSelection } from './useBatchSelection';
export type { UseBatchSelectionReturn } from './useBatchSelection';

// Upload management hooks
export { useUploadQueue } from './useUploadQueue';
export type { 
  UploadItem, 
  UploadStatus, 
  ProcessingStage
} from './useUploadQueue';

// Keyboard navigation hooks
export { useKeyboardNavigation } from './useKeyboardNavigation';
export type { KeyboardNavigationOptions } from './useKeyboardNavigation';
