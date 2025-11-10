// Neo Alexandria 2.0 Frontend - Error Handling Utilities
// Centralized error handling for API and application errors

import axios, { AxiosError } from 'axios';

export interface ErrorMessage {
  title: string;
  message: string;
  code: number;
}

/**
 * Handle API errors and convert them to user-friendly messages
 */
export function handleApiError(error: unknown): ErrorMessage {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    
    if (axiosError.response) {
      // Server responded with error status
      const status = axiosError.response.status;
      const detail = axiosError.response.data?.detail;
      
      // Customize messages based on status code
      switch (status) {
        case 400:
          return {
            title: 'Invalid Request',
            message: detail || 'The request contains invalid data',
            code: status,
          };
        case 401:
          return {
            title: 'Unauthorized',
            message: detail || 'You need to be authenticated to perform this action',
            code: status,
          };
        case 403:
          return {
            title: 'Forbidden',
            message: detail || 'You do not have permission to perform this action',
            code: status,
          };
        case 404:
          return {
            title: 'Not Found',
            message: detail || 'The requested resource was not found',
            code: status,
          };
        case 409:
          return {
            title: 'Conflict',
            message: detail || 'The request conflicts with existing data',
            code: status,
          };
        case 422:
          return {
            title: 'Validation Error',
            message: detail || 'The provided data failed validation',
            code: status,
          };
        case 429:
          return {
            title: 'Too Many Requests',
            message: detail || 'Please slow down and try again later',
            code: status,
          };
        case 500:
          return {
            title: 'Server Error',
            message: detail || 'An internal server error occurred',
            code: status,
          };
        case 503:
          return {
            title: 'Service Unavailable',
            message: detail || 'The service is temporarily unavailable',
            code: status,
          };
        default:
          return {
            title: 'Request Failed',
            message: detail || 'An error occurred while processing your request',
            code: status,
          };
      }
    } else if (axiosError.request) {
      // Request was made but no response received
      return {
        title: 'Network Error',
        message: 'Unable to reach the server. Please check your connection.',
        code: 0,
      };
    }
  }
  
  // Unknown error type
  if (error instanceof Error) {
    return {
      title: 'Unexpected Error',
      message: error.message,
      code: -1,
    };
  }
  
  return {
    title: 'Unexpected Error',
    message: 'An unexpected error occurred',
    code: -1,
  };
}

/**
 * Format error for display in UI
 */
export function formatErrorMessage(error: unknown): string {
  const errorMsg = handleApiError(error);
  return `${errorMsg.title}: ${errorMsg.message}`;
}

/**
 * Get a short error message (just the message part)
 */
export function getErrorMessage(error: unknown): string {
  const errorMsg = handleApiError(error);
  return errorMsg.message;
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return !error.response && !!error.request;
  }
  return false;
}

/**
 * Check if error is an authentication error
 */
export function isAuthError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.response?.status === 401;
  }
  return false;
}

/**
 * Check if error is a not found error
 */
export function isNotFoundError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.response?.status === 404;
  }
  return false;
}

/**
 * Check if error is a validation error
 */
export function isValidationError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.response?.status === 422 || error.response?.status === 400;
  }
  return false;
}

/**
 * Check if error is a server error
 */
export function isServerError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    return !!status && status >= 500;
  }
  return false;
}
