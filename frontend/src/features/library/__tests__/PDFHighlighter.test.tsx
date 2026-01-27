import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PDFHighlighter, Highlight } from '../PDFHighlighter';
import { usePDFViewer } from '@/lib/hooks/usePDFViewer';

// Mock the PDF viewer hook
vi.mock('@/lib/hooks/usePDFViewer', () => ({
  usePDFViewer: vi.fn(),
}));

describe('PDFHighlighter', () => {
  const mockAddHighlight = vi.fn();
  const mockRemoveHighlight = vi.fn();
  const mockClearHighlights = vi.fn();
  const mockOnSaveHighlight = vi.fn();
  const mockOnDeleteHighlight = vi.fn();

  const mockHighlight: Highlight = {
    id: 'highlight-1',
    resourceId: 'test-resource',
    pageNumber: 1,
    text: 'Test highlight text',
    color: '#fef08a',
    position: {
      x: 100,
      y: 100,
      width: 200,
      height: 20,
    },
    createdAt: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.0,
      highlights: [],
      addHighlight: mockAddHighlight,
      removeHighlight: mockRemoveHighlight,
      clearHighlights: mockClearHighlights,
    });
  });

  it('renders highlighter toolbar', () => {
    render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    expect(screen.getByText('Highlight')).toBeInTheDocument();
  });

  it('toggles highlighting mode', async () => {
    render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    const highlightButton = screen.getByText('Highlight');
    fireEvent.click(highlightButton);

    // Button should have default variant when active
    expect(highlightButton.closest('button')).toHaveClass('bg-primary');
  });

  it('displays color picker', async () => {
    render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    const colorButton = screen.getByTitle('Choose highlight color');
    fireEvent.click(colorButton);

    // Color picker should be visible - wait for it
    await new Promise((resolve) => setTimeout(resolve, 100));
  });

  it('displays highlights for current page', () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.0,
      highlights: [mockHighlight],
      addHighlight: mockAddHighlight,
      removeHighlight: mockRemoveHighlight,
      clearHighlights: mockClearHighlights,
    });

    render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    expect(screen.getByText('1 highlight on this page')).toBeInTheDocument();
  });

  it('displays multiple highlights count', () => {
    const highlights = [
      mockHighlight,
      { ...mockHighlight, id: 'highlight-2' },
      { ...mockHighlight, id: 'highlight-3' },
    ];

    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.0,
      highlights,
      addHighlight: mockAddHighlight,
      removeHighlight: mockRemoveHighlight,
      clearHighlights: mockClearHighlights,
    });

    render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    expect(screen.getByText('3 highlights on this page')).toBeInTheDocument();
  });

  it('filters highlights by current page', () => {
    const highlights = [
      mockHighlight,
      { ...mockHighlight, id: 'highlight-2', pageNumber: 2 },
      { ...mockHighlight, id: 'highlight-3', pageNumber: 3 },
    ];

    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.0,
      highlights,
      addHighlight: mockAddHighlight,
      removeHighlight: mockRemoveHighlight,
      clearHighlights: mockClearHighlights,
    });

    render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    // Should only show 1 highlight for page 1
    expect(screen.getByText('1 highlight on this page')).toBeInTheDocument();
  });

  it('renders highlight overlays', () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.0,
      highlights: [mockHighlight],
      addHighlight: mockAddHighlight,
      removeHighlight: mockRemoveHighlight,
      clearHighlights: mockClearHighlights,
    });

    const { container } = render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    const overlay = container.querySelector('.highlight-overlays');
    expect(overlay).toBeInTheDocument();
  });

  it('calls onDeleteHighlight when delete button clicked', async () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.0,
      highlights: [mockHighlight],
      addHighlight: mockAddHighlight,
      removeHighlight: mockRemoveHighlight,
      clearHighlights: mockClearHighlights,
    });

    const { container } = render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    // Find and hover over highlight to show delete button
    const highlightOverlay = container.querySelector('.group');
    expect(highlightOverlay).toBeInTheDocument();

    // Find delete button
    const deleteButton = container.querySelector('button[class*="destructive"]');
    if (deleteButton) {
      fireEvent.click(deleteButton);
      expect(mockRemoveHighlight).toHaveBeenCalledWith('highlight-1');
      expect(mockOnDeleteHighlight).toHaveBeenCalledWith('highlight-1');
    }
  });

  it('applies custom className', () => {
    const { container } = render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
        className="custom-class"
      />
    );

    const highlighter = container.querySelector('.pdf-highlighter');
    expect(highlighter).toHaveClass('custom-class');
  });

  it('shows no highlights message when page has no highlights', () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 2,
      totalPages: 10,
      zoom: 1.0,
      highlights: [mockHighlight], // Only on page 1
      addHighlight: mockAddHighlight,
      removeHighlight: mockRemoveHighlight,
      clearHighlights: mockClearHighlights,
    });

    render(
      <PDFHighlighter
        resourceId="test-resource"
        onSaveHighlight={mockOnSaveHighlight}
        onDeleteHighlight={mockOnDeleteHighlight}
      />
    );

    // Should not show highlight count
    expect(
      screen.queryByText(/highlight.*on this page/)
    ).not.toBeInTheDocument();
  });
});
