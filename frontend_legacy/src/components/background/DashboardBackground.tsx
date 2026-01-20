import { useEffect, useState } from 'react';
import { usePerformanceMonitor } from '../../hooks/usePerformanceMonitor';
import './DashboardBackground.css';

interface DashboardBackgroundProps {
  intensity?: 'low' | 'medium' | 'high';
  speed?: 'slow' | 'normal' | 'fast';
  layers?: number; // Number of gradient orbs (default: 5)
}

export const DashboardBackground = ({ 
  intensity = 'low', 
  speed = 'slow',
  layers = 5
}: DashboardBackgroundProps) => {
  const [reducedMotion, setReducedMotion] = useState(false);
  const { isLowPerformance } = usePerformanceMonitor(30);

  useEffect(() => {
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Disable animations if performance is low or reduced motion is preferred
  const shouldDisableAnimations = reducedMotion || isLowPerformance;

  // Adjust number of layers based on performance
  const effectiveLayers = isLowPerformance ? Math.min(3, layers) : layers;

  return (
    <div 
      className={`dashboard-background ${shouldDisableAnimations ? 'reduced-motion' : ''}`}
      data-intensity={intensity}
      data-speed={speed}
      data-performance={isLowPerformance ? 'low' : 'normal'}
      aria-hidden="true"
    >
      {/* Core 5 gradient orbs with independent animations */}
      {effectiveLayers >= 1 && <div className="gradient-orb gradient-orb-1" />}
      {effectiveLayers >= 2 && <div className="gradient-orb gradient-orb-2" />}
      {effectiveLayers >= 3 && <div className="gradient-orb gradient-orb-3" />}
      {effectiveLayers >= 4 && <div className="gradient-orb gradient-orb-4" />}
      {effectiveLayers >= 5 && <div className="gradient-orb gradient-orb-5" />}
    </div>
  );
};
