/**
 * PDF Viewer Store Tests
 * 
 * Tests for the PDF viewer Zustand store including page navigation,
 * zoom controls, and highlight management.
 * 
 * Phase: 3 Living Library
 * Epic: 2 State Management
 * Task: 2.4
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  usePDFViewerStore,
  selectCurrentPageHighlights,
  selectIsFirstPage,
  selectIsLastPage,
  selectHighlightCountsByPage,
  selectZoomPercentage,
  type PDFHighlight
} from '../pdfViewer';

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Create a mock highlight for testing
 */
const createMockHighlight = (overrides?: Partial<PDFHighlight>): PDFHighlight => ({
  id: `hl_${Math.random().toString(36).substr(2, 9)}`,
  pageNumber: 1,
  position: { x: 100, y: 100, width: 200, height: 20 },
  color: '#ffff00',
  text: 'Highlighted text',
  createdAt: new Date().toISOString(),
  ...overrides
});

/**
 * Reset store to initial state before each test
 */
const resetStore = () => {
  usePDFViewerStore.getState().reset();
};

// ============================================================================
// Tests
// ============================================================================

describe('PDF Viewer Store', () => {
  beforeEach(() => {
    resetStore();
  });

  // ==========================================================================
  // Initial State
  // ==========================================================================

  describe('Initial State', () => {
    it('should start on page 1', () => {
      const { currentPage } = usePDFViewerStore.getState();
      expect(currentPage).toBe(1);
    });

    it('should have 0 total pages', () => {
      const { totalPages } = usePDFViewerStore.getState();
      expect(totalPages).toBe(0);
    });

    it('should have 100% zoom', () => {
      const { zoom } = usePDFViewerStore.getState();
      expect(zoom).toBe(1.0);
    });

    it('should have no highlights', () => {
      const { highlights } = usePDFViewerStore.getState();
      expect(highlights).toEqual([]);
    });

    it('should not be loading', () => {
      const { isLoading } = usePDFViewerStore.getState();
      expect(isLoading).toBe(false);
    });

    it('should have single view mode', () => {
      const { viewMode } = usePDFViewerStore.getState();
      expect(viewMode).toBe('single');
    });

    it('should have sidebar visible', () => {
      const { sidebarVisible } = usePDFViewerStore.getState();
      expect(sidebarVisible).toBe(true);
    });
  });

  // ==========================================================================
  // Page Navigation
  // ==========================================================================

  describe('Page Navigation', () => {
    beforeEach(() => {
      usePDFViewerStore.getState().setTotalPages(10);
    });

    it('should set current page', () => {
      usePDFViewerStore.getState().setCurrentPage(5);
      expect(usePDFViewerStore.getState().currentPage).toBe(5);
    });

    it('should clamp page to valid range (min)', () => {
      usePDFViewerStore.getState().setCurrentPage(0);
      expect(usePDFViewerStore.getState().currentPage).toBe(1);
    });

    it('should clamp page to valid range (max)', () => {
      usePDFViewerStore.getState().setCurrentPage(20);
      expect(usePDFViewerStore.getState().currentPage).toBe(10);
    });

    it('should navigate to next page', () => {
      usePDFViewerStore.getState().setCurrentPage(5);
      usePDFViewerStore.getState().nextPage();
      expect(usePDFViewerStore.getState().currentPage).toBe(6);
    });

    it('should not go beyond last page', () => {
      usePDFViewerStore.getState().setCurrentPage(10);
      usePDFViewerStore.getState().nextPage();
      expect(usePDFViewerStore.getState().currentPage).toBe(10);
    });

    it('should navigate to previous page', () => {
      usePDFViewerStore.getState().setCurrentPage(5);
      usePDFViewerStore.getState().previousPage();
      expect(usePDFViewerStore.getState().currentPage).toBe(4);
    });

    it('should not go before first page', () => {
      usePDFViewerStore.getState().setCurrentPage(1);
      usePDFViewerStore.getState().previousPage();
      expect(usePDFViewerStore.getState().currentPage).toBe(1);
    });

    it('should set total pages', () => {
      usePDFViewerStore.getState().setTotalPages(25);
      expect(usePDFViewerStore.getState().totalPages).toBe(25);
    });
  });

  // ==========================================================================
  // Zoom Controls
  // ==========================================================================

  describe('Zoom Controls', () => {
    it('should set zoom level', () => {
      usePDFViewerStore.getState().setZoom(1.5);
      expect(usePDFViewerStore.getState().zoom).toBe(1.5);
    });

    it('should clamp zoom to minimum (0.25)', () => {
      usePDFViewerStore.getState().setZoom(0.1);
      expect(usePDFViewerStore.getState().zoom).toBe(0.25);
    });

    it('should clamp zoom to maximum (3.0)', () => {
      usePDFViewerStore.getState().setZoom(5.0);
      expect(usePDFViewerStore.getState().zoom).toBe(3.0);
    });

    it('should zoom in by 25%', () => {
      usePDFViewerStore.getState().setZoom(1.0);
      usePDFViewerStore.getState().zoomIn();
      expect(usePDFViewerStore.getState().zoom).toBe(1.25);
    });

    it('should not zoom in beyond maximum', () => {
      usePDFViewerStore.getState().setZoom(2.9);
      usePDFViewerStore.getState().zoomIn();
      expect(usePDFViewerStore.getState().zoom).toBe(3.0);
    });

    it('should zoom out by 20%', () => {
      usePDFViewerStore.getState().setZoom(1.0);
      usePDFViewerStore.getState().zoomOut();
      expect(usePDFViewerStore.getState().zoom).toBe(0.8);
    });

    it('should not zoom out beyond minimum', () => {
      usePDFViewerStore.getState().setZoom(0.3);
      usePDFViewerStore.getState().zoomOut();
      expect(usePDFViewerStore.getState().zoom).toBe(0.25);
    });

    it('should reset zoom to 100%', () => {
      usePDFViewerStore.getState().setZoom(1.5);
      usePDFViewerStore.getState().resetZoom();
      expect(usePDFViewerStore.getState().zoom).toBe(1.0);
    });

    it('should fit width', () => {
      usePDFViewerStore.getState().fitWidth();
      expect(usePDFViewerStore.getState().zoom).toBe(1.2);
    });

    it('should fit page', () => {
      usePDFViewerStore.getState().fitPage();
      expect(usePDFViewerStore.getState().zoom).toBe(0.9);
    });
  });

  // ==========================================================================
  // Highlight Management
  // ==========================================================================

  describe('Highlight Management', () => {
    it('should add a highlight', () => {
      const highlight = createMockHighlight();
      usePDFViewerStore.getState().addHighlight(highlight);

      const { highlights } = usePDFViewerStore.getState();
      expect(highlights).toHaveLength(1);
      expect(highlights[0]).toEqual(highlight);
    });

    it('should add multiple highlights', () => {
      const highlight1 = createMockHighlight({ id: 'hl_1' });
      const highlight2 = createMockHighlight({ id: 'hl_2' });

      usePDFViewerStore.getState().addHighlight(highlight1);
      usePDFViewerStore.getState().addHighlight(highlight2);

      expect(usePDFViewerStore.getState().highlights).toHaveLength(2);
    });

    it('should update a highlight', () => {
      const highlight = createMockHighlight({ id: 'hl_1', color: '#ffff00' });
      usePDFViewerStore.getState().addHighlight(highlight);

      usePDFViewerStore.getState().updateHighlight('hl_1', { color: '#ff0000' });

      const updated = usePDFViewerStore.getState().highlights[0];
      expect(updated.color).toBe('#ff0000');
      expect(updated.id).toBe('hl_1');
    });

    it('should not affect other highlights when updating', () => {
      const highlight1 = createMockHighlight({ id: 'hl_1', color: '#ffff00' });
      const highlight2 = createMockHighlight({ id: 'hl_2', color: '#00ff00' });

      usePDFViewerStore.getState().addHighlight(highlight1);
      usePDFViewerStore.getState().addHighlight(highlight2);

      usePDFViewerStore.getState().updateHighlight('hl_1', { color: '#ff0000' });

      const { highlights } = usePDFViewerStore.getState();
      expect(highlights[0].color).toBe('#ff0000'); // Updated color
      expect(highlights[1].color).toBe('#00ff00'); // Unchanged
    });

    it('should remove a highlight', () => {
      const highlight1 = createMockHighlight({ id: 'hl_1' });
      const highlight2 = createMockHighlight({ id: 'hl_2' });

      usePDFViewerStore.getState().addHighlight(highlight1);
      usePDFViewerStore.getState().addHighlight(highlight2);

      usePDFViewerStore.getState().removeHighlight('hl_1');

      const { highlights } = usePDFViewerStore.getState();
      expect(highlights).toHaveLength(1);
      expect(highlights[0].id).toBe('hl_2');
    });

    it('should clear all highlights', () => {
      usePDFViewerStore.getState().addHighlight(createMockHighlight());
      usePDFViewerStore.getState().addHighlight(createMockHighlight());

      usePDFViewerStore.getState().clearHighlights();

      expect(usePDFViewerStore.getState().highlights).toEqual([]);
    });
  });

  // ==========================================================================
  // UI State
  // ==========================================================================

  describe('UI State', () => {
    it('should set loading state', () => {
      usePDFViewerStore.getState().setLoading(true);
      expect(usePDFViewerStore.getState().isLoading).toBe(true);

      usePDFViewerStore.getState().setLoading(false);
      expect(usePDFViewerStore.getState().isLoading).toBe(false);
    });

    it('should set view mode', () => {
      usePDFViewerStore.getState().setViewMode('continuous');
      expect(usePDFViewerStore.getState().viewMode).toBe('continuous');
    });

    it('should toggle sidebar', () => {
      usePDFViewerStore.getState().toggleSidebar();
      expect(usePDFViewerStore.getState().sidebarVisible).toBe(false);

      usePDFViewerStore.getState().toggleSidebar();
      expect(usePDFViewerStore.getState().sidebarVisible).toBe(true);
    });

    it('should set sidebar tab', () => {
      usePDFViewerStore.getState().setSidebarTab('outline');
      expect(usePDFViewerStore.getState().sidebarTab).toBe('outline');
    });
  });

  // ==========================================================================
  // Reset
  // ==========================================================================

  describe('Reset', () => {
    it('should reset all state to initial values', () => {
      // Modify state
      usePDFViewerStore.getState().setCurrentPage(5);
      usePDFViewerStore.getState().setTotalPages(10);
      usePDFViewerStore.getState().setZoom(1.5);
      usePDFViewerStore.getState().addHighlight(createMockHighlight());
      usePDFViewerStore.getState().setLoading(true);
      usePDFViewerStore.getState().setViewMode('continuous');
      usePDFViewerStore.getState().toggleSidebar();

      // Reset
      usePDFViewerStore.getState().reset();

      // Verify initial state
      const state = usePDFViewerStore.getState();
      expect(state.currentPage).toBe(1);
      expect(state.totalPages).toBe(0);
      expect(state.zoom).toBe(1.0);
      expect(state.highlights).toEqual([]);
      expect(state.isLoading).toBe(false);
      expect(state.viewMode).toBe('single');
      expect(state.sidebarVisible).toBe(true);
      expect(state.sidebarTab).toBe('thumbnails');
    });
  });

  // ==========================================================================
  // Selectors
  // ==========================================================================

  describe('Selectors', () => {
    describe('selectCurrentPageHighlights', () => {
      it('should return highlights for current page', () => {
        const highlight1 = createMockHighlight({ pageNumber: 1 });
        const highlight2 = createMockHighlight({ pageNumber: 2 });
        const highlight3 = createMockHighlight({ pageNumber: 1 });

        usePDFViewerStore.getState().addHighlight(highlight1);
        usePDFViewerStore.getState().addHighlight(highlight2);
        usePDFViewerStore.getState().addHighlight(highlight3);
        usePDFViewerStore.getState().setCurrentPage(1);

        const pageHighlights = selectCurrentPageHighlights(usePDFViewerStore.getState());
        expect(pageHighlights).toHaveLength(2);
        expect(pageHighlights.every(h => h.pageNumber === 1)).toBe(true);
      });

      it('should return empty array when no highlights on page', () => {
        usePDFViewerStore.getState().addHighlight(createMockHighlight({ pageNumber: 2 }));
        usePDFViewerStore.getState().setCurrentPage(1);

        const pageHighlights = selectCurrentPageHighlights(usePDFViewerStore.getState());
        expect(pageHighlights).toEqual([]);
      });
    });

    describe('selectIsFirstPage', () => {
      it('should return true on first page', () => {
        usePDFViewerStore.getState().setTotalPages(10);
        usePDFViewerStore.getState().setCurrentPage(1);
        expect(selectIsFirstPage(usePDFViewerStore.getState())).toBe(true);
      });

      it('should return false on other pages', () => {
        usePDFViewerStore.getState().setTotalPages(10);
        usePDFViewerStore.getState().setCurrentPage(2);
        expect(selectIsFirstPage(usePDFViewerStore.getState())).toBe(false);
      });
    });

    describe('selectIsLastPage', () => {
      it('should return true on last page', () => {
        usePDFViewerStore.getState().setTotalPages(10);
        usePDFViewerStore.getState().setCurrentPage(10);
        expect(selectIsLastPage(usePDFViewerStore.getState())).toBe(true);
      });

      it('should return false on other pages', () => {
        usePDFViewerStore.getState().setTotalPages(10);
        usePDFViewerStore.getState().setCurrentPage(5);
        expect(selectIsLastPage(usePDFViewerStore.getState())).toBe(false);
      });
    });

    describe('selectHighlightCountsByPage', () => {
      it('should count highlights per page', () => {
        usePDFViewerStore.getState().addHighlight(createMockHighlight({ pageNumber: 1 }));
        usePDFViewerStore.getState().addHighlight(createMockHighlight({ pageNumber: 1 }));
        usePDFViewerStore.getState().addHighlight(createMockHighlight({ pageNumber: 2 }));
        usePDFViewerStore.getState().addHighlight(createMockHighlight({ pageNumber: 3 }));

        const counts = selectHighlightCountsByPage(usePDFViewerStore.getState());
        expect(counts[1]).toBe(2);
        expect(counts[2]).toBe(1);
        expect(counts[3]).toBe(1);
      });

      it('should return empty object when no highlights', () => {
        const counts = selectHighlightCountsByPage(usePDFViewerStore.getState());
        expect(counts).toEqual({});
      });
    });

    describe('selectZoomPercentage', () => {
      it('should return zoom as percentage', () => {
        usePDFViewerStore.getState().setZoom(1.0);
        expect(selectZoomPercentage(usePDFViewerStore.getState())).toBe(100);

        usePDFViewerStore.getState().setZoom(1.5);
        expect(selectZoomPercentage(usePDFViewerStore.getState())).toBe(150);

        usePDFViewerStore.getState().setZoom(0.75);
        expect(selectZoomPercentage(usePDFViewerStore.getState())).toBe(75);
      });
    });
  });
});
