/**
 * Utility functions and constants
 * Central export point for all utility modules
 */

// Animation utilities
export {
  animations,
  fadeIn,
  slideUp,
  scalePress,
  hover,
  slideInRight,
  scaleAndFade,
  staggerChildren,
  createAnimation,
  DURATIONS,
  EASE_OUT,
} from './animations';

// Fuse.js configuration
export {
  defaultFuseOptions,
  createFuseInstance,
  searchWithFuse,
} from './fuse-config';

// Note: Motion configuration exports are available directly from './motion-config'
// Import as: import { defaultTransition, prefersReducedMotion } from '@/lib/utils/motion-config';

// Accessibility utilities
export {
  announceToScreenReader,
  announceFilterChange,
  announceUploadProgress,
  announceBatchSelection,
  announceNavigation,
  announceLoading,
  announceError,
  announceSuccess,
} from './announceToScreenReader';

export {
  getFocusableElements,
  trapFocus,
  FocusManager,
  moveFocusTo,
  FOCUS_VISIBLE_STYLES,
  SR_ONLY_CLASS,
  makeSROnly,
} from './focusManagement';
