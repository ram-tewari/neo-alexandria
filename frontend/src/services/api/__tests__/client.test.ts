/**
 * API Client Tests
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { APIClient } from '../client';
import { APIError } from '../errors';

describe('APIClient', () => {
  let client: APIClient;
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    client = new APIClient('http://localhost:8000');
    fetchMock = vi.fn();
    global.fetch = fetchMock;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('GET requests', () => {
    it('should make successful GET request', async () => {
      const mockData = { id: '123', title: 'Test Resource' };
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockData }),
      });

      const result = await client.get('/api/resources/123');

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/resources/123',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(mockData);
    });

    it('should handle query parameters', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] }),
      });

      await client.get('/api/resources', { page: 1, limit: 20 });

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/resources?page=1&limit=20',
        expect.any(Object)
      );
    });

    it('should handle array query parameters', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] }),
      });

      await client.get('/api/resources', { tags: ['ai', 'ml'] });

      const url = fetchMock.mock.calls[0][0];
      expect(url).toContain('tags=ai');
      expect(url).toContain('tags=ml');
    });

    it('should cache GET requests', async () => {
      const mockData = { id: '123', title: 'Test' };
      fetchMock.mockResolvedValue({
        ok: true,
        json: async () => ({ data: mockData }),
      });

      // First request
      await client.get('/api/resources/123');
      expect(fetchMock).toHaveBeenCalledTimes(1);

      // Second request should use cache
      await client.get('/api/resources/123');
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    it('should bypass cache when requested', async () => {
      const mockData = { id: '123', title: 'Test' };
      fetchMock.mockResolvedValue({
        ok: true,
        json: async () => ({ data: mockData }),
      });

      await client.get('/api/resources/123', {}, true);
      await client.get('/api/resources/123', {}, false);

      expect(fetchMock).toHaveBeenCalledTimes(2);
    });
  });

  describe('POST requests', () => {
    it('should make successful POST request', async () => {
      const mockData = { id: '123', title: 'New Resource' };
      const postData = { title: 'New Resource' };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockData }),
      });

      const result = await client.post('/api/resources', postData);

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/resources',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
        })
      );
      expect(result).toEqual(mockData);
    });

    it('should invalidate cache after POST', async () => {
      fetchMock.mockResolvedValue({
        ok: true,
        json: async () => ({ data: {} }),
      });

      // Cache a GET request
      await client.get('/api/resources/123');
      expect(fetchMock).toHaveBeenCalledTimes(1);

      // POST should invalidate cache
      await client.post('/api/resources', { title: 'New' });

      // Next GET should fetch again
      await client.get('/api/resources/123');
      expect(fetchMock).toHaveBeenCalledTimes(3);
    });
  });

  describe('PUT requests', () => {
    it('should make successful PUT request', async () => {
      const mockData = { id: '123', title: 'Updated' };
      const putData = { title: 'Updated' };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockData }),
      });

      const result = await client.put('/api/resources/123', putData);

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/resources/123',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(putData),
        })
      );
      expect(result).toEqual(mockData);
    });
  });

  describe('PATCH requests', () => {
    it('should make successful PATCH request', async () => {
      const mockData = { id: '123', read_status: 'completed' };
      const patchData = { read_status: 'completed' };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockData }),
      });

      const result = await client.patch('/api/resources/123', patchData);

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/resources/123',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(patchData),
        })
      );
      expect(result).toEqual(mockData);
    });
  });

  describe('DELETE requests', () => {
    it('should make successful DELETE request', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await client.delete('/api/resources/123');

      expect(fetchMock).toHaveBeenCalledWith(
        'http://localhost:8000/api/resources/123',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });

  describe('Error handling', () => {
    it('should handle 404 errors', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({
          error: {
            code: 'RESOURCE_NOT_FOUND',
            message: 'Resource not found',
          },
        }),
      });

      await expect(client.get('/api/resources/999')).rejects.toThrow(APIError);
      
      try {
        await client.get('/api/resources/999');
      } catch (error) {
        expect(error).toBeInstanceOf(APIError);
        expect((error as APIError).statusCode).toBe(404);
        expect((error as APIError).code).toBe('RESOURCE_NOT_FOUND');
      }
    });

    it('should handle 500 errors', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({
          error: {
            code: 'SERVER_ERROR',
            message: 'Internal server error',
          },
        }),
      });

      await expect(client.get('/api/resources')).rejects.toThrow(APIError);
    });

    it('should handle network errors', async () => {
      fetchMock.mockRejectedValueOnce(new Error('Network error'));

      await expect(client.get('/api/resources')).rejects.toThrow(APIError);
      
      try {
        await client.get('/api/resources');
      } catch (error) {
        expect(error).toBeInstanceOf(APIError);
        expect((error as APIError).isNetworkError()).toBe(true);
      }
    });
  });

  describe('Retry logic', () => {
    it('should retry on network errors', async () => {
      // Fail twice, then succeed
      fetchMock
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { id: '123' } }),
        });

      const result = await client.get('/api/resources/123', {}, false);

      expect(fetchMock).toHaveBeenCalledTimes(3);
      expect(result).toEqual({ id: '123' });
    });

    it('should retry on 500 errors', async () => {
      // Fail once with 500, then succeed
      fetchMock
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          json: async () => ({ error: { code: 'SERVER_ERROR', message: 'Error' } }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: { id: '123' } }),
        });

      const result = await client.get('/api/resources/123', {}, false);

      expect(fetchMock).toHaveBeenCalledTimes(2);
      expect(result).toEqual({ id: '123' });
    });

    it('should not retry on 404 errors', async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ error: { code: 'NOT_FOUND', message: 'Not found' } }),
      });

      await expect(client.get('/api/resources/999', {}, false)).rejects.toThrow();

      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    it('should give up after max retries', async () => {
      fetchMock.mockRejectedValue(new Error('Network error'));

      await expect(client.get('/api/resources', {}, false)).rejects.toThrow();

      // Should try 4 times total (1 initial + 3 retries)
      expect(fetchMock).toHaveBeenCalledTimes(4);
    });
  });

  describe('Authentication', () => {
    it('should set auth token', () => {
      client.setAuthToken('test-token');

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: {} }),
      });

      client.get('/api/resources');

      expect(fetchMock).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );
    });

    it('should clear auth token', () => {
      client.setAuthToken('test-token');
      client.clearAuthToken();

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: {} }),
      });

      client.get('/api/resources');

      expect(fetchMock).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.not.objectContaining({
            Authorization: expect.any(String),
          }),
        })
      );
    });
  });

  describe('Cache management', () => {
    it('should invalidate all cache', async () => {
      fetchMock.mockResolvedValue({
        ok: true,
        json: async () => ({ data: {} }),
      });

      await client.get('/api/resources/1');
      await client.get('/api/resources/2');
      expect(fetchMock).toHaveBeenCalledTimes(2);

      client.invalidateCache();

      await client.get('/api/resources/1');
      await client.get('/api/resources/2');
      expect(fetchMock).toHaveBeenCalledTimes(4);
    });

    it('should invalidate cache by pattern', async () => {
      fetchMock.mockResolvedValue({
        ok: true,
        json: async () => ({ data: {} }),
      });

      await client.get('/api/resources/1');
      await client.get('/api/collections/1');
      expect(fetchMock).toHaveBeenCalledTimes(2);

      client.invalidateCache('/api/resources');

      await client.get('/api/resources/1');
      await client.get('/api/collections/1');
      expect(fetchMock).toHaveBeenCalledTimes(3); // Only resources refetched
    });
  });
});
