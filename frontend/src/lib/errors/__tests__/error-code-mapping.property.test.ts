/**
 * Property-based tests for error code mapping
 * 
 * Property 4: Error Code Mapping
 * For any HTTP error status code, the frontend should map it to a user-friendly
 * error message and appropriate action (retry, redirect, or display).
 * 
 * Validates: Requirements 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
 */
import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import axios, { AxiosError } from 'axios';
import {
  classifyError,
  ErrorCategory,
  ErrorSeverity,
  formatError,
  getErrorMessage,
  getErrorAction,
} from '../index';

/**
 * Create a mock AxiosError with a specific status code
 */
function createAxiosError(statusCode: number, message: string = 'Error'): AxiosError {
  const error = new Error(message) as AxiosError;
  error.isAxiosError = true;
  error.response = {
    status: statusCode,
    statusText: message,
    headers: {},
    config: {} as any,
    data: { detail: message },
  };
  error.config = {} as any;
  error.toJSON = () => ({});
  return error;
}

describe('Property 4: Error Code Mapping', () => {
  describe('401 Unauthorized errors', () => {
    it('should always map 401 to authentication category', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            // Execute: Classify 401 error
            const error = createAxiosError(401, message);
            const classified = classifyError(error);
            
            // Verify: Mapped to authentication category
            expect(classified.category).toBe(ErrorCategory.AUTHENTICATION);
            expect(classified.statusCode).toBe(401);
            expect(classified.retryable).toBe(false);
            expect(classified.severity).toBe(ErrorSeverity.CRITICAL);
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should provide user-friendly message for 401 errors', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(401, message);
            const classified = classifyError(error);
            const userMessage = getErrorMessage(classified);
            
            // Verify: User-friendly message
            expect(userMessage).toBeTruthy();
            expect(userMessage.length).toBeGreaterThan(0);
            expect(userMessage).toContain('session');
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('403 Forbidden errors', () => {
    it('should always map 403 to authorization category', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(403, message);
            const classified = classifyError(error);
            
            // Verify: Mapped to authorization category
            expect(classified.category).toBe(ErrorCategory.AUTHORIZATION);
            expect(classified.statusCode).toBe(403);
            expect(classified.retryable).toBe(false);
            expect(classified.severity).toBe(ErrorSeverity.HIGH);
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should provide access denied message for 403 errors', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(403, message);
            const classified = classifyError(error);
            const userMessage = getErrorMessage(classified);
            
            // Verify: Access denied message
            expect(userMessage).toBeTruthy();
            expect(userMessage.toLowerCase()).toContain('permission');
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('404 Not Found errors', () => {
    it('should always map 404 to not_found category', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(404, message);
            const classified = classifyError(error);
            
            // Verify: Mapped to not_found category
            expect(classified.category).toBe(ErrorCategory.NOT_FOUND);
            expect(classified.statusCode).toBe(404);
            expect(classified.retryable).toBe(false);
            expect(classified.severity).toBe(ErrorSeverity.MEDIUM);
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should provide not found message for 404 errors', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(404, message);
            const classified = classifyError(error);
            const userMessage = getErrorMessage(classified);
            
            // Verify: Not found message
            expect(userMessage).toBeTruthy();
            expect(userMessage.toLowerCase()).toMatch(/not found|could not be found/);
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('429 Rate Limit errors', () => {
    it('should always map 429 to rate_limit category', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 300 }),
          (retryAfter) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(429, 'Rate limit exceeded');
            error.response!.headers['retry-after'] = String(retryAfter);
            const classified = classifyError(error);
            
            // Verify: Mapped to rate_limit category
            expect(classified.category).toBe(ErrorCategory.RATE_LIMIT);
            expect(classified.statusCode).toBe(429);
            expect(classified.retryable).toBe(true);
            expect(classified.severity).toBe(ErrorSeverity.MEDIUM);
            expect(classified.retryAfter).toBe(retryAfter);
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should provide rate limit message for 429 errors', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 300 }),
          (retryAfter) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(429, 'Rate limit exceeded');
            error.response!.headers['retry-after'] = String(retryAfter);
            const classified = classifyError(error);
            const userMessage = getErrorMessage(classified);
            
            // Verify: Rate limit message with retry time
            expect(userMessage).toBeTruthy();
            expect(userMessage.toLowerCase()).toContain('request');
            expect(userMessage).toContain(String(retryAfter));
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('5xx Server errors', () => {
    it('should always map 5xx to server_error category', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 500, max: 599 }),
          fc.string({ minLength: 1, maxLength: 100 }),
          (statusCode, message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(statusCode, message);
            const classified = classifyError(error);
            
            // Verify: Mapped to server_error category
            expect(classified.category).toBe(ErrorCategory.SERVER_ERROR);
            expect(classified.statusCode).toBe(statusCode);
            expect(classified.retryable).toBe(true);
            expect(classified.severity).toBe(ErrorSeverity.HIGH);
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should provide server error message for 5xx errors', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 500, max: 599 }),
          (statusCode) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(statusCode, 'Server error');
            const classified = classifyError(error);
            const userMessage = getErrorMessage(classified);
            
            // Verify: Server error message
            expect(userMessage).toBeTruthy();
            expect(userMessage.toLowerCase()).toContain('server');
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('Network errors', () => {
    it('should always map network errors to network_error category', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            // Create error without response (network error)
            const error = new Error(message) as AxiosError;
            error.isAxiosError = true;
            error.config = {} as any;
            error.toJSON = () => ({});
            
            const classified = classifyError(error);
            
            // Verify: Mapped to network_error category
            expect(classified.category).toBe(ErrorCategory.NETWORK_ERROR);
            expect(classified.retryable).toBe(true);
            expect(classified.severity).toBe(ErrorSeverity.HIGH);
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should provide connection error message for network errors', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 100 }),
          (message) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = new Error(message) as AxiosError;
            error.isAxiosError = true;
            error.config = {} as any;
            error.toJSON = () => ({});
            
            const classified = classifyError(error);
            const userMessage = getErrorMessage(classified);
            
            // Verify: Connection error message
            expect(userMessage).toBeTruthy();
            expect(userMessage.toLowerCase()).toContain('connection');
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('Error action mapping', () => {
    it('should provide appropriate action for each error category', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(401, 403, 404, 429, 500, 503),
          (statusCode) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(statusCode, 'Error');
            const classified = classifyError(error);
            const action = getErrorAction(classified);
            
            // Verify: Action is provided and non-empty
            expect(action).toBeTruthy();
            expect(action.length).toBeGreaterThan(0);
            
            // Verify: Action matches category
            if (classified.retryable) {
              expect(action.toLowerCase()).toMatch(/retry|wait/);
            }
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('Formatted error output', () => {
    it('should always provide complete formatted error for any status code', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 400, max: 599 }),
          (statusCode) => {
            // Feature: phase2.5-backend-api-integration, Property 4: Error Code Mapping
            
            const error = createAxiosError(statusCode, 'Error');
            const classified = classifyError(error);
            const formatted = formatError(classified);
            
            // Verify: All required fields are present
            expect(formatted.title).toBeTruthy();
            expect(formatted.message).toBeTruthy();
            expect(formatted.action).toBeTruthy();
            expect(formatted.icon).toBeTruthy();
            expect(typeof formatted.retryable).toBe('boolean');
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
