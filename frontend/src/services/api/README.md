# API Client Service

This module provides a centralized HTTP client for all backend communication with type safety, error handling, retry logic, and caching.

## Features

- **Type Safety**: Full TypeScript support with interfaces matching backend schemas
- **Error Handling**: Custom `APIError` class with user-friendly messages
- **Retry Logic**: Automatic retry with exponential backoff for network and server errors
- **Caching**: GET requests cached for 5 minutes, automatic invalidation on mutations
- **Request/Response Transformation**: Handles API response wrappers automatically

## Usage

### Basic GET Request

```typescript
import { apiClient } from '@/services/api';

// Simple GET request
const resource = await apiClient.get<Resource>('/api/resources/123');

// GET with query parameters
const resources = await apiClient.get<Resource[]>('/api/resources', {
  page: 1,
  limit: 20,
  sort_by: 'created_at'
});
```

### POST/PUT/PATCH Requests

```typescript
// Create resource
const newResource = await apiClient.post<Resource>('/api/resources', {
  title: 'My Resource',
  description: 'A great resource'
});

// Update resource
const updated = await apiClient.put<Resource>('/api/resources/123', {
  title: 'Updated Title'
});

// Partial update
const patched = await apiClient.patch<Resource>('/api/resources/123', {
  read_status: 'completed'
});
```

### DELETE Request

```typescript
await apiClient.delete('/api/resources/123');
```

### Error Handling

```typescript
import { APIError } from '@/services/api';

try {
  const resource = await apiClient.get<Resource>('/api/resources/123');
} catch (error) {
  if (error instanceof APIError) {
    console.error('Status:', error.statusCode);
    console.error('Code:', error.code);
    console.error('Message:', error.getUserMessage());
    
    if (error.isNetworkError()) {
      // Handle network error
    } else if (error.isClientError()) {
      // Handle 4xx error
    } else if (error.isServerError()) {
      // Handle 5xx error
    }
  }
}
```

### Cache Management

```typescript
// Disable cache for specific request
const freshData = await apiClient.get<Resource>('/api/resources/123', {}, false);

// Invalidate all cache
apiClient.invalidateCache();

// Invalidate specific cache entries
apiClient.invalidateCache('/api/resources');
```

### Authentication

```typescript
// Set auth token
apiClient.setAuthToken('your-jwt-token');

// Clear auth token
apiClient.clearAuthToken();
```

## Configuration

Set the API base URL in `.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Architecture

```
services/api/
├── client.ts       # Base HTTP client with retry and caching
├── errors.ts       # Error handling and custom error classes
├── index.ts        # Module exports
└── README.md       # This file
```

## Retry Logic

The client automatically retries failed requests with exponential backoff:

- **Max Retries**: 3 attempts
- **Base Delay**: 1 second
- **Max Delay**: 10 seconds
- **Jitter**: Random delay added to prevent thundering herd

Only network errors and 5xx server errors are retried. Client errors (4xx) fail immediately.

## Caching Strategy

- **TTL**: 5 minutes for GET requests
- **Invalidation**: Automatic on POST/PUT/PATCH/DELETE
- **Pattern Matching**: Can invalidate by URL pattern

## Error Codes

Common error codes and their meanings:

- `NETWORK_ERROR`: No response from server
- `TIMEOUT_ERROR`: Request timed out
- `RESOURCE_NOT_FOUND`: 404 error
- `VALIDATION_ERROR`: Invalid input data
- `UNAUTHORIZED`: 401 - authentication required
- `FORBIDDEN`: 403 - insufficient permissions
- `SERVER_ERROR`: 5xx server error
- `UNKNOWN_ERROR`: Unexpected error

## Next Steps

After completing the base client, implement:

1. Resource API endpoints (`api/resources.ts`)
2. Collections API endpoints (`api/collections.ts`)
3. Search API endpoints (`api/search.ts`)
4. Tags API endpoints (`api/tags.ts`)
