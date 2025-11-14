import './KnowledgeGraph.css';

export const KnowledgeGraph = () => {
  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Knowledge Graph</h1>
        <p className="page-subtitle">Visualize connections between your resources.</p>
      </div>

      <div className="graph-container">
        <div className="graph-placeholder">
          <i className="fas fa-project-diagram"></i>
          <h3>Knowledge Graph Visualization</h3>
          <p>Interactive graph visualization will be displayed here.</p>
          <p className="graph-hint">Connect resources, create relationships, and explore your knowledge network.</p>
        </div>
      </div>
    </div>
  );
};
