import { useEffect, useState, useRef } from 'react';

interface PerformanceMetrics {
  fps: number;
  isLowPerformance: boolean;
}

/**
 * Hook to monitor FPS and detect low performance
 * Automatically reduces animation complexity if FPS drops below threshold
 */
export function usePerformanceMonitor(threshold: number = 30): PerformanceMetrics {
  const [fps, setFps] = useState(60);
  const [isLowPerformance, setIsLowPerformance] = useState(false);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());
  const rafIdRef = useRef<number>();

  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      const elapsed = currentTime - lastTime;

      // Update FPS every second
      if (elapsed >= 1000) {
        const currentFPS = Math.round((frameCount * 1000) / elapsed);
        setFps(currentFPS);
        
        // Check if performance is low
        if (currentFPS < threshold) {
          setIsLowPerformance(true);
        } else if (currentFPS > threshold + 10) {
          // Add hysteresis to prevent flickering
          setIsLowPerformance(false);
        }

        frameCount = 0;
        lastTime = currentTime;
      }

      rafIdRef.current = requestAnimationFrame(measureFPS);
    };

    rafIdRef.current = requestAnimationFrame(measureFPS);

    return () => {
      if (rafIdRef.current) {
        cancelAnimationFrame(rafIdRef.current);
      }
    };
  }, [threshold]);

  return { fps, isLowPerformance };
}
