import { describe, it, expect, beforeEach } from 'vitest';
import { useAnnotationStore } from '../annotation';
import type { Annotation, AnnotationCreate, AnnotationUpdate } from '@/features/editor/types';

/**
 * Unit Tests for Annotation Store
 * 
 * Feature: phase2-living-code-editor
 * Tests state updates, CRUD operations, and optimistic updates
 * Validates: Requirements 4.1, 4.6, 4.7
 */

describe('Annotation Store', () => {
  beforeEach(() => {
    // Reset store to initial state
    useAnnotationStore.setState({
      annotations: [],
      selectedAnnotation: null,
      isCreating: false,
      isLoading: false,
      error: null,
    });
  });

  describe('Basic State Management', () => {
    it('should set annotations', () => {
      const mockAnnotations: Annotation[] = [
        {
          id: '1',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'hello world',
          note: 'Test note',
          color: '#3b82f6',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      useAnnotationStore.getState().setAnnotations(mockAnnotations);

      expect(useAnnotationStore.getState().annotations).toEqual(mockAnnotations);
    });

    it('should select annotation by id', () => {
      const mockAnnotations: Annotation[] = [
        {
          id: '1',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'hello world',
          color: '#3b82f6',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
        {
          id: '2',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 20,
          end_offset: 30,
          highlighted_text: 'test',
          color: '#ef4444',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      useAnnotationStore.getState().setAnnotations(mockAnnotations);
      useAnnotationStore.getState().selectAnnotation('1');

      expect(useAnnotationStore.getState().selectedAnnotation).toEqual(mockAnnotations[0]);
    });

    it('should clear selected annotation', () => {
      const mockAnnotations: Annotation[] = [
        {
          id: '1',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'hello world',
          color: '#3b82f6',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      useAnnotationStore.getState().setAnnotations(mockAnnotations);
      useAnnotationStore.getState().selectAnnotation('1');
      useAnnotationStore.getState().selectAnnotation(null);

      expect(useAnnotationStore.getState().selectedAnnotation).toBeNull();
    });

    it('should set creating state', () => {
      useAnnotationStore.getState().setIsCreating(true);
      expect(useAnnotationStore.getState().isCreating).toBe(true);

      useAnnotationStore.getState().setIsCreating(false);
      expect(useAnnotationStore.getState().isCreating).toBe(false);
    });
  });

  describe('Optimistic Updates', () => {
    it('should add annotation optimistically', () => {
      const mockAnnotation: Annotation = {
        id: '1',
        resource_id: 'resource-1',
        user_id: 'user-1',
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'hello world',
        color: '#3b82f6',
        is_shared: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useAnnotationStore.getState().addAnnotationOptimistic(mockAnnotation);

      expect(useAnnotationStore.getState().annotations).toHaveLength(1);
      expect(useAnnotationStore.getState().annotations[0]).toEqual(mockAnnotation);
    });

    it('should update annotation optimistically', () => {
      const mockAnnotation: Annotation = {
        id: '1',
        resource_id: 'resource-1',
        user_id: 'user-1',
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'hello world',
        note: 'Original note',
        color: '#3b82f6',
        is_shared: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useAnnotationStore.getState().addAnnotationOptimistic(mockAnnotation);
      useAnnotationStore.getState().updateAnnotationOptimistic('1', {
        note: 'Updated note',
      });

      const updated = useAnnotationStore.getState().annotations[0];
      expect(updated.note).toBe('Updated note');
    });

    it('should remove annotation optimistically', () => {
      const mockAnnotations: Annotation[] = [
        {
          id: '1',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 0,
          end_offset: 10,
          highlighted_text: 'hello world',
          color: '#3b82f6',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
        {
          id: '2',
          resource_id: 'resource-1',
          user_id: 'user-1',
          start_offset: 20,
          end_offset: 30,
          highlighted_text: 'test',
          color: '#ef4444',
          is_shared: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      useAnnotationStore.getState().setAnnotations(mockAnnotations);
      useAnnotationStore.getState().removeAnnotationOptimistic('1');

      expect(useAnnotationStore.getState().annotations).toHaveLength(1);
      expect(useAnnotationStore.getState().annotations[0].id).toBe('2');
    });

    it('should clear selected annotation when removed', () => {
      const mockAnnotation: Annotation = {
        id: '1',
        resource_id: 'resource-1',
        user_id: 'user-1',
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'hello world',
        color: '#3b82f6',
        is_shared: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useAnnotationStore.getState().addAnnotationOptimistic(mockAnnotation);
      useAnnotationStore.getState().selectAnnotation('1');
      useAnnotationStore.getState().removeAnnotationOptimistic('1');

      expect(useAnnotationStore.getState().selectedAnnotation).toBeNull();
    });
  });

  describe('CRUD Operations', () => {
    it('should create annotation with optimistic update', async () => {
      const createData: AnnotationCreate = {
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'hello world',
        note: 'Test note',
        color: '#3b82f6',
      };

      await useAnnotationStore.getState().createAnnotation('resource-1', createData);

      const annotations = useAnnotationStore.getState().annotations;
      expect(annotations).toHaveLength(1);
      expect(annotations[0].highlighted_text).toBe('hello world');
      expect(annotations[0].note).toBe('Test note');
    });

    it('should update annotation with optimistic update', async () => {
      const mockAnnotation: Annotation = {
        id: '1',
        resource_id: 'resource-1',
        user_id: 'user-1',
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'hello world',
        note: 'Original note',
        color: '#3b82f6',
        is_shared: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useAnnotationStore.getState().addAnnotationOptimistic(mockAnnotation);

      const updateData: AnnotationUpdate = {
        note: 'Updated note',
      };

      await useAnnotationStore.getState().updateAnnotation('1', updateData);

      const updated = useAnnotationStore.getState().annotations[0];
      expect(updated.note).toBe('Updated note');
    });

    it('should delete annotation with optimistic update', async () => {
      const mockAnnotation: Annotation = {
        id: '1',
        resource_id: 'resource-1',
        user_id: 'user-1',
        start_offset: 0,
        end_offset: 10,
        highlighted_text: 'hello world',
        color: '#3b82f6',
        is_shared: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      useAnnotationStore.getState().addAnnotationOptimistic(mockAnnotation);
      await useAnnotationStore.getState().deleteAnnotation('1');

      expect(useAnnotationStore.getState().annotations).toHaveLength(0);
    });

    it('should fetch annotations', async () => {
      await useAnnotationStore.getState().fetchAnnotations('resource-1');

      expect(useAnnotationStore.getState().isLoading).toBe(false);
      expect(useAnnotationStore.getState().annotations).toEqual([]);
    });
  });
});
