import { useEffect } from 'react';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import { useAnnotationStore } from '@/stores/annotation';
import { useEditorStore } from '@/stores/editor';

/**
 * Editor-specific keyboard shortcut handler
 * 
 * Registers keyboard shortcuts for the Living Code Editor:
 * 
 * Global shortcuts:
 * - Cmd/Ctrl + /: Toggle annotation mode
 * - Cmd/Ctrl + Shift + A: Show all annotations
 * - Cmd/Ctrl + Shift + Q: Toggle quality badge visibility
 * - Cmd/Ctrl + Shift + C: Toggle chunk boundary visibility
 * - Cmd/Ctrl + Shift + R: Toggle reference visibility
 * 
 * Annotation mode shortcuts (when annotation mode is active):
 * - Enter: Create annotation from selection
 * - Cmd/Ctrl + S: Save annotation
 * - Cmd/Ctrl + Backspace: Delete annotation
 * - Tab: Navigate to next annotation
 * - Shift + Tab: Navigate to previous annotation
 * 
 * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
 */
export function useEditorKeyboard() {
  const {
    toggleChunkBoundaries,
    toggleQualityBadges,
    toggleAnnotations,
    toggleReferences,
  } = useEditorPreferencesStore();
  
  const { 
    setIsCreating, 
    isCreating,
    annotations,
    selectedAnnotation,
    selectAnnotation,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
  } = useAnnotationStore();
  
  const { selection, activeFile } = useEditorStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modKey = isMac ? e.metaKey : e.ctrlKey;

      // ======================================================================
      // Global Editor Shortcuts
      // ======================================================================

      // Cmd/Ctrl + /: Toggle annotation mode
      // Requirement 8.2
      if (e.key === '/' && modKey && !e.shiftKey) {
        e.preventDefault();
        setIsCreating(!isCreating);
        return;
      }

      // Cmd/Ctrl + Shift + A: Show all annotations
      // Requirement 8.3
      if (e.key === 'A' && modKey && e.shiftKey) {
        e.preventDefault();
        // Toggle annotations visibility
        toggleAnnotations();
        return;
      }

      // Cmd/Ctrl + Shift + Q: Toggle quality badge visibility
      // Requirement 8.4
      if (e.key === 'Q' && modKey && e.shiftKey) {
        e.preventDefault();
        toggleQualityBadges();
        return;
      }

      // Cmd/Ctrl + Shift + C: Toggle chunk boundary visibility
      // Requirement 8.5
      if (e.key === 'C' && modKey && e.shiftKey) {
        e.preventDefault();
        toggleChunkBoundaries();
        return;
      }

      // Cmd/Ctrl + Shift + R: Toggle reference visibility
      // Requirement 8.5 (references)
      if (e.key === 'R' && modKey && e.shiftKey) {
        e.preventDefault();
        toggleReferences();
        return;
      }

      // ======================================================================
      // Annotation Mode Shortcuts (only active when annotation mode is on)
      // Requirements: 8.2, 8.3
      // ======================================================================

      if (isCreating) {
        // Enter: Create annotation from selection
        // Requirement 8.2
        if (e.key === 'Enter' && !modKey && !e.shiftKey) {
          e.preventDefault();
          
          // Only create if there's a selection and active file
          if (selection && activeFile) {
            // Calculate offsets (simplified - assumes single line for now)
            // In a real implementation, this would need to calculate actual character offsets
            const startOffset = (selection.start.line - 1) * 100 + selection.start.column;
            const endOffset = (selection.end.line - 1) * 100 + selection.end.column;
            
            // Get selected text (placeholder - would need actual text extraction)
            const highlightedText = `Selected text from line ${selection.start.line} to ${selection.end.line}`;
            
            createAnnotation(activeFile.resource_id, {
              start_offset: startOffset,
              end_offset: endOffset,
              highlighted_text: highlightedText,
              note: '',
            }).catch((error) => {
              console.error('Failed to create annotation:', error);
            });
          }
          return;
        }

        // Cmd/Ctrl + S: Save annotation (when editing)
        // Requirement 8.2
        if (e.key === 's' && modKey && !e.shiftKey) {
          e.preventDefault();
          
          // If there's a selected annotation, trigger save
          // The actual save logic is handled by the AnnotationPanel component
          // This shortcut just triggers the save action
          if (selectedAnnotation) {
            // Dispatch a custom event that the AnnotationPanel can listen to
            window.dispatchEvent(new CustomEvent('editor:save-annotation'));
          }
          return;
        }

        // Cmd/Ctrl + Backspace: Delete annotation
        // Requirement 8.3
        if (e.key === 'Backspace' && modKey && !e.shiftKey) {
          e.preventDefault();
          
          if (selectedAnnotation) {
            // Confirm deletion
            if (window.confirm('Delete this annotation?')) {
              deleteAnnotation(selectedAnnotation.id).catch((error) => {
                console.error('Failed to delete annotation:', error);
              });
            }
          }
          return;
        }

        // Tab: Navigate to next annotation
        // Requirement 8.3
        if (e.key === 'Tab' && !modKey && !e.shiftKey) {
          e.preventDefault();
          
          if (annotations.length > 0) {
            const currentIndex = selectedAnnotation
              ? annotations.findIndex((a) => a.id === selectedAnnotation.id)
              : -1;
            
            const nextIndex = (currentIndex + 1) % annotations.length;
            selectAnnotation(annotations[nextIndex].id);
          }
          return;
        }

        // Shift + Tab: Navigate to previous annotation
        // Requirement 8.3
        if (e.key === 'Tab' && !modKey && e.shiftKey) {
          e.preventDefault();
          
          if (annotations.length > 0) {
            const currentIndex = selectedAnnotation
              ? annotations.findIndex((a) => a.id === selectedAnnotation.id)
              : -1;
            
            const prevIndex = currentIndex <= 0 
              ? annotations.length - 1 
              : currentIndex - 1;
            
            selectAnnotation(annotations[prevIndex].id);
          }
          return;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [
    toggleChunkBoundaries,
    toggleQualityBadges,
    toggleAnnotations,
    toggleReferences,
    setIsCreating,
    isCreating,
    selection,
    activeFile,
    annotations,
    selectedAnnotation,
    selectAnnotation,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
  ]);
}
