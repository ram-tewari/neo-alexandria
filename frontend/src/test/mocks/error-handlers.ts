/**
 * MSW Error Scenario Handlers
 * 
 * Mock handlers for testing error scenarios:
 * - 401 Unauthorized
 * - 403 Forbidden
 * - 404 Not Found
 * - 429 Rate Limited
 * - 500 Server Error
 * - Network failures
 * - Timeout scenarios
 */

import { http, HttpResponse, delay } from 'msw';

const API_BASE_URL = 'https://pharos.onrender.com';

// ============================================================================
// 401 Unauthorized Errors
// ============================================================================

export const unauthorizedHandlers = [
  // Unauthorized user endpoint
  http.get(`${API_BASE_URL}/api/auth/me`, () => {
    return HttpResponse.json(
      {
        code: 'UNAUTHORIZED',
        message: 'Authentication required',
        timestamp: new Date().toISOString(),
      },
      { status: 401 }
    );
  }),

  // Unauthorized resource access
  http.get(`${API_BASE_URL}/resources/:resourceId`, () => {
    return HttpResponse.json(
      {
        code: 'UNAUTHORIZED',
        message: 'Authentication required',
        timestamp: new Date().toISOString(),
      },
      { status: 401 }
    );
  }),

  // Unauthorized annotation creation
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, () => {
    return HttpResponse.json(
      {
        code: 'UNAUTHORIZED',
        message: 'Authentication required',
        timestamp: new Date().toISOString(),
      },
      { status: 401 }
    );
  }),
];

// ============================================================================
// 403 Forbidden Errors
// ============================================================================

export const forbiddenHandlers = [
  // Forbidden resource access
  http.get(`${API_BASE_URL}/resources/:resourceId`, () => {
    return HttpResponse.json(
      {
        code: 'FORBIDDEN',
        message: 'You do not have permission to access this resource',
        timestamp: new Date().toISOString(),
      },
      { status: 403 }
    );
  }),

  // Forbidden annotation update
  http.put(`${API_BASE_URL}/annotations/:annotationId`, () => {
    return HttpResponse.json(
      {
        code: 'FORBIDDEN',
        message: 'You do not have permission to update this annotation',
        timestamp: new Date().toISOString(),
      },
      { status: 403 }
    );
  }),

  // Forbidden annotation deletion
  http.delete(`${API_BASE_URL}/annotations/:annotationId`, () => {
    return HttpResponse.json(
      {
        code: 'FORBIDDEN',
        message: 'You do not have permission to delete this annotation',
        timestamp: new Date().toISOString(),
      },
      { status: 403 }
    );
  }),
];

// ============================================================================
// 404 Not Found Errors
// ============================================================================

export const notFoundHandlers = [
  // Resource not found
  http.get(`${API_BASE_URL}/resources/:resourceId`, () => {
    return HttpResponse.json(
      {
        code: 'NOT_FOUND',
        message: 'Resource not found',
        timestamp: new Date().toISOString(),
      },
      { status: 404 }
    );
  }),

  // Annotation not found
  http.get(`${API_BASE_URL}/annotations/:annotationId`, () => {
    return HttpResponse.json(
      {
        code: 'NOT_FOUND',
        message: 'Annotation not found',
        timestamp: new Date().toISOString(),
      },
      { status: 404 }
    );
  }),

  // Chunk not found
  http.get(`${API_BASE_URL}/chunks/:chunkId`, () => {
    return HttpResponse.json(
      {
        code: 'NOT_FOUND',
        message: 'Chunk not found',
        timestamp: new Date().toISOString(),
      },
      { status: 404 }
    );
  }),

  // Quality data not found
  http.get(`${API_BASE_URL}/resources/:resourceId/quality-details`, () => {
    return HttpResponse.json(
      {
        code: 'NOT_FOUND',
        message: 'Quality data not found for this resource',
        timestamp: new Date().toISOString(),
      },
      { status: 404 }
    );
  }),
];

// ============================================================================
// 429 Rate Limited Errors
// ============================================================================

export const rateLimitHandlers = [
  // Rate limited user endpoint
  http.get(`${API_BASE_URL}/api/auth/me`, () => {
    return HttpResponse.json(
      {
        code: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        timestamp: new Date().toISOString(),
        details: {
          retry_after: 60,
          limit: 100,
          reset: Math.floor(Date.now() / 1000) + 60,
        },
      },
      { 
        status: 429,
        headers: {
          'Retry-After': '60',
          'X-RateLimit-Limit': '100',
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': String(Math.floor(Date.now() / 1000) + 60),
        },
      }
    );
  }),

  // Rate limited resource list
  http.get(`${API_BASE_URL}/resources`, () => {
    return HttpResponse.json(
      {
        code: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        timestamp: new Date().toISOString(),
        details: {
          retry_after: 60,
          limit: 100,
          reset: Math.floor(Date.now() / 1000) + 60,
        },
      },
      { 
        status: 429,
        headers: {
          'Retry-After': '60',
        },
      }
    );
  }),

  // Rate limited annotation creation
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, () => {
    return HttpResponse.json(
      {
        code: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        timestamp: new Date().toISOString(),
        details: {
          retry_after: 60,
          limit: 100,
          reset: Math.floor(Date.now() / 1000) + 60,
        },
      },
      { status: 429 }
    );
  }),
];

