import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SemanticChunk } from '@/features/editor/types';

interface ChunkState {
  // Chunk data
  chunks: SemanticChunk[];
  selectedChunk: SemanticChunk | null;
  
  // UI state
  chunkVisibility: boolean;
  
  // Actions
  setChunks: (chunks: SemanticChunk[]) => void;
  selectChunk: (id: string | null) => void;
  toggleChunkVisibility: () => void;
  setChunkVisibility: (visible: boolean) => void;
  clearChunks: () => void;
}

export const useChunkStore = create<ChunkState>()(
  persist(
    (set, get) => ({
      // Initial state
      chunks: [],
      selectedChunk: null,
      chunkVisibility: true,
      
      // Set chunks (called by components using TanStack Query)
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
      
      // Clear chunks (called when switching resources)
      clearChunks: () =>
        set({ chunks: [], selectedChunk: null }),
    }),
    {
      name: 'chunk-storage',
      // Persist chunk visibility preference only
      partialize: (state) => ({
        chunkVisibility: state.chunkVisibility,
      }),
    }
  )
);
