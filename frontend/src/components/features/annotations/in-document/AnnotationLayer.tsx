import React from 'react';
import type { Annotation } from '../../../../types/annotations';
import './AnnotationLayer.css';

interface AnnotationLayerProps {
    annotations: Annotation[];
    onAnnotationClick: (annotation: Annotation) => void;
    containerRef: React.RefObject<HTMLElement>;
}

/**
 * AnnotationLayer - Renders highlight overlays on top of content
 * 
 * Features:
 * - Maps annotation offsets to screen coordinates
 * - Colored highlight overlays with semi-transparency
 * - Hover effect increases opacity and shows note icon
 * - Click handler opens annotation editor
 * - Smooth fade-in animation for new highlights
 */
export const AnnotationLayer: React.FC<AnnotationLayerProps> = ({
    annotations,
    onAnnotationClick,
    containerRef,
}) => {
    // For now, we'll use a simplified positioning approach
    // In a production app, you'd calculate positions based on actual text ranges
    const getHighlightPosition = (annotation: Annotation) => {
        // This is a placeholder - actual implementation would use:
        // - Document Range API for text positions
        // - PDF.js text layer coordinates for PDFs
        // - Intersection with viewport for scrolling

        // For demo purposes, we'll position highlights based on page number
        const pageHeight = 1000; // Approximate page height
        const pageNumber = annotation.highlight.pageNumber || 1;
        const yOffset = (pageNumber - 1) * pageHeight;

        return {
            top: yOffset + 100, // Placeholder offset
            left: 50,
            width: 300,
            height: 20,
        };
    };

    return (
        <div className="annotation-layer">
            {annotations.map((annotation) => {
                const position = getHighlightPosition(annotation);

                return (
                    <div
                        key={annotation.id}
                        className={`annotation-highlight color-${annotation.highlight.color}`}
                        style={{
                            top: position.top,
                            left: position.left,
                            width: position.width,
                            height: position.height,
                        }}
                        onClick={() => onAnnotationClick(annotation)}
                        role="button"
                        tabIndex={0}
                        aria-label={`Annotation: ${annotation.highlight.text.substring(0, 50)}...`}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                onAnnotationClick(annotation);
                            }
                        }}
                    >
                        {annotation.note && (
                            <div className="annotation-icon">
                                <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path
                                        d="M3 3h10v7l-3 3H3V3z"
                                        fill="currentColor"
                                    />
                                </svg>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
};
