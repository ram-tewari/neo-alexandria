/**
 * Example: Integrating SemanticChunkOverlay with MonacoEditorWrapper
 * 
 * This example shows how to use the SemanticChunkOverlay component
 * with the MonacoEditorWrapper to display semantic chunk boundaries.
 */

import { useState, useCallback } from 'react';
import { MonacoEditorWrapper } from './MonacoEditorWrapper';
import { SemanticChunkOverlay } from './SemanticChunkOverlay';
import type * as Monaco from 'monaco-editor';
import type { CodeFile, SemanticChunk } from './types';
import { DecorationManager } from '@/lib/monaco/decorations';

export function EditorWithChunks() {
  const [editor, setEditor] = useState<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const [monaco, setMonaco] = useState<typeof Monaco | null>(null);
  const [hoveredChunk, setHoveredChunk] = useState<SemanticChunk | null>(null);

  // Example code file
  const codeFile: CodeFile = {
    id: 'file-1',
    resource_id: 'resource-1',
    path: 'src/example.ts',
    name: 'example.ts',
    language: 'typescript',
    content: `function greet(name: string): string {
  return \`Hello, \${name}!\`;
}

function farewell(name: string): string {
  return \`Goodbye, \${name}!\`;
}

class Greeter {
  constructor(private name: string) {}
  
  greet(): string {
    return greet(this.name);
  }
  
  farewell(): string {
    return farewell(this.name);
  }
}`,
    size: 1024,
    lines: 18,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  // Handle editor ready
  const handleEditorReady = useCallback(
    (
      editorInstance: Monaco.editor.IStandaloneCodeEditor,
      monacoInstance: typeof Monaco,
      decorationManager: DecorationManager
    ) => {
      setEditor(editorInstance);
      setMonaco(monacoInstance);
      console.log('Editor ready with decoration manager:', decorationManager);
    },
    []
  );

  // Handle chunk click
  const handleChunkClick = useCallback((chunk: SemanticChunk) => {
    console.log('Chunk clicked:', chunk);
    // You can open a metadata panel, navigate, etc.
  }, []);

  // Handle chunk hover
  const handleChunkHover = useCallback((chunk: SemanticChunk | null) => {
    setHoveredChunk(chunk);
    if (chunk) {
      console.log('Hovering over chunk:', chunk.chunk_metadata.function_name || chunk.chunk_metadata.class_name);
    }
  }, []);

  return (
    <div className="h-screen flex flex-col">
      {/* Header with chunk info */}
      <div className="p-4 border-b bg-background">
        <h2 className="text-lg font-semibold">Code Editor with Semantic Chunks</h2>
        {hoveredChunk && (
          <p className="text-sm text-muted-foreground mt-1">
            Hovering: {hoveredChunk.chunk_metadata.function_name || hoveredChunk.chunk_metadata.class_name || 'Code Block'} 
            (Lines {hoveredChunk.chunk_metadata.start_line}-{hoveredChunk.chunk_metadata.end_line})
          </p>
        )}
      </div>

      {/* Editor */}
      <div className="flex-1 relative">
        <MonacoEditorWrapper
          file={codeFile}
          onEditorReady={handleEditorReady}
          className="h-full"
        />

        {/* Semantic Chunk Overlay */}
        {editor && monaco && (
          <SemanticChunkOverlay
            editor={editor}
            monaco={monaco}
            resourceId={codeFile.resource_id}
            visible={true}
            onChunkClick={handleChunkClick}
            onChunkHover={handleChunkHover}
          />
        )}
      </div>
    </div>
  );
}

/**
 * Usage Notes:
 * 
 * 1. The SemanticChunkOverlay is a logical component that doesn't render DOM.
 *    It manages Monaco decorations and event listeners.
 * 
 * 2. You must wait for the editor to be ready before rendering the overlay.
 *    Use the onEditorReady callback from MonacoEditorWrapper.
 * 
 * 3. The overlay automatically fetches chunks from the chunkStore when mounted.
 *    Make sure the backend API is configured in src/lib/api/editor.ts.
 * 
 * 4. Chunk visibility is controlled by:
 *    - The `visible` prop (component-level)
 *    - chunkStore.chunkVisibility (store-level)
 *    - editorPreferencesStore.chunkBoundaries (user preference)
 * 
 * 5. The overlay handles nested/overlapping chunks by selecting the innermost
 *    (smallest range) chunk when multiple chunks contain the cursor position.
 * 
 * 6. Keyboard shortcuts for toggling chunk visibility should be implemented
 *    in the parent component or global keyboard handler (Task 12).
 * 
 * 7. The CSS styles for chunk decorations are in src/features/editor/editor.css.
 *    You can customize colors and animations there.
 */
