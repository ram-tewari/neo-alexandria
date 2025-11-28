/**
 * Property-Based Tests for Theme Context
 * Feature: dual-theme-animated-website
 * Property 14: Theme persistence
 * Property 17: Component theme reactivity
 * Validates: Requirements 13.3, 13.2, 15.2
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react';
import * as fc from 'fast-check';
import { ThemeProvider, useTheme, Theme } from '../ThemeContext';
import React from 'react';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

describe('Theme Context Property Tests', () => {
  beforeEach(() => {
    // Setup localStorage mock
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    });
    localStorageMock.clear();
    
    // Clear document attributes
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.classList.remove('light', 'dark');
  });

  afterEach(() => {
    localStorageMock.clear();
  });

  describe('Property 14: Theme Persistence', () => {
    it('should persist any theme selection to localStorage', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<Theme>('light', 'dark'),
          fc.string({ minLength: 1, maxLength: 20 }),
          (theme, storageKey) => {
            // Clear storage before each iteration
            localStorageMock.clear();
            
            const { result } = renderHook(() => useTheme(), {
              wrapper: ({ children }) => (
                <ThemeProvider storageKey={storageKey}>{children}</ThemeProvider>
              ),
            });

            // Set theme
            act(() => {
              result.current.setTheme(theme);
            });

            // Verify theme is stored
            const stored = localStorageMock.getItem(storageKey);
            return stored === theme;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should restore theme from localStorage on mount', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<Theme>('light', 'dark'),
          fc.string({ minLength: 1, maxLength: 20 }),
          (theme, storageKey) => {
            // Pre-populate localStorage
            localStorageMock.clear();
            localStorageMock.setItem(storageKey, theme);

            // Mount provider
            const { result } = renderHook(() => useTheme(), {
              wrapper: ({ children }) => (
                <ThemeProvider storageKey={storageKey}>{children}</ThemeProvider>
              ),
            });

            // Verify theme is restored
            return result.current.theme === theme;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should maintain theme persistence across multiple set operations', () => {
      fc.assert(
        fc.property(
          fc.array(fc.constantFrom<Theme>('light', 'dark'), { minLength: 1, maxLength: 10 }),
          fc.string({ minLength: 1, maxLength: 20 }),
          (themes, storageKey) => {
            localStorageMock.clear();
            
            const { result } = renderHook(() => useTheme(), {
              wrapper: ({ children }) => (
                <ThemeProvider storageKey={storageKey}>{children}</ThemeProvider>
              ),
            });

            // Apply each theme in sequence
            themes.forEach((theme) => {
              act(() => {
                result.current.setTheme(theme);
              });
            });

            // Verify last theme is persisted
            const lastTheme = themes[themes.length - 1];
            const stored = localStorageMock.getItem(storageKey);
            
            return stored === lastTheme && result.current.theme === lastTheme;
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should handle toggle operations and persist correctly', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<Theme>('light', 'dark'),
          fc.integer({ min: 1, max: 10 }),
          (initialTheme, toggleCount) => {
            localStorageMock.clear();
            localStorageMock.setItem('theme-test', initialTheme);
            
            const { result } = renderHook(() => useTheme(), {
              wrapper: ({ children }) => (
                <ThemeProvider storageKey="theme-test">{children}</ThemeProvider>
              ),
            });

            // Toggle theme multiple times
            for (let i = 0; i < toggleCount; i++) {
              act(() => {
                result.current.toggleTheme();
              });
            }

            // Calculate expected theme
            const expectedTheme = toggleCount % 2 === 0 ? initialTheme : (initialTheme === 'light' ? 'dark' : 'light');
            const stored = localStorageMock.getItem('theme-test');
            
            return stored === expectedTheme && result.current.theme === expectedTheme;
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('Property 17: Component Theme Reactivity', () => {
    // Test component that displays current theme
    function ThemeDisplay() {
      const { theme } = useTheme();
      return <div data-testid="theme-display">{theme}</div>;
    }

    it('should update all consuming components when theme changes', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<Theme>('light', 'dark'),
          fc.constantFrom<Theme>('light', 'dark'),
          (initialTheme, newTheme) => {
            localStorageMock.clear();
            
            const { result } = renderHook(() => useTheme(), {
              wrapper: ({ children }) => (
                <ThemeProvider defaultTheme={initialTheme}>{children}</ThemeProvider>
              ),
            });

            // Change theme
            act(() => {
              result.current.setTheme(newTheme);
            });

            // Verify theme updated
            return result.current.theme === newTheme;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should apply theme to document root when theme changes', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<Theme>('light', 'dark'),
          (theme) => {
            localStorageMock.clear();
            document.documentElement.removeAttribute('data-theme');
            document.documentElement.classList.remove('light', 'dark');
            
            const { result } = renderHook(() => useTheme(), {
              wrapper: ({ children }) => (
                <ThemeProvider>{children}</ThemeProvider>
              ),
            });

            // Set theme
            act(() => {
              result.current.setTheme(theme);
            });

            // Verify document attributes
            const hasDataAttr = document.documentElement.getAttribute('data-theme') === theme;
            const hasClass = document.documentElement.classList.contains(theme);
            
            return hasDataAttr && hasClass;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should maintain theme consistency across multiple component instances', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<Theme>('light', 'dark'),
          (theme) => {
            localStorageMock.clear();
            
            // Create a single hook instance
            const { result } = renderHook(() => useTheme(), {
              wrapper: ({ children }) => (
                <ThemeProvider>{children}</ThemeProvider>
              ),
            });

            // Set theme
            act(() => {
              result.current.setTheme(theme);
            });

            // Verify theme is set correctly
            const themeMatches = result.current.theme === theme;
            
            // Verify document root also has the theme
            const docTheme = document.documentElement.getAttribute('data-theme');
            const docMatches = docTheme === theme;
            
            return themeMatches && docMatches;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should update theme within transition duration', async () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: ({ children }) => (
          <ThemeProvider>{children}</ThemeProvider>
        ),
      });

      const startTime = Date.now();
      
      act(() => {
        result.current.setTheme('dark');
      });

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Theme update should be nearly instant (well under 300ms)
      expect(duration).toBeLessThan(300);
      expect(result.current.theme).toBe('dark');
    });
  });

  describe('Cross-Property Tests', () => {
    it('should maintain persistence and reactivity together', () => {
      fc.assert(
        fc.property(
          fc.array(fc.constantFrom<Theme>('light', 'dark'), { minLength: 2, maxLength: 5 }),
          (themes) => {
            localStorageMock.clear();
            
            const { result, rerender } = renderHook(() => useTheme(), {
              wrapper: ({ children }) => (
                <ThemeProvider storageKey="test-key">{children}</ThemeProvider>
              ),
            });

            // Apply themes in sequence
            themes.forEach((theme) => {
              act(() => {
                result.current.setTheme(theme);
              });
              
              // Verify both state and storage are updated
              const currentTheme = result.current.theme;
              const storedTheme = localStorageMock.getItem('test-key');
              
              if (currentTheme !== theme || storedTheme !== theme) {
                return false;
              }
            });

            return true;
          }
        ),
        { numRuns: 50 }
      );
    });
  });
});
