import { describe, it, expect, beforeEach } from 'vitest';
import { useAnnotationStore } from '../annotation';

/**
 * Unit Tests for Annotation Store
 * 
 * Feature: phase2.5-backend-api-integration
 * Task: 6.3 - Update annotation store to use real data
 * Tests simplified UI state management (data fetching moved to TanStack Query)
 * Validates: Requirements 4.1, 4.2, 4.3, 4.4
 */

describe('Annotation Store', () => {
  beforeEach(() => {
    // Reset store to initial state
    useAnnotationStore.setState({
      selectedAnnotationId: null,
      isCreating: false,
      pendingSelection: null,
    });
  });

  describe('Selection State Management', () => {
    it('should select annotation by id', () => {
      useAnnotationStore.getState().selectAnnotation('annotation-1');
      expect(useAnnotationStore.getState().selectedAnnotationId).toBe('annotation-1');
    });

    it('should clear selected annotation', () => {
      useAnnotationStore.getState().selectAnnotation('annotation-1');
      useAnnotationStore.getState().selectAnnotation(null);
      expect(useAnnotationStore.getState().selectedAnnotationId).toBeNull();
    });

    it('should set creating state', () => {
      useAnnotationStore.getState().setIsCreating(true);
      expect(useAnnotationStore.getState().isCreating).toBe(true);

      useAnnotationStore.getState().setIsCreating(false);
      expect(useAnnotationStore.getState().isCreating).toBe(false);
    });
  });

  describe('Pending Selection Management', () => {
    it('should set pending selection', () => {
      const selection = {
        startOffset: 0,
        endOffset: 10,
        highlightedText: 'hello world',
      };

      useAnnotationStore.getState().setPendingSelection(selection);

      expect(useAnnotationStore.getState().pendingSelection).toEqual(selection);
      expect(useAnnotationStore.getState().isCreating).toBe(true);
    });

    it('should clear pending selection', () => {
      const selection = {
        startOffset: 0,
        endOffset: 10,
        highlightedText: 'hello world',
      };

      useAnnotationStore.getState().setPendingSelection(selection);
      useAnnotationStore.getState().setPendingSelection(null);

      expect(useAnnotationStore.getState().pendingSelection).toBeNull();
      expect(useAnnotationStore.getState().isCreating).toBe(false);
    });

    it('should set isCreating to true when setting pending selection', () => {
      const selection = {
        startOffset: 0,
        endOffset: 10,
        highlightedText: 'hello world',
      };

      useAnnotationStore.getState().setPendingSelection(selection);
      expect(useAnnotationStore.getState().isCreating).toBe(true);
    });

    it('should set isCreating to false when clearing pending selection', () => {
      const selection = {
        startOffset: 0,
        endOffset: 10,
        highlightedText: 'hello world',
      };

      useAnnotationStore.getState().setPendingSelection(selection);
      useAnnotationStore.getState().setPendingSelection(null);
      expect(useAnnotationStore.getState().isCreating).toBe(false);
    });
  });

  describe('Clear Selection', () => {
    it('should clear all selection state', () => {
      const selection = {
        startOffset: 0,
        endOffset: 10,
        highlightedText: 'hello world',
      };

      useAnnotationStore.getState().selectAnnotation('annotation-1');
      useAnnotationStore.getState().setPendingSelection(selection);

      useAnnotationStore.getState().clearSelection();

      expect(useAnnotationStore.getState().selectedAnnotationId).toBeNull();
      expect(useAnnotationStore.getState().isCreating).toBe(false);
      expect(useAnnotationStore.getState().pendingSelection).toBeNull();
    });
  });
});
