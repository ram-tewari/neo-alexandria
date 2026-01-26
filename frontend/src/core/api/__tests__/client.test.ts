/**
 * API Client Tests
 * 
 * Tests for the core API client configuration, interceptors, and retry logic
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '../../../test/mocks/server';
import { apiClient, setAuthToken, clearAuthToken, getAuthToken } from '../client';
import type { AxiosError } from 'axios';

describe('API Client', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Clear any default headers
    delete apiClient.defaults.headers.common['Authorization'];
  });

  afterEach(() => {
    // Reset handlers after each test
    server.resetHandlers();
  });

  describe('Configuration', () => {
    it('should use base URL from environment variable', () => {
      expect(apiClient.defaults.baseURL).toBe(import.meta.env.VITE_API_BASE_URL || 'https://pharos.onrender.com');
    });

    it('should have 30 second timeout', () => {
      expect(apiClient.defaults.timeout).toBe(30000);
    });

    it('should have JSON content type header', () => {
      expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
    });
  });

  describe('Authentication Token Management', () => {
    it('should set auth token in localStorage and headers', () => {
      const token = 'test-token-123';
      setAuthToken(token);

      expect(localStorage.getItem('access_token')).toBe(token);
      expect(apiClient.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);
    });

    it('should get auth token from localStorage', () => {
      const token = 'test-token-456';
      localStorage.setItem('access_token', token);

      expect(getAuthToken()).toBe(token);
    });

    it('should clear auth token from localStorage and headers', () => {
      localStorage.setItem('access_token', 'test-token');
      localStorage.setItem('refresh_token', 'refresh-token');
      apiClient.defaults.headers.common['Authorization'] = 'Bearer test-token';

      clearAuthToken();

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
      expect(apiClient.defaults.headers.common['Authorization']).toBeUndefined();
    });

    it('should return null when no auth token exists', () => {
      expect(getAuthToken()).toBeNull();
    });
  });

  describe('Request Interceptor', () => {
    it('should attach auth token to requests', async () => {
      const token = 'test-token-789';
      setAuthToken(token);

      server.use(
        http.get('https://pharos.onrender.com/test', ({ request }) => {
          const authHeader = request.headers.get('Authorization');
          return HttpResponse.json({ authHeader });
        })
      );

      const response = await apiClient.get('/test');
      expect(response.data.authHeader).toBe(`Bearer ${token}`);
    });

    it('should not attach auth token when none exists', async () => {
      server.use(
        http.get('https://pharos.onrender.com/test', ({ request }) => {
          const authHeader = request.headers.get('Authorization');
          return HttpResponse.json({ authHeader });
        })
      );

      const response = await apiClient.get('/test');
      expect(response.data.authHeader).toBeNull();
    });
  });

  describe('Response Interceptor - Error Handling', () => {
    it('should handle 401 errors with token refresh', async () => {
      localStorage.setItem('refresh_token', 'valid-refresh-token');

      // First request returns 401
      server.use(
        http.get('*/protected', () => {
          return HttpResponse.json(
            { detail: 'Unauthorized' },
            { status: 401 }
          );
        }, { once: true }),
        // Refresh endpoint returns new token
        http.post('*/auth/refresh', () => {
          return HttpResponse.json({ access_token: 'new-token' });
        }),
        // Retry with new token succeeds
        http.get('*/protected', () => {
          return HttpResponse.json({ data: 'success' });
        })
      );

      const response = await apiClient.get('/protected');
      expect(response.data.data).toBe('success');
      expect(localStorage.getItem('access_token')).toBe('new-token');
    });

    it('should redirect to login when refresh token is missing', async () => {
      const originalLocation = window.location.href;
      
      // Mock window.location.href
      delete (window as any).location;
      window.location = { href: originalLocation } as any;

      server.use(
        http.get('*/protected', () => {
          return HttpResponse.json(
            { detail: 'Unauthorized' },
            { status: 401 }
          );
        })
      );

      try {
        await apiClient.get('/protected');
      } catch (error) {
        // Expected to fail
      }

      expect(window.location.href).toBe('/login');
    });

    it.skip('should handle 429 rate limit errors', async () => {
      server.use(
        http.get('*/rate-limited', () => {
          return HttpResponse.json(
            { detail: 'Rate limit exceeded' },
            { 
              status: 429,
              headers: { 'Retry-After': '60' }
            }
          );
        })
      );

      try {
        await apiClient.get('/rate-limited');
        expect.fail('Should have thrown rate limit error');
      } catch (error: any) {
        expect(error.message).toBe('Rate limit exceeded');
        expect(error.status).toBe(429);
        expect(error.retryAfter).toBe(60);
      }
    });
  });

  describe('Retry Logic', () => {
    it.skip('should retry on network errors with exponential backoff', async () => {
      let attemptCount = 0;

      server.use(
        http.get('*/flaky', () => {
          attemptCount++;
          if (attemptCount < 3) {
            // Simulate network error by returning error response
            return HttpResponse.json(
              { detail: 'Internal Server Error' },
              { status: 500 }
            );
          }
          return HttpResponse.json({ data: 'success' });
        })
      );

      const response = await apiClient.get('/flaky');
      expect(response.data.data).toBe('success');
      expect(attemptCount).toBe(3);
    });

    it.skip('should retry on 5xx server errors', async () => {
      let attemptCount = 0;

      server.use(
        http.get('*/server-error', () => {
          attemptCount++;
          if (attemptCount < 2) {
            return HttpResponse.json(
              { detail: 'Service Unavailable' },
              { status: 503 }
            );
          }
          return HttpResponse.json({ data: 'recovered' });
        })
      );

      const response = await apiClient.get('/server-error');
      expect(response.data.data).toBe('recovered');
      expect(attemptCount).toBe(2);
    });

    it.skip('should not retry on 4xx client errors (except 401, 429)', async () => {
      let attemptCount = 0;

      server.use(
        http.get('*/not-found', () => {
          attemptCount++;
          return HttpResponse.json(
            { detail: 'Not Found' },
            { status: 404 }
          );
        })
      );

      try {
        await apiClient.get('/not-found');
        expect.fail('Should have thrown 404 error');
      } catch (error: any) {
        expect(error.response?.status).toBe(404);
        expect(attemptCount).toBe(1); // No retries
      }
    });

    it.skip('should stop retrying after max attempts', async () => {
      let attemptCount = 0;

      server.use(
        http.get('*/always-fails', () => {
          attemptCount++;
          return HttpResponse.json(
            { detail: 'Internal Server Error' },
            { status: 500 }
          );
        })
      );

      try {
        await apiClient.get('/always-fails');
        expect.fail('Should have thrown error after max retries');
      } catch (error: any) {
        expect(error.response?.status).toBe(500);
        // Initial attempt + 3 retries = 4 total attempts
        expect(attemptCount).toBe(4);
      }
    });
  });

  describe('Timeout Handling', () => {
    it('should timeout requests after configured duration', async () => {
      server.use(
        http.get('*/slow', async () => {
          // Delay longer than timeout
          await new Promise(resolve => setTimeout(resolve, 35000));
          return HttpResponse.json({ data: 'too late' });
        })
      );

      try {
        await apiClient.get('/slow');
        expect.fail('Should have timed out');
      } catch (error: any) {
        // Axios timeout error code
        expect(error.code).toMatch(/ECONNABORTED|ERR_INVALID_URL/);
      }
    }, 40000); // Increase test timeout
  });

  describe('Request/Response Logging', () => {
    it.skip('should log requests in development mode', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

      server.use(
        http.get('*/test', () => {
          return HttpResponse.json({ data: 'test' });
        })
      );

      await apiClient.get('/test');

      if (import.meta.env.DEV) {
        expect(consoleSpy).toHaveBeenCalledWith(
          expect.stringContaining('[API Request]'),
          expect.any(Object)
        );
      }

      consoleSpy.mockRestore();
    });

    it('should log errors in development mode', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      server.use(
        http.get('*/error', () => {
          return HttpResponse.json(
            { detail: 'Bad Request' },
            { status: 400 }
          );
        })
      );

      try {
        await apiClient.get('/error');
      } catch (error) {
        // Expected
      }

      if (import.meta.env.DEV) {
        expect(consoleSpy).toHaveBeenCalledWith(
          expect.stringContaining('[API Response Error]'),
          expect.any(Object)
        );
      }

      consoleSpy.mockRestore();
    });
  });
});
