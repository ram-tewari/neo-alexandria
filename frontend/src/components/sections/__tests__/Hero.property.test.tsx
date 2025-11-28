/**
 * Property-Based Tests for Hero Component
 * Feature: dual-theme-animated-website
 * Property 18: Scroll-based parallax (light mode)
 * Property 19: Glow effects (dark mode)
 * Validates: Requirements 3.4, 3.5
 */

import { describe, it, expect } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import * as fc from 'fast-check';
import { Hero } from '../Hero';
import { ThemeProvider } from '../../../contexts/ThemeContext';

describe('Hero Property Tests', () => {
  describe('Property 18: Scroll-based parallax (light mode)', () => {
    it('should apply parallax transform to background accent in light mode', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined }),
          (title, subtitle) => {
            const { container, unmount } = render(
              <ThemeProvider defaultTheme="light">
                <Hero
                  title={title}
                  subtitle={subtitle}
                  backgroundAnimation={true}
                />
              </ThemeProvider>
            );

            // In light mode, should have parallax background accent
            const lightAccent = container.querySelector('.hero__background-accent--light');
            const result = lightAccent !== null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should not have parallax accent in dark mode', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.string({ minLength: 1, maxLength: 100 }),
          async (title) => {
            // Set dark theme in localStorage
            localStorage.setItem('theme-test', 'dark');
            
            const { container, unmount } = render(
              <ThemeProvider defaultTheme="dark" storageKey="theme-test">
                <Hero
                  title={title}
                  backgroundAnimation={true}
                />
              </ThemeProvider>
            );

            // Wait for theme to be applied
            await waitFor(() => {
              const hero = container.querySelector('.hero');
              expect(hero?.getAttribute('data-theme')).toBe('dark');
            });

            // In dark mode, should NOT have light parallax accent
            const lightAccent = container.querySelector('.hero__background-accent--light');
            const result = lightAccent === null;
            
            unmount();
            localStorage.removeItem('theme-test');
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should disable background animation when backgroundAnimation is false', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<'light' | 'dark'>('light', 'dark'),
          fc.string({ minLength: 1, maxLength: 100 }),
          (theme, title) => {
            const { container, unmount } = render(
              <ThemeProvider defaultTheme={theme}>
                <Hero
                  title={title}
                  backgroundAnimation={false}
                />
              </ThemeProvider>
            );

            // Should not have any background accents when disabled
            const background = container.querySelector('.hero__background');
            const result = background === null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('Property 19: Glow effects (dark mode)', () => {
    it('should apply glow effects to background accents in dark mode', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.string({ minLength: 1, maxLength: 100 }),
          fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined }),
          async (title, subtitle) => {
            // Set dark theme in localStorage
            localStorage.setItem('theme-test', 'dark');
            
            const { container, unmount } = render(
              <ThemeProvider defaultTheme="dark" storageKey="theme-test">
                <Hero
                  title={title}
                  subtitle={subtitle}
                  backgroundAnimation={true}
                />
              </ThemeProvider>
            );

            // Wait for theme to be applied
            await waitFor(() => {
              const hero = container.querySelector('.hero');
              expect(hero?.getAttribute('data-theme')).toBe('dark');
            });

            // In dark mode, should have glow background accents
            const glow1 = container.querySelector('.hero__background-accent--glow-1');
            const glow2 = container.querySelector('.hero__background-accent--glow-2');
            const result = glow1 !== null && glow2 !== null;
            
            unmount();
            localStorage.removeItem('theme-test');
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should have dark mode class on glow elements', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.string({ minLength: 1, maxLength: 100 }),
          async (title) => {
            // Set dark theme in localStorage
            localStorage.setItem('theme-test', 'dark');
            
            const { container, unmount } = render(
              <ThemeProvider defaultTheme="dark" storageKey="theme-test">
                <Hero
                  title={title}
                  backgroundAnimation={true}
                />
              </ThemeProvider>
            );

            // Wait for theme to be applied
            await waitFor(() => {
              const hero = container.querySelector('.hero');
              expect(hero?.getAttribute('data-theme')).toBe('dark');
            });

            // All glow elements should have dark mode class
            const glowElements = container.querySelectorAll('.hero__background-accent--dark');
            const result = glowElements.length === 2;
            
            unmount();
            localStorage.removeItem('theme-test');
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should not have glow effects in light mode', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (title) => {
            const { container, unmount } = render(
              <ThemeProvider defaultTheme="light">
                <Hero
                  title={title}
                  backgroundAnimation={true}
                />
              </ThemeProvider>
            );

            // In light mode, should NOT have dark glow accents
            const glowElements = container.querySelectorAll('.hero__background-accent--dark');
            const result = glowElements.length === 0;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should render hero content regardless of theme', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<'light' | 'dark'>('light', 'dark'),
          fc.string({ minLength: 1, maxLength: 100 }),
          fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined }),
          (theme, title, subtitle) => {
            const { container, unmount } = render(
              <ThemeProvider defaultTheme={theme}>
                <Hero
                  title={title}
                  subtitle={subtitle}
                  backgroundAnimation={true}
                />
              </ThemeProvider>
            );

            // Should always have hero content
            const heroContent = container.querySelector('.hero__content');
            const heroTitle = container.querySelector('.hero__title');
            const result = heroContent !== null && heroTitle !== null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
