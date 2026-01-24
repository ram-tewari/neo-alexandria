/**
 * Error Handling Tests for Editor Stores
 * 
 * Tests error handling and fallback behavior for:
 * - Annotation store (cached data fallback)
 * - Chunk store (line-based fallback)
 * - Quality store (badge hiding)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAnnotationStore } from '../annotation';
import { useChunkStore } from '../chunk';
import { useQualityStore } from '../quality';
import { editorApi } from '@/lib/api/editor';
import type { Annotation, SemanticChunk, QualityDetails } from '@/features/editor/types';

// Mock the API client
vi.mock('@/lib/api/editor', () => ({
  editorApi: {
    getAnnotations: vi.fn(),
    createAnnotation: vi.fn(),
    updateAnnotation: vi.fn(),
    deleteAnnotation: vi.fn(),
    getChunks: vi.fn(),
    getQualityDetails: vi.fn(),
  },
}));

describe('Annotation Store Error Handling', () => {
  beforeEach(() => {
    // Reset store state
    useAnnotationStore.setState({
      annotations: [],
      selectedAnnotation: null,
      annotationCache: {},
      isCreating: false,
      isLoading: false,
      error: null,
      usingCachedData: false,
    });
    
    // Clear all mocks
    vi.clearAllMocks();
  });

  it('should use cached data when API fails', async () => {
    const resourceId = 'resource-1';
    const cachedAnnotations: Annotation[] = [
      {
        id: 'ann-1',
        resource_id: resourceId,
        user_id: 'user-1',
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'cached text',
        color: '#3b82f6',
        is_shared: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];
    
    // Set up cache
    useAnnotationStore.getState().setCachedAnnotations(resourceId, cachedAnnotations);
    
    // Mock API failure
    vi.mocked(editorApi.getAnnotations).mockRejectedValue(
      new Error('Network error')
    );
    
    // Fetch annotations (should use cache)
    await useAnnotationStore.getState().fetchAnnotations(resourceId);
    
    const state = useAnnotationStore.getState();
    expect(state.annotations).toEqual(cachedAnnotations);
    expect(state.usingCachedData).toBe(true);
    expect(state.error).toContain('cached data');
    expect(state.isLoading).toBe(false);
  });

  it('should show error when API fails and no cache available', async () => {
    const resourceId = 'resource-2';
    
    // Mock API failure
    vi.mocked(editorApi.getAnnotations).mockRejectedValue(
      new Error('Network error')
    );
    
    // Fetch annotations (no cache)
    await useAnnotationStore.getState().fetchAnnotations(resourceId);
    
    const state = useAnnotationStore.getState();
    expect(state.annotations).toEqual([]);
    expect(state.usingCachedData).toBe(false);
    expect(state.error).toBeTruthy();
    expect(state.error).toContain('Network error');
    expect(state.isLoading).toBe(false);
  });

  it('should rollback optimistic update on create failure', async () => {
    const resourceId = 'resource-1';
    const annotationData = {
      start_offset: 0,
      end_offset: 10,
      highlighted_text: 'test text',
    };
    
    // Mock API failure
    vi.mocked(editorApi.createAnnotation).mockRejectedValue(
      new Error('Create failed')
    );
    
    // Try to create annotation
    await expect(
      useAnnotationStore.getState().createAnnotation(resourceId, annotationData)
    ).rejects.toThrow();
    
    const state = useAnnotationStore.getState();
    expect(state.annotations).toEqual([]); // Optimistic annotation removed
    expect(state.error).toBeTruthy();
    expect(state.error).toContain('Create failed');
  });

  it('should rollback optimistic update on update failure', async () => {
    const annotation: Annotation = {
      id: 'ann-1',
      resource_id: 'resource-1',
      user_id: 'user-1',
      start_offset: 0,
      end_offset: 10,
      highlighted_text: 'original text',
      note: 'original note',
      color: '#3b82f6',
      is_shared: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };
    
    // Set up initial state
    useAnnotationStore.setState({ annotations: [annotation] });
    
    // Mock API failure
    vi.mocked(editorApi.updateAnnotation).mockRejectedValue(
      new Error('Update failed')
    );
    
    // Try to update annotation
    await expect(
      useAnnotationStore.getState().updateAnnotation('ann-1', { note: 'new note' })
    ).rejects.toThrow();
    
    const state = useAnnotationStore.getState();
    expect(state.annotations[0].note).toBe('original note'); // Rolled back
    expect(state.error).toBeTruthy();
    expect(state.error).toContain('Update failed');
  });

  it('should rollback optimistic delete on failure', async () => {
    const annotation: Annotation = {
      id: 'ann-1',
      resource_id: 'resource-1',
      user_id: 'user-1',
      start_offset: 0,
      end_offset: 10,
      highlighted_text: 'text',
      color: '#3b82f6',
      is_shared: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };
    
    // Set up initial state
    useAnnotationStore.setState({ annotations: [annotation] });
    
    // Mock API failure
    vi.mocked(editorApi.deleteAnnotation).mockRejectedValue(
      new Error('Delete failed')
    );
    
    // Try to delete annotation
    await expect(
      useAnnotationStore.getState().deleteAnnotation('ann-1')
    ).rejects.toThrow();
    
    const state = useAnnotationStore.getState();
    expect(state.annotations).toHaveLength(1); // Annotation restored
    expect(state.annotations[0]).toEqual(annotation);
    expect(state.error).toBeTruthy();
    expect(state.error).toContain('Delete failed');
  });

  it('should support retry functionality', async () => {
    const resourceId = 'resource-1';
    
    // First call fails
    vi.mocked(editorApi.getAnnotations).mockRejectedValueOnce(
      new Error('Network error')
    );
    
    // Second call succeeds
    vi.mocked(editorApi.getAnnotations).mockResolvedValueOnce({
      data: [],
    } as any);
    
    // First attempt fails
    await useAnnotationStore.getState().fetchAnnotations(resourceId);
    expect(useAnnotationStore.getState().error).toBeTruthy();
    
    // Retry succeeds
    await useAnnotationStore.getState().retryLastOperation();
    expect(useAnnotationStore.getState().error).toBe(null);
  });
});

describe('Chunk Store Error Handling', () => {
  beforeEach(() => {
    // Reset store state
    useChunkStore.setState({
      chunks: [],
      selectedChunk: null,
      chunkCache: {},
      chunkVisibility: true,
      isLoading: false,
      error: null,
      usingFallback: false,
    });
    
    // Clear all mocks
    vi.clearAllMocks();
  });

  it('should use line-based fallback when API fails', async () => {
    const resourceId = 'resource-1';
    const fileContent = 'line 1\nline 2\nline 3\nline 4\nline 5';
    const language = 'typescript';
    
    // Mock API failure
    vi.mocked(editorApi.getChunks).mockRejectedValue(
      new Error('Chunking failed')
    );
    
    // Fetch chunks with fallback data
    await useChunkStore.getState().fetchChunks(resourceId, fileContent, language);
    
    const state = useChunkStore.getState();
    expect(state.chunks.length).toBeGreaterThan(0); // Fallback chunks generated
    expect(state.usingFallback).toBe(true);
    expect(state.error).toContain('line-based display');
    expect(state.isLoading).toBe(false);
    
    // Verify fallback chunk structure
    const firstChunk = state.chunks[0];
    expect(firstChunk.id).toContain('fallback');
    expect(firstChunk.chunk_metadata.language).toBe(language);
  });

  it('should show error when API fails and no fallback available', async () => {
    const resourceId = 'resource-2';
    
    // Mock API failure
    vi.mocked(editorApi.getChunks).mockRejectedValue(
      new Error('Chunking failed')
    );
    
    // Fetch chunks without fallback data
    await useChunkStore.getState().fetchChunks(resourceId);
    
    const state = useChunkStore.getState();
    expect(state.chunks).toEqual([]);
    expect(state.usingFallback).toBe(false);
    expect(state.error).toBeTruthy();
    expect(state.error).toContain('Chunking failed');
    expect(state.isLoading).toBe(false);
  });

  it('should generate correct line-based chunks', async () => {
    const resourceId = 'resource-1';
    const lines = Array.from({ length: 100 }, (_, i) => `line ${i + 1}`);
    const fileContent = lines.join('\n');
    const language = 'python';
    
    // Mock API failure
    vi.mocked(editorApi.getChunks).mockRejectedValue(
      new Error('Chunking failed')
    );
    
    // Fetch chunks
    await useChunkStore.getState().fetchChunks(resourceId, fileContent, language);
    
    const state = useChunkStore.getState();
    
    // Should have 2 chunks (50 lines each)
    expect(state.chunks).toHaveLength(2);
    
    // First chunk: lines 1-50
    expect(state.chunks[0].chunk_metadata.start_line).toBe(1);
    expect(state.chunks[0].chunk_metadata.end_line).toBe(50);
    
    // Second chunk: lines 51-100
    expect(state.chunks[1].chunk_metadata.start_line).toBe(51);
    expect(state.chunks[1].chunk_metadata.end_line).toBe(100);
  });

  it('should support retry functionality', async () => {
    const resourceId = 'resource-1';
    
    // First call fails
    vi.mocked(editorApi.getChunks).mockRejectedValueOnce(
      new Error('Network error')
    );
    
    // Second call succeeds
    vi.mocked(editorApi.getChunks).mockResolvedValueOnce({
      data: [],
    } as any);
    
    // First attempt fails
    await useChunkStore.getState().fetchChunks(resourceId);
    expect(useChunkStore.getState().error).toBeTruthy();
    
    // Retry succeeds
    await useChunkStore.getState().retryLastOperation();
    expect(useChunkStore.getState().error).toBe(null);
  });
});

describe('Quality Store Error Handling', () => {
  beforeEach(() => {
    // Reset store state
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

  it('should hide badges when API fails', async () => {
    const resourceId = 'resource-1';
    
    // Mock API failure
    vi.mocked(editorApi.getQualityDetails).mockRejectedValue(
      new Error('Quality fetch failed')
    );
    
    // Fetch quality data
    await useQualityStore.getState().fetchQualityData(resourceId);
    
    const state = useQualityStore.getState();
    expect(state.qualityData).toBe(null);
    expect(state.hideBadgesDueToError).toBe(true);
    expect(state.error).toBeTruthy();
    expect(state.error).toContain('Quality fetch failed');
    expect(state.isLoading).toBe(false);
  });

  it('should clear error flag when manually toggling badges', () => {
    // Set error state
    useQualityStore.setState({
      error: 'Some error',
      hideBadgesDueToError: true,
      badgeVisibility: false,
    });
    
    // Toggle badges
    useQualityStore.getState().toggleBadgeVisibility();
    
    const state = useQualityStore.getState();
    expect(state.hideBadgesDueToError).toBe(false);
    expect(state.badgeVisibility).toBe(true);
  });

  it('should clear error flag when manually setting badge visibility', () => {
    // Set error state
    useQualityStore.setState({
      error: 'Some error',
      hideBadgesDueToError: true,
    });
    
    // Set badge visibility
    useQualityStore.getState().setBadgeVisibility(true);
    
    const state = useQualityStore.getState();
    expect(state.hideBadgesDueToError).toBe(false);
  });

  it('should support retry functionality', async () => {
    const resourceId = 'resource-1';
    const qualityData: QualityDetails = {
      resource_id: resourceId,
      quality_dimensions: {
        accuracy: 0.9,
        completeness: 0.8,
        consistency: 0.85,
        timeliness: 0.7,
        relevance: 0.95,
      },
      quality_overall: 0.85,
      quality_weights: {
        accuracy: 0.3,
        completeness: 0.2,
        consistency: 0.2,
        timeliness: 0.15,
        relevance: 0.15,
      },
      quality_last_computed: '2024-01-01T00:00:00Z',
      is_quality_outlier: false,
      needs_quality_review: false,
    };
    
    // First call fails
    vi.mocked(editorApi.getQualityDetails).mockRejectedValueOnce(
      new Error('Network error')
    );
    
    // Second call succeeds
    vi.mocked(editorApi.getQualityDetails).mockResolvedValueOnce({
      data: qualityData,
    } as any);
    
    // First attempt fails
    await useQualityStore.getState().fetchQualityData(resourceId);
    expect(useQualityStore.getState().error).toBeTruthy();
    expect(useQualityStore.getState().hideBadgesDueToError).toBe(true);
    
    // Retry succeeds
    await useQualityStore.getState().retryLastOperation();
    expect(useQualityStore.getState().error).toBe(null);
    expect(useQualityStore.getState().hideBadgesDueToError).toBe(false);
    expect(useQualityStore.getState().qualityData).toEqual(qualityData);
  });

  it('should use cached data when available', async () => {
    const resourceId = 'resource-1';
    const qualityData: QualityDetails = {
      resource_id: resourceId,
      quality_dimensions: {
        accuracy: 0.9,
        completeness: 0.8,
        consistency: 0.85,
        timeliness: 0.7,
        relevance: 0.95,
      },
      quality_overall: 0.85,
      quality_weights: {
        accuracy: 0.3,
        completeness: 0.2,
        consistency: 0.2,
        timeliness: 0.15,
        relevance: 0.15,
      },
      quality_last_computed: '2024-01-01T00:00:00Z',
      is_quality_outlier: false,
      needs_quality_review: false,
    };
    
    // Set up cache
    useQualityStore.getState().setCachedQuality(resourceId, qualityData);
    
    // Fetch quality data (should use cache, no API call)
    await useQualityStore.getState().fetchQualityData(resourceId);
    
    const state = useQualityStore.getState();
    expect(state.qualityData).toEqual(qualityData);
    expect(state.hideBadgesDueToError).toBe(false);
    expect(editorApi.getQualityDetails).not.toHaveBeenCalled();
  });
});
