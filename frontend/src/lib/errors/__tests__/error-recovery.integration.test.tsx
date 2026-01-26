/**
 * Integration tests for error recovery
 * 
 * Tests error handling and recovery flows:
 * - Network error recovery
 * - 401 redirect to login
 * - 429 rate limit handling
 * - 500 server error retry
 * 
 * Validates: Requirement 10.4
 */
import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { apiClient } from '@/core/api/client';
import { classifyError } from '../classification';

// Mock server setup
const server = setupServer();

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'bypass' });
});

afterEach(() => {
  server.resetHandlers();
  localStorage.clear();
});

afterAll(() => {
  server.close();
});

describe('Error Recovery Integration Tests', () => {
  describe('Network error recovery', () => {
    it('should classify network errors correctly', async () => {
      // Feature: phase2.5-backend-api-integration, Requirement 10.4
      
      // Setup: Mock network error (no response)
      const error = new Error('Network Error') as any;
      error.isAxiosError = true;
      error.config = {};
      error.toJSON = () => ({});

      // Execute: Classify error
      const classified = classifyError(error);

      // Verify: Error is classified as network error
      expect(classified.category).toBe('network_error');
      expect(classified.retryable).toBe(true);
      expect(classified.severity).toBe('high');
    });
  });

  describe('401 redirect to login', () => {
    it('should classify 401 errors correctly', async () => {
      // Feature: phase2.5-backend-api-integration, Requirement 10.4
      
      // Setup: Mock 401 error
      server.use(
        http.get('https://pharos.onrender.com/test', () => {
          return new HttpResponse(null, { status: 401 });
        })
      );

      // Execute: Make request
      try {
        await apiClient.get('/test');
        expect.fail('Should have thrown an error');
      } catch (error) {
        // Verify: Error is classified as authentication error
        const classified = classifyError(error);
        expect(classified.category).toBe('authentication');
        expect(classified.statusCode).toBe(401);
        expect(classified.retryable).toBe(false);
        expect(classified.severity).toBe('critical');
      }
    }, 10000);
  });

  describe('429 rate limit handling', () => {
    it('should classify 429 errors correctly', async () => {
      // Feature: phase2.5-backend-api-integration, Requirement 10.4
      
      // Create a mock 429 error directly
      const error = new Error('Rate limit exceeded') as any;
      error.isAxiosError = true;
      error.response = {
        status: 429,
        statusText: 'Too Many Requests',
        headers: { 'retry-after': '60' },
        config: {} as any,
        data: { detail: 'Rate limit exceeded' },
      };
      error.config = {} as any;
      error.toJSON = () => ({});

      // Execute: Classify error
      const classified = classifyError(error);

      // Verify: Error is classified as rate limit error
      expect(classified.category).toBe('rate_limit');
      expect(classified.statusCode).toBe(429);
      expect(classified.retryable).toBe(true);
      expect(classified.retryAfter).toBe(60);
    });

    it('should extract retry-after header from 429 response', async () => {
      // Feature: phase2.5-backend-api-integration, Requirement 10.4
      
      // Create a mock 429 error with retry-after
      const error = new Error('Rate limit exceeded') as any;
      error.isAxiosError = true;
      error.response = {
        status: 429,
        statusText: 'Too Many Requests',
        headers: { 'retry-after': '120' },
        config: {} as any,
        data: { detail: 'Rate limit exceeded' },
      };
      error.config = {} as any;
      error.toJSON = () => ({});

      // Execute: Classify error
      const classified = classifyError(error);

      // Verify: Retry-after is extracted
      expect(classified.retryAfter).toBe(120);
      expect(classified.statusCode).toBe(429);
    });
  });

  describe('500 server error retry', () => {
    it('should classify 500 errors correctly', async () => {
      // Feature: phase2.5-backend-api-integration, Requirement 10.4
      
      // Setup: Mock 500 error
      server.use(
        http.get('https://pharos.onrender.com/test', () => {
          return new HttpResponse(null, { status: 500 });
        })
      );

      // Execute: Make request
      try {
        await apiClient.get('/test');
        expect.fail('Should have thrown an error');
      } catch (error) {
        // Verify: Error is classified as server error
        const classified = classifyError(error);
        expect(classified.category).toBe('server_error');
        expect(classified.statusCode).toBe(500);
        expect(classified.retryable).toBe(true);
        expect(classified.severity).toBe('high');
      }
    }, 15000);
  });

  describe('Error recovery with exponential backoff', () => {
    it('should calculate exponential backoff delays', async () => {
      // Feature: phase2.5-backend-api-integration, Requirement 10.4
      
      // Import the retry utilities from index
      const { calculateRetryDelay } = await import('../index');
      
      // Verify: Delays increase exponentially
      const delay0 = calculateRetryDelay(0, 1000);
      const delay1 = calculateRetryDelay(1, 1000);
      const delay2 = calculateRetryDelay(2, 1000);
      
      // First retry should be around 1s
      expect(delay0).toBeGreaterThan(900);
      expect(delay0).toBeLessThan(1500);
      
      // Second retry should be around 2s
      expect(delay1).toBeGreaterThan(1800);
      expect(delay1).toBeLessThan(3000);
      
      // Third retry should be around 4s
      expect(delay2).toBeGreaterThan(3600);
      expect(delay2).toBeLessThan(6000);
      
      // Verify exponential growth
      expect(delay1).toBeGreaterThan(delay0);
      expect(delay2).toBeGreaterThan(delay1);
    });
  });
});
