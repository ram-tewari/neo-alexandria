import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SemanticChunk } from '@/features/editor/types';
import { editorApi } from '@/lib/api/editor';

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
  usingFallback: boolean; // Indicates if using line-based fallback
  
  // Actions
  setChunks: (chunks: SemanticChunk[]) => void;
  selectChunk: (id: string | null) => void;
  toggleChunkVisibility: () => void;
  setChunkVisibility: (visible: boolean) => void;
  clearError: () => void;
  
  // Data fetching with fallback
  fetchChunks: (resourceId: string, fileContent?: string, language?: string) => Promise<void>;
  
  // Retry failed operations
  retryLastOperation: () => Promise<void>;
  
  // Cache management
  getCachedChunks: (resourceId: string) => SemanticChunk[] | null;
  setCachedChunks: (resourceId: string, chunks: SemanticChunk[]) => void;
  clearCache: () => void;
}

// Store last operation for retry functionality
let lastChunkOperation: (() => Promise<void>) | null = null;

/**
 * Generate line-based fallback chunks when AST chunking fails
 * This provides a basic chunking strategy based on line numbers
 */
function generateLineBasedChunks(
  resourceId: string,
  fileContent: string,
  language: string
): SemanticChunk[] {
  const lines = fileContent.split('\n');
  const chunks: SemanticChunk[] = [];
  const chunkSize = 50; // Lines per chunk
  
  for (let i = 0; i < lines.length; i += chunkSize) {
    const endLine = Math.min(i + chunkSize, lines.length);
    const chunkLines = lines.slice(i, endLine);
    const content = chunkLines.join('\n');
    
    chunks.push({
      id: `fallback-${resourceId}-${i}`,
      resource_id: resourceId,
      content,
      chunk_index: Math.floor(i / chunkSize),
      chunk_metadata: {
        start_line: i + 1,
        end_line: endLine,
        language,
      },
      created_at: new Date().toISOString(),
    });
  }
  
  return chunks;
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
      usingFallback: false,
      
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
      
      // Clear error
      clearError: () =>
        set({ error: null, usingFallback: false }),
      
      // Fetch chunks for a resource with line-based fallback
      fetchChunks: async (resourceId: string, fileContent?: string, language?: string) => {
        const operation = async () => {
          // Check cache first
          const cached = get().getCachedChunks(resourceId);
          if (cached) {
            set({ chunks: cached, isLoading: false, usingFallback: false });
            return;
          }
          
          set({ isLoading: true, error: null, usingFallback: false });
          
          try {
            const response = await editorApi.getChunks(resourceId);
            const chunks = response.data;
            
            // Update state and cache
            set({ 
              chunks, 
              isLoading: false,
              usingFallback: false,
            });
            get().setCachedChunks(resourceId, chunks);
          } catch (error) {
            // Try line-based fallback if file content is available
            if (fileContent && language) {
              const fallbackChunks = generateLineBasedChunks(
                resourceId,
                fileContent,
                language
              );
              
              set({
                chunks: fallbackChunks,
                error: 'AST chunking unavailable. Using line-based display.',
                usingFallback: true,
                isLoading: false,
              });
              
              // Cache fallback chunks
              get().setCachedChunks(resourceId, fallbackChunks);
            } else {
              // No fallback available
              set({
                chunks: [],
                error: error instanceof Error 
                  ? error.message 
                  : 'Failed to fetch chunks. No fallback available.',
                usingFallback: false,
                isLoading: false,
              });
            }
          }
        };
        
        lastChunkOperation = operation;
        await operation();
      },
      
      // Retry last failed operation
      retryLastOperation: async () => {
        if (lastChunkOperation) {
          await lastChunkOperation();
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
