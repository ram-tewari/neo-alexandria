/**
 * MarbleBackdrop Component
 * 
 * Decorative marble texture background for light mode only
 * Features white base with gold veins and glossy finish
 */

import { useEffect, useState } from 'react';
import './MarbleBackdrop.css';

export const MarbleBackdrop = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');

  useEffect(() => {
    // Detect initial theme
    const root = document.documentElement;
    const initialTheme = root.classList.contains('light') ? 'light' : 'dark';
    setTheme(initialTheme);

    // Watch for theme changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          const currentTheme = root.classList.contains('light') ? 'light' : 'dark';
          setTheme(currentTheme);
        }
      });
    });

    observer.observe(root, {
      attributes: true,
      attributeFilter: ['class'],
    });

    return () => observer.disconnect();
  }, []);

  // Only render in light mode
  if (theme !== 'light') {
    return null;
  }

  return (
    <div className="marble-backdrop light" aria-hidden="true">
      <div className="marble-texture" />
      <div className="marble-gradient" />
    </div>
  );
};
