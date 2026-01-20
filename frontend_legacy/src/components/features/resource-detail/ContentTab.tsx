import React, { useState, useRef, useCallback } from 'react';
import { ResourceRead } from '../../../lib/api/types';
import { PDFViewer } from '../../ui/PDFViewer/PDFViewer';
import { AnnotationLayer } from '../annotations/in-document/AnnotationLayer';
import { SelectionToolbar } from '../annotations/in-document/SelectionToolbar';
import { AnnotationEditor } from '../annotations/in-document/AnnotationEditor';
import { AnnotationSidebar } from '../annotations/in-document/AnnotationSidebar';
import {
  useResourceAnnotations,
  useCreateAnnotation,
  useUpdateAnnotation,
  useDeleteAnnotation,
} from '../../../lib/hooks/useAnnotations';
import { useToast } from '../../../contexts/ToastContext';
import type {
  AnnotationColor,
  TextSelection,
  AnnotationEditorState,
  Annotation,
} from '../../../types/annotations';
import './ContentTab.css';

interface ContentTabProps {
  resource: ResourceRead;
}

/**
 * ContentTab - Displays resource content with PDF viewer and annotations
 * 
 * Features:
 * - PDF viewing with zoom and navigation controls
 * - Text selection and annotation creation
 * - Annotation highlights overlay
 * - Annotation sidebar
 * - Fallback for non-PDF resources
 */
