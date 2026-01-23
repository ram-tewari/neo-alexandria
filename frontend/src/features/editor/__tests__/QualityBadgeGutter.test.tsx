/**
 * QualityBadgeGutter Component Tests
 * 
 * Tests for quality badge rendering, color coding, tooltips,
 * visibility toggle, and lazy-loading functionality.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { QualityBadgeGutter } from '../QualityBadgeGutter';
import { useQualityStore } from '@/stores/quality';
import type { QualityDetails } from '../types';
import type * as Monaco from 'monaco-editor';

// ============================================================================
// Mock Setup
// ============================================================================

// Mock the quality store
vi.mock('@/stores/quality', () => ({
  useQualityStore: vi.fn(),
}));

// Mock Monaco editor
const createMockEditor = () => {
  const decorations: string[] = [];
  const listeners: Array<(e: any) => void> = [];
  const scrollListeners: Array<() => void> = [];
  
  return {
    deltaDecorations: vi.fn((oldDecorations: string[], newDecorations: any[]) => {
      decorations.length = 0;
      decorations.push(...newDecorations.map((_, i) => `decoration-${i}`));
      return decorations;
    }),
    onMouseDown: vi.fn((callback: (e: any) => void) => {
      listeners.push(callback);
      return { dispose: vi.fn() };
    }),
    onDidScrollChange: vi.fn((callback: () => void) => {
      scrollListeners.push(callback);
      return { dispose: vi.fn() };
    }),
    _triggerMouseDown: (event: any) => {
      listeners.forEach((listener) => listener(event));
    },
    _triggerScroll: () => {
      scrollListeners.forEach((listener) => listener());
    },
  } as unknown as Monaco.editor.IStandaloneCodeEditor;
};

// Mock quality data
const createMockQualityData = (overallScore: number): QualityDetails => ({
  resource_id: 'test-resource-1',
  quality_dimensions: {
    accuracy: 0.85,
    completeness: 0.90,
    consistency: 0.80,
    timeliness: 0.75,
    relevance: 0.88,
  },
  quality_overall: overallScore,
  quality_weights: {
    accuracy: 0.25,
    completeness: 0.25,
    consistency: 0.20,
    timeliness: 0.15,
    relevance: 0.15,
  },
  quality_last_computed: '2024-01-15T10:00:00Z',
  is_quality_outlier: false,
  needs_quality_review: false,
});

// ============================================================================
// Tests
// ============================================================================

describe('QualityBadgeGutter', () => {
  let mockEditor: Monaco.editor.IStandaloneCodeEditor;
  let mockFetchQualityData: ReturnType<typeof vi.fn>;
  let mockGetCachedQuality: ReturnType<typeof vi.fn>;
  
  beforeEach(() => {
    mockEditor = createMockEditor();
    mockFetchQualityData = vi.fn();
    mockGetCachedQuality = vi.fn(() => null);
    
    // Setup quality store mock
    (useQualityStore as any).mockReturnValue({
      fetchQualityData: mockFetchQualityData,
      getCachedQuality: mockGetCachedQuality,
    });
    
    // Mock window.monaco
    (window as any).monaco = {
      Range: class {
        constructor(
          public startLineNumber: number,
          public startColumn: number,
          public endLineNumber: number,
          public endColumn: number
        ) {}
      },
      editor: {
        MouseTargetType: {
          GUTTER_GLYPH_MARGIN: 2,
        },
      },
    };
  });
  
  afterEach(() => {
    vi.clearAllMocks();
    delete (window as any).monaco;
  });
  
  // ==========================================================================
  // Badge Rendering Tests
  // ==========================================================================
  
  describe('Badge Rendering', () => {
    it('should render quality badge when visible and quality data is provided', () => {
      const qualityData = createMockQualityData(0.85);
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      // Verify deltaDecorations was called with badge decoration
      expect(mockEditor.deltaDecorations).toHaveBeenCalled();
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      
      expect(decorations).toHaveLength(1);
      expect(decorations[0].options.glyphMarginClassName).toContain('quality-badge');
    });
    
    it('should not render badges when not visible', () => {
      const qualityData = createMockQualityData(0.85);
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={false}
        />
      );
      
      // Verify decorations were cleared
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      
      expect(decorations).toHaveLength(0);
    });
    
    it('should not render badges when quality data is null', () => {
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={null}
          visible={true}
        />
      );
      
      // Verify decorations were cleared
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      
      expect(decorations).toHaveLength(0);
    });
  });
  
  // ==========================================================================
  // Color Coding Tests
  // ==========================================================================
  
  describe('Color Coding', () => {
    it('should use high quality badge for scores >= 0.8', () => {
      const qualityData = createMockQualityData(0.85);
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      
      expect(decorations[0].options.glyphMarginClassName).toContain('quality-badge-high');
    });
    
    it('should use medium quality badge for scores 0.6 - 0.8', () => {
      const qualityData = createMockQualityData(0.7);
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      
      expect(decorations[0].options.glyphMarginClassName).toContain('quality-badge-medium');
    });
    
    it('should use low quality badge for scores < 0.6', () => {
      const qualityData = createMockQualityData(0.5);
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      
      expect(decorations[0].options.glyphMarginClassName).toContain('quality-badge-low');
    });
  });
  
  // ==========================================================================
  // Tooltip Tests
  // ==========================================================================
  
  describe('Tooltip Display', () => {
    it('should include quality score in hover message', () => {
      const qualityData = createMockQualityData(0.85);
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      
      const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
      expect(hoverMessage).toContain('Quality Score: 85%');
    });
    
    it('should include all quality dimensions in hover message', () => {
      const qualityData = createMockQualityData(0.85);
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      
      const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
      expect(hoverMessage).toContain('Accuracy: 85%');
      expect(hoverMessage).toContain('Completeness: 90%');
      expect(hoverMessage).toContain('Consistency: 80%');
      expect(hoverMessage).toContain('Timeliness: 75%');
      expect(hoverMessage).toContain('Relevance: 88%');
    });
  });
  
  // ==========================================================================
  // Visibility Toggle Tests
  // ==========================================================================
  
  describe('Visibility Toggle', () => {
    it('should clear decorations when visibility is toggled off', () => {
      const qualityData = createMockQualityData(0.85);
      
      const { rerender } = render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      // Verify badges are rendered
      let calls = (mockEditor.deltaDecorations as any).mock.calls;
      let lastCall = calls[calls.length - 1];
      let decorations = lastCall[1];
      expect(decorations).toHaveLength(1);
      
      // Toggle visibility off
      rerender(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={false}
        />
      );
      
      // Verify decorations are cleared
      calls = (mockEditor.deltaDecorations as any).mock.calls;
      lastCall = calls[calls.length - 1];
      decorations = lastCall[1];
      expect(decorations).toHaveLength(0);
    });
    
    it('should restore decorations when visibility is toggled on', () => {
      const qualityData = createMockQualityData(0.85);
      
      const { rerender } = render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={false}
        />
      );
      
      // Toggle visibility on
      rerender(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      // Verify badges are rendered
      const calls = (mockEditor.deltaDecorations as any).mock.calls;
      const lastCall = calls[calls.length - 1];
      const decorations = lastCall[1];
      expect(decorations).toHaveLength(1);
    });
  });
  
  // ==========================================================================
  // Lazy-Loading Tests
  // ==========================================================================
  
  describe('Lazy-Loading', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });
    
    afterEach(() => {
      vi.useRealTimers();
    });
    
    it('should fetch quality data when resourceId is provided', () => {
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={null}
          visible={true}
          resourceId="test-resource-1"
        />
      );
      
      // Fast-forward debounce timer
      vi.advanceTimersByTime(300);
      
      expect(mockFetchQualityData).toHaveBeenCalledWith('test-resource-1');
    });
    
    it('should debounce quality data requests', () => {
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={null}
          visible={true}
          resourceId="test-resource-1"
        />
      );
      
      // Trigger multiple scroll events
      (mockEditor as any)._triggerScroll();
      (mockEditor as any)._triggerScroll();
      (mockEditor as any)._triggerScroll();
      
      // Fast-forward debounce timer
      vi.advanceTimersByTime(300);
      
      // Should only fetch once due to debouncing
      expect(mockFetchQualityData).toHaveBeenCalledTimes(1);
    });
    
    it('should not fetch if cached data exists', () => {
      mockGetCachedQuality.mockReturnValue(createMockQualityData(0.85));
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={null}
          visible={true}
          resourceId="test-resource-1"
        />
      );
      
      // Fast-forward debounce timer
      vi.advanceTimersByTime(300);
      
      expect(mockFetchQualityData).not.toHaveBeenCalled();
    });
    
    it('should fetch quality data on scroll', () => {
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={null}
          visible={true}
          resourceId="test-resource-1"
        />
      );
      
      // Clear initial fetch
      mockFetchQualityData.mockClear();
      
      // Trigger scroll event
      (mockEditor as any)._triggerScroll();
      
      // Fast-forward debounce timer
      vi.advanceTimersByTime(300);
      
      expect(mockFetchQualityData).toHaveBeenCalled();
    });
  });
  
  // ==========================================================================
  // Badge Click Tests
  // ==========================================================================
  
  describe('Badge Click Handling', () => {
    it('should call onBadgeClick when badge is clicked', () => {
      const qualityData = createMockQualityData(0.85);
      const onBadgeClick = vi.fn();
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
          onBadgeClick={onBadgeClick}
        />
      );
      
      // Simulate click on glyph margin at line 1
      (mockEditor as any)._triggerMouseDown({
        target: {
          type: 2, // GUTTER_GLYPH_MARGIN
          position: { lineNumber: 1 },
        },
      });
      
      expect(onBadgeClick).toHaveBeenCalledWith(1);
    });
    
    it('should not call onBadgeClick for clicks outside glyph margin', () => {
      const qualityData = createMockQualityData(0.85);
      const onBadgeClick = vi.fn();
      
      render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
          onBadgeClick={onBadgeClick}
        />
      );
      
      // Simulate click outside glyph margin
      (mockEditor as any)._triggerMouseDown({
        target: {
          type: 1, // Not GUTTER_GLYPH_MARGIN
          position: { lineNumber: 1 },
        },
      });
      
      expect(onBadgeClick).not.toHaveBeenCalled();
    });
  });
  
  // ==========================================================================
  // Cleanup Tests
  // ==========================================================================
  
  describe('Cleanup', () => {
    it('should clear decorations on unmount', () => {
      const qualityData = createMockQualityData(0.85);
      
      const { unmount } = render(
        <QualityBadgeGutter
          editor={mockEditor}
          qualityData={qualityData}
          visible={true}
        />
      );
      
      // Clear mock calls
      (mockEditor.deltaDecorations as any).mockClear();
      
      // Unmount component
      unmount();
      
      // Verify decorations were cleared
      expect(mockEditor.deltaDecorations).toHaveBeenCalledWith(
        expect.any(Array),
        []
      );
    });
  });
});

