/**
 * API Utilities
 * Shared utilities for API clients including error handling
 */

import { ApiError } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Handle API errors and convert to ApiError instances
 * 
 * @param response - The failed fetch response
 * @throws {ApiError} Always throws an ApiError with details
 */
export async function handleApiError(response: Response): Promise<never> {
  let errorData: unknown;
  
  try {
    // Try to parse JSON error response
    errorData = await response.json();
  } catch {
    // Fallback to text if JSON parsing fails
    try {
      errorData = await response.text();
    } catch {
      errorData = null;
    }
  }

  // Extract error message from response
  const message = 
    typeof errorData === 'object' && errorData !== null && 'detail' in errorData
      ? String((errorData as { detail: unknown }).detail)
      : `API Error: ${response.status} ${response.statusText}`;

  throw new ApiError(message, response.status, errorData);
}

/**
 * Make an API request with automatic error handling
 * 
 * @param endpoint - API endpoint path (e.g., '/resources')
 * @param options - Fetch options
 * @returns Parsed JSON response
 * @throws {ApiError} On HTTP errors or network failures
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  } catch (error) {
    // Re-throw ApiError instances
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Wrap network errors and other exceptions
    if (error instanceof Error) {
      throw new ApiError(
        `Network error: ${error.message}`,
        0,
        { originalError: error.message }
      );
    }
    
    // Unknown error type
    throw new ApiError('An unknown error occurred', 0);
  }
}

/**
 * Check if an error is an ApiError instance
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/**
 * Get user-friendly error message from any error
 */
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'An unexpected error occurred';
}

/**
 * Check if error is a specific HTTP status code
 */
export function isHttpError(error: unknown, status: number): boolean {
  return isApiError(error) && error.status === status;
}

/**
 * Check if error is a 404 Not Found
 */
export function isNotFoundError(error: unknown): boolean {
  return isHttpError(error, 404);
}

/**
 * Check if error is a 401 Unauthorized
 */
export function isUnauthorizedError(error: unknown): boolean {
  return isHttpError(error, 401);
}

/**
 * Check if error is a 403 Forbidden
 */
export function isForbiddenError(error: unknown): boolean {
  return isHttpError(error, 403);
}

/**
 * Check if error is a 500 Internal Server Error
 */
export function isServerError(error: unknown): boolean {
  return isApiError(error) && error.status >= 500 && error.status < 600;
}

/**
 * Check if error is a network error (no response from server)
 */
export function isNetworkError(error: unknown): boolean {
  return isApiError(error) && error.status === 0;
}

export { API_BASE_URL };
