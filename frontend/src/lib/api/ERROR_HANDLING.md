# Error Handling Guide

This document describes the error handling strategy implemented in the Neo Alexandria frontend application.

## Overview

The application uses a multi-layered error handling approach:

1. **API Layer**: Centralized error handling in API clients
2. **Component Layer**: Error boundaries for React component errors
3. **UI Layer**: User-friendly error messages and recovery options

## API Error Handling

### ApiError Class

All API errors are wrapped in the `ApiError` class, which provides:

- `message`: User-friendly error message
- `status`: HTTP status code (0 for network errors)
- `data`: Raw error data from the server

```typescript
import { ApiError } from './lib/api';

try {
  const resource = await resourcesApi.get(id);
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API Error:', error.message, error.status);
  }
}
```

### Error Handling Utilities

The `apiUtils.ts` module provides several utility functions:

#### `handleApiError(response: Response)`
Converts HTTP error responses into `ApiError` instances.

#### `apiRequest<T>(endpoint: string, options?: RequestInit)`
Makes API requests with automatic error handling.

#### `isApiError(error: unknown)`
Type guard to check if an error is an `ApiError`.

#### `getErrorMessage(error: unknown)`
Extracts user-friendly error message from any error type.

#### HTTP Status Helpers
- `isNotFoundError(error)` - Check for 404 errors
- `isUnauthorizedError(error)` - Check for 401 errors
- `isForbiddenError(error)` - Check for 403 errors
- `isServerError(error)` - Check for 5xx errors
- `isNetworkError(error)` - Check for network failures

### Usage Example

```typescript
import { resourcesApi, isNotFoundError, getErrorMessage } from './lib/api';

try {
  const resource = await resourcesApi.get(id);
  // Handle success
} catch (error) {
  if (isNotFoundError(error)) {
    // Show 404 UI
    showNotFoundPage();
  } else {
    // Show generic error
    showToast({
      variant: 'error',
      message: getErrorMessage(error),
    });
  }
}
```

## React Error Boundaries

### FeatureErrorBoundary Component

Wraps major features to prevent entire app crashes. Catches React rendering errors and displays fallback UI.

```typescript
import { FeatureErrorBoundary } from './components/common/FeatureErrorBoundary';

<FeatureErrorBoundary featureName="Library">
  <LibraryView />
</FeatureErrorBoundary>
```

#### Props

- `children`: React components to wrap
- `featureName`: Optional name for better error context
- `fallback`: Optional custom fallback UI
- `onError`: Optional callback when error occurs

#### Features

- Displays user-friendly error UI with retry button
- Logs detailed error information to console
- Shows error details in development mode
- Provides "Try Again" and "Go Back" actions

### Where to Use Error Boundaries

Error boundaries should wrap:

- Page-level components (routes)
- Major feature components (library, upload, detail pages)
- Complex interactive components

**Do NOT wrap:**

- Individual UI primitives (buttons, inputs)
- Simple presentational components
- Components that already handle their own errors

## Component-Level Error Handling

### React Query Error Handling

React Query automatically handles API errors. Access error state in components:

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['resource', id],
  queryFn: () => resourcesApi.get(id),
});

if (error) {
  return <ErrorMessage error={error} />;
}
```

### Display Error States

Components should display appropriate error UI:

#### LibraryView
Shows error message with retry button when resource loading fails.

#### ResourceDetailPage
Shows 404 page for missing resources, generic error for other failures.

#### UploadItem
Displays error message with retry action for failed uploads.

### Error UI Patterns

#### Inline Errors
For form validation and minor errors:
```tsx
<div className="error-message" role="alert">
  {error.message}
</div>
```

#### Full-Page Errors
For critical failures:
```tsx
<div className="error-state">
  <div className="error-icon">⚠️</div>
  <h2>Error Title</h2>
  <p>{error.message}</p>
  <Button onClick={retry}>Retry</Button>
</div>
```

#### Toast Notifications
For transient errors:
```typescript
showToast({
  variant: 'error',
  message: getErrorMessage(error),
});
```

## Best Practices

### 1. Always Handle Errors

Never leave API calls without error handling:

```typescript
// ❌ Bad
const data = await resourcesApi.get(id);

// ✅ Good
try {
  const data = await resourcesApi.get(id);
} catch (error) {
  handleError(error);
}

// ✅ Better (with React Query)
const { data, error } = useQuery({
  queryKey: ['resource', id],
  queryFn: () => resourcesApi.get(id),
});
```

### 2. Provide User-Friendly Messages

```typescript
// ❌ Bad
<p>{error.toString()}</p>

// ✅ Good
<p>{getErrorMessage(error)}</p>
```

### 3. Offer Recovery Options

Always provide a way for users to recover:

- Retry button for transient errors
- Back button for navigation errors
- Clear filters for empty results
- Contact support for persistent errors

### 4. Log Errors for Debugging

```typescript
console.error('Error details:', {
  message: error.message,
  status: error.status,
  data: error.data,
  timestamp: new Date().toISOString(),
});
```

### 5. Test Error States

Always test error scenarios:

- Network failures
- 404 Not Found
- 401 Unauthorized
- 500 Server Errors
- Validation errors
- Timeout errors

## Error Handling Checklist

When implementing a new feature:

- [ ] Wrap API calls with try-catch or use React Query
- [ ] Display user-friendly error messages
- [ ] Provide retry/recovery options
- [ ] Log errors for debugging
- [ ] Wrap major features with error boundaries
- [ ] Test error scenarios
- [ ] Handle loading and error states in UI
- [ ] Use appropriate error UI patterns

## Common Error Scenarios

### Network Failure
```typescript
if (isNetworkError(error)) {
  showToast({
    variant: 'error',
    message: 'Network error. Please check your connection.',
  });
}
```

### Resource Not Found
```typescript
if (isNotFoundError(error)) {
  navigate('/404');
}
```

### Unauthorized Access
```typescript
if (isUnauthorizedError(error)) {
  navigate('/login');
}
```

### Server Error
```typescript
if (isServerError(error)) {
  showToast({
    variant: 'error',
    message: 'Server error. Please try again later.',
  });
}
```

## Future Improvements

- [ ] Implement error tracking service (e.g., Sentry)
- [ ] Add retry logic with exponential backoff
- [ ] Implement offline mode with queue
- [ ] Add error analytics and monitoring
- [ ] Create error recovery strategies
- [ ] Implement circuit breaker pattern
