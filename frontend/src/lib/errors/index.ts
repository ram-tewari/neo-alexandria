/**
 * Error handling utilities
 * 
 * This module provides comprehensive error handling for API calls:
 * - Error classification by category and severity
 * - User-friendly error messages
 * - Retry strategies with exponential backoff
 * - Circuit breaker pattern for failing endpoints
 */

export {
  ErrorCategory,
  ErrorSeverity,
  classifyError,
  shouldRetry,
  calculateRetryDelay,
  type ClassifiedError,
} from './classification';

export {
  getErrorMessage,
  getErrorAction,
  getErrorTitle,
  getErrorIcon,
  formatError,
  formatRetryCountdown,
  formatErrorForLogging,
  type FormattedError,
} from './messages';

export {
  withRetry,
  createRetryManager,
  type RetryConfig,
  type RetryState,
} from './retry';

export {
  CircuitState,
  CircuitBreaker,
  CircuitBreakerError,
  createCircuitBreaker,
  getCircuitBreaker,
  resetAllCircuitBreakers,
  type CircuitBreakerConfig,
} from './circuit-breaker';
