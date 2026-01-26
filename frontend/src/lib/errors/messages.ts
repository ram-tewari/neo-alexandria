/**
 * Error message mapping and formatting
 */
import { ErrorCategory, ErrorSeverity, type ClassifiedError } from './classification';

/**
 * Error message templates by category
 */
const ERROR_MESSAGES: Record<ErrorCategory, string> = {
  [ErrorCategory.AUTHENTICATION]: 'Your session has expired. Please log in again.',
  [ErrorCategory.AUTHORIZATION]: 'You do not have permission to access this resource.',
  [ErrorCategory.NOT_FOUND]: 'The requested resource could not be found.',
  [ErrorCategory.RATE_LIMIT]: 'Too many requests. Please wait before trying again.',
  [ErrorCategory.SERVER_ERROR]: 'The server encountered an error. Please try again.',
  [ErrorCategory.NETWORK_ERROR]: 'Connection lost. Please check your internet connection.',
  [ErrorCategory.VALIDATION_ERROR]: 'Invalid request. Please check your input.',
  [ErrorCategory.UNKNOWN]: 'An unexpected error occurred. Please try again.',
};

/**
 * Error action messages by category
 */
const ERROR_ACTIONS: Record<ErrorCategory, string> = {
  [ErrorCategory.AUTHENTICATION]: 'Log in',
  [ErrorCategory.AUTHORIZATION]: 'Contact support',
  [ErrorCategory.NOT_FOUND]: 'Go back',
  [ErrorCategory.RATE_LIMIT]: 'Wait and retry',
  [ErrorCategory.SERVER_ERROR]: 'Retry',
  [ErrorCategory.NETWORK_ERROR]: 'Retry',
  [ErrorCategory.VALIDATION_ERROR]: 'Fix input',
  [ErrorCategory.UNKNOWN]: 'Retry',
};

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: ClassifiedError): string {
  return error.userMessage || ERROR_MESSAGES[error.category];
}

/**
 * Get error action text
 */
export function getErrorAction(error: ClassifiedError): string {
  return ERROR_ACTIONS[error.category];
}

/**
 * Get error title by category
 */
export function getErrorTitle(category: ErrorCategory): string {
  switch (category) {
    case ErrorCategory.AUTHENTICATION:
      return 'Authentication Required';
    case ErrorCategory.AUTHORIZATION:
      return 'Access Denied';
    case ErrorCategory.NOT_FOUND:
      return 'Not Found';
    case ErrorCategory.RATE_LIMIT:
      return 'Rate Limit Exceeded';
    case ErrorCategory.SERVER_ERROR:
      return 'Server Error';
    case ErrorCategory.NETWORK_ERROR:
      return 'Connection Error';
    case ErrorCategory.VALIDATION_ERROR:
      return 'Validation Error';
    case ErrorCategory.UNKNOWN:
      return 'Error';
  }
}

/**
 * Get error icon by severity
 */
export function getErrorIcon(severity: ErrorSeverity): string {
  switch (severity) {
    case ErrorSeverity.LOW:
      return 'ℹ️';
    case ErrorSeverity.MEDIUM:
      return '⚠️';
    case ErrorSeverity.HIGH:
      return '❌';
    case ErrorSeverity.CRITICAL:
      return '🚨';
  }
}

/**
 * Format error for display
 */
export interface FormattedError {
  title: string;
  message: string;
  action: string;
  icon: string;
  retryable: boolean;
  retryAfter?: number;
}

/**
 * Format classified error for UI display
 */
export function formatError(error: ClassifiedError): FormattedError {
  return {
    title: getErrorTitle(error.category),
    message: getErrorMessage(error),
    action: getErrorAction(error),
    icon: getErrorIcon(error.severity),
    retryable: error.retryable,
    retryAfter: error.retryAfter,
  };
}

/**
 * Format retry countdown message
 */
export function formatRetryCountdown(seconds: number): string {
  if (seconds <= 0) {
    return 'Ready to retry';
  }
  if (seconds === 1) {
    return 'Retry in 1 second';
  }
  return `Retry in ${seconds} seconds`;
}

/**
 * Format error for logging
 */
export function formatErrorForLogging(error: ClassifiedError): string {
  const parts = [
    `[${error.category.toUpperCase()}]`,
    error.statusCode ? `HTTP ${error.statusCode}` : '',
    error.message,
  ].filter(Boolean);

  return parts.join(' - ');
}
