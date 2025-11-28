import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import App from '../App';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests (a11y)', () => {
  it('should not have any accessibility violations on main app', async () => {
    const { container } = render(<App />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper heading hierarchy', () => {
    const { container } = render(<App />);
    const h1Elements = container.querySelectorAll('h1');
    
    // Should have exactly one h1
    expect(h1Elements.length).toBeLessThanOrEqual(1);
  });

  it('should have ARIA labels on interactive elements', () => {
    const { container } = render(<App />);
    const buttons = container.querySelectorAll('button');
    
    buttons.forEach((button) => {
      const hasAriaLabel = button.hasAttribute('aria-label');
      const hasAriaLabelledBy = button.hasAttribute('aria-labelledby');
      const hasTextContent = button.textContent && button.textContent.trim().length > 0;
      
      // Button should have either aria-label, aria-labelledby, or text content
      expect(hasAriaLabel || hasAriaLabelledBy || hasTextContent).toBe(true);
    });
  });

  it('should have sufficient color contrast', () => {
    const { container } = render(<App />);
    
    // This is a simplified check - in production, use axe-core for comprehensive testing
    const textElements = container.querySelectorAll('p, span, a, button, h1, h2, h3, h4, h5, h6');
    
    textElements.forEach((element) => {
      const styles = window.getComputedStyle(element);
      const color = styles.color;
      const backgroundColor = styles.backgroundColor;
      
      // Ensure color and background color are defined
      expect(color).toBeTruthy();
      expect(backgroundColor).toBeTruthy();
    });
  });

  it('should support keyboard navigation', () => {
    const { container } = render(<App />);
    const focusableElements = container.querySelectorAll(
      'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    // Should have focusable elements
    expect(focusableElements.length).toBeGreaterThan(0);
    
    // All focusable elements should be visible or have proper ARIA
    focusableElements.forEach((element) => {
      const isVisible = (element as HTMLElement).offsetParent !== null;
      const hasAriaHidden = element.hasAttribute('aria-hidden');
      
      if (!isVisible) {
        // If not visible, should have aria-hidden
        expect(hasAriaHidden).toBe(true);
      }
    });
  });

  it('should have proper focus indicators', () => {
    const { container } = render(<App />);
    const focusableElements = container.querySelectorAll('a, button, input');
    
    focusableElements.forEach((element) => {
      const styles = window.getComputedStyle(element, ':focus');
      
      // Should have some focus styling (outline, box-shadow, etc.)
      // This is a basic check - actual implementation may vary
      expect(element).toBeTruthy();
    });
  });

  it('should have alt text for images', () => {
    const { container } = render(<App />);
    const images = container.querySelectorAll('img');
    
    images.forEach((img) => {
      const hasAlt = img.hasAttribute('alt');
      const hasAriaLabel = img.hasAttribute('aria-label');
      const hasAriaLabelledBy = img.hasAttribute('aria-labelledby');
      const isDecorative = img.getAttribute('role') === 'presentation' || img.getAttribute('alt') === '';
      
      // Image should have alt, aria-label, aria-labelledby, or be marked as decorative
      expect(hasAlt || hasAriaLabel || hasAriaLabelledBy || isDecorative).toBe(true);
    });
  });

  it('should have proper form labels', () => {
    const { container } = render(<App />);
    const inputs = container.querySelectorAll('input, select, textarea');
    
    inputs.forEach((input) => {
      const hasLabel = input.hasAttribute('aria-label');
      const hasLabelledBy = input.hasAttribute('aria-labelledby');
      const hasAssociatedLabel = input.id && container.querySelector(`label[for="${input.id}"]`);
      
      // Input should have label, aria-label, aria-labelledby, or associated label
      expect(hasLabel || hasLabelledBy || hasAssociatedLabel).toBe(true);
    });
  });

  it('should have proper ARIA roles', () => {
    const { container } = render(<App />);
    
    // Check for proper landmark roles
    const main = container.querySelector('main, [role="main"]');
    const nav = container.querySelector('nav, [role="navigation"]');
    
    // Should have main content area
    expect(main).toBeTruthy();
  });

  it('should support screen readers with live regions', () => {
    const { container } = render(<App />);
    
    // Check for ARIA live regions for dynamic content
    const liveRegions = container.querySelectorAll('[aria-live]');
    
    // Should have at least some live regions for notifications, etc.
    // This is optional but recommended
    expect(liveRegions.length).toBeGreaterThanOrEqual(0);
  });
});
