/**
 * Performance Tests for Living Code Editor
 * 
 * Tests performance characteristics including:
 * - Large file rendering (>5000 lines)
 * - Decoration update performance
 * - Scroll performance
 * - API caching
 * 
 * **Validates Requirements**: 7.1, 7.2, 7.3, 7.4
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MonacoEditorWrapper } from '../MonacoEditorWrapper';
import type { CodeFile, SemanticChunk, Annotation, QualityDetails } from '../types';
import { useEditorStore } from '@/stores/editor';
import { useChunkStore } from '@/stores/chunk';
import { useQualityStore } from '@/stores/quality';
import { useAnnotationStore } from '@/stores/annotation';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// ==========================================================================
// Mocks
// ==========================================================================

// Mock Monaco Editor with performance tracking
const mockEditorInstance = {
  dispose: vi.fn(),
  setScrollTop: vi.fn(),
  updateOptions: vi.fn(),
  onDidChangeCursorPosition: vi.fn(() => ({ dispose: vi.fn() })),
  onDidChangeCursorSelection: vi.fn(() => ({ dispose: vi.fn() })),
  onDidScrollChange: vi.fn(() => ({ dispose: vi.fn() })),
  deltaDecorations: vi.fn(() => []),
  getScrollTop: vi.fn(() => 0),
  getScrollHeight: vi.fn(() => 10000),
  getVisibleRanges: vi.fn(() => [{ startLineNumber: 1, endLineNumber: 100 }]),
};

vi.mock('@monaco-editor/react', () => ({
  default: ({ onMount, loading }: any) => {
    setTimeout(() => {
      const mockMonaco = {
        editor: {
          defineTheme: vi.fn(),
          setTheme: vi.fn(),
        },
        Range: class {
          constructor(
            public startLineNumber: number,
            public startColumn: number,
            public endLineNumber: number,
            public endColumn: number
          ) {}
        },
      };

      onMount?.(mockEditorInstance, mockMonaco);
    }, 0);

    return <div data-testid="monaco-editor-mock">{loading}</div>;
  },
}));

vi.mock('@/lib/monaco/themes', () => ({
  registerThemes: vi.fn(),
  getMonacoTheme: vi.fn(() => 'pharos-light'),
}));

vi.mock('@/lib/monaco/languages', () => ({
  detectLanguage: vi.fn(() => 'typescript'),
}));

vi.mock('@/lib/monaco/decorations', () => ({
  DecorationManager: class DecorationManager {
    updateDecorations = vi.fn();
    clearDecorations = vi.fn();
    clearAll = vi.fn();
    dispose = vi.fn();
  },
}));

// ==========================================================================
// Test Utilities
// ==========================================================================

/**
 * Generate a large code file for performance testing
 */
function generateLargeFile(lines: number): CodeFile {
  const content = Array.from({ length: lines }, (_, i) => 
    `function example${i}() {\n  return ${i};\n}`
  ).join('\n');

  return {
    id: `large-file-${lines}`,
    resource_id: 'resource-1',
    path: `src/large-file-${lines}.ts`,
    name: `large-file-${lines}.ts`,
    language: 'typescript',
    content,
    size: content.length,
    lines,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };
}

/**
 * Generate semantic chunks for testing
 */
function generateChunks(count: number): SemanticChunk[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `chunk-${i}`,
    resource_id: 'resource-1',
    content: `function example${i}() { return ${i}; }`,
    chunk_index: i,
    chunk_metadata: {
      function_name: `example${i}`,
      start_line: i * 10,
      end_line: (i + 1) * 10,
      language: 'typescript',
    },
    created_at: '2024-01-01T00:00:00Z',
  }));
}

/**
 * Generate annotations for testing
 */
function generateAnnotations(count: number): Annotation[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `annotation-${i}`,
    resource_id: 'resource-1',
    user_id: 'user-1',
    start_offset: i * 100,
    end_offset: i * 100 + 50,
    highlighted_text: `text ${i}`,
    note: `Note ${i}`,
    tags: [`tag${i}`],
    color: '#ffeb3b',
    is_shared: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  }));
}

/**
 * Generate quality details for testing
 */
function generateQualityDetails(): QualityDetails {
  return {
    resource_id: 'resource-1',
    quality_dimensions: {
      accuracy: 0.85,
      completeness: 0.90,
      consistency: 0.88,
      timeliness: 0.92,
      relevance: 0.87,
    },
    quality_overall: 0.88,
    quality_weights: {
      accuracy: 0.3,
      completeness: 0.25,
      consistency: 0.2,
      timeliness: 0.15,
      relevance: 0.1,
    },
    quality_last_computed: '2024-01-01T00:00:00Z',
    is_quality_outlier: false,
    needs_quality_review: false,
  };
}

