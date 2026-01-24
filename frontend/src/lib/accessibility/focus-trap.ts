/**
 * Focus Trap Utility
 * 
 * Provides utilities for trapping focus within modals and popovers
 * to ensure keyboard navigation stays within the active component.
 * 
 * Requirements: Accessibility - Focus management
 */

/**
 * Get all focusable elements within a container
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const focusableSelectors = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(', ');
  
  return Array.from(container.querySelectorAll<HTMLElement>(focusableSelectors));
}

/**
 * Create a focus trap within a container
 * @param container - The container element to trap focus within
 * @param options - Configuration options
 * @returns A function to release the focus trap
 */
export function createFocusTrap(
  container: HTMLElement,
  options: {
    initialFocus?: HTMLElement;
    returnFocus?: HTMLElement;
    onEscape?: () => void;
  } = {}
): () => void {
  const { initialFocus, returnFocus, onEscape } = options;
  
  // Store the previously focused element
  const previouslyFocused = returnFocus || (document.activeElement as HTMLElement);
  
  // Get all focusable elements
  const focusableElements = getFocusableElements(container);
  
  if (focusableElements.length === 0) {
    console.warn('No focusable elements found in focus trap container');
    return () => {};
  }
  
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];
  
  // Focus the initial element or the first focusable element
  if (initialFocus && focusableElements.includes(initialFocus)) {
    initialFocus.focus();
  } else {
    firstFocusable.focus();
  }
  
  // Handle keyboard events
  const handleKeyDown = (e: KeyboardEvent) => {
    // Handle Escape key
    if (e.key === 'Escape' && onEscape) {
      e.preventDefault();
      onEscape();
      return;
    }
    
    // Handle Tab key
    if (e.key === 'Tab') {
      // Get current focusable elements (in case they changed)
      const currentFocusable = getFocusableElements(container);
      
      if (currentFocusable.length === 0) return;
      
      const currentFirst = currentFocusable[0];
      const currentLast = currentFocusable[currentFocusable.length - 1];
      
      // Shift + Tab (backwards)
      if (e.shiftKey) {
        if (document.activeElement === currentFirst) {
          e.preventDefault();
          currentLast.focus();
        }
      }
      // Tab (forwards)
      else {
        if (document.activeElement === currentLast) {
          e.preventDefault();
          currentFirst.focus();
        }
      }
    }
  };
  
  // Add event listener
  container.addEventListener('keydown', handleKeyDown);
  
  // Return cleanup function
  return () => {
    container.removeEventListener('keydown', handleKeyDown);
    
    // Restore focus to previously focused element
    if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
      previouslyFocused.focus();
    }
  };
}

/**
 * React hook for focus trap
 */
export function useFocusTrap(
  containerRef: React.RefObject<HTMLElement>,
  isActive: boolean,
  options: {
    initialFocus?: HTMLElement;
    returnFocus?: HTMLElement;
    onEscape?: () => void;
  } = {}
): void {
  const { initialFocus, returnFocus, onEscape } = options;
  
  React.useEffect(() => {
    if (!isActive || !containerRef.current) return;
    
    const cleanup = createFocusTrap(containerRef.current, {
      initialFocus,
      returnFocus,
      onEscape,
    });
    
    return cleanup;
  }, [isActive, containerRef, initialFocus, returnFocus, onEscape]);
}

// Export React for the hook
import * as React from 'react';
