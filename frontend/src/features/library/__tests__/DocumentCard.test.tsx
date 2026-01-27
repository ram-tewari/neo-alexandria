/**
 * DocumentCard Component Tests
 * 
 * Tests for the DocumentCard component including:
 * - Rendering with different document types
 * - Quality score badge display
 * - User interactions (click, select, delete)
 * - Hover effects
 * - Responsive behavior
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DocumentCard } from '../DocumentCard';
import type { Resource } from '@/types/library';

// Mock resource data
const mockDocument: Resource = {
  id: '1',
  title: 'Introduction to Machine Learning',
  creator: 'John Doe, Jane Smith',
  authors: ['John Doe', 'Jane Smith'],
  publication_date: '2024-01-15T00:00:00Z',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:00Z',
  ingestion_status: 'completed',
  content_type: 'pdf',
  quality_score: 0.85,
  thumbnail_url: 'https://example.com/thumbnail.jpg',
  type: 'academic_paper',
};

const mockDocumentNoThumbnail: Resource = {
  ...mockDocument,
  id: '2',
  thumbnail_url: undefined,
};

const mockDocumentLowQuality: Resource = {
  ...mockDocument,
  id: '3',
  quality_score: 0.45,
};

describe('DocumentCard', () => {
  describe('Rendering', () => {
    it('renders document title', () => {
      render(<DocumentCard document={mockDocument} />);
      expect(screen.getByText('Introduction to Machine Learning')).toBeInTheDocument();
    });

    it('renders authors', () => {
      render(<DocumentCard document={mockDocument} />);
      expect(screen.getByText('John Doe, Jane Smith')).toBeInTheDocument();
    });

    it('renders formatted date', () => {
      render(<DocumentCard document={mockDocument} />);
      // Date might vary by timezone, just check it's a valid date format
      expect(screen.getByText(/Jan \d{1,2}, 2024/)).toBeInTheDocument();
    });

    it('renders thumbnail when available', () => {
      render(<DocumentCard document={mockDocument} />);
      const img = screen.getByAltText('Introduction to Machine Learning');
      expect(img).toHaveAttribute('src', 'https://example.com/thumbnail.jpg');
    });

    it('renders placeholder icon when no thumbnail', () => {
      render(<DocumentCard document={mockDocumentNoThumbnail} />);
      // FileText icon should be present - check by class name
      const container = screen.getByText('Introduction to Machine Learning').closest('div')?.parentElement;
      expect(container?.querySelector('.lucide-file-text')).toBeInTheDocument();
    });

    it('renders quality score badge', () => {
      render(<DocumentCard document={mockDocument} />);
      expect(screen.getByText('85%')).toBeInTheDocument();
    });

    it('renders content type badge', () => {
      render(<DocumentCard document={mockDocument} />);
      // Badge shows lowercase content_type
      expect(screen.getByText('pdf')).toBeInTheDocument();
    });

    it('truncates long author names', () => {
      const longAuthors = {
        ...mockDocument,
        authors: [
          'Very Long Author Name One',
          'Very Long Author Name Two',
          'Very Long Author Name Three',
        ],
      };
      render(<DocumentCard document={longAuthors} />);
      const authorText = screen.getByText(/Very Long Author Name/);
      expect(authorText.textContent).toContain('...');
    });
  });

  describe('Quality Score Badge', () => {
    it('shows high quality badge for score >= 0.8', () => {
      render(<DocumentCard document={mockDocument} />);
      const badge = screen.getByText('85%');
      expect(badge).toHaveClass('text-green-600');
    });

    it('shows medium quality badge for score >= 0.6', () => {
      const mediumQuality = { ...mockDocument, quality_score: 0.7 };
      render(<DocumentCard document={mediumQuality} />);
      const badge = screen.getByText('70%');
      expect(badge).toHaveClass('text-yellow-600');
    });

    it('shows low quality badge for score < 0.6', () => {
      render(<DocumentCard document={mockDocumentLowQuality} />);
      const badge = screen.getByText('45%');
      expect(badge).toHaveClass('text-red-600');
    });

    it('handles missing quality score', () => {
      const noQuality = { ...mockDocument, quality_score: undefined };
      render(<DocumentCard document={noQuality} />);
      expect(screen.queryByText(/%/)).not.toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls onClick when card is clicked', () => {
      const handleClick = vi.fn();
      render(<DocumentCard document={mockDocument} onClick={handleClick} />);
      
      const card = screen.getByRole('img', { name: 'Introduction to Machine Learning' }).closest('div')?.parentElement;
      fireEvent.click(card!);
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when clicking checkbox', () => {
      const handleClick = vi.fn();
      const handleSelect = vi.fn();
      render(
        <DocumentCard
          document={mockDocument}
          onClick={handleClick}
          onSelect={handleSelect}
        />
      );
      
      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);
      
      expect(handleSelect).toHaveBeenCalled();
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('calls onSelect when checkbox is toggled', () => {
      const handleSelect = vi.fn();
      render(<DocumentCard document={mockDocument} onSelect={handleSelect} />);
      
      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);
      
      expect(handleSelect).toHaveBeenCalledWith(true);
    });

    it('shows selected state when isSelected is true', () => {
      render(<DocumentCard document={mockDocument} isSelected onSelect={vi.fn()} />);
      
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeChecked();
    });

    it('renders delete action when onDelete is provided', () => {
      const handleDelete = vi.fn();
      render(<DocumentCard document={mockDocument} onDelete={handleDelete} />);
      
      // Menu button should be present
      const menuButton = screen.getByLabelText('Document actions');
      expect(menuButton).toBeInTheDocument();
    });

    it('renders add to collection action when onAddToCollection is provided', () => {
      const handleAddToCollection = vi.fn();
      render(
        <DocumentCard document={mockDocument} onAddToCollection={handleAddToCollection} />
      );
      
      // Menu button should be present
      const menuButton = screen.getByLabelText('Document actions');
      expect(menuButton).toBeInTheDocument();
      
      // Footer button should also be present
      const card = screen.getByText('Introduction to Machine Learning').closest('div')?.parentElement?.parentElement;
      fireEvent.mouseEnter(card!);
      expect(screen.getByText('Add')).toBeInTheDocument();
    });

    it('shows Open button in footer on hover', () => {
      render(<DocumentCard document={mockDocument} onClick={vi.fn()} />);
      
      const card = screen.getByText('Introduction to Machine Learning').closest('div')?.parentElement?.parentElement;
      fireEvent.mouseEnter(card!);
      
      expect(screen.getByText('Open')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has accessible checkbox label', () => {
      render(<DocumentCard document={mockDocument} onSelect={vi.fn()} />);
      
      const checkbox = screen.getByLabelText('Select Introduction to Machine Learning');
      expect(checkbox).toBeInTheDocument();
    });

    it('has accessible actions menu', () => {
      render(<DocumentCard document={mockDocument} onDelete={vi.fn()} />);
      
      const menuButton = screen.getByLabelText('Document actions');
      expect(menuButton).toBeInTheDocument();
    });

    it('provides title attribute for truncated text', () => {
      render(<DocumentCard document={mockDocument} />);
      
      const title = screen.getByText('Introduction to Machine Learning');
      expect(title).toHaveAttribute('title', 'Introduction to Machine Learning');
    });
  });

  describe('Styling', () => {
    it('applies custom className', () => {
      const { container } = render(
        <DocumentCard document={mockDocument} className="custom-class" />
      );
      
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('applies selected ring when isSelected is true', () => {
      const { container } = render(
        <DocumentCard document={mockDocument} isSelected onSelect={vi.fn()} />
      );
      
      expect(container.firstChild).toHaveClass('ring-2', 'ring-primary');
    });

    it('applies cursor-pointer when onClick is provided', () => {
      const { container } = render(
        <DocumentCard document={mockDocument} onClick={vi.fn()} />
      );
      
      expect(container.firstChild).toHaveClass('cursor-pointer');
    });
  });

  describe('Edge Cases', () => {
    it('handles missing publication date', () => {
      const noDate = {
        ...mockDocument,
        publication_date: undefined,
      };
      render(<DocumentCard document={noDate} />);
      
      // Should fall back to created_at
      expect(screen.getByText(/Jan 15, 2024/)).toBeInTheDocument();
    });

    it('handles missing authors', () => {
      const noAuthors = {
        ...mockDocument,
        authors: undefined,
        creator: undefined,
      };
      render(<DocumentCard document={noAuthors} />);
      
      expect(screen.getByText('Unknown author')).toBeInTheDocument();
    });

    it('handles missing content type', () => {
      const noType = {
        ...mockDocument,
        content_type: undefined,
      };
      render(<DocumentCard document={noType} />);
      
      expect(screen.queryByText('PDF')).not.toBeInTheDocument();
    });

    it('renders without optional callbacks', () => {
      render(<DocumentCard document={mockDocument} />);
      
      // Should render without errors
      expect(screen.getByText('Introduction to Machine Learning')).toBeInTheDocument();
    });
  });
});