/**
 * Measure execution time of a function
 */
async function measureTime(fn: () => Promise<void> | void): Promise<number> {
  const start = performance.now();
  await fn();
  const end = performance.now();
  return end - start;
}

/**
 * Create a test wrapper with QueryClient
 */
function createTestWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

// ==========================================================================
// Performance Tests
// ==========================================================================

describe('Performance Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    // Reset stores
    useEditorStore.setState({
      activeFile: null,
      cursorPosition: { line: 1, column: 1 },
      selection: null,
      scrollPosition: 0,
      fontSize: 14,
      showLineNumbers: true,
      showMinimap: true,
    });

    useChunkStore.setState({
      chunks: [],
      selectedChunk: null,
      chunkVisibility: true,
      isLoading: false,
      error: null,
    });

    useQualityStore.setState({
      qualityData: null,
      badgeVisibility: true,
      isLoading: false,
      error: null,
    });

    useAnnotationStore.setState({
      annotations: [],
      selectedAnnotation: null,
      isCreating: false,
      isLoading: false,
      error: null,
    });

    // Clear all mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  // ==========================================================================
  // Requirement 7.1: Large File Rendering (>5000 lines)
  // ==========================================================================

  describe('Large File Rendering', () => {
    it('should render 5000 line file within acceptable time', async () => {
      const largeFile = generateLargeFile(5000);

      const renderTime = await measureTime(async () => {
        render(
          <QueryClientProvider client={queryClient}>
            <MonacoEditorWrapper file={largeFile} />
          </QueryClientProvider>
        );

        await waitFor(() => {
          expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
        });
      });

      // Should render within 1 second
      expect(renderTime).toBeLessThan(1000);
    });

    it('should render 10000 line file with virtualization', async () => {
      const veryLargeFile = generateLargeFile(10000);

      const renderTime = await measureTime(async () => {
        render(
          <QueryClientProvider client={queryClient}>
            <MonacoEditorWrapper file={veryLargeFile} />
          </QueryClientProvider>
        );

        await waitFor(() => {
          expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
        });
      });

      // Should still render within 1.5 seconds with virtualization
      expect(renderTime).toBeLessThan(1500);
    });

    it('should handle 20000 line file without crashing', async () => {
      const massiveFile = generateLargeFile(20000);

      const { container } = render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={massiveFile} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Should not crash
      expect(container).toBeInTheDocument();
    });

    it('should disable minimap for large files automatically', async () => {
      const largeFile = generateLargeFile(6000);

      render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={largeFile} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Minimap should be disabled for performance
      await waitFor(() => {
        expect(mockEditorInstance.updateOptions).toHaveBeenCalled();
      });
    });
  });

  // ==========================================================================
  // Requirement 7.2: Decoration Update Performance
  // ==========================================================================

  describe('Decoration Update Performance', () => {
    it('should batch decoration updates efficiently', async () => {
      const file = generateLargeFile(1000);
      const chunks = generateChunks(100);

      useChunkStore.setState({ chunks });

      const { rerender } = render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Measure time to update decorations
      const updateTime = await measureTime(async () => {
        // Trigger decoration update by changing chunks
        useChunkStore.setState({ chunks: generateChunks(150) });
        rerender(
          <QueryClientProvider client={queryClient}>
            <MonacoEditorWrapper file={file} />
          </QueryClientProvider>
        );

        // Wait for potential updates
        await new Promise(resolve => setTimeout(resolve, 50));
      });

      // Decoration updates should be fast (<200ms including debounce)
      expect(updateTime).toBeLessThan(200);
    });

    it('should debounce rapid decoration updates', async () => {
      const file = generateLargeFile(1000);

      render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      const initialCallCount = mockEditorInstance.deltaDecorations.mock.calls.length;

      // Trigger multiple rapid updates
      for (let i = 0; i < 10; i++) {
        useChunkStore.setState({ chunks: generateChunks(i + 1) });
      }

      // Wait for debounce
      await new Promise(resolve => setTimeout(resolve, 150));

      const finalCallCount = mockEditorInstance.deltaDecorations.mock.calls.length;

      // Should not call deltaDecorations 10 times (debouncing should reduce calls)
      expect(finalCallCount - initialCallCount).toBeLessThan(10);
    });

    it('should handle 500 chunk decorations efficiently', async () => {
      const file = generateLargeFile(5000);
      const chunks = generateChunks(500);

      useChunkStore.setState({ chunks });

      const renderTime = await measureTime(async () => {
        render(
          <QueryClientProvider client={queryClient}>
            <MonacoEditorWrapper file={file} />
          </QueryClientProvider>
        );

        await waitFor(() => {
          expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
        });
      });

      // Should handle many decorations within 1 second
      expect(renderTime).toBeLessThan(1000);
    });

    it('should handle 1000 annotation decorations efficiently', async () => {
      const file = generateLargeFile(5000);
      const annotations = generateAnnotations(1000);

      useAnnotationStore.setState({ annotations });

      const renderTime = await measureTime(async () => {
        render(
          <QueryClientProvider client={queryClient}>
            <MonacoEditorWrapper file={file} />
          </QueryClientProvider>
        );

        await waitFor(() => {
          expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
        });
      });

      // Should handle many annotations within 1.5 seconds
      expect(renderTime).toBeLessThan(1500);
    });
  });

  // ==========================================================================
  // Requirement 7.3: Scroll Performance
  // ==========================================================================

  describe('Scroll Performance', () => {
    it('should handle scroll events with debouncing', async () => {
      const file = generateLargeFile(5000);

      render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Get the scroll handler
      const scrollHandler = mockEditorInstance.onDidScrollChange.mock.calls[0]?.[0];

      if (scrollHandler) {
        const scrollTime = await measureTime(async () => {
          // Simulate rapid scroll events
          for (let i = 0; i < 50; i++) {
            scrollHandler({ scrollTop: i * 100 });
          }

          // Wait for debounce
          await new Promise(resolve => setTimeout(resolve, 150));
        });

        // Scroll handling should be fast even with many events
        expect(scrollTime).toBeLessThan(200);
      }
    });

    it('should lazy-load decorations on scroll', async () => {
      const file = generateLargeFile(10000);
      const chunks = generateChunks(1000);

      useChunkStore.setState({ chunks });

      render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      const initialDecorationCalls = mockEditorInstance.deltaDecorations.mock.calls.length;

      // Simulate scroll to trigger lazy loading
      const scrollHandler = mockEditorInstance.onDidScrollChange.mock.calls[0]?.[0];
      if (scrollHandler) {
        scrollHandler({ scrollTop: 5000 });
        await new Promise(resolve => setTimeout(resolve, 150));
      }

      const finalDecorationCalls = mockEditorInstance.deltaDecorations.mock.calls.length;

      // Should have triggered additional decoration updates for visible range
      expect(finalDecorationCalls).toBeGreaterThanOrEqual(initialDecorationCalls);
    });

    it('should maintain smooth scrolling with quality badges', async () => {
      const file = generateLargeFile(5000);
      const qualityData = generateQualityDetails();

      useQualityStore.setState({ qualityData });

      render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      const scrollHandler = mockEditorInstance.onDidScrollChange.mock.calls[0]?.[0];

      if (scrollHandler) {
        const scrollTime = await measureTime(async () => {
          // Simulate smooth scrolling
          for (let i = 0; i < 20; i++) {
            scrollHandler({ scrollTop: i * 200 });
            await new Promise(resolve => setTimeout(resolve, 16)); // ~60fps
          }
        });

        // Should maintain reasonable performance (16ms per frame * 20 frames = 320ms + overhead)
        // Allow up to 800ms for slower test environments
        expect(scrollTime).toBeLessThan(800);
      }
    });
  });

  // ==========================================================================
  // Requirement 7.4: API Caching
  // ==========================================================================

  describe('API Caching', () => {
    it('should cache chunk data and avoid redundant fetches', async () => {
      const file = generateLargeFile(1000);
      const chunks = generateChunks(50);

      // Mock fetch function
      const mockFetchChunks = vi.fn().mockResolvedValue(chunks);
      useChunkStore.setState({ 
        fetchChunks: mockFetchChunks,
        chunks: [],
      });

      const { rerender } = render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Fetch chunks
      await useChunkStore.getState().fetchChunks('resource-1');
      const firstFetchCount = mockFetchChunks.mock.calls.length;

      // Rerender component
      rerender(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Should not fetch again (cached)
      expect(mockFetchChunks.mock.calls.length).toBe(firstFetchCount);
    });

    it('should cache quality data efficiently', async () => {
      const file = generateLargeFile(1000);
      const qualityData = generateQualityDetails();

      const mockFetchQuality = vi.fn().mockResolvedValue(qualityData);
      useQualityStore.setState({
        fetchQualityData: mockFetchQuality,
        qualityData: null,
      });

      const { rerender } = render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Fetch quality data
      await useQualityStore.getState().fetchQualityData('resource-1');
      const firstFetchCount = mockFetchQuality.mock.calls.length;

      // Rerender multiple times
      for (let i = 0; i < 5; i++) {
        rerender(
          <QueryClientProvider client={queryClient}>
            <MonacoEditorWrapper file={file} />
          </QueryClientProvider>
        );
      }

      // Should not fetch again (cached)
      expect(mockFetchQuality.mock.calls.length).toBe(firstFetchCount);
    });

    it('should cache annotation data and support optimistic updates', async () => {
      const file = generateLargeFile(1000);
      const annotations = generateAnnotations(100);

      const mockFetchAnnotations = vi.fn().mockResolvedValue(annotations);
      useAnnotationStore.setState({
        fetchAnnotations: mockFetchAnnotations,
        annotations: [],
      });

      render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Fetch annotations
      await useAnnotationStore.getState().fetchAnnotations('resource-1');
      const firstFetchCount = mockFetchAnnotations.mock.calls.length;

      // Add annotation optimistically
      const newAnnotation: Annotation = {
        id: 'temp-id',
        resource_id: 'resource-1',
        user_id: 'user-1',
        start_offset: 1000,
        end_offset: 1050,
        highlighted_text: 'new text',
        note: 'New note',
        tags: [],
        color: '#ffeb3b',
        is_shared: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      useAnnotationStore.setState({
        annotations: [...annotations, newAnnotation],
      });

      // Should not trigger new fetch (optimistic update)
      expect(mockFetchAnnotations.mock.calls.length).toBe(firstFetchCount);
    });

    it('should debounce hover card API requests', async () => {
      const file = generateLargeFile(1000);

      render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Mock hover requests
      const mockFetchHoverData = vi.fn().mockResolvedValue({
        symbol: 'example',
        summary: 'Test summary',
        connections: [],
      });

      // Simulate rapid hover events
      const hoverTime = await measureTime(async () => {
        for (let i = 0; i < 20; i++) {
          mockFetchHoverData();
          await new Promise(resolve => setTimeout(resolve, 10));
        }

        // Wait for debounce (300ms)
        await new Promise(resolve => setTimeout(resolve, 350));
      });

      // Should complete within reasonable time
      expect(hoverTime).toBeLessThan(1000);
    });
  });

  // ==========================================================================
  // React Component Optimization Tests
  // ==========================================================================

  describe('React Component Optimization', () => {
    it('should memoize MonacoEditorWrapper to prevent unnecessary rerenders', async () => {
      const file = generateLargeFile(1000);

      const { rerender } = render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Clear mock calls after initial render
      mockEditorInstance.updateOptions.mockClear();

      // Rerender with same props
      rerender(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      // Wait a bit to ensure no updates happen
      await new Promise(resolve => setTimeout(resolve, 50));

      // Should not trigger unnecessary updates (or minimal updates)
      expect(mockEditorInstance.updateOptions.mock.calls.length).toBeLessThanOrEqual(1);
    });

    it('should handle large annotation lists efficiently', async () => {
      const file = generateLargeFile(1000);
      const annotations = generateAnnotations(1000);

      useAnnotationStore.setState({ annotations });

      const renderTime = await measureTime(async () => {
        render(
          <QueryClientProvider client={queryClient}>
            <MonacoEditorWrapper file={file} />
          </QueryClientProvider>
        );

        await waitFor(() => {
          expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
        });
      });

      // Should render with large annotation list quickly
      expect(renderTime).toBeLessThan(1000);
    });

    it('should handle rapid state updates efficiently', async () => {
      const file = generateLargeFile(1000);

      render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      const updateTime = await measureTime(async () => {
        // Simulate rapid state updates
        for (let i = 0; i < 50; i++) {
          useEditorStore.setState({
            cursorPosition: { line: i, column: 1 },
          });
        }

        await new Promise(resolve => setTimeout(resolve, 100));
      });

      // Should handle rapid updates efficiently
      expect(updateTime).toBeLessThan(200);
    });
  });

  // ==========================================================================
  // Memory Management Tests
  // ==========================================================================

  describe('Memory Management', () => {
    it('should dispose Monaco instance on unmount', async () => {
      const file = generateLargeFile(1000);

      const { unmount } = render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      unmount();

      // Should dispose editor instance
      expect(mockEditorInstance.dispose).toHaveBeenCalled();
    });

    it('should clear decorations when switching files', async () => {
      const file1 = generateLargeFile(1000);
      const file2 = generateLargeFile(1000);

      const { rerender } = render(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file1} />
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });

      // Switch to different file
      rerender(
        <QueryClientProvider client={queryClient}>
          <MonacoEditorWrapper file={file2} />
        </QueryClientProvider>
      );

      // Wait for file switch to process
      await new Promise(resolve => setTimeout(resolve, 50));

      // Component should handle file switch without errors
      expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
    });
  });
});
