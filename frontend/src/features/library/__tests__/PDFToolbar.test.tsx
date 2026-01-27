import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PDFToolbar } from '../PDFToolbar';
import { usePDFViewer } from '@/lib/hooks/usePDFViewer';

// Mock the PDF viewer hook
vi.mock('@/lib/hooks/usePDFViewer', () => ({
  usePDFViewer: vi.fn(),
}));

describe('PDFToolbar', () => {
  const mockSetCurrentPage = vi.fn();
  const mockSetZoom = vi.fn();
  const mockNextPage = vi.fn();
  const mockPrevPage = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.0,
      setCurrentPage: mockSetCurrentPage,
      setZoom: mockSetZoom,
      nextPage: mockNextPage,
      prevPage: mockPrevPage,
      canGoNext: true,
      canGoPrev: false,
    });
  });

  it('renders toolbar with page navigation', () => {
    render(<PDFToolbar />);

    expect(screen.getByDisplayValue('1')).toBeInTheDocument();
    expect(screen.getByText('/ 10')).toBeInTheDocument();
  });

  it('navigates to next page', async () => {
    render(<PDFToolbar />);

    const nextButton = screen.getByTitle('Next page (→)');
    fireEvent.click(nextButton);

    expect(mockNextPage).toHaveBeenCalled();
  });

  it('navigates to previous page', async () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 5,
      totalPages: 10,
      zoom: 1.0,
      setCurrentPage: mockSetCurrentPage,
      setZoom: mockSetZoom,
      nextPage: mockNextPage,
      prevPage: mockPrevPage,
      canGoNext: true,
      canGoPrev: true,
    });

    render(<PDFToolbar />);

    const prevButton = screen.getByTitle('Previous page (←)');
    fireEvent.click(prevButton);

    expect(mockPrevPage).toHaveBeenCalled();
  });

  it('disables previous button on first page', () => {
    render(<PDFToolbar />);

    const prevButton = screen.getByTitle('Previous page (←)');
    expect(prevButton).toBeDisabled();
  });

  it('disables next button on last page', () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 10,
      totalPages: 10,
      zoom: 1.0,
      setCurrentPage: mockSetCurrentPage,
      setZoom: mockSetZoom,
      nextPage: mockNextPage,
      prevPage: mockPrevPage,
      canGoNext: false,
      canGoPrev: true,
    });

    render(<PDFToolbar />);

    const nextButton = screen.getByTitle('Next page (→)');
    expect(nextButton).toBeDisabled();
  });

  it('jumps to specific page', async () => {
    render(<PDFToolbar />);

    const pageInput = screen.getByDisplayValue('1');
    fireEvent.change(pageInput, { target: { value: '5' } });

    expect(mockSetCurrentPage).toHaveBeenCalledWith(5);
  });

  it('renders zoom controls', () => {
    render(<PDFToolbar />);

    expect(screen.getByTitle('Zoom out (Ctrl+-)')).toBeInTheDocument();
    expect(screen.getByTitle('Zoom in (Ctrl++)')).toBeInTheDocument();
    expect(screen.getByTitle('Fit to width')).toBeInTheDocument();
  });

  it('zooms in', async () => {
    render(<PDFToolbar />);

    const zoomInButton = screen.getByTitle('Zoom in (Ctrl++)');
    fireEvent.click(zoomInButton);

    expect(mockSetZoom).toHaveBeenCalledWith(1.25);
  });

  it('zooms out', async () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.5,
      setCurrentPage: mockSetCurrentPage,
      setZoom: mockSetZoom,
      nextPage: mockNextPage,
      prevPage: mockPrevPage,
      canGoNext: true,
      canGoPrev: false,
    });

    render(<PDFToolbar />);

    const zoomOutButton = screen.getByTitle('Zoom out (Ctrl+-)');
    fireEvent.click(zoomOutButton);

    expect(mockSetZoom).toHaveBeenCalledWith(1.25);
  });

  it('fits to width', async () => {
    render(<PDFToolbar />);

    const fitButton = screen.getByTitle('Fit to width');
    fireEvent.click(fitButton);

    expect(mockSetZoom).toHaveBeenCalledWith(1.0);
  });

  it('renders download button', () => {
    render(<PDFToolbar resourceUrl="https://example.com/test.pdf" />);

    expect(screen.getByTitle('Download PDF')).toBeInTheDocument();
  });

  it('renders print button', () => {
    render(<PDFToolbar resourceUrl="https://example.com/test.pdf" />);

    expect(screen.getByTitle('Print PDF')).toBeInTheDocument();
  });

  it('disables download when no URL provided', () => {
    render(<PDFToolbar />);

    const downloadButton = screen.getByTitle('Download PDF');
    expect(downloadButton).toBeDisabled();
  });

  it('disables print when no URL provided', () => {
    render(<PDFToolbar />);

    const printButton = screen.getByTitle('Print PDF');
    expect(printButton).toBeDisabled();
  });

  it('handles keyboard shortcuts', () => {
    render(<PDFToolbar />);

    // Simulate arrow right key
    fireEvent.keyDown(window, { key: 'ArrowRight' });
    expect(mockNextPage).toHaveBeenCalled();
  });

  it('applies custom className', () => {
    const { container } = render(<PDFToolbar className="custom-class" />);

    const toolbar = container.firstChild;
    expect(toolbar).toHaveClass('custom-class');
  });
});
