/**
 * Error classification and handling utilities
 */
import type { AxiosError } from 'axios';

/**
 * Error categories for classification
 */
export enum ErrorCategory {
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  NOT_FOUND = 'not_found',
  RATE_LIMIT = 'rate_limit',
  SERVER_ERROR = 'server_error',
  NETWORK_ERROR = 'network_error',
  VALIDATION_ERROR = 'validation_error',
  UNKNOWN = 'unknown',
}

/**
 * Error severity levels
 */
export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Classified error with metadata
 */
export interface ClassifiedError {
  category: ErrorCategory;
  severity: ErrorSeverity;
  message: string;
  userMessage: string;
  statusCode?: number;
  retryable: boolean;
  retryAfter?: number;
  originalError: Error;
}

/**
 * Classify an error based on its properties
 */
export function classifyError(error: unknown): ClassifiedError {
  // Handle Axios errors
  if (isAxiosError(error)) {
    return classifyAxiosError(error);
  }

  // Handle generic errors
  if (error instanceof Error) {
    return {
      category: ErrorCategory.UNKNOWN,
      severity: ErrorSeverity.MEDIUM,
      message: error.message,
      userMessage: 'An unexpected error occurred. Please try again.',
      retryable: false,
      originalError: error,
    };
  }

  // Handle unknown error types
  return {
    category: ErrorCategory.UNKNOWN,
    severity: ErrorSeverity.MEDIUM,
    message: String(error),
    userMessage: 'An unexpected error occurred. Please try again.',
    retryable: false,
    originalError: new Error(String(error)),
  };
}

/**
 * Type guard for Axios errors
 */
function isAxiosError(error: unknown): error is AxiosError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'isAxiosError' in error &&
    (error as AxiosError).isAxiosError === true
  );
}

/**
 * Classify Axios-specific errors
 */
function classifyAxiosError(error: AxiosError): ClassifiedError {
  const statusCode = error.response?.status;

  // Network errors (no response)
  if (!error.response) {
    return {
      category: ErrorCategory.NETWORK_ERROR,
      severity: ErrorSeverity.HIGH,
      message: error.message,
      userMessage: 'Connection lost. Please check your internet connection and try again.',
      retryable: true,
      originalError: error,
    };
  }

  // Classify by status code
  switch (statusCode) {
    case 401:
      return {
        category: ErrorCategory.AUTHENTICATION,
        severity: ErrorSeverity.CRITICAL,
        message: 'Authentication failed',
        userMessage: 'Your session has expired. Please log in again.',
        statusCode,
        retryable: false,
        originalError: error,
      };

    case 403:
      return {
        category: ErrorCategory.AUTHORIZATION,
        severity: ErrorSeverity.HIGH,
        message: 'Access denied',
        userMessage: 'You do not have permission to access this resource.',
        statusCode,
        retryable: false,
        originalError: error,
      };

    case 404:
      return {
        category: ErrorCategory.NOT_FOUND,
        severity: ErrorSeverity.MEDIUM,
        message: 'Resource not found',
        userMessage: 'The requested resource could not be found.',
        statusCode,
        retryable: false,
        originalError: error,
      };

    case 429:
      const retryAfter = error.response.headers['retry-after'];
      return {
        category: ErrorCategory.RATE_LIMIT,
        severity: ErrorSeverity.MEDIUM,
        message: 'Rate limit exceeded',
        userMessage: retryAfter
          ? `Too many requests. Please wait ${retryAfter} seconds before trying again.`
          : 'Too many requests. Please wait a moment before trying again.',
        statusCode,
        retryable: true,
        retryAfter: retryAfter ? parseInt(retryAfter, 10) : undefined,
        originalError: error,
      };

    case 400:
    case 422:
      return {
        category: ErrorCategory.VALIDATION_ERROR,
        severity: ErrorSeverity.LOW,
        message: 'Validation error',
        userMessage: extractValidationMessage(error),
        statusCode,
        retryable: false,
        originalError: error,
      };

    default:
      // 5xx server errors
      if (statusCode && statusCode >= 500) {
        return {
          category: ErrorCategory.SERVER_ERROR,
          severity: ErrorSeverity.HIGH,
          message: 'Server error',
          userMessage: 'The server encountered an error. Please try again in a moment.',
          statusCode,
          retryable: true,
          originalError: error,
        };
      }

      // Unknown status codes
      return {
        category: ErrorCategory.UNKNOWN,
        severity: ErrorSeverity.MEDIUM,
        message: error.message,
        userMessage: 'An unexpected error occurred. Please try again.',
        statusCode,
        retryable: false,
        originalError: error,
      };
  }
}

/**
 * Extract validation error message from response
 */
function extractValidationMessage(error: AxiosError): string {
  const data = error.response?.data as any;

  // Try to extract detail message
  if (data?.detail) {
    if (typeof data.detail === 'string') {
      return data.detail;
    }
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: any) => d.msg || d.message || String(d)).join(', ');
    }
  }

  // Try to extract message
  if (data?.message) {
    return data.message;
  }

  return 'Invalid request. Please check your input and try again.';
}

/**
 * Determine if an error should be retried
 */
export function shouldRetry(error: ClassifiedError, attemptCount: number, maxAttempts: number): boolean {
  // Don't retry if max attempts reached
  if (attemptCount >= maxAttempts) {
    return false;
  }

  // Only retry if error is marked as retryable
  return error.retryable;
}

/**
 * Calculate retry delay with exponential backoff
 */
export function calculateRetryDelay(attemptCount: number, baseDelay: number = 1000): number {
  const delay = baseDelay * Math.pow(2, attemptCount);
  const jitter = Math.random() * 0.3 * delay; // Add 0-30% jitter
  return Math.min(delay + jitter, 30000); // Cap at 30 seconds
}
