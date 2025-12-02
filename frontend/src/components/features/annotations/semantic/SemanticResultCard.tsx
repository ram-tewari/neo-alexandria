import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { SemanticAnnotationResult } from '../../../../types/annotations';
import './SemanticResultCard.css';

interface SemanticResultCardProps {
    result: SemanticAnnotationResult;
}

/**
 * SemanticResultCard - Result card for semantic search
 * 
 * Features:
 * - Annotation snippet and note
 * - Similarity score badge (percentage)
 * - Color-coded border matching highlight
 * - Source resource link
 * - Related annotations section
 */
export const SemanticResultCard: React.FC<SemanticResultCardProps> = ({ result }) => {
    const navigate = useNavigate();
    const { annotation, similarityScore, relatedAnnotations } = result;

    const handleClick = () => {
        navigate(`/resources/${annotation.resourceId}?annotation=${annotation.id}`);
    };

    const similarityPercentage = Math.round(similarityScore * 100);

    return (
        <div
            className={`semantic-result-card color-${annotation.highlight.color}`}
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
            <div className="semantic-result-header">
                <div className="semantic-result-similarity">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                        <path
                            d="M7 1l1.5 4.5H13L9 9l1.5 4.5L7 10 3.5 13.5 5 9 1 5.5h4.5L7 1z"
                            fill="currentColor"
                        />
                    </svg>
                    {similarityPercentage}% match
                </div>
            </div>

            <div className="semantic-result-content">
                <div className="semantic-result-highlight">
                    "{annotation.highlight.text}"
                </div>
                {annotation.note && (
                    <div className="semantic-result-note">{annotation.note}</div>
                )}
            </div>

            {relatedAnnotations && relatedAnnotations.length > 0 && (
                <div className="semantic-result-related">
                    <div className="semantic-result-related-title">Related Annotations</div>
                    <div className="semantic-result-related-items">
                        {relatedAnnotations.slice(0, 3).map((related) => (
                            <div
                                key={related.annotation.id}
                                className="semantic-result-related-item"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    navigate(
                                        `/resources/${related.annotation.resourceId}?annotation=${related.annotation.id}`
                                    );
                                }}
                            >
                                {related.annotation.highlight.text.substring(0, 60)}...
                                ({Math.round(related.score * 100)}% similar)
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
