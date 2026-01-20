/**
 * Property-based tests for ResourceDataTable component
 * 
 * Feature: phase1-ingestion-management
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import * as fc from 'fast-check';
import { ResourceDataTable } from './ResourceDataTable';
import { ResourceStatus, ReadStatus } from '@/core/types/resource';
import type { Resource } from '@/core/types/resource';

// Mock Link component from TanStack Router
vi.mock('@tanstack/react-router', () => ({
  Link: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <a className={className}>{children}</a>
  ),
}));

describe('ResourceDataTable - Property Tests', () => {
  it('Property 5: Quality Score Color Coding', () => {
    // Feature: phase1-ingestion-management, Property 5: Quality Score Color Coding
    // Validates: Requirements 3.4
    
    fc.assert(
      fc.property(
        fc.float({ min: 0.0, max: 1.0 }),
        (qualityScore) => {
          const mockResource: Resource = {
            id: '1',
            title: 'Test Resource',
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
            quality_score: qualityScore,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            ingestion_status: ResourceStatus.COMPLETED,
            ingestion_error: null,
            ingestion_started_at: null,
            ingestion_completed_at: null,
          };

          const { unmount } = render(
            <ResourceDataTable
              data={[mockResource]}
              isLoading={false}
              page={1}
              totalPages={1}
              totalResources={1}
              onPageChange={vi.fn()}
            />
          );

          const scoreElement = screen.getByText(qualityScore.toFixed(2));
          expect(scoreElement).toBeInTheDocument();

          // Verify correct color class based on thresholds
          if (qualityScore < 0.5) {
            expect(scoreElement).toHaveClass('text-red-600');
          } else if (qualityScore < 0.7) {
            expect(scoreElement).toHaveClass('text-yellow-600');
          } else {
            expect(scoreElement).toHaveClass('text-green-600');
          }

          // Clean up after each iteration
          unmount();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('Property 5: Quality Score Boundary Testing', () => {
    // Feature: phase1-ingestion-management, Property 5: Quality Score Color Coding
    // Validates: Requirements 3.4
    
    // Test boundary values
    const boundaries = [
      { score: 0.0, expectedClass: 'text-red-600' },
      { score: 0.49, expectedClass: 'text-red-600' },
      { score: 0.5, expectedClass: 'text-yellow-600' },
      { score: 0.69, expectedClass: 'text-yellow-600' },
      { score: 0.7, expectedClass: 'text-green-600' },
      { score: 1.0, expectedClass: 'text-green-600' },
    ];

    boundaries.forEach(({ score, expectedClass }) => {
      const mockResource: Resource = {
        id: `test-${score}`,
        title: `Test Resource ${score}`,
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
        quality_score: score,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        ingestion_status: ResourceStatus.COMPLETED,
        ingestion_error: null,
        ingestion_started_at: null,
        ingestion_completed_at: null,
      };

      const { unmount } = render(
        <ResourceDataTable
          data={[mockResource]}
          isLoading={false}
          page={1}
          totalPages={1}
          totalResources={1}
          onPageChange={vi.fn()}
        />
      );

      const scoreElement = screen.getByText(score.toFixed(2));
      expect(scoreElement).toHaveClass(expectedClass);

      unmount();
    });
  });
});
