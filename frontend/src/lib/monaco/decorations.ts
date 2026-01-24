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
 * 
 * Features:
 * - Batches multiple decoration updates into a single reflow
 * - Debounces updates to reduce frequency (100ms)
 * - Limits concurrent operations to prevent performance issues
 * - Tracks pending updates for efficient batching
 * - Provides immediate and deferred update modes
 * 
 * Requirements: 7.1, 7.2 (Performance and Responsiveness)
 */
export class DecorationManager {
  private editor: Monaco.editor.IStandaloneCodeEditor;
  private decorations: Map<string, string[]> = new Map();
  private pendingUpdates: Map<string, Monaco.editor.IModelDeltaDecoration[]> = new Map();
  private updateTimeout: NodeJS.Timeout | null = null;
  private batchTimeout: NodeJS.Timeout | null = null;
  private isProcessing: boolean = false;
  private concurrentOperations: number = 0;
  
  // Configuration
  private readonly DEBOUNCE_MS = 100;
  private readonly BATCH_DELAY_MS = 16; // ~60fps
  private readonly MAX_CONCURRENT_OPERATIONS = 3;
  private readonly BATCH_SIZE = 5; // Max updates per batch

  constructor(editor: Monaco.editor.IStandaloneCodeEditor) {
    this.editor = editor;
  }

  /**
   * Update decorations with debouncing and batching
   * 
   * This method queues decoration updates and processes them in batches
   * to minimize reflows and improve performance.
   */
  updateDecorations(
    key: string,
    newDecorations: Monaco.editor.IModelDeltaDecoration[]
  ): void {
    // Add to pending updates
    this.pendingUpdates.set(key, newDecorations);

    // Clear existing debounce timeout
    if (this.updateTimeout) {
      clearTimeout(this.updateTimeout);
    }

    // Debounce the batch processing
    this.updateTimeout = setTimeout(() => {
      this.processBatch();
    }, this.DEBOUNCE_MS);
  }

  /**
   * Update decorations immediately without batching
   * 
   * Use this for critical updates that need to be applied immediately,
   * such as user interactions or selection changes.
   */
  updateDecorationsImmediate(
    key: string,
    newDecorations: Monaco.editor.IModelDeltaDecoration[]
  ): void {
    // Cancel any pending batched update for this key
    this.pendingUpdates.delete(key);

    // Apply immediately if not at concurrent limit
    if (this.concurrentOperations < this.MAX_CONCURRENT_OPERATIONS) {
      this.applyDecorations(key, newDecorations);
    } else {
      // Queue for next batch if at limit
      this.pendingUpdates.set(key, newDecorations);
      this.scheduleBatch();
    }
  }

  /**
   * Process pending decoration updates in batches
   * 
   * This method processes multiple decoration updates in a single batch
   * to reduce the number of reflows and improve performance.
   */
  private processBatch(): void {
    if (this.isProcessing || this.pendingUpdates.size === 0) {
      return;
    }

    // Check concurrent operation limit
    if (this.concurrentOperations >= this.MAX_CONCURRENT_OPERATIONS) {
      // Reschedule batch processing
      this.scheduleBatch();
      return;
    }

    this.isProcessing = true;
    this.concurrentOperations++;

    // Get batch of updates (up to BATCH_SIZE)
    const entries = Array.from(this.pendingUpdates.entries()).slice(0, this.BATCH_SIZE);
    
    // Apply all decorations in the batch
    try {
      for (const [key, decorations] of entries) {
        this.applyDecorations(key, decorations);
        this.pendingUpdates.delete(key);
      }

      // Process remaining updates if any
      if (this.pendingUpdates.size > 0) {
        this.scheduleBatch();
      }
    } finally {
      this.concurrentOperations--;
      this.isProcessing = false;
    }
  }

  /**
   * Schedule the next batch processing
   */
  private scheduleBatch(): void {
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
    }

    this.batchTimeout = setTimeout(() => {
      this.processBatch();
    }, this.BATCH_DELAY_MS);
  }

  /**
   * Apply decorations to the editor
   * 
   * This is the core method that actually updates Monaco decorations.
   */
  private applyDecorations(
    key: string,
    newDecorations: Monaco.editor.IModelDeltaDecoration[]
  ): void {
    try {
      const oldDecorations = this.decorations.get(key) || [];
      const ids = this.editor.deltaDecorations(oldDecorations, newDecorations);
      this.decorations.set(key, ids);
    } catch (error) {
      console.error(`Error applying decorations for key "${key}":`, error);
    }
  }

  /**
   * Clear decorations for a specific key
   */
  clearDecorations(key: string): void {
    // Remove from pending updates
    this.pendingUpdates.delete(key);

    // Clear existing decorations
    const oldDecorations = this.decorations.get(key) || [];
    if (oldDecorations.length > 0) {
      this.editor.deltaDecorations(oldDecorations, []);
    }
    this.decorations.delete(key);
  }

  /**
   * Clear all decorations
   */
  clearAll(): void {
    // Clear all pending updates
    this.pendingUpdates.clear();

    // Clear all decorations
    for (const key of this.decorations.keys()) {
      this.clearDecorations(key);
    }
  }

  /**
   * Flush all pending updates immediately
   * 
   * Use this when you need to ensure all decorations are applied
   * before a critical operation (e.g., taking a screenshot, printing).
   */
  flush(): void {
    // Cancel any pending timeouts
    if (this.updateTimeout) {
      clearTimeout(this.updateTimeout);
      this.updateTimeout = null;
    }
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    // Apply all pending updates immediately
    const entries = Array.from(this.pendingUpdates.entries());
    for (const [key, decorations] of entries) {
      this.applyDecorations(key, decorations);
    }
    this.pendingUpdates.clear();
  }

  /**
   * Get statistics about decoration manager state
   * 
   * Useful for debugging and performance monitoring.
   */
  getStats(): {
    activeDecorations: number;
    pendingUpdates: number;
    concurrentOperations: number;
    isProcessing: boolean;
  } {
    return {
      activeDecorations: this.decorations.size,
      pendingUpdates: this.pendingUpdates.size,
      concurrentOperations: this.concurrentOperations,
      isProcessing: this.isProcessing,
    };
  }

  /**
   * Dispose of the decoration manager
   */
  dispose(): void {
    // Clear all timeouts
    if (this.updateTimeout) {
      clearTimeout(this.updateTimeout);
      this.updateTimeout = null;
    }
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    // Clear all decorations
    this.clearAll();

    // Reset state
    this.isProcessing = false;
    this.concurrentOperations = 0;
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
