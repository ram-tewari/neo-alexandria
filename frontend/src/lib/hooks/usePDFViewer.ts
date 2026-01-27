import { useCallback, useEffect } from 'react';
import { usePDFViewerStore } from '@/stores/pdfViewer';

/**
 * Custom hook for PDF viewer functionality
 * Provides page navigation, zoom controls, and highlight management
 * with keyboard shortcuts support
 */
export function usePDFViewer() {
  const {
    currentPage,
    totalPages,
    zoom,
    highlights,
    setCurrentPage,
    setTotalPages,
    setZoom,
    addHighlight,
    removeHighlight,
    clearHighlights,
  } = usePDFViewerStore();

  // Page navigation
  const goToPage = useCallback(
    (page: number) => {
      if (page >= 1 && page <= totalPages) {
        setCurrentPage(page);
      }
    },
    [totalPages, setCurrentPage]
  );

  const nextPage = useCallback(() => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  }, [currentPage, totalPages, setCurrentPage]);

  const previousPage = useCallback(() => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  }, [currentPage, setCurrentPage]);

  const goToFirstPage = useCallback(() => {
    setCurrentPage(1);
  }, [setCurrentPage]);

  const goToLastPage = useCallback(() => {
    if (totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, setCurrentPage]);

  // Zoom controls
  const zoomIn = useCallback(() => {
    setZoom(Math.min(zoom + 0.25, 3.0));
  }, [zoom, setZoom]);

  const zoomOut = useCallback(() => {
    setZoom(Math.max(zoom - 0.25, 0.5));
  }, [zoom, setZoom]);

  const resetZoom = useCallback(() => {
    setZoom(1.0);
  }, [setZoom]);

  const fitToWidth = useCallback(() => {
    setZoom(1.0); // Simplified - actual implementation would calculate based on container width
  }, [setZoom]);

  const fitToPage = useCallback(() => {
    setZoom(0.9); // Simplified - actual implementation would calculate based on container height
  }, [setZoom]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Page navigation
      if (e.key === 'ArrowRight' || e.key === 'PageDown') {
        e.preventDefault();
        nextPage();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault();
        previousPage();
      } else if (e.key === 'Home') {
        e.preventDefault();
        goToFirstPage();
      } else if (e.key === 'End') {
        e.preventDefault();
        goToLastPage();
      }
      // Zoom controls
      else if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        zoomIn();
      } else if (e.key === '-') {
        e.preventDefault();
        zoomOut();
      } else if (e.key === '0' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        resetZoom();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [nextPage, previousPage, goToFirstPage, goToLastPage, zoomIn, zoomOut, resetZoom]);

  // Highlight management
  const createHighlight = useCallback(
    (highlight: {
      pageNumber: number;
      position: { x: number; y: number; width: number; height: number };
      color: string;
      text: string;
    }) => {
      const newHighlight = {
        id: `highlight-${Date.now()}-${Math.random()}`,
        ...highlight,
      };
      addHighlight(newHighlight);
      return newHighlight.id;
    },
    [addHighlight]
  );

  const deleteHighlight = useCallback(
    (highlightId: string) => {
      removeHighlight(highlightId);
    },
    [removeHighlight]
  );

  const getHighlightsForPage = useCallback(
    (pageNumber: number) => {
      return highlights.filter((h) => h.pageNumber === pageNumber);
    },
    [highlights]
  );

  return {
    // State
    currentPage,
    totalPages,
    zoom,
    highlights,

    // Page navigation
    goToPage,
    nextPage,
    previousPage,
    goToFirstPage,
    goToLastPage,
    canGoNext: currentPage < totalPages,
    canGoPrevious: currentPage > 1,

    // Zoom controls
    zoomIn,
    zoomOut,
    resetZoom,
    fitToWidth,
    fitToPage,
    setZoom,

    // Document setup
    setTotalPages,

    // Highlight management
    createHighlight,
    deleteHighlight,
    clearHighlights,
    getHighlightsForPage,
  };
}
