/**
 * useInfiniteScroll hook
 * Implements IntersectionObserver-based infinite scroll functionality
 */

import { useEffect, useRef } from 'react';

export interface UseInfiniteScrollOptions {
  /** Callback to trigger when sentinel element intersects */
  onIntersect: () => void;
  /** Whether the hook is enabled */
  enabled?: boolean;
  /** Intersection threshold (0-1) */
  threshold?: number;
  /** Root margin for intersection observer */
  rootMargin?: string;
}

/**
 * Hook for implementing infinite scroll with IntersectionObserver
 * 
 * @example
 * ```tsx
 * const sentinelRef = useInfiniteScroll({
 *   onIntersect: fetchNextPage,
 *   enabled: hasNextPage && !isFetchingNextPage,
 *   threshold: 0.8,
 * });
 * 
 * return (
 *   <div>
 *     {items.map(item => <Item key={item.id} {...item} />)}
 *     <div ref={sentinelRef} className="h-20" />
 *   </div>
 * );
 * ```
 */
export function useInfiniteScroll({
  onIntersect,
  enabled = true,
  threshold = 0.8,
  rootMargin = '0px',
}: UseInfiniteScrollOptions) {
  const sentinelRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    // Don't set up observer if disabled or no sentinel element
    if (!enabled || !sentinelRef.current) {
      return;
    }

    // Create intersection observer
    observerRef.current = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        
        // Trigger callback when sentinel intersects
        if (entry.isIntersecting) {
          onIntersect();
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    // Start observing the sentinel element
    observerRef.current.observe(sentinelRef.current);

    // Cleanup: disconnect observer
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
        observerRef.current = null;
      }
    };
  }, [enabled, onIntersect, threshold, rootMargin]);

  return sentinelRef;
}
