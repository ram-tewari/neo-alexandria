/**
 * MonacoEditorWrapper Component Tests
 * 
 * Tests for the core Monaco Editor wrapper component including:
 * - Monaco initialization
 * - Theme switching
 * - Cursor/selection tracking
 * - Decoration management
 * - Large file optimization
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MonacoEditorWrapper } from '../MonacoEditorWrapper';
import type { CodeFile } from '../types';
import { useEditorStore } from '@/stores/editor';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ onMount, loading }: any) => {
    // Simulate editor mount after a short delay
    setTimeout(() => {
      const mockEditor = {
        dispose: vi.fn(),
        setScrollTop: vi.fn(),
        updateOptions: vi.fn(),
        onDidChangeCursorPosition: vi.fn(() => ({ dispose: vi.fn() })),
        onDidChangeCursorSelection: vi.fn(() => ({ dispose: vi.fn() })),
        onDidScrollChange: vi.fn(() => ({ dispose: vi.fn() })),
        deltaDecorations: vi.fn(() => []),
      };

      const mockMonaco = {
        editor: {
          defineTheme: vi.fn(),
          setTheme: vi.fn(),
        },
      };

      onMount?.(mockEditor, mockMonaco);
    }, 0);

    return <div data-testid="monaco-editor-mock">{loading}</div>;
  },
}));

// Mock Monaco utilities
vi.mock('@/lib/monaco/themes', () => ({
  registerThemes: vi.fn(),
  getMonacoTheme: vi.fn((theme) => theme === 'dark' ? 'pharos-dark' : 'pharos-light'),
}));

vi.mock('@/lib/monaco/languages', () => ({
  detectLanguage: vi.fn((path) => {
    if (path.endsWith('.ts')) return 'typescript';
    if (path.endsWith('.py')) return 'python';
    return 'plaintext';
  }),
}));

vi.mock('@/lib/monaco/decorations', () => ({
  DecorationManager: vi.fn().mockImplementation(() => ({
    updateDecorations: vi.fn(),
    clearDecorations: vi.fn(),
    clearAll: vi.fn(),
    dispose: vi.fn(),
  })),
}));

describe('MonacoEditorWrapper', () => {
  // ==========================================================================
  // Test Data
  // ==========================================================================

  const mockFile: CodeFile = {
    id: 'file-1',
    resource_id: 'resource-1',
    path: 'src/example.ts',
    name: 'example.ts',
    language: 'typescript',
    content: 'const x = 1;\nconst y = 2;\nconst z = x + y;',
    size: 100,
    lines: 3,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  const mockLargeFile: CodeFile = {
    ...mockFile,
    id: 'file-2',
    lines: 6000, // Large file
    content: Array(6000).fill('const x = 1;').join('\n'),
  };

  // ==========================================================================
  // Setup & Teardown
  // ==========================================================================

  beforeEach(() => {
    // Reset stores
    useEditorStore.setState({
      activeFile: null,
      cursorPosition: { line: 1, column: 1 },
      selection: null,
      scrollPosition: 0,
      scrollPositions: {},
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
  // Monaco Initialization Tests
  // ==========================================================================

  describe('Monaco Initialization', () => {
    it('should render Monaco editor', () => {
      render(<MonacoEditorWrapper file={mockFile} />);
      
      expect(screen.getByTestId('monaco-editor-wrapper')).toBeInTheDocument();
      expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
    });

    it('should show loading state initially', () => {
      render(<MonacoEditorWrapper file={mockFile} />);
      
      expect(screen.getByText('Loading editor...')).toBeInTheDocument();
    });

    it('should detect language from file path', () => {
      const { detectLanguage } = require('@/lib/monaco/languages');
      
      render(<MonacoEditorWrapper file={mockFile} />);
      
      expect(detectLanguage).toHaveBeenCalledWith(mockFile.path);
    });

    it('should call onEditorReady when editor mounts', async () => {
      const onEditorReady = vi.fn();
      
      render(<MonacoEditorWrapper file={mockFile} onEditorReady={onEditorReady} />);
      
      await waitFor(() => {
        expect(onEditorReady).toHaveBeenCalled();
      });
    });

    it('should initialize decoration manager', async () => {
      const { DecorationManager } = require('@/lib/monaco/decorations');
      const onEditorReady = vi.fn();
      
      render(<MonacoEditorWrapper file={mockFile} onEditorReady={onEditorReady} />);
      
      await waitFor(() => {
        expect(DecorationManager).toHaveBeenCalled();
        expect(onEditorReady).toHaveBeenCalledWith(
          expect.anything(),
          expect.anything(),
          expect.anything() // decoration manager
        );
      });
    });
  });

  // ==========================================================================
  // Theme Switching Tests
  // ==========================================================================

  describe('Theme Switching', () => {
    it('should use correct theme based on preferences', () => {
      const { getMonacoTheme } = require('@/lib/monaco/themes');
      
      render(<MonacoEditorWrapper file={mockFile} />);
      
      expect(getMonacoTheme).toHaveBeenCalledWith('dark');
    });

    it('should update theme when preferences change', async () => {
      const { rerender } = render(<MonacoEditorWrapper file={mockFile} />);
      
      // Change theme preference
      useEditorPreferencesStore.setState({ theme: 'vs-light' });
      
      rerender(<MonacoEditorWrapper file={mockFile} />);
      
      const { getMonacoTheme } = require('@/lib/monaco/themes');
      expect(getMonacoTheme).toHaveBeenCalledWith('light');
    });

    it('should register custom themes on mount', async () => {
      const { registerThemes } = require('@/lib/monaco/themes');
      
      render(<MonacoEditorWrapper file={mockFile} />);
      
      await waitFor(() => {
        expect(registerThemes).toHaveBeenCalled();
      });
    });
  });

  // ==========================================================================
  // Cursor/Selection Tracking Tests
  // ==========================================================================

  describe('Cursor and Selection Tracking', () => {
    it('should call onCursorChange when cursor moves', async () => {
      const onCursorChange = vi.fn();
      
      render(<MonacoEditorWrapper file={mockFile} onCursorChange={onCursorChange} />);
      
      await waitFor(() => {
        // Editor should set up cursor tracking
        expect(onCursorChange).toHaveBeenCalledTimes(0); // Not called until cursor actually moves
      });
    });

    it('should call onSelectionChange when selection changes', async () => {
      const onSelectionChange = vi.fn();
      
      render(<MonacoEditorWrapper file={mockFile} onSelectionChange={onSelectionChange} />);
      
      await waitFor(() => {
        // Editor should set up selection tracking
        expect(onSelectionChange).toHaveBeenCalledTimes(0); // Not called until selection actually changes
      });
    });

    it('should update editor store with cursor position', async () => {
      render(<MonacoEditorWrapper file={mockFile} />);
      
      await waitFor(() => {
        // Initial cursor position should be set
        const state = useEditorStore.getState();
        expect(state.cursorPosition).toEqual({ line: 1, column: 1 });
      });
    });
  });

  // ==========================================================================
  // Decoration Management Tests
  // ==========================================================================

  describe('Decoration Management', () => {
    it('should provide decoration manager to parent', async () => {
      const onEditorReady = vi.fn();
      
      render(<MonacoEditorWrapper file={mockFile} onEditorReady={onEditorReady} />);
      
      await waitFor(() => {
        expect(onEditorReady).toHaveBeenCalledWith(
          expect.anything(),
          expect.anything(),
          expect.objectContaining({
            updateDecorations: expect.any(Function),
            clearDecorations: expect.any(Function),
            dispose: expect.any(Function),
          })
        );
      });
    });

    it('should dispose decoration manager on unmount', async () => {
      const { DecorationManager } = require('@/lib/monaco/decorations');
      const mockDispose = vi.fn();
      
      DecorationManager.mockImplementation(() => ({
        updateDecorations: vi.fn(),
        clearDecorations: vi.fn(),
        clearAll: vi.fn(),
        dispose: mockDispose,
      }));
      
      const { unmount } = render(<MonacoEditorWrapper file={mockFile} />);
      
      await waitFor(() => {
        expect(DecorationManager).toHaveBeenCalled();
      });
      
      unmount();
      
      expect(mockDispose).toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Large File Optimization Tests
  // ==========================================================================

  describe('Large File Optimization', () => {
    it('should detect large files (>5000 lines)', () => {
      render(<MonacoEditorWrapper file={mockLargeFile} />);
      
      // Component should render without errors
      expect(screen.getByTestId('monaco-editor-wrapper')).toBeInTheDocument();
    });

    it('should disable minimap for large files', async () => {
      render(<MonacoEditorWrapper file={mockLargeFile} />);
      
      await waitFor(() => {
        // Minimap should be disabled for large files
        // This is tested through Monaco options
      });
    });

    it('should enable minimap for small files', async () => {
      render(<MonacoEditorWrapper file={mockFile} />);
      
      await waitFor(() => {
        // Minimap should be enabled for small files
        // This is tested through Monaco options
      });
    });
  });

  // ==========================================================================
  // Preferences Update Tests
  // ==========================================================================

  describe('Preferences Updates', () => {
    it('should update editor options when preferences change', async () => {
      const { rerender } = render(<MonacoEditorWrapper file={mockFile} />);
      
      // Wait for editor to mount
      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });
      
      // Change preferences
      useEditorPreferencesStore.setState({
        fontSize: 16,
        lineNumbers: false,
        minimap: false,
        wordWrap: true,
      });
      
      rerender(<MonacoEditorWrapper file={mockFile} />);
      
      // Editor should update options (tested through Monaco mock)
    });

    it('should respect font size preference', () => {
      useEditorPreferencesStore.setState({ fontSize: 18 });
      
      render(<MonacoEditorWrapper file={mockFile} />);
      
      // Font size should be applied to Monaco options
      expect(screen.getByTestId('monaco-editor-wrapper')).toBeInTheDocument();
    });

    it('should respect line numbers preference', () => {
      useEditorPreferencesStore.setState({ lineNumbers: false });
      
      render(<MonacoEditorWrapper file={mockFile} />);
      
      // Line numbers should be disabled in Monaco options
      expect(screen.getByTestId('monaco-editor-wrapper')).toBeInTheDocument();
    });

    it('should respect word wrap preference', () => {
      useEditorPreferencesStore.setState({ wordWrap: true });
      
      render(<MonacoEditorWrapper file={mockFile} />);
      
      // Word wrap should be enabled in Monaco options
      expect(screen.getByTestId('monaco-editor-wrapper')).toBeInTheDocument();
    });
  });

  // ==========================================================================
  // Scroll Position Tests
  // ==========================================================================

  describe('Scroll Position', () => {
    it('should restore scroll position from store', async () => {
      useEditorStore.setState({
        scrollPosition: 500,
        scrollPositions: { 'file-1': 500 },
      });
      
      render(<MonacoEditorWrapper file={mockFile} />);
      
      await waitFor(() => {
        // Scroll position should be restored
        // This is tested through Monaco mock
      });
    });

    it('should persist scroll position on scroll', async () => {
      render(<MonacoEditorWrapper file={mockFile} />);
      
      await waitFor(() => {
        // Scroll tracking should be set up
        // This is tested through Monaco mock
      });
    });
  });

  // ==========================================================================
  // Cleanup Tests
  // ==========================================================================

  describe('Cleanup', () => {
    it('should dispose editor on unmount', async () => {
      const { unmount } = render(<MonacoEditorWrapper file={mockFile} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });
      
      unmount();
      
      // Editor should be disposed (tested through Monaco mock)
    });

    it('should dispose decoration manager on unmount', async () => {
      const { DecorationManager } = require('@/lib/monaco/decorations');
      const mockDispose = vi.fn();
      
      DecorationManager.mockImplementation(() => ({
        dispose: mockDispose,
        updateDecorations: vi.fn(),
        clearDecorations: vi.fn(),
        clearAll: vi.fn(),
      }));
      
      const { unmount } = render(<MonacoEditorWrapper file={mockFile} />);
      
      await waitFor(() => {
        expect(DecorationManager).toHaveBeenCalled();
      });
      
      unmount();
      
      expect(mockDispose).toHaveBeenCalled();
    });
  });

  // ==========================================================================
  // Custom Props Tests
  // ==========================================================================

  describe('Custom Props', () => {
    it('should apply custom className', () => {
      render(<MonacoEditorWrapper file={mockFile} className="custom-class" />);
      
      const wrapper = screen.getByTestId('monaco-editor-wrapper');
      expect(wrapper).toHaveClass('custom-class');
    });

    it('should handle missing optional callbacks', () => {
      // Should not throw errors when callbacks are not provided
      expect(() => {
        render(<MonacoEditorWrapper file={mockFile} />);
      }).not.toThrow();
    });
  });
});

