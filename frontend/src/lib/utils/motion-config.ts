/**
 * Framer Motion configuration and defaults
 * Sets up global animation preferences for the application
 */

/**
 * Default transition configuration for all motion components
 */
export const defaultTransition = {
  duration: 0.2,
  ease: [0.4, 0, 0.2, 1] as const,
};

/**
 * Reduced motion configuration for accessibility
 * Respects user's prefers-reduced-motion setting
 */
export const reducedMotionTransition = {
  duration: 0,
  ease: 'linear' as const,
};

/**
 * Check if user prefers reduced motion
 */
export const prefersReducedMotion = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/**
 * Get appropriate transition based on user preference
 */
export const getTransition = (transition = defaultTransition) => {
  return prefersReducedMotion() ? reducedMotionTransition : transition;
};
