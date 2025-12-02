/**
 * Focus management utilities for accessibility
 */

/**
 * Get all focusable elements within a container
 */
export const getFocusableElements = (container: HTMLElement): HTMLElement[] => {
  const focusableSelectors = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
  ].join(', ');

  return Array.from(container.querySelectorAll<HTMLElement>(focusableSelectors));
};

/**
 * Trap focus within a container (useful for modals/dialogs)
 */
export const trapFocus = (container: HTMLElement): (() => void) => {
  const focusableElements = getFocusableElements(container);
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable?.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable?.focus();
      }
    }
  };

  container.addEventListener('keydown', handleKeyDown);

  // Focus first element
  firstFocusable?.focus();

  // Return cleanup function
  return () => {
    container.removeEventListener('keydown', handleKeyDown);
  };
};

/**
 * Save and restore focus (useful when opening/closing modals)
 */
export class FocusManager {
  private previouslyFocused: HTMLElement | null = null;

  /**
   * Save the currently focused element
   */
  saveFocus(): void {
    this.previouslyFocused = document.activeElement as HTMLElement;
  }

  /**
   * Restore focus to the previously focused element
   */
  restoreFocus(): void {
    if (this.previouslyFocused && typeof this.previouslyFocused.focus === 'function') {
      this.previouslyFocused.focus();
    }
    this.previouslyFocused = null;
  }
}

/**
 * Move focus to an element with optional scroll behavior
 */
export const moveFocusTo = (
  element: HTMLElement | null,
  options?: {
    preventScroll?: boolean;
    scrollBehavior?: ScrollBehavior;
  }
): void => {
  if (!element) return;

  element.focus({ preventScroll: options?.preventScroll });

  if (!options?.preventScroll && options?.scrollBehavior) {
    element.scrollIntoView({ behavior: options.scrollBehavior, block: 'nearest' });
  }
};

/**
 * Create a focus indicator style that meets WCAG requirements
 * 2px outline with 2px offset
 */
export const FOCUS_VISIBLE_STYLES = {
  outline: '2px solid var(--color-primary, #3b82f6)',
  outlineOffset: '2px',
  borderRadius: '4px',
} as const;

/**
 * CSS class for screen reader only content
 */
export const SR_ONLY_CLASS = 'sr-only';

/**
 * Ensure an element is visible to screen readers but hidden visually
 */
export const makeSROnly = (element: HTMLElement): void => {
  element.style.cssText = `
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  `;
};
