// Performance monitoring utilities
import { onCLS, onFCP, onINP, onLCP, onTTFB, type Metric } from 'web-vitals';

export interface PerformanceMetrics {
  fcp?: number;
  lcp?: number;
  inp?: number;
  cls?: number;
  ttfb?: number;
}

// Performance budgets (in milliseconds or score)
export const PERFORMANCE_BUDGETS = {
  FCP: 1800, // First Contentful Paint
  LCP: 2500, // Largest Contentful Paint
  INP: 200, // Interaction to Next Paint (replaces FID)
  CLS: 0.1, // Cumulative Layout Shift
  TTFB: 600, // Time to First Byte
};

let metrics: PerformanceMetrics = {};

function sendToAnalytics(metric: Metric) {
  // Store metrics
  metrics[metric.name.toLowerCase() as keyof PerformanceMetrics] = metric.value;

  // Log to console in development
  if (import.meta.env.DEV) {
    console.log(`[Performance] ${metric.name}:`, metric.value);
    
    // Check against budget
    const budget = PERFORMANCE_BUDGETS[metric.name as keyof typeof PERFORMANCE_BUDGETS];
    if (budget && metric.value > budget) {
      console.warn(`[Performance] ${metric.name} exceeds budget: ${metric.value} > ${budget}`);
    }
  }

  // In production, send to analytics service
  // Example: analytics.track('web-vital', { name: metric.name, value: metric.value });
}

export function initPerformanceMonitoring() {
  // Monitor Core Web Vitals
  onCLS(sendToAnalytics);
  onFCP(sendToAnalytics);
  onINP(sendToAnalytics);
  onLCP(sendToAnalytics);
  onTTFB(sendToAnalytics);
}

export function getPerformanceMetrics(): PerformanceMetrics {
  return { ...metrics };
}

export function checkPerformanceBudgets(): { passed: boolean; violations: string[] } {
  const violations: string[] = [];

  if (metrics.fcp && metrics.fcp > PERFORMANCE_BUDGETS.FCP) {
    violations.push(`FCP: ${metrics.fcp}ms > ${PERFORMANCE_BUDGETS.FCP}ms`);
  }
  if (metrics.lcp && metrics.lcp > PERFORMANCE_BUDGETS.LCP) {
    violations.push(`LCP: ${metrics.lcp}ms > ${PERFORMANCE_BUDGETS.LCP}ms`);
  }
  if (metrics.inp && metrics.inp > PERFORMANCE_BUDGETS.INP) {
    violations.push(`INP: ${metrics.inp}ms > ${PERFORMANCE_BUDGETS.INP}ms`);
  }
  if (metrics.cls && metrics.cls > PERFORMANCE_BUDGETS.CLS) {
    violations.push(`CLS: ${metrics.cls} > ${PERFORMANCE_BUDGETS.CLS}`);
  }
  if (metrics.ttfb && metrics.ttfb > PERFORMANCE_BUDGETS.TTFB) {
    violations.push(`TTFB: ${metrics.ttfb}ms > ${PERFORMANCE_BUDGETS.TTFB}ms`);
  }

  return {
    passed: violations.length === 0,
    violations,
  };
}

// Resource hints helper
export function preloadResource(href: string, as: string) {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = href;
  link.as = as;
  document.head.appendChild(link);
}

export function prefetchResource(href: string) {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = href;
  document.head.appendChild(link);
}

export function preconnect(href: string) {
  const link = document.createElement('link');
  link.rel = 'preconnect';
  link.href = href;
  document.head.appendChild(link);
}
