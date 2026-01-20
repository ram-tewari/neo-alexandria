/**
 * Unit tests for ResourceDataTable component
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResourceDataTable } from './ResourceDataTable';
import { ResourceStatus, ReadStatus } from '@/core/types/resource';
import type { Resource } from '@/core/types/resource';

// Mock Link component from TanStack Router
vi.mock('@tanstack/react-router', () => ({
  Link: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <a className={className}>{children}</a>
  ),
}));

// Mock data
const mockResources: Resource[] = [
  {
    id: '1',
    title: 'Test Resource 1',
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
    classification_code: 'A.1',
    read_status: ReadStatus.UNREAD,
    quality_score: 0.85,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ingestion_status: ResourceStatus.COMPLETED,
    ingestion_error: null,
    ingestion_started_at: null,
    ingestion_completed_at: null,
  },
  {
    id: '2',
    title: 'Test Resource 2',
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
    quality_score: 0.45,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
    ingestion_status: ResourceStatus.PROCESSING,
    ingestion_error: null,
    ingestion_started_at: null,
    ingestion_completed_at: null,
  },
];

describe('ResourceDataTable', () => {
  describe('Rendering', () => {
    it('should render all columns correctly', () => {
      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={1}
          totalPages={1}
          totalResources={2}
          onPageChange={vi.fn()}
        />
      );

      // Check column headers
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Title')).toBeInTheDocument();
      expect(screen.getByText('Classification')).toBeInTheDocument();
      expect(screen.getByText('Quality')).toBeInTheDocument();
      expect(screen.getByText('Date')).toBeInTheDocument();
    });

    it('should render resource data', () => {
      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={1}
          totalPages={1}
          totalResources={2}
          onPageChange={vi.fn()}
        />
      );

      expect(screen.getByText('Test Resource 1')).toBeInTheDocument();
      expect(screen.getByText('Test Resource 2')).toBeInTheDocument();
    });

    it('should render status badges', () => {
      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={1}
          totalPages={1}
          totalResources={2}
          onPageChange={vi.fn()}
        />
      );

      expect(screen.getByText('Completed')).toBeInTheDocument();
      expect(screen.getByText('Processing')).toBeInTheDocument();
    });

    it('should render classification badges', () => {
      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={1}
          totalPages={1}
          totalResources={2}
          onPageChange={vi.fn()}
        />
      );

      expect(screen.getByText('A.1')).toBeInTheDocument();
      expect(screen.getByText('—')).toBeInTheDocument(); // No classification
    });

    it('should render quality scores with correct colors', () => {
      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={1}
          totalPages={1}
          totalResources={2}
          onPageChange={vi.fn()}
        />
      );

      const highQuality = screen.getByText('0.85');
      expect(highQuality).toHaveClass('text-green-600');

      const lowQuality = screen.getByText('0.45');
      expect(lowQuality).toHaveClass('text-red-600');
    });
  });

  describe('Pagination', () => {
    it('should disable Previous button on first page', () => {
      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={1}
          totalPages={3}
          totalResources={75}
          onPageChange={vi.fn()}
        />
      );

      const prevButton = screen.getByText('Previous');
      expect(prevButton).toBeDisabled();
    });

    it('should disable Next button on last page', () => {
      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={3}
          totalPages={3}
          totalResources={75}
          onPageChange={vi.fn()}
        />
      );

      const nextButton = screen.getByText('Next');
      expect(nextButton).toBeDisabled();
    });

    it('should display correct pagination info', () => {
      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={2}
          totalPages={5}
          totalResources={125}
          onPageChange={vi.fn()}
        />
      );

      expect(screen.getByText('Page 2 of 5 (125 total resources)')).toBeInTheDocument();
    });

    it('should call onPageChange when clicking Previous', () => {
      const onPageChange = vi.fn();

      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={2}
          totalPages={3}
          totalResources={75}
          onPageChange={onPageChange}
        />
      );

      const prevButton = screen.getByText('Previous');
      prevButton.click();

      expect(onPageChange).toHaveBeenCalledWith(1);
    });

    it('should call onPageChange when clicking Next', () => {
      const onPageChange = vi.fn();

      render(
        <ResourceDataTable
          data={mockResources}
          isLoading={false}
          page={1}
          totalPages={3}
          totalResources={75}
          onPageChange={onPageChange}
        />
      );

      const nextButton = screen.getByText('Next');
      nextButton.click();

      expect(onPageChange).toHaveBeenCalledWith(2);
    });
  });

  describe('Loading state', () => {
    it('should show skeleton loader during loading', () => {
      const { container } = render(
        <ResourceDataTable
          data={[]}
          isLoading={true}
          page={1}
          totalPages={1}
          totalResources={0}
          onPageChange={vi.fn()}
        />
      );

      // Check for skeleton elements with animate-pulse
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Empty state', () => {
    it('should show empty state when no resources', () => {
      render(
        <ResourceDataTable
          data={[]}
          isLoading={false}
          page={1}
          totalPages={0}
          totalResources={0}
          onPageChange={vi.fn()}
        />
      );

      expect(screen.getByText('No resources found')).toBeInTheDocument();
      expect(screen.getByText('Start by ingesting your first resource')).toBeInTheDocument();
    });
  });
});
