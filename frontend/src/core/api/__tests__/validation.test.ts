/**
 * Tests for Runtime Type Validation
 * 
 * Validates that the validation utility correctly validates API responses
 * against zod schemas in development mode.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { z } from 'zod';
import {
  validateResponse,
  validateResponseStrict,
  validateArrayResponse,
  validatePaginatedResponse,
  validateResponseSoft,
  createValidator,
  isValidationEnabled,
} from '../validation';

describe('Runtime Type Validation', () => {
  // Save original NODE_ENV
  const originalEnv = import.meta.env.DEV;

  beforeEach(() => {
    // Mock console methods to avoid noise in tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('validateResponse', () => {
    const TestSchema = z.object({
      id: z.string(),
      name: z.string(),
      count: z.number(),
    });

    it('should validate correct data successfully', () => {
      const data = { id: '123', name: 'Test', count: 42 };
      const result = validateResponse(data, TestSchema, '/test');

      expect(result.success).toBe(true);
      expect(result.data).toEqual(data);
      expect(result.errors).toBeUndefined();
    });

    it('should return validation errors for incorrect data', () => {
      const data = { id: '123', name: 'Test', count: 'not-a-number' };
      const result = validateResponse(data, TestSchema, '/test');

      expect(result.success).toBe(false);
      expect(result.data).toBeUndefined();
      expect(result.errors).toBeDefined();
      expect(result.errors).toHaveLength(1);
      expect(result.errors![0].path).toBe('count');
    });

    it('should return validation errors for missing required fields', () => {
      const data = { id: '123', name: 'Test' };
      const result = validateResponse(data, TestSchema, '/test');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors![0].path).toBe('count');
    });

    it('should log validation errors to console in dev mode', () => {
      const data = { id: '123', name: 'Test', count: 'invalid' };
      validateResponse(data, TestSchema, '/test');

      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining('[API Validation Error] /test'),
        expect.anything(),
        expect.anything(),
        expect.anything(),
        expect.anything(),
        expect.anything(),
        expect.anything()
      );
    });
  });

  describe('validateResponseStrict', () => {
    const TestSchema = z.object({
      id: z.string(),
      value: z.number(),
    });

    it('should return validated data for correct input', () => {
      const data = { id: '123', value: 42 };
      const result = validateResponseStrict(data, TestSchema, '/test');

      expect(result).toEqual(data);
    });

    it('should throw error for invalid data', () => {
      const data = { id: '123', value: 'invalid' };

      expect(() => {
        validateResponseStrict(data, TestSchema, '/test');
      }).toThrow('API response validation failed for /test');
    });

    it('should include error details in thrown error', () => {
      const data = { id: 123, value: 'invalid' };

      expect(() => {
        validateResponseStrict(data, TestSchema, '/test');
      }).toThrow(/id, value/);
    });
  });

  describe('validateArrayResponse', () => {
    const ItemSchema = z.object({
      id: z.string(),
      name: z.string(),
    });

    it('should validate array of items successfully', () => {
      const data = [
        { id: '1', name: 'Item 1' },
        { id: '2', name: 'Item 2' },
      ];
      const result = validateArrayResponse(data, ItemSchema, '/test');

      expect(result).toEqual(data);
    });

    it('should throw error for invalid array items', () => {
      const data = [
        { id: '1', name: 'Item 1' },
        { id: 2, name: 'Item 2' }, // Invalid: id should be string
      ];

      expect(() => {
        validateArrayResponse(data, ItemSchema, '/test');
      }).toThrow();
    });

    it('should validate empty array', () => {
      const data: unknown[] = [];
      const result = validateArrayResponse(data, ItemSchema, '/test');

      expect(result).toEqual([]);
    });
  });

  describe('validatePaginatedResponse', () => {
    const ItemSchema = z.object({
      id: z.string(),
      value: z.number(),
    });

    it('should validate paginated response successfully', () => {
      const data = {
        items: [
          { id: '1', value: 10 },
          { id: '2', value: 20 },
        ],
        total: 2,
      };
      const result = validatePaginatedResponse(data, ItemSchema, '/test');

      expect(result).toEqual(data);
    });

    it('should throw error for missing total field', () => {
      const data = {
        items: [{ id: '1', value: 10 }],
      };

      expect(() => {
        validatePaginatedResponse(data, ItemSchema, '/test');
      }).toThrow();
    });

    it('should throw error for invalid items', () => {
      const data = {
        items: [{ id: 1, value: 10 }], // Invalid: id should be string
        total: 1,
      };

      expect(() => {
        validatePaginatedResponse(data, ItemSchema, '/test');
      }).toThrow();
    });
  });

  describe('validateResponseSoft', () => {
    const TestSchema = z.object({
      id: z.string(),
      name: z.string(),
    });

    it('should return data without throwing for valid input', () => {
      const data = { id: '123', name: 'Test' };
      const result = validateResponseSoft(data, TestSchema, '/test');

      expect(result).toEqual(data);
      expect(console.warn).not.toHaveBeenCalled();
    });

    it('should log warning but return data for invalid input', () => {
      const data = { id: 123, name: 'Test' };
      const result = validateResponseSoft(data, TestSchema, '/test');

      expect(result).toEqual(data);
      expect(console.warn).toHaveBeenCalledWith(
        expect.stringContaining('[API Validation Warning] /test')
      );
    });
  });

  describe('createValidator', () => {
    const TestSchema = z.object({
      id: z.string(),
      count: z.number(),
    });

    it('should create a validator function', () => {
      const validator = createValidator('/test', TestSchema);

      expect(typeof validator).toBe('function');
    });

    it('should validate data using created validator', () => {
      const validator = createValidator('/test', TestSchema);
      const data = { id: '123', count: 42 };
      const result = validator(data);

      expect(result).toEqual(data);
    });

    it('should throw error for invalid data', () => {
      const validator = createValidator('/test', TestSchema);
      const data = { id: '123', count: 'invalid' };

      expect(() => validator(data)).toThrow();
    });
  });

  describe('isValidationEnabled', () => {
    it('should return true in development mode', () => {
      expect(isValidationEnabled()).toBe(true);
    });
  });

  describe('Error formatting', () => {
    const TestSchema = z.object({
      user: z.object({
        name: z.string(),
        age: z.number(),
      }),
      tags: z.array(z.string()),
    });

    it('should format nested path errors correctly', () => {
      const data = {
        user: { name: 'John', age: 'invalid' },
        tags: ['tag1', 'tag2'],
      };
      const result = validateResponse(data, TestSchema, '/test');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors![0].path).toBe('user.age');
    });

    it('should format array path errors correctly', () => {
      const data = {
        user: { name: 'John', age: 25 },
        tags: ['tag1', 123, 'tag3'], // Invalid: 123 should be string
      };
      const result = validateResponse(data, TestSchema, '/test');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors![0].path).toContain('tags');
    });
  });

  describe('Complex schema validation', () => {
    const ComplexSchema = z.object({
      id: z.string(),
      status: z.enum(['pending', 'completed', 'failed']),
      metadata: z.object({
        created_at: z.string(),
        updated_at: z.string(),
      }),
      items: z.array(z.object({
        name: z.string(),
        value: z.number(),
      })),
      optional_field: z.string().optional(),
    });

    it('should validate complex nested structure', () => {
      const data = {
        id: '123',
        status: 'completed',
        metadata: {
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
        },
        items: [
          { name: 'Item 1', value: 10 },
          { name: 'Item 2', value: 20 },
        ],
      };
      const result = validateResponse(data, ComplexSchema, '/test');

      expect(result.success).toBe(true);
      expect(result.data).toEqual(data);
    });

    it('should validate with optional fields present', () => {
      const data = {
        id: '123',
        status: 'pending',
        metadata: {
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
        },
        items: [],
        optional_field: 'present',
      };
      const result = validateResponse(data, ComplexSchema, '/test');

      expect(result.success).toBe(true);
    });

    it('should fail validation for invalid enum value', () => {
      const data = {
        id: '123',
        status: 'invalid-status',
        metadata: {
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
        },
        items: [],
      };
      const result = validateResponse(data, ComplexSchema, '/test');

      expect(result.success).toBe(false);
      expect(result.errors![0].path).toBe('status');
    });
  });
});
