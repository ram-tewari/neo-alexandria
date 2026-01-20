/**
 * Unit tests for useResourcePoller hook
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useResourcePoller } from './useResourcePoller';
import { getResourceStatus } from '../api';
import { ResourceStatus } from '@/core/types/resource';
import type { ResourceStatusResponse } from '@/core/types/resource';
import React from 'react';

// Mock the API
vi.mock('../api', () => ({
  getResourceStatus: vi.fn(),
}));

describe('useResourcePoller', () => {
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

  it('should not poll when resourceId is null', () => {
    const { result } = renderHook(
      () => useResourcePoller({ resourceId: null }),
      { wrapper }
    );

    expect(result.current.isFetching).toBe(false);
    expect(getResourceStatus).not.toHaveBeenCalled();
  });

  it('should start polling for pending status', async () => {
    const mockStatus: ResourceStatusResponse = {
      id: '123',
      ingestion_status: ResourceStatus.PENDING,
      ingestion_error: null,
      ingestion_started_at: null,
      ingestion_completed_at: null,
    };

    vi.mocked(getResourceStatus).mockResolvedValue(mockStatus);

    const { result } = renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.ingestion_status).toBe(ResourceStatus.PENDING);
    expect(getResourceStatus).toHaveBeenCalledWith('123');
  });

  it('should start polling for processing status', async () => {
    const mockStatus: ResourceStatusResponse = {
      id: '123',
      ingestion_status: ResourceStatus.PROCESSING,
      ingestion_error: null,
      ingestion_started_at: '2024-01-01T00:00:00Z',
      ingestion_completed_at: null,
    };

    vi.mocked(getResourceStatus).mockResolvedValue(mockStatus);

    const { result } = renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.ingestion_status).toBe(ResourceStatus.PROCESSING);
  });

  it('should stop polling for completed status', async () => {
    const mockStatus: ResourceStatusResponse = {
      id: '123',
      ingestion_status: ResourceStatus.COMPLETED,
      ingestion_error: null,
      ingestion_started_at: '2024-01-01T00:00:00Z',
      ingestion_completed_at: '2024-01-01T00:00:05Z',
    };

    vi.mocked(getResourceStatus).mockResolvedValue(mockStatus);

    const { result } = renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.ingestion_status).toBe(ResourceStatus.COMPLETED);
  });

  it('should stop polling for failed status', async () => {
    const mockStatus: ResourceStatusResponse = {
      id: '123',
      ingestion_status: ResourceStatus.FAILED,
      ingestion_error: 'Network error',
      ingestion_started_at: '2024-01-01T00:00:00Z',
      ingestion_completed_at: '2024-01-01T00:00:05Z',
    };

    vi.mocked(getResourceStatus).mockResolvedValue(mockStatus);

    const { result } = renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.ingestion_status).toBe(ResourceStatus.FAILED);
    expect(result.current.data?.ingestion_error).toBe('Network error');
  });

  it('should invoke onComplete callback on completion', async () => {
    const onComplete = vi.fn();
    const mockStatus: ResourceStatusResponse = {
      id: '123',
      ingestion_status: ResourceStatus.COMPLETED,
      ingestion_error: null,
      ingestion_started_at: '2024-01-01T00:00:00Z',
      ingestion_completed_at: '2024-01-01T00:00:05Z',
    };

    vi.mocked(getResourceStatus).mockResolvedValue(mockStatus);

    renderHook(
      () => useResourcePoller({ resourceId: '123', onComplete }),
      { wrapper }
    );

    await waitFor(() => {
      expect(onComplete).toHaveBeenCalled();
    });
  });

  it('should invoke onError callback on failure', async () => {
    const onError = vi.fn();
    const mockStatus: ResourceStatusResponse = {
      id: '123',
      ingestion_status: ResourceStatus.FAILED,
      ingestion_error: 'Processing failed',
      ingestion_started_at: '2024-01-01T00:00:00Z',
      ingestion_completed_at: '2024-01-01T00:00:05Z',
    };

    vi.mocked(getResourceStatus).mockResolvedValue(mockStatus);

    renderHook(
      () => useResourcePoller({ resourceId: '123', onError }),
      { wrapper }
    );

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith('Processing failed');
    });
  });

  it('should invalidate resource list query on completion', async () => {
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
    const mockStatus: ResourceStatusResponse = {
      id: '123',
      ingestion_status: ResourceStatus.COMPLETED,
      ingestion_error: null,
      ingestion_started_at: '2024-01-01T00:00:00Z',
      ingestion_completed_at: '2024-01-01T00:00:05Z',
    };

    vi.mocked(getResourceStatus).mockResolvedValue(mockStatus);

    renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['resources', 'list'] });
    });
  });

  it('should have staleTime set to 0', async () => {
    const mockStatus: ResourceStatusResponse = {
      id: '123',
      ingestion_status: ResourceStatus.PENDING,
      ingestion_error: null,
      ingestion_started_at: null,
      ingestion_completed_at: null,
    };

    vi.mocked(getResourceStatus).mockResolvedValue(mockStatus);

    const { result } = renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Data should always be considered stale (staleTime: 0)
    expect(result.current.isStale).toBe(true);
  });
});
