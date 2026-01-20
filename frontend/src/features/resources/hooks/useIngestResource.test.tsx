/**
 * Unit tests for useIngestResource hook
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useIngestResource } from './useIngestResource';
import { ingestResource } from '../api';
import type { ResourceAccepted, IngestResourcePayload } from '@/core/types/resource';
import React from 'react';

// Mock the API
vi.mock('../api', () => ({
  ingestResource: vi.fn(),
}));

describe('useIngestResource', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: {
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

  it('should call ingestResource API with correct payload', async () => {
    const mockResponse: ResourceAccepted = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      message: 'Resource ingestion started',
    };

    vi.mocked(ingestResource).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useIngestResource(), { wrapper });

    const payload: IngestResourcePayload = {
      title: 'Test Resource',
      url: 'https://example.com',
    };

    result.current.mutate(payload);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(ingestResource).toHaveBeenCalledWith(payload);
    expect(result.current.data).toEqual(mockResponse);
  });

  it('should invalidate resource list query on success', async () => {
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const mockResponse: ResourceAccepted = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      message: 'Resource ingestion started',
    };

    vi.mocked(ingestResource).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useIngestResource(), { wrapper });

    const payload: IngestResourcePayload = {
      title: 'Test Resource',
      url: 'https://example.com',
    };

    result.current.mutate(payload);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['resources', 'list'] });
  });

  it('should handle mutation with minimal payload', async () => {
    const mockResponse: ResourceAccepted = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      message: 'Resource ingestion started',
    };

    vi.mocked(ingestResource).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useIngestResource(), { wrapper });

    const payload: IngestResourcePayload = {
      title: 'Minimal Resource',
    };

    result.current.mutate(payload);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(ingestResource).toHaveBeenCalledWith(payload);
  });

  it('should handle mutation with full payload', async () => {
    const mockResponse: ResourceAccepted = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      message: 'Resource ingestion started',
    };

    vi.mocked(ingestResource).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useIngestResource(), { wrapper });

    const payload: IngestResourcePayload = {
      title: 'Full Resource',
      url: 'https://example.com',
      source: 'https://example.com',
      description: 'Test description',
      type: 'article',
      format: 'html',
      language: 'en',
      subject: ['test', 'example'],
    };

    result.current.mutate(payload);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(ingestResource).toHaveBeenCalledWith(payload);
  });

  it('should handle errors correctly', async () => {
    const mockError = new Error('Network error');

    vi.mocked(ingestResource).mockRejectedValue(mockError);

    const { result } = renderHook(() => useIngestResource(), { wrapper });

    const payload: IngestResourcePayload = {
      title: 'Test Resource',
    };

    result.current.mutate(payload);

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(mockError);
  });

  it('should track pending state during mutation', async () => {
    const mockResponse: ResourceAccepted = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      message: 'Resource ingestion started',
    };

    // Delay the response to test pending state
    vi.mocked(ingestResource).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(mockResponse), 100);
        })
    );

    const { result } = renderHook(() => useIngestResource(), { wrapper });

    const payload: IngestResourcePayload = {
      title: 'Test Resource',
    };

    result.current.mutate(payload);

    // Wait for pending state to be true
    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.isPending).toBe(false);
  });

  it('should support onSuccess callback', async () => {
    const onSuccess = vi.fn();
    const mockResponse: ResourceAccepted = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      message: 'Resource ingestion started',
    };

    vi.mocked(ingestResource).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useIngestResource(), { wrapper });

    const payload: IngestResourcePayload = {
      title: 'Test Resource',
    };

    result.current.mutate(payload, { onSuccess });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Verify callback was invoked
    expect(onSuccess).toHaveBeenCalledTimes(1);
    
    // Verify first argument is the response
    const callArgs = onSuccess.mock.calls[0];
    expect(callArgs[0]).toEqual(mockResponse);
    expect(callArgs[1]).toEqual(payload);
  });

  it('should support onError callback', async () => {
    const onError = vi.fn();
    const mockError = new Error('API error');

    vi.mocked(ingestResource).mockRejectedValue(mockError);

    const { result } = renderHook(() => useIngestResource(), { wrapper });

    const payload: IngestResourcePayload = {
      title: 'Test Resource',
    };

    result.current.mutate(payload, { onError });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    // Verify callback was invoked
    expect(onError).toHaveBeenCalledTimes(1);
    
    // Verify first argument is the error
    const callArgs = onError.mock.calls[0];
    expect(callArgs[0]).toEqual(mockError);
    expect(callArgs[1]).toEqual(payload);
  });
});
