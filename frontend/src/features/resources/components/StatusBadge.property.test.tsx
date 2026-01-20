/**
 * Property-based tests for StatusBadge component
 * 
 * Feature: phase1-ingestion-management
 */
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import * as fc from 'fast-check';
import { StatusBadge } from './StatusBadge';
import { ResourceStatus } from '@/core/types/resource';

describe('StatusBadge - Property Tests', () => {
  it('Property 4: Status Badge Color Mapping', () => {
    // Feature: phase1-ingestion-management, Property 4: Status Badge Color Mapping
    // Validates: Requirements 3.3, 6.2-6.5
    
    fc.assert(
      fc.property(
        fc.constantFrom(
          ResourceStatus.PENDING,
          ResourceStatus.PROCESSING,
          ResourceStatus.COMPLETED,
          ResourceStatus.FAILED
        ),
        (status) => {
          const { container } = render(<StatusBadge status={status} />);
          const badge = container.querySelector('[aria-label]');

          expect(badge).toBeInTheDocument();

          // Verify correct color class applied based on status
          switch (status) {
            case ResourceStatus.PENDING:
              expect(badge).toHaveClass('bg-yellow-100');
              expect(badge).toHaveClass('text-yellow-800');
              break;
            case ResourceStatus.PROCESSING:
              expect(badge).toHaveClass('bg-blue-100');
              expect(badge).toHaveClass('text-blue-800');
              break;
            case ResourceStatus.COMPLETED:
              expect(badge).toHaveClass('bg-green-100');
              expect(badge).toHaveClass('text-green-800');
              break;
            case ResourceStatus.FAILED:
              expect(badge).toHaveClass('bg-red-100');
              expect(badge).toHaveClass('text-red-800');
              break;
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('Property 4: Status Badge Icon Mapping', () => {
    // Feature: phase1-ingestion-management, Property 4: Status Badge Color Mapping
    // Validates: Requirements 3.3, 6.2-6.5
    
    fc.assert(
      fc.property(
        fc.constantFrom(
          ResourceStatus.PENDING,
          ResourceStatus.PROCESSING,
          ResourceStatus.COMPLETED,
          ResourceStatus.FAILED
        ),
        (status) => {
          const { container } = render(<StatusBadge status={status} />);
          const icon = container.querySelector('svg');

          expect(icon).toBeInTheDocument();

          // Verify icon has correct classes
          expect(icon).toHaveClass('h-3');
          expect(icon).toHaveClass('w-3');
          expect(icon).toHaveClass('mr-1');

          // Verify spinning animation only for processing
          if (status === ResourceStatus.PROCESSING) {
            expect(icon).toHaveClass('animate-spin');
          } else {
            expect(icon).not.toHaveClass('animate-spin');
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('Property 4: Status Badge Accessibility', () => {
    // Feature: phase1-ingestion-management, Property 4: Status Badge Color Mapping
    // Validates: Requirements 3.3, 6.2-6.5
    
    fc.assert(
      fc.property(
        fc.constantFrom(
          ResourceStatus.PENDING,
          ResourceStatus.PROCESSING,
          ResourceStatus.COMPLETED,
          ResourceStatus.FAILED
        ),
        (status) => {
          const { container } = render(<StatusBadge status={status} />);
          const badge = container.querySelector('[aria-label]');

          expect(badge).toBeInTheDocument();
          expect(badge).toHaveAttribute('aria-label', `Status: ${status}`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('Property 4: Status Badge Consistency', () => {
    // Feature: phase1-ingestion-management, Property 4: Status Badge Color Mapping
    // Validates: Requirements 3.3, 6.2-6.5
    
    // Verify that rendering the same status multiple times produces consistent results
    fc.assert(
      fc.property(
        fc.constantFrom(
          ResourceStatus.PENDING,
          ResourceStatus.PROCESSING,
          ResourceStatus.COMPLETED,
          ResourceStatus.FAILED
        ),
        (status) => {
          const { container: container1 } = render(<StatusBadge status={status} />);
          const { container: container2 } = render(<StatusBadge status={status} />);

          const badge1 = container1.querySelector('[aria-label]');
          const badge2 = container2.querySelector('[aria-label]');

          // Both should have the same classes
          expect(badge1?.className).toBe(badge2?.className);
          expect(badge1?.getAttribute('aria-label')).toBe(badge2?.getAttribute('aria-label'));
        }
      ),
      { numRuns: 100 }
    );
  });
});
