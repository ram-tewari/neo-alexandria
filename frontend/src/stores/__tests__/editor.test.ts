import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useEditorStore, resourceToCodeFile } from '../editor';
import type { CodeFile } from '@/features/editor/types';
import type { Resource } from '@/types/api';

/**
 * Unit Tests for Editor Store
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 5.3 Update editor store to use real resource data
 * Tests state updates, actions, loading/error states, and persistence logic
 * Validates: Requirements 3.1, 3.5, 3.6
 */

describe('Editor Store', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset store to initial state
    useEditorStore.setState({
      activeResourceId: null,
      activeFile: null,
      isLoading: false,
      error: null,
      cursorPosition: { line: 1, column: 1 },
      selection: null,
      scrollPosition: 0,
      scrollPositions: {},
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Resource to CodeFile Conversion', () => {
    it('should convert Resource to CodeFile', () => {
      const mockResource: Resource = {
        id: 'resource-1',
        title: 'main.ts',
        content: 'console.log("hello");',
        content_type: 'code',
        language: 'typescript',
        file_path: '/src/main.ts',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        ingestion_status: 'completed',
      };

      const codeFile = resourceToCodeFile(mockResource);

      expect(codeFile).toEqual({
        id: 'resource-1',
        resource_id: 'resource-1',
        path: '/src/main.ts',
        name: 'main.ts',
        language: 'typescript',
        content: 'console.log("hello");',
        size: 21,
        lines: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      });
    });

    it('should handle Resource without file_path', () => {
      const mockResource: Resource = {
        id: 'resource-1',
        title: 'Document',
        content: 'test content',
        url: 'https://example.com/doc',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        ingestion_status: 'completed',
      };

      const codeFile = resourceToCodeFile(mockResource);

      expect(codeFile.path).toBe('https://example.com/doc');
    });

    it('should handle Resource with no content', () => {
      const mockResource: Resource = {
        id: 'resource-1',
        title: 'Empty',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        ingestion_status: 'pending',
      };

      const codeFile = resourceToCodeFile(mockResource);

      expect(codeFile.content).toBe('');
      expect(codeFile.size).toBe(0);
      expect(codeFile.lines).toBe(0);
    });
  });

  describe('Active Resource Management', () => {
    it('should set active resource ID and loading state', () => {
      useEditorStore.getState().setActiveResource('resource-1');

      const state = useEditorStore.getState();
      expect(state.activeResourceId).toBe('resource-1');
      expect(state.isLoading).toBe(true);
      expect(state.error).toBeNull();
    });

    it('should clear loading state when resource ID is null', () => {
      useEditorStore.getState().setActiveResource('resource-1');
      useEditorStore.getState().setActiveResource(null);

      const state = useEditorStore.getState();
      expect(state.activeResourceId).toBeNull();
      expect(state.isLoading).toBe(false);
    });
  });

  describe('Active File Management', () => {
    it('should set active file', () => {
      const mockFile: CodeFile = {
        id: 'file-1',
        resource_id: 'resource-1',
        path: '/src/main.ts',
        name: 'main.ts',
        language: 'typescript',
        content: 'console.log("hello");',
        size: 1024,
        lines: 10,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useEditorStore.getState().setActiveFile(mockFile);

      const state = useEditorStore.getState();
      expect(state.activeFile).toEqual(mockFile);
      expect(state.cursorPosition).toEqual({ line: 1, column: 1 });
      expect(state.selection).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should clear active file', () => {
      const mockFile: CodeFile = {
        id: 'file-1',
        resource_id: 'resource-1',
        path: '/src/main.ts',
        name: 'main.ts',
        language: 'typescript',
        content: 'console.log("hello");',
        size: 1024,
        lines: 10,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useEditorStore.getState().setActiveFile(mockFile);
      useEditorStore.getState().setActiveFile(null);

      const state = useEditorStore.getState();
      expect(state.activeFile).toBeNull();
      expect(state.scrollPosition).toBe(0);
      expect(state.isLoading).toBe(false);
    });
  });

  describe('Loading and Error States', () => {
    it('should set loading state', () => {
      useEditorStore.getState().setLoading(true);
      expect(useEditorStore.getState().isLoading).toBe(true);

      useEditorStore.getState().setLoading(false);
      expect(useEditorStore.getState().isLoading).toBe(false);
    });

    it('should set error state and clear loading', () => {
      const error = new Error('Failed to load resource');
      
      useEditorStore.getState().setLoading(true);
      useEditorStore.getState().setError(error);

      const state = useEditorStore.getState();
      expect(state.error).toBe(error);
      expect(state.isLoading).toBe(false);
    });

    it('should clear error state', () => {
      const error = new Error('Failed to load resource');
      
      useEditorStore.getState().setError(error);
      expect(useEditorStore.getState().error).toBe(error);

      useEditorStore.getState().setError(null);
      expect(useEditorStore.getState().error).toBeNull();
    });
  });

  describe('Clear Editor', () => {
    it('should clear all editor state', () => {
      const mockFile: CodeFile = {
        id: 'file-1',
        resource_id: 'resource-1',
        path: '/src/main.ts',
        name: 'main.ts',
        language: 'typescript',
        content: 'console.log("hello");',
        size: 1024,
        lines: 10,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useEditorStore.getState().setActiveResource('resource-1');
      useEditorStore.getState().setActiveFile(mockFile);
      useEditorStore.getState().updateCursorPosition({ line: 10, column: 5 });
      useEditorStore.getState().updateSelection({
        start: { line: 1, column: 1 },
        end: { line: 5, column: 10 },
      });

      useEditorStore.getState().clearEditor();

      const state = useEditorStore.getState();
      expect(state.activeResourceId).toBeNull();
      expect(state.activeFile).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.cursorPosition).toEqual({ line: 1, column: 1 });
      expect(state.selection).toBeNull();
      expect(state.scrollPosition).toBe(0);
    });
  });

  describe('Cursor Position', () => {
    it('should update cursor position', () => {
      const position = { line: 10, column: 5 };
      
      useEditorStore.getState().updateCursorPosition(position);

      expect(useEditorStore.getState().cursorPosition).toEqual(position);
    });

    it('should handle multiple cursor position updates', () => {
      const positions = [
        { line: 1, column: 1 },
        { line: 5, column: 10 },
        { line: 20, column: 3 },
      ];

      for (const position of positions) {
        useEditorStore.getState().updateCursorPosition(position);
        expect(useEditorStore.getState().cursorPosition).toEqual(position);
      }
    });
  });

  describe('Selection', () => {
    it('should update selection', () => {
      const selection = {
        start: { line: 1, column: 1 },
        end: { line: 5, column: 10 },
      };

      useEditorStore.getState().updateSelection(selection);

      expect(useEditorStore.getState().selection).toEqual(selection);
    });

    it('should clear selection', () => {
      const selection = {
        start: { line: 1, column: 1 },
        end: { line: 5, column: 10 },
      };

      useEditorStore.getState().updateSelection(selection);
      useEditorStore.getState().updateSelection(null);

      expect(useEditorStore.getState().selection).toBeNull();
    });
  });

  describe('Scroll Position Persistence', () => {
    it('should update scroll position for active file', () => {
      const mockFile: CodeFile = {
        id: 'file-1',
        resource_id: 'resource-1',
        path: '/src/main.ts',
        name: 'main.ts',
        language: 'typescript',
        content: 'console.log("hello");',
        size: 1024,
        lines: 10,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useEditorStore.getState().setActiveFile(mockFile);
      useEditorStore.getState().updateScrollPosition(500);

      const state = useEditorStore.getState();
      expect(state.scrollPosition).toBe(500);
      expect(state.scrollPositions['file-1']).toBe(500);
    });

    it('should restore scroll position when switching files', async () => {
      const file1: CodeFile = {
        id: 'file-1',
        resource_id: 'resource-1',
        path: '/src/main.ts',
        name: 'main.ts',
        language: 'typescript',
        content: 'console.log("hello");',
        size: 1024,
        lines: 10,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      const file2: CodeFile = {
        id: 'file-2',
        resource_id: 'resource-1',
        path: '/src/utils.ts',
        name: 'utils.ts',
        language: 'typescript',
        content: 'export const add = (a, b) => a + b;',
        size: 512,
        lines: 5,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      // Open file1 and scroll
      useEditorStore.getState().setActiveFile(file1);
      useEditorStore.getState().updateScrollPosition(300);

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      // Switch to file2
      useEditorStore.getState().setActiveFile(file2);
      expect(useEditorStore.getState().scrollPosition).toBe(0);

      // Switch back to file1
      useEditorStore.getState().setActiveFile(file1);
      expect(useEditorStore.getState().scrollPosition).toBe(300);
    });

    it('should persist scroll positions to localStorage', async () => {
      const mockFile: CodeFile = {
        id: 'file-1',
        resource_id: 'resource-1',
        path: '/src/main.ts',
        name: 'main.ts',
        language: 'typescript',
        content: 'console.log("hello");',
        size: 1024,
        lines: 10,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useEditorStore.getState().setActiveFile(mockFile);
      useEditorStore.getState().updateScrollPosition(750);

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      const stored = localStorage.getItem('editor-storage');
      expect(stored).toBeTruthy();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.scrollPositions['file-1']).toBe(750);
      }
    });

    it('should restore scroll position using restoreScrollPosition', () => {
      useEditorStore.setState({
        scrollPositions: {
          'file-1': 100,
          'file-2': 200,
          'file-3': 300,
        },
      });

      expect(useEditorStore.getState().restoreScrollPosition('file-1')).toBe(100);
      expect(useEditorStore.getState().restoreScrollPosition('file-2')).toBe(200);
      expect(useEditorStore.getState().restoreScrollPosition('file-3')).toBe(300);
      expect(useEditorStore.getState().restoreScrollPosition('file-4')).toBe(0);
    });
  });
});
