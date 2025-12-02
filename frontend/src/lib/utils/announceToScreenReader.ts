/**
 * Screen reader announcement utilities
 * Provides functions to announce dynamic content changes to screen readers
 */

/**
 * Announce a message to screen readers using aria-live region
 * @param message - The message to announce
 * @param priority - 'polite' (default) or 'assertive'
 */
export const announceToScreenReader = (
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
): void => {
  // Find or create the live region
  let liveRegion = document.getElementById(`aria-live-${priority}`);
  
  if (!liveRegion) {
    liveRegion = document.createElement('div');
    liveRegion.id = `aria-live-${priority}`;
    liveRegion.setAttribute('aria-live', priority);
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.setAttribute('role', priority === 'assertive' ? 'alert' : 'status');
    liveRegion.className = 'sr-only';
    liveRegion.style.cssText = `
      position: absolute;
      left: -10000px;
      width: 1px;
      height: 1px;
      overflow: hidden;
    `;
    document.body.appendChild(liveRegion);
  }

  // Clear previous message
  liveRegion.textContent = '';
  
  // Set new message after a brief delay to ensure screen readers pick it up
  setTimeout(() => {
    if (liveRegion) {
      liveRegion.textContent = message;
    }
  }, 100);
};

/**
 * Announce filter changes to screen readers
 */
export const announceFilterChange = (filterName: string, value: string, resultCount?: number): void => {
  const message = resultCount !== undefined
    ? `${filterName} filter set to ${value}. ${resultCount} results found.`
    : `${filterName} filter set to ${value}.`;
  announceToScreenReader(message, 'polite');
};

/**
 * Announce upload progress to screen readers
 */
export const announceUploadProgress = (fileName: string, progress: number, stage?: string): void => {
  const stageText = stage ? ` ${stage}` : '';
  const message = `${fileName}${stageText}: ${progress}% complete`;
  announceToScreenReader(message, 'polite');
};

/**
 * Announce batch selection changes
 */
export const announceBatchSelection = (selectedCount: number, totalCount?: number): void => {
  const message = totalCount !== undefined
    ? `${selectedCount} of ${totalCount} items selected`
    : `${selectedCount} items selected`;
  announceToScreenReader(message, 'polite');
};

/**
 * Announce navigation changes
 */
export const announceNavigation = (location: string): void => {
  announceToScreenReader(`Navigated to ${location}`, 'polite');
};

/**
 * Announce loading state
 */
export const announceLoading = (isLoading: boolean, context?: string): void => {
  const contextText = context ? ` ${context}` : '';
  const message = isLoading ? `Loading${contextText}...` : `Finished loading${contextText}`;
  announceToScreenReader(message, 'polite');
};

/**
 * Announce error messages
 */
export const announceError = (error: string): void => {
  announceToScreenReader(`Error: ${error}`, 'assertive');
};

/**
 * Announce success messages
 */
export const announceSuccess = (message: string): void => {
  announceToScreenReader(message, 'polite');
};
