import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useChunkStore } from '../chunk';
import type { SemanticChunk } from '@/features/editor/types';

/**
 * Unit Tests for Chunk Store
 * 
 * Feature: phase2-living-code-editor
 * Tests state updates, caching logic, and visibility toggles
 * Validates: Requirements 2.1, 2.4
 */

describe('Chunk Store', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset store to initial state
    useChunkStore.setState({
      chunks: [],
      selectedChunk: null,
      chunkCache: {},
      chunkVisibility: true,
      isLoading: false,
      error: null,
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

  describe('Chunk Caching', () => {
    it('should cache chunks for a resource', () => {
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

      useChunkStore.getState().setCachedChunks('resource-1', mockChunks);

      const cached = useChunkStore.getState().getCachedChunks('resource-1');
      expect(cached).toEqual(mockChunks);
    });

    it('should return null for uncached resource', () => {
      const cached = useChunkStore.getState().getCachedChunks('resource-999');
      expect(cached).toBeNull();
    });

    it('should clear all cached chunks', () => {
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

      useChunkStore.getState().setCachedChunks('resource-1', mockChunks);
      useChunkStore.getState().setCachedChunks('resource-2', mockChunks);
      useChunkStore.getState().clearCache();

      expect(useChunkStore.getState().chunkCache).toEqual({});
    });

    it('should persist chunk cache to localStorage', async () => {
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

      useChunkStore.getState().setCachedChunks('resource-1', mockChunks);

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      const stored = localStorage.getItem('chunk-storage');
      expect(stored).toBeTruthy();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.chunkCache['resource-1']).toEqual(mockChunks);
      }
    });
  });

  describe('Fetch Chunks', () => {
    it('should fetch chunks and update state', async () => {
      await useChunkStore.getState().fetchChunks('resource-1');

      expect(useChunkStore.getState().isLoading).toBe(false);
      expect(useChunkStore.getState().chunks).toEqual([]);
    });

    it('should use cached chunks if available', async () => {
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

      useChunkStore.getState().setCachedChunks('resource-1', mockChunks);
      await useChunkStore.getState().fetchChunks('resource-1');

      expect(useChunkStore.getState().chunks).toEqual(mockChunks);
      expect(useChunkStore.getState().isLoading).toBe(false);
    });
  });
});
