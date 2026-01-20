/**
 * Property-Based Testing Helpers
 * 
 * Generators and utilities for property-based testing with fast-check
 */

import * as fc from 'fast-check';

/**
 * Generate a random JWT token structure
 */
export const jwtArbitrary = fc.record({
  sub: fc.string({ minLength: 1, maxLength: 50 }),
  email: fc.emailAddress(),
  exp: fc.integer({ min: Math.floor(Date.now() / 1000), max: Math.floor(Date.now() / 1000) + 86400 }),
  iat: fc.integer({ min: Math.floor(Date.now() / 1000) - 3600, max: Math.floor(Date.now() / 1000) }),
  roles: fc.array(fc.constantFrom('user', 'admin', 'moderator'), { maxLength: 3 }),
});

/**
 * Generate random rate limit values
 */
export const rateLimitArbitrary = fc.record({
  limit: fc.integer({ min: 10, max: 10000 }),
  remaining: fc.integer({ min: 0, max: 10000 }),
  reset: fc.integer({ min: Math.floor(Date.now() / 1000), max: Math.floor(Date.now() / 1000) + 86400 }),
});

/**
 * Generate random API response
 */
export const apiResponseArbitrary = <T>(dataArbitrary: fc.Arbitrary<T>) =>
  fc.record({
    data: dataArbitrary,
    status: fc.constantFrom(200, 201, 204),
    statusText: fc.constant('OK'),
  });

/**
 * Generate random API error response
 */
export const apiErrorArbitrary = fc.record({
  detail: fc.string({ minLength: 1, maxLength: 200 }),
  error_code: fc.constantFrom(
    'VALIDATION_ERROR',
    'NOT_FOUND',
    'UNAUTHORIZED',
    'RATE_LIMIT_EXCEEDED'
  ),
  status: fc.constantFrom(400, 401, 404, 429, 500),
});

/**
 * Generate random resource data
 */
export const resourceArbitrary = fc.record({
  id: fc.uuid(),
  title: fc.string({ minLength: 1, maxLength: 200 }),
  url: fc.webUrl(),
  description: fc.option(fc.string({ maxLength: 500 }), { nil: null }),
  created_at: fc.date().map((d) => d.toISOString()),
  updated_at: fc.date().map((d) => d.toISOString()),
});

/**
 * Generate random collection data
 */
export const collectionArbitrary = fc.record({
  id: fc.uuid(),
  name: fc.string({ minLength: 1, maxLength: 100 }),
  description: fc.option(fc.string({ maxLength: 500 }), { nil: null }),
  resource_count: fc.integer({ min: 0, max: 1000 }),
  created_at: fc.date().map((d) => d.toISOString()),
});

/**
 * Generate random annotation data
 */
export const annotationArbitrary = fc.record({
  id: fc.uuid(),
  resource_id: fc.uuid(),
  text: fc.string({ minLength: 1, maxLength: 1000 }),
  start_offset: fc.integer({ min: 0, max: 10000 }),
  end_offset: fc.integer({ min: 0, max: 10000 }),
  note: fc.option(fc.string({ maxLength: 500 }), { nil: null }),
  tags: fc.array(fc.string({ minLength: 1, maxLength: 50 }), { maxLength: 10 }),
  created_at: fc.date().map((d) => d.toISOString()),
});

/**
 * Generate random search query
 */
export const searchQueryArbitrary = fc.record({
  query: fc.string({ minLength: 1, maxLength: 200 }),
  limit: fc.integer({ min: 1, max: 100 }),
  offset: fc.integer({ min: 0, max: 1000 }),
  filters: fc.option(
    fc.record({
      category: fc.option(fc.string(), { nil: undefined }),
      tags: fc.option(fc.array(fc.string()), { nil: undefined }),
    }),
    { nil: undefined }
  ),
});

/**
 * Generate random request history entry
 */
export const requestHistoryArbitrary = fc.record({
  id: fc.uuid(),
  method: fc.constantFrom('GET', 'POST', 'PUT', 'DELETE'),
  url: fc.webUrl(),
  status: fc.integer({ min: 200, max: 599 }),
  timestamp: fc.date().map((d) => d.getTime()),
  duration: fc.integer({ min: 10, max: 5000 }),
  module: fc.constantFrom(
    'resources',
    'search',
    'collections',
    'annotations',
    'taxonomy'
  ),
});

/**
 * Generate non-empty whitespace string
 */
export const whitespaceStringArbitrary = fc
  .array(fc.constantFrom(' ', '\t', '\n', '\r'), { minLength: 1, maxLength: 20 })
  .map((chars) => chars.join(''));

/**
 * Generate valid task description (non-whitespace)
 */
export const validTaskDescriptionArbitrary = fc
  .string({ minLength: 1, maxLength: 500 })
  .filter((s) => s.trim().length > 0);

/**
 * Property test configuration
 */
export const propertyTestConfig = {
  numRuns: 100, // Minimum 100 iterations as per testing strategy
  verbose: true,
};
