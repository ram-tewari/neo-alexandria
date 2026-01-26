import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CodeFile, Position, Selection } from '@/features/editor/types';
import type { Resource } from '@/types/api';

interface EditorState {
  // Active resource state (replaces mock file data)
  activeResourceId: string | null;
  activeFile: CodeFile | null;
  
  // Loading and error states (Requirement 3.5, 3.6)
  isLoading: boolean;
  error: Error | null;
  
  // Cursor and selection state
  cursorPosition: Position;
  selection: Selection | null;
  
  // Scroll position (persisted per file)
  scrollPosition: number;
  scrollPositions: Record<string, number>; // fileId -> scrollPosition
  
  // Actions
  setActiveResource: (resourceId: string | null) => void;
  setActiveFile: (file: CodeFile | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: Error | null) => void;
  updateCursorPosition: (position: Position) => void;
  updateSelection: (selection: Selection | null) => void;
  updateScrollPosition: (position: number) => void;
  restoreScrollPosition: (fileId: string) => number;
  clearEditor: () => void;
}

/**
 * Helper function to convert Resource to CodeFile
 * Maps backend Resource model to frontend CodeFile model
 */
export function resourceToCodeFile(resource: Resource): CodeFile {
  return {
    id: resource.id,
    resource_id: resource.id,
    path: resource.file_path || resource.url || `/${resource.title}`,
    name: resource.title,
    language: resource.language || 'plaintext',
    content: resource.content || '',
    size: resource.content?.length || 0,
    lines: resource.content?.split('\n').length || 0,
    created_at: resource.created_at,
    updated_at: resource.updated_at,
  };
}

export const useEditorStore = create<EditorState>()(
  persist(
    (set, get) => ({
      // Initial state
      activeResourceId: null,
      activeFile: null,
      isLoading: false,
      error: null,
      cursorPosition: { line: 1, column: 1 },
      selection: null,
      scrollPosition: 0,
      scrollPositions: {},
      
      // Set active resource ID (used by components to trigger useResource hook)
      setActiveResource: (resourceId: string | null) => {
        set({
          activeResourceId: resourceId,
          isLoading: !!resourceId, // Set loading if we have a resource ID
          error: null,
        });
      },
      
      // Set active file and restore scroll position
      // This is called by components after useResource hook returns data
      setActiveFile: (file: CodeFile | null) => {
        if (file) {
          const savedScrollPosition = get().scrollPositions[file.id] || 0;
          set({
            activeFile: file,
            scrollPosition: savedScrollPosition,
            cursorPosition: { line: 1, column: 1 },
            selection: null,
            isLoading: false,
            error: null,
          });
        } else {
          set({
            activeFile: null,
            scrollPosition: 0,
            cursorPosition: { line: 1, column: 1 },
            selection: null,
            isLoading: false,
          });
        }
      },
      
      // Set loading state (Requirement 3.5)
      setLoading: (loading: boolean) => set({ isLoading: loading }),
      
      // Set error state (Requirement 3.6)
      setError: (error: Error | null) => set({ error, isLoading: false }),
      
      // Update cursor position
      updateCursorPosition: (position: Position) =>
        set({ cursorPosition: position }),
      
      // Update selection
      updateSelection: (selection: Selection | null) =>
        set({ selection }),
      
      // Update scroll position and persist it for current file
      updateScrollPosition: (position: number) => {
        const { activeFile } = get();
        if (activeFile) {
          set((state) => ({
            scrollPosition: position,
            scrollPositions: {
              ...state.scrollPositions,
              [activeFile.id]: position,
            },
          }));
        } else {
          set({ scrollPosition: position });
        }
      },
      
      // Restore scroll position for a specific file
      restoreScrollPosition: (fileId: string) => {
        return get().scrollPositions[fileId] || 0;
      },
      
      // Clear editor state
      clearEditor: () => set({
        activeResourceId: null,
        activeFile: null,
        isLoading: false,
        error: null,
        cursorPosition: { line: 1, column: 1 },
        selection: null,
        scrollPosition: 0,
      }),
    }),
    {
      name: 'editor-storage',
      // Only persist scroll positions, not the active file or cursor state
      partialize: (state) => ({
        scrollPositions: state.scrollPositions,
      }),
    }
  )
);
