import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useMinimumLoadingDuration } from './useMinimumLoadingDuration';

describe('useMinimumLoadingDuration', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('returns true immediately when loading starts', () => {
    const { result } = renderHook(() => useMinimumLoadingDuration(true, 200));
    
    expect(result.current).toBe(true);
  });

  it('maintains loading state for minimum duration', async () => {
    const { result, rerender } = renderHook(
      ({ isLoading }) => useMinimumLoadingDuration(isLoading, 200),
      { initialProps: { isLoading: true } }
    );
    
    expect(result.current).toBe(true);
    
    // Loading finishes after 50ms
    await vi.advanceTimersByTimeAsync(50);
    rerender({ isLoading: false });
    
    // Should still be loading (150ms remaining)
    await vi.advanceTimersByTimeAsync(0); // Flush microtasks
    expect(result.current).toBe(true);
    
    // Advance to complete minimum duration
    await vi.advanceTimersByTimeAsync(150);
    
    await waitFor(() => {
      expect(result.current).toBe(false);
    });
  });

  it('stops loading immediately if minimum duration already passed', async () => {
    const { result, rerender } = renderHook(
      ({ isLoading }) => useMinimumLoadingDuration(isLoading, 200),
      { initialProps: { isLoading: true } }
    );
    
    expect(result.current).toBe(true);
    
    // Loading finishes after 300ms (past minimum)
    vi.advanceTimersByTime(300);
    rerender({ isLoading: false });
    
    expect(result.current).toBe(false);
  });

  it('handles multiple loading cycles', async () => {
    const { result, rerender } = renderHook(
      ({ isLoading }) => useMinimumLoadingDuration(isLoading, 200),
      { initialProps: { isLoading: false } }
    );
    
    expect(result.current).toBe(false);
    
    // First loading cycle
    rerender({ isLoading: true });
    expect(result.current).toBe(true);
    
    await vi.advanceTimersByTimeAsync(50);
    rerender({ isLoading: false });
    
    await vi.advanceTimersByTimeAsync(150);
    await waitFor(() => {
      expect(result.current).toBe(false);
    });
    
    // Second loading cycle
    rerender({ isLoading: true });
    expect(result.current).toBe(true);
    
    await vi.advanceTimersByTimeAsync(100);
    rerender({ isLoading: false });
    
    await vi.advanceTimersByTimeAsync(100);
    await waitFor(() => {
      expect(result.current).toBe(false);
    });
  });

  it('uses custom minimum duration', async () => {
    const { result, rerender } = renderHook(
      ({ isLoading }) => useMinimumLoadingDuration(isLoading, 500),
      { initialProps: { isLoading: true } }
    );
    
    expect(result.current).toBe(true);
    
    // Loading finishes after 100ms
    await vi.advanceTimersByTimeAsync(100);
    rerender({ isLoading: false });
    
    // Should still be loading (400ms remaining)
    await vi.advanceTimersByTimeAsync(0); // Flush microtasks
    expect(result.current).toBe(true);
    
    // Advance to complete minimum duration
    await vi.advanceTimersByTimeAsync(400);
    
    await waitFor(() => {
      expect(result.current).toBe(false);
    });
  });

  it('cleans up timer on unmount', () => {
    const { unmount, rerender } = renderHook(
      ({ isLoading }) => useMinimumLoadingDuration(isLoading, 200),
      { initialProps: { isLoading: true } }
    );
    
    vi.advanceTimersByTime(50);
    rerender({ isLoading: false });
    
    // Unmount before timer completes
    unmount();
    
    // Should not throw or cause issues
    vi.advanceTimersByTime(200);
  });
});
