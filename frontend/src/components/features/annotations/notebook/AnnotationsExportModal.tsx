import React, { useState, useRef } from 'react';
import { Button } from '../../../ui/Button/Button';
import { useFocusTrap } from '../../../../lib/hooks/useFocusTrap';
import { exportAnnotations } from '../../../../lib/api/annotations';
import { useToast } from '../../../../contexts/ToastContext';
import type { ExportFormat, AnnotationSearchFilters } from '../../../../types/annotations';
import './AnnotationsExportModal.css';

interface AnnotationsExportModalProps {
    filters?: AnnotationSearchFilters;
    onClose: () => void;
}

/**
 * AnnotationsExportModal - Modal for exporting annotations
 * 
 * Features:
 * - Format selection (Markdown / JSON)
 * - Preview area
 * - Export button triggers download
 * - Loading state during export
 * - Error handling with toast
 */
export const AnnotationsExportModal: React.FC<AnnotationsExportModalProps> = ({
    filters,
    onClose,
}) => {
    const [format, setFormat] = useState<ExportFormat>('markdown');
    const [isExporting, setIsExporting] = useState(false);
    const modalRef = useRef<HTMLDivElement>(null);
    const { showToast } = useToast();

    useFocusTrap(modalRef, true);

    const handleExport = async () => {
        setIsExporting(true);
        try {
            const result = await exportAnnotations(format, filters);

            // Create download link
            const blob = new Blob([result.content], { type: result.mimeType });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = result.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

            showToast({ variant: 'success', message: 'Annotations exported successfully' });
            onClose();
        } catch (error) {
            showToast({ variant: 'error', message: 'Failed to export annotations' });
        } finally {
            setIsExporting(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Escape') {
            onClose();
        }
    };

    return (
        <>
            <div className="annotations-export-modal-overlay" onClick={onClose} />
            <div
                ref={modalRef}
                className="annotations-export-modal"
                role="dialog"
                aria-labelledby="export-modal-title"
                aria-modal="true"
                onKeyDown={handleKeyDown}
            >
                <div className="annotations-export-modal-header">
                    <h2 id="export-modal-title" className="annotations-export-modal-title">
                        Export Annotations
                    </h2>
                    <button
                        className="annotations-export-modal-close"
                        onClick={onClose}
                        aria-label="Close export modal"
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

                <div className="annotations-export-modal-body">
                    <label className="annotations-export-format-label">
                        Select Export Format
                    </label>
                    <div className="annotations-export-formats">
                        <div
                            className={`annotations-export-format-option ${format === 'markdown' ? 'selected' : ''
                                }`}
                            onClick={() => setFormat('markdown')}
                            role="radio"
                            aria-checked={format === 'markdown'}
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    setFormat('markdown');
                                }
                            }}
                        >
                            <div className="annotations-export-format-icon">📝</div>
                            <div className="annotations-export-format-name">Markdown</div>
                            <div className="annotations-export-format-desc">
                                Human-readable format
                            </div>
                        </div>

                        <div
                            className={`annotations-export-format-option ${format === 'json' ? 'selected' : ''
                                }`}
                            onClick={() => setFormat('json')}
                            role="radio"
                            aria-checked={format === 'json'}
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    setFormat('json');
                                }
                            }}
                        >
                            <div className="annotations-export-format-icon">📊</div>
                            <div className="annotations-export-format-name">JSON</div>
                            <div className="annotations-export-format-desc">
                                Machine-readable format
                            </div>
                        </div>
                    </div>

                    <div className="annotations-export-preview">
                        <div className="annotations-export-preview-label">Preview</div>
                        <div className="annotations-export-preview-content">
                            {format === 'markdown' ? (
                                `# Annotations Export\n\n## Resource Title\n\n> "Highlighted text..."\n\n**Note:** Your annotation note here.\n\n**Tags:** tag1, tag2\n\n---`
                            ) : (
                                `{\n  "annotations": [\n    {\n      "id": "...",\n      "highlight": {...},\n      "note": "...",\n      "tags": [...]\n    }\n  ]\n}`
                            )}
                        </div>
                    </div>
                </div>

                <div className="annotations-export-modal-footer">
                    {isExporting ? (
                        <div className="annotations-export-loading">
                            <div className="annotations-export-spinner" />
                            <span>Exporting...</span>
                        </div>
                    ) : (
                        <>
                            <Button variant="secondary" onClick={onClose}>
                                Cancel
                            </Button>
                            <Button onClick={handleExport}>
                                Export {format === 'markdown' ? 'Markdown' : 'JSON'}
                            </Button>
                        </>
                    )}
                </div>
            </div>
        </>
    );
};
