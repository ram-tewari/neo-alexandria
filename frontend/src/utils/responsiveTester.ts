// Neo Alexandria 2.0 Frontend - Responsive Testing Utility
// Development tool for testing responsive breakpoints and touch targets

/**
 * Responsive breakpoints matching Tailwind config
 */
export const BREAKPOINTS = {
  xs: 320,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

/**
 * Common device viewport sizes for testing
 */
export const DEVICE_SIZES = {
  // Mobile devices
  'iPhone SE': { width: 375, height: 667 },
  'iPhone 12/13/14': { width: 390, height: 844 },
  'iPhone 14 Pro Max': { width: 430, height: 932 },
  'Samsung Galaxy S21': { width: 360, height: 800 },
  'Pixel 5': { width: 393, height: 851 },
  
  // Tablets
  'iPad Mini': { width: 768, height: 1024 },
  'iPad': { width: 810, height: 1080 },
  'iPad Pro 11"': { width: 834, height: 1194 },
  'iPad Pro 12.9"': { width: 1024, height: 1366 },
  
  // Desktop
  'Laptop 13"': { width: 1280, height: 800 },
  'Desktop HD': { width: 1920, height: 1080 },
  'Desktop 2K': { width: 2560, height: 1440 },
} as const;

/**
 * Test viewport sizes as specified in requirements
 */
export const TEST_VIEWPORTS = {
  mobile: [320, 375, 414],
  tablet: [768, 1024],
  desktop: [1280, 1920],
} as const;

/**
 * Minimum touch target size (WCAG 2.1 Level AAA)
 */
export const MIN_TOUCH_TARGET_SIZE = 44;

/**
 * Get current viewport size
 */
export function getCurrentViewport() {
  return {
    width: window.innerWidth,
    height: window.innerHeight,
  };
}

/**
 * Get current breakpoint
 */
export function getCurrentBreakpoint(): keyof typeof BREAKPOINTS {
  const width = window.innerWidth;
  
  if (width >= BREAKPOINTS['2xl']) return '2xl';
  if (width >= BREAKPOINTS.xl) return 'xl';
  if (width >= BREAKPOINTS.lg) return 'lg';
  if (width >= BREAKPOINTS.md) return 'md';
  if (width >= BREAKPOINTS.sm) return 'sm';
  return 'xs';
}

/**
 * Check if element meets minimum touch target size
 */
export function checkTouchTargetSize(element: HTMLElement): {
  valid: boolean;
  width: number;
  height: number;
  minSize: number;
} {
  const rect = element.getBoundingClientRect();
  const width = rect.width;
  const height = rect.height;
  
  return {
    valid: width >= MIN_TOUCH_TARGET_SIZE && height >= MIN_TOUCH_TARGET_SIZE,
    width,
    height,
    minSize: MIN_TOUCH_TARGET_SIZE,
  };
}

/**
 * Find all interactive elements on the page
 */
export function findInteractiveElements(): HTMLElement[] {
  const selectors = [
    'button',
    'a',
    'input',
    'select',
    'textarea',
    '[role="button"]',
    '[role="link"]',
    '[tabindex]:not([tabindex="-1"])',
  ];
  
  return Array.from(document.querySelectorAll(selectors.join(', '))) as HTMLElement[];
}

/**
 * Check all touch targets on the page
 */
export function checkAllTouchTargets(): {
  total: number;
  valid: number;
  invalid: Array<{
    element: HTMLElement;
    size: ReturnType<typeof checkTouchTargetSize>;
    selector: string;
  }>;
} {
  const elements = findInteractiveElements();
  const results = elements.map(element => ({
    element,
    size: checkTouchTargetSize(element),
    selector: getElementSelector(element),
  }));
  
  const invalid = results.filter(r => !r.size.valid);
  
  return {
    total: results.length,
    valid: results.length - invalid.length,
    invalid,
  };
}

/**
 * Get a CSS selector for an element
 */
function getElementSelector(element: HTMLElement): string {
  if (element.id) return `#${element.id}`;
  if (element.className) {
    const classes = element.className.split(' ').filter(c => c).slice(0, 2).join('.');
    return `${element.tagName.toLowerCase()}.${classes}`;
  }
  return element.tagName.toLowerCase();
}

/**
 * Highlight elements that don't meet touch target requirements
 */
export function highlightInvalidTouchTargets() {
  const { invalid } = checkAllTouchTargets();
  
  // Remove existing highlights
  document.querySelectorAll('.responsive-test-highlight').forEach(el => el.remove());
  
  // Add highlights
  invalid.forEach(({ element, size }) => {
    const highlight = document.createElement('div');
    highlight.className = 'responsive-test-highlight';
    highlight.style.cssText = `
      position: absolute;
      pointer-events: none;
      border: 2px solid red;
      background: rgba(255, 0, 0, 0.1);
      z-index: 10000;
    `;
    
    const rect = element.getBoundingClientRect();
    highlight.style.top = `${rect.top + window.scrollY}px`;
    highlight.style.left = `${rect.left + window.scrollX}px`;
    highlight.style.width = `${rect.width}px`;
    highlight.style.height = `${rect.height}px`;
    
    // Add label
    const label = document.createElement('div');
    label.style.cssText = `
      position: absolute;
      top: -20px;
      left: 0;
      background: red;
      color: white;
      padding: 2px 6px;
      font-size: 10px;
      font-family: monospace;
      white-space: nowrap;
    `;
    label.textContent = `${Math.round(size.width)}x${Math.round(size.height)}px`;
    highlight.appendChild(label);
    
    document.body.appendChild(highlight);
  });
  
  return invalid.length;
}

/**
 * Remove touch target highlights
 */
export function removeHighlights() {
  document.querySelectorAll('.responsive-test-highlight').forEach(el => el.remove());
}

/**
 * Log responsive testing information to console
 */
export function logResponsiveInfo() {
  const viewport = getCurrentViewport();
  const breakpoint = getCurrentBreakpoint();
  const touchTargets = checkAllTouchTargets();
  
  console.group('📱 Responsive Testing Info');
  console.log('Viewport:', `${viewport.width}x${viewport.height}px`);
  console.log('Breakpoint:', breakpoint);
  console.log('Touch Targets:', `${touchTargets.valid}/${touchTargets.total} valid`);
  
  if (touchTargets.invalid.length > 0) {
    console.group('❌ Invalid Touch Targets:');
    touchTargets.invalid.forEach(({ selector, size }) => {
      console.log(
        `${selector}: ${Math.round(size.width)}x${Math.round(size.height)}px`,
        `(min: ${size.minSize}px)`
      );
    });
    console.groupEnd();
  }
  
  console.groupEnd();
}

/**
 * Create a responsive testing overlay
 */
export function createTestingOverlay() {
  // Remove existing overlay
  const existing = document.getElementById('responsive-test-overlay');
  if (existing) {
    existing.remove();
    removeHighlights();
    return;
  }
  
  const viewport = getCurrentViewport();
  const breakpoint = getCurrentBreakpoint();
  const touchTargets = checkAllTouchTargets();
  
  const overlay = document.createElement('div');
  overlay.id = 'responsive-test-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    background: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 16px;
    border-radius: 8px;
    font-family: monospace;
    font-size: 12px;
    z-index: 10001;
    min-width: 250px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  `;
  
  overlay.innerHTML = `
    <div style="margin-bottom: 12px; font-weight: bold; font-size: 14px;">
      📱 Responsive Testing
    </div>
    <div style="margin-bottom: 8px;">
      <strong>Viewport:</strong> ${viewport.width}x${viewport.height}px
    </div>
    <div style="margin-bottom: 8px;">
      <strong>Breakpoint:</strong> ${breakpoint}
    </div>
    <div style="margin-bottom: 12px;">
      <strong>Touch Targets:</strong> 
      <span style="color: ${touchTargets.invalid.length === 0 ? '#10B981' : '#EF4444'}">
        ${touchTargets.valid}/${touchTargets.total} valid
      </span>
    </div>
    <button id="highlight-btn" style="
      width: 100%;
      padding: 8px;
      background: #3B82F6;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      margin-bottom: 8px;
    ">
      ${touchTargets.invalid.length > 0 ? 'Highlight Invalid' : 'All Valid ✓'}
    </button>
    <button id="close-btn" style="
      width: 100%;
      padding: 8px;
      background: #6B7280;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    ">
      Close
    </button>
  `;
  
  document.body.appendChild(overlay);
  
  // Add event listeners
  const highlightBtn = document.getElementById('highlight-btn');
  const closeBtn = document.getElementById('close-btn');
  
  if (highlightBtn && touchTargets.invalid.length > 0) {
    highlightBtn.addEventListener('click', () => {
      highlightInvalidTouchTargets();
      logResponsiveInfo();
    });
  }
  
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      overlay.remove();
      removeHighlights();
    });
  }
  
  // Update on resize
  let resizeTimeout: ReturnType<typeof setTimeout>;
  const handleResize = () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      overlay.remove();
      removeHighlights();
      createTestingOverlay();
    }, 500);
  };
  
  window.addEventListener('resize', handleResize);
}

/**
 * Initialize responsive testing (for development only)
 */
export function initResponsiveTesting() {
  if (process.env.NODE_ENV !== 'development') return;
  
  // Add keyboard shortcut: Ctrl+Shift+R
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'R') {
      e.preventDefault();
      createTestingOverlay();
    }
  });
  
  console.log('📱 Responsive Testing enabled. Press Ctrl+Shift+R to toggle overlay.');
}

// Export for use in browser console
if (typeof window !== 'undefined') {
  (window as any).responsiveTester = {
    getCurrentViewport,
    getCurrentBreakpoint,
    checkAllTouchTargets,
    highlightInvalidTouchTargets,
    removeHighlights,
    logResponsiveInfo,
    createTestingOverlay,
    BREAKPOINTS,
    DEVICE_SIZES,
    TEST_VIEWPORTS,
  };
}
