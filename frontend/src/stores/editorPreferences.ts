import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface EditorPreferencesState {
  // Monaco editor preferences
  theme: 'vs-light' | 'vs-dark';
  fontSize: number;
  lineNumbers: boolean;
  minimap: boolean;
  wordWrap: boolean;
  
  // Overlay visibility preferences
  chunkBoundaries: boolean;
  qualityBadges: boolean;
  annotations: boolean;
  references: boolean;
  
  // Actions
  updatePreference: <K extends keyof EditorPreferencesState>(
    key: K,
    value: EditorPreferencesState[K]
  ) => void;
  
  // Convenience methods for toggling overlays
  toggleChunkBoundaries: () => void;
  toggleQualityBadges: () => void;
  toggleAnnotations: () => void;
  toggleReferences: () => void;
  
  // Reset to defaults
  resetToDefaults: () => void;
}

// Default preferences
const defaultPreferences = {
  theme: 'vs-dark' as const,
  fontSize: 14,
  lineNumbers: true,
  minimap: true,
  wordWrap: false,
  chunkBoundaries: true,
  qualityBadges: true,
  annotations: true,
  references: true,
};

export const useEditorPreferencesStore = create<EditorPreferencesState>()(
  persist(
    (set) => ({
      // Initial state (defaults)
      ...defaultPreferences,
      
      // Update any preference
      updatePreference: (key, value) =>
        set({ [key]: value }),
      
      // Toggle chunk boundaries
      toggleChunkBoundaries: () =>
        set((state) => ({ chunkBoundaries: !state.chunkBoundaries })),
      
      // Toggle quality badges
      toggleQualityBadges: () =>
        set((state) => ({ qualityBadges: !state.qualityBadges })),
      
      // Toggle annotations
      toggleAnnotations: () =>
        set((state) => ({ annotations: !state.annotations })),
      
      // Toggle references
      toggleReferences: () =>
        set((state) => ({ references: !state.references })),
      
      // Reset all preferences to defaults
      resetToDefaults: () =>
        set(defaultPreferences),
    }),
    {
      name: 'editor-preferences-storage',
      // Persist all preferences
      partialize: (state) => ({
        theme: state.theme,
        fontSize: state.fontSize,
        lineNumbers: state.lineNumbers,
        minimap: state.minimap,
        wordWrap: state.wordWrap,
        chunkBoundaries: state.chunkBoundaries,
        qualityBadges: state.qualityBadges,
        annotations: state.annotations,
        references: state.references,
      }),
    }
  )
);
