/**
 * API type definitions
 */

/**
 * API error response
 */
export interface ApiError {
  detail: string;
  status: number;
  retryAfter?: number;
}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}
