/**
 * API Error Handling
 * 
 * Custom error classes and error handling utilities
 */

export class APIError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'APIError';
    
    // Maintains proper stack trace for where error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, APIError);
    }
  }

  /**
   * Check if error is a network error (no response from server)
   */
  isNetworkError(): boolean {
    return this.statusCode === 0 && this.code === 'NETWORK_ERROR';
  }

  /**
   * Check if error is a client error (4xx)
   */
  isClientError(): boolean {
    return this.statusCode >= 400 && this.statusCode < 500;
  }

  /**
   * Check if error is a server error (5xx)
   */
  isServerError(): boolean {
    return this.statusCode >= 500 && this.statusCode < 600;
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage(): string {
    if (this.isNetworkError()) {
      return 'Connection lost. Please check your internet connection.';
    }

    if (this.statusCode === 404) {
      return 'Resource not found. It may have been deleted.';
    }

    if (this.statusCode === 403) {
      return "You don't have permission to access this resource.";
    }

    if (this.statusCode === 401) {
      return 'Please log in to continue.';
    }

    if (this.isServerError()) {
      return 'Something went wrong on our end. Please try again later.';
    }

    // Return the original message for other errors
    return this.message;
  }
}

/**
 * Handle errors from fetch/axios and convert to APIError
 */
export function handleAPIError(error: any): APIError {
  // If it's already an APIError, return it
  if (error instanceof APIError) {
    return error;
  }

  // Handle fetch Response errors
  if (error.response) {
    const response = error.response;
    const data = response.data || {};
    
    return new APIError(
      response.status,
      data.error?.code || 'UNKNOWN_ERROR',
      data.error?.message || response.statusText || 'An error occurred',
      data.error?.details
    );
  }

  // Handle network errors (no response)
  if (error.request) {
    return new APIError(
      0,
      'NETWORK_ERROR',
      'Network connection failed. Please check your internet connection.'
    );
  }

  // Handle other errors
  return new APIError(
    0,
    'UNKNOWN_ERROR',
    error.message || 'An unexpected error occurred'
  );
}

/**
 * User-friendly error messages by error code
 */
export const ERROR_MESSAGES: Record<string, string> = {
  NETWORK_ERROR: 'Connection lost. Please check your internet.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  RESOURCE_NOT_FOUND: 'Resource not found.',
  COLLECTION_NOT_FOUND: 'Collection not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UNAUTHORIZED: 'Please log in to continue.',
  FORBIDDEN: "You don't have permission to perform this action.",
  SERVER_ERROR: 'Something went wrong. Please try again later.',
  UNKNOWN_ERROR: 'An unexpected error occurred.',
};

/**
 * Get user-friendly message for error code
 */
export function getErrorMessage(code: string, fallback?: string): string {
  return ERROR_MESSAGES[code] || fallback || ERROR_MESSAGES.UNKNOWN_ERROR;
}
