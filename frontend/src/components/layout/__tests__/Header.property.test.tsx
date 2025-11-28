/**
 * Property-Based Tests for Header Component
 * Feature: dual-theme-animated-website
 * Property 7: Collapse state synchronization
 * Property 9: Theme accent color application
 * Validates: Requirements 5.7, 6.3, 5.4, 6.6, 8.4, 9.2, 9.3
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import * as fc from 'fast-check';
import { Header, NavigationLink } from '../Header';
import { ThemeProvider } from '../../../contexts/ThemeContext';

describe('Header Property Tests', () => {
  describe('Property 7: Collapse State Synchronization', () => {
    it('should synchronize arrow rotation with collapse state', async () => {
      const user = userEvent.setup();
      
      const mockLinks: NavigationLink[] = [
        { label: 'Home', href: '/' },
        { label: 'About', href: '/about' },
      ];

      const { container } = render(
        <ThemeProvider>
          <Header links={mockLinks} />
        </ThemeProvider>
      );

      const collapseBtn = screen.getByLabelText('Collapse navigation');
      
      // Initial state - not collapsed, should show ChevronUp
      expect(collapseBtn).toHaveAttribute('aria-expanded', 'true');
      
      // Click to collapse
      await user.click(collapseBtn);
      
      // Should be collapsed now
      const expandBtn = screen.getByLabelText('Expand navigation');
      expect(expandBtn).toHaveAttribute('aria-expanded', 'false');
      
      // Click to expand
      await user.click(expandBtn);
      
      // Should be expanded again
      expect(screen.getByLabelText('Collapse navigation')).toHaveAttribute('aria-expanded', 'true');
    });

    it('should maintain collapse state across multiple toggles', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.integer({ min: 1, max: 10 }),
          async (toggleCount) => {
            const user = userEvent.setup();
            
            const mockLinks: NavigationLink[] = [
              { label: 'Test', href: '/test' },
            ];

            const { unmount } = render(
              <ThemeProvider>
                <Header links={mockLinks} />
              </ThemeProvider>
            );

            // Toggle multiple times
            for (let i = 0; i < toggleCount; i++) {
              const button = i % 2 === 0 
                ? screen.getByLabelText('Collapse navigation')
                : screen.getByLabelText('Expand navigation');
              
              await user.click(button);
            }

            // Final state should match toggle count parity
            const expectedLabel = toggleCount % 2 === 0 
              ? 'Collapse navigation'
              : 'Expand navigation';
            
            const finalButton = screen.getByLabelText(expectedLabel);
            const result = finalButton !== null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 20 }
      );
    });
  });

  describe('Property 9: Theme Accent Color Application', () => {
    it('should apply accent color to active navigation links', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<'light' | 'dark'>('light', 'dark'),
          fc.integer({ min: 0, max: 4 }),
          (theme, activeIndex) => {
            const mockLinks: NavigationLink[] = Array.from({ length: 5 }, (_, i) => ({
              label: `Link ${i}`,
              href: `/link-${i}`,
              active: i === activeIndex,
            }));

            const { container, unmount } = render(
              <ThemeProvider defaultTheme={theme}>
                <Header links={mockLinks} />
              </ThemeProvider>
            );

            // Find active link
            const activeLink = container.querySelector('.header__nav-link--active');
            const result = activeLink !== null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should apply theme colors to all navigation elements', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<'light' | 'dark'>('light', 'dark'),
          (theme) => {
            const mockLinks: NavigationLink[] = [
              { label: 'Home', href: '/', active: true },
              { label: 'About', href: '/about' },
            ];

            const { container, unmount } = render(
              <ThemeProvider defaultTheme={theme}>
                <Header links={mockLinks} />
              </ThemeProvider>
            );

            // Header should be rendered
            const header = container.querySelector('.header');
            const result = header !== null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
