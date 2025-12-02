import React from 'react';
import './GraphTab.css';

interface GraphTabProps {
  resourceId: string;
}

/**
 * GraphTab - Displays resource relationship graph (placeholder)
 * 
 * Future features:
 * - Interactive knowledge graph visualization
 * - Related resources and connections
 * - Citation network
 * - Semantic relationships
 */
export const GraphTab: React.FC<GraphTabProps> = ({ resourceId }) => {
  return (
    <div
      role="tabpanel"
      id="panel-graph"
      aria-labelledby="tab-graph"
      className="graph-tab"
    >
      <div className="placeholder-content">
        <div className="placeholder-icon">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="12" r="6" fill="currentColor" opacity="0.3" />
            <circle cx="12" cy="32" r="6" fill="currentColor" opacity="0.3" />
            <circle cx="52" cy="32" r="6" fill="currentColor" opacity="0.3" />
            <circle cx="32" cy="52" r="6" fill="currentColor" opacity="0.3" />
            <line x1="32" y1="18" x2="32" y2="46" stroke="currentColor" strokeWidth="2" opacity="0.3" />
            <line x1="18" y1="32" x2="46" y2="32" stroke="currentColor" strokeWidth="2" opacity="0.3" />
            <line x1="26" y1="18" x2="18" y2="26" stroke="currentColor" strokeWidth="2" opacity="0.3" />
            <line x1="38" y1="18" x2="46" y2="26" stroke="currentColor" strokeWidth="2" opacity="0.3" />
          </svg>
        </div>
        <h3>Knowledge Graph</h3>
        <p>
          The knowledge graph visualization will show how this resource connects to other resources
          in your library through citations, topics, and semantic relationships.
        </p>
        <div className="placeholder-features">
          <div className="placeholder-feature">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2L12 8L18 10L12 12L10 18L8 12L2 10L8 8L10 2Z" fill="currentColor" />
            </svg>
            <span>Interactive graph visualization</span>
          </div>
          <div className="placeholder-feature">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2L12 8L18 10L12 12L10 18L8 12L2 10L8 8L10 2Z" fill="currentColor" />
            </svg>
            <span>Citation network analysis</span>
          </div>
          <div className="placeholder-feature">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2L12 8L18 10L12 12L10 18L8 12L2 10L8 8L10 2Z" fill="currentColor" />
            </svg>
            <span>Semantic relationship mapping</span>
          </div>
        </div>
        <p className="placeholder-status">Coming soon in a future update</p>
      </div>
    </div>
  );
};
