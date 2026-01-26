/**
 * Property-Based Tests for Type Safety at Runtime
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 12.3 - Property test for type safety
 * Property 6: Type Safety at Runtime
 * Validates: Requirements 7.5
 * 
 * This test verifies that for any API response, if the response does not match
 * the expected TypeScript type, then the frontend should throw a validation
 * error in development mode.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import fc from 'fast-check';
import { z } from 'zod';
import {
  validateResponse,
  validateResponseStrict,
  validateArrayResponse,
  validatePaginatedResponse,
  validateResponseSoft,
  isValidationEnabled,
  createValidator,
} from '../validation';
import {
  UserSchema,
  ResourceSchema,
  AnnotationSchema,
  SemanticChunkSchema,
  QualityDetailsSchema,
} from '@/types/api.schemas';

// ============================================================================
// Test Setup
// ============================================================================

describe('Property 6: Type Safety at Runtime', () => {
  // Store original NODE_ENV
  const originalEnv = import.meta.env.DEV;

  beforeEach(() => {
    // Ensure we're in development mode for validation
    vi.stubEnv('DEV', true);
  });

  afterEach(() => {
    // Restore original environment
    vi.unstubAllEnvs();
  });

  // ==========================================================================
  // Arbitraries (Generators for Property-Based Testing)
  // ==========================================================================

  /**
   * Generate a valid user object matching UserSchema
   */
  const validUserArbitrary = fc.record({
    id: fc.string({ minLength: 1, maxLength: 50 }).filter((s) => s.trim().length > 0),
    username: fc.string({ minLength: 1, maxLength: 50 }).filter((s) => s.trim().length > 0),
    email: fc.emailAddress().filter((email) => {
      // Ensure email passes zod's email validation
      try {
        z.string().email().parse(email);
        return true;
      } catch {
        return false;
      }
    }),
    tier: fc.constantFrom('free', 'premium', 'admin'),
    is_active: fc.boolean(),
  });

  /**
   * Generate an invalid user object (missing required fields)
   */
  const invalidUserArbitrary = fc.oneof(
    // Missing id
    fc.record({
      username: fc.string(),
      email: fc.emailAddress(),
      tier: fc.constantFrom('free', 'premium', 'admin'),
      is_active: fc.boolean(),
    }),
    // Invalid email
    fc.record({
      id: fc.string(),
      username: fc.string(),
      email: fc.string().filter((s) => !s.includes('@')),
      tier: fc.constantFrom('free', 'premium', 'admin'),
      is_active: fc.boolean(),
    }),
    // Invalid tier
    fc.record({
      id: fc.string(),
      username: fc.string(),
      email: fc.emailAddress(),
      tier: fc.string().filter((s) => !['free', 'premium', 'admin'].includes(s)),
      is_active: fc.boolean(),
    }),
    // Wrong type for is_active
    fc.record({
      id: fc.string(),
      username: fc.string(),
      email: fc.emailAddress(),
      tier: fc.constantFrom('free', 'premium', 'admin'),
      is_active: fc.string(),
    })
  );

  /**
   * Generate a valid resource object matching ResourceSchema
   */
  const validResourceArbitrary = fc.record({
    id: fc.string({ minLength: 1 }),
    title: fc.string({ minLength: 1 }),
    created_at: fc.date().map((d) => d.toISOString()),
    updated_at: fc.date().map((d) => d.toISOString()),
    ingestion_status: fc.constantFrom('pending', 'processing', 'completed', 'failed'),
  });

  /**
   * Generate an invalid resource object
   */
  const invalidResourceArbitrary = fc.oneof(
    // Missing required fields
    fc.record({
      title: fc.string(),
    }),
    // Invalid ingestion_status
    fc.record({
      id: fc.string(),
      title: fc.string(),
      created_at: fc.date().map((d) => d.toISOString()),
      updated_at: fc.date().map((d) => d.toISOString()),
      ingestion_status: fc.string().filter(
        (s) => !['pending', 'processing', 'completed', 'failed'].includes(s) && s.length > 0
      ),
    }),
    // Invalid date format
    fc.record({
      id: fc.string(),
      title: fc.string(),
      created_at: fc.string().filter((s) => s.length > 0 && isNaN(Date.parse(s))),
      updated_at: fc.date().map((d) => d.toISOString()),
      ingestion_status: fc.constantFrom('pending', 'processing', 'completed', 'failed'),
    })
  );

  /**
   * Generate a simple schema for testing
   */
  const simpleSchema = z.object({
    id: z.string(),
    name: z.string(),
    count: z.number(),
  });

  const validSimpleObjectArbitrary = fc.record({
    id: fc.string({ minLength: 1 }),
    name: fc.string({ minLength: 1 }),
    count: fc.integer(),
  });

  const invalidSimpleObjectArbitrary = fc.oneof(
    // Missing fields
    fc.record({
      id: fc.string(),
    }),
    // Wrong type for count
    fc.record({
      id: fc.string(),
      name: fc.string(),
      count: fc.string(),
    })
    // Note: Extra fields are allowed by zod's default behavior, so we don't test that
  );

  // ==========================================================================
  // Property Tests
  // ==========================================================================

  /**
   * Property: For any valid data matching the schema, validation should succeed
   * and return the typed data.
   */
  it('should validate and return data for valid responses', () => {
    fc.assert(
      fc.property(validUserArbitrary, (validUser) => {
        // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

        // Execute: Validate valid user data
        const result = validateResponse(validUser, UserSchema, '/api/auth/me');

        // Verify: Validation succeeds
        expect(result.success).toBe(true);
        expect(result.data).toEqual(validUser);
        expect(result.errors).toBeUndefined();
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Property: For any invalid data not matching the schema, validation should
   * fail and return error details in development mode.
   */
  it('should fail validation for invalid responses in development mode', () => {
    fc.assert(
      fc.property(invalidUserArbitrary, (invalidUser) => {
        // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

        // Execute: Validate invalid user data
        const result = validateResponse(invalidUser, UserSchema, '/api/auth/me');

        // Verify: Validation fails
        expect(result.success).toBe(false);
        expect(result.data).toBeUndefined();
        expect(result.errors).toBeDefined();
        expect(result.errors!.length).toBeGreaterThan(0);

        // Verify error details are provided
        result.errors!.forEach((error) => {
          expect(error.path).toBeDefined();
          expect(error.message).toBeDefined();
        });
      }),
      { numRuns: 50 }
    );
  });

  /**
   * Property: For any data, validateResponseStrict should throw an error
   * if validation fails in development mode.
   */
  it('should throw error for invalid responses with strict validation', () => {
    fc.assert(
      fc.property(invalidSimpleObjectArbitrary, (invalidData) => {
        // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

        // Execute & Verify: Strict validation throws on invalid data
        expect(() => {
          validateResponseStrict(invalidData, simpleSchema, '/api/test');
        }).toThrow();
      }),
      { numRuns: 50 }
    );
  });

  /**
   * Property: For any valid data, validateResponseStrict should return
   * the typed data without throwing.
   */
  it('should return typed data for valid responses with strict validation', () => {
    fc.assert(
      fc.property(validSimpleObjectArbitrary, (validData) => {
        // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

        // Execute: Strict validation on valid data
        const result = validateResponseStrict(validData, simpleSchema, '/api/test');

        // Verify: Returns typed data
        expect(result).toEqual(validData);
        expect(result.id).toBe(validData.id);
        expect(result.name).toBe(validData.name);
        expect(result.count).toBe(validData.count);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Property: For any array of valid items, validateArrayResponse should
   * return the typed array.
   */
  it('should validate arrays of valid items', () => {
    fc.assert(
      fc.property(
        fc.array(validUserArbitrary, { minLength: 0, maxLength: 10 }),
        (validUsers) => {
          // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

          // Execute: Validate array of users
          const result = validateArrayResponse(validUsers, UserSchema, '/api/users');

          // Verify: Returns typed array
          expect(result).toEqual(validUsers);
          expect(result.length).toBe(validUsers.length);

          // Verify each item is typed correctly
          result.forEach((user, index) => {
            expect(user.id).toBe(validUsers[index].id);
            expect(user.email).toBe(validUsers[index].email);
          });
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: For any array containing invalid items, validateArrayResponse
   * should throw an error.
   */
  it('should throw error for arrays with invalid items', () => {
    fc.assert(
      fc.property(
        fc.array(invalidUserArbitrary, { minLength: 1, maxLength: 5 }),
        (invalidUsers) => {
          // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

          // Execute & Verify: Array validation throws on invalid items
          expect(() => {
            validateArrayResponse(invalidUsers, UserSchema, '/api/users');
          }).toThrow();
        }
      ),
      { numRuns: 30 }
    );
  });

  /**
   * Property: For any valid paginated response, validatePaginatedResponse
   * should return the typed paginated data.
   */
  it('should validate paginated responses', () => {
    fc.assert(
      fc.property(
        fc.array(validResourceArbitrary, { minLength: 0, maxLength: 10 }),
        fc.nat({ max: 1000 }),
        (validResources, total) => {
          // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

          const paginatedData = {
            items: validResources,
            total,
          };

          // Execute: Validate paginated response
          const result = validatePaginatedResponse(
            paginatedData,
            ResourceSchema,
            '/api/resources'
          );

          // Verify: Returns typed paginated data
          expect(result.items).toEqual(validResources);
          expect(result.total).toBe(total);
          expect(result.items.length).toBe(validResources.length);
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: For any invalid paginated response, validatePaginatedResponse
   * should throw an error.
   */
  it('should throw error for invalid paginated responses', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          // Missing items
          fc.record({
            total: fc.nat(),
          }),
          // Missing total
          fc.record({
            items: fc.array(validResourceArbitrary),
          }),
          // Invalid items (at least one invalid item)
          fc.record({
            items: fc.array(invalidResourceArbitrary, { minLength: 1 }),
            total: fc.nat(),
          }),
          // Wrong type for total
          fc.record({
            items: fc.array(validResourceArbitrary),
            total: fc.string(),
          })
        ),
        (invalidPaginatedData) => {
          // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

          // Execute & Verify: Paginated validation throws on invalid data
          expect(() => {
            validatePaginatedResponse(
              invalidPaginatedData,
              ResourceSchema,
              '/api/resources'
            );
          }).toThrow();
        }
      ),
      { numRuns: 30 }
    );
  });

  /**
   * Property: For any data, validateResponseSoft should never throw,
   * even for invalid data.
   */
  it('should not throw for invalid responses with soft validation', () => {
    fc.assert(
      fc.property(
        fc.oneof(validSimpleObjectArbitrary, invalidSimpleObjectArbitrary),
        (data) => {
          // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

          // Execute: Soft validation should not throw
          const result = validateResponseSoft(data, simpleSchema, '/api/test');

          // Verify: Returns original data (even if invalid)
          expect(result).toEqual(data);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: For any schema and endpoint, createValidator should return
   * a function that validates data against that schema.
   */
  it('should create validators that validate against the schema', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 50 }),
        validSimpleObjectArbitrary,
        (endpoint, validData) => {
          // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

          // Execute: Create validator
          const validator = createValidator(endpoint, simpleSchema);

          // Verify: Validator validates data
          const result = validator(validData);
          expect(result).toEqual(validData);
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: For any schema and endpoint, createValidator should return
   * a function that throws for invalid data.
   */
  it('should create validators that throw for invalid data', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 50 }),
        invalidSimpleObjectArbitrary,
        (endpoint, invalidData) => {
          // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

          // Execute: Create validator
          const validator = createValidator(endpoint, simpleSchema);

          // Verify: Validator throws for invalid data
          expect(() => {
            validator(invalidData);
          }).toThrow();
        }
      ),
      { numRuns: 30 }
    );
  });

  /**
   * Property: isValidationEnabled should return true in development mode.
   */
  it('should report validation as enabled in development mode', () => {
    // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

    // Verify: Validation is enabled in dev mode
    expect(isValidationEnabled()).toBe(true);
  });

  /**
   * Property: For any valid data, validation should preserve the exact
   * structure and values of the data.
   */
  it('should preserve data structure and values after validation', () => {
    fc.assert(
      fc.property(validUserArbitrary, (validUser) => {
        // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

        // Execute: Validate data
        const result = validateResponseStrict(validUser, UserSchema, '/api/auth/me');

        // Verify: Data is preserved exactly
        expect(result).toEqual(validUser);
        expect(JSON.stringify(result)).toBe(JSON.stringify(validUser));

        // Verify no extra properties added
        expect(Object.keys(result).sort()).toEqual(Object.keys(validUser).sort());
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Property: For any validation error, the error details should include
   * the path to the invalid field.
   */
  it('should provide path information in validation errors', () => {
    fc.assert(
      fc.property(invalidUserArbitrary, (invalidUser) => {
        // Feature: phase2.5-backend-api-integration, Property 6: Type Safety at Runtime

        // Execute: Validate invalid data
        const result = validateResponse(invalidUser, UserSchema, '/api/auth/me');

        // Verify: Error details include path
        if (!result.success) {
          expect(result.errors).toBeDefined();
          result.errors!.forEach((error) => {
            expect(typeof error.path).toBe('string');
            expect(error.message).toBeTruthy();
          });
        }
      }),
      { numRuns: 50 }
    );
  });
});
