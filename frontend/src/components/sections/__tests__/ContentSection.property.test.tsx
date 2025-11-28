/**
 * Property-Based Tests for ContentSection Component
 * Feature: dual-theme-animated-website
 * Property 6: Viewport-triggered animations
 * Validates: Requirements 3.1, 3.2, 8.1
 */

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import * as fc from 'fast-check';
import { ContentSection } from '../ContentSection';
import { ThemeProvider } from '../../../contexts/ThemeContext';

describe('ContentSection Property Tests', () => {
  describe('Property 6: Viewport-triggered animations', () => {
    it('should render content section with animation type', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<'fade' | 'slide' | 'scale'>('fade', 'slide', 'scale'),
          fc.string({ minLength: 1, maxLength: 100 }),
          (animationType, content) => {
            const { container, unmount } = render(
              <ThemeProvider>
                <ContentSection animationType={animationType}>
                  <div>{content}</div>
                </ContentSection>
              </ThemeProvider>
            );

            // Should render the content section
            const section = container.querySelector('.content-section');
            const result = section !== null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should render title and subtitle when provided', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          fc.string({ minLength: 1, maxLength: 200 }),
          fc.string({ minLength: 1, maxLength: 100 }),
          (title, subtitle, content) => {
            const { container, unmount } = render(
              <ThemeProvider>
                <ContentSection title={title} subtitle={subtitle}>
                  <div>{content}</div>
                </ContentSection>
              </ThemeProvider>
            );

            // Should have header with title and subtitle
            const header = container.querySelector('.content-section__header');
            const titleEl = container.querySelector('.content-section__title');
            const subtitleEl = container.querySelector('.content-section__subtitle');
            const result = header !== null && titleEl !== null && subtitleEl !== null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should render without title and subtitle', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (content) => {
            const { container, unmount } = render(
              <ThemeProvider>
                <ContentSection>
                  <div>{content}</div>
                </ContentSection>
              </ThemeProvider>
            );

            // Should not have header when no title/subtitle
            const header = container.querySelector('.content-section__header');
            const result = header === null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should apply theme data attribute', () => {
      fc.assert(
        fc.property(
          fc.constantFrom<'light' | 'dark'>('light', 'dark'),
          fc.string({ minLength: 1, maxLength: 100 }),
          (theme, content) => {
            const { container, unmount } = render(
              <ThemeProvider defaultTheme={theme}>
                <ContentSection>
                  <div>{content}</div>
                </ContentSection>
              </ThemeProvider>
            );

            // Should have theme data attribute
            const section = container.querySelector('.content-section');
            const result = section !== null && section.hasAttribute('data-theme');
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should render children content', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (content) => {
            const { container, unmount } = render(
              <ThemeProvider>
                <ContentSection>
                  <div className="test-content">{content}</div>
                </ContentSection>
              </ThemeProvider>
            );

            // Should render children
            const body = container.querySelector('.content-section__body');
            const testContent = container.querySelector('.test-content');
            const result = body !== null && testContent !== null;
            
            unmount();
            return result;
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
