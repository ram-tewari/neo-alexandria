# Frontend Deployment Guide

## Overview

This document describes the CI/CD pipeline and deployment process for the Neo Alexandria frontend application.

## CI/CD Pipeline

The frontend uses GitHub Actions for continuous integration and deployment. The pipeline consists of several jobs:

### 1. Test Job

Runs on every push and pull request to `main` or `develop` branches.

**Steps:**
- Type checking with TypeScript
- Linting with ESLint
- Unit tests with Vitest
- Accessibility tests with axe-core
- Coverage reporting to Codecov

**Commands:**
```bash
npm run type-check
npm run lint
npm run test:ci
npm run test:a11y
npm run test:coverage
```

### 2. E2E Job

Runs end-to-end tests with Playwright across multiple browsers.

**Browsers tested:**
- Chromium (Desktop)
- Firefox (Desktop)
- WebKit (Desktop)
- Mobile Chrome (Pixel 5)
- Mobile Safari (iPhone 12)

**Commands:**
```bash
npm run build
npm run test:e2e
```

### 3. Lighthouse Job

Runs performance audits on pull requests.

**Metrics checked:**
- Performance score > 90
- Accessibility score > 95
- Best practices score > 90
- SEO score > 90
- First Contentful Paint < 1.8s
- Largest Contentful Paint < 2.5s
- Cumulative Layout Shift < 0.1
- Total Blocking Time < 300ms

**Command:**
```bash
npm run lighthouse
```

### 4. Build Job

Creates production build and analyzes bundle size.

**Optimizations:**
- Code splitting by vendor chunks
- Tree shaking
- Minification with Terser
- Source maps for debugging
- Console removal in production

**Command:**
```bash
npm run build
```

### 5. Deploy Preview Job

Deploys preview builds for pull requests (when configured).

## Performance Budgets

The application enforces strict performance budgets:

| Metric | Budget | Description |
|--------|--------|-------------|
| FCP | 1.8s | First Contentful Paint |
| LCP | 2.5s | Largest Contentful Paint |
| INP | 200ms | Interaction to Next Paint |
| CLS | 0.1 | Cumulative Layout Shift |
| TTFB | 600ms | Time to First Byte |
| Main Bundle | 200KB | Gzipped main bundle size |
| Total Bundle | 500KB | Gzipped total bundle size |

## Local Development

### Prerequisites

- Node.js 18+
- npm 9+

### Setup

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

Runs on http://localhost:3000 with hot module replacement.

### Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:ui

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run accessibility tests
npm run test:a11y

# Generate coverage report
npm run test:coverage
```

### Building

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

### Linting and Type Checking

```bash
# Type check
npm run type-check

# Lint
npm run lint
```

## Production Deployment

### Build Artifacts

The production build creates optimized assets in the `dist/` directory:

```
dist/
├── assets/
│   ├── index-[hash].js       # Main application bundle
│   ├── react-vendor-[hash].js # React vendor chunk
│   ├── query-vendor-[hash].js # React Query chunk
│   ├── ui-vendor-[hash].js    # UI library chunk
│   ├── d3-vendor-[hash].js    # D3 visualization chunk
│   └── index-[hash].css       # Compiled styles
├── index.html                 # Entry HTML
└── service-worker.js          # Service worker for offline support
```

### Environment Variables

Create a `.env.production` file:

```env
VITE_API_BASE_URL=https://api.neo-alexandria.com
VITE_ENABLE_ANALYTICS=true
VITE_SENTRY_DSN=your-sentry-dsn
```

### Deployment Steps

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Test the production build locally:**
   ```bash
   npm run preview
   ```

3. **Deploy to hosting service:**
   
   **Option A: Static hosting (Netlify, Vercel, etc.)**
   ```bash
   # Deploy dist/ directory
   netlify deploy --prod --dir=dist
   ```

   **Option B: Docker**
   ```bash
   docker build -t neo-alexandria-frontend .
   docker run -p 80:80 neo-alexandria-frontend
   ```

   **Option C: AWS S3 + CloudFront**
   ```bash
   aws s3 sync dist/ s3://your-bucket-name
   aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
   ```

### Service Worker

The application includes a service worker for offline support:

- Caches static assets on install
- Serves cached content when offline
- Updates cache on new deployments
- Network-first strategy for API calls
- Cache-first strategy for static assets

To clear the cache:
```javascript
navigator.serviceWorker.controller?.postMessage({ type: 'CLEAR_CACHE' });
```

## Monitoring

### Performance Monitoring

Performance metrics are automatically tracked using Web Vitals:

```typescript
import { initPerformanceMonitoring } from '@/utils/performance';

// Initialize in main.tsx
initPerformanceMonitoring();
```

Metrics are logged to console in development and can be sent to analytics in production.

### Error Tracking

Errors are caught by error boundaries and can be sent to error tracking services:

```typescript
// Configure in ErrorBoundary.tsx
const logErrorToService = (error: Error, errorInfo: ErrorInfo) => {
  // Send to Sentry, LogRocket, etc.
};
```

## Troubleshooting

### Build Failures

**Issue:** Type errors during build
```bash
# Run type check to see detailed errors
npm run type-check
```

**Issue:** Bundle size too large
```bash
# Analyze bundle
npm run build
# Check dist/assets/ for large chunks
```

### Test Failures

**Issue:** E2E tests failing
```bash
# Run with UI to debug
npm run test:e2e:ui
```

**Issue:** Accessibility violations
```bash
# Run accessibility tests
npm run test:a11y
```

### Performance Issues

**Issue:** Lighthouse score below threshold
```bash
# Run Lighthouse locally
npm run lighthouse
# Check .lighthouseci/ for detailed report
```

**Issue:** Slow page load
- Check bundle sizes in dist/assets/
- Verify code splitting is working
- Check network waterfall in DevTools
- Verify service worker is caching correctly

## Best Practices

1. **Always run tests before pushing:**
   ```bash
   npm run type-check && npm run lint && npm test
   ```

2. **Check bundle size after adding dependencies:**
   ```bash
   npm run build
   du -h dist/assets/*.js | sort -h
   ```

3. **Test accessibility:**
   ```bash
   npm run test:a11y
   ```

4. **Monitor performance:**
   - Check Web Vitals in DevTools
   - Run Lighthouse audits regularly
   - Monitor real user metrics in production

5. **Keep dependencies updated:**
   ```bash
   npm outdated
   npm update
   ```

## Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
