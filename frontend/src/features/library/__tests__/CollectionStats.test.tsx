import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CollectionStats, CollectionStatsSkeleton } from '../CollectionStats';
import type { Collection } from '@/types/library';

const mockCollection: Collection = {
  id: 'col_1',
  name: 'Research Papers',
  description: 'Academic research collection',
  tags: ['research', 'academic', 'papers', 'science', 'technology'],
  is_public: false,
  resource_count: 25,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
};

describe('CollectionStats', () => {
  describe('Rendering', () => {
    it('renders statistics header', () => {
      render(<CollectionStats collection={mockCollection} />);

      expect(screen.getByText('Statistics')).toBeInTheDocument();
    });

    it('displays total documents count', () => {
      render(<CollectionStats collection={mockCollection} />);

      expect(screen.getByText('Total Documents')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
    });

    it('displays document types section', () => {
      render(<CollectionStats collection={mockCollection} />);

      expect(screen.getByText('Document Types')).toBeInTheDocument();
      expect(screen.getByText('PDF')).toBeInTheDocument();
      expect(screen.getByText('Code')).toBeInTheDocument();
      expect(screen.getByText('Markdown')).toBeInTheDocument();
    });

    it('displays average quality score', () => {
      render(<CollectionStats collection={mockCollection} />);

      expect(screen.getByText('Average Quality')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
    });

    it('displays date range', () => {
      render(<CollectionStats collection={mockCollection} />);

      expect(screen.getByText('Date Range')).toBeInTheDocument();
      expect(screen.getByText(/Created:/i)).toBeInTheDocument();
      expect(screen.getByText(/Updated:/i)).toBeInTheDocument();
    });

    it('displays top tags when available', () => {
      render(<CollectionStats collection={mockCollection} />);

      expect(screen.getByText('Top Tags')).toBeInTheDocument();
      expect(screen.getByText(/research/i)).toBeInTheDocument();
      expect(screen.getByText(/academic/i)).toBeInTheDocument();
    });

    it('does not display top tags when collection has no tags', () => {
      const collectionWithoutTags: Collection = {
        ...mockCollection,
        tags: [],
      };

      render(<CollectionStats collection={collectionWithoutTags} />);

      expect(screen.queryByText('Top Tags')).not.toBeInTheDocument();
    });
  });

  describe('Document Type Breakdown', () => {
    it('displays document type counts', () => {
      render(<CollectionStats collection={mockCollection} />);

      // PDF should be ~60% of 25 = 15
      expect(screen.getByText('15')).toBeInTheDocument();
      // Code should be ~30% of 25 = 7
      expect(screen.getByText('7')).toBeInTheDocument();
      // Markdown should be ~10% of 25 = 2
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('displays progress bars for document types', () => {
      const { container } = render(<CollectionStats collection={mockCollection} />);

      const progressBars = container.querySelectorAll('.h-2.bg-muted');
      expect(progressBars.length).toBeGreaterThan(0);
    });

    it('uses correct colors for document types', () => {
      const { container } = render(<CollectionStats collection={mockCollection} />);

      // Check for color classes
      expect(container.querySelector('.bg-red-500')).toBeInTheDocument(); // PDF
      expect(container.querySelector('.bg-blue-500')).toBeInTheDocument(); // Code
      expect(container.querySelector('.bg-green-500')).toBeInTheDocument(); // Markdown
    });
  });

  describe('Quality Score Display', () => {
    it('displays quality score as percentage', () => {
      render(<CollectionStats collection={mockCollection} />);

      expect(screen.getByText('85%')).toBeInTheDocument();
    });

    it('displays quality progress bar', () => {
      const { container } = render(<CollectionStats collection={mockCollection} />);

      const qualityBar = container.querySelector('.bg-green-500');
      expect(qualityBar).toBeInTheDocument();
    });
  });

  describe('Date Formatting', () => {
    it('formats dates correctly', () => {
      render(<CollectionStats collection={mockCollection} />);

      // Check that dates are formatted (exact format depends on locale)
      const dateElements = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
      expect(dateElements.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Tag Display', () => {
    it('displays up to 5 tags', () => {
      render(<CollectionStats collection={mockCollection} />);

      // Collection has 5 tags, all should be displayed
      expect(screen.getByText(/research/i)).toBeInTheDocument();
      expect(screen.getByText(/academic/i)).toBeInTheDocument();
      expect(screen.getByText(/papers/i)).toBeInTheDocument();
      expect(screen.getByText(/science/i)).toBeInTheDocument();
      expect(screen.getByText(/technology/i)).toBeInTheDocument();
    });

    it('displays tag counts', () => {
      const { container } = render(<CollectionStats collection={mockCollection} />);

      // Tags should have counts in parentheses - check for specific badge content
      const badgeText = container.textContent;
      expect(badgeText).toContain('research');
      expect(badgeText).toContain('(');
      expect(badgeText).toContain(')');
    });

    it('limits tags to first 5', () => {
      const collectionWithManyTags: Collection = {
        ...mockCollection,
        tags: ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7'],
      };

      const { container } = render(<CollectionStats collection={collectionWithManyTags} />);

      const badges = container.querySelectorAll('[class*="badge"]');
      // Should only show 5 tags
      expect(badges.length).toBeLessThanOrEqual(5);
    });
  });

  describe('Empty Collection', () => {
    it('handles collection with zero resources', () => {
      const emptyCollection: Collection = {
        ...mockCollection,
        resource_count: 0,
      };

      render(<CollectionStats collection={emptyCollection} />);

      // Use getAllByText since there are multiple "0" elements
      const zeros = screen.getAllByText('0');
      expect(zeros.length).toBeGreaterThan(0);
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const { container } = render(
        <CollectionStats collection={mockCollection} className="custom-class" />
      );

      expect(container.querySelector('.custom-class')).toBeInTheDocument();
    });
  });
});

describe('CollectionStatsSkeleton', () => {
  it('renders loading skeleton', () => {
    const { container } = render(<CollectionStatsSkeleton />);

    // Check for skeleton elements by class
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('applies custom className', () => {
    const { container } = render(<CollectionStatsSkeleton className="custom-class" />);

    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });

  it('displays skeleton header', () => {
    const { container } = render(<CollectionStatsSkeleton />);

    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThanOrEqual(3);
  });
});
