import React, { useState, useEffect } from 'react';
import type { Annotation } from '../../../../types/annotations';
import './AnnotationSidebar.css';

interface AnnotationSidebarProps {
    annotations: Annotation[];
    activeAnnotationId?: string;
    onAnnotationClick: (annotation: Annotation) => void;
    isLoading?: boolean;
}

/**
 * AnnotationSidebar - Collapsible sidebar showing all annotations for current resource
 * 
 * Features:
 * - List annotations in reading order
 * - Color-coded badges matching highlight colors
 * - Click annotation to scroll document
 * - Active annotation highlighted when scrolling
 * - Empty state when no annotations
 * - Loading skeleton
 */
export const AnnotationSidebar: React.FC<AnnotationSidebarProps> = ({
    annotations,
    activeAnnotationId,
    onAnnotationClick,
    isLoading = false,
}) => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    // Sort annotations by page number and offset
    const sortedAnnotations = [...annotations].sort((a, b) => {
        const pageA = a.highlight.pageNumber || 0;
        const pageB = b.highlight.pageNumber || 0;
        if (pageA !== pageB) return pageA - pageB;
        return a.highlight.startOffset - b.highlight.startOffset;
    });

    if (isLoading) {
        return (
            <div className={`annotation-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
                <button
                    className="annotation-sidebar-toggle"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    aria-label={isCollapsed ? 'Show annotations' : 'Hide annotations'}
                >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path
                            d={isCollapsed ? 'M6 12L10 8L6 4' : 'M10 12L6 8L10 4'}
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                    </svg>
                </button>

                <div className="annotation-sidebar-header">
                    <h3 className="annotation-sidebar-title">Annotations</h3>
                </div>

                <div className="annotation-sidebar-skeleton">
                    {[...Array(3)].map((_, i) => (
                        <div key={i} className="annotation-sidebar-skeleton-item" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className={`annotation-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
            <button
                className="annotation-sidebar-toggle"
                onClick={() => setIsCollapsed(!isCollapsed)}
                aria-label={isCollapsed ? 'Show annotations' : 'Hide annotations'}
            >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path
                        d={isCollapsed ? 'M6 12L10 8L6 4' : 'M10 12L6 8L10 4'}
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                </svg>
            </button>

            <div className="annotation-sidebar-header">
                <h3 className="annotation-sidebar-title">
                    Annotations ({annotations.length})
                </h3>
            </div>

            <div className="annotation-sidebar-list">
                {sortedAnnotations.length === 0 ? (
                    <div className="annotation-sidebar-empty">
                        <svg
                            className="annotation-sidebar-empty-icon"
                            viewBox="0 0 48 48"
                            fill="none"
                        >
                            <path
                                d="M12 10h24a4 4 0 014 4v24a4 4 0 01-4 4H12a4 4 0 01-4-4V14a4 4 0 014-4z"
                                stroke="currentColor"
                                strokeWidth="2"
                            />
                            <path
                                d="M16 18h16M16 24h16M16 30h10"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                            />
                        </svg>
                        <p className="annotation-sidebar-empty-text">
                            No annotations yet. Select text to create your first annotation.
                        </p>
                    </div>
                ) : (
                    sortedAnnotations.map((annotation) => (
                        <div
                            key={annotation.id}
                            className={`annotation-sidebar-item color-${annotation.highlight.color} ${annotation.id === activeAnnotationId ? 'active' : ''
                                }`}
                            onClick={() => onAnnotationClick(annotation)}
                            role="button"
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    onAnnotationClick(annotation);
                                }
                            }}
                        >
                            <div className="annotation-sidebar-text">
                                {annotation.highlight.text}
                            </div>
                            {annotation.note && (
                                <div className="annotation-sidebar-text" style={{ fontSize: '12px', opacity: 0.8 }}>
                                    {annotation.note.substring(0, 80)}
                                    {annotation.note.length > 80 && '...'}
                                </div>
                            )}
                            <div className="annotation-sidebar-meta">
                                {annotation.highlight.pageNumber && (
                                    <span className="annotation-sidebar-page">
                                        Page {annotation.highlight.pageNumber}
                                    </span>
                                )}
                                {annotation.tags.length > 0 && (
                                    <span>
                                        {annotation.tags.map(t => t.name).join(', ')}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
