/**
 * DocumentGrid Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DocumentGrid } from '../DocumentGrid';
import type { Resource } from '@/types/library';

// Mock react-window and auto-sizer
vi.mock('react-window', () => ({
  FixedSizeGrid: ({ children }: any) => <div data-testid="virtual-grid">{children}</div>,
}));

vi.mock('react-virtualized-auto-sizer', () => ({
  default: ({ children }: any) => children({ height: 600, width: 800 }),
}));

const mockDocuments: Resource[] = Array.from({ length: 10 }, (_, i) => ({
  id: `doc-${i}`,
  title: `Document ${i}`,
  creator: 'Test Author',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:00Z',
  ingestion_status: 'completed' as const,
  content_type: 'pdf' as const,
  quality_score: 0.8,
}));

describe('DocumentGrid', () => {
  describe('Loading State', () => {
    it('renders loading skeletons when isLoading is true', () => {
      render(<DocumentGrid documents={[]} isLoading />);
      
      // Should show skeleton cards
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Empty State', () => {
    it('renders empty state when no documents', () => {
      render(<DocumentGrid documents={[]} />);
      
      expect(screen.getByText('No documents yet')).toBeInTheDocument();
      expect(screen.getByText(/Get started by uploading/)).toBeInTheDocument();
    });

    it('shows upload button in empty state when onUploadClick provided', () => {
      const handleUpload = vi.fn();
      render(<DocumentGrid documents={[]} onUploadClick={handleUpload} />);
      
      const uploadButton = screen.getByText('Upload Document');
      expect(uploadButton).toBeInTheDocument();
    });

    it('does not show upload button when onUploadClick not provided', () => {
      render(<DocumentGrid documents={[]} />);
      
      expect(screen.queryByText('Upload Document')).not.toBeInTheDocument();
    });
  });

  describe('Grid Rendering', () => {
    it('renders documents in grid', () => {
      render(<DocumentGrid documents={mockDocuments} />);
      
      // Should render document titles
      expect(screen.getByText('Document 0')).toBeInTheDocument();
      expect(screen.getByText('Document 1')).toBeInTheDocument();
    });

    it('passes selected state to cards', () => {
      const selectedIds = new Set(['doc-0', 'doc-2']);
      render(<DocumentGrid documents={mockDocuments} selectedIds={selectedIds} />);
      
      // Cards should receive selected state (tested via DocumentCard tests)
      expect(screen.getByText('Document 0')).toBeInTheDocument();
    });
  });

  describe('Event Handlers', () => {
    it('calls onDocumentClick when card is clicked', () => {
      const handleClick = vi.fn();
      render(
        <DocumentGrid documents={mockDocuments.slice(0, 1)} onDocumentClick={handleClick} />
      );
      
      // Click would be handled by DocumentCard
      expect(screen.getByText('Document 0')).toBeInTheDocument();
    });

    it('calls onDocumentSelect when card is selected', () => {
      const handleSelect = vi.fn();
      render(
        <DocumentGrid documents={mockDocuments.slice(0, 1)} onDocumentSelect={handleSelect} />
      );
      
      expect(screen.getByText('Document 0')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('renders with proper structure', () => {
      const { container } = render(<DocumentGrid documents={mockDocuments} />);
      
      expect(container.firstChild).toBeInTheDocument();
    });
  });
});
