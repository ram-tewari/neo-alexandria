/**
 * Property-based tests for useResourcePoller hook
 * 
 * Feature: phase1-ingestion-management
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as fc from 'fast-check';
import { useResourcePoller } from './useResourcePoller';
import { getResourceStatus } from '../api';
import { ResourceStatus } from '@/core/types/resource';
import type { ResourceStatusResponse } from '@/core/types/resource';
import React from 'react';

// Mock the API
vi.mock('../api', () => ({
  getResourceStatus: vi.fn(),
}));

describe('useResourcePoller - Property Tests', () => {
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

  it('Property 2: Polling Interval Consistency - pending status', async () => {
    // Feature: phase1-ingestion-management, Property 2: Polling Interval Consistency
    // Validates: Requirements 2.2
    
    const timestamps: number[] = [];
    let callCount = 0;

    vi.mocked(getResourceStatus).mockImplementation(async () => {
      timestamps.push(Date.now());
      callCount++;

      // After 3 calls, switch to completed to stop polling
      if (callCount >= 3) {
        return {
          id: '123',
          ingestion_status: ResourceStatus.COMPLETED,
          ingestion_error: null,
          ingestion_started_at: '2024-01-01T00:00:00Z',
          ingestion_completed_at: '2024-01-01T00:00:05Z',
        };
      }

      return {
        id: '123',
        ingestion_status: ResourceStatus.PENDING,
        ingestion_error: null,
        ingestion_started_at: null,
        ingestion_completed_at: null,
      };
    });

    renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    // Wait for polling to complete
    await waitFor(
      () => {
        expect(callCount).toBeGreaterThanOrEqual(3);
      },
      { timeout: 10000 }
    );

    // Verify intervals are approximately 2000ms (±100ms tolerance)
    for (let i = 1; i < timestamps.length; i++) {
      const interval = timestamps[i] - timestamps[i - 1];
      expect(interval).toBeGreaterThanOrEqual(1900);
      expect(interval).toBeLessThanOrEqual(2100);
    }
  });

  it('Property 2: Polling Interval Consistency - processing status', async () => {
    // Feature: phase1-ingestion-management, Property 2: Polling Interval Consistency
    // Validates: Requirements 2.2
    
    const timestamps: number[] = [];
    let callCount = 0;

    vi.mocked(getResourceStatus).mockImplementation(async () => {
      timestamps.push(Date.now());
      callCount++;

      // After 3 calls, switch to completed to stop polling
      if (callCount >= 3) {
        return {
          id: '123',
          ingestion_status: ResourceStatus.COMPLETED,
          ingestion_error: null,
          ingestion_started_at: '2024-01-01T00:00:00Z',
          ingestion_completed_at: '2024-01-01T00:00:05Z',
        };
      }

      return {
        id: '123',
        ingestion_status: ResourceStatus.PROCESSING,
        ingestion_error: null,
        ingestion_started_at: '2024-01-01T00:00:00Z',
        ingestion_completed_at: null,
      };
    });

    renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    // Wait for polling to complete
    await waitFor(
      () => {
        expect(callCount).toBeGreaterThanOrEqual(3);
      },
      { timeout: 10000 }
    );

    // Verify intervals are approximately 2000ms (±100ms tolerance)
    for (let i = 1; i < timestamps.length; i++) {
      const interval = timestamps[i] - timestamps[i - 1];
      expect(interval).toBeGreaterThanOrEqual(1900);
      expect(interval).toBeLessThanOrEqual(2100);
    }
  });

  it('Property 3: Polling Termination - completed status', async () => {
    // Feature: phase1-ingestion-management, Property 3: Polling Termination
    // Validates: Requirements 2.3
    
    const finalStatuses = [ResourceStatus.COMPLETED, ResourceStatus.FAILED];

    for (const finalStatus of finalStatuses) {
      queryClient.clear();
      vi.clearAllMocks();

      let callCount = 0;

      vi.mocked(getResourceStatus).mockImplementation(async () => {
        callCount++;

        return {
          id: '123',
          ingestion_status: finalStatus,
          ingestion_error: finalStatus === ResourceStatus.FAILED ? 'Error' : null,
          ingestion_started_at: '2024-01-01T00:00:00Z',
          ingestion_completed_at: '2024-01-01T00:00:05Z',
        };
      });

      renderHook(
        () => useResourcePoller({ resourceId: '123' }),
        { wrapper }
      );

      // Wait for initial fetch
      await waitFor(() => {
        expect(callCount).toBeGreaterThanOrEqual(1);
      });

      const initialCallCount = callCount;

      // Wait 2.5 seconds to ensure no additional polling
      await new Promise((resolve) => setTimeout(resolve, 2500));

      // Verify no additional API calls after termination
      expect(callCount).toBe(initialCallCount);
    }
  }, 10000);

  it('Property 3: Polling Termination - status transitions', async () => {
    // Feature: phase1-ingestion-management, Property 3: Polling Termination
    // Validates: Requirements 2.3
    
    let callCount = 0;

    vi.mocked(getResourceStatus).mockImplementation(async () => {
      callCount++;

      // Transition: pending → processing → completed
      if (callCount === 1) {
        return {
          id: '123',
          ingestion_status: ResourceStatus.PENDING,
          ingestion_error: null,
          ingestion_started_at: null,
          ingestion_completed_at: null,
        };
      } else if (callCount === 2) {
        return {
          id: '123',
          ingestion_status: ResourceStatus.PROCESSING,
          ingestion_error: null,
          ingestion_started_at: '2024-01-01T00:00:00Z',
          ingestion_completed_at: null,
        };
      } else {
        return {
          id: '123',
          ingestion_status: ResourceStatus.COMPLETED,
          ingestion_error: null,
          ingestion_started_at: '2024-01-01T00:00:00Z',
          ingestion_completed_at: '2024-01-01T00:00:05Z',
        };
      }
    });

    renderHook(
      () => useResourcePoller({ resourceId: '123' }),
      { wrapper }
    );

    // Wait for completion
    await waitFor(
      () => {
        expect(callCount).toBeGreaterThanOrEqual(3);
      },
      { timeout: 10000 }
    );

    const callsBeforeWait = callCount;

    // Wait 2.5 seconds to ensure polling stopped
    await new Promise((resolve) => setTimeout(resolve, 2500));

    // Verify no additional calls after completion
    expect(callCount).toBe(callsBeforeWait);
  }, 15000);
});
