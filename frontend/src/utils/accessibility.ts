/**
 * Accessibility utilities for WCAG compliance
 */

/**
 * Calculate color contrast ratio between two colors
 * @param color1 Hex color string (e.g., '#ffffff')
 * @param color2 Hex color string (e.g., '#000000')
 * @returns Contrast ratio (1-21)
 */
export const calculateContrast = (color1: string, color2: string): number => {
  const getLuminance = (hex: string): number => {
    const rgb = parseInt(hex.slice(1), 16);
    const r = (rgb >> 16) & 0xff;
    const g = (rgb >> 8) & 0xff;
    const b = (rgb >> 0) & 0xff;

    const [rs, gs, bs] = [r, g, b].map((c) => {
      const sRGB = c / 255;
      return sRGB <= 0.03928
        ? sRGB / 12.92
        : Math.pow((sRGB + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const lum1 = getLuminance(color1);
  const lum2 = getLuminance(color2);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
};

/**
 * Check if color contrast meets WCAG AA standards
 * @param foreground Foreground color hex
 * @param background Background color hex
 * @param isLargeText Whether the text is large (18pt+ or 14pt+ bold)
 * @returns Whether the contrast meets WCAG AA
 */
export const meetsWCAGAA = (
  foreground: string,
  background: string,
  isLargeText: boolean = false
): boolean => {
  const contrast = calculateContrast(foreground, background);
  return isLargeText ? contrast >= 3 : contrast >= 4.5;
};

/**
 * Check if color contrast meets WCAG AAA standards
 * @param foreground Foreground color hex
 * @param background Background color hex
 * @param isLargeText Whether the text is large (18pt+ or 14pt+ bold)
 * @returns Whether the contrast meets WCAG AAA
 */
export const meetsWCAGAAA = (
  foreground: string,
  background: string,
  isLargeText: boolean = false
): boolean => {
  const contrast = calculateContrast(foreground, background);
  return isLargeText ? contrast >= 4.5 : contrast >= 7;
};

/**
 * Generate accessible focus styles
 */
export const focusStyles = {
  outline: '2px solid var(--color-primary-500)',
  outlineOffset: '2px',
  borderRadius: '4px',
};

/**
 * Screen reader only CSS class
 */
export const srOnly = {
  position: 'absolute' as const,
  width: '1px',
  height: '1px',
  padding: '0',
  margin: '-1px',
  overflow: 'hidden',
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap' as const,
  borderWidth: '0',
};

/**
 * Announce message to screen readers
 */
export const announceToScreenReader = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};
