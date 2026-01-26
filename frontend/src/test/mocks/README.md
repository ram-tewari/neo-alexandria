# MSW Mock Handlers

This directory contains Mock Service Worker (MSW) handlers for testing the Neo Alexandria frontend.

## Files

### `handlers.ts`
Default mock handlers that return successful responses matching the backend API schemas.

**Usage:**
```typescript
import { handlers } from '@/test/mocks/handlers';
import { setupServer } from 'msw/node';

const server = setupServer(...handlers);
```

**Exported Mock Data:**
- `mockUser` - Mock user object
- `mockResources` - Array of mock resources
- `mockResource` - Single mock resource
- `mockAnnotations` - Array of mock annotations
- `mockChunks` - Array of mock semantic chunks
- `mockQualityDetails` - Mock quality details
- `mockProcessingStatus` - Mock processing status
- `mockRateLimitStatus` - Mock rate limit status
- `mockHealthStatus` - Mock health status
- `mockNode2VecSummary` - Mock Node2Vec summary
- `mockGraphConnections` - Mock graph connections

### `error-handlers.ts`
Mock handlers for testing error scenarios (401, 403, 404, 429, 500, network errors, timeouts).

**Usage:**
```typescript
import { server } from '@/test/setup';
import { 
  unauthorizedHandlers,
  notFoundHandlers,
  rateLimitHandlers,
  serverErrorHandlers,
  networkErrorHandlers,
  timeoutHandlers,
} from '@/test/mocks/error-handlers';

// Override default handlers for a specific test
test('handles 404 error', () => {
  server.use(...notFoundHandlers);
  // Your test code
});
```

**Available Handler Sets:**
- `unauthorizedHandlers` - 401 Unauthorized errors
- `forbiddenHandlers` - 403 Forbidden errors
- `notFoundHandlers` - 404 Not Found errors
- `rateLimitHandlers` - 429 Rate Limited errors
- `serverErrorHandlers` - 500 Server errors
- `networkErrorHandlers` - Network connection failures
- `timeoutHandlers` - Request timeout scenarios
- `validationErrorHandlers` - 422 Validation errors

**Helper Functions:**
```typescript
// Create a custom error handler
createErrorHandler('get', '/resources/:id', 404, 'NOT_FOUND', 'Resource not found');

// Create a network error handler
createNetworkErrorHandler('post', '/annotations');

// Create a timeout handler
createTimeoutHandler('get', '/resources/:id', 5000); // 5 second delay
```

### `delayed-handlers.ts`
Mock handlers with configurable delays for testing loading states.

**Usage:**
```typescript
import { 
  allDelayedHandlers,
  setMockDelay,
  DEFAULT_DELAYS,
} from '@/test/mocks/delayed-handlers';

// Set delay for all handlers
setMockDelay(DEFAULT_DELAYS.slow); // 2 seconds

// Use delayed handlers
server.use(...allDelayedHandlers);

// Test loading state
test('shows loading spinner', async () => {
  setMockDelay(1000);
  render(<MyComponent />);
  expect(screen.getByRole('progressbar')).toBeInTheDocument();
  await waitFor(() => expect(screen.queryByRole('progressbar')).not.toBeInTheDocument());
});
```

**Available Delays:**
- `DEFAULT_DELAYS.fast` - 100ms (cached data)
- `DEFAULT_DELAYS.normal` - 500ms (typical API calls)
- `DEFAULT_DELAYS.slow` - 2000ms (complex queries)
- `DEFAULT_DELAYS.verySlow` - 5000ms (heavy processing)

**Helper Functions:**
```typescript
// Set custom delay
setMockDelay(1500);

// Reset to default
resetMockDelay();

// Get current delay
const delay = getCurrentDelay();

// Create custom delayed handler
createDelayedHandler('get', '/resources/:id', mockResource, 200, 2000);
```

## Common Testing Patterns

### Testing Success Scenarios
```typescript
import { server } from '@/test/setup';
import { handlers } from '@/test/mocks/handlers';

test('loads resources successfully', async () => {
  // Default handlers are already set up
  render(<ResourceList />);
  
  await waitFor(() => {
    expect(screen.getByText('example.ts')).toBeInTheDocument();
  });
});
```

