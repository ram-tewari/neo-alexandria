/**
 * useDebounce Hook Tests
 */

import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Import from JS file
import { useDebounce } from '../useDebounce.js';

describe('useDebounce', () => {
  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('test', 300));
    expect(result.current).toBe('test');
  });

  it('should debounce value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 300 } }
    );

    expect(result.current).toBe('initial');

    // Change value
    rerender({ value: 'updated', delay: 300 });
    
    // Should still be initial immediately
    expect(result.current).toBe('initial');

    // Wait for debounce
    await waitFor(() => expect(result.current).toBe('updated'), { timeout: 400 });
  });

  it('should handle rapid changes', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 'v1' } }
    );

    // Rapid changes
    rerender({ value: 'v2' });
    rerender({ value: 'v3' });
    rerender({ value: 'v4' });

    // Should still be initial
    expect(result.current).toBe('v1');

    // Wait for debounce - should only update to final value
    await waitFor(() => expect(result.current).toBe('v4'), { timeout: 400 });
  });

  it('should cleanup timeout on unmount', () => {
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
    const { unmount } = renderHook(() => useDebounce('test', 300));
    
    unmount();
    
    expect(clearTimeoutSpy).toHaveBeenCalled();
    clearTimeoutSpy.mockRestore();
  });

  it('should work with different types', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 42 } }
    );

    expect(result.current).toBe(42);

    rerender({ value: 100 });
    await waitFor(() => expect(result.current).toBe(100), { timeout: 400 });
  });
});
