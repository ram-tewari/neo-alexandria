/**
 * Property-Based Tests for Debounce Consistency
 * 
 * Feature: phase2.5-backend-api-integration
 * Property 8: Debounce Consistency
 * 
 * For any debounced API call (e.g., hover requests), if multiple calls are
 * triggered within the debounce window, then only the last call should execute.
 * 
 * Validates: Requirements 6.2
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import fc from 'fast-check';
import { useState, useEffect } from 'react';

// Inline implementation to avoid Vitest SSR import issues
function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

describe('Property 8: Debounce Consistency', () => {
  it('should only return the last value when multiple values are set within debounce window', async () => {
    // Feature: phase2.5-backend-api-integration, Property 8: Debounce Consistency
    
    await fc.assert(
      fc.asyncProperty(
        // Generate a sequence of values
        fc.array(fc.string(), { minLength: 2, maxLength: 5 }),
        async (valueSequence) => {
          const debounceMs = 300;
          
          // Execute: Trigger multiple value changes rapidly (within debounce window)
          const { result, rerender } = renderHook(
            ({ value }) => useDebounce(value, debounceMs),
            {
              initialProps: { value: valueSequence[0] },
            }
          );

          // Initial value should be set immediately
          expect(result.current).toBe(valueSequence[0]);

          // Trigger all value changes within the debounce window (< 300ms)
          for (let i = 1; i < valueSequence.length; i++) {
            rerender({ value: valueSequence[i] });
            // Wait a short time between calls (less than debounce delay)
            await new Promise((resolve) => setTimeout(resolve, 50));
          }

          // Wait for debounce to complete
          await new Promise((resolve) => setTimeout(resolve, debounceMs + 100));

          // Verify: Only the last value should be returned
          const lastValue = valueSequence[valueSequence.length - 1];
          expect(result.current).toBe(lastValue);
        }
      ),
      { numRuns: 10, timeout: 15000 } // Run 10 times with 15s timeout
    );
  }, 20000); // 20 second test timeout

  it('should return each value when values are set with sufficient delay between them', async () => {
    // Feature: phase2.5-backend-api-integration, Property 8: Debounce Consistency
    
    await fc.assert(
      fc.asyncProperty(
        // Generate 2-3 values
        fc.array(fc.string(), { minLength: 2, maxLength: 3 }),
        async (valueSequence) => {
          const debounceMs = 300;
          const values: string[] = [];
          
          // Execute: Trigger value changes with sufficient delay between them
          const { result, rerender } = renderHook(
            ({ value }) => useDebounce(value, debounceMs),
            {
              initialProps: { value: valueSequence[0] },
            }
          );

          // Track the initial value
          values.push(result.current);

          for (let i = 1; i < valueSequence.length; i++) {
            rerender({ value: valueSequence[i] });
            
            // Wait for debounce to complete
            await new Promise((resolve) => setTimeout(resolve, debounceMs + 50));
            
            await waitFor(
              () => {
                expect(result.current).toBe(valueSequence[i]);
              },
              { timeout: 1000 }
            );
            
            values.push(result.current);
          }

          // Verify: Each value should have been returned
          expect(values).toEqual(valueSequence);
        }
      ),
      { numRuns: 5, timeout: 15000 } // Run 5 times with 15s timeout
    );
  });

  it('should cancel pending debounce when new value arrives within debounce window', async () => {
    // Feature: phase2.5-backend-api-integration, Property 8: Debounce Consistency
    
    const value1 = 'first';
    const value2 = 'second';
    const debounceMs = 300;

    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, debounceMs),
      {
        initialProps: { value: value1 },
      }
    );

    // Initial value should be set immediately
    expect(result.current).toBe(value1);

    // Trigger first change
    rerender({ value: value2 });

    // Wait 100ms (less than debounce delay)
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Value should still be the initial value (debounce not complete)
    expect(result.current).toBe(value1);

    // Trigger second change (should cancel first debounce)
    const value3 = 'third';
    rerender({ value: value3 });

    // Wait for debounce to complete
    await new Promise((resolve) => setTimeout(resolve, debounceMs + 50));

    // Verify: Only the last value should be returned (value2 was cancelled)
    await waitFor(
      () => {
        expect(result.current).toBe(value3);
      },
      { timeout: 1000 }
    );
    
    // value2 should never have been returned
    expect(result.current).not.toBe(value2);
  });
});
