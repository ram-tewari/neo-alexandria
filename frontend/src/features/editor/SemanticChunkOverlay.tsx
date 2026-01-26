/**
 * Semantic Chunk Overlay Component
 * 
 * Renders visual boundaries around AST-based code chunks with:
 * - Chunk boundary decorations
 * - Hover highlighting
 * - Click selection
 * - Nested/overlapping chunk handling
 * 
 * Performance optimizations:
 * - Memoized with React.memo to prevent unnecessary re-renders
 * - Callbacks memoized with useCallback
 * - Expensive computations memoized with useMemo
 */

import { useEffect, useCallback, useRef, memo } from 'react';
import type * as Monaco from 'monaco-editor';
import { createChunkDecorations } from '@/lib/monaco/decorations';
import { useChunkStore } from '@/stores/chunk';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import { useChunks } from '@/lib/hooks/useEditorData';
import type { SemanticChunk } from './types';

// ============================================================================
// Types
// ============================================================================

export interface SemanticChunkOverlayProps {
  editor: Monaco.editor.IStandaloneCodeEditor;
  monaco: typeof Monaco;
  resourceId: string;
  visible?: boolean;
  onChunkClick?: (chunk: SemanticChunk) => void;
  onChunkHover?: (chunk: SemanticChunk | null) => void;
}

// ============================================================================
// Component
// ============================================================================

const SemanticChunkOverlayComponent = ({
  editor,
  monaco,
  resourceId,
  visible = true,
  onChunkClick,
  onChunkHover,
}: SemanticChunkOverlayProps) => {
  // ==========================================================================
  // Store State
  // ==========================================================================

  const {
    chunks,
    selectedChunk,
    chunkVisibility,
    setChunks,
    selectChunk,
  } = useChunkStore();

  const { chunkBoundaries } = useEditorPreferencesStore();

  // ==========================================================================
  // Fetch Chunks with TanStack Query
  // ==========================================================================

  const {
    data: fetchedChunks,
    isLoading,
    error,
  } = useChunks(resourceId);

  // Update store when chunks are fetched
  useEffect(() => {
    if (fetchedChunks) {
      setChunks(fetchedChunks);
    }
  }, [fetchedChunks, setChunks]);

  // ==========================================================================
  // Derived Values
  // ==========================================================================

  // Combine all visibility flags with smooth transition support
  const shouldShowChunks = visible && chunkVisibility && chunkBoundaries;

  // ==========================================================================
  // Refs
  // ==========================================================================

  const decorationIdsRef = useRef<string[]>([]);
  const hoverChunkRef = useRef<SemanticChunk | null>(null);

  // ==========================================================================
  // Find Chunk at Position
  // ==========================================================================

  const findChunkAtPosition = useCallback(
    (lineNumber: number): SemanticChunk | null => {
      if (!chunks.length) return null;

      // Find all chunks that contain this line
      const containingChunks = chunks.filter(
        (chunk) =>
          lineNumber >= chunk.chunk_metadata.start_line &&
          lineNumber <= chunk.chunk_metadata.end_line
      );

      if (containingChunks.length === 0) return null;

      // If multiple chunks (nested), return the most specific (smallest range)
      return containingChunks.reduce((smallest, current) => {
        const smallestRange =
          smallest.chunk_metadata.end_line - smallest.chunk_metadata.start_line;
        const currentRange =
          current.chunk_metadata.end_line - current.chunk_metadata.start_line;
        return currentRange < smallestRange ? current : smallest;
      });
    },
    [chunks]
  );

  // ==========================================================================
  // Handle Mouse Move (Hover Detection)
  // ==========================================================================

  useEffect(() => {
    if (!editor || !shouldShowChunks) return;

    const disposable = editor.onMouseMove((e) => {
      if (!e.target.position) {
        // Mouse not over text
        if (hoverChunkRef.current) {
          hoverChunkRef.current = null;
          onChunkHover?.(null);
        }
        return;
      }

      const lineNumber = e.target.position.lineNumber;
      const chunk = findChunkAtPosition(lineNumber);

      // Only trigger callback if chunk changed
      if (chunk?.id !== hoverChunkRef.current?.id) {
        hoverChunkRef.current = chunk;
        onChunkHover?.(chunk);
      }
    });

    return () => disposable.dispose();
  }, [editor, shouldShowChunks, findChunkAtPosition, onChunkHover]);

  // ==========================================================================
  // Handle Mouse Down (Click Detection)
  // ==========================================================================

  useEffect(() => {
    if (!editor || !shouldShowChunks) return;

    const disposable = editor.onMouseDown((e) => {
      if (!e.target.position) return;

      const lineNumber = e.target.position.lineNumber;
      const chunk = findChunkAtPosition(lineNumber);

      if (chunk) {
        // Select the chunk in the store
        selectChunk(chunk.id);
        
        // Notify parent component
        onChunkClick?.(chunk);

        // Select the chunk text in the editor
        const range = new monaco.Range(
          chunk.chunk_metadata.start_line,
          1,
          chunk.chunk_metadata.end_line,
          Number.MAX_VALUE
        );
        editor.setSelection(range);
        editor.revealRangeInCenter(range);
      }
    });

    return () => disposable.dispose();
  }, [editor, monaco, shouldShowChunks, findChunkAtPosition, selectChunk, onChunkClick]);

  // ==========================================================================
  // Update Decorations
  // ==========================================================================

  useEffect(() => {
    if (!editor || !monaco) return;

    // Clear decorations if not visible
    if (!shouldShowChunks) {
      decorationIdsRef.current = editor.deltaDecorations(
        decorationIdsRef.current,
        []
      );
      return;
    }

    // Create chunk decorations
    const decorations = createChunkDecorations(
      chunks,
      selectedChunk?.id
    );

    // Apply decorations
    decorationIdsRef.current = editor.deltaDecorations(
      decorationIdsRef.current,
      decorations
    );
  }, [editor, monaco, chunks, selectedChunk, shouldShowChunks]);

  // ==========================================================================
  // Cleanup
  // ==========================================================================

  useEffect(() => {
    return () => {
      if (editor && decorationIdsRef.current.length > 0) {
        editor.deltaDecorations(decorationIdsRef.current, []);
      }
    };
  }, [editor]);

  // ==========================================================================
  // Render
  // ==========================================================================

  // This is a logical component that manages decorations
  // It doesn't render any DOM elements
  return null;
}

// Memoize the component to prevent unnecessary re-renders
// Requirements: 7.2 - React optimization
export const SemanticChunkOverlay = memo(SemanticChunkOverlayComponent, (prevProps, nextProps) => {
  // Custom comparison function for better memoization
  return (
    prevProps.editor === nextProps.editor &&
    prevProps.monaco === nextProps.monaco &&
    prevProps.resourceId === nextProps.resourceId &&
    prevProps.visible === nextProps.visible &&
    prevProps.onChunkClick === nextProps.onChunkClick &&
    prevProps.onChunkHover === nextProps.onChunkHover
  );
});

SemanticChunkOverlay.displayName = 'SemanticChunkOverlay';