### Testing Error Scenarios
```typescript
import { server } from '@/test/setup';
import { notFoundHandlers } from '@/test/mocks/error-handlers';

test('handles resource not found', async () => {
  server.use(...notFoundHandlers);
  
  render(<ResourceDetail id="invalid-id" />);
  
  await waitFor(() => {
    expect(screen.getByText(/not found/i)).toBeInTheDocument();
  });
});
```

### Testing Loading States
```typescript
import { server } from '@/test/setup';
import { 
  delayedResourceHandlers,
  setMockDelay,
  DEFAULT_DELAYS,
} from '@/test/mocks/delayed-handlers';

test('shows loading spinner while fetching', async () => {
  setMockDelay(DEFAULT_DELAYS.slow);
  server.use(...delayedResourceHandlers);
  
  render(<ResourceList />);
  
  // Loading state should be visible
  expect(screen.getByRole('progressbar')).toBeInTheDocument();
  
  // Wait for data to load
  await waitFor(() => {
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });
  
  // Data should be displayed
  expect(screen.getByText('example.ts')).toBeInTheDocument();
});
```

### Testing Rate Limiting
```typescript
import { server } from '@/test/setup';
import { rateLimitHandlers } from '@/test/mocks/error-handlers';

test('handles rate limit error', async () => {
  server.use(...rateLimitHandlers);
  
  render(<ResourceList />);
  
  await waitFor(() => {
    expect(screen.getByText(/rate limit exceeded/i)).toBeInTheDocument();
    expect(screen.getByText(/retry after/i)).toBeInTheDocument();
  });
});
```

### Testing Network Failures
```typescript
import { server } from '@/test/setup';
import { networkErrorHandlers } from '@/test/mocks/error-handlers';

test('handles network error', async () => {
  server.use(...networkErrorHandlers);
  
  render(<ResourceList />);
  
  await waitFor(() => {
    expect(screen.getByText(/network error/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });
});
```

### Testing Optimistic Updates
```typescript
import { server } from '@/test/setup';
import { serverErrorHandlers } from '@/test/mocks/error-handlers';

test('reverts optimistic update on error', async () => {
  render(<AnnotationList resourceId="resource-1" />);
  
  // Initial state
  expect(screen.getAllByRole('listitem')).toHaveLength(2);
  
  // Trigger optimistic update
  const createButton = screen.getByRole('button', { name: /create/i });
  fireEvent.click(createButton);
  
  // Optimistic update applied
  expect(screen.getAllByRole('listitem')).toHaveLength(3);
  
  // Simulate server error
  server.use(...serverErrorHandlers);
  
  // Wait for error and rollback
  await waitFor(() => {
    expect(screen.getAllByRole('listitem')).toHaveLength(2);
  });
});
```

## Best Practices

1. **Use default handlers for happy path tests** - The default handlers in `handlers.ts` cover most success scenarios.

2. **Override handlers per test** - Use `server.use()` to override specific handlers for error scenarios.

3. **Reset handlers after each test** - The test setup automatically resets handlers, but you can manually reset with `server.resetHandlers()`.

4. **Test loading states with delays** - Use `delayed-handlers.ts` to test loading spinners and skeleton screens.

5. **Test error recovery** - Verify that your components handle errors gracefully and provide retry mechanisms.

6. **Test rate limiting** - Ensure your app respects rate limits and shows appropriate messages to users.

7. **Keep mocks in sync with backend** - Update mock data when backend schemas change.

## Debugging

### View MSW Logs
MSW logs all intercepted requests in development mode. Check the console for:
- `[MSW] GET /resources (200 OK)`
- `[MSW] POST /annotations (201 Created)`

### Verify Handler Matching
If a request isn't being intercepted:
1. Check the URL matches exactly (including base URL)
2. Verify the HTTP method is correct
3. Ensure handlers are registered before the request

### Common Issues

**Issue:** Mock data not updating
**Solution:** Handlers are set up once. Use `server.use()` to override for specific tests.

**Issue:** Delays not working
**Solution:** Make sure you're using handlers from `delayed-handlers.ts` and calling `setMockDelay()`.

**Issue:** Error handlers not triggering
**Solution:** Verify you're calling `server.use()` with error handlers before making the request.

## Related Documentation

- [MSW Documentation](https://mswjs.io/)
- [Testing Library](https://testing-library.com/)
- [Vitest](https://vitest.dev/)
- [Backend API Documentation](../../../backend/docs/api/)
