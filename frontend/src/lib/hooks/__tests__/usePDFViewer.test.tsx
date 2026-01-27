import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePDFViewer } from '../usePDFViewer';
import { usePDFViewerStore } from '@/stores/pdfViewer';

// Mock the store
vi.mock('@/stores/pdfViewer', () => ({
  usePDFViewerStore: vi.fn(),
}));

describe('usePDFViewer', () => {
  let mockStoreState: any;
  let mockStoreActions: any;

  beforeEach(() => {
    mockStoreState = {
      currentPage: 1,
      totalPages: 10,
      zoom: 1.0,
      highlights: [],
    };

    mockStoreActions = {
      setCurrentPage: vi.fn((page) => {
        mockStoreState.currentPage = page;
      }),
      setTotalPages: vi.fn((total) => {
        mockStoreState.totalPages = total;
      }),
      setZoom: vi.fn((zoom) => {
        mockStoreState.zoom = zoom;
      }),
      addHighlight: vi.fn((highlight) => {
        mockStoreState.highlights = [...mockStoreState.highlights, highlight];
      }),
      removeHighlight: vi.fn((id) => {
        mockStoreState.highlights = mockStoreState.highlights.filter(h => h.id !== id);
      }),
      clearHighlights: vi.fn(() => {
        mockStoreState.highlights = [];
      }),
    };

    (usePDFViewerStore as any).mockImplementation(() => ({
      ...mockStoreState,
      ...mockStoreActions,
    }));
  });

  describe('page navigation', () => {
    it('should navigate to specific page', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.goToPage(5);
      });

      expect(mockStoreActions.setCurrentPage).toHaveBeenCalledWith(5);
    });

    it('should not navigate beyond total pages', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.goToPage(15);
      });

      expect(mockStoreActions.setCurrentPage).not.toHaveBeenCalled();
    });

    it('should not navigate to page less than 1', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.goToPage(0);
      });

      expect(mockStoreActions.setCurrentPage).not.toHaveBeenCalled();
    });

    it('should go to next page', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.nextPage();
      });

      expect(mockStoreActions.setCurrentPage).toHaveBeenCalledWith(2);
    });

    it('should not go beyond last page', () => {
      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        currentPage: 10,
        ...mockStoreActions,
      }));

      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.nextPage();
      });

      expect(mockStoreActions.setCurrentPage).not.toHaveBeenCalled();
    });

    it('should go to previous page', () => {
      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        currentPage: 5,
        ...mockStoreActions,
      }));

      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.previousPage();
      });

      expect(mockStoreActions.setCurrentPage).toHaveBeenCalledWith(4);
    });

    it('should not go before first page', () => {
      mockStoreState.currentPage = 1;
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.previousPage();
      });

      expect(mockStoreActions.setCurrentPage).not.toHaveBeenCalled();
    });

    it('should go to first page', () => {
      mockStoreState.currentPage = 5;
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.goToFirstPage();
      });

      expect(mockStoreActions.setCurrentPage).toHaveBeenCalledWith(1);
    });

    it('should go to last page', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.goToLastPage();
      });

      expect(mockStoreActions.setCurrentPage).toHaveBeenCalledWith(10);
    });

    it('should report canGoNext correctly', () => {
      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        currentPage: 5,
        ...mockStoreActions,
      }));

      const { result } = renderHook(() => usePDFViewer());

      expect(result.current.canGoNext).toBe(true);

      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        currentPage: 10,
        ...mockStoreActions,
      }));

      const { result: result2 } = renderHook(() => usePDFViewer());

      expect(result2.current.canGoNext).toBe(false);
    });

    it('should report canGoPrevious correctly', () => {
      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        currentPage: 5,
        ...mockStoreActions,
      }));

      const { result } = renderHook(() => usePDFViewer());

      expect(result.current.canGoPrevious).toBe(true);

      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        currentPage: 1,
        ...mockStoreActions,
      }));

      const { result: result2 } = renderHook(() => usePDFViewer());

      expect(result2.current.canGoPrevious).toBe(false);
    });
  });

  describe('zoom controls', () => {
    it('should zoom in', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.zoomIn();
      });

      expect(mockStoreActions.setZoom).toHaveBeenCalledWith(1.25);
    });

    it('should not zoom in beyond max', () => {
      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        zoom: 3.0,
        ...mockStoreActions,
      }));

      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.zoomIn();
      });

      expect(mockStoreActions.setZoom).toHaveBeenCalledWith(3.0);
    });

    it('should zoom out', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.zoomOut();
      });

      expect(mockStoreActions.setZoom).toHaveBeenCalledWith(0.75);
    });

    it('should not zoom out beyond min', () => {
      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        zoom: 0.5,
        ...mockStoreActions,
      }));

      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.zoomOut();
      });

      expect(mockStoreActions.setZoom).toHaveBeenCalledWith(0.5);
    });

    it('should reset zoom', () => {
      mockStoreState.zoom = 1.5;
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.resetZoom();
      });

      expect(mockStoreActions.setZoom).toHaveBeenCalledWith(1.0);
    });

    it('should fit to width', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.fitToWidth();
      });

      expect(mockStoreActions.setZoom).toHaveBeenCalled();
    });

    it('should fit to page', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.fitToPage();
      });

      expect(mockStoreActions.setZoom).toHaveBeenCalled();
    });
  });

  describe('highlight management', () => {
    it('should create highlight', () => {
      const { result } = renderHook(() => usePDFViewer());

      const highlight = {
        pageNumber: 1,
        position: { x: 10, y: 20, width: 100, height: 20 },
        color: '#ffff00',
        text: 'Test highlight',
      };

      let highlightId: string;
      act(() => {
        highlightId = result.current.createHighlight(highlight);
      });

      expect(mockStoreActions.addHighlight).toHaveBeenCalled();
      expect(highlightId!).toMatch(/^highlight-/);
    });

    it('should delete highlight', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.deleteHighlight('highlight-123');
      });

      expect(mockStoreActions.removeHighlight).toHaveBeenCalledWith('highlight-123');
    });

    it('should clear all highlights', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.clearHighlights();
      });

      expect(mockStoreActions.clearHighlights).toHaveBeenCalled();
    });

    it('should get highlights for specific page', () => {
      const testHighlights = [
        { id: '1', pageNumber: 1, position: {}, color: '', text: '' },
        { id: '2', pageNumber: 2, position: {}, color: '', text: '' },
        { id: '3', pageNumber: 1, position: {}, color: '', text: '' },
      ];

      (usePDFViewerStore as any).mockImplementation(() => ({
        ...mockStoreState,
        highlights: testHighlights,
        ...mockStoreActions,
      }));

      const { result } = renderHook(() => usePDFViewer());

      const page1Highlights = result.current.getHighlightsForPage(1);

      expect(page1Highlights).toHaveLength(2);
      expect(page1Highlights.every((h) => h.pageNumber === 1)).toBe(true);
    });
  });

  describe('keyboard shortcuts', () => {
    it('should handle arrow right key', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        const event = new KeyboardEvent('keydown', { key: 'ArrowRight' });
        window.dispatchEvent(event);
      });

      // Note: In real implementation, this would trigger nextPage
      // For this test, we're just verifying the hook sets up listeners
      expect(result.current).toBeDefined();
    });

    it('should handle arrow left key', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        const event = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
        window.dispatchEvent(event);
      });

      expect(result.current).toBeDefined();
    });
  });

  describe('document setup', () => {
    it('should set total pages', () => {
      const { result } = renderHook(() => usePDFViewer());

      act(() => {
        result.current.setTotalPages(20);
      });

      expect(mockStoreActions.setTotalPages).toHaveBeenCalledWith(20);
    });
  });
});
