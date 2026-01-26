/**
 * Property-Based Tests for Authentication Token Persistence
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 12.1 - Property test for authentication persistence
 * Property 1: Authentication Token Persistence
 * Validates: Requirements 1.2
 * 
 * This test verifies that for any authenticated user session, if the user
 * refreshes the page, then the authentication token should persist and the
 * user should remain logged in.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import fc from 'fast-check';
import { setAuthToken, clearAuthToken, getAuthToken, apiClient } from '../client';

// ============================================================================
// Test Setup
// ============================================================================

describe('Property 1: Authentication Token Persistence', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Clear any existing auth headers
    delete apiClient.defaults.headers.common['Authorization'];
  });

  afterEach(() => {
    // Clean up after each test
    localStorage.clear();
    delete apiClient.defaults.headers.common['Authorization'];
  });

  // ==========================================================================
  // Arbitraries (Generators for Property-Based Testing)
  // ==========================================================================

  /**
   * Generate a valid JWT token structure
   * Format: header.payload.signature (base64url encoded)
   */
  const jwtTokenArbitrary = fc
    .tuple(
      fc.stringMatching(/^[A-Za-z0-9_-]{20,40}$/), // header
      fc.stringMatching(/^[A-Za-z0-9_-]{50,200}$/), // payload
      fc.stringMatching(/^[A-Za-z0-9_-]{40,60}$/) // signature
    )
    .map(([header, payload, signature]) => `${header}.${payload}.${signature}`);

  /**
   * Generate a simple alphanumeric token
   */
  const simpleTokenArbitrary = fc.stringMatching(/^[A-Za-z0-9]{32,128}$/);

  /**
   * Generate any valid token (JWT or simple)
   */
  const tokenArbitrary = fc.oneof(jwtTokenArbitrary, simpleTokenArbitrary);

  // ==========================================================================
  // Property Tests
  // ==========================================================================

  /**
   * Property: For any valid token, setting it should persist to localStorage
   * and be retrievable after a simulated page refresh.
   */
  it('should persist authentication token across page refresh', () => {
    fc.assert(
      fc.property(tokenArbitrary, (token) => {
        // Feature: phase2.5-backend-api-integration, Property 1: Authentication Token Persistence

        // Step 1: Set authentication token
        setAuthToken(token);

        // Step 2: Verify token is stored in localStorage
        const storedToken = localStorage.getItem('access_token');
        expect(storedToken).toBe(token);

        // Step 3: Verify token is set in axios headers
        expect(apiClient.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);

        // Step 4: Simulate page refresh by retrieving token
        const retrievedToken = getAuthToken();

        // Step 5: Verify token persists after "refresh"
        expect(retrievedToken).toBe(token);
        expect(retrievedToken).toBe(storedToken);

        // Property: Token should be identical before and after refresh
        expect(retrievedToken).not.toBeNull();
        expect(retrievedToken).toBe(token);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Property: For any valid token, after setting and clearing,
   * the token should not persist across page refresh.
   */
  it('should not persist authentication token after logout', () => {
    fc.assert(
      fc.property(tokenArbitrary, (token) => {
        // Feature: phase2.5-backend-api-integration, Property 1: Authentication Token Persistence

        // Step 1: Set authentication token
        setAuthToken(token);

        // Step 2: Verify token is set
        expect(getAuthToken()).toBe(token);

        // Step 3: Clear authentication token (logout)
        clearAuthToken();

        // Step 4: Verify token is removed from localStorage
        const storedToken = localStorage.getItem('access_token');
        expect(storedToken).toBeNull();

        // Step 5: Verify token is removed from axios headers
        expect(apiClient.defaults.headers.common['Authorization']).toBeUndefined();

        // Step 6: Simulate page refresh by retrieving token
        const retrievedToken = getAuthToken();

        // Property: Token should be null after logout and refresh
        expect(retrievedToken).toBeNull();
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Property: For any sequence of token updates, the most recent token
   * should always be the one that persists.
   */
  it('should always persist the most recent authentication token', () => {
    fc.assert(
      fc.property(fc.array(tokenArbitrary, { minLength: 2, maxLength: 10 }), (tokens) => {
        // Feature: phase2.5-backend-api-integration, Property 1: Authentication Token Persistence

        // Step 1: Set each token in sequence
        tokens.forEach((token) => {
          setAuthToken(token);
        });

        // Step 2: Get the last token (most recent)
        const lastToken = tokens[tokens.length - 1];

        // Step 3: Verify the last token is stored
        const storedToken = localStorage.getItem('access_token');
        expect(storedToken).toBe(lastToken);

        // Step 4: Verify the last token is in axios headers
        expect(apiClient.defaults.headers.common['Authorization']).toBe(`Bearer ${lastToken}`);

        // Step 5: Simulate page refresh
        const retrievedToken = getAuthToken();

        // Property: Only the most recent token should persist
        expect(retrievedToken).toBe(lastToken);
        expect(retrievedToken).not.toBe(tokens[0]); // Not the first token (unless array has 1 element)
      }),
      { numRuns: 50 }
    );
  });

  /**
   * Property: For any valid token, the token should be included in
   * subsequent API requests after being set.
   */
  it('should include authentication token in API request headers', () => {
    fc.assert(
      fc.property(tokenArbitrary, (token) => {
        // Feature: phase2.5-backend-api-integration, Property 1: Authentication Token Persistence

        // Step 1: Set authentication token
        setAuthToken(token);

        // Step 2: Create a mock request config
        const mockConfig = {
          url: '/test',
          method: 'GET',
          headers: {
            ...apiClient.defaults.headers.common,
          },
        };

        // Step 3: Verify Authorization header is set
        expect(mockConfig.headers['Authorization']).toBe(`Bearer ${token}`);

        // Property: Token should be in request headers
        expect(mockConfig.headers['Authorization']).toContain(token);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Property: For any valid token, after multiple page refreshes (simulated),
   * the token should remain consistent.
   */
  it('should maintain token consistency across multiple page refreshes', () => {
    fc.assert(
      fc.property(
        tokenArbitrary,
        fc.integer({ min: 2, max: 10 }),
        (token, refreshCount) => {
          // Feature: phase2.5-backend-api-integration, Property 1: Authentication Token Persistence

          // Step 1: Set authentication token
          setAuthToken(token);

          // Step 2: Simulate multiple page refreshes
          const retrievedTokens: (string | null)[] = [];
          for (let i = 0; i < refreshCount; i++) {
            retrievedTokens.push(getAuthToken());
          }

          // Property: All retrieved tokens should be identical
          retrievedTokens.forEach((retrievedToken) => {
            expect(retrievedToken).toBe(token);
          });

          // Verify all tokens are the same
          const allSame = retrievedTokens.every((t) => t === token);
          expect(allSame).toBe(true);
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: For any valid token, localStorage and axios headers
   * should always be in sync.
   */
  it('should keep localStorage and axios headers in sync', () => {
    fc.assert(
      fc.property(tokenArbitrary, (token) => {
        // Feature: phase2.5-backend-api-integration, Property 1: Authentication Token Persistence

        // Step 1: Set authentication token
        setAuthToken(token);

        // Step 2: Get token from localStorage
        const storedToken = localStorage.getItem('access_token');

        // Step 3: Get token from axios headers
        const headerToken = apiClient.defaults.headers.common['Authorization'];

        // Property: localStorage and headers should be in sync
        expect(storedToken).toBe(token);
        expect(headerToken).toBe(`Bearer ${token}`);

        // Verify they represent the same token
        expect(headerToken).toContain(storedToken!);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Property: For any valid token, clearing should remove from both
   * localStorage and axios headers.
   */
  it('should clear token from both localStorage and axios headers', () => {
    fc.assert(
      fc.property(tokenArbitrary, (token) => {
        // Feature: phase2.5-backend-api-integration, Property 1: Authentication Token Persistence

        // Step 1: Set authentication token
        setAuthToken(token);

        // Step 2: Verify token is set
        expect(localStorage.getItem('access_token')).toBe(token);
        expect(apiClient.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);

        // Step 3: Clear authentication token
        clearAuthToken();

        // Property: Both localStorage and headers should be cleared
        expect(localStorage.getItem('access_token')).toBeNull();
        expect(apiClient.defaults.headers.common['Authorization']).toBeUndefined();

        // Verify refresh_token is also cleared
        expect(localStorage.getItem('refresh_token')).toBeNull();

        // Verify neo-alexandria-auth is also cleared
        expect(localStorage.getItem('neo-alexandria-auth')).toBeNull();
      }),
      { numRuns: 100 }
    );
  });
});
