/**
 * CodeEditorView Component
 * 
 * Main view component that integrates all editor features with error handling:
 * - Monaco editor with fallback
 * - Semantic chunk overlay with line-based fallback
 * - Quality badges with auto-hide on error
 * - Annotations with cached data fallback
 * - Error banners for all API failures
 * - Retry functionality for failed operations
 */

import { useEffect, useState, useCallback } from 'react';
import type * as Monaco from 'monaco-editor';
import { MonacoEditorWrapper } from './MonacoEditorWrapper';
import { SemanticChunkOverlay } from './SemanticChunkOverlay';
import { QualityBadgeGutter } from './QualityBadgeGutter';
import { AnnotationGutter } from './AnnotationGutter';
import { AnnotationPanel } from './AnnotationPanel';
import { ChunkMetadataPanel } from './ChunkMetadataPanel';
import { HoverCardProvider } from './HoverCardProvider';
import {
  AnnotationErrorBanner,
  ChunkErrorBanner,
  QualityErrorBanner,
} from './components/ErrorBanner';
import {
  AnnotationsLoadingIndicator,
  ChunksLoadingIndicator,
  QualityLoadingIndicator,
} from './components/ApiLoadingIndicators';
import { DecorationManager } from '@/lib/monaco/decorations';
import { useAnnotationStore } from '@/stores/annotation';
import { useChunkStore } from '@/stores/chunk';
import { useQualityStore } from '@/stores/quality';
import { useEditorStore } from '@/stores/editor';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import type { CodeFile } from './types';

// ============================================================================
// Types
// ============================================================================

