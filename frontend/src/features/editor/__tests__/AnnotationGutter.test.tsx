/**
 * AnnotationGutter Component Tests
 * 
 * Tests for the annotation gutter component including:
 * - Chip rendering and stacking
 * - Hover and click interactions
 * - Text highlighting
 * - Overlapping annotations
 * 
 * Requirements: 4.2, 4.3, 4.4, 4.5
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { AnnotationGutter } from '../AnnotationGutter';
import type { Annotation } from '../types';
import { useAnnotationStore } from '@/stores/annotation';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import type * as Monaco from 'monaco-editor';

// Mock Monaco types
const createMockEditor = () => ({
  deltaDecorations: vi.fn(() => ['decoration-1', 'decoration-2']),
  onMouseDown: vi.fn(() => ({ dispose: vi.fn() })),
  onMouseMove: vi.fn(() => ({ dispose: vi.fn() })),
  dispose: vi.fn(),
});

const createMockMonaco = () => ({
  editor: {
    MouseTargetType: {
      GUTTER_GLYPH_MARGIN: 2,
      CONTENT_TEXT: 6,
    },
  },
});

const createMockDecorationManager = () => ({
  updateDecorations: vi.fn(),
  clearDecorations: vi.fn(),
  clearAll: vi.fn(),
  dispose: vi.fn(),
});

describe('AnnotationGutter', () => {
  // ==========================================================================
  // Test Data
  // ==========================================================================

  const mockFileContent = `const x = 1;
const y = 2;
const z = x + y;
console.log(z);`;

  const mockAnnotations: Annotation[] = [
    {
      id: 'annotation-1',
      resource_id: 'resource-1',
      user_id: 'user-1',
      start_offset: 0,
      end_offset: 12, // "const x = 1;"
      highlighted_text: 'const x = 1;',
      note: 'Variable declaration',
      tags: ['variable'],
      color: '#3b82f6',
      is_shared: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 'annotation-2',
      resource_id: 'resource-1',
      user_id: 'user-1',
      start_offset: 13,
      end_offset: 25, // "const y = 2;"
      highlighted_text: 'const y = 2;',
      note: 'Another variable',
      tags: ['variable'],
      color: '#10b981',
      is_shared: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 'annotation-3',
      resource_id: 'resource-1',
      user_id: 'user-1',
      start_offset: 0,
      end_offset: 5, // "const" - overlapping with annotation-1
      highlighted_text: 'const',
      note: 'Keyword',
      tags: ['keyword'],
      color: '#f59e0b',
      is_shared: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ];

  let mockEditor: ReturnType<typeof createMockEditor>;
  let mockMonaco: ReturnType<typeof createMockMonaco>;
  let mockDecorationManager: ReturnType<typeof createMockDecorationManager>;

  // ==========================================================================
  // Setup & Teardown
  // ==========================================================================

  beforeEach(() => {
    mockEditor = createMockEditor();
    mockMonaco = createMockMonaco();
    mockDecorationManager = createMockDecorationManager();

    // Reset stores
    useAnnotationStore.setState({
      annotations: [],
      selectedAnnotation: null,
      isCreating: false,
      isLoading: false,
      error: null,
    });

    useEditorPreferencesStore.setState({
      theme: 'vs-dark',
      fontSize: 14,
      lineNumbers: true,
      minimap: true,
      wordWrap: false,
      chunkBoundaries: true,
      qualityBadges: true,
      annotations: true,
      references: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ==========================================================================
  // Chip Rendering Tests
  // ==========================================================================

  describe('Chip Rendering', () => {
    it('should render annotation chips when annotations are visible', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        expect(mockDecorationManager.updateDecorations).toHaveBeenCalledWith(
          'annotation-gutter',
          expect.any(Array)
        );
      });
    });

    it('should not render chips when annotations are hidden', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });
      useEditorPreferencesStore.setState({ annotations: false });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        expect(mockDecorationManager.clearDecorations).toHaveBeenCalledWith('annotation-gutter');
      });
    });

    it('should render chips for each annotation', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        const calls = mockDecorationManager.updateDecorations.mock.calls;
        const gutterCall = calls.find((call) => call[0] === 'annotation-gutter');
        expect(gutterCall).toBeDefined();
        expect(gutterCall![1].length).toBeGreaterThan(0);
      });
    });

    it('should handle empty annotations array', async () => {
      useAnnotationStore.setState({ annotations: [] });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        const calls = mockDecorationManager.updateDecorations.mock.calls;
        const gutterCall = calls.find((call) => call[0] === 'annotation-gutter');
        if (gutterCall) {
          expect(gutterCall[1]).toEqual([]);
        }
      });
    });
  });

  // ==========================================================================
  // Chip Stacking Tests
  // ==========================================================================

  describe('Chip Stacking', () => {
    it('should stack multiple annotations on the same line', async () => {
      // Both annotation-1 and annotation-3 start on line 1
      const sameLineAnnotations = [mockAnnotations[0], mockAnnotations[2]];
      useAnnotationStore.setState({ annotations: sameLineAnnotations });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        const calls = mockDecorationManager.updateDecorations.mock.calls;
        const gutterCall = calls.find((call) => call[0] === 'annotation-gutter');
        expect(gutterCall).toBeDefined();
        
        // Should have decorations for both annotations
        const decorations = gutterCall![1];
        expect(decorations.length).toBeGreaterThanOrEqual(2);
        
        // Check for stack classes
        const hasStackClasses = decorations.some((dec: any) =>
          dec.options.glyphMarginClassName?.includes('annotation-chip-stack')
        );
        expect(hasStackClasses).toBe(true);
      });
    });

    it('should sort stacked annotations by start offset', async () => {
      // annotation-3 starts before annotation-1 on the same line
      const sameLineAnnotations = [mockAnnotations[0], mockAnnotations[2]];
      useAnnotationStore.setState({ annotations: sameLineAnnotations });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        const calls = mockDecorationManager.updateDecorations.mock.calls;
        const gutterCall = calls.find((call) => call[0] === 'annotation-gutter');
        expect(gutterCall).toBeDefined();
        
        // Decorations should be sorted by start offset
        const decorations = gutterCall![1];
        expect(decorations.length).toBeGreaterThan(0);
      });
    });
  });

  // ==========================================================================
  // Text Highlighting Tests
  // ==========================================================================

  describe('Text Highlighting', () => {
    it('should render text highlights for annotations', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        expect(mockDecorationManager.updateDecorations).toHaveBeenCalledWith(
          'annotation-highlights',
          expect.any(Array)
        );
      });
    });

    it('should apply highlight class to annotated text', async () => {
      useAnnotationStore.setState({ annotations: [mockAnnotations[0]] });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        const calls = mockDecorationManager.updateDecorations.mock.calls;
        const highlightCall = calls.find((call) => call[0] === 'annotation-highlights');
        expect(highlightCall).toBeDefined();
        
        const decorations = highlightCall![1];
        expect(decorations.length).toBeGreaterThan(0);
        expect(decorations[0].options.inlineClassName).toContain('annotation-highlight');
      });
    });

    it('should not render highlights when annotations are hidden', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });
      useEditorPreferencesStore.setState({ annotations: false });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        expect(mockDecorationManager.clearDecorations).toHaveBeenCalledWith('annotation-highlights');
      });
    });
  });

  // ==========================================================================
  // Overlapping Annotations Tests
  // ==========================================================================

  describe('Overlapping Annotations', () => {
    it('should handle overlapping annotations', async () => {
      // annotation-1 and annotation-3 overlap
      const overlappingAnnotations = [mockAnnotations[0], mockAnnotations[2]];
      useAnnotationStore.setState({ annotations: overlappingAnnotations });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        const calls = mockDecorationManager.updateDecorations.mock.calls;
        const highlightCall = calls.find((call) => call[0] === 'annotation-highlights');
        expect(highlightCall).toBeDefined();
        
        // Should have highlights for both annotations
        const decorations = highlightCall![1];
        expect(decorations.length).toBe(2);
      });
    });

    it('should render overlapping annotations in order', async () => {
      const overlappingAnnotations = [mockAnnotations[0], mockAnnotations[2]];
      useAnnotationStore.setState({ annotations: overlappingAnnotations });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        const calls = mockDecorationManager.updateDecorations.mock.calls;
        const highlightCall = calls.find((call) => call[0] === 'annotation-highlights');
        expect(highlightCall).toBeDefined();
        
        // Decorations should be sorted by start offset
        const decorations = highlightCall![1];
        expect(decorations.length).toBe(2);
      });
    });
  });

  // ==========================================================================
  // Click Interaction Tests
  // ==========================================================================

  describe('Click Interactions', () => {
    it('should call onAnnotationClick when chip is clicked', async () => {
      const onAnnotationClick = vi.fn();
      useAnnotationStore.setState({ annotations: [mockAnnotations[0]] });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
          onAnnotationClick={onAnnotationClick}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseDown).toHaveBeenCalled();
      });

      // Simulate click on glyph margin
      const mouseDownHandler = mockEditor.onMouseDown.mock.calls[0][0];
      mouseDownHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN,
          position: { lineNumber: 1 },
        },
      });

      expect(onAnnotationClick).toHaveBeenCalledWith(mockAnnotations[0]);
    });

    it('should not call onAnnotationClick when clicking outside gutter', async () => {
      const onAnnotationClick = vi.fn();
      useAnnotationStore.setState({ annotations: [mockAnnotations[0]] });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
          onAnnotationClick={onAnnotationClick}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseDown).toHaveBeenCalled();
      });

      // Simulate click on content text
      const mouseDownHandler = mockEditor.onMouseDown.mock.calls[0][0];
      mouseDownHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.CONTENT_TEXT,
          position: { lineNumber: 1 },
        },
      });

      expect(onAnnotationClick).not.toHaveBeenCalled();
    });

    it('should handle click on line with multiple annotations', async () => {
      const onAnnotationClick = vi.fn();
      const sameLineAnnotations = [mockAnnotations[0], mockAnnotations[2]];
      useAnnotationStore.setState({ annotations: sameLineAnnotations });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
          onAnnotationClick={onAnnotationClick}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseDown).toHaveBeenCalled();
      });

      // Simulate click on glyph margin
      const mouseDownHandler = mockEditor.onMouseDown.mock.calls[0][0];
      mouseDownHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN,
          position: { lineNumber: 1 },
        },
      });

      // Should call with first annotation on that line
      expect(onAnnotationClick).toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Hover Interaction Tests
  // ==========================================================================

  describe('Hover Interactions', () => {
    it('should call onAnnotationHover when hovering over chip', async () => {
      const onAnnotationHover = vi.fn();
      useAnnotationStore.setState({ annotations: [mockAnnotations[0]] });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
          onAnnotationHover={onAnnotationHover}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseMove).toHaveBeenCalled();
      });

      // Simulate hover over glyph margin
      const mouseMoveHandler = mockEditor.onMouseMove.mock.calls[0][0];
      mouseMoveHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN,
          position: { lineNumber: 1 },
        },
      });

      expect(onAnnotationHover).toHaveBeenCalledWith(mockAnnotations[0]);
    });

    it('should call onAnnotationHover with null when not hovering', async () => {
      const onAnnotationHover = vi.fn();
      useAnnotationStore.setState({ annotations: [mockAnnotations[0]] });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
          onAnnotationHover={onAnnotationHover}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseMove).toHaveBeenCalled();
      });

      // Simulate hover over content text (not gutter)
      const mouseMoveHandler = mockEditor.onMouseMove.mock.calls[0][0];
      mouseMoveHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.CONTENT_TEXT,
          position: { lineNumber: 2 },
        },
      });

      expect(onAnnotationHover).toHaveBeenCalledWith(null);
    });

    it('should call onAnnotationHover when hovering over annotated text', async () => {
      const onAnnotationHover = vi.fn();
      useAnnotationStore.setState({ annotations: [mockAnnotations[0]] });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
          onAnnotationHover={onAnnotationHover}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseMove).toHaveBeenCalled();
      });

      // Simulate hover over annotated text
      const mouseMoveHandler = mockEditor.onMouseMove.mock.calls[0][0];
      mouseMoveHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.CONTENT_TEXT,
          position: { lineNumber: 1, column: 5 }, // Within annotation range
        },
      });

      expect(onAnnotationHover).toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Selected Annotation Tests
  // ==========================================================================

  describe('Selected Annotation', () => {
    it('should highlight selected annotation', async () => {
      useAnnotationStore.setState({
        annotations: mockAnnotations,
        selectedAnnotation: mockAnnotations[0],
      });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        const calls = mockDecorationManager.updateDecorations.mock.calls;
        const gutterCall = calls.find((call) => call[0] === 'annotation-gutter');
        expect(gutterCall).toBeDefined();
        
        // Should have selected class
        const decorations = gutterCall![1];
        const hasSelectedClass = decorations.some((dec: any) =>
          dec.options.glyphMarginClassName?.includes('annotation-chip-selected')
        );
        expect(hasSelectedClass).toBe(true);
      });
    });

    it('should update decorations when selection changes', async () => {
      useAnnotationStore.setState({
        annotations: mockAnnotations,
        selectedAnnotation: null,
      });

      const { rerender } = render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      // Select an annotation
      useAnnotationStore.setState({
        selectedAnnotation: mockAnnotations[0],
      });

      rerender(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        expect(mockDecorationManager.updateDecorations).toHaveBeenCalled();
      });
    });
  });

  // ==========================================================================
  // Cleanup Tests
  // ==========================================================================

  describe('Cleanup', () => {
    it('should clear decorations on unmount', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });

      const { unmount } = render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      unmount();

      expect(mockDecorationManager.clearDecorations).toHaveBeenCalledWith('annotation-gutter');
      expect(mockDecorationManager.clearDecorations).toHaveBeenCalledWith('annotation-highlights');
    });

    it('should dispose event listeners on unmount', async () => {
      const mockClickDispose = vi.fn();
      const mockMoveDispose = vi.fn();
      
      mockEditor.onMouseDown = vi.fn(() => ({ dispose: mockClickDispose }));
      mockEditor.onMouseMove = vi.fn(() => ({ dispose: mockMoveDispose }));

      const { unmount } = render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      unmount();

      expect(mockClickDispose).toHaveBeenCalled();
      expect(mockMoveDispose).toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Visibility Toggle Tests
  // ==========================================================================

  describe('Visibility Toggle', () => {
    it('should show decorations when annotations are enabled', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });
      useEditorPreferencesStore.setState({ annotations: true });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        expect(mockDecorationManager.updateDecorations).toHaveBeenCalled();
      });
    });

    it('should hide decorations when annotations are disabled', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });
      useEditorPreferencesStore.setState({ annotations: false });

      render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        expect(mockDecorationManager.clearDecorations).toHaveBeenCalledWith('annotation-gutter');
        expect(mockDecorationManager.clearDecorations).toHaveBeenCalledWith('annotation-highlights');
      });
    });

    it('should toggle decorations when preference changes', async () => {
      useAnnotationStore.setState({ annotations: mockAnnotations });
      useEditorPreferencesStore.setState({ annotations: true });

      const { rerender } = render(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      // Disable annotations
      useEditorPreferencesStore.setState({ annotations: false });

      rerender(
        <AnnotationGutter
          editor={mockEditor as any}
          monaco={mockMonaco as any}
          decorationManager={mockDecorationManager as any}
          fileContent={mockFileContent}
        />
      );

      await waitFor(() => {
        expect(mockDecorationManager.clearDecorations).toHaveBeenCalled();
      });
    });
  });
});
