/**
 * Error Handling Tests
 */

import { describe, it, expect } from 'vitest';
import { APIError, handleAPIError, getErrorMessage } from '../errors';

describe('APIError', () => {
  it('should create error with all properties', () => {
    const error = new APIError(404, 'NOT_FOUND', 'Resource not found', { id: '123' });

    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(APIError);
    expect(error.statusCode).toBe(404);
    expect(error.code).toBe('NOT_FOUND');
    expect(error.message).toBe('Resource not found');
    expect(error.details).toEqual({ id: '123' });
  });

  describe('isNetworkError', () => {
    it('should identify network errors', () => {
      const error = new APIError(0, 'NETWORK_ERROR', 'Network failed');
      expect(error.isNetworkError()).toBe(true);
    });

    it('should not identify other errors as network errors', () => {
      const error = new APIError(404, 'NOT_FOUND', 'Not found');
      expect(error.isNetworkError()).toBe(false);
    });
  });

  describe('isClientError', () => {
    it('should identify 4xx errors', () => {
      expect(new APIError(400, 'BAD_REQUEST', 'Bad request').isClientError()).toBe(true);
      expect(new APIError(404, 'NOT_FOUND', 'Not found').isClientError()).toBe(true);
      expect(new APIError(403, 'FORBIDDEN', 'Forbidden').isClientError()).toBe(true);
    });

    it('should not identify other errors as client errors', () => {
      expect(new APIError(500, 'SERVER_ERROR', 'Server error').isClientError()).toBe(false);
      expect(new APIError(0, 'NETWORK_ERROR', 'Network error').isClientError()).toBe(false);
    });
  });

  describe('isServerError', () => {
    it('should identify 5xx errors', () => {
      expect(new APIError(500, 'SERVER_ERROR', 'Server error').isServerError()).toBe(true);
      expect(new APIError(502, 'BAD_GATEWAY', 'Bad gateway').isServerError()).toBe(true);
      expect(new APIError(503, 'UNAVAILABLE', 'Service unavailable').isServerError()).toBe(true);
    });

    it('should not identify other errors as server errors', () => {
      expect(new APIError(404, 'NOT_FOUND', 'Not found').isServerError()).toBe(false);
      expect(new APIError(0, 'NETWORK_ERROR', 'Network error').isServerError()).toBe(false);
    });
  });

  describe('getUserMessage', () => {
    it('should return user-friendly message for network errors', () => {
      const error = new APIError(0, 'NETWORK_ERROR', 'Network failed');
      expect(error.getUserMessage()).toContain('Connection lost');
    });

    it('should return user-friendly message for 404', () => {
      const error = new APIError(404, 'NOT_FOUND', 'Not found');
      expect(error.getUserMessage()).toContain('not found');
    });

    it('should return user-friendly message for 403', () => {
      const error = new APIError(403, 'FORBIDDEN', 'Forbidden');
      expect(error.getUserMessage()).toContain('permission');
    });

    it('should return user-friendly message for 401', () => {
      const error = new APIError(401, 'UNAUTHORIZED', 'Unauthorized');
      expect(error.getUserMessage()).toContain('log in');
    });

    it('should return user-friendly message for 5xx', () => {
      const error = new APIError(500, 'SERVER_ERROR', 'Server error');
      expect(error.getUserMessage()).toContain('went wrong');
    });

    it('should return original message for other errors', () => {
      const error = new APIError(418, 'TEAPOT', "I'm a teapot");
      expect(error.getUserMessage()).toBe("I'm a teapot");
    });
  });
});

describe('handleAPIError', () => {
  it('should return APIError as-is', () => {
    const originalError = new APIError(404, 'NOT_FOUND', 'Not found');
    const result = handleAPIError(originalError);
    expect(result).toBe(originalError);
  });

  it('should handle response errors', () => {
    const fetchError = {
      response: {
        status: 404,
        statusText: 'Not Found',
        data: {
          error: {
            code: 'RESOURCE_NOT_FOUND',
            message: 'Resource not found',
            details: { id: '123' },
          },
        },
      },
    };

    const result = handleAPIError(fetchError);

    expect(result).toBeInstanceOf(APIError);
    expect(result.statusCode).toBe(404);
    expect(result.code).toBe('RESOURCE_NOT_FOUND');
    expect(result.message).toBe('Resource not found');
    expect(result.details).toEqual({ id: '123' });
  });

  it('should handle response errors without error data', () => {
    const fetchError = {
      response: {
        status: 500,
        statusText: 'Internal Server Error',
        data: {},
      },
    };

    const result = handleAPIError(fetchError);

    expect(result).toBeInstanceOf(APIError);
    expect(result.statusCode).toBe(500);
    expect(result.code).toBe('UNKNOWN_ERROR');
    expect(result.message).toBe('Internal Server Error');
  });

  it('should handle network errors', () => {
    const fetchError = {
      request: {},
    };

    const result = handleAPIError(fetchError);

    expect(result).toBeInstanceOf(APIError);
    expect(result.statusCode).toBe(0);
    expect(result.code).toBe('NETWORK_ERROR');
    expect(result.isNetworkError()).toBe(true);
  });

  it('should handle unknown errors', () => {
    const unknownError = new Error('Something went wrong');

    const result = handleAPIError(unknownError);

    expect(result).toBeInstanceOf(APIError);
    expect(result.statusCode).toBe(0);
    expect(result.code).toBe('UNKNOWN_ERROR');
    expect(result.message).toBe('Something went wrong');
  });

  it('should handle errors without message', () => {
    const error = {};

    const result = handleAPIError(error);

    expect(result).toBeInstanceOf(APIError);
    expect(result.message).toBe('An unexpected error occurred');
  });
});

describe('getErrorMessage', () => {
  it('should return message for known error codes', () => {
    expect(getErrorMessage('NETWORK_ERROR')).toContain('Connection lost');
    expect(getErrorMessage('RESOURCE_NOT_FOUND')).toContain('not found');
    expect(getErrorMessage('UNAUTHORIZED')).toContain('log in');
  });

  it('should return fallback for unknown codes', () => {
    expect(getErrorMessage('UNKNOWN_CODE', 'Custom fallback')).toBe('Custom fallback');
  });

  it('should return default fallback for unknown codes', () => {
    expect(getErrorMessage('UNKNOWN_CODE')).toContain('unexpected error');
  });
});
