/**
 * Runtime Type Validation for API Responses
 * 
 * This module provides runtime validation of API responses using zod schemas.
 * Validation only runs in development mode to catch type mismatches between
 * frontend and backend without impacting production performance.
 * 
 * @see frontend/src/types/api.schemas.ts for zod schemas
 */

import { z } from 'zod';

/**
 * Validation error details
 */
export interface ValidationErrorDetails {
  path: string;
  expected: string;
  received: unknown;
  message: string;
}

/**
 * Validation result
 */
export interface ValidationResult<T> {
  success: boolean;
  data?: T;
  errors?: ValidationErrorDetails[];
}

/**
 * Format zod error for logging
 */
function formatZodError(error: z.ZodError): ValidationErrorDetails[] {
  return error.issues.map((issue) => ({
    path: issue.path.join('.'),
    expected: 'expected' in issue ? String(issue.expected) : issue.code,
    received: 'received' in issue ? issue.received : 'unknown',
    message: issue.message,
  }));
}

/**
 * Validate API response data against a zod schema
 * 
 * @param data - The data to validate
 * @param schema - The zod schema to validate against
 * @param endpoint - The API endpoint (for logging)
 * @returns Validation result with typed data or errors
 */
export function validateResponse<T>(
  data: unknown,
  schema: z.ZodSchema<T>,
  endpoint: string
): ValidationResult<T> {
  // Skip validation in production
  if (!import.meta.env.DEV) {
    return {
      success: true,
      data: data as T,
    };
  }

  try {
    const validated = schema.parse(data);
    return {
      success: true,
      data: validated,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = formatZodError(error);
      
      // Log validation error in development
      console.error(
        `[API Validation Error] ${endpoint}`,
        '\n\nValidation Errors:',
        errors,
        '\n\nReceived Data:',
        data,
        '\n\nExpected Schema:',
        schema
      );

      return {
        success: false,
        errors,
      };
    }

    // Re-throw non-zod errors
    throw error;
  }
}

/**
 * Validate API response and throw on validation failure
 * 
 * This is useful when you want to fail fast on validation errors
 * rather than handling them explicitly.
 * 
 * @param data - The data to validate
 * @param schema - The zod schema to validate against
 * @param endpoint - The API endpoint (for logging)
 * @returns The validated and typed data
 * @throws Error if validation fails in development mode
 */
export function validateResponseStrict<T>(
  data: unknown,
  schema: z.ZodSchema<T>,
  endpoint: string
): T {
  const result = validateResponse(data, schema, endpoint);

  if (!result.success) {
    throw new Error(
      `API response validation failed for ${endpoint}. ` +
      `See console for details. ` +
      `Errors: ${result.errors?.map(e => e.path).join(', ')}`
    );
  }

  return result.data!;
}

/**
 * Create a validated API response handler
 * 
 * This returns a function that validates responses for a specific endpoint
 * and schema, making it easy to add validation to API client methods.
 * 
 * @param endpoint - The API endpoint
 * @param schema - The zod schema to validate against
 * @returns A function that validates response data
 * 
 * @example
 * const validateUser = createValidator('/api/auth/me', UserSchema);
 * const user = validateUser(responseData);
 */
export function createValidator<T>(
  endpoint: string,
  schema: z.ZodSchema<T>
): (data: unknown) => T {
  return (data: unknown) => validateResponseStrict(data, schema, endpoint);
}

/**
 * Validate an array response
 * 
 * @param data - The array data to validate
 * @param itemSchema - The zod schema for array items
 * @param endpoint - The API endpoint (for logging)
 * @returns The validated and typed array
 */
export function validateArrayResponse<T>(
  data: unknown,
  itemSchema: z.ZodSchema<T>,
  endpoint: string
): T[] {
  const arraySchema = z.array(itemSchema);
  return validateResponseStrict(data, arraySchema, endpoint);
}

/**
 * Validate a paginated response
 * 
 * @param data - The paginated data to validate
 * @param itemSchema - The zod schema for array items
 * @param endpoint - The API endpoint (for logging)
 * @returns The validated and typed paginated response
 */
export function validatePaginatedResponse<T>(
  data: unknown,
  itemSchema: z.ZodSchema<T>,
  endpoint: string
): { items: T[]; total: number } {
  const paginatedSchema = z.object({
    items: z.array(itemSchema),
    total: z.number(),
  });
  return validateResponseStrict(data, paginatedSchema, endpoint);
}

/**
 * Log validation warning without throwing
 * 
 * Use this when you want to log validation errors but continue execution
 * with the unvalidated data (useful for non-critical endpoints).
 * 
 * @param data - The data to validate
 * @param schema - The zod schema to validate against
 * @param endpoint - The API endpoint (for logging)
 * @returns The original data (unvalidated)
 */
export function validateResponseSoft<T>(
  data: unknown,
  schema: z.ZodSchema<T>,
  endpoint: string
): unknown {
  const result = validateResponse(data, schema, endpoint);

  if (!result.success) {
    console.warn(
      `[API Validation Warning] ${endpoint} - Validation failed but continuing with unvalidated data`
    );
  }

  return data;
}

/**
 * Check if validation is enabled
 * 
 * @returns true if running in development mode
 */
export function isValidationEnabled(): boolean {
  return import.meta.env.DEV;
}
