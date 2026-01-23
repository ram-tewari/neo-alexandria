import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CodeFile, Position, Selection } from '@/features/editor/types';

interface EditorState {
  // Active file state
  activeFile: CodeFile | null;
  
  // Cursor and selection state
  cursorPosition: Position;
  selection: Selection | null;
  
  // Scroll position (persisted per file)
  scrollPosition: number;
  scrollPositions: Record<string, number>; // fileId -> scrollPosition
  
  // Actions
  setActiveFile: (file: CodeFile | null) => void;
  updateCursorPosition: (position: Position) => void;
  updateSelection: (selection: Selection | null) => void;
  updateScrollPosition: (position: number) => void;
  restoreScrollPosition: (fileId: string) => number;
}

export const useEditorStore = create<EditorState>()(
  persist(
    (set, get) => ({
      // Initial state
      activeFile: null,
      cursorPosition: { line: 1, column: 1 },
      selection: null,
      scrollPosition: 0,
      scrollPositions: {},
      
      // Set active file and restore scroll position
      setActiveFile: (file: CodeFile | null) => {
        if (file) {
          const savedScrollPosition = get().scrollPositions[file.id] || 0;
          set({
            activeFile: file,
            scrollPosition: savedScrollPosition,
            cursorPosition: { line: 1, column: 1 },
            selection: null,
          });
        } else {
          set({
            activeFile: null,
            scrollPosition: 0,
            cursorPosition: { line: 1, column: 1 },
            selection: null,
          });
        }
      },
      
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
