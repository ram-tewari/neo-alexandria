import React from 'react';
import './AnnotationsTab.css';

interface AnnotationsTabProps {
  resourceId: string;
}

/**
 * AnnotationsTab - Displays resource annotations and highlights (placeholder)
 * 
 * Future features:
 * - Personal notes and highlights
 * - Collaborative annotations
 * - Annotation search and filtering
 * - Export annotations
 */
export const AnnotationsTab: React.FC<AnnotationsTabProps> = ({ resourceId }) => {
  return (
    <div
      role="tabpanel"
      id="panel-annotations"
      aria-labelledby="tab-annotations"
      className="annotations-tab"
    >
      <div className="placeholder-content">
        <div className="placeholder-icon">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="12" y="8" width="40" height="48" rx="4" stroke="currentColor" strokeWidth="2" opacity="0.3" />
            <line x1="20" y1="20" x2="44" y2="20" stroke="currentColor" strokeWidth="2" opacity="0.3" />
            <line x1="20" y1="28" x2="44" y2="28" stroke="currentColor" strokeWidth="2" opacity="0.3" />
            <line x1="20" y1="36" x2="36" y2="36" stroke="currentColor" strokeWidth="2" opacity="0.3" />
            <path d="M48 40L52 44L48 48L44 44L48 40Z" fill="currentColor" opacity="0.3" />
          </svg>
        </div>
        <h3>Annotations & Notes</h3>
        <p>
          Add personal notes, highlights, and annotations to your resources. Organize your thoughts
          and insights as you read and research.
        </p>
        <div className="placeholder-features">
          <div className="placeholder-feature">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2L12 8L18 10L12 12L10 18L8 12L2 10L8 8L10 2Z" fill="currentColor" />
            </svg>
            <span>Highlight important passages</span>
          </div>
          <div className="placeholder-feature">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2L12 8L18 10L12 12L10 18L8 12L2 10L8 8L10 2Z" fill="currentColor" />
            </svg>
            <span>Add personal notes and comments</span>
          </div>
          <div className="placeholder-feature">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2L12 8L18 10L12 12L10 18L8 12L2 10L8 8L10 2Z" fill="currentColor" />
            </svg>
            <span>Search and filter annotations</span>
          </div>
        </div>
        <p className="placeholder-status">Coming soon in a future update</p>
      </div>
    </div>
  );
};