export interface CodeEditorViewProps {
  file: CodeFile;
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function CodeEditorView({ file, className = '' }: CodeEditorViewProps) {
  // ==========================================================================
  // State
  // ==========================================================================

  const [editor, setEditor] = useState<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const [monaco, setMonaco] = useState<typeof Monaco | null>(null);
  const [decorationManager, setDecorationManager] = useState<DecorationManager | null>(null);

  // ==========================================================================
  // Store State
  // ==========================================================================

  // Annotation store
  const {
    annotations,
    isLoading: annotationsLoading,
    error: annotationError,
    usingCachedData,
    fetchAnnotations,
    retryLastOperation: retryAnnotations,
    clearError: clearAnnotationError,
  } = useAnnotationStore();

  // Chunk store
  const {
    chunks,
    selectedChunk,
    chunkVisibility,
    isLoading: chunksLoading,
    error: chunkError,
    usingFallback,
    fetchChunks,
    retryLastOperation: retryChunks,
    clearError: clearChunkError,
    selectChunk,
  } = useChunkStore();

  // Quality store
  const {
    qualityData,
    badgeVisibility,
    isLoading: qualityLoading,
    error: qualityError,
    hideBadgesDueToError,
    fetchQualityData,
    retryLastOperation: retryQuality,
    clearError: clearQualityError,
  } = useQualityStore();

  // Editor preferences
  const preferences = useEditorPreferencesStore();

  // ==========================================================================
  // Data Fetching
  // ==========================================================================

  // Fetch all data when file changes
  useEffect(() => {
    const resourceId = file.resource_id;

    // Fetch annotations with cached fallback
    fetchAnnotations(resourceId);

    // Fetch chunks with line-based fallback
    // Pass file content and language for fallback generation
    fetchChunks(resourceId, file.content, file.language);

    // Fetch quality data (will auto-hide badges on error)
    fetchQualityData(resourceId);
  }, [file.resource_id, file.content, file.language, fetchAnnotations, fetchChunks, fetchQualityData]);

  // ==========================================================================
  // Editor Ready Handler
  // ==========================================================================

  const handleEditorReady = useCallback(
    (
      editorInstance: Monaco.editor.IStandaloneCodeEditor,
      monacoInstance: typeof Monaco,
      decorationManagerInstance: DecorationManager
    ) => {
      setEditor(editorInstance);
      setMonaco(monacoInstance);
      setDecorationManager(decorationManagerInstance);
    },
    []
  );

  // ==========================================================================
  // Error Banner Handlers
  // ==========================================================================

  const handleRetryAnnotations = useCallback(async () => {
    await retryAnnotations();
  }, [retryAnnotations]);

  const handleRetryChunks = useCallback(async () => {
    await retryChunks();
  }, [retryChunks]);

  const handleRetryQuality = useCallback(async () => {
    await retryQuality();
  }, [retryQuality]);

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div className={`code-editor-view flex flex-col h-full ${className}`}>
      {/* Error Banners and Loading Indicators */}
      <div className="error-banners-container p-4 space-y-2">
        {/* Loading Indicators */}
        {annotationsLoading && !annotationError && <AnnotationsLoadingIndicator />}
        {chunksLoading && !chunkError && <ChunksLoadingIndicator />}
        {qualityLoading && !qualityError && <QualityLoadingIndicator />}

        {/* Annotation Error Banner */}
        {annotationError && (
          <AnnotationErrorBanner
            error={annotationError}
            usingCachedData={usingCachedData}
            onRetry={handleRetryAnnotations}
            onDismiss={clearAnnotationError}
            isRetrying={annotationsLoading}
          />
        )}

        {/* Chunk Error Banner */}
        {chunkError && (
          <ChunkErrorBanner
            error={chunkError}
            usingFallback={usingFallback}
            onRetry={handleRetryChunks}
            onDismiss={clearChunkError}
            isRetrying={chunksLoading}
          />
        )}

        {/* Quality Error Banner */}
        {qualityError && hideBadgesDueToError && (
          <QualityErrorBanner
            error={qualityError}
            onRetry={handleRetryQuality}
            onDismiss={clearQualityError}
            isRetrying={qualityLoading}
          />
        )}
      </div>

      {/* Main Editor Area */}
      <div className="editor-container flex-1 flex gap-4 p-4">
        {/* Monaco Editor with Overlays */}
        <div className="editor-main flex-1 relative">
          <MonacoEditorWrapper
            file={file}
            onEditorReady={handleEditorReady}
            className="h-full"
          />

          {/* Semantic Chunk Overlay */}
          {editor && preferences.chunkBoundaries && (
            <SemanticChunkOverlay
              editor={editor}
              chunks={chunks}
              visible={chunkVisibility}
              selectedChunk={selectedChunk}
              onChunkClick={(chunk) => selectChunk(chunk.id)}
              onChunkHover={(chunk) => {
                // Optional: Show chunk preview on hover
              }}
            />
          )}

          {/* Quality Badge Gutter */}
          {editor && preferences.qualityBadges && !hideBadgesDueToError && (
            <QualityBadgeGutter
              editor={editor}
              qualityData={qualityData}
              visible={badgeVisibility}
              resourceId={file.resource_id}
              onBadgeClick={(line) => {
                // Optional: Show quality details on click
                console.log('Quality badge clicked at line:', line);
              }}
            />
          )}

          {/* Annotation Gutter */}
          {editor && preferences.annotations && (
            <AnnotationGutter
              editor={editor}
              annotations={annotations}
              visible={true}
              onAnnotationClick={(annotation) => {
                // Optional: Open annotation panel or show details
                console.log('Annotation clicked:', annotation);
              }}
              onAnnotationHover={(annotation) => {
                // Optional: Show annotation preview
              }}
            />
          )}

          {/* Hover Card Provider */}
          {editor && monaco && (
            <HoverCardProvider
              editor={editor}
              monaco={monaco}
              resourceId={file.resource_id}
            />
          )}
        </div>

        {/* Side Panels */}
        <div className="editor-panels flex flex-col gap-4 w-80">
          {/* Chunk Metadata Panel */}
          {selectedChunk && (
            <ChunkMetadataPanel
              chunk={selectedChunk}
              onNavigateToChunk={(chunkId) => selectChunk(chunkId)}
            />
          )}

          {/* Annotation Panel */}
          {preferences.annotations && (
            <AnnotationPanel
              resourceId={file.resource_id}
              annotations={annotations}
              onAnnotationSelect={(id) => {
                // Optional: Scroll to annotation in editor
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}
