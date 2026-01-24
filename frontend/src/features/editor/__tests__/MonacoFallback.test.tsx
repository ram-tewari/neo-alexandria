/**
 * Unit tests for MonacoFallback component
 * 
 * Tests fallback text viewer functionality when Monaco fails to load.
 * 
 * Requirements: 10.1 - Error Handling and Fallbacks
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MonacoFallback } from '../MonacoFallback';
import type { CodeFile } from '../types';

// ============================================================================
// Test Data
// ============================================================================

const mockFile: CodeFile = {
  id: 'file-1',
  resource_id: 'resource-1',
  path: 'src/example.ts',
  name: 'example.ts',
  language: 'typescript',
  content: 'function hello() {\n  console.log("Hello, world!");\n}\n',
  size: 1024,
  lines: 3,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

// ============================================================================
// Tests
// ============================================================================

describe('MonacoFallback', () => {
  describe('Rendering', () => {
    it('should render fallback viewer with file content', () => {
      render(<MonacoFallback file={mockFile} />);

      // Check for fallback container
      expect(screen.getByTestId('monaco-fallback')).toBeInTheDocument();

      // Check for file name
      expect(screen.getByText('example.ts')).toBeInTheDocument();

      // Check for file metadata
      expect(screen.getByText(/typescript/)).toBeInTheDocument();
      expect(screen.getByText(/3 lines/)).toBeInTheDocument();

      // Check for file content
      expect(screen.getByText(/function hello\(\)/)).toBeInTheDocument();
      expect(screen.getByText(/console\.log/)).toBeInTheDocument();
    });

    it('should render error alert with default message', () => {
      render(<MonacoFallback file={mockFile} />);

      expect(screen.getByText('Editor Failed to Load')).toBeInTheDocument();
      expect(screen.getByText('Failed to load Monaco Editor')).toBeInTheDocument();
    });

    it('should render error alert with custom error message', () => {
      const errorMessage = 'Network error: Failed to fetch Monaco resources';
      render(<MonacoFallback file={mockFile} error={errorMessage} />);

      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    it('should render error alert with Error object', () => {
      const error = new Error('Monaco initialization failed');
      render(<MonacoFallback file={mockFile} error={error} />);

      expect(screen.getByText('Monaco initialization failed')).toBeInTheDocument();
    });

    it('should render info message about fallback mode', () => {
      render(<MonacoFallback file={mockFile} />);

      expect(
        screen.getByText(/Displaying file in fallback mode/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/syntax highlighting, annotations, and quality badges are unavailable/)
      ).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <MonacoFallback file={mockFile} className="custom-class" />
      );

      const fallback = container.querySelector('.monaco-fallback');
      expect(fallback).toHaveClass('custom-class');
    });
  });

  describe('Retry Functionality', () => {
    it('should render retry button when onRetry is provided', () => {
      const onRetry = vi.fn();
      render(<MonacoFallback file={mockFile} onRetry={onRetry} />);

      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('should not render retry button when onRetry is not provided', () => {
      render(<MonacoFallback file={mockFile} />);

      expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument();
    });

    it('should call onRetry when retry button is clicked', async () => {
      const user = userEvent.setup();
      const onRetry = vi.fn();
      render(<MonacoFallback file={mockFile} onRetry={onRetry} />);

      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);

      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    it('should show loading state while retrying', async () => {
      const user = userEvent.setup();
      const onRetry = vi.fn(() => new Promise((resolve) => setTimeout(resolve, 100)));
      render(<MonacoFallback file={mockFile} onRetry={onRetry} />);

      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);

      // Check for loading state
      expect(screen.getByText(/retrying/i)).toBeInTheDocument();
      expect(retryButton).toBeDisabled();

      // Wait for retry to complete
      await waitFor(() => {
        expect(screen.queryByText(/retrying/i)).not.toBeInTheDocument();
      });
    });

    it('should disable retry button during retry', async () => {
      const user = userEvent.setup();
      const onRetry = vi.fn(() => new Promise((resolve) => setTimeout(resolve, 100)));
      render(<MonacoFallback file={mockFile} onRetry={onRetry} />);

      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);

      expect(retryButton).toBeDisabled();

      // Wait for retry to complete
      await waitFor(() => {
        expect(retryButton).not.toBeDisabled();
      });
    });

    it('should handle retry errors gracefully', async () => {
      const user = userEvent.setup();
      const onRetry = vi.fn(() => Promise.reject(new Error('Retry failed')));
      render(<MonacoFallback file={mockFile} onRetry={onRetry} />);

      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);

      // Should still reset loading state even if retry fails
      await waitFor(() => {
        expect(retryButton).not.toBeDisabled();
      });
    });
  });

  describe('Content Display', () => {
    it('should preserve file content exactly', () => {
      const fileWithSpecialChars: CodeFile = {
        ...mockFile,
        content: 'const x = "<>&\'";\nconst y = `template ${x}`;',
      };

      render(<MonacoFallback file={fileWithSpecialChars} />);

      // Content should be preserved without HTML escaping issues
      expect(screen.getByText(/const x = "<>&'/)).toBeInTheDocument();
      expect(screen.getByText(/template \$\{x\}/)).toBeInTheDocument();
    });

    it('should handle empty file content', () => {
      const emptyFile: CodeFile = {
        ...mockFile,
        content: '',
        lines: 0,
      };

      render(<MonacoFallback file={emptyFile} />);

      expect(screen.getByTestId('monaco-fallback')).toBeInTheDocument();
      expect(screen.getByText('example.ts')).toBeInTheDocument();
    });

    it('should handle large file content', () => {
      const largeContent = Array.from({ length: 1000 }, (_, i) => `line ${i + 1}`).join('\n');
      const largeFile: CodeFile = {
        ...mockFile,
        content: largeContent,
        lines: 1000,
      };

      render(<MonacoFallback file={largeFile} />);

      expect(screen.getByText(/1000 lines/)).toBeInTheDocument();
      expect(screen.getByText(/line 1/)).toBeInTheDocument();
      expect(screen.getByText(/line 1000/)).toBeInTheDocument();
    });

    it('should preserve whitespace and indentation', () => {
      const indentedFile: CodeFile = {
        ...mockFile,
        content: 'function test() {\n    if (true) {\n        return 42;\n    }\n}',
      };

      const { container } = render(<MonacoFallback file={indentedFile} />);

      // Check that pre/code elements preserve whitespace
      const codeElement = container.querySelector('code');
      expect(codeElement).toHaveClass('whitespace-pre');
    });
  });

  describe('Accessibility', () => {
    it('should have proper semantic structure', () => {
      render(<MonacoFallback file={mockFile} onRetry={vi.fn()} />);

      // Check for alert role
      expect(screen.getByRole('alert')).toBeInTheDocument();

      // Check for button
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('should have accessible retry button', () => {
      const onRetry = vi.fn();
      render(<MonacoFallback file={mockFile} onRetry={onRetry} />);

      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toHaveAccessibleName();
    });
  });
});
