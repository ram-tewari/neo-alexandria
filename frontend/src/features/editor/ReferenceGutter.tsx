/**
 * ReferenceGutter Component
 * 
 * Displays reference icons (book icons) in the Monaco editor glyph margin
 * linking code to external papers, documentation, or resources.
 * 
 * Features:
 * - Renders book icons in Monaco glyph margin
 * - Hover tooltips with paper title and authors
 * - Click events to open reference details panel
 * - Visibility toggle support
 * - Support for multiple reference types (paper, documentation, external)
 * 
 * Requirements: 6.1, 6.2, 6.3
 * 
 * NOTE: This is a placeholder implementation for Phase 3 integration.
 * The reference data structure and API endpoints will be finalized in Phase 3.
 */

import { useEffect, useRef, useCallback, useMemo } from 'react';
import type * as Monaco from 'monaco-editor';
import type { Reference } from './types';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';

// ============================================================================
// Types
// ============================================================================

export interface ReferenceGutterProps {
  editor: Monaco.editor.IStandaloneCodeEditor | null;
  references: Reference[];
  visible: boolean;
  onReferenceClick?: (reference: Reference) => void;
  onReferenceHover?: (reference: Reference | null) => void;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Generate hover message for reference icon
 */
function generateReferenceHoverMessage(reference: Reference): string {
  const lines: string[] = [];
  
  // Title
  lines.push(`**${reference.title}**`);
  lines.push('');
  
  // Authors (if available)
  if (reference.authors && reference.authors.length > 0) {
    lines.push(`**Authors:** ${reference.authors.join(', ')}`);
  }
  
  // Reference type
  const typeLabel = reference.reference_type.charAt(0).toUpperCase() + 
                    reference.reference_type.slice(1);
  lines.push(`**Type:** ${typeLabel}`);
  
  // Citation (if available)
  if (reference.citation) {
    lines.push('');
    lines.push(`**Citation:** ${reference.citation}`);
  }
  
  // URL (if available)
  if (reference.url) {
    lines.push('');
    lines.push(`**URL:** ${reference.url}`);
  }
  
  // Library link hint (if pdf_id available)
  if (reference.pdf_id) {
    lines.push('');
    lines.push('_Click to view in Library_');
  }
  
  return lines.join('\n');
}

/**
 * Get CSS class for reference icon based on type
 */
function getReferenceIconClass(referenceType: Reference['reference_type']): string {
  switch (referenceType) {
    case 'paper':
      return 'reference-icon reference-icon-paper';
    case 'documentation':
      return 'reference-icon reference-icon-documentation';
    case 'external':
      return 'reference-icon reference-icon-external';
    default:
      return 'reference-icon';
  }
}

/**
 * Group references by line number
 */
function groupReferencesByLine(references: Reference[]): Map<number, Reference[]> {
  const lineMap = new Map<number, Reference[]>();
  
  for (const reference of references) {
    const existing = lineMap.get(reference.line_number) || [];
    lineMap.set(reference.line_number, [...existing, reference]);
  }
  
  return lineMap;
}

// ============================================================================
// Component
// ============================================================================

export function ReferenceGutter({
  editor,
  references,
  visible,
  onReferenceClick,
  onReferenceHover,
}: ReferenceGutterProps) {
  const decorationsRef = useRef<string[]>([]);
  
  // Get preferences
  const { references: referencesVisible } = useEditorPreferencesStore();
  
  // Determine if references should be shown
  const shouldShowReferences = visible && referencesVisible;
  
  // Group references by line for efficient lookup
  const referencesByLine = useMemo(() => {
    return groupReferencesByLine(references);
  }, [references]);
  
  // ==========================================================================
  // Update Decorations Effect
  // ==========================================================================
  
  useEffect(() => {
    if (!editor) return;
    
    // Check if monaco is available (not available in test environment)
    const monaco = (window as any).monaco;
    if (!monaco || !monaco.Range) {
      return;
    }
    
    // Clear existing decorations if not visible or no references
    if (!shouldShowReferences || references.length === 0) {
      decorationsRef.current = editor.deltaDecorations(
        decorationsRef.current,
        []
      );
      return;
    }
    
    // Create Monaco decorations for each reference
    const newDecorations: Monaco.editor.IModelDeltaDecoration[] = [];
    
    for (const [lineNumber, lineReferences] of referencesByLine.entries()) {
      // For now, show only the first reference if multiple exist on same line
      // TODO: In future, support stacking or showing multiple references
      const reference = lineReferences[0];
      
      newDecorations.push({
        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
        options: {
          glyphMarginClassName: getReferenceIconClass(reference.reference_type),
          glyphMarginHoverMessage: {
            value: generateReferenceHoverMessage(reference),
            isTrusted: true,
          },
        },
      });
    }
    
    // Apply decorations
    decorationsRef.current = editor.deltaDecorations(
      decorationsRef.current,
      newDecorations
    );
  }, [editor, references, shouldShowReferences, referencesByLine]);
  
  // ==========================================================================
  // Click Handler
  // ==========================================================================
  
  const handleGutterClick = useCallback(
    (e: Monaco.editor.IEditorMouseEvent) => {
      if (!shouldShowReferences || !onReferenceClick) return;
      
      // Check if monaco is available
      const monaco = (window as any).monaco;
      if (!monaco || !monaco.editor || !monaco.editor.MouseTargetType) {
        return;
      }
      
      // Check if click was in glyph margin
      if (e.target.type !== monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        return;
      }
      
      // Get the line number that was clicked
      const lineNumber = e.target.position?.lineNumber;
      if (!lineNumber) return;
      
      // Find references on this line
      const lineReferences = referencesByLine.get(lineNumber);
      if (!lineReferences || lineReferences.length === 0) return;
      
      // If multiple references, select the first one
      // TODO: In future, show a menu to select which reference
      const reference = lineReferences[0];
      onReferenceClick(reference);
    },
    [shouldShowReferences, referencesByLine, onReferenceClick]
  );
  
  // ==========================================================================
  // Hover Handler
  // ==========================================================================
  
  const handleMouseMove = useCallback(
    (e: Monaco.editor.IEditorMouseEvent) => {
      if (!shouldShowReferences || !onReferenceHover) return;
      
      // Check if monaco is available
      const monaco = (window as any).monaco;
      if (!monaco || !monaco.editor || !monaco.editor.MouseTargetType) {
        return;
      }
      
      // Check if hovering over glyph margin
      if (e.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        const lineNumber = e.target.position?.lineNumber;
        if (!lineNumber) {
          onReferenceHover(null);
          return;
        }
        
        // Find references on this line
        const lineReferences = referencesByLine.get(lineNumber);
        if (lineReferences && lineReferences.length > 0) {
          onReferenceHover(lineReferences[0]);
          return;
        }
      }
      
      onReferenceHover(null);
    },
    [shouldShowReferences, referencesByLine, onReferenceHover]
  );
  
  // ==========================================================================
  // Event Listeners Effect
  // ==========================================================================
  
  useEffect(() => {
    if (!editor) return;
    
    // Add click listener
    const clickDisposable = editor.onMouseDown(handleGutterClick);
    
    // Add hover listener (if hover callback provided)
    const moveDisposable = onReferenceHover
      ? editor.onMouseMove(handleMouseMove)
      : null;
    
    // Cleanup
    return () => {
      clickDisposable.dispose();
      moveDisposable?.dispose();
    };
  }, [editor, handleGutterClick, handleMouseMove, onReferenceHover]);
  
  // ==========================================================================
  // Cleanup Effect
  // ==========================================================================
  
  useEffect(() => {
    return () => {
      if (editor && decorationsRef.current.length > 0) {
        editor.deltaDecorations(decorationsRef.current, []);
      }
    };
  }, [editor]);
  
  // This component doesn't render anything directly
  // It only manages Monaco decorations
  return null;
}
