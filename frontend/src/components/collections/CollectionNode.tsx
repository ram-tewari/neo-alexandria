/**
 * Collection Node Component
 * 
 * Recursive tree node for collection hierarchy
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '../common/Icon';
import { icons } from '@/config/icons';
import { useCollectionStore } from '@/store';
import type { CollectionNode as CollectionNodeType } from '@/types/collection';
import './CollectionNode.css';

interface CollectionNodeProps {
  node: CollectionNodeType;
}

export const CollectionNode = ({ node }: CollectionNodeProps) => {
  const { activeCollection, selectCollection, toggleCollectionExpanded } = useCollectionStore();
  const [showContextMenu, setShowContextMenu] = useState(false);

  const isActive = activeCollection?.id === node.id;
  const hasChildren = node.children && node.children.length > 0;

  const handleClick = () => {
    selectCollection(node.id);
  };

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (hasChildren) {
      toggleCollectionExpanded(node.id);
    }
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowContextMenu(true);
  };

  return (
    <div className="collection-node" style={{ paddingLeft: `${node.depth * 1}rem` }}>
      <motion.div
        className={`collection-node__item ${isActive ? 'active' : ''}`}
        onClick={handleClick}
        onContextMenu={handleContextMenu}
        whileHover={{ x: 2 }}
        whileTap={{ scale: 0.98 }}
      >
        {hasChildren && (
          <button className="collection-node__toggle" onClick={handleToggle}>
            <motion.div
              animate={{ rotate: node.isExpanded ? 90 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <Icon icon={icons.chevronRight} size={14} />
            </motion.div>
          </button>
        )}

        <div className="collection-node__icon">
          <Icon icon={icons.library} size={16} />
        </div>

        <span className="collection-node__name">{node.name}</span>

        {node.resource_count > 0 && (
          <span className="collection-node__count">{node.resource_count}</span>
        )}
      </motion.div>

      <AnimatePresence>
        {hasChildren && node.isExpanded && (
          <motion.div
            className="collection-node__children"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {node.children.map((child) => (
              <CollectionNode key={child.id} node={child} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Context Menu - TODO: Implement full context menu */}
      {showContextMenu && (
        <div
          className="collection-node__context-overlay"
          onClick={() => setShowContextMenu(false)}
        />
      )}
    </div>
  );
};
