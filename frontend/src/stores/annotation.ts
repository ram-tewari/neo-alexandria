import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  Annotation,
  AnnotationCreate,
  AnnotationUpdate,
} from '@/features/editor/types';
import { editorApi } from '@/lib/api/editor';

interface AnnotationState {
  // Annotation data
  annotations: Annotation[];
  selectedAnnotation: Annotation | null;
  
  // Cache for offline/fallback support (resourceId -> annotations)
  annotationCache: Record<string, Annotation[]>;
  
  // UI state
  isCreating: boolean;
  isLoading: boolean;
  error: string | null;
  usingCachedData: boolean; // Indicates if showing cached data due to API failure
  
  // Actions
  setAnnotations: (annotations: Annotation[]) => void;
  selectAnnotation: (id: string | null) => void;
  setIsCreating: (isCreating: boolean) => void;
  clearError: () => void;
  
  // CRUD operations with error handling
  fetchAnnotations: (resourceId: string) => Promise<void>;
  createAnnotation: (resourceId: string, data: AnnotationCreate) => Promise<void>;
  updateAnnotation: (id: string, data: AnnotationUpdate) => Promise<void>;
  deleteAnnotation: (id: string) => Promise<void>;
  
  // Retry failed operations
  retryLastOperation: () => Promise<void>;
  
  // Optimistic updates
  addAnnotationOptimistic: (annotation: Annotation) => void;
  updateAnnotationOptimistic: (id: string, data: Partial<Annotation>) => void;
  removeAnnotationOptimistic: (id: string) => void;
  
  // Cache management
  getCachedAnnotations: (resourceId: string) => Annotation[] | null;
  setCachedAnnotations: (resourceId: string, annotations: Annotation[]) => void;
}

// Store last operation for retry functionality
let lastOperation: (() => Promise<void>) | null = null;

export const useAnnotationStore = create<AnnotationState>()(
  persist(
    (set, get) => ({
      // Initial state
      annotations: [],
      selectedAnnotation: null,
      annotationCache: {},
      isCreating: false,
      isLoading: false,
      error: null,
      usingCachedData: false,
      
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
      
      // Clear error
      clearError: () =>
        set({ error: null, usingCachedData: false }),
      
      // Fetch annotations for a resource with fallback to cached data
      fetchAnnotations: async (resourceId: string) => {
        const operation = async () => {
          set({ isLoading: true, error: null, usingCachedData: false });
          
          try {
            const response = await editorApi.getAnnotations(resourceId);
            const annotations = response.data;
            
            // Update state and cache
            set({ 
              annotations, 
              isLoading: false,
              usingCachedData: false,
            });
            get().setCachedAnnotations(resourceId, annotations);
          } catch (error) {
            // Try to use cached data as fallback
            const cached = get().getCachedAnnotations(resourceId);
            
            if (cached && cached.length > 0) {
              // Use cached data with warning
              set({
                annotations: cached,
                error: 'Unable to fetch latest annotations. Showing cached data.',
                usingCachedData: true,
                isLoading: false,
              });
            } else {
              // No cached data available
              set({
                annotations: [],
                error: error instanceof Error 
                  ? error.message 
                  : 'Failed to fetch annotations. No cached data available.',
                usingCachedData: false,
                isLoading: false,
              });
            }
          }
        };
        
        lastOperation = operation;
        await operation();
      },
      
      // Create annotation with optimistic update and error handling
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
        
        const operation = async () => {
          try {
            const response = await editorApi.createAnnotation(resourceId, data);
            
            // Replace optimistic annotation with real one
            set((state) => ({
              annotations: state.annotations.map((a) =>
                a.id === optimisticAnnotation.id ? response.data : a
              ),
              error: null,
            }));
            
            // Update cache
            const currentAnnotations = get().annotations;
            get().setCachedAnnotations(resourceId, currentAnnotations);
          } catch (error) {
            // Remove optimistic annotation on error
            get().removeAnnotationOptimistic(optimisticAnnotation.id);
            
            const errorMessage = error instanceof Error 
              ? error.message 
              : 'Failed to create annotation';
            
            set({ error: errorMessage });
            throw new Error(errorMessage);
          }
        };
        
        lastOperation = operation;
        await operation();
      },
      
      // Update annotation with optimistic update and error handling
      updateAnnotation: async (id: string, data: AnnotationUpdate) => {
        // Store original for rollback
        const original = get().annotations.find((a) => a.id === id);
        if (!original) {
          throw new Error('Annotation not found');
        }
        
        // Update optimistically
        get().updateAnnotationOptimistic(id, {
          ...data,
          updated_at: new Date().toISOString(),
        });
        
        const operation = async () => {
          try {
            const response = await editorApi.updateAnnotation(id, data);
            
            // Update with server response
            set((state) => ({
              annotations: state.annotations.map((a) =>
                a.id === id ? response.data : a
              ),
              error: null,
            }));
            
            // Update cache
            const resourceId = original.resource_id;
            const currentAnnotations = get().annotations;
            get().setCachedAnnotations(resourceId, currentAnnotations);
          } catch (error) {
            // Rollback on error
            get().updateAnnotationOptimistic(id, original);
            
            const errorMessage = error instanceof Error 
              ? error.message 
              : 'Failed to update annotation';
            
            set({ error: errorMessage });
            throw new Error(errorMessage);
          }
        };
        
        lastOperation = operation;
        await operation();
      },
      
      // Delete annotation with optimistic update and error handling
      deleteAnnotation: async (id: string) => {
        // Store original for rollback
        const original = get().annotations.find((a) => a.id === id);
        if (!original) {
          throw new Error('Annotation not found');
        }
        
        // Remove optimistically
        get().removeAnnotationOptimistic(id);
        
        const operation = async () => {
          try {
            await editorApi.deleteAnnotation(id);
            
            set({ error: null });
            
            // Update cache
            const resourceId = original.resource_id;
            const currentAnnotations = get().annotations;
            get().setCachedAnnotations(resourceId, currentAnnotations);
          } catch (error) {
            // Rollback on error
            get().addAnnotationOptimistic(original);
            
            const errorMessage = error instanceof Error 
              ? error.message 
              : 'Failed to delete annotation';
            
            set({ error: errorMessage });
            throw new Error(errorMessage);
          }
        };
        
        lastOperation = operation;
        await operation();
      },
      
      // Retry last failed operation
      retryLastOperation: async () => {
        if (lastOperation) {
          await lastOperation();
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
      
      // Cache management
      getCachedAnnotations: (resourceId: string) => {
        return get().annotationCache[resourceId] || null;
      },
      
      setCachedAnnotations: (resourceId: string, annotations: Annotation[]) =>
        set((state) => ({
          annotationCache: {
            ...state.annotationCache,
            [resourceId]: annotations,
          },
        })),
    }),
    {
      name: 'annotation-storage',
      // Persist annotation cache for offline support
      partialize: (state) => ({
        annotationCache: state.annotationCache,
      }),
    }
  )
);
