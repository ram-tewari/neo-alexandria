import React, { useState, useEffect, useRef } from 'react';
import { ColorPicker } from './ColorPicker';
import { Button } from '../../../ui/Button/Button';
import { useToast } from '../../../../contexts/ToastContext';
import { useFocusTrap } from '../../../../lib/hooks/useFocusTrap';
import type { Annotation, AnnotationColor, TextSelection } from '../../../../types/annotations';
import './AnnotationEditor.css';

interface AnnotationEditorProps {
    mode: 'create' | 'edit';
    annotation?: Annotation;
    selection?: TextSelection;
    initialColor?: AnnotationColor;
    onSave: (data: {
        note?: string;
        tags?: string[];
        color: AnnotationColor;
    }) => Promise<void>;
    onDelete?: () => Promise<void>;
    onClose: () => void;
}

/**
 * AnnotationEditor - Panel for creating/editing annotation notes
 * 
 * Features:
 * - Textarea with markdown support
 * - Tag autocomplete
 * - Color picker
 * - Autosave with debounce (1000ms)
 * - Toast notifications
 * - Delete button for existing annotations
 */
export const AnnotationEditor: React.FC<AnnotationEditorProps> = ({
    mode,
    annotation,
    selection,
    initialColor = 'yellow',
    onSave,
    onDelete,
    onClose,
}) => {
    const [note, setNote] = useState(annotation?.note || '');
    const [tags, setTags] = useState<string[]>(annotation?.tags.map(t => t.name) || []);
    const [color, setColor] = useState<AnnotationColor>(
        annotation?.highlight.color || initialColor
    );
    const [tagInput, setTagInput] = useState('');
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
    const [isDeleting, setIsDeleting] = useState(false);

    const saveTimeoutRef = useRef<number>();
    const editorRef = useRef<HTMLDivElement>(null);
    const { showToast } = useToast();

    useFocusTrap(editorRef, true);

    // Autosave with debounce
    useEffect(() => {
        if (mode === 'edit' && annotation) {
            // Clear existing timeout
            if (saveTimeoutRef.current) {
                clearTimeout(saveTimeoutRef.current);
            }

            // Set new timeout for autosave
            saveTimeoutRef.current = setTimeout(async () => {
                setSaveStatus('saving');
                try {
                    await onSave({ note, tags, color });
                    setSaveStatus('saved');
                    setTimeout(() => setSaveStatus('idle'), 2000);
                } catch (error) {
                    setSaveStatus('error');
                    showToast({ variant: 'error', message: 'Failed to save annotation' });
                }
            }, 1000);
        }

        return () => {
            if (saveTimeoutRef.current) {
                clearTimeout(saveTimeoutRef.current);
            }
        };
    }, [note, tags, color, mode, annotation, onSave, showToast]);

    const handleSave = async () => {
        setSaveStatus('saving');
        try {
            await onSave({ note, tags, color });
            showToast({ variant: 'success', message: 'Annotation saved' });
            onClose();
        } catch (error) {
            setSaveStatus('error');
            showToast({ variant: 'error', message: 'Failed to save annotation' });
        }
    };

    const handleDelete = async () => {
        if (!onDelete) return;

        setIsDeleting(true);
        try {
            await onDelete();
            showToast({ variant: 'success', message: 'Annotation deleted' });
            onClose();
        } catch (error) {
            setIsDeleting(false);
            showToast({ variant: 'error', message: 'Failed to delete annotation' });
        }
    };

    const handleAddTag = () => {
        const trimmed = tagInput.trim();
        if (trimmed && !tags.includes(trimmed)) {
            setTags([...tags, trimmed]);
            setTagInput('');
        }
    };

    const handleRemoveTag = (tagToRemove: string) => {
        setTags(tags.filter(t => t !== tagToRemove));
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Escape') {
            onClose();
        }
        if (e.key === 's' && (e.metaKey || e.ctrlKey)) {
            e.preventDefault();
            handleSave();
        }
    };

    const highlightText = selection?.text || annotation?.highlight.text || '';

    return (
        <>
            <div className="annotation-editor-overlay" onClick={onClose} />
            <div
                ref={editorRef}
                className="annotation-editor"
                role="dialog"
                aria-labelledby="annotation-editor-title"
                aria-modal="true"
                onKeyDown={handleKeyDown}
            >
                <div className="annotation-editor-header">
                    <h2 id="annotation-editor-title" className="annotation-editor-title">
                        {mode === 'create' ? 'New Annotation' : 'Edit Annotation'}
                    </h2>
                    <button
                        className="annotation-editor-close"
                        onClick={onClose}
                        aria-label="Close editor"
                    >
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path
                                d="M15 5L5 15M5 5l10 10"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                            />
                        </svg>
                    </button>
                </div>

                <div className="annotation-editor-body">
                    {/* Highlight Preview */}
                    <div className="annotation-editor-section">
                        <label className="annotation-editor-label">Highlighted Text</label>
                        <div className={`annotation-highlight-preview color-${color}`}>
                            {highlightText.substring(0, 200)}
                            {highlightText.length > 200 && '...'}
                        </div>
                    </div>

                    {/* Color Picker */}
                    <div className="annotation-editor-section">
                        <label className="annotation-editor-label">Highlight Color</label>
                        <ColorPicker selectedColor={color} onColorChange={setColor} />
                    </div>

                    {/* Note Textarea */}
                    <div className="annotation-editor-section">
                        <label className="annotation-editor-label" htmlFor="annotation-note">
                            Note (Markdown supported)
                        </label>
                        <textarea
                            id="annotation-note"
                            className="annotation-note-textarea"
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            placeholder="Add your thoughts, insights, or connections..."
                        />
                    </div>

                    {/* Tags */}
                    <div className="annotation-editor-section">
                        <label className="annotation-editor-label">Tags</label>
                        <div className="annotation-tags-input">
                            {tags.map((tag) => (
                                <div key={tag} className="annotation-tag-chip">
                                    <span>{tag}</span>
                                    <button
                                        className="annotation-tag-remove"
                                        onClick={() => handleRemoveTag(tag)}
                                        aria-label={`Remove tag ${tag}`}
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                            <input
                                type="text"
                                className="annotation-tag-input"
                                value={tagInput}
                                onChange={(e) => setTagInput(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        handleAddTag();
                                    }
                                }}
                                placeholder="Add tag..."
                            />
                        </div>
                    </div>
                </div>

                <div className="annotation-editor-footer">
                    <div className="annotation-save-status">
                        {mode === 'edit' && (
                            <>
                                {saveStatus === 'saving' && (
                                    <>
                                        <div className="annotation-save-spinner" />
                                        <span>Saving...</span>
                                    </>
                                )}
                                {saveStatus === 'saved' && <span className="saved">✓ Saved</span>}
                                {saveStatus === 'error' && <span className="error">Failed to save</span>}
                            </>
                        )}
                        <Button onClick={handleSave} disabled={saveStatus === 'saving'}>
                            {mode === 'create' ? 'Create' : 'Save'}
                        </Button>
                    </div>
                </div>
            </div>
        </>
    );
};
