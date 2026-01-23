/**
 * Monaco Editor decoration utilities
 * 
 * Provides helpers for managing Monaco decorations including
 * semantic chunks, quality badges, annotations, and references.
 */

import type * as Monaco from 'monaco-editor';
import type { SemanticChunk, Annotation, QualityLevel } from '@/features/editor/types';

/**
 * Decoration manager for batching and optimizing decoration updates
 */
export class DecorationManager {
  private editor: Monaco.editor.IStandaloneCodeEditor;
  private decorations: Map<string, string[]> = new Map();
  private updateTimeout: NodeJS.Timeout | null = null;
  private readonly DEBOUNCE_MS = 100;

  constructor(editor: Monaco.editor.IStandaloneCodeEditor) {
    this.editor = editor;
  }

  /**
   * Update decorations with debouncing
   */
  updateDecorations(
    key: string,
    newDecorations: Monaco.editor.IModelDeltaDecoration[]
  ): void {
    if (this.updateTimeout) {
      clearTimeout(this.updateTimeout);
    }

    this.updateTimeout = setTimeout(() => {
      const oldDecorations = this.decorations.get(key) || [];
      const ids = this.editor.deltaDecorations(oldDecorations, newDecorations);
      this.decorations.set(key, ids);
    }, this.DEBOUNCE_MS);
  }

  /**
   * Clear decorations for a specific key
   */
  clearDecorations(key: string): void {
    const oldDecorations = this.decorations.get(key) || [];
    this.editor.deltaDecorations(oldDecorations, []);
    this.decorations.delete(key);
  }

  /**
   * Clear all decorations
   */
  clearAll(): void {
    for (const key of this.decorations.keys()) {
      this.clearDecorations(key);
    }
  }

  /**
   * Dispose of the decoration manager
   */
  dispose(): void {
    if (this.updateTimeout) {
      clearTimeout(this.updateTimeout);
    }
    this.clearAll();
  }
}

/**
 * Create chunk boundary decorations
 */
export function createChunkDecorations(
  chunks: SemanticChunk[],
  selectedChunkId?: string
): Monaco.editor.IModelDeltaDecoration[] {
  return chunks.map((chunk) => {
    const isSelected = chunk.id === selectedChunkId;
    const className = isSelected
      ? 'semantic-chunk-boundary-selected'
      : 'semantic-chunk-boundary';

    return {
      range: {
        startLineNumber: chunk.chunk_metadata.start_line,
        startColumn: 1,
        endLineNumber: chunk.chunk_metadata.end_line,
        endColumn: Number.MAX_VALUE,
      },
      options: {
        isWholeLine: false,
        className,
        glyphMarginClassName: 'chunk-glyph',
        hoverMessage: {
          value: `**Chunk**: ${chunk.chunk_metadata.function_name || chunk.chunk_metadata.class_name || 'Code Block'}`,
        },
      },
    };
  });
}

/**
 * Get quality level from score
 */
export function getQualityLevel(score: number): QualityLevel {
  if (score >= 0.8) return 'high';
  if (score >= 0.6) return 'medium';
  return 'low';
}

/**
 * Create quality badge decorations
 */
export function createQualityDecorations(
  qualityData: { line: number; score: number; dimensions: any }[]
): Monaco.editor.IModelDeltaDecoration[] {
  return qualityData.map((item) => {
    const level = getQualityLevel(item.score);
    const percentage = (item.score * 100).toFixed(0);

    return {
      range: {
        startLineNumber: item.line,
        startColumn: 1,
        endLineNumber: item.line,
        endColumn: 1,
      },
      options: {
        glyphMarginClassName: `quality-badge quality-${level}`,
        glyphMarginHoverMessage: {
          value: [
            `**Quality**: ${percentage}%`,
            `**Accuracy**: ${(item.dimensions.accuracy * 100).toFixed(0)}%`,
            `**Completeness**: ${(item.dimensions.completeness * 100).toFixed(0)}%`,
            `**Consistency**: ${(item.dimensions.consistency * 100).toFixed(0)}%`,
          ].join('\n'),
        },
      },
    };
  });
}

/**
 * Create annotation decorations
 */
export function createAnnotationDecorations(
  annotations: Annotation[],
  content: string
): Monaco.editor.IModelDeltaDecoration[] {
  const decorations: Monaco.editor.IModelDeltaDecoration[] = [];

  // Sort annotations by start offset to handle overlapping properly
  const sortedAnnotations = [...annotations].sort(
    (a, b) => a.start_offset - b.start_offset
  );

  for (const annotation of sortedAnnotations) {
    // Calculate line and column from offset
    const { line, column } = offsetToPosition(content, annotation.start_offset);
    const { line: endLine, column: endColumn } = offsetToPosition(
      content,
      annotation.end_offset
    );

    // Gutter chip decoration
    decorations.push({
      range: {
        startLineNumber: line,
        startColumn: 1,
        endLineNumber: line,
        endColumn: 1,
      },
      options: {
        glyphMarginClassName: `annotation-chip`,
        glyphMarginHoverMessage: {
          value: annotation.note || annotation.highlighted_text,
        },
      },
    });

    // Text highlight decoration with color support
    // Use a lower z-index for overlapping annotations (earlier annotations appear below)
    decorations.push({
      range: {
        startLineNumber: line,
        startColumn: column,
        endLineNumber: endLine,
        endColumn: endColumn,
      },
      options: {
        inlineClassName: `annotation-highlight`,
        inlineClassNameAffectsLetterSpacing: false,
        stickiness: 1, // NeverGrowsWhenTypingAtEdges
      },
    });
  }

  return decorations;
}

/**
 * Create reference decorations
 */
export function createReferenceDecorations(
  references: Array<{ line: number; title: string; type: string }>
): Monaco.editor.IModelDeltaDecoration[] {
  return references.map((ref) => ({
    range: {
      startLineNumber: ref.line,
      startColumn: 1,
      endLineNumber: ref.line,
      endColumn: 1,
    },
    options: {
      glyphMarginClassName: `reference-icon reference-${ref.type}`,
      glyphMarginHoverMessage: {
        value: `**Reference**: ${ref.title}`,
      },
    },
  }));
}

/**
 * Convert character offset to line/column position
 */
export function offsetToPosition(
  content: string,
  offset: number
): { line: number; column: number } {
  const lines = content.substring(0, offset).split('\n');
  return {
    line: lines.length,
    column: lines[lines.length - 1].length + 1,
  };
}

/**
 * Convert line/column position to character offset
 */
export function positionToOffset(
  content: string,
  line: number,
  column: number
): number {
  const lines = content.split('\n');
  let offset = 0;

  for (let i = 0; i < line - 1 && i < lines.length; i++) {
    offset += lines[i].length + 1; // +1 for newline
  }

  offset += Math.min(column - 1, lines[line - 1]?.length || 0);
  return offset;
}
