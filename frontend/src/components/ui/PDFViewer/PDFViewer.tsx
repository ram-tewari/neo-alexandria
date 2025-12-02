import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { Button } from '../Button/Button';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import './PDFViewer.css';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerProps {
  url: string;
  onPageChange?: (page: number) => void;
  initialPage?: number;
}

/**
 * PDFViewer - Component for viewing PDF documents with zoom and navigation controls
 * 
 * Features:
 * - Page navigation (prev, next, jump-to)
 * - Zoom controls with preset levels
 * - Responsive layout with mobile-optimized scaling
 * - Loading states
 * - Error handling
 * - Touch-friendly controls (44x44px minimum)
 */
export const PDFViewer: React.FC<PDFViewerProps> = ({
  url,
  onPageChange,
  initialPage = 1,
}) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [zoom, setZoom] = useState(1.0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile devices and adjust initial zoom
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      // Adjust zoom for mobile devices
      if (mobile && zoom === 1.0) {
        setZoom(0.75);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setIsLoading(false);
    setError(null);
  };

  const handleDocumentLoadError = (error: Error) => {
    console.error('Error loading PDF:', error);
    setError('Failed to load PDF document');
    setIsLoading(false);
  };

  const handlePageChange = (page: number) => {
    const newPage = Math.max(1, Math.min(numPages, page));
    setCurrentPage(newPage);
    onPageChange?.(newPage);
  };

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(2.0, prev + 0.25));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(0.5, prev - 0.25));
  };

  const handleZoomPreset = (level: number) => {
    setZoom(level);
  };

  return (
    <div className="pdf-viewer" role="region" aria-label="PDF document viewer">
      {/* Screen reader announcements */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {!isLoading && !error && `Page ${currentPage} of ${numPages}, zoom ${Math.round(zoom * 100)}%`}
      </div>

      {/* Toolbar */}
      <div className="pdf-toolbar" role="toolbar" aria-label="PDF viewer controls">
        {/* Page Navigation */}
        <div className="pdf-toolbar-section">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1 || isLoading}
            aria-label="Previous page"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </Button>
          
          <span className="pdf-page-info">
            {isLoading ? (
              'Loading...'
            ) : (
              <>
                Page <strong>{currentPage}</strong> of <strong>{numPages}</strong>
              </>
            )}
          </span>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === numPages || isLoading}
            aria-label="Next page"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 12L10 8L6 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </Button>
        </div>

        {/* Zoom Controls */}
        <div className="pdf-toolbar-section">
          <Button
            size="sm"
            variant="ghost"
            onClick={handleZoomOut}
            disabled={zoom <= 0.5 || isLoading}
            aria-label="Zoom out"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="2"/>
              <path d="M5 7H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M11 11L14 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </Button>
          
          <div className="pdf-zoom-presets" role="group" aria-label="Zoom presets">
            <button
              className={zoom === 0.75 ? 'active' : ''}
              onClick={() => handleZoomPreset(0.75)}
              disabled={isLoading}
              aria-label="Zoom to 75%"
              aria-pressed={zoom === 0.75}
            >
              75%
            </button>
            <button
              className={zoom === 1.0 ? 'active' : ''}
              onClick={() => handleZoomPreset(1.0)}
              disabled={isLoading}
              aria-label="Zoom to 100%"
              aria-pressed={zoom === 1.0}
            >
              100%
            </button>
            <button
              className={zoom === 1.25 ? 'active' : ''}
              onClick={() => handleZoomPreset(1.25)}
              disabled={isLoading}
              aria-label="Zoom to 125%"
              aria-pressed={zoom === 1.25}
            >
              125%
            </button>
            <button
              className={zoom === 1.5 ? 'active' : ''}
              onClick={() => handleZoomPreset(1.5)}
              disabled={isLoading}
              aria-label="Zoom to 150%"
              aria-pressed={zoom === 1.5}
            >
              150%
            </button>
          </div>
          
          <span className="pdf-zoom-display">
            {Math.round(zoom * 100)}%
          </span>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={handleZoomIn}
            disabled={zoom >= 2.0 || isLoading}
            aria-label="Zoom in"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="2"/>
              <path d="M5 7H9M7 5V9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M11 11L14 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </Button>
        </div>
      </div>

      {/* PDF Canvas */}
      <div className="pdf-canvas">
        {error ? (
          <div className="pdf-error">
            <div className="pdf-error-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2"/>
                <path d="M24 16V26M24 30V32" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h3>Failed to Load PDF</h3>
            <p>{error}</p>
            <Button onClick={() => window.location.reload()}>
              Reload Page
            </Button>
          </div>
        ) : (
          <Document
            file={url}
            onLoadSuccess={handleDocumentLoadSuccess}
            onLoadError={handleDocumentLoadError}
            loading={
              <div className="pdf-loading">
                <div className="pdf-loading-spinner" />
                <p>Loading PDF...</p>
              </div>
            }
            className="pdf-document"
          >
            <Page
              pageNumber={currentPage}
              scale={zoom}
              width={isMobile ? Math.min(window.innerWidth - 32, 600) : undefined}
              renderTextLayer={true}
              renderAnnotationLayer={true}
              loading={
                <div className="pdf-page-loading">
                  <div className="pdf-loading-spinner" />
                </div>
              }
              className="pdf-page"
            />
          </Document>
        )}
      </div>
    </div>
  );
};
