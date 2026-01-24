/**
 * Screen Reader Announcer Utility
 * 
 * Provides functions to announce status updates to screen readers
 * using ARIA live regions.
 * 
 * Requirements: Accessibility - Screen reader support
 */

/**
 * Announce a message to screen readers
 * @param message - The message to announce
 * @param priority - The priority level ('polite' or 'assertive')
 */
export function announce(message: string, priority: 'polite' | 'assertive' = 'polite'): void {
  // Get or create the announcer element
  let announcer = document.getElementById('sr-announcer');
  
  if (!announcer) {
    announcer = document.createElement('div');
    announcer.id = 'sr-announcer';
    announcer.setAttribute('role', 'status');
    announcer.setAttribute('aria-live', priority);
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    announcer.style.cssText = `
      position: absolute;
      left: -10000px;
      width: 1px;
      height: 1px;
      overflow: hidden;
    `;
    document.body.appendChild(announcer);
  }
  
  // Update the aria-live attribute if priority changed
  if (announcer.getAttribute('aria-live') !== priority) {
    announcer.setAttribute('aria-live', priority);
  }
  
  // Clear and set the message
  announcer.textContent = '';
  
  // Use setTimeout to ensure the screen reader picks up the change
  setTimeout(() => {
    if (announcer) {
      announcer.textContent = message;
    }
  }, 100);
}

/**
 * Announce an error message to screen readers
 * @param message - The error message to announce
 */
export function announceError(message: string): void {
  announce(`Error: ${message}`, 'assertive');
}

/**
 * Announce a success message to screen readers
 * @param message - The success message to announce
 */
export function announceSuccess(message: string): void {
  announce(`Success: ${message}`, 'polite');
}

/**
 * Announce a warning message to screen readers
 * @param message - The warning message to announce
 */
export function announceWarning(message: string): void {
  announce(`Warning: ${message}`, 'polite');
}

/**
 * Announce a loading state to screen readers
 * @param message - The loading message to announce
 */
export function announceLoading(message: string): void {
  announce(`Loading: ${message}`, 'polite');
}

/**
 * Clear the announcer
 */
export function clearAnnouncer(): void {
  const announcer = document.getElementById('sr-announcer');
  if (announcer) {
    announcer.textContent = '';
  }
}
