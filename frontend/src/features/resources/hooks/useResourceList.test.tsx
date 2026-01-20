/**
 * Unit tests for useResourceList hook
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useResourceList } from './useResourceList';
import { fetchResources } from '../api';
import { ResourceStatus, ReadStatus } from '@/core/types/resource';
import type { ResourceListResponse } from '@/core/types/resource';
import React from 'react';

// Mock the API
vi.mock('../api', () => ({
  fetchResources: vi.fn(),
}));

describe('useResourceList', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('should include page, limit, and sort in query key', async () => {
    const mockResponse: ResourceListResponse = {
      items: [],
      total: 0,
    };

    vi.mocked(fetchResources).mockResolvedValue(mockResponse);

    const { result } = renderHook(
      () => useResourceList({ page: 2, limit: 50, sort: 'title:asc' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Verify query key includes all parameters
    const queryKey = result.current.dataUpdatedAt > 0 
      ? queryClient.getQueryCache().findAll()[0]?.queryKey 
      : null;

    expect(queryKey).toBeTruthy();
    expect(queryKey).toEqual([
      'resources',
      'list',
      { page: 2, limit: 50, sort: 'title:asc' },
    ]);
  });

  it('should use default values when no options provided', async () => {
    const mockResponse: ResourceListResponse = {
      items: [],
      total: 0,
    };

    vi.mocked(fetchResources).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useResourceList(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Verify fetchResources called with defaults
    expect(fetchResources).toHaveBeenCalledWith({
      page: 1,
      limit: 25,
      sort: 'created_at:desc',
    });
  });

  it('should include filter parameters in query key', async () => {
    const mockResponse: ResourceListResponse = {
      items: [],
      total: 0,
    };

    vi.mocked(fetchResources).mockResolvedValue(mockResponse);

    const { result } = renderHook(
      () =>
        useResourceList({
          page: 1,
          limit: 25,
          sort: 'created_at:desc',
          q: 'test',
          classification_code: 'A.1',
          min_quality: 0.7,
        }),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    const queryKey = queryClient.getQueryCache().findAll()[0]?.queryKey;

    expect(queryKey).toEqual([
      'resources',
      'list',
      {
        page: 1,
        limit: 25,
        sort: 'created_at:desc',
        q: 'test',
        classification_code: 'A.1',
        min_quality: 0.7,
      },
    ]);
  });

  it('should keep previous data during refetch (placeholderData)', async () => {
    const mockResponse1: ResourceListResponse = {
      items: [
        {
          id: '1',
          title: 'Resource 1',
          description: null,
          creator: null,
          publisher: null,
          contributor: null,
          date_created: null,
          date_modified: null,
          type: null,
          format: null,
          identifier: null,
          source: null,
          url: null,
          language: null,
          coverage: null,
          rights: null,
          subject: [],
          relation: [],
          classification_code: null,
          read_status: ReadStatus.UNREAD,
          quality_score: 0.8,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          ingestion_status: ResourceStatus.COMPLETED,
          ingestion_error: null,
          ingestion_started_at: null,
          ingestion_completed_at: null,
        },
      ],
      total: 1,
    };

    vi.mocked(fetchResources).mockResolvedValue(mockResponse1);

    const { result, rerender } = renderHook(
      ({ page }: { page: number }) => useResourceList({ page }),
      { wrapper, initialProps: { page: 1 } }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.items).toHaveLength(1);

    // Change page - should keep previous data during refetch
    const mockResponse2: ResourceListResponse = {
      items: [],
      total: 0,
    };
    vi.mocked(fetchResources).mockResolvedValue(mockResponse2);

    rerender({ page: 2 });

    // During refetch, previous data should still be available
    expect(result.current.data?.items).toHaveLength(1);

    await waitFor(() => {
      expect(result.current.data?.items).toHaveLength(0);
    });
  });

  it('should have staleTime set to 30 seconds', async () => {
    const mockResponse: ResourceListResponse = {
      items: [],
      total: 0,
    };

    vi.mocked(fetchResources).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useResourceList(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Data should not be stale immediately after fetch
    expect(result.current.isStale).toBe(false);

    // Verify staleTime is configured (check query cache)
    const query = queryClient.getQueryCache().findAll()[0];
    expect(query?.options.staleTime).toBe(30000);
  });

  it('should call fetchResources with correct parameters', async () => {
    const mockResponse: ResourceListResponse = {
      items: [],
      total: 0,
    };

    vi.mocked(fetchResources).mockResolvedValue(mockResponse);

    renderHook(
      () =>
        useResourceList({
          page: 3,
          limit: 10,
          sort: 'quality_score:desc',
          q: 'search term',
        }),
      { wrapper }
    );

    await waitFor(() => {
      expect(fetchResources).toHaveBeenCalledWith({
        page: 3,
        limit: 10,
        sort: 'quality_score:desc',
        q: 'search term',
      });
    });
  });
});
