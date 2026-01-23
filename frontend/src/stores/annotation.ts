import { create } from 'zustand';
import type {
  Annotation,
  AnnotationCreate,
  AnnotationUpdate,
} from '@/features/editor/types';

interface AnnotationState {
  // Annotation data
  annotations: Annotation[];
  selectedAnnotation: Annotation | null;
  
  // UI state
  isCreating: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setAnnotations: (annotations: Annotation[]) => void;
  selectAnnotation: (id: string | null) => void;
  setIsCreating: (isCreating: boolean) => void;
  
  // CRUD operations (will be connected to API in Task 3)
  fetchAnnotations: (resourceId: string) => Promise<void>;
  createAnnotation: (resourceId: string, data: AnnotationCreate) => Promise<void>;
  updateAnnotation: (id: string, data: AnnotationUpdate) => Promise<void>;
  deleteAnnotation: (id: string) => Promise<void>;
  
  // Optimistic updates
  addAnnotationOptimistic: (annotation: Annotation) => void;
  updateAnnotationOptimistic: (id: string, data: Partial<Annotation>) => void;
  removeAnnotationOptimistic: (id: string) => void;
}

export const useAnnotationStore = create<AnnotationState>((set, get) => ({
  // Initial state
  annotations: [],
  selectedAnnotation: null,
  isCreating: false,
  isLoading: false,
  error: null,
  
  // Set annotations
  setAnnotations: (annotations: Annotation[]) =>
    set({ annotations }),
  
  // Select annotation
  selectAnnotation: (id: string | null) => {
    if (id === null) {
      set({ selectedAnnotation: null });
    } else {
      const annotation = get().annotations.find((a) => a.id === id);
      set({ selectedAnnotation: annotation || null });
    }
  },
  
  // Set creating state
  setIsCreating: (isCreating: boolean) =>
    set({ isCreating }),
  
  // Fetch annotations for a resource
  fetchAnnotations: async (resourceId: string) => {
    set({ isLoading: true, error: null });
    
    try {
      // TODO: Replace with actual API call in Task 3
      // const response = await editorApi.getAnnotations(resourceId);
      // set({ annotations: response.data, isLoading: false });
      
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 300));
      
      // Mock data for now
      set({
        annotations: [],
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch annotations',
        isLoading: false,
      });
    }
  },
  
  // Create annotation with optimistic update
  createAnnotation: async (resourceId: string, data: AnnotationCreate) => {
    // Create optimistic annotation
    const optimisticAnnotation: Annotation = {
      id: `temp-${Date.now()}`,
      resource_id: resourceId,
      user_id: 'current-user', // TODO: Get from auth context
      ...data,
      color: data.color || '#3b82f6',
      is_shared: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    // Add optimistically
    get().addAnnotationOptimistic(optimisticAnnotation);
    
    try {
      // TODO: Replace with actual API call in Task 3
      // const response = await editorApi.createAnnotation(resourceId, data);
      // Replace optimistic annotation with real one
      // set((state) => ({
      //   annotations: state.annotations.map((a) =>
      //     a.id === optimisticAnnotation.id ? response.data : a
      //   ),
      // }));
      
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 300));
      
      // For now, just keep the optimistic annotation
    } catch (error) {
      // Remove optimistic annotation on error
      get().removeAnnotationOptimistic(optimisticAnnotation.id);
      
      set({
        error: error instanceof Error ? error.message : 'Failed to create annotation',
      });
      throw error;
    }
  },
  
  // Update annotation with optimistic update
  updateAnnotation: async (id: string, data: AnnotationUpdate) => {
    // Store original for rollback
    const original = get().annotations.find((a) => a.id === id);
    if (!original) return;
    
    // Update optimistically
    get().updateAnnotationOptimistic(id, {
      ...data,
      updated_at: new Date().toISOString(),
    });
    
    try {
      // TODO: Replace with actual API call in Task 3
      // const response = await editorApi.updateAnnotation(id, data);
      // set((state) => ({
      //   annotations: state.annotations.map((a) =>
      //     a.id === id ? response.data : a
      //   ),
      // }));
      
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 300));
    } catch (error) {
      // Rollback on error
      get().updateAnnotationOptimistic(id, original);
      
      set({
        error: error instanceof Error ? error.message : 'Failed to update annotation',
      });
      throw error;
    }
  },
  
  // Delete annotation with optimistic update
  deleteAnnotation: async (id: string) => {
    // Store original for rollback
    const original = get().annotations.find((a) => a.id === id);
    if (!original) return;
    
    // Remove optimistically
    get().removeAnnotationOptimistic(id);
    
    try {
      // TODO: Replace with actual API call in Task 3
      // await editorApi.deleteAnnotation(id);
      
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 300));
    } catch (error) {
      // Rollback on error
      get().addAnnotationOptimistic(original);
      
      set({
        error: error instanceof Error ? error.message : 'Failed to delete annotation',
      });
      throw error;
    }
  },
  
  // Optimistic update helpers
  addAnnotationOptimistic: (annotation: Annotation) =>
    set((state) => ({
      annotations: [...state.annotations, annotation],
    })),
  
  updateAnnotationOptimistic: (id: string, data: Partial<Annotation>) =>
    set((state) => ({
      annotations: state.annotations.map((a) =>
        a.id === id ? { ...a, ...data } : a
      ),
    })),
  
  removeAnnotationOptimistic: (id: string) =>
    set((state) => ({
      annotations: state.annotations.filter((a) => a.id !== id),
      selectedAnnotation:
        state.selectedAnnotation?.id === id ? null : state.selectedAnnotation,
    })),
}));