// ============================================================================
// 500 Server Errors
// ============================================================================

export const serverErrorHandlers = [
  // Server error on user endpoint
  http.get(`${API_BASE_URL}/api/auth/me`, () => {
    return HttpResponse.json(
      {
        code: 'SERVER_ERROR',
        message: 'Internal server error',
        timestamp: new Date().toISOString(),
        details: {
          error_id: 'err-12345',
        },
      },
      { status: 500 }
    );
  }),

  // Server error on resource fetch
  http.get(`${API_BASE_URL}/resources/:resourceId`, () => {
    return HttpResponse.json(
      {
        code: 'SERVER_ERROR',
        message: 'Internal server error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }),

  // Server error on annotation creation
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, () => {
    return HttpResponse.json(
      {
        code: 'SERVER_ERROR',
        message: 'Failed to create annotation',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }),

  // Server error on quality recalculation
  http.post(`${API_BASE_URL}/quality/recalculate`, () => {
    return HttpResponse.json(
      {
        code: 'SERVER_ERROR',
        message: 'Failed to queue quality computation',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }),
];

// ============================================================================
// Network Failure Scenarios
// ============================================================================

export const networkErrorHandlers = [
  // Network error on user endpoint
  http.get(`${API_BASE_URL}/api/auth/me`, () => {
    return HttpResponse.error();
  }),

  // Network error on resource fetch
  http.get(`${API_BASE_URL}/resources/:resourceId`, () => {
    return HttpResponse.error();
  }),

  // Network error on annotation creation
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, () => {
    return HttpResponse.error();
  }),
];

// ============================================================================
// Timeout Scenarios
// ============================================================================

export const timeoutHandlers = [
  // Timeout on user endpoint (10 seconds)
  http.get(`${API_BASE_URL}/api/auth/me`, async () => {
    await delay(10000);
    return HttpResponse.json({ id: 'user-123' });
  }),

  // Timeout on resource fetch (10 seconds)
  http.get(`${API_BASE_URL}/resources/:resourceId`, async () => {
    await delay(10000);
    return HttpResponse.json({ id: 'resource-1' });
  }),

  // Timeout on annotation creation (10 seconds)
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, async () => {
    await delay(10000);
    return HttpResponse.json({ id: 'ann-1' }, { status: 201 });
  }),

  // Timeout on quality recalculation (10 seconds)
  http.post(`${API_BASE_URL}/quality/recalculate`, async () => {
    await delay(10000);
    return HttpResponse.json({ status: 'accepted' });
  }),
];

// ============================================================================
// Validation Error Scenarios
// ============================================================================

export const validationErrorHandlers = [
  // Validation error on annotation creation
  http.post(`${API_BASE_URL}/resources/:resourceId/annotations`, () => {
    return HttpResponse.json(
      {
        code: 'VALIDATION_ERROR',
        message: 'Validation failed',
        timestamp: new Date().toISOString(),
        details: [
          {
            field: 'start_offset',
            message: 'start_offset must be less than end_offset',
          },
          {
            field: 'highlighted_text',
            message: 'highlighted_text is required',
          },
        ],
      },
      { status: 422 }
    );
  }),

  // Validation error on resource creation
  http.post(`${API_BASE_URL}/resources`, () => {
    return HttpResponse.json(
      {
        code: 'VALIDATION_ERROR',
        message: 'Validation failed',
        timestamp: new Date().toISOString(),
        details: [
          {
            field: 'url',
            message: 'url must be a valid URL',
          },
        ],
      },
      { status: 422 }
    );
  }),
];

// ============================================================================
// Combined Error Handlers
// ============================================================================

/**
 * All error handlers combined for easy testing
 */
export const allErrorHandlers = [
  ...unauthorizedHandlers,
  ...forbiddenHandlers,
  ...notFoundHandlers,
  ...rateLimitHandlers,
  ...serverErrorHandlers,
  ...networkErrorHandlers,
  ...timeoutHandlers,
  ...validationErrorHandlers,
];

/**
 * Helper to create a specific error handler for a given endpoint
 */
export function createErrorHandler(
  method: 'get' | 'post' | 'put' | 'delete',
  path: string,
  statusCode: 401 | 403 | 404 | 429 | 500,
  errorCode: string,
  message: string
) {
  const httpMethod = http[method];
  
  return httpMethod(`${API_BASE_URL}${path}`, () => {
    return HttpResponse.json(
      {
        code: errorCode,
        message,
        timestamp: new Date().toISOString(),
      },
      { status: statusCode }
    );
  });
}

/**
 * Helper to create a network error handler for a given endpoint
 */
export function createNetworkErrorHandler(
  method: 'get' | 'post' | 'put' | 'delete',
  path: string
) {
  const httpMethod = http[method];
  
  return httpMethod(`${API_BASE_URL}${path}`, () => {
    return HttpResponse.error();
  });
}

/**
 * Helper to create a timeout handler for a given endpoint
 */
export function createTimeoutHandler(
  method: 'get' | 'post' | 'put' | 'delete',
  path: string,
  delayMs: number = 10000
) {
  const httpMethod = http[method];
  
  return httpMethod(`${API_BASE_URL}${path}`, async () => {
    await delay(delayMs);
    return HttpResponse.json({ status: 'timeout' });
  });
}
