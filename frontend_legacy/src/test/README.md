# Test Infrastructure

This directory contains the testing infrastructure for the Neo Alexandria frontend.

## Files

### `setup.ts`
Global test configuration and setup for Vitest. This file:
- Configures the test environment
- Mocks browser APIs (localStorage, sessionStorage, matchMedia)
- Sets up cleanup after each test
- Provides environment variable mocks

### `utils.tsx`
Helper functions for testing React components:
- `renderWithProviders()` - Renders components with necessary providers (Router, React Query)
- `createMockResponse()` - Creates mock fetch responses
- `createMockErrorResponse()` - Creates mock error responses
- `createMockJWT()` - Creates mock JWT tokens
- `createMockRateLimitHeaders()` - Creates mock rate limit headers
- Re-exports all `@testing-library/react` utilities

### `property-helpers.ts`
Generators and utilities for property-based testing with fast-check:
- `jwtArbitrary` - Generates random JWT claims
- `rateLimitArbitrary` - Generates random rate limit values
- `apiResponseArbitrary` - Generates random API responses
- `apiErrorArbitrary` - Generates random API errors
- `resourceArbitrary` - Generates random resource data
- `collectionArbitrary` - Generates random collection data
- `annotationArbitrary` - Generates random annotation data
- `searchQueryArbitrary` - Generates random search queries
- `requestHistoryArbitrary` - Generates random request history entries
- `propertyTestConfig` - Default configuration for property tests (100 runs minimum)

### `example.test.tsx`
Example test file demonstrating:
- Unit testing patterns
- Property-based testing patterns
- Mock function usage
- Component rendering with providers

## Usage

### Unit Testing

```typescript
import { describe, it, expect } from 'vitest';
import { renderWithProviders } from '@/test/utils';

describe('MyComponent', () => {
  it('should render correctly', () => {
    const { getByText } = renderWithProviders(<MyComponent />);
    expect(getByText('Hello')).toBeInTheDocument();
  });
});
```

### Property-Based Testing

```typescript
import { describe, it } from 'vitest';
import * as fc from 'fast-check';
import { jwtArbitrary, propertyTestConfig } from '@/test/property-helpers';

describe('JWT Decoding', () => {
  it('should decode all valid JWT tokens', () => {
    fc.assert(
      fc.property(jwtArbitrary, (claims) => {
        const token = encodeJWT(claims);
        const decoded = decodeJWT(token);
        return decoded.sub === claims.sub;
      }),
      propertyTestConfig
    );
  });
});
```

### Mocking API Calls

```typescript
import { vi } from 'vitest';
import { createMockResponse } from '@/test/utils';

it('should fetch data', async () => {
  global.fetch = vi.fn().mockResolvedValue(
    createMockResponse({ id: '123', name: 'Test' })
  );

  const data = await fetchData();
  expect(data.id).toBe('123');
});
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Testing Strategy

### Unit Tests
- Test individual components and functions
- Mock external dependencies
- Focus on logic and rendering
- Use descriptive test names

### Property-Based Tests
- Test universal properties across all inputs
- Use fast-check for random input generation
- Validate correctness guarantees
- Run minimum 100 iterations per property

### Integration Tests
- Test complete workflows
- Use real API client (with mocked backend)
- Verify component interactions

## Best Practices

1. **Keep tests focused** - One assertion per test when possible
2. **Use descriptive names** - Test names should explain what is being tested
3. **Mock external dependencies** - Don't make real API calls in tests
4. **Clean up after tests** - Use `afterEach` for cleanup
5. **Use property tests for universal properties** - Test across many inputs
6. **Use unit tests for specific examples** - Test edge cases and error conditions
7. **Don't over-test** - Focus on core functionality
8. **Keep tests maintainable** - Refactor tests as code changes

## Property Test Configuration

All property tests should use the `propertyTestConfig` which sets:
- `numRuns: 100` - Minimum 100 iterations per test
- `verbose: true` - Show detailed output on failure

This ensures comprehensive coverage through randomization while maintaining reasonable test execution time.
