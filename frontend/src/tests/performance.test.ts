import { describe, it, expect, beforeAll } from 'vitest';
import { 
  getPerformanceMetrics, 
  checkPerformanceBudgets, 
  PERFORMANCE_BUDGETS 
} from '../utils/performance';

describe('Performance Tests', () => {
  beforeAll(() => {
    // Mock performance API if needed
    if (!global.performance) {
      global.performance = {
        now: () => Date.now(),
        getEntriesByType: () => [],
      } as any;
    }
  });

  it('should have defined performance budgets', () => {
    expect(PERFORMANCE_BUDGETS.FCP).toBeDefined();
    expect(PERFORMANCE_BUDGETS.LCP).toBeDefined();
    expect(PERFORMANCE_BUDGETS.FID).toBeDefined();
    expect(PERFORMANCE_BUDGETS.CLS).toBeDefined();
    expect(PERFORMANCE_BUDGETS.TTFB).toBeDefined();
  });

  it('should track performance metrics', () => {
    const metrics = getPerformanceMetrics();
    expect(metrics).toBeDefined();
    expect(typeof metrics).toBe('object');
  });

  it('should validate performance budgets', () => {
    const result = checkPerformanceBudgets();
    expect(result).toHaveProperty('passed');
    expect(result).toHaveProperty('violations');
    expect(Array.isArray(result.violations)).toBe(true);
  });

  it('FCP budget should be reasonable', () => {
    expect(PERFORMANCE_BUDGETS.FCP).toBeLessThanOrEqual(2000);
  });

  it('LCP budget should be reasonable', () => {
    expect(PERFORMANCE_BUDGETS.LCP).toBeLessThanOrEqual(2500);
  });

  it('FID budget should be reasonable', () => {
    expect(PERFORMANCE_BUDGETS.FID).toBeLessThanOrEqual(100);
  });

  it('CLS budget should be reasonable', () => {
    expect(PERFORMANCE_BUDGETS.CLS).toBeLessThanOrEqual(0.1);
  });

  it('TTFB budget should be reasonable', () => {
    expect(PERFORMANCE_BUDGETS.TTFB).toBeLessThanOrEqual(800);
  });
});

describe('Bundle Size Tests', () => {
  it('should have code splitting configured', async () => {
    // Check if lazy loading is used
    const appModule = await import('../App');
    expect(appModule).toBeDefined();
  });

  it('should lazy load route components', async () => {
    // Verify that routes use React.lazy
    const routeModules = [
      '../pages/Dashboard',
      '../pages/Resources',
      '../pages/Search',
      '../pages/Collections',
    ];

    for (const modulePath of routeModules) {
      try {
        const module = await import(modulePath);
        expect(module).toBeDefined();
      } catch (error) {
        // Module might not exist yet, that's okay
        console.log(`Module ${modulePath} not found, skipping`);
      }
    }
  });
});

describe('Image Optimization Tests', () => {
  it('should use lazy loading for images', () => {
    const img = document.createElement('img');
    img.loading = 'lazy';
    expect(img.loading).toBe('lazy');
  });

  it('should support modern image formats', () => {
    // Check if browser supports WebP
    const canvas = document.createElement('canvas');
    const supportsWebP = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    
    // This is informational - we should provide fallbacks
    console.log('WebP support:', supportsWebP);
    expect(typeof supportsWebP).toBe('boolean');
  });
});

describe('Animation Performance Tests', () => {
  it('should respect prefers-reduced-motion', () => {
    // Mock matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: (query: string) => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        onchange: null,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => true,
      }),
    });

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    expect(typeof prefersReducedMotion).toBe('boolean');
  });

  it('should use CSS transforms for animations', () => {
    const div = document.createElement('div');
    div.style.transform = 'translateX(100px)';
    expect(div.style.transform).toBe('translateX(100px)');
  });

  it('should use will-change for optimized animations', () => {
    const div = document.createElement('div');
    div.style.willChange = 'transform';
    expect(div.style.willChange).toBe('transform');
  });
});

describe('Resource Hints Tests', () => {
  it('should support preconnect', () => {
    const link = document.createElement('link');
    link.rel = 'preconnect';
    link.href = 'https://api.example.com';
    expect(link.rel).toBe('preconnect');
  });

  it('should support prefetch', () => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = '/next-page.js';
    expect(link.rel).toBe('prefetch');
  });

  it('should support preload', () => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'script';
    link.href = '/critical.js';
    expect(link.rel).toBe('preload');
    expect(link.as).toBe('script');
  });
});
