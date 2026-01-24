/**
 * Keyboard Navigation Utilities
 * 
 * Provides utilities for keyboard navigation and shortcuts.
 * 
 * Requirements: Accessibility - Keyboard navigation
 */

/**
 * Check if an element is focusable
 */
export function isFocusable(element: HTMLElement): boolean {
  if (element.hasAttribute('disabled')) return false;
  if (element.getAttribute('tabindex') === '-1') return false;
  
  const focusableElements = [
    'A',
    'BUTTON',
    'INPUT',
    'SELECT',
    'TEXTAREA',
  ];
  
  if (focusableElements.includes(element.tagName)) return true;
  if (element.hasAttribute('tabindex')) return true;
  
  return false;
}

/**
 * Get the next focusable element in a container
 */
export function getNextFocusable(
  container: HTMLElement,
  current: HTMLElement,
  direction: 'forward' | 'backward' = 'forward'
): HTMLElement | null {
  const focusableElements = Array.from(
    container.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  );
  
  const currentIndex = focusableElements.indexOf(current);
  if (currentIndex === -1) return null;
  
  if (direction === 'forward') {
    return focusableElements[currentIndex + 1] || focusableElements[0];
  } else {
    return focusableElements[currentIndex - 1] || focusableElements[focusableElements.length - 1];
  }
}

/**
 * Check if a keyboard event matches a shortcut
 */
export function matchesShortcut(
  event: KeyboardEvent,
  shortcut: {
    key: string;
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
    meta?: boolean;
  }
): boolean {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const modKey = isMac ? event.metaKey : event.ctrlKey;
  
  // Check key
  if (event.key.toLowerCase() !== shortcut.key.toLowerCase()) return false;
  
  // Check modifiers
  if (shortcut.ctrl !== undefined && modKey !== shortcut.ctrl) return false;
  if (shortcut.shift !== undefined && event.shiftKey !== shortcut.shift) return false;
  if (shortcut.alt !== undefined && event.altKey !== shortcut.alt) return false;
  if (shortcut.meta !== undefined && event.metaKey !== shortcut.meta) return false;
  
  return true;
}

/**
 * Format a keyboard shortcut for display
 */
export function formatShortcut(shortcut: {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
}): string {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const parts: string[] = [];
  
  if (shortcut.ctrl) parts.push(isMac ? '⌘' : 'Ctrl');
  if (shortcut.shift) parts.push(isMac ? '⇧' : 'Shift');
  if (shortcut.alt) parts.push(isMac ? '⌥' : 'Alt');
  if (shortcut.meta && !isMac) parts.push('Meta');
  
  parts.push(shortcut.key.toUpperCase());
  
  return parts.join(isMac ? '' : '+');
}

/**
 * Prevent default behavior for keyboard events
 */
export function preventDefaultKeys(
  event: KeyboardEvent,
  keys: string[]
): boolean {
  if (keys.includes(event.key)) {
    event.preventDefault();
    return true;
  }
  return false;
}

/**
 * Check if an element is visible and not hidden
 */
export function isVisible(element: HTMLElement): boolean {
  if (!element) return false;
  
  const style = window.getComputedStyle(element);
  if (style.display === 'none') return false;
  if (style.visibility === 'hidden') return false;
  if (parseFloat(style.opacity) === 0) return false;
  
  return true;
}

/**
 * Focus the first focusable element in a container
 */
export function focusFirstElement(container: HTMLElement): boolean {
  const focusableElements = Array.from(
    container.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  );
  
  for (const element of focusableElements) {
    if (isVisible(element)) {
      element.focus();
      return true;
    }
  }
  
  return false;
}

/**
 * Restore focus to a previously focused element
 */
export function restoreFocus(element: HTMLElement | null): void {
  if (element && typeof element.focus === 'function') {
    // Use setTimeout to ensure the element is ready to receive focus
    setTimeout(() => {
      element?.focus();
    }, 0);
  }
}
