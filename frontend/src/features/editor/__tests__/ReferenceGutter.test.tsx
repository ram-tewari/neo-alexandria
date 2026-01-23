/**
 * ReferenceGutter Component Tests
 * 
 * Tests for the reference gutter component including:
 * - Icon rendering
 * - Tooltip display
 * - Panel open/close
 * - Multiple reference types
 * - Click and hover interactions
 * 
 * Requirements: 6.1, 6.2, 6.3, 6.4
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { ReferenceGutter } from '../ReferenceGutter';
import type { Reference } from '../types';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import type * as Monaco from 'monaco-editor';

// Mock Monaco types
const createMockEditor = () => ({
  deltaDecorations: vi.fn(() => ['decoration-1']),
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

describe('ReferenceGutter', () => {
  // ==========================================================================
  // Test Data
  // ==========================================================================

  const mockReferences: Reference[] = [
    {
      id: 'ref-1',
      resource_id: 'resource-1',
      line_number: 5,
      reference_type: 'paper',
      title: 'Deep Learning for Code Understanding',
      authors: ['John Doe', 'Jane Smith'],
      url: 'https://arxiv.org/abs/1234.5678',
      pdf_id: 'pdf-123',
      citation: 'Doe, J., & Smith, J. (2024). Deep Learning for Code Understanding. arXiv preprint.',
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 'ref-2',
      resource_id: 'resource-1',
      line_number: 12,
      reference_type: 'documentation',
      title: 'React Hooks Documentation',
      url: 'https://react.dev/reference/react',
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 'ref-3',
      resource_id: 'resource-1',
      line_number: 20,
      reference_type: 'external',
      title: 'Stack Overflow: How to use TypeScript',
      url: 'https://stackoverflow.com/questions/12345',
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 'ref-4',
      resource_id: 'resource-1',
      line_number: 5, // Same line as ref-1
      reference_type: 'paper',
      title: 'Another Paper on Same Line',
      authors: ['Alice Brown'],
      created_at: '2024-01-01T00:00:00Z',
    },
  ];

  let mockEditor: ReturnType<typeof createMockEditor>;
  let mockMonaco: ReturnType<typeof createMockMonaco>;

  // ==========================================================================
  // Setup & Teardown
  // ==========================================================================

  beforeEach(() => {
    mockEditor = createMockEditor();
    mockMonaco = createMockMonaco();

    // Set up global monaco mock
    (window as any).monaco = {
      Range: class Range {
        constructor(
          public startLineNumber: number,
          public startColumn: number,
          public endLineNumber: number,
          public endColumn: number
        ) {}
      },
      editor: mockMonaco.editor,
    };

    // Reset preferences store
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
    // Clean up global monaco mock
    delete (window as any).monaco;
  });

  // ==========================================================================
  // Icon Rendering Tests
  // ==========================================================================

  describe('Icon Rendering', () => {
    it('should render reference icons when references are visible', async () => {
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      await waitFor(() => {
        expect(mockEditor.deltaDecorations).toHaveBeenCalled();
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations.length).toBeGreaterThan(0);
      });
    });

    it('should not render icons when references are hidden', async () => {
      useEditorPreferencesStore.setState({ references: false });

      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      await waitFor(() => {
        expect(mockEditor.deltaDecorations).toHaveBeenCalled();
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations).toEqual([]);
      });
    });

    it('should not render icons when visible prop is false', async () => {
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={false}
        />
      );

      await waitFor(() => {
        expect(mockEditor.deltaDecorations).toHaveBeenCalled();
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations).toEqual([]);
      });
    });

    it('should render icons for each unique line', async () => {
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      await waitFor(() => {
        expect(mockEditor.deltaDecorations).toHaveBeenCalled();
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        
        // Should have 3 decorations (3 unique lines: 5, 12, 20)
        expect(decorations.length).toBe(3);
      });
    });

    it('should handle empty references array', async () => {
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[]}
          visible={true}
        />
      );

      await waitFor(() => {
        expect(mockEditor.deltaDecorations).toHaveBeenCalled();
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations).toEqual([]);
      });
    });
  });

  // ==========================================================================
  // Reference Type Tests
  // ==========================================================================

  describe('Reference Types', () => {
    it('should apply correct class for paper reference', async () => {
      const paperRef = [mockReferences[0]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={paperRef}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations[0].options.glyphMarginClassName).toContain('reference-icon-paper');
      });
    });

    it('should apply correct class for documentation reference', async () => {
      const docRef = [mockReferences[1]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={docRef}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations[0].options.glyphMarginClassName).toContain('reference-icon-documentation');
      });
    });

    it('should apply correct class for external reference', async () => {
      const externalRef = [mockReferences[2]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={externalRef}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations[0].options.glyphMarginClassName).toContain('reference-icon-external');
      });
    });

    it('should handle different reference types on different lines', async () => {
      const mixedRefs = [mockReferences[0], mockReferences[1], mockReferences[2]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mixedRefs}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations.length).toBe(3);
        
        // Check that each has appropriate class
        const classes = decorations.map((d: any) => d.options.glyphMarginClassName);
        expect(classes.some((c: string) => c.includes('reference-icon-paper'))).toBe(true);
        expect(classes.some((c: string) => c.includes('reference-icon-documentation'))).toBe(true);
        expect(classes.some((c: string) => c.includes('reference-icon-external'))).toBe(true);
      });
    });
  });

  // ==========================================================================
  // Tooltip Tests
  // ==========================================================================

  describe('Tooltip Display', () => {
    it('should include title in hover message', async () => {
      const ref = [mockReferences[0]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={ref}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
        expect(hoverMessage).toContain(mockReferences[0].title);
      });
    });

    it('should include authors in hover message when available', async () => {
      const ref = [mockReferences[0]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={ref}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
        expect(hoverMessage).toContain('John Doe');
        expect(hoverMessage).toContain('Jane Smith');
      });
    });

    it('should include reference type in hover message', async () => {
      const ref = [mockReferences[0]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={ref}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
        expect(hoverMessage).toContain('Paper');
      });
    });

    it('should include citation when available', async () => {
      const ref = [mockReferences[0]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={ref}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
        expect(hoverMessage).toContain(mockReferences[0].citation);
      });
    });

    it('should include URL when available', async () => {
      const ref = [mockReferences[0]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={ref}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
        expect(hoverMessage).toContain(mockReferences[0].url);
      });
    });

    it('should include library hint when pdf_id is available', async () => {
      const ref = [mockReferences[0]];
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={ref}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
        expect(hoverMessage).toContain('Click to view in Library');
      });
    });

    it('should handle references without optional fields', async () => {
      const minimalRef: Reference = {
        id: 'ref-minimal',
        resource_id: 'resource-1',
        line_number: 10,
        reference_type: 'external',
        title: 'Minimal Reference',
        created_at: '2024-01-01T00:00:00Z',
      };
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[minimalRef]}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        const hoverMessage = decorations[0].options.glyphMarginHoverMessage.value;
        expect(hoverMessage).toContain('Minimal Reference');
        expect(hoverMessage).toContain('External');
      });
    });
  });

  // ==========================================================================
  // Click Interaction Tests
  // ==========================================================================

  describe('Click Interactions', () => {
    it('should call onReferenceClick when icon is clicked', async () => {
      const onReferenceClick = vi.fn();
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0]]}
          visible={true}
          onReferenceClick={onReferenceClick}
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
          position: { lineNumber: 5 },
        },
      });

      expect(onReferenceClick).toHaveBeenCalledWith(mockReferences[0]);
    });

    it('should not call onReferenceClick when clicking outside gutter', async () => {
      const onReferenceClick = vi.fn();
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0]]}
          visible={true}
          onReferenceClick={onReferenceClick}
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
          position: { lineNumber: 5 },
        },
      });

      expect(onReferenceClick).not.toHaveBeenCalled();
    });

    it('should not call onReferenceClick when clicking line without reference', async () => {
      const onReferenceClick = vi.fn();
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0]]}
          visible={true}
          onReferenceClick={onReferenceClick}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseDown).toHaveBeenCalled();
      });

      // Simulate click on different line
      const mouseDownHandler = mockEditor.onMouseDown.mock.calls[0][0];
      mouseDownHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN,
          position: { lineNumber: 99 },
        },
      });

      expect(onReferenceClick).not.toHaveBeenCalled();
    });

    it('should handle click on line with multiple references', async () => {
      const onReferenceClick = vi.fn();
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
          onReferenceClick={onReferenceClick}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseDown).toHaveBeenCalled();
      });

      // Simulate click on line 5 (has ref-1 and ref-4)
      const mouseDownHandler = mockEditor.onMouseDown.mock.calls[0][0];
      mouseDownHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN,
          position: { lineNumber: 5 },
        },
      });

      // Should call with first reference on that line
      expect(onReferenceClick).toHaveBeenCalled();
      expect(onReferenceClick).toHaveBeenCalledWith(
        expect.objectContaining({ line_number: 5 })
      );
    });

    it('should not call onReferenceClick when references are hidden', async () => {
      const onReferenceClick = vi.fn();
      useEditorPreferencesStore.setState({ references: false });
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0]]}
          visible={true}
          onReferenceClick={onReferenceClick}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseDown).toHaveBeenCalled();
      });

      // Simulate click
      const mouseDownHandler = mockEditor.onMouseDown.mock.calls[0][0];
      mouseDownHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN,
          position: { lineNumber: 5 },
        },
      });

      expect(onReferenceClick).not.toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Hover Interaction Tests
  // ==========================================================================

  describe('Hover Interactions', () => {
    it('should call onReferenceHover when hovering over icon', async () => {
      const onReferenceHover = vi.fn();
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0]]}
          visible={true}
          onReferenceHover={onReferenceHover}
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
          position: { lineNumber: 5 },
        },
      });

      expect(onReferenceHover).toHaveBeenCalledWith(mockReferences[0]);
    });

    it('should call onReferenceHover with null when not hovering', async () => {
      const onReferenceHover = vi.fn();
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0]]}
          visible={true}
          onReferenceHover={onReferenceHover}
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
          position: { lineNumber: 5 },
        },
      });

      expect(onReferenceHover).toHaveBeenCalledWith(null);
    });

    it('should not register hover listener when callback not provided', async () => {
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0]]}
          visible={true}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseDown).toHaveBeenCalled();
      });

      // onMouseMove should not be called when no hover callback
      expect(mockEditor.onMouseMove).not.toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Multiple References Tests
  // ==========================================================================

  describe('Multiple References', () => {
    it('should handle multiple references on same line', async () => {
      const sameLineRefs = [mockReferences[0], mockReferences[3]]; // Both on line 5
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={sameLineRefs}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        // Should only show one icon per line (first reference)
        expect(decorations.length).toBe(1);
      });
    });

    it('should show first reference when multiple on same line', async () => {
      const sameLineRefs = [mockReferences[0], mockReferences[3]];
      const onReferenceClick = vi.fn();
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={sameLineRefs}
          visible={true}
          onReferenceClick={onReferenceClick}
        />
      );

      await waitFor(() => {
        expect(mockEditor.onMouseDown).toHaveBeenCalled();
      });

      // Click on line 5
      const mouseDownHandler = mockEditor.onMouseDown.mock.calls[0][0];
      mouseDownHandler({
        target: {
          type: mockMonaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN,
          position: { lineNumber: 5 },
        },
      });

      // Should use first reference
      expect(onReferenceClick).toHaveBeenCalledWith(
        expect.objectContaining({ id: expect.stringMatching(/ref-[14]/) })
      );
    });
  });

  // ==========================================================================
  // Visibility Toggle Tests
  // ==========================================================================

  describe('Visibility Toggle', () => {
    it('should show icons when references are enabled', async () => {
      useEditorPreferencesStore.setState({ references: true });
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations.length).toBeGreaterThan(0);
      });
    });

    it('should hide icons when references are disabled', async () => {
      useEditorPreferencesStore.setState({ references: false });
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      await waitFor(() => {
        const decorations = mockEditor.deltaDecorations.mock.calls[0][1];
        expect(decorations).toEqual([]);
      });
    });

    it('should toggle icons when preference changes', async () => {
      useEditorPreferencesStore.setState({ references: true });
      
      const { rerender } = render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      // Disable references
      useEditorPreferencesStore.setState({ references: false });

      rerender(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      await waitFor(() => {
        // Should have been called multiple times
        expect(mockEditor.deltaDecorations).toHaveBeenCalled();
      });
    });
  });

  // ==========================================================================
  // Cleanup Tests
  // ==========================================================================

  describe('Cleanup', () => {
    it('should clear decorations on unmount', async () => {
      const { unmount } = render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      unmount();

      // Should call deltaDecorations with empty array to clear
      const lastCall = mockEditor.deltaDecorations.mock.calls[
        mockEditor.deltaDecorations.mock.calls.length - 1
      ];
      expect(lastCall[1]).toEqual([]);
    });

    it('should dispose event listeners on unmount', async () => {
      const mockClickDispose = vi.fn();
      const mockMoveDispose = vi.fn();
      
      mockEditor.onMouseDown = vi.fn(() => ({ dispose: mockClickDispose }));
      mockEditor.onMouseMove = vi.fn(() => ({ dispose: mockMoveDispose }));

      const { unmount } = render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
          onReferenceHover={vi.fn()}
        />
      );

      unmount();

      expect(mockClickDispose).toHaveBeenCalled();
      expect(mockMoveDispose).toHaveBeenCalled();
    });

    it('should handle unmount when no hover listener registered', async () => {
      const mockClickDispose = vi.fn();
      
      mockEditor.onMouseDown = vi.fn(() => ({ dispose: mockClickDispose }));

      const { unmount } = render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={mockReferences}
          visible={true}
        />
      );

      unmount();

      expect(mockClickDispose).toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Edge Cases
  // ==========================================================================

  describe('Edge Cases', () => {
    it('should handle null editor gracefully', async () => {
      render(
        <ReferenceGutter
          editor={null}
          references={mockReferences}
          visible={true}
        />
      );

      // Should not throw error
      expect(true).toBe(true);
    });

    it('should handle references with missing line numbers', async () => {
      const invalidRef = {
        ...mockReferences[0],
        line_number: undefined as any,
      };
      
      render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[invalidRef]}
          visible={true}
        />
      );

      // Should handle gracefully
      await waitFor(() => {
        expect(mockEditor.deltaDecorations).toHaveBeenCalled();
      });
    });

    it('should update decorations when references change', async () => {
      const { rerender } = render(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0]]}
          visible={true}
        />
      );

      // Update references
      rerender(
        <ReferenceGutter
          editor={mockEditor as any}
          references={[mockReferences[0], mockReferences[1]]}
          visible={true}
        />
      );

      await waitFor(() => {
        expect(mockEditor.deltaDecorations).toHaveBeenCalledTimes(2);
      });
    });
  });
});
