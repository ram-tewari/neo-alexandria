/**
 * Monaco Editor Wrapper Component
 * 
 * Core Monaco Editor integration with:
 * - Read-only mode
 * - Theme switching (light/dark)
 * - Cursor and selection tracking
 * - Scroll position restoration
 * - Custom decorations support
 * 
 * Performance optimizations:
 * - Memoized with React.memo to prevent unnecessary re-renders
 * - Callbacks memoized with useCallback
 * - Expensive computations memoized with useMemo
 */

import { useEffect, useRef, useState, useCallback, useMemo, memo } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import type * as Monaco from 'monaco-editor';
import { registerThemes, getMonacoTheme } from '@/lib/monaco/themes';
import { detectLanguage } from '@/lib/monaco/languages';
import { DecorationManager } from '@/lib/monaco/decorations';
import { useEditorStore } from '@/stores/editor';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import { useAnnotationStore } from '@/stores/annotation';
import { useEditorKeyboard } from '@/lib/hooks/useEditorKeyboard';
import { MonacoFallback } from './MonacoFallback';
import { MonacoEditorSkeleton } from './components/LoadingSkeletons';
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

const MonacoEditorWrapperComponent = ({
  file,
  onCursorChange,
  onSelectionChange,
  onEditorReady,
  className = '',
}: MonacoEditorWrapperProps) => {
  // ==========================================================================
  // State & Refs
  // ==========================================================================

  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof Monaco | null>(null);
  const decorationManagerRef = useRef<DecorationManager | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [isLargeFile, setIsLargeFile] = useState(false);
  const [loadError, setLoadError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  // ==========================================================================
  // Store State
  // ==========================================================================

  const { scrollPosition, updateCursorPosition, updateSelection } = useEditorStore();
  const preferences = useEditorPreferencesStore();
  const { setPendingSelection } = useAnnotationStore();

  // ==========================================================================
  // Keyboard Shortcuts
  // ==========================================================================

  // Register editor-specific keyboard shortcuts
  // Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
  useEditorKeyboard();

  // ==========================================================================
  // Derived Values (Memoized)
  // ==========================================================================

  const language = useMemo(() => detectLanguage(file.path), [file.path]);
  const theme = useMemo(
    () => getMonacoTheme(preferences.theme === 'vs-dark' ? 'dark' : 'light'),
    [preferences.theme]
  );
  
  // Check if file is large (>5000 lines)
  useEffect(() => {
    setIsLargeFile(file.lines > 5000);
  }, [file.lines]);

  // ==========================================================================
  // Monaco Options (Memoized)
  // ==========================================================================

  const monacoOptions: Monaco.editor.IStandaloneEditorConstructionOptions = useMemo(
    () => ({
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
    }),
    [preferences.minimap, preferences.lineNumbers, preferences.fontSize, preferences.wordWrap, isLargeFile]
  );

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
          
          // Get selected text and calculate offsets for annotation
          const model = editor.getModel();
          if (model) {
            const selectedText = model.getValueInRange(selection);
            
            // Calculate character offsets from line/column positions
            const startOffset = model.getOffsetAt({
              lineNumber: selection.startLineNumber,
              column: selection.startColumn,
            });
            const endOffset = model.getOffsetAt({
              lineNumber: selection.endLineNumber,
              column: selection.endColumn,
            });
            
            // Trigger annotation creation with selected text
            if (selectedText.trim().length > 0) {
              setPendingSelection({
                startOffset,
                endOffset,
                highlightedText: selectedText,
              });
            }
          }
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
  // Error Handlers
  // ==========================================================================

  const handleEditorError = useCallback((error: Error) => {
    console.error('Monaco Editor failed to load:', error);
    setLoadError(error);
  }, []);

  const handleRetry = useCallback(() => {
    setLoadError(null);
    setRetryCount((prev) => prev + 1);
  }, []);

  // ==========================================================================
  // Render Fallback
  // ==========================================================================

  if (loadError) {
    return (
      <MonacoFallback
        file={file}
        error={loadError}
        onRetry={handleRetry}
        className={className}
      />
    );
  }

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div 
      className={`monaco-editor-wrapper ${className}`} 
      data-testid="monaco-editor-wrapper"
      role="region"
      aria-label="Code editor"
    >
      <Editor
        key={retryCount} // Force remount on retry
        height="100%"
        language={language}
        value={file.content}
        theme={theme}
        options={monacoOptions}
        onMount={handleEditorMount}
        onValidate={(markers) => {
          // Monaco validation errors (not load errors)
          if (markers.length > 0) {
            console.warn('Monaco validation markers:', markers);
          }
        }}
        loading={<MonacoEditorSkeleton />}
      />
    </div>
  );
}

// Memoize the component to prevent unnecessary re-renders
// Requirements: 7.2 - React optimization
export const MonacoEditorWrapper = memo(MonacoEditorWrapperComponent, (prevProps, nextProps) => {
  // Custom comparison function for better memoization
  return (
    prevProps.file.id === nextProps.file.id &&
    prevProps.file.content === nextProps.file.content &&
    prevProps.className === nextProps.className &&
    prevProps.onCursorChange === nextProps.onCursorChange &&
    prevProps.onSelectionChange === nextProps.onSelectionChange &&
    prevProps.onEditorReady === nextProps.onEditorReady
  );
});

MonacoEditorWrapper.displayName = 'MonacoEditorWrapper';

// Error Boundary Wrapper for Monaco Editor
export function MonacoEditorWithErrorBoundary(props: MonacoEditorWrapperProps) {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Reset error state when file changes
    setHasError(false);
    setError(null);
  }, [props.file.id]);

  if (hasError && error) {
    return (
      <MonacoFallback
        file={props.file}
        error={error}
        onRetry={() => {
          setHasError(false);
          setError(null);
        }}
        className={props.className}
      />
    );
  }

  try {
    return <MonacoEditorWrapper {...props} />;
  } catch (err) {
    setHasError(true);
    setError(err instanceof Error ? err : new Error(String(err)));
    return null;
  }
}

