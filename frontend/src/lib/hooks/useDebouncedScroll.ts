/**
 * useDebouncedScroll Hook
 * 
 * Provides debounced scroll event handling for performance optimization.
 * Prevents excessive callback invocations during rapid scroll events.
 * 
 * Requirements: 7.2 - React optimization
 * 
 * @param callback - Function to call on scroll (debounced)
 * @param delay - Debounce delay in milliseconds (default: 100ms)
 * @returns Debounced scroll handler
 */

import { useCallback, useRef, useEffect } from 'react';

export function useDebouncedScroll(
  callback: () => void,
  delay: number = 100
): () => void {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);

  // Update callback ref when callback changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Return debounced scroll handler
  return useCallback(() => {
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      callbackRef.current();
    }, delay);
  }, [delay]);
}
