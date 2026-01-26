import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useChunkStore } from '../chunk';
import type { SemanticChunk } from '@/features/editor/types';

/**
 * Unit Tests for Chunk Store
 * 
 * Feature: phase2.5-backend-api-integration
 * Tests state updates and visibility toggles
 * Validates: Requirements 3.2, 3.3, 3.5, 3.6
 * 
 * Note: Data fetching is now handled by TanStack Query hooks (useChunks)
 * The store only manages UI state and chunk selection
 */

describe('Chunk Store', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset store to initial state
    useChunkStore.setState({
      chunks: [],
      selectedChunk: null,
      chunkVisibility: true,
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Basic State Management', () => {
    it('should set chunks', () => {
      const mockChunks: SemanticChunk[] = [
        {
          id: '1',
          resource_id: 'resource-1',
          content: 'function hello() { return "world"; }',
          chunk_index: 0,
          chunk_metadata: {
            function_name: 'hello',
            start_line: 1,
            end_line: 3,
            language: 'typescript',
          },
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      useChunkStore.getState().setChunks(mockChunks);

      expect(useChunkStore.getState().chunks).toEqual(mockChunks);
    });

    it('should select chunk by id', () => {
      const mockChunks: SemanticChunk[] = [
        {
          id: '1',
          resource_id: 'resource-1',
          content: 'function hello() { return "world"; }',
          chunk_index: 0,
          chunk_metadata: {
            function_name: 'hello',
            start_line: 1,
            end_line: 3,
            language: 'typescript',
          },
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: '2',
          resource_id: 'resource-1',
          content: 'function goodbye() { return "world"; }',
          chunk_index: 1,
          chunk_metadata: {
            function_name: 'goodbye',
            start_line: 5,
            end_line: 7,
            language: 'typescript',
          },
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      useChunkStore.getState().setChunks(mockChunks);
      useChunkStore.getState().selectChunk('1');

      expect(useChunkStore.getState().selectedChunk).toEqual(mockChunks[0]);
    });

    it('should clear selected chunk', () => {
      const mockChunks: SemanticChunk[] = [
        {
          id: '1',
          resource_id: 'resource-1',
          content: 'function hello() { return "world"; }',
          chunk_index: 0,
          chunk_metadata: {
            function_name: 'hello',
            start_line: 1,
            end_line: 3,
            language: 'typescript',
          },
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      useChunkStore.getState().setChunks(mockChunks);
      useChunkStore.getState().selectChunk('1');
      useChunkStore.getState().selectChunk(null);

      expect(useChunkStore.getState().selectedChunk).toBeNull();
    });

    it('should clear all chunks', () => {
      const mockChunks: SemanticChunk[] = [
        {
          id: '1',
          resource_id: 'resource-1',
          content: 'function hello() { return "world"; }',
          chunk_index: 0,
          chunk_metadata: {
            function_name: 'hello',
            start_line: 1,
            end_line: 3,
            language: 'typescript',
          },
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      useChunkStore.getState().setChunks(mockChunks);
      useChunkStore.getState().selectChunk('1');
      useChunkStore.getState().clearChunks();

      expect(useChunkStore.getState().chunks).toEqual([]);
      expect(useChunkStore.getState().selectedChunk).toBeNull();
    });
  });

  describe('Chunk Visibility', () => {
    it('should toggle chunk visibility', () => {
      expect(useChunkStore.getState().chunkVisibility).toBe(true);

      useChunkStore.getState().toggleChunkVisibility();
      expect(useChunkStore.getState().chunkVisibility).toBe(false);

      useChunkStore.getState().toggleChunkVisibility();
      expect(useChunkStore.getState().chunkVisibility).toBe(true);
    });

    it('should set chunk visibility', () => {
      useChunkStore.getState().setChunkVisibility(false);
      expect(useChunkStore.getState().chunkVisibility).toBe(false);

      useChunkStore.getState().setChunkVisibility(true);
      expect(useChunkStore.getState().chunkVisibility).toBe(true);
    });

    it('should persist chunk visibility to localStorage', async () => {
      useChunkStore.getState().setChunkVisibility(false);

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      const stored = localStorage.getItem('chunk-storage');
      expect(stored).toBeTruthy();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.chunkVisibility).toBe(false);
      }
    });
  });
});
