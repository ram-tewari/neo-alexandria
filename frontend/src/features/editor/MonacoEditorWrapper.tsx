/**
 * Monaco Editor Wrapper Component
 * 
 * Core Monaco Editor integration with:
 * - Read-only mode
 * - Theme switching (light/dark)
 * - Cursor and selection tracking
 * - Scroll position restoration
 * - Custom decorations support
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import type * as Monaco from 'monaco-editor';
import { registerThemes, getMonacoTheme } from '@/lib/monaco/themes';
import { detectLanguage } from '@/lib/monaco/languages';
import { DecorationManager } from '@/lib/monaco/decorations';
import { useEditorStore } from '@/stores/editor';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import type { CodeFile, Position, Selection } from './types';

// ============================================================================
// Types
// ============================================================================

export interface MonacoEditorWrapperProps {
  file: CodeFile;
  onCursorChange?: (position: Position) => void;
  onSelectionChange?: (selection: Selection | null) => void;
  onEditorReady?: (
    editor: Monaco.editor.IStandaloneCodeEditor,
    monaco: typeof Monaco,
    decorationManager: DecorationManager
  ) => void;
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function MonacoEditorWrapper({
  file,
  onCursorChange,
  onSelectionChange,
  onEditorReady,
  className = '',
}: MonacoEditorWrapperProps) {
  // ==========================================================================
  // State & Refs
  // ==========================================================================

  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof Monaco | null>(null);
  const decorationManagerRef = useRef<DecorationManager | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [isLargeFile, setIsLargeFile] = useState(false);

  // ==========================================================================
  // Store State
  // ==========================================================================

  const { scrollPosition, updateCursorPosition, updateSelection } = useEditorStore();
  const preferences = useEditorPreferencesStore();

  // ==========================================================================
  // Derived Values
  // ==========================================================================

  const language = detectLanguage(file.path);
  const theme = getMonacoTheme(preferences.theme === 'vs-dark' ? 'dark' : 'light');
  
  // Check if file is large (>5000 lines)
  useEffect(() => {
    setIsLargeFile(file.lines > 5000);
  }, [file.lines]);

  // ==========================================================================
  // Monaco Options
  // ==========================================================================

  const monacoOptions: Monaco.editor.IStandaloneEditorConstructionOptions = {
    readOnly: true,
    minimap: { enabled: preferences.minimap && !isLargeFile }, // Disable minimap for large files
    lineNumbers: preferences.lineNumbers ? 'on' : 'off',
    fontSize: preferences.fontSize,
    wordWrap: preferences.wordWrap ? 'on' : 'off',
    scrollBeyondLastLine: false,
    renderLineHighlight: 'line',
    glyphMargin: true, // Enable gutter for decorations
    folding: true,
    automaticLayout: true,
    scrollbar: {
      vertical: 'visible',
      horizontal: 'visible',
      useShadows: false,
      verticalScrollbarSize: 10,
      horizontalScrollbarSize: 10,
    },
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    overviewRulerBorder: false,
    // Performance optimizations for large files
    ...(isLargeFile && {
      renderValidationDecorations: 'off',
      renderWhitespace: 'none',
      renderControlCharacters: false,
      smoothScrolling: false,
    }),
  };

  // ==========================================================================
  // Editor Mount Handler
  // ==========================================================================

  const handleEditorMount: OnMount = useCallback(
    (editor, monaco) => {
      // Store references
      editorRef.current = editor;
      monacoRef.current = monaco;

      // Initialize decoration manager
      decorationManagerRef.current = new DecorationManager(editor);

      // Register custom themes
      registerThemes(monaco);

      // Set theme
      monaco.editor.setTheme(theme);

      // Restore scroll position if available
      if (scrollPosition > 0) {
        editor.setScrollTop(scrollPosition);
      }

      // Track cursor position changes
      editor.onDidChangeCursorPosition((e) => {
        const position: Position = {
          line: e.position.lineNumber,
          column: e.position.column,
        };
        updateCursorPosition(position);
        onCursorChange?.(position);
      });

      // Track selection changes
      editor.onDidChangeCursorSelection((e) => {
        const selection = e.selection;
        
        // Check if there's an actual selection (not just cursor position)
        if (
          selection.startLineNumber !== selection.endLineNumber ||
          selection.startColumn !== selection.endColumn
        ) {
          const selectionData: Selection = {
            start: {
              line: selection.startLineNumber,
              column: selection.startColumn,
            },
            end: {
              line: selection.endLineNumber,
              column: selection.endColumn,
            },
          };
          updateSelection(selectionData);
          onSelectionChange?.(selectionData);
        } else {
          updateSelection(null);
          onSelectionChange?.(null);
        }
      });

      // Track scroll position for persistence
      editor.onDidScrollChange((e) => {
        if (e.scrollTopChanged) {
          // Debounce scroll position updates
          const scrollTop = e.scrollTop;
          setTimeout(() => {
            useEditorStore.getState().updateScrollPosition(scrollTop);
          }, 200);
        }
      });

      // Mark as ready
      setIsReady(true);

      // Notify parent component with decoration manager
      onEditorReady?.(editor, monaco, decorationManagerRef.current);
    },
    [theme, scrollPosition, updateCursorPosition, updateSelection, onCursorChange, onSelectionChange, onEditorReady]
  );

  // ==========================================================================
  // Theme Update Effect
  // ==========================================================================

  useEffect(() => {
    if (monacoRef.current && isReady) {
      monacoRef.current.editor.setTheme(theme);
    }
  }, [theme, isReady]);

  // ==========================================================================
  // Preferences Update Effect
  // ==========================================================================

  useEffect(() => {
    if (editorRef.current && isReady) {
      editorRef.current.updateOptions({
        minimap: { enabled: preferences.minimap && !isLargeFile },
        lineNumbers: preferences.lineNumbers ? 'on' : 'off',
        fontSize: preferences.fontSize,
        wordWrap: preferences.wordWrap ? 'on' : 'off',
      });
    }
  }, [
    preferences.minimap,
    preferences.lineNumbers,
    preferences.fontSize,
    preferences.wordWrap,
    isLargeFile,
    isReady,
  ]);

  // ==========================================================================
  // Cleanup Effect
  // ==========================================================================

  useEffect(() => {
    return () => {
      // Dispose decoration manager
      if (decorationManagerRef.current) {
        decorationManagerRef.current.dispose();
      }
      
      // Dispose editor on unmount
      if (editorRef.current) {
        editorRef.current.dispose();
      }
    };
  }, []);

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div className={`monaco-editor-wrapper ${className}`} data-testid="monaco-editor-wrapper">
      <Editor
        height="100%"
        language={language}
        value={file.content}
        theme={theme}
        options={monacoOptions}
        onMount={handleEditorMount}
        loading={
          <div className="flex items-center justify-center h-full">
            <div className="text-muted-foreground">Loading editor...</div>
          </div>
        }
      />
    </div>
  );
}

