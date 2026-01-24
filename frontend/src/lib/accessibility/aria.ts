/**
 * ARIA Utilities
 * 
 * Provides utilities for managing ARIA attributes and labels.
 * 
 * Requirements: Accessibility - ARIA labels and attributes
 */

/**
 * Generate a unique ID for ARIA relationships
 */
let idCounter = 0;
export function generateAriaId(prefix: string = 'aria'): string {
  return `${prefix}-${Date.now()}-${++idCounter}`;
}

/**
 * Set ARIA label on an element
 */
export function setAriaLabel(element: HTMLElement, label: string): void {
  element.setAttribute('aria-label', label);
}

/**
 * Set ARIA described by on an element
 */
export function setAriaDescribedBy(element: HTMLElement, id: string): void {
  element.setAttribute('aria-describedby', id);
}

/**
 * Set ARIA labelled by on an element
 */
export function setAriaLabelledBy(element: HTMLElement, id: string): void {
  element.setAttribute('aria-labelledby', id);
}

/**
 * Set ARIA expanded state
 */
export function setAriaExpanded(element: HTMLElement, expanded: boolean): void {
  element.setAttribute('aria-expanded', String(expanded));
}

/**
 * Set ARIA pressed state
 */
export function setAriaPressed(element: HTMLElement, pressed: boolean): void {
  element.setAttribute('aria-pressed', String(pressed));
}

/**
 * Set ARIA selected state
 */
export function setAriaSelected(element: HTMLElement, selected: boolean): void {
  element.setAttribute('aria-selected', String(selected));
}

/**
 * Set ARIA checked state
 */
export function setAriaChecked(element: HTMLElement, checked: boolean | 'mixed'): void {
  element.setAttribute('aria-checked', String(checked));
}

/**
 * Set ARIA disabled state
 */
export function setAriaDisabled(element: HTMLElement, disabled: boolean): void {
  element.setAttribute('aria-disabled', String(disabled));
}

/**
 * Set ARIA hidden state
 */
export function setAriaHidden(element: HTMLElement, hidden: boolean): void {
  element.setAttribute('aria-hidden', String(hidden));
}

/**
 * Set ARIA live region
 */
export function setAriaLive(
  element: HTMLElement,
  level: 'off' | 'polite' | 'assertive'
): void {
  element.setAttribute('aria-live', level);
}

/**
 * Set ARIA busy state
 */
export function setAriaBusy(element: HTMLElement, busy: boolean): void {
  element.setAttribute('aria-busy', String(busy));
}

/**
 * Set ARIA invalid state
 */
export function setAriaInvalid(element: HTMLElement, invalid: boolean): void {
  element.setAttribute('aria-invalid', String(invalid));
}

/**
 * Set ARIA required state
 */
export function setAriaRequired(element: HTMLElement, required: boolean): void {
  element.setAttribute('aria-required', String(required));
}

/**
 * Create ARIA label for icon-only button
 */
export function createIconButtonLabel(action: string, context?: string): string {
  if (context) {
    return `${action} ${context}`;
  }
  return action;
}

/**
 * Create ARIA label for toggle button
 */
export function createToggleButtonLabel(
  feature: string,
  isEnabled: boolean
): string {
  return `${isEnabled ? 'Hide' : 'Show'} ${feature}`;
}

/**
 * Create ARIA label for navigation button
 */
export function createNavigationLabel(
  direction: 'next' | 'previous',
  item: string
): string {
  return `Go to ${direction} ${item}`;
}

/**
 * Create ARIA label for close button
 */
export function createCloseLabel(context: string): string {
  return `Close ${context}`;
}

/**
 * Create ARIA label for delete button
 */
export function createDeleteLabel(item: string): string {
  return `Delete ${item}`;
}

/**
 * Create ARIA label for edit button
 */
export function createEditLabel(item: string): string {
  return `Edit ${item}`;
}

/**
 * Create ARIA label for save button
 */
export function createSaveLabel(item: string): string {
  return `Save ${item}`;
}

/**
 * Create ARIA label for cancel button
 */
export function createCancelLabel(action: string): string {
  return `Cancel ${action}`;
}

/**
 * Create ARIA label for retry button
 */
export function createRetryLabel(action: string): string {
  return `Retry ${action}`;
}

/**
 * Create ARIA description for status
 */
export function createStatusDescription(
  status: 'loading' | 'success' | 'error',
  message: string
): string {
  const prefix = {
    loading: 'Loading:',
    success: 'Success:',
    error: 'Error:',
  }[status];
  
  return `${prefix} ${message}`;
}

/**
 * Create ARIA label for quality badge
 */
export function createQualityBadgeLabel(
  level: 'high' | 'medium' | 'low',
  score: number
): string {
  const percentage = Math.round(score * 100);
  return `Quality ${level}, ${percentage} percent`;
}

/**
 * Create ARIA label for annotation chip
 */
export function createAnnotationChipLabel(
  annotationNumber: number,
  totalAnnotations: number
): string {
  return `Annotation ${annotationNumber} of ${totalAnnotations}`;
}

/**
 * Create ARIA label for chunk boundary
 */
export function createChunkBoundaryLabel(
  chunkName: string,
  lineRange: string
): string {
  return `Code chunk: ${chunkName}, lines ${lineRange}`;
}

/**
 * Create ARIA label for reference icon
 */
export function createReferenceIconLabel(
  referenceType: string,
  title: string
): string {
  return `${referenceType} reference: ${title}`;
}
