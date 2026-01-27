/**
 * PDF Viewer Store
 * 
 * Zustand store for managing PDF viewer state including page navigation,
 * zoom level, and text highlights.
 * 
 * Phase: 3 Living Library
 * Epic: 2 State Management
 * Task: 2.2
 */

import { create } from 'zustand';

// ============================================================================
// Types
// ============================================================================

/**
 * Text highlight in a PDF
 */
export interface PDFHighlight {
  /** Unique highlight ID */
  id: string;
  /** Page number (1-indexed) */
  pageNumber: number;
  /** Position and dimensions on the page */
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  /** Highlight color (hex or CSS color) */
  color: string;
  /** Highlighted text content */
  text: string;
  /** Optional note/comment */
  note?: string;
  /** Creation timestamp */
  createdAt: string;
}

// ============================================================================
// State Interface
// ============================================================================

/**
 * PDF viewer store state and actions
 */
interface PDFViewerState {
  // ========================================================================
  // State
  // ========================================================================
  
  /** Current page number (1-indexed) */
  currentPage: number;
  
  /** Total number of pages in the document */
  totalPages: number;
  
  /** Zoom level (1.0 = 100%) */
  zoom: number;
  
  /** Text highlights on the document */
  highlights: PDFHighlight[];
  
  /** Whether the document is loading */
  isLoading: boolean;
  
  /** Current view mode */
  viewMode: 'single' | 'continuous' | 'facing';
  
  /** Whether sidebar is visible */
  sidebarVisible: boolean;
  
  /** Active sidebar tab */
  sidebarTab: 'thumbnails' | 'outline' | 'highlights';
  
  // ========================================================================
  // Actions
  // ========================================================================
  
  /**
   * Set current page number
   * Clamps to valid range [1, totalPages]
   */
  setCurrentPage: (page: number) => void;
  
  /**
   * Set total number of pages
   * Called when document loads
   */
  setTotalPages: (total: number) => void;
  
  /**
   * Set zoom level
   * Common values: 0.5, 0.75, 1.0, 1.25, 1.5, 2.0
   */
  setZoom: (zoom: number) => void;
  
  /**
   * Navigate to next page
   * Does nothing if already on last page
   */
  nextPage: () => void;
  
  /**
   * Navigate to previous page
   * Does nothing if already on first page
   */
  previousPage: () => void;
  
  /**
   * Zoom in (increase by 25%)
   * Max zoom: 3.0 (300%)
   */
  zoomIn: () => void;
  
  /**
   * Zoom out (decrease by 25%)
   * Min zoom: 0.25 (25%)
   */
  zoomOut: () => void;
  
  /**
   * Reset zoom to 100%
   */
  resetZoom: () => void;
  
  /**
   * Fit page width to viewport
   */
  fitWidth: () => void;
  
  /**
   * Fit entire page to viewport
   */
  fitPage: () => void;
  
  /**
   * Add a text highlight
   */
  addHighlight: (highlight: PDFHighlight) => void;
  
  /**
   * Update a highlight by ID
   */
  updateHighlight: (id: string, updates: Partial<PDFHighlight>) => void;
  
  /**
   * Remove a highlight by ID
   */
  removeHighlight: (id: string) => void;
  
  /**
   * Clear all highlights
   */
  clearHighlights: () => void;
  
  /**
   * Set loading state
   */
  setLoading: (loading: boolean) => void;
  
  /**
   * Set view mode
   */
  setViewMode: (mode: PDFViewerState['viewMode']) => void;
  
  /**
   * Toggle sidebar visibility
   */
  toggleSidebar: () => void;
  
  /**
   * Set active sidebar tab
   */
  setSidebarTab: (tab: PDFViewerState['sidebarTab']) => void;
  
  /**
   * Reset viewer state
   * Called when switching documents
   */
  reset: () => void;
}

// ============================================================================
// Store Implementation
// ============================================================================

/**
 * PDF viewer store instance
 * 
 * @example
 * ```typescript
 * // In a component
 * const { currentPage, totalPages, nextPage, setZoom } = usePDFViewerStore();
 * 
 * // Navigate pages
 * <button onClick={nextPage}>Next Page</button>
 * 
 * // Zoom controls
 * <button onClick={() => setZoom(1.5)}>150%</button>
 * ```
 */
