/**
 * Tests for Monaco Editor decoration utilities
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  DecorationManager,
  createChunkDecorations,
  getQualityLevel,
  createQualityDecorations,
  createAnnotationDecorations,
  createReferenceDecorations,
  offsetToPosition,
  positionToOffset,
} from '../decorations';
import type { SemanticChunk, Annotation } from '@/features/editor/types';

describe('Monaco Decorations', () => {
  describe('DecorationManager', () => {
    let mockEditor: any;
    let manager: DecorationManager;

    beforeEach(() => {
      vi.useFakeTimers();
      mockEditor = {
        deltaDecorations: vi.fn().mockReturnValue(['decoration-1', 'decoration-2']),
      };
      manager = new DecorationManager(mockEditor);
    });

    afterEach(() => {
      vi.restoreAllMocks();
      vi.useRealTimers();
    });

    it('should debounce decoration updates', () => {
      const decorations = [
        {
          range: { startLineNumber: 1, startColumn: 1, endLineNumber: 1, endColumn: 10 },
          options: { className: 'test' },
        },
      ];

      manager.updateDecorations('test-key', decorations);
      expect(mockEditor.deltaDecorations).not.toHaveBeenCalled();

      vi.advanceTimersByTime(100);
      expect(mockEditor.deltaDecorations).toHaveBeenCalledTimes(1);
    });

    it('should clear decorations for a specific key', () => {
      const decorations = [
        {
          range: { startLineNumber: 1, startColumn: 1, endLineNumber: 1, endColumn: 10 },
          options: { className: 'test' },
        },
      ];

      manager.updateDecorations('test-key', decorations);
      vi.advanceTimersByTime(100);

      manager.clearDecorations('test-key');
      expect(mockEditor.deltaDecorations).toHaveBeenCalledWith(
        ['decoration-1', 'decoration-2'],
        []
      );
    });

    it('should clear all decorations', () => {
      const decorations = [
        {
          range: { startLineNumber: 1, startColumn: 1, endLineNumber: 1, endColumn: 10 },
          options: { className: 'test' },
        },
      ];

      // Update decorations for two different keys
      manager.updateDecorations('key1', decorations);
      vi.advanceTimersByTime(100);
      
      manager.updateDecorations('key2', decorations);
      vi.advanceTimersByTime(100);

      // After updates, should have been called twice
      expect(mockEditor.deltaDecorations).toHaveBeenCalledTimes(2);

      manager.clearAll();
      
      // After clearAll, should have been called 4 times total (2 updates + 2 clears)
      expect(mockEditor.deltaDecorations).toHaveBeenCalledTimes(4);
    });

    it('should dispose properly', () => {
      manager.updateDecorations('test-key', []);
      manager.dispose();

      vi.advanceTimersByTime(100);
      expect(mockEditor.deltaDecorations).not.toHaveBeenCalled();
    });
  });

  describe('createChunkDecorations', () => {
    it('should create decorations for chunks', () => {
      const chunks: SemanticChunk[] = [
        {
          id: 'chunk-1',
          resource_id: 'resource-1',
          content: 'function test() {}',
          chunk_index: 0,
          chunk_metadata: {
            function_name: 'test',
            start_line: 1,
            end_line: 3,
            language: 'javascript',
          },
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      const decorations = createChunkDecorations(chunks);

      expect(decorations).toHaveLength(1);
      expect(decorations[0].range.startLineNumber).toBe(1);
      expect(decorations[0].range.endLineNumber).toBe(3);
      expect(decorations[0].options.className).toBe('semantic-chunk-boundary');
    });

    it('should highlight selected chunk', () => {
      const chunks: SemanticChunk[] = [
        {
          id: 'chunk-1',
          resource_id: 'resource-1',
          content: 'function test() {}',
          chunk_index: 0,
          chunk_metadata: {
            function_name: 'test',
            start_line: 1,
            end_line: 3,
            language: 'javascript',
          },
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      const decorations = createChunkDecorations(chunks, 'chunk-1');

      expect(decorations[0].options.className).toBe('semantic-chunk-boundary-selected');
    });

    it('should include function name in hover message', () => {
      const chunks: SemanticChunk[] = [
        {
          id: 'chunk-1',
          resource_id: 'resource-1',
          content: 'function myFunction() {}',
          chunk_index: 0,
          chunk_metadata: {
            function_name: 'myFunction',
            start_line: 1,
            end_line: 3,
            language: 'javascript',
          },
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      const decorations = createChunkDecorations(chunks);

      expect(decorations[0].options.hoverMessage?.value).toContain('myFunction');
    });
  });

  describe('getQualityLevel', () => {
    it('should return high for scores >= 0.8', () => {
      expect(getQualityLevel(0.8)).toBe('high');
      expect(getQualityLevel(0.9)).toBe('high');
      expect(getQualityLevel(1.0)).toBe('high');
    });

    it('should return medium for scores between 0.6 and 0.8', () => {
      expect(getQualityLevel(0.6)).toBe('medium');
      expect(getQualityLevel(0.7)).toBe('medium');
      expect(getQualityLevel(0.79)).toBe('medium');
    });

    it('should return low for scores < 0.6', () => {
      expect(getQualityLevel(0.0)).toBe('low');
      expect(getQualityLevel(0.3)).toBe('low');
      expect(getQualityLevel(0.59)).toBe('low');
    });
  });

  describe('createQualityDecorations', () => {
    it('should create decorations for quality data', () => {
      const qualityData = [
        {
          line: 10,
          score: 0.85,
          dimensions: {
            accuracy: 0.9,
            completeness: 0.8,
            consistency: 0.85,
            timeliness: 0.8,
            relevance: 0.9,
          },
        },
      ];

      const decorations = createQualityDecorations(qualityData);

      expect(decorations).toHaveLength(1);
      expect(decorations[0].range.startLineNumber).toBe(10);
      expect(decorations[0].options.glyphMarginClassName).toContain('quality-high');
    });

    it('should include quality metrics in hover message', () => {
      const qualityData = [
        {
          line: 10,
          score: 0.75,
          dimensions: {
            accuracy: 0.8,
            completeness: 0.7,
            consistency: 0.75,
            timeliness: 0.7,
            relevance: 0.8,
          },
        },
      ];

      const decorations = createQualityDecorations(qualityData);

      expect(decorations[0].options.glyphMarginHoverMessage?.value).toContain('Quality');
      expect(decorations[0].options.glyphMarginHoverMessage?.value).toContain('Accuracy');
      expect(decorations[0].options.glyphMarginHoverMessage?.value).toContain('Completeness');
    });
  });

  describe('createAnnotationDecorations', () => {
    it('should create gutter chip and text highlight decorations', () => {
      const content = 'function test() {\n  return 42;\n}';
      const annotations: Annotation[] = [
        {
          id: 'ann-1',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 0,
          end_offset: 13,
          highlighted_text: 'function test',
          note: 'Test annotation',
          color: 'yellow',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      const decorations = createAnnotationDecorations(annotations, content);

      // Should create 2 decorations: gutter chip + text highlight
      expect(decorations).toHaveLength(2);
      expect(decorations[0].options.glyphMarginClassName).toContain('annotation-chip');
      expect(decorations[1].options.inlineClassName).toContain('annotation-highlight');
    });

    it('should apply annotation color to decorations', () => {
      const content = 'test';
      const annotations: Annotation[] = [
        {
          id: 'ann-1',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 0,
          end_offset: 4,
          highlighted_text: 'test',
          color: 'blue',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      const decorations = createAnnotationDecorations(annotations, content);

      expect(decorations[0].options.glyphMarginClassName).toContain('blue');
      expect(decorations[1].options.inlineClassName).toContain('blue');
    });
  });

  describe('createReferenceDecorations', () => {
    it('should create decorations for references', () => {
      const references = [
        { line: 5, title: 'Research Paper', type: 'paper' },
        { line: 10, title: 'Documentation', type: 'documentation' },
      ];

      const decorations = createReferenceDecorations(references);

      expect(decorations).toHaveLength(2);
      expect(decorations[0].range.startLineNumber).toBe(5);
      expect(decorations[0].options.glyphMarginClassName).toContain('reference-paper');
      expect(decorations[1].range.startLineNumber).toBe(10);
      expect(decorations[1].options.glyphMarginClassName).toContain('reference-documentation');
    });

    it('should include reference title in hover message', () => {
      const references = [{ line: 5, title: 'Important Paper', type: 'paper' }];

      const decorations = createReferenceDecorations(references);

      expect(decorations[0].options.glyphMarginHoverMessage?.value).toContain('Important Paper');
    });
  });

  describe('offsetToPosition', () => {
    it('should convert offset to line and column', () => {
      const content = 'line 1\nline 2\nline 3';

      expect(offsetToPosition(content, 0)).toEqual({ line: 1, column: 1 });
      expect(offsetToPosition(content, 7)).toEqual({ line: 2, column: 1 });
      expect(offsetToPosition(content, 14)).toEqual({ line: 3, column: 1 });
    });

    it('should handle offset in middle of line', () => {
      const content = 'hello world';

      expect(offsetToPosition(content, 6)).toEqual({ line: 1, column: 7 });
    });

    it('should handle multi-line content', () => {
      const content = 'first\nsecond\nthird';

      expect(offsetToPosition(content, 6)).toEqual({ line: 2, column: 1 });
      expect(offsetToPosition(content, 13)).toEqual({ line: 3, column: 1 });
    });
  });

  describe('positionToOffset', () => {
    it('should convert line and column to offset', () => {
      const content = 'line 1\nline 2\nline 3';

      expect(positionToOffset(content, 1, 1)).toBe(0);
      expect(positionToOffset(content, 2, 1)).toBe(7);
      expect(positionToOffset(content, 3, 1)).toBe(14);
    });

    it('should handle position in middle of line', () => {
      const content = 'hello world';

      expect(positionToOffset(content, 1, 7)).toBe(6);
    });

    it('should handle multi-line content', () => {
      const content = 'first\nsecond\nthird';

      expect(positionToOffset(content, 2, 1)).toBe(6);
      expect(positionToOffset(content, 3, 1)).toBe(13);
    });

    it('should handle column beyond line length', () => {
      const content = 'short';

      expect(positionToOffset(content, 1, 100)).toBe(5);
    });
  });
});
