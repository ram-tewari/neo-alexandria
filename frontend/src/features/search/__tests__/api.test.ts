/**
 * Search API Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { searchResources } from '../api';

describe('searchResources', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should call search API with correct payload', async () => {
    const mockResponse = {
      results: [
        {
          id: 1,
          title: 'Test Resource',
          description: 'Test description',
          resource_type: 'article',
          score: 0.85,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ],
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const payload = {
      text: 'test query',
      hybrid_weight: 0.7,
      filters: { min_quality: 0.5 },
      limit: 20,
    };

    const results = await searchResources(payload);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/search'),
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
    );

    expect(results).toEqual(mockResponse.results);
  });

  it('should handle 400 error with user-friendly message', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 400,
    });

    await expect(
      searchResources({ text: 'test', limit: 20 })
    ).rejects.toThrow('Invalid search query');
  });

  it('should handle 500 error with user-friendly message', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    await expect(
      searchResources({ text: 'test', limit: 20 })
    ).rejects.toThrow('Search service is currently unavailable');
  });

  it('should handle network errors', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    await expect(
      searchResources({ text: 'test', limit: 20 })
    ).rejects.toThrow();
  });

  it('should handle timeout', async () => {
    (global.fetch as any).mockImplementationOnce(() =>
      new Promise((resolve) => setTimeout(resolve, 15000))
    );

    await expect(
      searchResources({ text: 'test', limit: 20 })
    ).rejects.toThrow();
  });

  it('should handle both response formats', async () => {
    // Test array format
    const arrayResponse = [
      {
        id: 1,
        title: 'Test',
        description: 'Test',
        resource_type: 'article',
        score: 0.85,
        created_at: '2024-01-01',
        updated_at: '2024-01-01',
      },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => arrayResponse,
    });

    const results = await searchResources({ text: 'test', limit: 20 });
    expect(results).toEqual(arrayResponse);
  });
});
