/**
 * ChunkMetadataPanel Component Tests
 * 
 * Tests for the chunk metadata panel including:
 * - Metadata display
 * - Navigation
 * - Expand/collapse
 * 
 * Requirements: 2.4
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { ChunkMetadataPanel } from '../ChunkMetadataPanel';
import type { SemanticChunk } from '../types';

describe('ChunkMetadataPanel', () => {
  // ==========================================================================
  // Test Data
  // ==========================================================================

  const mockChunk: SemanticChunk = {
    id: 'chunk-1',
    resource_id: 'resource-1',
    content: 'function calculateSum(a, b) {\n  return a + b;\n}',
    chunk_index: 0,
    chunk_metadata: {
      function_name: 'calculateSum',
      start_line: 10,
      end_line: 12,
      language: 'typescript',
    },
    created_at: '2024-01-01T00:00:00Z',
  };

  const mockClassChunk: SemanticChunk = {
    id: 'chunk-2',
    resource_id: 'resource-1',
    content: 'class Calculator {\n  // ...\n}',
    chunk_index: 1,
    chunk_metadata: {
      class_name: 'Calculator',
      start_line: 20,
      end_line: 30,
      language: 'typescript',
    },
    created_at: '2024-01-01T00:00:00Z',
  };

  // ==========================================================================
  // Metadata Display Tests
  // ==========================================================================

  describe('Metadata Display', () => {
    it('should display function name when available', () => {
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      expect(screen.getByText('Function')).toBeInTheDocument();
      expect(screen.getByText('calculateSum')).toBeInTheDocument();
    });

    it('should display class name when available', () => {
      render(<ChunkMetadataPanel chunk={mockClassChunk} />);
      
      expect(screen.getByText('Class')).toBeInTheDocument();
      expect(screen.getByText('Calculator')).toBeInTheDocument();
    });

    it('should display line range', () => {
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      expect(screen.getByText('10-12')).toBeInTheDocument();
      expect(screen.getByText('(3 lines)')).toBeInTheDocument();
    });

    it('should display language', () => {
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      expect(screen.getByText('typescript')).toBeInTheDocument();
    });

    it('should display chunk index', () => {
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('should display content preview', () => {
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      expect(screen.getByText(/function calculateSum/)).toBeInTheDocument();
    });

    it('should truncate long content', () => {
      const longChunk: SemanticChunk = {
        ...mockChunk,
        content: 'a'.repeat(300),
      };
      
      render(<ChunkMetadataPanel chunk={longChunk} />);
      
      const preview = screen.getByText(/a+\.\.\./);
      expect(preview).toBeInTheDocument();
    });

    it('should show placeholder when no chunk selected', () => {
      render(<ChunkMetadataPanel chunk={null} />);
      
      expect(screen.getByText('No Chunk Selected')).toBeInTheDocument();
      expect(screen.getByText(/Click on a chunk boundary/)).toBeInTheDocument();
    });
  });

  // ==========================================================================
  // Expand/Collapse Tests
  // ==========================================================================

  describe('Expand/Collapse', () => {
    it('should be expanded by default', () => {
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      expect(screen.getByText('Function')).toBeInTheDocument();
      expect(screen.getByText('Line Range')).toBeInTheDocument();
    });

    it('should collapse when clicking collapse button', async () => {
      const user = userEvent.setup();
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      const collapseButton = screen.getByRole('button');
      await user.click(collapseButton);
      
      expect(screen.queryByText('Function')).not.toBeInTheDocument();
      expect(screen.queryByText('Line Range')).not.toBeInTheDocument();
    });

    it('should expand when clicking expand button', async () => {
      const user = userEvent.setup();
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      const collapseButton = screen.getByRole('button');
      await user.click(collapseButton); // Collapse
      await user.click(collapseButton); // Expand
      
      expect(screen.getByText('Function')).toBeInTheDocument();
      expect(screen.getByText('Line Range')).toBeInTheDocument();
    });
  });

  // ==========================================================================
  // Navigation Tests
  // ==========================================================================

  describe('Navigation', () => {
    it('should show related chunks section when onNavigateToChunk provided', () => {
      const onNavigateToChunk = vi.fn();
      render(
        <ChunkMetadataPanel
          chunk={mockChunk}
          onNavigateToChunk={onNavigateToChunk}
        />
      );
      
      expect(screen.getByText('Related Chunks')).toBeInTheDocument();
    });

    it('should not show related chunks section when onNavigateToChunk not provided', () => {
      render(<ChunkMetadataPanel chunk={mockChunk} />);
      
      expect(screen.queryByText('Related Chunks')).not.toBeInTheDocument();
    });

    it('should show Phase 3 placeholder message', () => {
      const onNavigateToChunk = vi.fn();
      render(
        <ChunkMetadataPanel
          chunk={mockChunk}
          onNavigateToChunk={onNavigateToChunk}
        />
      );
      
      expect(screen.getByText(/Graph-based chunk relationships/)).toBeInTheDocument();
    });
  });

  // ==========================================================================
  // Edge Cases
  // ==========================================================================

  describe('Edge Cases', () => {
    it('should handle chunk without function or class name', () => {
      const unknownChunk: SemanticChunk = {
        ...mockChunk,
        chunk_metadata: {
          start_line: 1,
          end_line: 5,
          language: 'typescript',
        },
      };
      
      render(<ChunkMetadataPanel chunk={unknownChunk} />);
      
      expect(screen.getByText('Unknown')).toBeInTheDocument();
    });

    it('should handle single line chunk', () => {
      const singleLineChunk: SemanticChunk = {
        ...mockChunk,
        chunk_metadata: {
          ...mockChunk.chunk_metadata,
          start_line: 10,
          end_line: 10,
        },
      };
      
      render(<ChunkMetadataPanel chunk={singleLineChunk} />);
      
      expect(screen.getByText('(1 line)')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <ChunkMetadataPanel chunk={mockChunk} className="custom-class" />
      );
      
      const card = container.querySelector('.custom-class');
      expect(card).toBeInTheDocument();
    });

    it('should handle empty content', () => {
      const emptyChunk: SemanticChunk = {
        ...mockChunk,
        content: '',
      };
      
      render(<ChunkMetadataPanel chunk={emptyChunk} />);
      
      // Should not crash
      expect(screen.getByText('Content Preview')).toBeInTheDocument();
    });
  });
});
