import { useEffect, useState } from 'react';
import { useReducedMotion } from '../hooks/useReducedMotion';

/**
 * Hook for animated number counting
 * @param end - Target number to count to
 * @param duration - Animation duration in milliseconds
 * @param start - Starting number (default: 0)
 * @returns Current animated count value
 */
export const useCountUp = (
  end: number,
  duration: number = 2000,
  start: number = 0
): number => {
  const [count, setCount] = useState(start);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    // If reduced motion is preferred, show final value immediately
    if (prefersReducedMotion) {
      setCount(end);
      return;
    }

    let startTime: number | null = null;
    
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      // Easing function (easeOutExpo) for smooth deceleration
      const easeOut = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      
      setCount(Math.floor(start + (end - start) * easeOut));

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };

    requestAnimationFrame(step);
  }, [end, duration, start, prefersReducedMotion]);

  return count;
};

/**
 * Hook for generating staggered animation delays
 * @param itemCount - Number of items to stagger
 * @param baseDelay - Base delay between items in seconds
 * @returns Array of delay objects
 */
export const useStaggeredAnimation = (itemCount: number, baseDelay: number = 0.05) => {
  return Array.from({ length: itemCount }, (_, i) => ({
    delay: i * baseDelay
  }));
};

/**
 * Helper to get animation variants based on reduced motion preference
 * @param variants - Animation variants object
 * @param prefersReducedMotion - Whether user prefers reduced motion
 * @returns Simplified or full variants
 */
export const getVariants = (variants: any, prefersReducedMotion: boolean) => {
  if (prefersReducedMotion) {
    return {
      hidden: { opacity: 0 },
      visible: { opacity: 1, transition: { duration: 0 } }
    };
  }
  return variants;
};
