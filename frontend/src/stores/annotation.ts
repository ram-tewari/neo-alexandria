/**
 * Annotation Store
 * 
 * Simplified Zustand store for annotation UI state.
 * Data fetching and mutations are handled by TanStack Query hooks in useEditorData.ts
 * 
 * This store only manages:
 * - Selected annotation ID (for highlighting)
 * - Pending selection (for annotation creation)
 * - UI state (creating mode)
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 6.3 - Update annotation store to use real data
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.9, 4.10
 */

import { create } from 'zustand';

interface AnnotationState {
  // Selected annotation ID (for highlighting in editor)
  selectedAnnotationId: string | null;
  
  // UI state for annotation creation
  isCreating: boolean;
  
  // Pending selection for annotation creation
  pendingSelection: {
    startOffset: number;
    endOffset: number;
    highlightedText: string;
  } | null;
  
  // Actions
  selectAnnotation: (id: string | null) => void;
  setIsCreating: (isCreating: boolean) => void;
  setPendingSelection: (selection: { startOffset: number; endOffset: number; highlightedText: string } | null) => void;
  clearSelection: () => void;
}

export const useAnnotationStore = create<AnnotationState>((set) => ({
  // Initial state
  selectedAnnotationId: null,
  isCreating: false,
  pendingSelection: null,
  
  // Select annotation by ID
  selectAnnotation: (id: string | null) =>
    set({ selectedAnnotationId: id }),
  
  // Set creating state
  setIsCreating: (isCreating: boolean) =>
    set({ isCreating }),
  
  // Set pending selection for annotation creation
  setPendingSelection: (selection: { startOffset: number; endOffset: number; highlightedText: string } | null) =>
    set({ 
      pendingSelection: selection, 
      isCreating: selection !== null 
    }),
  
  // Clear all selection state
  clearSelection: () =>
    set({ 
      selectedAnnotationId: null, 
      isCreating: false, 
      pendingSelection: null 
    }),
}));
