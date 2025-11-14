import { motion } from 'framer-motion';
import { Icon } from '../common/Icon';
import { icons } from '../../config/icons';
import { pageVariants } from '../../animations/variants';
import './KnowledgeGraph.css';

export const KnowledgeGraph = () => {
  return (
    <motion.div
      className="container"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div className="page-header">
        <h1 className="page-title">Knowledge Graph</h1>
        <p className="page-subtitle">Visualize connections between your resources.</p>
      </div>

      <div className="graph-container">
        <div className="graph-placeholder">
          <Icon icon={icons.graph} size={48} />
          <h3>Knowledge Graph Visualization</h3>
          <p>Interactive graph visualization will be displayed here.</p>
          <p className="graph-hint">Connect resources, create relationships, and explore your knowledge network.</p>
        </div>
      </div>
    </motion.div>
  );
};
