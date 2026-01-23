import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useEditorStore } from '../editor';
import type { CodeFile } from '@/features/editor/types';

/**
 * Unit Tests for Editor Store
 * 
 * Feature: phase2-living-code-editor
 * Tests state updates, actions, and persistence logic
 * Validates: Requirements 9.1, 9.2
 */

describe('Editor Store', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset store to initial state
    useEditorStore.setState({
      activeFile: null,
      cursorPosition: { line: 1, column: 1 },
      selection: null,
      scrollPosition: 0,
      scrollPositions: {},
    });
  });

  afterEach(() => {
    localStorage.clear();
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
