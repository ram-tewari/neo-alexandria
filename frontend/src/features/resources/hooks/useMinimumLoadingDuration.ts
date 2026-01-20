import { useState, useEffect } from 'react';

/**
 * Hook to enforce a minimum loading duration to prevent UI flashing
 * 
 * @param isLoading - Actual loading state from query
 * @param minimumDuration - Minimum duration in milliseconds (default: 200ms)
 * @returns Extended loading state that respects minimum duration
 */
export function useMinimumLoadingDuration(
  isLoading: boolean,
  minimumDuration: number = 200
): boolean {
  const [isMinimumLoading, setIsMinimumLoading] = useState(false);
  const [loadingStartTime, setLoadingStartTime] = useState<number | null>(null);

  useEffect(() => {
    if (isLoading && !loadingStartTime) {
      // Loading started
      setLoadingStartTime(Date.now());
      setIsMinimumLoading(true);
    } else if (!isLoading && loadingStartTime) {
      // Loading finished, check if minimum duration has passed
      const elapsed = Date.now() - loadingStartTime;
      const remaining = minimumDuration - elapsed;

      if (remaining > 0) {
        // Wait for remaining time
        const timer = setTimeout(() => {
          setIsMinimumLoading(false);
          setLoadingStartTime(null);
        }, remaining);
        return () => clearTimeout(timer);
      } else {
        // Minimum duration already passed
        setIsMinimumLoading(false);
        setLoadingStartTime(null);
      }
    }
  }, [isLoading, loadingStartTime, minimumDuration]);

  return isMinimumLoading;
}
