/**
 * useFocusTrap hook for modal focus management
 * Implements WCAG 2.1 focus trap pattern for accessible modals and dialogs
 */

import { useEffect, RefObject } from 'react';

/**
 * Selector for all focusable elements
 */
const FOCUSABLE_ELEMENTS_SELECTOR = [
  'a[href]',
  'button:not([disabled])',
  'textarea:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ');

/**
 * Options for focus trap behavior
 */
export interface FocusTrapOptions {
  /** Whether to auto-focus the first element when trap activates (default: true) */
  autoFocus?: boolean;
  /** Whether to restore focus to the previous element when trap deactivates (default: true) */
  restoreFocus?: boolean;
  /** Element to focus initially (overrides autoFocus behavior) */
  initialFocusElement?: HTMLElement | null;
}

/**
 * Custom hook for trapping focus within a container element
 * Useful for modals, dialogs, and other overlay components
 * 
 * @param ref - React ref to the container element
 * @param isActive - Whether the focus trap is active
 * @param options - Additional options for focus trap behavior
 * 
 * @example
 * const modalRef = useRef<HTMLDivElement>(null);
 * useFocusTrap(modalRef, isOpen);
 * 
 * return (
 *   <div ref={modalRef} role="dialog">
 *     <button>First focusable</button>
 *     <input type="text" />
 *     <button>Last focusable</button>
 *   </div>
 * );
 */
export function useFocusTrap(
  ref: RefObject<HTMLElement>,
  isActive: boolean,
  options: FocusTrapOptions = {}
): void {
  const {
    autoFocus = true,
    restoreFocus = true,
    initialFocusElement = null,
  } = options;

  useEffect(() => {
    // Only activate trap when isActive is true and ref is available
    if (!isActive || !ref.current) {
      return;
    }

    const container = ref.current;
    
    // Store the element that had focus before the trap activated
    const previouslyFocusedElement = document.activeElement as HTMLElement;

    // Get all focusable elements within the container
    const getFocusableElements = (): HTMLElement[] => {
      const elements = container.querySelectorAll<HTMLElement>(FOCUSABLE_ELEMENTS_SELECTOR);
      return Array.from(elements).filter(
        (element) => !element.hasAttribute('disabled') && element.offsetParent !== null
      );
    };

    // Focus the first element or specified initial element
    if (autoFocus || initialFocusElement) {
      const elementToFocus = initialFocusElement || getFocusableElements()[0];
      if (elementToFocus) {
        // Use setTimeout to ensure the element is rendered and focusable
        setTimeout(() => {
          elementToFocus.focus();
        }, 0);
      }
    }

    // Handle Tab key to cycle focus within the container
    const handleTab = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') {
        return;
      }

      const focusableElements = getFocusableElements();
      
      // If no focusable elements, prevent tabbing
      if (focusableElements.length === 0) {
        event.preventDefault();
        return;
      }

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];
      const activeElement = document.activeElement as HTMLElement;

      // Shift + Tab: moving backwards
      if (event.shiftKey) {
        if (activeElement === firstElement || !container.contains(activeElement)) {
          event.preventDefault();
          lastElement.focus();
        }
      } 
      // Tab: moving forwards
      else {
        if (activeElement === lastElement || !container.contains(activeElement)) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };

    // Attach event listener
    document.addEventListener('keydown', handleTab);

    // Cleanup function
    return () => {
      document.removeEventListener('keydown', handleTab);
      
      // Restore focus to the previously focused element
      if (restoreFocus && previouslyFocusedElement && previouslyFocusedElement.focus) {
        previouslyFocusedElement.focus();
      }
    };
  }, [ref, isActive, autoFocus, restoreFocus, initialFocusElement]);
}
