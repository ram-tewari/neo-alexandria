/**
 * PDFViewer Component
 * 
 * Renders PDF documents with zoom and pagination support.
 * Integrates with the PDF viewer store for state management.
 * 
 * Features:
 * - PDF.js integration for document rendering
 * - Zoom controls via store
 * - Page navigation
 * - Loading states with skeleton
 * - Error handling with user-friendly messages
 * - Text layer and annotation layer rendering
 * 
 * @example
 * ```tsx
 * <PDFViewer 
 *   url="https://example.com/document.pdf"
 *   resourceId="123"
 * />
 * ```
 */

import { useState, useCallback } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { usePDFViewer } from '@/lib/hooks/usePDFViewer';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/loading/Skeleton';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

/**
 * Props for the PDFViewer component
 */
interface PDFViewerProps {
  /** URL of the PDF document to display */
  url: string;
  /** ID of the resource for tracking and state management */
  resourceId: string;
  /** Optional CSS class name for styling */
  className?: string;
}

export function PDFViewer({ url, resourceId, className = '' }: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const { currentPage, zoom, setTotalPages, setCurrentPage } = usePDFViewer();

  const onDocumentLoadSuccess = useCallback(
    ({ numPages: pages }: { numPages: number }) => {
      setNumPages(pages);
      setTotalPages(pages);
      setLoading(false);
      setError(null);
    },
    [setTotalPages]
  );

  const onDocumentLoadError = useCallback((err: Error) => {
    console.error('PDF load error:', err);
    setError('Failed to load PDF. Please try again.');
    setLoading(false);
  }, []);

  const onPageLoadSuccess = useCallback(() => {
    setLoading(false);
  }, []);

  const onPageLoadError = useCallback((err: Error) => {
    console.error('Page load error:', err);
    setError('Failed to load page. Please try again.');
  }, []);

  if (error) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <Alert variant="destructive" className="max-w-md">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`pdf-viewer-container ${className}`}>
      <Document
        file={url}
        onLoadSuccess={onDocumentLoadSuccess}
        onLoadError={onDocumentLoadError}
        loading={
          <div className="flex items-center justify-center h-full">
            <Skeleton className="w-full h-full" />
          </div>
        }
        error={
          <div className="flex items-center justify-center h-full p-4">
            <Alert variant="destructive" className="max-w-md">
              <AlertDescription>
                Failed to load PDF document. Please check the file and try again.
              </AlertDescription>
            </Alert>
          </div>
        }
        className="flex flex-col items-center"
      >
        <Page
          pageNumber={currentPage}
          scale={zoom}
          onLoadSuccess={onPageLoadSuccess}
          onLoadError={onPageLoadError}
          loading={
            <div className="flex items-center justify-center p-8">
              <Skeleton className="w-[600px] h-[800px]" />
            </div>
          }
          renderTextLayer={true}
          renderAnnotationLayer={true}
          className="shadow-lg"
        />
      </Document>
    </div>
  );
}
