import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SemanticChunk } from '@/features/editor/types';

interface ChunkState {
  // Chunk data
  chunks: SemanticChunk[];
  selectedChunk: SemanticChunk | null;
  
  // Chunk cache (resourceId -> chunks)
  chunkCache: Record<string, SemanticChunk[]>;
  
  // UI state
  chunkVisibility: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setChunks: (chunks: SemanticChunk[]) => void;
  selectChunk: (id: string | null) => void;
  toggleChunkVisibility: () => void;
  setChunkVisibility: (visible: boolean) => void;
  
  // Data fetching
  fetchChunks: (resourceId: string) => Promise<void>;
  
  // Cache management
  getCachedChunks: (resourceId: string) => SemanticChunk[] | null;
  setCachedChunks: (resourceId: string, chunks: SemanticChunk[]) => void;
  clearCache: () => void;
}

export const useChunkStore = create<ChunkState>()(
  persist(
    (set, get) => ({
      // Initial state
      chunks: [],
      selectedChunk: null,
      chunkCache: {},
      chunkVisibility: true,
      isLoading: false,
      error: null,
      
      // Set chunks
      setChunks: (chunks: SemanticChunk[]) =>
        set({ chunks }),
      
      // Select chunk
      selectChunk: (id: string | null) => {
        if (id === null) {
          set({ selectedChunk: null });
        } else {
          const chunk = get().chunks.find((c) => c.id === id);
          set({ selectedChunk: chunk || null });
        }
      },
      
      // Toggle chunk visibility
      toggleChunkVisibility: () =>
        set((state) => ({ chunkVisibility: !state.chunkVisibility })),
      
      // Set chunk visibility
      setChunkVisibility: (visible: boolean) =>
        set({ chunkVisibility: visible }),
      
      // Fetch chunks for a resource
      fetchChunks: async (resourceId: string) => {
        // Check cache first
        const cached = get().getCachedChunks(resourceId);
        if (cached) {
          set({ chunks: cached, isLoading: false });
          return;
        }
        
        set({ isLoading: true, error: null });
        
        try {
          // TODO: Replace with actual API call in Task 3
          // const response = await editorApi.getChunks(resourceId);
          // const chunks = response.data;
          
          // Simulate API delay
          await new Promise((resolve) => setTimeout(resolve, 300));
          
          // Mock data for now
          const chunks: SemanticChunk[] = [];
          
          // Update state and cache
          set({ chunks, isLoading: false });
          get().setCachedChunks(resourceId, chunks);
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch chunks',
            isLoading: false,
          });
        }
      },
      
      // Get cached chunks for a resource
      getCachedChunks: (resourceId: string) => {
        return get().chunkCache[resourceId] || null;
      },
      
      // Set cached chunks for a resource
      setCachedChunks: (resourceId: string, chunks: SemanticChunk[]) =>
        set((state) => ({
          chunkCache: {
            ...state.chunkCache,
            [resourceId]: chunks,
          },
        })),
      
      // Clear all cached chunks
      clearCache: () =>
        set({ chunkCache: {} }),
    }),
    {
      name: 'chunk-storage',
      // Persist chunk visibility preference and cache
      partialize: (state) => ({
        chunkVisibility: state.chunkVisibility,
        chunkCache: state.chunkCache,
      }),
    }
  )
);
