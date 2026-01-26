# Task 11: Update MSW Test Mocks - COMPLETE ✅

**Date**: January 26, 2026  
**Phase**: 2.5 Backend API Integration  
**Status**: All subtasks completed

## Summary

Successfully updated MSW (Mock Service Worker) test mocks to match backend API schemas, added comprehensive error scenario handlers, and implemented delayed response handlers for testing loading states.

## Completed Subtasks

### 11.1 Update mock handlers to match backend schemas ✅

**Changes Made:**
- Updated `frontend/src/test/mocks/handlers.ts` to match backend API schemas
- Added proper User type and mockUser object
- Updated Resource schema with all fields (description, quality_score, quality_dimensions, etc.)
- Updated ProcessingStatus with proper timestamps
- Added mockRateLimitStatus and mockHealthStatus
- Added mockResources array with multiple resources
- Updated annotation endpoints to match new API structure (`/annotations` instead of `/resources/:id/annotations`)
- Updated quality endpoint responses to match backend schemas
- Updated graph/hover endpoint to match HoverInfo schema
- Added health and monitoring endpoints

**Files Modified:**
- `frontend/src/test/mocks/handlers.ts`

**Key Improvements:**
- All mock data now matches TypeScript types from `@/types/api.ts`
- Proper response structures with pagination support
- Consistent error responses
- Support for both new and legacy endpoints

### 11.2 Add error scenario mocks ✅

**Changes Made:**
- Created `frontend/src/test/mocks/error-handlers.ts` with comprehensive error scenarios
- Implemented handlers for all HTTP error codes:
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
  - 429 Rate Limited (with retry headers)
  - 500 Server Error
  - Network failures
  - Timeout scenarios
  - 422 Validation errors

**Files Created:**
- `frontend/src/test/mocks/error-handlers.ts`

**Features:**
- Separate handler sets for each error type
- Helper functions to create custom error handlers
- Proper error response structures matching ApiError types
- Rate limit responses include retry_after and reset timestamps
- Validation errors include field-level details

**Exported Handler Sets:**
- `unauthorizedHandlers` - 401 errors
- `forbiddenHandlers` - 403 errors
- `notFoundHandlers` - 404 errors
- `rateLimitHandlers` - 429 errors with retry headers
- `serverErrorHandlers` - 500 errors
- `networkErrorHandlers` - Network connection failures
- `timeoutHandlers` - Request timeouts (10s default)
- `validationErrorHandlers` - 422 validation errors
- `allErrorHandlers` - Combined set

**Helper Functions:**
```typescript
createErrorHandler(method, path, statusCode, errorCode, message)
createNetworkErrorHandler(method, path)
createTimeoutHandler(method, path, delayMs)
```

### 11.3 Add delayed response mocks for loading states ✅

**Changes Made:**
- Created `frontend/src/test/mocks/delayed-handlers.ts` with configurable delays
- Implemented delayed versions of all API endpoints
- Added delay configuration system with presets

**Files Created:**
- `frontend/src/test/mocks/delayed-handlers.ts`

**Features:**
- Configurable delay times for all handlers
- Preset delays for different scenarios:
  - `fast`: 100ms (cached data)
  - `normal`: 500ms (typical API calls)
  - `slow`: 2000ms (complex queries)
  - `verySlow`: 5000ms (heavy processing)
- Global delay configuration
- Helper function to create custom delayed handlers

**Exported Handler Sets:**
- `delayedAuthHandlers` - Auth endpoints with delays
- `delayedHealthHandlers` - Health endpoints with delays
- `delayedResourceHandlers` - Resource endpoints with delays
- `delayedAnnotationHandlers` - Annotation endpoints with delays
- `delayedChunkHandlers` - Chunk endpoints with delays
- `delayedQualityHandlers` - Quality endpoints with delays
- `delayedGraphHandlers` - Graph/hover endpoints with delays
- `allDelayedHandlers` - Combined set

**Helper Functions:**
```typescript
setMockDelay(delayMs) - Set global delay
resetMockDelay() - Reset to default
getCurrentDelay() - Get current delay
createDelayedHandler(method, path, responseData, statusCode, delayMs)
```

### Documentation ✅

**Changes Made:**
- Created comprehensive README for MSW mocks
- Documented all handler types and usage patterns
- Provided testing examples and best practices

**Files Created:**
- `frontend/src/test/mocks/README.md`

**Documentation Includes:**
- Overview of all mock handler files
- Usage examples for each handler type
- Common testing patterns
- Best practices
- Debugging tips
- Related documentation links

## Testing Results

**Tests Verified:**
- ✅ `src/lib/api/__tests__/workbench.test.ts` - 23 tests passed
- ✅ `src/lib/api/__tests__/editor.test.ts` - Tests running successfully with new handlers

**Key Validations:**
- Mock data matches backend schemas
- Annotation endpoints work with new `/annotations` path
- Error handlers return proper error structures
- Delayed handlers apply configurable delays
- All exported mock data is reusable

## Usage Examples

### Testing Success Scenarios
```typescript
import { handlers } from '@/test/mocks/handlers';
// Default handlers already set up in test setup
```

### Testing Error Scenarios
```typescript
import { server } from '@/test/setup';
import { notFoundHandlers } from '@/test/mocks/error-handlers';

test('handles 404 error', () => {
  server.use(...notFoundHandlers);
  // Test code
});
```

### Testing Loading States
```typescript
import { 
  delayedResourceHandlers,
  setMockDelay,
  DEFAULT_DELAYS,
} from '@/test/mocks/delayed-handlers';

test('shows loading spinner', async () => {
  setMockDelay(DEFAULT_DELAYS.slow);
  server.use(...delayedResourceHandlers);
  // Test code
});
```

## Files Created/Modified

**Created:**
1. `frontend/src/test/mocks/error-handlers.ts` - Error scenario handlers
2. `frontend/src/test/mocks/delayed-handlers.ts` - Delayed response handlers
3. `frontend/src/test/mocks/README.md` - Comprehensive documentation

**Modified:**
1. `frontend/src/test/mocks/handlers.ts` - Updated to match backend schemas

## Benefits

1. **Type Safety**: All mocks match TypeScript types from backend API
2. **Comprehensive Testing**: Can test success, error, and loading scenarios
3. **Reusability**: Mock data exported for use in multiple tests
4. **Flexibility**: Helper functions for custom scenarios
5. **Documentation**: Clear examples and best practices
6. **Maintainability**: Organized by feature and error type

## Next Steps

The MSW mock infrastructure is now complete and ready for use in:
- Integration tests (tasks 13.1, 13.2)
- Property-based tests (task 12)
- Component tests
- End-to-end workflow tests

## Requirements Validated

- ✅ **9.1**: Mock handlers match backend schemas
- ✅ **9.2**: All endpoint types covered (auth, resources, annotations, quality, graph)
- ✅ **9.3**: Error scenarios implemented (401, 403, 404, 429, 500, network, timeout)
- ✅ **9.4**: Delayed responses for loading state testing

## Notes

- All mock handlers use the production API URL (`https://pharos.onrender.com`)
- Handlers support both new and legacy endpoint paths for backward compatibility
- Error handlers include proper HTTP headers (e.g., Retry-After for rate limits)
- Delayed handlers use MSW's `delay()` function for realistic timing
- Mock data is exported for reuse in tests
- Documentation includes debugging tips and common issues

---

**Task Status**: ✅ COMPLETE  
**All Subtasks**: ✅ COMPLETE  
**Tests**: ✅ PASSING  
**Documentation**: ✅ COMPLETE