export const usePDFViewerStore = create<PDFViewerState>((set, get) => ({
  // Initial state
  currentPage: 1,
  totalPages: 0,
  zoom: 1.0,
  highlights: [],
  isLoading: false,
  viewMode: 'single',
  sidebarVisible: true,
  sidebarTab: 'thumbnails',
  
  // Page navigation actions
  setCurrentPage: (page) => set((state) => ({
    currentPage: Math.max(1, Math.min(page, state.totalPages || 1))
  })),
  
  setTotalPages: (total) => set({ totalPages: total }),
  
  nextPage: () => {
    const { currentPage, totalPages } = get();
    if (currentPage < totalPages) {
      set({ currentPage: currentPage + 1 });
    }
  },
  
  previousPage: () => {
    const { currentPage } = get();
    if (currentPage > 1) {
      set({ currentPage: currentPage - 1 });
    }
  },
  
  // Zoom actions
  setZoom: (zoom) => set({ zoom: Math.max(0.25, Math.min(zoom, 3.0)) }),
  
  zoomIn: () => {
    const { zoom } = get();
    set({ zoom: Math.min(zoom * 1.25, 3.0) });
  },
  
  zoomOut: () => {
    const { zoom } = get();
    set({ zoom: Math.max(zoom * 0.8, 0.25) });
  },
  
  resetZoom: () => set({ zoom: 1.0 }),
  
  fitWidth: () => {
    // This will be calculated based on viewport width
    // For now, set a reasonable default
    set({ zoom: 1.2 });
  },
  
  fitPage: () => {
    // This will be calculated based on viewport height
    // For now, set a reasonable default
    set({ zoom: 0.9 });
  },
  
  // Highlight actions
  addHighlight: (highlight) => set((state) => ({
    highlights: [...state.highlights, highlight]
  })),
  
  updateHighlight: (id, updates) => set((state) => ({
    highlights: state.highlights.map((h) =>
      h.id === id ? { ...h, ...updates } : h
    )
  })),
  
  removeHighlight: (id) => set((state) => ({
    highlights: state.highlights.filter((h) => h.id !== id)
  })),
  
  clearHighlights: () => set({ highlights: [] }),
  
  // UI state actions
  setLoading: (loading) => set({ isLoading: loading }),
  
  setViewMode: (mode) => set({ viewMode: mode }),
  
  toggleSidebar: () => set((state) => ({
    sidebarVisible: !state.sidebarVisible
  })),
  
  setSidebarTab: (tab) => set({ sidebarTab: tab }),
  
  // Reset action
  reset: () => set({
    currentPage: 1,
    totalPages: 0,
    zoom: 1.0,
    highlights: [],
    isLoading: false,
    viewMode: 'single',
    sidebarVisible: true,
    sidebarTab: 'thumbnails'
  })
}));

// ============================================================================
// Selectors
// ============================================================================

/**
 * Selector: Get highlights for current page
 * 
 * @example
 * ```typescript
 * const pageHighlights = usePDFViewerStore(selectCurrentPageHighlights);
 * ```
 */
export const selectCurrentPageHighlights = (state: PDFViewerState): PDFHighlight[] => {
  return state.highlights.filter((h) => h.pageNumber === state.currentPage);
};

/**
 * Selector: Check if on first page
 * 
 * @example
 * ```typescript
 * const isFirstPage = usePDFViewerStore(selectIsFirstPage);
 * <button disabled={isFirstPage}>Previous</button>
 * ```
 */
export const selectIsFirstPage = (state: PDFViewerState): boolean => {
  return state.currentPage === 1;
};

/**
 * Selector: Check if on last page
 * 
 * @example
 * ```typescript
 * const isLastPage = usePDFViewerStore(selectIsLastPage);
 * <button disabled={isLastPage}>Next</button>
 * ```
 */
export const selectIsLastPage = (state: PDFViewerState): boolean => {
  return state.currentPage === state.totalPages;
};

/**
 * Selector: Get highlight count by page
 * 
 * @example
 * ```typescript
 * const highlightCounts = usePDFViewerStore(selectHighlightCountsByPage);
 * console.log(`Page 1 has ${highlightCounts[1] || 0} highlights`);
 * ```
 */
export const selectHighlightCountsByPage = (state: PDFViewerState): Record<number, number> => {
  return state.highlights.reduce((acc, highlight) => {
    acc[highlight.pageNumber] = (acc[highlight.pageNumber] || 0) + 1;
    return acc;
  }, {} as Record<number, number>);
};

/**
 * Selector: Get zoom percentage
 * 
 * @example
 * ```typescript
 * const zoomPercent = usePDFViewerStore(selectZoomPercentage);
 * console.log(`Zoom: ${zoomPercent}%`);
 * ```
 */
export const selectZoomPercentage = (state: PDFViewerState): number => {
  return Math.round(state.zoom * 100);
};
