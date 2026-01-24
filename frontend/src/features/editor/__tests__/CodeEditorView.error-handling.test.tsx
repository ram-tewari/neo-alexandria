/**
 * CodeEditorView Error Handling Integration Tests
 * 
 * Tests that error banners are properly displayed and functional when:
 * - Annotation API fails (shows cached data banner)
 * - Chunk API fails (shows line-based fallback banner)
 * - Quality API fails (shows badge hidden banner)
 * - Retry functionality works correctly
 * - Error dismissal works correctly
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CodeEditorView } from '../CodeEditorView';
import { useAnnotationStore } from '@/stores/annotation';
import { useChunkStore } from '@/stores/chunk';
import { useQualityStore } from '@/stores/quality';
import { editorApi } from '@/lib/api/editor';
import type { CodeFile } from '../types';

// Mock the API client
vi.mock('@/lib/api/editor', () => ({
  editorApi: {
    getAnnotations: vi.fn(),
    getChunks: vi.fn(),
    getQualityDetails: vi.fn(),
  },
}));

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ onMount }: any) => {
    // Simulate editor mount
    setTimeout(() => {
      const mockEditor = {
        onDidChangeCursorPosition: vi.fn(() => ({ dispose: vi.fn() })),
        onDidChangeCursorSelection: vi.fn(() => ({ dispose: vi.fn() })),
        onDidScrollChange: vi.fn(() => ({ dispose: vi.fn() })),
        onMouseDown: vi.fn(() => ({ dispose: vi.fn() })),
        deltaDecorations: vi.fn(() => []),
        setScrollTop: vi.fn(),
        updateOptions: vi.fn(),
        dispose: vi.fn(),
      };
      const mockMonaco = {
        editor: {
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
      onMount?.(mockEditor, mockMonaco);
    }, 0);
    return <div data-testid="monaco-editor">Monaco Editor</div>;
  },
}));

// Mock other editor components
vi.mock('../SemanticChunkOverlay', () => ({
  SemanticChunkOverlay: () => <div data-testid="chunk-overlay">Chunk Overlay</div>,
}));

vi.mock('../QualityBadgeGutter', () => ({
  QualityBadgeGutter: () => <div data-testid="quality-gutter">Quality Gutter</div>,
}));

vi.mock('../AnnotationGutter', () => ({
  AnnotationGutter: () => <div data-testid="annotation-gutter">Annotation Gutter</div>,
}));

vi.mock('../HoverCardProvider', () => ({
  HoverCardProvider: () => <div data-testid="hover-provider">Hover Provider</div>,
}));

vi.mock('../AnnotationPanel', () => ({
  AnnotationPanel: () => <div data-testid="annotation-panel">Annotation Panel</div>,
}));

vi.mock('../ChunkMetadataPanel', () => ({
  ChunkMetadataPanel: () => <div data-testid="chunk-panel">Chunk Panel</div>,
}));

describe('CodeEditorView Error Handling Integration', () => {
  const mockFile: CodeFile = {
    id: 'file-1',
    resource_id: 'resource-1',
    path: 'src/test.ts',
    name: 'test.ts',
    language: 'typescript',
    content: 'const x = 1;\nconst y = 2;\nconst z = 3;',
    size: 100,
    lines: 3,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    // Reset all stores
    useAnnotationStore.setState({
      annotations: [],
      selectedAnnotation: null,
      annotationCache: {},
      isCreating: false,
      isLoading: false,
      error: null,
      usingCachedData: false,
    });

    useChunkStore.setState({
      chunks: [],
      selectedChunk: null,
      chunkCache: {},
      chunkVisibility: true,
      isLoading: false,
      error: null,
      usingFallback: false,
    });

    useQualityStore.setState({
      qualityData: null,
      qualityCache: {},
      badgeVisibility: true,
      isLoading: false,
      error: null,
      hideBadgesDueToError: false,
    });

    // Clear all mocks
    vi.clearAllMocks();
  });

  describe('Annotation Error Handling', () => {
    it('should display cached data warning banner when annotation API fails', async () => {
      // Set up cached annotations
      const cachedAnnotations = [
        {
          id: 'ann-1',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'cached',
          color: '#3b82f6',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];
      useAnnotationStore.getState().setCachedAnnotations('resource-1', cachedAnnotations);

      // Mock API failure
      vi.mocked(editorApi.getAnnotations).mockRejectedValue(
        new Error('Network error')
      );
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: {} } as any);

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner to appear
      await waitFor(() => {
        expect(screen.getByText(/Using Cached Annotations/i)).toBeInTheDocument();
      });

      // Check that warning variant is used
      expect(screen.getByText(/cached data/i)).toBeInTheDocument();

      // Check that retry button is present
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('should display error banner when annotation API fails with no cache', async () => {
      // Mock API failure
      vi.mocked(editorApi.getAnnotations).mockRejectedValue(
        new Error('Network error')
      );
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: {} } as any);

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner to appear
      await waitFor(() => {
        expect(screen.getByText(/Annotation Error/i)).toBeInTheDocument();
      });

      // Check that error message is displayed
      expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    });

    it('should retry annotation fetch when retry button is clicked', async () => {
      const user = userEvent.setup();

      // First call fails
      vi.mocked(editorApi.getAnnotations)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ data: [] } as any);
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: {} } as any);

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner
      await waitFor(() => {
        expect(screen.getByText(/Annotation Error/i)).toBeInTheDocument();
      });

      // Click retry button
      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);

      // Wait for error to clear
      await waitFor(() => {
        expect(screen.queryByText(/Annotation Error/i)).not.toBeInTheDocument();
      });
    });

    it('should dismiss annotation error when dismiss button is clicked', async () => {
      const user = userEvent.setup();

      // Mock API failure
      vi.mocked(editorApi.getAnnotations).mockRejectedValue(
        new Error('Network error')
      );
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: {} } as any);

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner
      await waitFor(() => {
        expect(screen.getByText(/Annotation Error/i)).toBeInTheDocument();
      });

      // Click dismiss button
      const dismissButton = screen.getByRole('button', { name: /dismiss/i });
      await user.click(dismissButton);

      // Wait for error to be dismissed
      await waitFor(() => {
        expect(screen.queryByText(/Annotation Error/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Chunk Error Handling', () => {
    it('should display line-based fallback banner when chunk API fails', async () => {
      // Mock API failure
      vi.mocked(editorApi.getAnnotations).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getChunks).mockRejectedValue(
        new Error('Chunking failed')
      );
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: {} } as any);

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner to appear
      await waitFor(() => {
        expect(screen.getByText(/Using Line-Based Display/i)).toBeInTheDocument();
      });

      // Check that fallback message is displayed
      expect(screen.getByText(/line-based display/i)).toBeInTheDocument();
    });

    it('should display error banner when chunk API fails with no fallback', async () => {
      // Create file without content (no fallback possible)
      const fileWithoutContent: CodeFile = {
        ...mockFile,
        content: '',
      };

      // Mock API failure
      vi.mocked(editorApi.getAnnotations).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getChunks).mockRejectedValue(
        new Error('Chunking failed')
      );
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: {} } as any);

      render(<CodeEditorView file={fileWithoutContent} />);

      // Wait for error banner to appear
      await waitFor(() => {
        expect(screen.getByText(/Chunk Error/i)).toBeInTheDocument();
      });
    });

    it('should retry chunk fetch when retry button is clicked', async () => {
      const user = userEvent.setup();

      // First call fails, second succeeds
      vi.mocked(editorApi.getAnnotations).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getChunks)
        .mockRejectedValueOnce(new Error('Chunking failed'))
        .mockResolvedValueOnce({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: {} } as any);

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner
      await waitFor(() => {
        expect(screen.getByText(/Using Line-Based Display/i)).toBeInTheDocument();
      });

      // Click retry button
      const retryButtons = screen.getAllByRole('button', { name: /retry/i });
      await user.click(retryButtons[0]); // First retry button (chunks)

      // Wait for error to clear
      await waitFor(() => {
        expect(screen.queryByText(/Using Line-Based Display/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Quality Error Handling', () => {
    it('should display badge hidden banner when quality API fails', async () => {
      // Mock API failure
      vi.mocked(editorApi.getAnnotations).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails).mockRejectedValue(
        new Error('Quality fetch failed')
      );

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner to appear
      await waitFor(() => {
        expect(screen.getByText(/Quality Data Unavailable/i)).toBeInTheDocument();
      });

      // Check that badges are hidden message is displayed
      expect(screen.getByText(/badges are hidden/i)).toBeInTheDocument();
    });

    it('should retry quality fetch when retry button is clicked', async () => {
      const user = userEvent.setup();

      // First call fails, second succeeds
      vi.mocked(editorApi.getAnnotations).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails)
        .mockRejectedValueOnce(new Error('Quality fetch failed'))
        .mockResolvedValueOnce({ data: {} } as any);

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner
      await waitFor(() => {
        expect(screen.getByText(/Quality Data Unavailable/i)).toBeInTheDocument();
      });

      // Click retry button
      const retryButtons = screen.getAllByRole('button', { name: /retry/i });
      await user.click(retryButtons[0]); // Quality retry button

      // Wait for error to clear
      await waitFor(() => {
        expect(screen.queryByText(/Quality Data Unavailable/i)).not.toBeInTheDocument();
      });
    });

    it('should not display quality badges when hideBadgesDueToError is true', async () => {
      // Mock API failure
      vi.mocked(editorApi.getAnnotations).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails).mockRejectedValue(
        new Error('Quality fetch failed')
      );

      render(<CodeEditorView file={mockFile} />);

      // Wait for error banner
      await waitFor(() => {
        expect(screen.getByText(/Quality Data Unavailable/i)).toBeInTheDocument();
      });

      // Quality gutter should not be rendered
      expect(screen.queryByTestId('quality-gutter')).not.toBeInTheDocument();
    });
  });

  describe('Multiple Errors', () => {
    it('should display multiple error banners when multiple APIs fail', async () => {
      // Mock all API failures
      vi.mocked(editorApi.getAnnotations).mockRejectedValue(
        new Error('Annotation error')
      );
      vi.mocked(editorApi.getChunks).mockRejectedValue(
        new Error('Chunk error')
      );
      vi.mocked(editorApi.getQualityDetails).mockRejectedValue(
        new Error('Quality error')
      );

      render(<CodeEditorView file={mockFile} />);

      // Wait for all error banners to appear
      await waitFor(() => {
        expect(screen.getByText(/Annotation Error/i)).toBeInTheDocument();
        expect(screen.getByText(/Using Line-Based Display/i)).toBeInTheDocument();
        expect(screen.getByText(/Quality Data Unavailable/i)).toBeInTheDocument();
      });

      // Should have multiple retry buttons
      const retryButtons = screen.getAllByRole('button', { name: /retry/i });
      expect(retryButtons.length).toBeGreaterThanOrEqual(3);
    });

    it('should handle independent retry for each error', async () => {
      const user = userEvent.setup();

      // Mock all API failures initially
      vi.mocked(editorApi.getAnnotations)
        .mockRejectedValueOnce(new Error('Annotation error'))
        .mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getChunks).mockRejectedValue(
        new Error('Chunk error')
      );
      vi.mocked(editorApi.getQualityDetails).mockRejectedValue(
        new Error('Quality error')
      );

      render(<CodeEditorView file={mockFile} />);

      // Wait for all errors
      await waitFor(() => {
        expect(screen.getByText(/Annotation Error/i)).toBeInTheDocument();
      });

      // Retry annotation (should succeed)
      const retryButtons = screen.getAllByRole('button', { name: /retry/i });
      await user.click(retryButtons[0]);

      // Annotation error should clear, others remain
      await waitFor(() => {
        expect(screen.queryByText(/Annotation Error/i)).not.toBeInTheDocument();
        expect(screen.getByText(/Using Line-Based Display/i)).toBeInTheDocument();
        expect(screen.getByText(/Quality Data Unavailable/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Recovery', () => {
    it('should clear errors when file changes', async () => {
      // Mock API failure for first file
      vi.mocked(editorApi.getAnnotations).mockRejectedValue(
        new Error('Network error')
      );
      vi.mocked(editorApi.getChunks).mockResolvedValue({ data: [] } as any);
      vi.mocked(editorApi.getQualityDetails).mockResolvedValue({ data: {} } as any);

      const { rerender } = render(<CodeEditorView file={mockFile} />);

      // Wait for error
      await waitFor(() => {
        expect(screen.getByText(/Annotation Error/i)).toBeInTheDocument();
      });

      // Mock success for second file
      vi.mocked(editorApi.getAnnotations).mockResolvedValue({ data: [] } as any);

      // Change file
      const newFile: CodeFile = {
        ...mockFile,
        id: 'file-2',
        resource_id: 'resource-2',
      };
      rerender(<CodeEditorView file={newFile} />);

      // Error should clear
      await waitFor(() => {
        expect(screen.queryByText(/Annotation Error/i)).not.toBeInTheDocument();
      });
    });
  });
});
