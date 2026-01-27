import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { PDFViewer } from '../PDFViewer';
import { usePDFViewer } from '@/lib/hooks/usePDFViewer';

// Mock react-pdf
vi.mock('react-pdf', () => ({
  Document: ({ children, onLoadSuccess, loading }: any) => {
    // Simulate successful load
    setTimeout(() => {
      onLoadSuccess?.({ numPages: 10 });
    }, 0);
    return <div data-testid="pdf-document">{children}</div>;
  },
  Page: ({ pageNumber, loading }: any) => (
    <div data-testid="pdf-page" data-page={pageNumber}>
      Page {pageNumber}
    </div>
  ),
  pdfjs: {
    GlobalWorkerOptions: { workerSrc: '' },
    version: '3.0.0',
  },
}));

// Mock the PDF viewer hook
vi.mock('@/lib/hooks/usePDFViewer', () => ({
  usePDFViewer: vi.fn(),
}));

describe('PDFViewer', () => {
  const mockSetTotalPages = vi.fn();
  const mockSetCurrentPage = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 0,
      zoom: 1.0,
      setTotalPages: mockSetTotalPages,
      setCurrentPage: mockSetCurrentPage,
      highlights: [],
      addHighlight: vi.fn(),
      removeHighlight: vi.fn(),
      clearHighlights: vi.fn(),
    });
  });

  it('renders PDF document', async () => {
    render(
      <PDFViewer
        url="https://example.com/test.pdf"
        resourceId="test-resource"
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('pdf-document')).toBeInTheDocument();
    });
  });

  it('renders current page', async () => {
    render(
      <PDFViewer
        url="https://example.com/test.pdf"
        resourceId="test-resource"
      />
    );

    await waitFor(() => {
      const page = screen.getByTestId('pdf-page');
      expect(page).toBeInTheDocument();
      expect(page).toHaveAttribute('data-page', '1');
    });
  });

  it('calls setTotalPages on document load', async () => {
    render(
      <PDFViewer
        url="https://example.com/test.pdf"
        resourceId="test-resource"
      />
    );

    await waitFor(() => {
      expect(mockSetTotalPages).toHaveBeenCalledWith(10);
    });
  });

  it('renders with custom zoom level', async () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 1,
      totalPages: 10,
      zoom: 1.5,
      setTotalPages: mockSetTotalPages,
      setCurrentPage: mockSetCurrentPage,
      highlights: [],
      addHighlight: vi.fn(),
      removeHighlight: vi.fn(),
      clearHighlights: vi.fn(),
    });

    render(
      <PDFViewer
        url="https://example.com/test.pdf"
        resourceId="test-resource"
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('pdf-page')).toBeInTheDocument();
    });
  });

  it('renders different pages', async () => {
    (usePDFViewer as any).mockReturnValue({
      currentPage: 5,
      totalPages: 10,
      zoom: 1.0,
      setTotalPages: mockSetTotalPages,
      setCurrentPage: mockSetCurrentPage,
      highlights: [],
      addHighlight: vi.fn(),
      removeHighlight: vi.fn(),
      clearHighlights: vi.fn(),
    });

    render(
      <PDFViewer
        url="https://example.com/test.pdf"
        resourceId="test-resource"
      />
    );

    await waitFor(() => {
      const page = screen.getByTestId('pdf-page');
      expect(page).toHaveAttribute('data-page', '5');
    });
  });

  it('applies custom className', async () => {
    const { container } = render(
      <PDFViewer
        url="https://example.com/test.pdf"
        resourceId="test-resource"
        className="custom-class"
      />
    );

    await waitFor(() => {
      const viewer = container.querySelector('.pdf-viewer-container');
      expect(viewer).toHaveClass('custom-class');
    });
  });
});