export const ContentTab: React.FC<ContentTabProps> = ({ resource }) => {
  const [selection, setSelection] = useState<TextSelection | null>(null);
  const [editorState, setEditorState] = useState<AnnotationEditorState>({
    mode: 'create',
    isOpen: false,
    color: 'yellow',
  });
  const [activeAnnotationId, setActiveAnnotationId] = useState<string>();

  const viewerRef = useRef<HTMLDivElement>(null);
  const { showToast } = useToast();

  // Fetch annotations for this resource
  const { data: annotations = [], isLoading: annotationsLoading } = useResourceAnnotations(
    resource.id
  );

  // Mutations
  const createMutation = useCreateAnnotation(resource.id);
  const updateMutation = useUpdateAnnotation();
  const deleteMutation = useDeleteAnnotation();

  // Handle text selection in PDF
  const handleTextSelection = useCallback(() => {
    const selectedText = window.getSelection();
    if (!selectedText || selectedText.toString().trim().length === 0) {
      setSelection(null);
      return;
    }

    const text = selectedText.toString().trim();
    const range = selectedText.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    setSelection({
      text,
      startOffset: 0, // Would need proper calculation with PDF.js text layer
      endOffset: text.length,
      pageNumber: 1, // Would need to detect current page
      boundingRect: rect,
    });
  }, []);

  // Handle highlight creation
  const handleHighlight = useCallback(
    (color: AnnotationColor) => {
      if (!selection) return;

      createMutation.mutate(
        {
          highlight: {
            startOffset: selection.startOffset,
            endOffset: selection.endOffset,
            pageNumber: selection.pageNumber,
            color,
            text: selection.text,
          },
        },
        {
          onSuccess: () => {
            showToast({ variant: 'success', message: 'Highlight created' });
            setSelection(null);
          },
          onError: () => {
            showToast({ variant: 'error', message: 'Failed to create highlight' });
          },
        }
      );
    },
    [selection, createMutation, showToast]
  );

  // Handle add note (create highlight + open editor)
  const handleAddNote = useCallback(() => {
    if (!selection) return;

    setEditorState({
      mode: 'create',
      isOpen: true,
      color: 'yellow',
      selection,
    });
  }, [selection]);

  // Handle annotation click (open editor)
  const handleAnnotationClick = useCallback((annotation: Annotation) => {
    setEditorState({
      mode: 'edit',
      isOpen: true,
      annotation,
      color: annotation.highlight.color,
    });
    setActiveAnnotationId(annotation.id);
  }, []);

  // Handle editor save
  const handleEditorSave = useCallback(
    async (data: { note?: string; tags?: string[]; color: AnnotationColor }) => {
      if (editorState.mode === 'create' && editorState.selection) {
        await createMutation.mutateAsync({
          highlight: {
            startOffset: editorState.selection.startOffset,
            endOffset: editorState.selection.endOffset,
            pageNumber: editorState.selection.pageNumber,
            color: data.color,
            text: editorState.selection.text,
          },
          note: data.note,
          tags: data.tags,
        });
      } else if (editorState.mode === 'edit' && editorState.annotation) {
        await updateMutation.mutateAsync({
          annotationId: editorState.annotation.id,
          data: {
            note: data.note,
            tags: data.tags,
            highlight: {
              color: data.color,
            },
          },
        });
      }
    },
    [editorState, createMutation, updateMutation]
  );

  // Handle annotation delete
  const handleEditorDelete = useCallback(async () => {
    if (editorState.annotation) {
      await deleteMutation.mutateAsync({
        annotationId: editorState.annotation.id,
        resourceId: resource.id,
      });
    }
  }, [editorState, deleteMutation, resource.id]);

  // Handle editor close
  const handleEditorClose = useCallback(() => {
    setEditorState(prev => ({ ...prev, isOpen: false }));
    setSelection(null);
  }, []);

  // Handle selection toolbar close
  const handleToolbarClose = useCallback(() => {
    setSelection(null);
  }, []);

  // Check if resource has a PDF URL
  const isPDF =
    resource.format?.toLowerCase().includes('pdf') ||
    resource.url?.toLowerCase().endsWith('.pdf');

  // For PDF resources, show the PDF viewer with annotations
  if (isPDF && resource.url) {
    return (
      <div
        role="tabpanel"
        id="panel-content"
        aria-labelledby="tab-content"
        className="content-tab"
      >
        <div
          ref={viewerRef}
          className="content-tab-viewer"
          onMouseUp={handleTextSelection}
        >
          <PDFViewer url={resource.url} />

          {/* Annotation Layer */}
          <AnnotationLayer
            annotations={annotations}
            onAnnotationClick={handleAnnotationClick}
            containerRef={viewerRef}
          />

          {/* Selection Toolbar */}
          {selection && (
            <SelectionToolbar
              selection={selection}
              onHighlight={handleHighlight}
              onAddNote={handleAddNote}
              onClose={handleToolbarClose}
            />
          )}

          {/* Annotation Editor */}
          {editorState.isOpen && (
            <AnnotationEditor
              mode={editorState.mode}
              annotation={editorState.annotation}
              selection={editorState.selection}
              initialColor={editorState.color}
              onSave={handleEditorSave}
              onDelete={editorState.mode === 'edit' ? handleEditorDelete : undefined}
              onClose={handleEditorClose}
            />
          )}
        </div>

        {/* Annotation Sidebar */}
        <AnnotationSidebar
          annotations={annotations}
          activeAnnotationId={activeAnnotationId}
          onAnnotationClick={handleAnnotationClick}
          isLoading={annotationsLoading}
        />
      </div>
    );
  }

  // For non-PDF resources or resources without URL, show placeholder
  return (
    <div
      role="tabpanel"
      id="panel-content"
      aria-labelledby="tab-content"
      className="content-tab"
    >
      <div className="placeholder-content">
        <div className="placeholder-icon">
          <svg
            width="48"
            height="48"
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 8h24a4 4 0 014 4v24a4 4 0 01-4 4H12a4 4 0 01-4-4V12a4 4 0 014-4zm4 8v16h16V16H16z"
              fill="currentColor"
              opacity="0.3"
            />
          </svg>
        </div>
        <h3>Content Viewer</h3>
        {resource.format && !isPDF ? (
          <p>
            Viewing {resource.format} files is not yet supported. Please use the
            link below to view the original source.
          </p>
        ) : (
          <p>No content available for this resource.</p>
        )}
        {resource.url && (
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="external-link"
          >
            View Original Source →
          </a>
        )}
      </div>
    </div>
  );
};
