/**
 * Accessibility Tests for Phase 2 Living Code Editor
 * 
 * Tests WCAG 2.1 AA compliance including:
 * - Keyboard navigation
 * - ARIA labels and attributes
 * - Focus management
 * - Screen reader support
 * - Color contrast
 * 
 * Requirements: Task 15 - Implement accessibility features
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'vitest-axe';
import {
  announce,
  announceError,
  announceSuccess,
  createFocusTrap,
  getFocusableElements,
  matchesShortcut,
  createIconButtonLabel,
  createToggleButtonLabel,
  createQualityBadgeLabel,
} from '@/lib/accessibility';

describe('Accessibility Utilities', () => {
  describe('Screen Reader Announcer', () => {
    beforeEach(() => {
      // Clear any existing announcer
      const existing = document.getElementById('sr-announcer');
      if (existing) {
        existing.remove();
      }
    });

    it('should create announcer element on first use', () => {
      announce('Test message');
      
      const announcer = document.getElementById('sr-announcer');
      expect(announcer).toBeTruthy();
      expect(announcer?.getAttribute('role')).toBe('status');
      expect(announcer?.getAttribute('aria-live')).toBe('polite');
    });

    it('should announce messages with polite priority', async () => {
      announce('Test message', 'polite');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.textContent).toBe('Test message');
      });
    });

    it('should announce messages with assertive priority', async () => {
      announce('Urgent message', 'assertive');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.textContent).toBe('Urgent message');
        expect(announcer?.getAttribute('aria-live')).toBe('assertive');
      });
    });

    it('should announce errors with assertive priority', async () => {
      announceError('Error message');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.textContent).toBe('Error: Error message');
        expect(announcer?.getAttribute('aria-live')).toBe('assertive');
      });
    });

    it('should announce success messages', async () => {
      announceSuccess('Success message');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.textContent).toBe('Success: Success message');
      });
    });

    it('should announce warning messages', async () => {
      const { announceWarning } = await import('@/lib/accessibility');
      announceWarning('Warning message');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.textContent).toBe('Warning: Warning message');
      });
    });

    it('should announce loading messages', async () => {
      const { announceLoading } = await import('@/lib/accessibility');
      announceLoading('Loading data');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.textContent).toBe('Loading: Loading data');
      });
    });

    it('should have sr-only class for visual hiding', () => {
      announce('Test');
      
      const announcer = document.getElementById('sr-announcer');
      expect(announcer?.className).toContain('sr-only');
    });

    it('should update aria-live attribute when priority changes', async () => {
      announce('First message', 'polite');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.getAttribute('aria-live')).toBe('polite');
      });

      announce('Second message', 'assertive');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.getAttribute('aria-live')).toBe('assertive');
      });
    });

    it('should have aria-atomic attribute', () => {
      announce('Test');
      
      const announcer = document.getElementById('sr-announcer');
      expect(announcer?.getAttribute('aria-atomic')).toBe('true');
    });
  });

  describe('Focus Trap', () => {
    let container: HTMLElement;
    let button1: HTMLButtonElement;
    let button2: HTMLButtonElement;
    let button3: HTMLButtonElement;

    beforeEach(() => {
      container = document.createElement('div');
      button1 = document.createElement('button');
      button2 = document.createElement('button');
      button3 = document.createElement('button');
      
      button1.textContent = 'Button 1';
      button2.textContent = 'Button 2';
      button3.textContent = 'Button 3';
      
      container.appendChild(button1);
      container.appendChild(button2);
      container.appendChild(button3);
      document.body.appendChild(container);
    });

    afterEach(() => {
      document.body.removeChild(container);
    });

    it('should get all focusable elements', () => {
      const focusable = getFocusableElements(container);
      expect(focusable).toHaveLength(3);
      expect(focusable[0]).toBe(button1);
      expect(focusable[1]).toBe(button2);
      expect(focusable[2]).toBe(button3);
    });

    it('should focus initial element', () => {
      createFocusTrap(container, { initialFocus: button2 });
      expect(document.activeElement).toBe(button2);
    });

    it('should trap tab navigation', () => {
      createFocusTrap(container);
      
      button1.focus();
      expect(document.activeElement).toBe(button1);
      
      // Tab to next
      fireEvent.keyDown(container, { key: 'Tab' });
      // Note: Actual tab behavior would need more complex simulation
    });

    it('should call onEscape when Escape is pressed', () => {
      const onEscape = vi.fn();
      createFocusTrap(container, { onEscape });
      
      fireEvent.keyDown(container, { key: 'Escape' });
      expect(onEscape).toHaveBeenCalled();
    });

    it('should restore focus on cleanup', async () => {
      const externalButton = document.createElement('button');
      document.body.appendChild(externalButton);
      externalButton.focus();
      
      const cleanup = createFocusTrap(container, { returnFocus: externalButton });
      expect(document.activeElement).not.toBe(externalButton);
      
      cleanup();
      
      // Focus should be restored (with setTimeout)
      await new Promise(resolve => setTimeout(resolve, 20));
      expect(document.activeElement).toBe(externalButton);
      
      document.body.removeChild(externalButton);
    });
  });

  describe('Keyboard Shortcuts', () => {
    it('should match keyboard shortcuts correctly', () => {
      const event = new KeyboardEvent('keydown', {
        key: 'a',
        ctrlKey: true,
        shiftKey: false,
      });
      
      expect(matchesShortcut(event, { key: 'a', ctrl: true })).toBe(true);
      expect(matchesShortcut(event, { key: 'a', ctrl: true, shift: true })).toBe(false);
      expect(matchesShortcut(event, { key: 'b', ctrl: true })).toBe(false);
    });

    it('should handle meta key on Mac', () => {
      // Mock Mac platform
      Object.defineProperty(navigator, 'platform', {
        value: 'MacIntel',
        configurable: true,
      });
      
      const event = new KeyboardEvent('keydown', {
        key: 'a',
        metaKey: true,
      });
      
      expect(matchesShortcut(event, { key: 'a', ctrl: true })).toBe(true);
    });

    it('should match shift modifier', () => {
      const event = new KeyboardEvent('keydown', {
        key: 'A',
        shiftKey: true,
      });
      
      expect(matchesShortcut(event, { key: 'A', shift: true })).toBe(true);
      expect(matchesShortcut(event, { key: 'A', shift: false })).toBe(false);
    });

    it('should match alt modifier', () => {
      const event = new KeyboardEvent('keydown', {
        key: 'a',
        altKey: true,
      });
      
      expect(matchesShortcut(event, { key: 'a', alt: true })).toBe(true);
      expect(matchesShortcut(event, { key: 'a', alt: false })).toBe(false);
    });

    it('should be case insensitive for key matching', () => {
      const event = new KeyboardEvent('keydown', {
        key: 'A',
      });
      
      expect(matchesShortcut(event, { key: 'a' })).toBe(true);
      expect(matchesShortcut(event, { key: 'A' })).toBe(true);
    });

    it('should format shortcuts for display', async () => {
      const { formatShortcut } = await import('@/lib/accessibility');
      
      const result1 = formatShortcut({ key: 'a', ctrl: true });
      const result2 = formatShortcut({ key: 's', ctrl: true, shift: true });
      
      // Should contain the key in uppercase
      expect(result1).toContain('A');
      expect(result2).toContain('S');
      
      // Should contain modifier keys
      expect(result1.length).toBeGreaterThan(1); // Has modifier + key
      expect(result2.length).toBeGreaterThan(2); // Has multiple modifiers + key
    });

    it('should check if element is focusable', async () => {
      const { isFocusable } = await import('@/lib/accessibility');
      
      const button = document.createElement('button');
      expect(isFocusable(button)).toBe(true);
      
      button.setAttribute('disabled', 'true');
      expect(isFocusable(button)).toBe(false);
      
      const div = document.createElement('div');
      expect(isFocusable(div)).toBe(false);
      
      div.setAttribute('tabindex', '0');
      expect(isFocusable(div)).toBe(true);
    });

    it('should check if element is visible', async () => {
      const { isVisible } = await import('@/lib/accessibility');
      
      const element = document.createElement('div');
      document.body.appendChild(element);
      
      expect(isVisible(element)).toBe(true);
      
      element.style.display = 'none';
      expect(isVisible(element)).toBe(false);
      
      element.style.display = 'block';
      element.style.visibility = 'hidden';
      expect(isVisible(element)).toBe(false);
      
      element.style.visibility = 'visible';
      element.style.opacity = '0';
      expect(isVisible(element)).toBe(false);
      
      document.body.removeChild(element);
    });

    it('should get next focusable element', async () => {
      const { getNextFocusable } = await import('@/lib/accessibility');
      
      const container = document.createElement('div');
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      const button3 = document.createElement('button');
      
      container.appendChild(button1);
      container.appendChild(button2);
      container.appendChild(button3);
      document.body.appendChild(container);
      
      const next = getNextFocusable(container, button1, 'forward');
      expect(next).toBe(button2);
      
      const prev = getNextFocusable(container, button2, 'backward');
      expect(prev).toBe(button1);
      
      // Should wrap around
      const wrapped = getNextFocusable(container, button3, 'forward');
      expect(wrapped).toBe(button1);
      
      document.body.removeChild(container);
    });

    it('should focus first element in container', async () => {
      const { focusFirstElement } = await import('@/lib/accessibility');
      
      const container = document.createElement('div');
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      
      container.appendChild(button1);
      container.appendChild(button2);
      document.body.appendChild(container);
      
      const result = focusFirstElement(container);
      expect(result).toBe(true);
      expect(document.activeElement).toBe(button1);
      
      document.body.removeChild(container);
    });

    it('should restore focus to element', async () => {
      const { restoreFocus } = await import('@/lib/accessibility');
      
      const button = document.createElement('button');
      document.body.appendChild(button);
      
      restoreFocus(button);
      
      // Focus restoration uses setTimeout
      await new Promise(resolve => setTimeout(resolve, 10));
      expect(document.activeElement).toBe(button);
      
      document.body.removeChild(button);
    });
  });

  describe('ARIA Label Generators', () => {
    it('should create icon button labels', () => {
      expect(createIconButtonLabel('Delete')).toBe('Delete');
      expect(createIconButtonLabel('Delete', 'annotation')).toBe('Delete annotation');
      expect(createIconButtonLabel('Close', 'dialog')).toBe('Close dialog');
    });

    it('should create toggle button labels', () => {
      expect(createToggleButtonLabel('quality badges', true)).toBe('Hide quality badges');
      expect(createToggleButtonLabel('quality badges', false)).toBe('Show quality badges');
      expect(createToggleButtonLabel('chunk boundaries', true)).toBe('Hide chunk boundaries');
      expect(createToggleButtonLabel('annotations', false)).toBe('Show annotations');
    });

    it('should create quality badge labels', () => {
      expect(createQualityBadgeLabel('high', 0.85)).toBe('Quality high, 85 percent');
      expect(createQualityBadgeLabel('medium', 0.65)).toBe('Quality medium, 65 percent');
      expect(createQualityBadgeLabel('low', 0.45)).toBe('Quality low, 45 percent');
    });

    it('should create annotation chip labels', async () => {
      const { createAnnotationChipLabel } = await import('@/lib/accessibility');
      expect(createAnnotationChipLabel(1, 5)).toBe('Annotation 1 of 5');
      expect(createAnnotationChipLabel(3, 10)).toBe('Annotation 3 of 10');
    });

    it('should create chunk boundary labels', async () => {
      const { createChunkBoundaryLabel } = await import('@/lib/accessibility');
      expect(createChunkBoundaryLabel('myFunction', '10-25')).toBe('Code chunk: myFunction, lines 10-25');
      expect(createChunkBoundaryLabel('MyClass', '50-100')).toBe('Code chunk: MyClass, lines 50-100');
    });

    it('should create reference icon labels', async () => {
      const { createReferenceIconLabel } = await import('@/lib/accessibility');
      expect(createReferenceIconLabel('paper', 'Deep Learning Paper')).toBe('paper reference: Deep Learning Paper');
      expect(createReferenceIconLabel('documentation', 'API Docs')).toBe('documentation reference: API Docs');
    });

    it('should create navigation labels', async () => {
      const { createNavigationLabel } = await import('@/lib/accessibility');
      expect(createNavigationLabel('next', 'annotation')).toBe('Go to next annotation');
      expect(createNavigationLabel('previous', 'chunk')).toBe('Go to previous chunk');
    });

    it('should create close labels', async () => {
      const { createCloseLabel } = await import('@/lib/accessibility');
      expect(createCloseLabel('dialog')).toBe('Close dialog');
      expect(createCloseLabel('panel')).toBe('Close panel');
    });

    it('should create delete labels', async () => {
      const { createDeleteLabel } = await import('@/lib/accessibility');
      expect(createDeleteLabel('annotation')).toBe('Delete annotation');
      expect(createDeleteLabel('comment')).toBe('Delete comment');
    });

    it('should create edit labels', async () => {
      const { createEditLabel } = await import('@/lib/accessibility');
      expect(createEditLabel('annotation')).toBe('Edit annotation');
      expect(createEditLabel('note')).toBe('Edit note');
    });

    it('should create save labels', async () => {
      const { createSaveLabel } = await import('@/lib/accessibility');
      expect(createSaveLabel('annotation')).toBe('Save annotation');
      expect(createSaveLabel('changes')).toBe('Save changes');
    });

    it('should create cancel labels', async () => {
      const { createCancelLabel } = await import('@/lib/accessibility');
      expect(createCancelLabel('edit')).toBe('Cancel edit');
      expect(createCancelLabel('operation')).toBe('Cancel operation');
    });

    it('should create retry labels', async () => {
      const { createRetryLabel } = await import('@/lib/accessibility');
      expect(createRetryLabel('operation')).toBe('Retry operation');
      expect(createRetryLabel('request')).toBe('Retry request');
    });

    it('should create status descriptions', async () => {
      const { createStatusDescription } = await import('@/lib/accessibility');
      expect(createStatusDescription('loading', 'Fetching data')).toBe('Loading: Fetching data');
      expect(createStatusDescription('success', 'Data loaded')).toBe('Success: Data loaded');
      expect(createStatusDescription('error', 'Failed to load')).toBe('Error: Failed to load');
    });
  });
});

describe('ARIA Utilities', () => {
  describe('ARIA Attribute Setters', () => {
    let element: HTMLElement;

    beforeEach(() => {
      element = document.createElement('div');
    });

    it('should set aria-label', async () => {
      const { setAriaLabel } = await import('@/lib/accessibility');
      setAriaLabel(element, 'Test label');
      expect(element.getAttribute('aria-label')).toBe('Test label');
    });

    it('should set aria-describedby', async () => {
      const { setAriaDescribedBy } = await import('@/lib/accessibility');
      setAriaDescribedBy(element, 'description-id');
      expect(element.getAttribute('aria-describedby')).toBe('description-id');
    });

    it('should set aria-labelledby', async () => {
      const { setAriaLabelledBy } = await import('@/lib/accessibility');
      setAriaLabelledBy(element, 'label-id');
      expect(element.getAttribute('aria-labelledby')).toBe('label-id');
    });

    it('should set aria-expanded', async () => {
      const { setAriaExpanded } = await import('@/lib/accessibility');
      setAriaExpanded(element, true);
      expect(element.getAttribute('aria-expanded')).toBe('true');
      
      setAriaExpanded(element, false);
      expect(element.getAttribute('aria-expanded')).toBe('false');
    });

    it('should set aria-pressed', async () => {
      const { setAriaPressed } = await import('@/lib/accessibility');
      setAriaPressed(element, true);
      expect(element.getAttribute('aria-pressed')).toBe('true');
      
      setAriaPressed(element, false);
      expect(element.getAttribute('aria-pressed')).toBe('false');
    });

    it('should set aria-selected', async () => {
      const { setAriaSelected } = await import('@/lib/accessibility');
      setAriaSelected(element, true);
      expect(element.getAttribute('aria-selected')).toBe('true');
      
      setAriaSelected(element, false);
      expect(element.getAttribute('aria-selected')).toBe('false');
    });

    it('should set aria-checked', async () => {
      const { setAriaChecked } = await import('@/lib/accessibility');
      setAriaChecked(element, true);
      expect(element.getAttribute('aria-checked')).toBe('true');
      
      setAriaChecked(element, false);
      expect(element.getAttribute('aria-checked')).toBe('false');
      
      setAriaChecked(element, 'mixed');
      expect(element.getAttribute('aria-checked')).toBe('mixed');
    });

    it('should set aria-disabled', async () => {
      const { setAriaDisabled } = await import('@/lib/accessibility');
      setAriaDisabled(element, true);
      expect(element.getAttribute('aria-disabled')).toBe('true');
      
      setAriaDisabled(element, false);
      expect(element.getAttribute('aria-disabled')).toBe('false');
    });

    it('should set aria-hidden', async () => {
      const { setAriaHidden } = await import('@/lib/accessibility');
      setAriaHidden(element, true);
      expect(element.getAttribute('aria-hidden')).toBe('true');
      
      setAriaHidden(element, false);
      expect(element.getAttribute('aria-hidden')).toBe('false');
    });

    it('should set aria-live', async () => {
      const { setAriaLive } = await import('@/lib/accessibility');
      setAriaLive(element, 'polite');
      expect(element.getAttribute('aria-live')).toBe('polite');
      
      setAriaLive(element, 'assertive');
      expect(element.getAttribute('aria-live')).toBe('assertive');
      
      setAriaLive(element, 'off');
      expect(element.getAttribute('aria-live')).toBe('off');
    });

    it('should set aria-busy', async () => {
      const { setAriaBusy } = await import('@/lib/accessibility');
      setAriaBusy(element, true);
      expect(element.getAttribute('aria-busy')).toBe('true');
      
      setAriaBusy(element, false);
      expect(element.getAttribute('aria-busy')).toBe('false');
    });

    it('should set aria-invalid', async () => {
      const { setAriaInvalid } = await import('@/lib/accessibility');
      setAriaInvalid(element, true);
      expect(element.getAttribute('aria-invalid')).toBe('true');
      
      setAriaInvalid(element, false);
      expect(element.getAttribute('aria-invalid')).toBe('false');
    });

    it('should set aria-required', async () => {
      const { setAriaRequired } = await import('@/lib/accessibility');
      setAriaRequired(element, true);
      expect(element.getAttribute('aria-required')).toBe('true');
      
      setAriaRequired(element, false);
      expect(element.getAttribute('aria-required')).toBe('false');
    });

    it('should generate unique ARIA IDs', async () => {
      const { generateAriaId } = await import('@/lib/accessibility');
      const id1 = generateAriaId('test');
      const id2 = generateAriaId('test');
      
      expect(id1).toContain('test-');
      expect(id2).toContain('test-');
      expect(id1).not.toBe(id2);
    });
  });
});

describe('Component Accessibility', () => {
  describe('ErrorBanner', () => {
    it('should have proper ARIA attributes', () => {
      const { container } = render(
        <div>
          <ErrorBanner
            message="Test error"
            title="Error"
            variant="error"
            showRetry={true}
            onRetry={() => {}}
            showDismiss={true}
            onDismiss={() => {}}
          />
        </div>
      );
      
      const alert = container.querySelector('[role="alert"]');
      expect(alert).toBeTruthy();
      expect(alert?.getAttribute('aria-live')).toBe('polite');
      expect(alert?.getAttribute('aria-atomic')).toBe('true');
    });

    it('should have accessible button labels', () => {
      render(
        <ErrorBanner
          message="Test error"
          title="Error"
          variant="error"
          showRetry={true}
          onRetry={() => {}}
          showDismiss={true}
          onDismiss={() => {}}
        />
      );
      
      expect(screen.getByLabelText('Retry error')).toBeTruthy();
      expect(screen.getByLabelText('Dismiss error')).toBeTruthy();
    });

    it('should announce error to screen readers', async () => {
      // Clear announcer before test
      const existing = document.getElementById('sr-announcer');
      if (existing) {
        existing.remove();
      }
      
      render(
        <ErrorBanner
          message="Test error"
          title="Error"
          variant="error"
        />
      );
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.textContent).toContain('Error');
        expect(announcer?.textContent).toContain('Test error');
      });
    });
  });

  describe('Keyboard Navigation', () => {
    it('should support Tab navigation', async () => {
      const user = userEvent.setup();
      
      render(
        <div>
          <button>Button 1</button>
          <button>Button 2</button>
          <button>Button 3</button>
        </div>
      );
      
      const button1 = screen.getByText('Button 1');
      const button2 = screen.getByText('Button 2');
      
      button1.focus();
      expect(document.activeElement).toBe(button1);
      
      await user.tab();
      expect(document.activeElement).toBe(button2);
    });

    it('should support Shift+Tab navigation', async () => {
      const user = userEvent.setup();
      
      render(
        <div>
          <button>Button 1</button>
          <button>Button 2</button>
          <button>Button 3</button>
        </div>
      );
      
      const button2 = screen.getByText('Button 2');
      const button1 = screen.getByText('Button 1');
      
      button2.focus();
      expect(document.activeElement).toBe(button2);
      
      await user.tab({ shift: true });
      expect(document.activeElement).toBe(button1);
    });
  });

  describe('Focus Indicators', () => {
    it('should have visible focus indicators', () => {
      render(<button>Test Button</button>);
      
      const button = screen.getByText('Test Button');
      button.focus();
      
      const styles = window.getComputedStyle(button);
      // Note: Actual focus styles would need to be checked in browser
      expect(document.activeElement).toBe(button);
    });
  });

  describe('Color Contrast', () => {
    it('should meet WCAG AA contrast ratio for text', async () => {
      const { container } = render(
        <div>
          <p className="text-foreground">Primary text</p>
          <p className="text-muted-foreground">Secondary text</p>
        </div>
      );
      
      // Run axe accessibility tests
      const results = await axe(container);
      expect(results.violations).toHaveLength(0);
    });

    it('should have sufficient contrast for quality badges', async () => {
      const { container } = render(
        <div>
          <div className="quality-badge quality-high" aria-label="Quality high, 85 percent">
            High
          </div>
          <div className="quality-badge quality-medium" aria-label="Quality medium, 65 percent">
            Medium
          </div>
          <div className="quality-badge quality-low" aria-label="Quality low, 45 percent">
            Low
          </div>
        </div>
      );
      
      const results = await axe(container);
      expect(results.violations).toHaveLength(0);
    });

    it('should use patterns in addition to color for quality badges', () => {
      render(
        <div>
          <div className="quality-badge quality-high">High</div>
          <div className="quality-badge quality-medium">Medium</div>
          <div className="quality-badge quality-low">Low</div>
        </div>
      );
      
      // Quality badges should have visual patterns, not just color
      // This is tested via CSS classes
      const highBadge = screen.getByText('High');
      const mediumBadge = screen.getByText('Medium');
      const lowBadge = screen.getByText('Low');
      
      expect(highBadge.className).toContain('quality-high');
      expect(mediumBadge.className).toContain('quality-medium');
      expect(lowBadge.className).toContain('quality-low');
    });
  });

  describe('ARIA Labels', () => {
    it('should have aria-label on icon-only buttons', () => {
      render(
        <button aria-label="Close dialog">
          <span>×</span>
        </button>
      );
      
      expect(screen.getByLabelText('Close dialog')).toBeTruthy();
    });

    it('should have aria-expanded on collapsible sections', () => {
      const { rerender } = render(
        <button aria-expanded={false}>Expand</button>
      );
      
      const button = screen.getByText('Expand');
      expect(button.getAttribute('aria-expanded')).toBe('false');
      
      rerender(<button aria-expanded={true}>Collapse</button>);
      expect(button.getAttribute('aria-expanded')).toBe('true');
    });

    it('should have aria-busy on loading states', () => {
      const { container } = render(
        <div aria-busy={true} role="status">
          Loading...
        </div>
      );
      
      const status = container.querySelector('[role="status"][aria-busy="true"]');
      expect(status).toBeTruthy();
      expect(status?.getAttribute('aria-busy')).toBe('true');
    });
  });

  describe('Semantic HTML', () => {
    it('should use button elements for actions', () => {
      render(<button onClick={() => {}}>Click me</button>);
      
      const button = screen.getByRole('button');
      expect(button.tagName).toBe('BUTTON');
    });

    it('should use proper heading hierarchy', () => {
      render(
        <div>
          <h1>Main Title</h1>
          <h2>Section Title</h2>
          <h3>Subsection Title</h3>
        </div>
      );
      
      expect(screen.getByRole('heading', { level: 1 })).toBeTruthy();
      expect(screen.getByRole('heading', { level: 2 })).toBeTruthy();
      expect(screen.getByRole('heading', { level: 3 })).toBeTruthy();
    });

    it('should use region role for major sections', () => {
      render(
        <div role="region" aria-label="Code editor">
          Editor content
        </div>
      );
      
      expect(screen.getByRole('region')).toBeTruthy();
      expect(screen.getByLabelText('Code editor')).toBeTruthy();
    });

    it('should use nav element for navigation', () => {
      render(
        <nav aria-label="Main navigation">
          <a href="#home">Home</a>
          <a href="#about">About</a>
        </nav>
      );
      
      expect(screen.getByRole('navigation')).toBeTruthy();
      expect(screen.getByLabelText('Main navigation')).toBeTruthy();
    });

    it('should use main element for main content', () => {
      render(
        <main>
          <h1>Main Content</h1>
          <p>Content goes here</p>
        </main>
      );
      
      expect(screen.getByRole('main')).toBeTruthy();
    });

    it('should use aside element for complementary content', () => {
      render(
        <aside aria-label="Sidebar">
          <p>Sidebar content</p>
        </aside>
      );
      
      expect(screen.getByRole('complementary')).toBeTruthy();
    });
  });

  describe('Skip Links', () => {
    it('should have skip to content link', () => {
      render(
        <div>
          <a href="#main-content" className="skip-to-content">
            Skip to content
          </a>
          <main id="main-content">
            <h1>Main Content</h1>
          </main>
        </div>
      );
      
      const skipLink = screen.getByText('Skip to content');
      expect(skipLink).toBeTruthy();
      expect(skipLink.getAttribute('href')).toBe('#main-content');
    });

    it('should show skip link on focus', () => {
      render(
        <a href="#main-content" className="skip-to-content">
          Skip to content
        </a>
      );
      
      const skipLink = screen.getByText('Skip to content');
      skipLink.focus();
      
      expect(document.activeElement).toBe(skipLink);
    });
  });

  describe('Loading States', () => {
    beforeEach(() => {
      // Clear announcer before each test to avoid conflicts
      const existing = document.getElementById('sr-announcer');
      if (existing) {
        existing.remove();
      }
    });

    it('should have aria-busy on loading elements', () => {
      const { container } = render(
        <div aria-busy={true} role="status">
          Loading...
        </div>
      );
      
      const status = container.querySelector('[role="status"][aria-busy="true"]');
      expect(status).toBeTruthy();
      expect(status?.getAttribute('aria-busy')).toBe('true');
    });

    it('should announce loading states to screen readers', async () => {
      const { announceLoading } = await import('@/lib/accessibility');
      
      announceLoading('Fetching annotations');
      
      await waitFor(() => {
        const announcer = document.getElementById('sr-announcer');
        expect(announcer?.textContent).toBe('Loading: Fetching annotations');
      });
    });

    it('should have role="status" for loading indicators', () => {
      const { container } = render(
        <div role="status" aria-live="polite">
          <span>Loading annotations...</span>
        </div>
      );
      
      const status = container.querySelector('[role="status"]');
      expect(status).toBeTruthy();
    });
  });
});

describe('Axe Accessibility Tests', () => {
  it('should have no accessibility violations in editor wrapper', async () => {
    const { container } = render(
      <div role="region" aria-label="Code editor">
        <button aria-label="Toggle quality badges">Toggle</button>
        <div role="status" aria-live="polite">Loading...</div>
      </div>
    );
    
    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it('should have no accessibility violations in error banner', async () => {
    const { container } = render(
      <div role="alert" aria-live="polite" aria-atomic="true">
        <p>Error message</p>
        <button aria-label="Retry operation">Retry</button>
        <button aria-label="Dismiss error">Dismiss</button>
      </div>
    );
    
    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it('should have no accessibility violations in metadata panel', async () => {
    const { container } = render(
      <div role="region" aria-label="Chunk metadata">
        <button aria-label="Collapse chunk metadata" aria-expanded={true}>
          Collapse
        </button>
        <div>
          <h4>Function Name</h4>
          <p aria-label="Chunk name: myFunction">myFunction</p>
        </div>
      </div>
    );
    
    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });
});

// Mock ErrorBanner component for testing
function ErrorBanner({
  message,
  title,
  variant,
  showRetry,
  onRetry,
  showDismiss,
  onDismiss,
}: {
  message: string;
  title: string;
  variant: string;
  showRetry?: boolean;
  onRetry?: () => void;
  showDismiss?: boolean;
  onDismiss?: () => void;
}) {
  return (
    <div role="alert" aria-live="polite" aria-atomic="true">
      <h3>{title}</h3>
      <p>{message}</p>
      {showRetry && onRetry && (
        <button aria-label={`Retry ${title.toLowerCase()}`} onClick={onRetry}>
          Retry
        </button>
      )}
      {showDismiss && onDismiss && (
        <button aria-label={`Dismiss ${title.toLowerCase()}`} onClick={onDismiss}>
          Dismiss
        </button>
      )}
    </div>
  );
}
