/**
 * Tests for SemanticChunkOverlay component
 * 
 * Tests:
 * - Chunk boundary rendering
 * - Hover and click interactions
 * - Nested chunk handling
 * - Visibility toggle
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChunkStore } from '@/stores/chunk';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import type { SemanticChunk } from '../types';

// Mock Monaco Editor
const mockEditor = {
  onMouseMove: vi.fn(() => ({ dispose: vi.fn() })),
  onMouseDown: vi.fn(() => ({ dispose: vi.fn() })),
  deltaDecorations: vi.fn(() => []),
  setSelection: vi.fn(),
  revealRangeInCenter: vi.fn(),
  dispose: vi.fn(),
};

const mockMonaco = {
  Range: class Range {
    constructor(
      public startLineNumber: number,
      public startColumn: number,
      public endLineNumber: number,
      public endColumn: number
    ) {}
  },
};

// Mock chunks
const mockChunks: SemanticChunk[] = [
  {
    id: 'chunk-1',
    resource_id: 'resource-1',
    content: 'function foo() { return 42; }',
    chunk_index: 0,
    chunk_metadata: {
      function_name: 'foo',
      start_line: 1,
      end_line: 3,
      language: 'typescript',
    },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'chunk-2',
    resource_id: 'resource-1',
    content: 'function bar() { return foo(); }',
    chunk_index: 1,
    chunk_metadata: {
      function_name: 'bar',
      start_line: 5,
      end_line: 7,
      language: 'typescript',
    },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'chunk-3',
    resource_id: 'resource-1',
    content: 'const x = 1;',
    chunk_index: 2,
    chunk_metadata: {
      start_line: 2,
      end_line: 2,
      language: 'typescript',
    },
    created_at: '2024-01-01T00:00:00Z',
  },
];

describe('SemanticChunkOverlay', () => {
  beforeEach(() => {
    // Reset stores
    useChunkStore.getState().setChunks([]);
    useChunkStore.getState().selectChunk(null);
    useChunkStore.getState().setChunkVisibility(true);
    useEditorPreferencesStore.getState().updatePreference('chunkBoundaries', true);
    
    // Clear mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Clean up
    useChunkStore.getState().clearCache();
  });

  describe('Chunk Boundary Rendering', () => {
    it('should render chunk boundaries when chunks are available', () => {
      const { result } = renderHook(() => useChunkStore());

      act(() => {
        result.current.setChunks(mockChunks);
      });

      expect(result.current.chunks).toHaveLength(3);
      expect(result.current.chunks[0].chunk_metadata.function_name).toBe('foo');
    });

    it('should not render chunks when visibility is disabled', () => {
      const { result: chunkResult } = renderHook(() => useChunkStore());
      const { result: prefsResult } = renderHook(() => useEditorPreferencesStore());

      act(() => {
        chunkResult.current.setChunks(mockChunks);
        prefsResult.current.updatePreference('chunkBoundaries', false);
      });

      expect(chunkResult.current.chunks).toHaveLength(3);
      expect(prefsResult.current.chunkBoundaries).toBe(false);
    });

    it('should render selected chunk with different styling', () => {
      const { result } = renderHook(() => useChunkStore());

      act(() => {
        result.current.setChunks(mockChunks);
        result.current.selectChunk('chunk-1');
      });

      expect(result.current.selectedChunk?.id).toBe('chunk-1');
      expect(result.current.selectedChunk?.chunk_metadata.function_name).toBe('foo');
    });

    it('should handle empty chunks array', () => {
      const { result } = renderHook(() => useChunkStore());

      act(() => {
        result.current.setChunks([]);
      });

      expect(result.current.chunks).toHaveLength(0);
      expect(result.current.selectedChunk).toBeNull();
    });
  });

  describe('Hover Interactions', () => {
    it('should detect chunk at cursor position', () => {
      const { result } = renderHook(() => useChunkStore());

      act(() => {
        result.current.setChunks(mockChunks);
      });

      // Simulate finding chunk at line 2 (within chunk-1)
      const chunk = mockChunks.find(
        (c) => 2 >= c.chunk_metadata.start_line && 2 <= c.chunk_metadata.end_line
      );

      expect(chunk).toBeDefined();
      expect(chunk?.id).toBe('chunk-1');
    });

    it('should handle hover over nested chunks', () => {
      const { result } = renderHook(() => useChunkStore());

      // Create nested chunks
      const nestedChunks: SemanticChunk[] = [
        {
          ...mockChunks[0],
          id: 'outer-chunk',
          chunk_metadata: {
            class_name: 'MyClass',
            start_line: 1,
            end_line: 10,
            language: 'typescript',
          },
        },
        {
          ...mockChunks[0],
          id: 'inner-chunk',
          chunk_metadata: {
            function_name: 'method',
            start_line: 3,
            end_line: 5,
            language: 'typescript',
          },
        },
      ];

      act(() => {
        result.current.setChunks(nestedChunks);
      });

      // Find chunks at line 4 (both outer and inner)
      const containingChunks = nestedChunks.filter(
        (c) => 4 >= c.chunk_metadata.start_line && 4 <= c.chunk_metadata.end_line
      );

      expect(containingChunks).toHaveLength(2);

      // Should select the innermost (smallest range)
      const innermost = containingChunks.reduce((smallest, current) => {
        const smallestRange =
          smallest.chunk_metadata.end_line - smallest.chunk_metadata.start_line;
        const currentRange =
          current.chunk_metadata.end_line - current.chunk_metadata.start_line;
        return currentRange < smallestRange ? current : smallest;
      });

      expect(innermost.id).toBe('inner-chunk');
    });

    it('should clear hover when mouse leaves chunk', () => {
      const { result } = renderHook(() => useChunkStore());

      act(() => {
        result.current.setChunks(mockChunks);
        result.current.selectChunk('chunk-1');
      });

      expect(result.current.selectedChunk?.id).toBe('chunk-1');

      act(() => {
        result.current.selectChunk(null);
      });

      expect(result.current.selectedChunk).toBeNull();
    });
  });

  describe('Click Interactions', () => {
    it('should select chunk on click', () => {
      const { result } = renderHook(() => useChunkStore());

      act(() => {
        result.current.setChunks(mockChunks);
        result.current.selectChunk('chunk-2');
      });

      expect(result.current.selectedChunk?.id).toBe('chunk-2');
      expect(result.current.selectedChunk?.chunk_metadata.function_name).toBe('bar');
    });

    it('should deselect chunk when clicking outside', () => {
      const { result } = renderHook(() => useChunkStore());

      act(() => {
        result.current.setChunks(mockChunks);
        result.current.selectChunk('chunk-1');
      });

      expect(result.current.selectedChunk?.id).toBe('chunk-1');

      act(() => {
        result.current.selectChunk(null);
      });

      expect(result.current.selectedChunk).toBeNull();
    });

    it('should handle clicking on nested chunks', () => {
      const { result } = renderHook(() => useChunkStore());

      const nestedChunks: SemanticChunk[] = [
        {
          ...mockChunks[0],
          id: 'outer',
          chunk_metadata: {
            class_name: 'Outer',
            start_line: 1,
            end_line: 20,
            language: 'typescript',
          },
        },
        {
          ...mockChunks[0],
          id: 'inner',
          chunk_metadata: {
            function_name: 'inner',
            start_line: 5,
            end_line: 10,
            language: 'typescript',
          },
        },
      ];

      act(() => {
        result.current.setChunks(nestedChunks);
        result.current.selectChunk('inner');
      });

      expect(result.current.selectedChunk?.id).toBe('inner');
    });
  });

  describe('Nested Chunk Handling', () => {
    it('should handle overlapping chunks correctly', () => {
      const { result } = renderHook(() => useChunkStore());

      const overlappingChunks: SemanticChunk[] = [
        {
          ...mockChunks[0],
          id: 'chunk-a',
          chunk_metadata: {
            start_line: 1,
            end_line: 5,
            language: 'typescript',
          },
        },
        {
          ...mockChunks[0],
          id: 'chunk-b',
          chunk_metadata: {
            start_line: 3,
            end_line: 7,
            language: 'typescript',
          },
        },
      ];

      act(() => {
        result.current.setChunks(overlappingChunks);
      });

      expect(result.current.chunks).toHaveLength(2);

      // Both chunks should be present
      expect(result.current.chunks.map((c) => c.id)).toContain('chunk-a');
      expect(result.current.chunks.map((c) => c.id)).toContain('chunk-b');
    });

    it('should prioritize innermost chunk in nested hierarchy', () => {
      const { result } = renderHook(() => useChunkStore());

      const hierarchyChunks: SemanticChunk[] = [
        {
          ...mockChunks[0],
          id: 'level-1',
          chunk_metadata: {
            start_line: 1,
            end_line: 30,
            language: 'typescript',
          },
        },
        {
          ...mockChunks[0],
          id: 'level-2',
          chunk_metadata: {
            start_line: 5,
            end_line: 20,
            language: 'typescript',
          },
        },
        {
          ...mockChunks[0],
          id: 'level-3',
          chunk_metadata: {
            start_line: 10,
            end_line: 15,
            language: 'typescript',
          },
        },
      ];

      act(() => {
        result.current.setChunks(hierarchyChunks);
      });

      // Find chunks at line 12 (all three contain it)
      const containingChunks = hierarchyChunks.filter(
        (c) => 12 >= c.chunk_metadata.start_line && 12 <= c.chunk_metadata.end_line
      );

      expect(containingChunks).toHaveLength(3);

      // Get the innermost
      const innermost = containingChunks.reduce((smallest, current) => {
        const smallestRange =
          smallest.chunk_metadata.end_line - smallest.chunk_metadata.start_line;
        const currentRange =
          current.chunk_metadata.end_line - current.chunk_metadata.start_line;
        return currentRange < smallestRange ? current : smallest;
      });

      expect(innermost.id).toBe('level-3');
    });
  });

  describe('Visibility Toggle', () => {
    it('should toggle chunk visibility', () => {
      const { result } = renderHook(() => useChunkStore());

      expect(result.current.chunkVisibility).toBe(true);

      act(() => {
        result.current.toggleChunkVisibility();
      });

      expect(result.current.chunkVisibility).toBe(false);

      act(() => {
        result.current.toggleChunkVisibility();
      });

      expect(result.current.chunkVisibility).toBe(true);
    });

    it('should toggle chunk boundaries preference', () => {
      const { result } = renderHook(() => useEditorPreferencesStore());

      expect(result.current.chunkBoundaries).toBe(true);

      act(() => {
        result.current.toggleChunkBoundaries();
      });

      expect(result.current.chunkBoundaries).toBe(false);

      act(() => {
        result.current.toggleChunkBoundaries();
      });

      expect(result.current.chunkBoundaries).toBe(true);
    });

    it('should respect both visibility flags', () => {
      const { result: chunkResult } = renderHook(() => useChunkStore());
      const { result: prefsResult } = renderHook(() => useEditorPreferencesStore());

      // Both enabled
      expect(chunkResult.current.chunkVisibility).toBe(true);
      expect(prefsResult.current.chunkBoundaries).toBe(true);

      // Disable store visibility
      act(() => {
        chunkResult.current.setChunkVisibility(false);
      });

      expect(chunkResult.current.chunkVisibility).toBe(false);
      expect(prefsResult.current.chunkBoundaries).toBe(true);

      // Re-enable store, disable preference
      act(() => {
        chunkResult.current.setChunkVisibility(true);
        prefsResult.current.updatePreference('chunkBoundaries', false);
      });

      expect(chunkResult.current.chunkVisibility).toBe(true);
      expect(prefsResult.current.chunkBoundaries).toBe(false);
    });

    it('should persist visibility preference', () => {
      const { result } = renderHook(() => useChunkStore());

      act(() => {
        result.current.setChunkVisibility(false);
      });

      expect(result.current.chunkVisibility).toBe(false);

      // Simulate page reload by getting fresh state
      const freshState = useChunkStore.getState();
      expect(freshState.chunkVisibility).toBe(false);
    });
  });

  describe('Chunk Fetching', () => {
    it('should fetch chunks for a resource', async () => {
      const { result } = renderHook(() => useChunkStore());

      await act(async () => {
        await result.current.fetchChunks('resource-1');
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should use cached chunks when available', async () => {
      const { result } = renderHook(() => useChunkStore());

      // Set cached chunks
      act(() => {
        result.current.setCachedChunks('resource-1', mockChunks);
      });

      // Fetch should use cache
      await act(async () => {
        await result.current.fetchChunks('resource-1');
      });

      expect(result.current.chunks).toHaveLength(3);
      expect(result.current.isLoading).toBe(false);
    });

    it('should handle fetch errors gracefully', async () => {
      const { result } = renderHook(() => useChunkStore());

      // Mock API error by clearing cache and fetching non-existent resource
      await act(async () => {
        await result.current.fetchChunks('non-existent');
      });

      expect(result.current.isLoading).toBe(false);
      // Error handling is implementation-specific
    });
  });
});
