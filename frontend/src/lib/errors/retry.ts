/**
 * Retry strategy implementation
 */
import { classifyError, shouldRetry, calculateRetryDelay, type ClassifiedError } from './classification';

/**
 * Retry configuration
 */
export interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  onRetry?: (attempt: number, error: ClassifiedError) => void;
}

/**
 * Default retry configuration
 */
const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  baseDelay: 1000,
};

/**
 * Execute a function with retry logic
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  config: Partial<RetryConfig> = {}
): Promise<T> {
  const { maxAttempts, baseDelay, onRetry } = { ...DEFAULT_RETRY_CONFIG, ...config };
  let attemptCount = 0;

  while (true) {
    try {
      return await fn();
    } catch (error) {
      attemptCount++;
      const classifiedError = classifyError(error);

      // Check if we should retry
      if (!shouldRetry(classifiedError, attemptCount, maxAttempts)) {
        throw error;
      }

      // Call retry callback if provided
      if (onRetry) {
        onRetry(attemptCount, classifiedError);
      }

      // Calculate delay and wait
      const delay = calculateRetryDelay(attemptCount - 1, baseDelay);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

/**
 * Retry state for UI components
 */
export interface RetryState {
  isRetrying: boolean;
  attemptCount: number;
  maxAttempts: number;
  nextRetryIn?: number;
}

/**
 * Create retry state manager
 */
export function createRetryManager(maxAttempts: number = 3) {
  let state: RetryState = {
    isRetrying: false,
    attemptCount: 0,
    maxAttempts,
  };

  let countdownInterval: NodeJS.Timeout | null = null;

  return {
    getState: () => state,

    startRetry: (delayMs: number) => {
      state = {
        ...state,
        isRetrying: true,
        attemptCount: state.attemptCount + 1,
        nextRetryIn: Math.ceil(delayMs / 1000),
      };

      // Start countdown
      if (countdownInterval) {
        clearInterval(countdownInterval);
      }

      countdownInterval = setInterval(() => {
        if (state.nextRetryIn && state.nextRetryIn > 0) {
          state = {
            ...state,
            nextRetryIn: state.nextRetryIn - 1,
          };
        } else {
          if (countdownInterval) {
            clearInterval(countdownInterval);
            countdownInterval = null;
          }
        }
      }, 1000);
    },

    completeRetry: () => {
      if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
      }
      state = {
        ...state,
        isRetrying: false,
        nextRetryIn: undefined,
      };
    },

    reset: () => {
      if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
      }
      state = {
        isRetrying: false,
        attemptCount: 0,
        maxAttempts,
      };
    },

    canRetry: () => state.attemptCount < state.maxAttempts,
  };
}
