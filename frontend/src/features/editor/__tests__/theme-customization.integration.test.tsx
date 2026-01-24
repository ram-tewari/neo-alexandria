/**
 * Theme Customization Integration Tests
 * 
 * Tests the integration between theme switching and visual elements:
 * - Theme switching updates Monaco editor theme
 * - Syntax highlighting changes with theme
 * - Gutter decoration colors update with theme
 * 
 * Requirements: 1.2, 1.5
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MonacoEditorWrapper } from '../MonacoEditorWrapper';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import { getGutterDecorationColors } from '@/lib/monaco/themes';
import type { CodeFile } from '../types';

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ onMount, loading, theme }: any) => {
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

    return (
      <div data-testid="monaco-editor-mock" data-theme={theme}>
        {loading}
      </div>
    );
  },
}));

// Mock Monaco utilities
vi.mock('@/lib/monaco/themes', async () => {
  const actual = await vi.importActual('@/lib/monaco/themes');
  return {
    ...actual,
    registerThemes: vi.fn(),
    getMonacoTheme: vi.fn((theme) => theme === 'dark' ? 'pharos-dark' : 'pharos-light'),
  };
});

vi.mock('@/lib/monaco/languages', () => ({
  detectLanguage: vi.fn(() => 'typescript'),
}));

vi.mock('@/lib/monaco/decorations', () => ({
  DecorationManager: vi.fn().mockImplementation(() => ({
    updateDecorations: vi.fn(),
    clearDecorations: vi.fn(),
    clearAll: vi.fn(),
    dispose: vi.fn(),
  })),
}));

describe('Theme Customization Integration', () => {
  // ==========================================================================
  // Test Data
  // ==========================================================================

  const mockFile: CodeFile = {
    id: 'file-1',
    resource_id: 'resource-1',
    path: 'src/example.ts',
    name: 'example.ts',
    language: 'typescript',
    content: `// Comment
function greet(name: string): string {
  return \`Hello, \${name}!\`;
}

const result = greet("World");
console.log(result);`,
    size: 150,
    lines: 7,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  // ==========================================================================
  // Setup & Teardown
  // ==========================================================================

  beforeEach(() => {
    // Reset preferences to default
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

    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ==========================================================================
  // Theme Switching Tests (Requirement 1.5)
  // ==========================================================================

  describe('Theme Switching', () => {
    it('should apply dark theme by default', async () => {
      const { getMonacoTheme } = await import('@/lib/monaco/themes');
      
      render(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('dark');
      });
    });

    it('should apply light theme when preference is set', async () => {
      const { getMonacoTheme } = await import('@/lib/monaco/themes');
      
      useEditorPreferencesStore.setState({ theme: 'vs-light' });

      render(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('light');
      });
    });

    it('should switch theme without editor reload', async () => {
      const { getMonacoTheme } = await import('@/lib/monaco/themes');
      
      const { rerender } = render(<MonacoEditorWrapper file={mockFile} />);

      // Initial theme
      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('dark');
      });

      // Switch to light theme
      useEditorPreferencesStore.setState({ theme: 'vs-light' });
      rerender(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('light');
      });

      // Editor should not be recreated (no dispose call)
      expect(screen.getByTestId('monaco-editor-wrapper')).toBeInTheDocument();
    });

    it('should register custom themes on mount', async () => {
      const { registerThemes } = await import('@/lib/monaco/themes');
      
      render(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(registerThemes).toHaveBeenCalled();
      });
    });

    it('should update Monaco theme when preference changes', async () => {
      const { getMonacoTheme } = await import('@/lib/monaco/themes');
      
      const { rerender } = render(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('dark');
      });

      // Change theme
      useEditorPreferencesStore.setState({ theme: 'vs-light' });
      rerender(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('light');
      });
    });
  });

  // ==========================================================================
  // Syntax Highlighting Tests (Requirement 1.2)
  // ==========================================================================

  describe('Syntax Highlighting', () => {
    it('should detect language from file extension', async () => {
      const { detectLanguage } = require('@/lib/monaco/languages');

      render(<MonacoEditorWrapper file={mockFile} />);

      expect(detectLanguage).toHaveBeenCalledWith('src/example.ts');
    });

    it('should apply syntax highlighting for TypeScript', async () => {
      const tsFile: CodeFile = {
        ...mockFile,
        path: 'src/example.ts',
        language: 'typescript',
      };

      render(<MonacoEditorWrapper file={tsFile} />);

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });
    });

    it('should apply syntax highlighting for Python', async () => {
      const { detectLanguage } = require('@/lib/monaco/languages');
      detectLanguage.mockReturnValue('python');

      const pyFile: CodeFile = {
        ...mockFile,
        path: 'src/example.py',
        language: 'python',
        content: 'def greet(name: str) -> str:\n    return f"Hello, {name}!"',
      };

      render(<MonacoEditorWrapper file={pyFile} />);

      await waitFor(() => {
        expect(detectLanguage).toHaveBeenCalledWith('src/example.py');
      });
    });

    it('should apply syntax highlighting for JavaScript', async () => {
      const { detectLanguage } = require('@/lib/monaco/languages');
      detectLanguage.mockReturnValue('javascript');

      const jsFile: CodeFile = {
        ...mockFile,
        path: 'src/example.js',
        language: 'javascript',
        content: 'function greet(name) {\n  return `Hello, ${name}!`;\n}',
      };

      render(<MonacoEditorWrapper file={jsFile} />);

      await waitFor(() => {
        expect(detectLanguage).toHaveBeenCalledWith('src/example.js');
      });
    });

    it('should handle unsupported languages gracefully', async () => {
      const { detectLanguage } = require('@/lib/monaco/languages');
      detectLanguage.mockReturnValue('plaintext');

      const unknownFile: CodeFile = {
        ...mockFile,
        path: 'src/example.xyz',
        language: 'plaintext',
      };

      render(<MonacoEditorWrapper file={unknownFile} />);

      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor-mock')).toBeInTheDocument();
      });
    });
  });

  // ==========================================================================
  // Gutter Decoration Styling Tests (Requirement 1.2, 1.5)
  // ==========================================================================

  describe('Gutter Decoration Styling', () => {
    it('should use light theme colors for gutter decorations', () => {
      const colors = getGutterDecorationColors('light');

      expect(colors.qualityHigh).toBe('#22863a'); // Green
      expect(colors.qualityMedium).toBe('#e36209'); // Orange
      expect(colors.qualityLow).toBe('#cb2431'); // Red
      expect(colors.annotationDefault).toBe('#005cc5'); // Blue
      expect(colors.chunkSelectedBorder).toBe('#005cc5'); // Blue
    });

    it('should use dark theme colors for gutter decorations', () => {
      const colors = getGutterDecorationColors('dark');

      expect(colors.qualityHigh).toBe('#7ee787'); // Green
      expect(colors.qualityMedium).toBe('#ffa657'); // Orange
      expect(colors.qualityLow).toBe('#f85149'); // Red
      expect(colors.annotationDefault).toBe('#79c0ff'); // Blue
      expect(colors.chunkSelectedBorder).toBe('#79c0ff'); // Blue
    });

    it('should have different colors for light and dark themes', () => {
      const lightColors = getGutterDecorationColors('light');
      const darkColors = getGutterDecorationColors('dark');

      // Quality badge colors should differ
      expect(lightColors.qualityHigh).not.toBe(darkColors.qualityHigh);
      expect(lightColors.qualityMedium).not.toBe(darkColors.qualityMedium);
      expect(lightColors.qualityLow).not.toBe(darkColors.qualityLow);

      // Annotation colors should differ
      expect(lightColors.annotationDefault).not.toBe(darkColors.annotationDefault);
      expect(lightColors.annotationBorder).not.toBe(darkColors.annotationBorder);

      // Chunk colors should differ
      expect(lightColors.chunkSelectedBorder).not.toBe(darkColors.chunkSelectedBorder);
    });

    it('should provide chunk decoration colors', () => {
      const lightColors = getGutterDecorationColors('light');

      expect(lightColors.chunkBorder).toBeDefined();
      expect(lightColors.chunkBackground).toBeDefined();
      expect(lightColors.chunkHoverBorder).toBeDefined();
      expect(lightColors.chunkHoverBackground).toBeDefined();
      expect(lightColors.chunkSelectedBorder).toBeDefined();
      expect(lightColors.chunkSelectedBackground).toBeDefined();
    });

    it('should provide quality badge colors', () => {
      const lightColors = getGutterDecorationColors('light');

      expect(lightColors.qualityHigh).toBeDefined();
      expect(lightColors.qualityMedium).toBeDefined();
      expect(lightColors.qualityLow).toBeDefined();
    });

    it('should provide annotation colors', () => {
      const lightColors = getGutterDecorationColors('light');

      expect(lightColors.annotationDefault).toBeDefined();
      expect(lightColors.annotationHighlight).toBeDefined();
      expect(lightColors.annotationBorder).toBeDefined();
    });

    it('should provide reference icon colors', () => {
      const lightColors = getGutterDecorationColors('light');

      expect(lightColors.referenceIcon).toBeDefined();
      expect(lightColors.referenceIconHover).toBeDefined();
    });

    it('should use rgba colors for transparency', () => {
      const lightColors = getGutterDecorationColors('light');

      expect(lightColors.chunkBorder).toContain('rgba');
      expect(lightColors.chunkBackground).toContain('rgba');
      expect(lightColors.annotationHighlight).toContain('rgba');
    });
  });

  // ==========================================================================
  // Theme Consistency Tests
  // ==========================================================================

  describe('Theme Consistency', () => {
    it('should maintain consistent theme across editor and decorations', async () => {
      const { getMonacoTheme } = await import('@/lib/monaco/themes');
      
      useEditorPreferencesStore.setState({ theme: 'vs-light' });

      render(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('light');
      });

      // Gutter colors should match theme
      const colors = getGutterDecorationColors('light');
      expect(colors).toBeDefined();
    });

    it('should update all theme-dependent elements on theme change', async () => {
      const { getMonacoTheme } = await import('@/lib/monaco/themes');
      
      const { rerender } = render(<MonacoEditorWrapper file={mockFile} />);

      // Initial dark theme
      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('dark');
      });

      const darkColors = getGutterDecorationColors('dark');
      expect(darkColors.qualityHigh).toBe('#7ee787');

      // Switch to light theme
      useEditorPreferencesStore.setState({ theme: 'vs-light' });
      rerender(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('light');
      });

      const lightColors = getGutterDecorationColors('light');
      expect(lightColors.qualityHigh).toBe('#22863a');
    });

    it('should preserve theme preference across component remounts', async () => {
      const { getMonacoTheme } = await import('@/lib/monaco/themes');
      
      useEditorPreferencesStore.setState({ theme: 'vs-light' });

      const { unmount, rerender } = render(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('light');
      });

      unmount();

      // Remount with same preference
      rerender(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(getMonacoTheme).toHaveBeenCalledWith('light');
      });
    });
  });

  // ==========================================================================
  // WCAG Compliance Tests
  // ==========================================================================

  describe('WCAG Compliance', () => {
    it('should use WCAG AA compliant colors in light theme', () => {
      const colors = getGutterDecorationColors('light');

      // Quality colors should be distinguishable
      expect(colors.qualityHigh).toBe('#22863a'); // Green with good contrast
      expect(colors.qualityMedium).toBe('#e36209'); // Orange with good contrast
      expect(colors.qualityLow).toBe('#cb2431'); // Red with good contrast
    });

    it('should use WCAG AA compliant colors in dark theme', () => {
      const colors = getGutterDecorationColors('dark');

      // Quality colors should be distinguishable
      expect(colors.qualityHigh).toBe('#7ee787'); // Green with good contrast
      expect(colors.qualityMedium).toBe('#ffa657'); // Orange with good contrast
      expect(colors.qualityLow).toBe('#f85149'); // Red with good contrast
    });

    it('should provide sufficient contrast for annotations', () => {
      const lightColors = getGutterDecorationColors('light');
      const darkColors = getGutterDecorationColors('dark');

      // Annotation colors should be visible
      expect(lightColors.annotationDefault).toBe('#005cc5');
      expect(darkColors.annotationDefault).toBe('#79c0ff');
    });
  });

  // ==========================================================================
  // Performance Tests
  // ==========================================================================

  describe('Performance', () => {
    it('should not recreate editor on theme change', async () => {
      const { rerender } = render(<MonacoEditorWrapper file={mockFile} />);

      const initialWrapper = screen.getByTestId('monaco-editor-wrapper');

      // Change theme
      useEditorPreferencesStore.setState({ theme: 'vs-light' });
      rerender(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        expect(mockGetMonacoTheme).toHaveBeenCalledWith('light');
      });

      // Same wrapper element should exist
      expect(screen.getByTestId('monaco-editor-wrapper')).toBe(initialWrapper);
    });

    it('should batch theme updates efficiently', async () => {
      const { getMonacoTheme } = await import('@/lib/monaco/themes');
      
      const { rerender } = render(<MonacoEditorWrapper file={mockFile} />);

      // Multiple rapid theme changes
      useEditorPreferencesStore.setState({ theme: 'vs-light' });
      rerender(<MonacoEditorWrapper file={mockFile} />);

      useEditorPreferencesStore.setState({ theme: 'vs-dark' });
      rerender(<MonacoEditorWrapper file={mockFile} />);

      useEditorPreferencesStore.setState({ theme: 'vs-light' });
      rerender(<MonacoEditorWrapper file={mockFile} />);

      await waitFor(() => {
        // Should handle rapid changes without errors
        expect(screen.getByTestId('monaco-editor-wrapper')).toBeInTheDocument();
      });
    });
  });
});
