# API Client

Core API client configuration for communicating with the Neo Alexandria backend.

## Overview

The API client is built on Axios and provides:
- Centralized configuration with environment variables
- Automatic authentication token management
- Request/response interceptors for error handling
- Retry logic with exponential backoff
- Development mode logging

## Configuration

Environment variables (`.env`):

```env
VITE_API_BASE_URL=https://pharos.onrender.com
VITE_API_TIMEOUT=30000
VITE_API_RETRY_ATTEMPTS=3
VITE_API_RETRY_DELAY=1000
```

## Features

### Authentication Token Management

```typescript
import { setAuthToken, clearAuthToken, getAuthToken } from '@/core/api/client';

// Set token (stores in localStorage and adds to headers)
setAuthToken('your-jwt-token');

// Get current token
const token = getAuthToken();

// Clear token (removes from localStorage and headers)
clearAuthToken();
```

### Automatic Token Refresh

The client automatically handles 401 errors by:
1. Attempting to refresh the access token using the refresh token
2. Retrying the original request with the new token
3. Redirecting to login if refresh fails

### Retry Logic

Failed requests are automatically retried with exponential backoff:
- Network errors: Retried up to 3 times
- 5xx server errors: Retried up to 3 times
- Delay: 1s → 2s → 4s (exponential backoff)
- Max delay: 30 seconds

### Rate Limiting

429 errors are handled specially:
- Extracts `Retry-After` header
- Returns custom `RateLimitError` with retry information
- Does not automatically retry (app should handle cooldown)

### Error Handling

The client handles various error scenarios:
- **401 Unauthorized**: Attempts token refresh, redirects to login if fails
- **403 Forbidden**: Returns error (no retry)
- **404 Not Found**: Returns error (no retry)
- **429 Rate Limited**: Returns custom error with retry-after info
- **5xx Server Errors**: Retries with exponential backoff
- **Network Errors**: Retries with exponential backoff

### Development Logging

In development mode, the client logs:
- All outgoing requests (method, URL, params, data)
- All responses (status, data)
- All errors (URL, status, message, data)
- Retry attempts (attempt number, delay)

## Usage

```typescript
import { apiClient } from '@/core/api/client';

// Simple GET request
const response = await apiClient.get('/resources');

// GET with query parameters
const response = await apiClient.get('/resources', {
  params: { page: 1, limit: 25 }
});

// POST request
const response = await apiClient.post('/annotations', {
  resource_id: 'resource-1',
  start_offset: 0,
  end_offset: 10,
  highlighted_text: 'example'
});

// PUT request
const response = await apiClient.put('/annotations/123', {
  note: 'Updated note'
});

// DELETE request
await apiClient.delete('/annotations/123');
```

## Testing

Unit tests are located in `__tests__/client.test.ts` and cover:
- Configuration validation
- Authentication token management
- Request interceptor behavior
- Response interceptor error handling
- Retry logic with exponential backoff
- Timeout handling
- Development logging

Run tests:
```bash
npm test -- src/core/api/__tests__/client.test.ts
```

## Implementation Details

### Request Interceptor

1. Retrieves access token from localStorage
2. Adds `Authorization: Bearer <token>` header if token exists
3. Logs request details in development mode

### Response Interceptor

1. Logs successful responses in development mode
2. Handles 401 errors with token refresh flow
3. Handles 429 errors with custom error type
4. Retries network errors and 5xx errors with exponential backoff
5. Logs all errors in development mode

### Retry Strategy

```typescript
// Exponential backoff calculation
const delay = Math.min(initialDelay * Math.pow(2, retryCount), 30000);

// Example delays:
// Attempt 1: 1000ms (1s)
// Attempt 2: 2000ms (2s)
// Attempt 3: 4000ms (4s)
// Max: 30000ms (30s)
```

## Requirements Satisfied

- ✅ 1.1: Base URL from environment variables
- ✅ 1.2: Authentication tokens in all requests
- ✅ 1.3: Request timeouts (30 seconds default)
- ✅ 1.4: Request/response interceptors
- ✅ 1.5: Retry logic with exponential backoff (3 attempts)
- ✅ 1.6: Development mode logging

## Next Steps

- Integrate with TanStack Query for data fetching
- Create domain-specific API client modules (workbench, editor, etc.)
- Add TypeScript type definitions for API requests/responses
- Implement error UI components for user-facing errors
