/**
 * Annotation Gutter Component
 * 
 * Displays annotation chips in the Monaco editor gutter with:
 * - Colored chips for each annotation
 * - Chip stacking for multiple annotations on same line
 * - Hover highlighting for annotated text
 * - Click handling to open annotation details
 * 
 * Requirements: 4.2, 4.3, 4.4, 4.5
 */

import { useEffect, useCallback, useMemo } from 'react';
import type * as Monaco from 'monaco-editor';
import { useAnnotationStore } from '@/stores/annotation';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import type { DecorationManager } from '@/lib/monaco/decorations';
import { createAnnotationDecorations, offsetToPosition } from '@/lib/monaco/decorations';
import type { Annotation } from './types';

// ============================================================================
// Types
// ============================================================================

export interface AnnotationGutterProps {
  editor: Monaco.editor.IStandaloneCodeEditor;
  monaco: typeof Monaco;
  decorationManager: DecorationManager;
  fileContent: string;
  onAnnotationClick?: (annotation: Annotation) => void;
  onAnnotationHover?: (annotation: Annotation | null) => void;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Group annotations by line number for stacking
 */
function groupAnnotationsByLine(
  annotations: Annotation[],
  content: string
): Map<number, Annotation[]> {
  const lineMap = new Map<number, Annotation[]>();

  for (const annotation of annotations) {
    const { line } = offsetToPosition(content, annotation.start_offset);
    const existing = lineMap.get(line) || [];
    lineMap.set(line, [...existing, annotation]);
  }

  return lineMap;
}

/**
 * Create gutter decorations with stacking support
 */
function createGutterDecorations(
  annotations: Annotation[],
  content: string,
  selectedAnnotationId?: string
): Monaco.editor.IModelDeltaDecoration[] {
  const decorations: Monaco.editor.IModelDeltaDecoration[] = [];
  const lineMap = groupAnnotationsByLine(annotations, content);

  // Create decorations for each line with annotations
  for (const [line, lineAnnotations] of lineMap.entries()) {
    // Sort by start offset to maintain consistent order
    const sortedAnnotations = [...lineAnnotations].sort(
      (a, b) => a.start_offset - b.start_offset
    );

    // Create a chip for each annotation on this line
    sortedAnnotations.forEach((annotation, index) => {
      const isSelected = annotation.id === selectedAnnotationId;
      const chipClass = isSelected
        ? 'annotation-chip annotation-chip-selected'
        : 'annotation-chip';

      // Stack chips vertically using CSS custom properties
      decorations.push({
        range: {
          startLineNumber: line,
          startColumn: 1,
          endLineNumber: line,
          endColumn: 1,
        },
        options: {
          glyphMarginClassName: `${chipClass} annotation-chip-stack-${index}`,
          glyphMarginHoverMessage: {
            value: annotation.note || annotation.highlighted_text,
          },
        },
      });
    });
  }

  return decorations;
}

/**
 * Create text highlight decorations
 */
function createHighlightDecorations(
  annotations: Annotation[],
  content: string,
  hoveredAnnotationId?: string
): Monaco.editor.IModelDeltaDecoration[] {
  const decorations: Monaco.editor.IModelDeltaDecoration[] = [];

  for (const annotation of annotations) {
    const { line, column } = offsetToPosition(content, annotation.start_offset);
    const { line: endLine, column: endColumn } = offsetToPosition(
      content,
      annotation.end_offset
    );

    const isHovered = annotation.id === hoveredAnnotationId;
    const highlightClass = isHovered
      ? `annotation-highlight annotation-highlight-hover`
      : `annotation-highlight`;

    decorations.push({
      range: {
        startLineNumber: line,
        startColumn: column,
        endLineNumber: endLine,
        endColumn: endColumn,
      },
      options: {
        inlineClassName: highlightClass,
        inlineClassNameAffectsLetterSpacing: false,
        stickiness: 1, // Monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
      },
    });
  }

  return decorations;
}

// ============================================================================
// Component
// ============================================================================

export function AnnotationGutter({
  editor,
  monaco,
  decorationManager,
  fileContent,
  onAnnotationClick,
  onAnnotationHover,
}: AnnotationGutterProps) {
  // ==========================================================================
  // Store State
  // ==========================================================================

  const { annotations, selectedAnnotation } = useAnnotationStore();
  const { annotations: annotationsVisible } = useEditorPreferencesStore();

  // ==========================================================================
  // Memoized Values
  // ==========================================================================

  const gutterDecorations = useMemo(() => {
    if (!annotationsVisible || annotations.length === 0) {
      return [];
    }
    return createGutterDecorations(
      annotations,
      fileContent,
      selectedAnnotation?.id
    );
  }, [annotations, fileContent, annotationsVisible, selectedAnnotation?.id]);

  const highlightDecorations = useMemo(() => {
    if (!annotationsVisible || annotations.length === 0) {
      return [];
    }
    return createHighlightDecorations(annotations, fileContent);
  }, [annotations, fileContent, annotationsVisible]);

  // ==========================================================================
  // Update Decorations Effect
  // ==========================================================================

  useEffect(() => {
    if (!editor || !decorationManager) return;

    if (annotationsVisible) {
      // Update gutter chips
      decorationManager.updateDecorations('annotation-gutter', gutterDecorations);
      
      // Update text highlights
      decorationManager.updateDecorations('annotation-highlights', highlightDecorations);
    } else {
      // Clear decorations when hidden
      decorationManager.clearDecorations('annotation-gutter');
      decorationManager.clearDecorations('annotation-highlights');
    }
  }, [editor, decorationManager, annotationsVisible, gutterDecorations, highlightDecorations]);

  // ==========================================================================
  // Click Handler
  // ==========================================================================

  const handleGutterClick = useCallback(
    (e: Monaco.editor.IEditorMouseEvent) => {
      if (!annotationsVisible) return;

      // Check if click was in glyph margin
      if (e.target.type !== monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        return;
      }

      const lineNumber = e.target.position?.lineNumber;
      if (!lineNumber) return;

      // Find annotations on this line
      const lineAnnotations = annotations.filter((annotation) => {
        const { line } = offsetToPosition(fileContent, annotation.start_offset);
        return line === lineNumber;
      });

      if (lineAnnotations.length === 0) return;

      // If multiple annotations, select the first one
      // TODO: In future, show a menu to select which annotation
      const annotation = lineAnnotations[0];
      onAnnotationClick?.(annotation);
    },
    [annotations, fileContent, annotationsVisible, monaco, onAnnotationClick]
  );

  // ==========================================================================
  // Hover Handler
  // ==========================================================================

  const handleMouseMove = useCallback(
    (e: Monaco.editor.IEditorMouseEvent) => {
      if (!annotationsVisible) return;

      // Check if hovering over glyph margin
      if (e.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        const lineNumber = e.target.position?.lineNumber;
        if (!lineNumber) {
          onAnnotationHover?.(null);
          return;
        }

        // Find annotations on this line
        const lineAnnotations = annotations.filter((annotation) => {
          const { line } = offsetToPosition(fileContent, annotation.start_offset);
          return line === lineNumber;
        });

        if (lineAnnotations.length > 0) {
          onAnnotationHover?.(lineAnnotations[0]);
          return;
        }
      }

      // Check if hovering over annotated text
      const position = e.target.position;
      if (position) {
        // Convert position to offset
        const lines = fileContent.split('\n');
        let offset = 0;
        for (let i = 0; i < position.lineNumber - 1 && i < lines.length; i++) {
          offset += lines[i].length + 1;
        }
        offset += position.column - 1;

        // Find annotation at this offset
        const hoveredAnnotation = annotations.find(
          (annotation) =>
            offset >= annotation.start_offset && offset <= annotation.end_offset
        );

        if (hoveredAnnotation) {
          onAnnotationHover?.(hoveredAnnotation);
          return;
        }
      }

      onAnnotationHover?.(null);
    },
    [annotations, fileContent, annotationsVisible, monaco, onAnnotationHover]
  );

  // ==========================================================================
  // Event Listeners Effect
  // ==========================================================================

  useEffect(() => {
    if (!editor) return;

    // Add click listener
    const clickDisposable = editor.onMouseDown(handleGutterClick);

    // Add hover listener
    const moveDisposable = editor.onMouseMove(handleMouseMove);

    // Cleanup
    return () => {
      clickDisposable.dispose();
      moveDisposable.dispose();
    };
  }, [editor, handleGutterClick, handleMouseMove]);

  // ==========================================================================
  // Cleanup Effect
  // ==========================================================================

  useEffect(() => {
    return () => {
      if (decorationManager) {
        decorationManager.clearDecorations('annotation-gutter');
        decorationManager.clearDecorations('annotation-highlights');
      }
    };
  }, [decorationManager]);

  // This component doesn't render anything - it manages decorations
  return null;
}
