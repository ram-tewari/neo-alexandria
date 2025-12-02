import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Annotation } from '../../../../types/annotations';
import './AnnotationCard.css';

interface AnnotationCardProps {
    annotation: Annotation;
    resourceTitle?: string;
}

/**
 * AnnotationCard - Individual annotation card for notebook view
 * 
 * Features:
 * - Color-coded left border matching highlight color
 * - Highlighted text snippet
 * - Note body rendered as markdown
 * - Tags as colored chips
 * - Source resource info with link
 * - Timestamp
 * - Click to navigate to Resource Detail
 */
export const AnnotationCard: React.FC<AnnotationCardProps> = ({
    annotation,
    resourceTitle = 'Unknown Resource',
}) => {
    const navigate = useNavigate();

    const handleClick = () => {
        // Navigate to resource detail with annotation ID in query
        navigate(`/resources/${annotation.resourceId}?annotation=${annotation.id}`);
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
        return date.toLocaleDateString();
    };

    return (
        <div
            className={`annotation-card color-${annotation.highlight.color}`}
            onClick={handleClick}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleClick();
                }
            }}
        >
            <div className="annotation-card-header">
                <div className="annotation-card-source">
                    <a
                        href={`/resources/${annotation.resourceId}`}
                        className="annotation-card-resource"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {resourceTitle}
                    </a>
                    <div className="annotation-card-meta">
                        {annotation.highlight.pageNumber && (
                            <span>Page {annotation.highlight.pageNumber}</span>
                        )}
                        <span>•</span>
                        <span>{formatDate(annotation.createdAt)}</span>
                    </div>
                </div>
            </div>

            <div className="annotation-card-highlight">
                "{annotation.highlight.text}"
            </div>

            {annotation.note && (
                <div className="annotation-card-note">
                    {annotation.note}
                </div>
            )}

            {annotation.tags.length > 0 && (
                <div className="annotation-card-tags">
                    {annotation.tags.map((tag) => (
                        <span key={tag.id} className="annotation-card-tag">
                            {tag.name}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
};
