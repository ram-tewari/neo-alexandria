/**
 * Animation utilities for consistent micro-interactions across the application.
 * Uses Framer Motion animation objects with standardized timing and easing.
 */

import { Transition, Variants, TargetAndTransition } from 'framer-motion';

/**
 * Standard animation durations (in seconds)
 */
export const DURATIONS = {
  instant: 0.1,   // 100ms - button press, hover
  fast: 0.2,      // 200ms - fade, theme transition
  normal: 0.3,    // 300ms - slide, layout changes
  slow: 0.5,      // 500ms - complex transitions
} as const;

/**
 * Standard easing function
 */
export const EASE_OUT = [0.4, 0, 0.2, 1] as const;

/**
 * Base transition configuration
 */
const baseTransition: Transition = {
  duration: DURATIONS.fast,
  ease: EASE_OUT,
};

/**
 * Fade in/out animation
 */
export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: baseTransition },
  exit: { opacity: 0, transition: baseTransition },
};

/**
 * Slide up animation with fade
 */
const slideUpTransition: Transition = { duration: DURATIONS.normal, ease: EASE_OUT };

export const slideUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: slideUpTransition },
  exit: { opacity: 0, y: -20, transition: slideUpTransition },
};

/**
 * Scale press animation for buttons
 */
export const scalePress = {
  whileTap: { scale: 0.95, transition: { duration: DURATIONS.instant, ease: EASE_OUT } },
};

/**
 * Hover animation with subtle scale
 */
export const hover = {
  whileHover: { scale: 1.02 },
  transition: { duration: 0.15, ease: EASE_OUT },
};

/**
 * Slide in from right (for toasts)
 */
export const slideInRight: Variants = {
  initial: { opacity: 0, x: 100 },
  animate: { opacity: 1, x: 0, transition: baseTransition },
  exit: { opacity: 0, x: 100, transition: baseTransition },
};

/**
 * Scale and fade animation (for modals)
 */
const scaleAndFadeTransition: Transition = { duration: DURATIONS.instant, ease: EASE_OUT };

export const scaleAndFade: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1, transition: scaleAndFadeTransition },
  exit: { opacity: 0, scale: 0.95, transition: scaleAndFadeTransition },
};

/**
 * Stagger children animation
 */
export const staggerChildren = {
  animate: {
    transition: {
      staggerChildren: 0.05,
    },
  },
};

/**
 * Animation presets for common use cases
 */
export const animations = {
  fadeIn,
  slideUp,
  scalePress,
  hover,
  slideInRight,
  scaleAndFade,
  staggerChildren,
} as const;

/**
 * Helper function to create custom animation variants
 */
export function createAnimation(
  initial: Record<string, any>,
  animate: Record<string, any>,
  exit?: Record<string, any>,
  duration: number = DURATIONS.fast
): Variants {
  return {
    initial,
    animate: {
      ...animate,
      transition: { duration, ease: EASE_OUT },
    },
    exit: exit || initial,
  };
}

export const pageTransition = fadeIn;
