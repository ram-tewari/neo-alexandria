/**
 * Collection Sidebar Component
 * 
 * Collapsible sidebar with collection tree navigation
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
import { Icon } from '../common/Icon';
import { icons } from '@/config/icons';
import { CollectionNode } from './CollectionNode';
import { useCollectionStore, useUIStore } from '@/store';
import type { CollectionNode as CollectionNodeType } from '@/types/collection';
import './CollectionSidebar.css';

export const CollectionSidebar = () => {
  const { collectionTree, activeCollection, fetchCollections } = useCollectionStore();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewCollectionModal, setShowNewCollectionModal] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(280);
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      
      const newWidth = e.clientX;
      if (newWidth >= 200 && newWidth <= 500) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const filteredTree = searchQuery
    ? collectionTree.filter((node) =>
        node.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : collectionTree;

  return (
    <>
      <motion.aside
        ref={sidebarRef}
        className={`collection-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}
        initial={false}
        animate={{
          width: sidebarCollapsed ? 0 : sidebarWidth,
          opacity: sidebarCollapsed ? 0 : 1,
        }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      >
        {/* Resize Handle */}
        {!sidebarCollapsed && (
          <motion.div
            className="collection-sidebar__resize-handle"
            onMouseDown={handleMouseDown}
            whileHover={{ scale: 1.5 }}
            animate={{
              opacity: isResizing ? 1 : 0.5,
            }}
          />
        )}
        <div className="collection-sidebar__header">
          <motion.div 
            className="collection-sidebar__title"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <motion.div
              whileHover={{ rotate: 360, scale: 1.2 }}
              transition={{ duration: 0.6 }}
              style={{ display: 'flex' }}
            >
              <Icon icon={icons.library} size={20} />
            </motion.div>
            <motion.h2
              style={{
                background: 'linear-gradient(135deg, var(--white), var(--purple-bright))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              Collections
            </motion.h2>
          </motion.div>
          <motion.button
            className="collection-sidebar__toggle"
            onClick={toggleSidebar}
            title="Collapse sidebar"
            whileHover={{ scale: 1.15, rotate: 180 }}
            whileTap={{ scale: 0.9 }}
            transition={{ duration: 0.3 }}
          >
            <Icon icon={icons.chevronLeft} size={18} />
          </motion.button>
        </div>

        <div className="collection-sidebar__search">
          <Icon icon={icons.search} size={16} />
          <input
            type="text"
            placeholder="Search collections..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')}>
              <Icon icon={icons.close} size={14} />
            </button>
          )}
        </div>

        <div className="collection-sidebar__content">
          {filteredTree.length === 0 ? (
            <div className="collection-sidebar__empty">
              <p>No collections found</p>
              {searchQuery && <span>Try a different search</span>}
            </div>
          ) : (
            <div className="collection-sidebar__tree">
              {filteredTree.map((node) => (
                <CollectionNode key={node.id} node={node} />
              ))}
            </div>
          )}
        </div>

        {/* Stats Section */}
        <motion.div 
          className="collection-sidebar__stats"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="collection-sidebar__stat">
            <motion.span 
              className="collection-sidebar__stat-value"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {collectionTree.length}
            </motion.span>
            <span className="collection-sidebar__stat-label">Total</span>
          </div>
          <div className="collection-sidebar__stat">
            <motion.span 
              className="collection-sidebar__stat-value"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
            >
              {collectionTree.filter(n => n.isExpanded).length}
            </motion.span>
            <span className="collection-sidebar__stat-label">Open</span>
          </div>
          <div className="collection-sidebar__stat">
            <motion.span 
              className="collection-sidebar__stat-value"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
            >
              {activeCollection ? 1 : 0}
            </motion.span>
            <span className="collection-sidebar__stat-label">Active</span>
          </div>
        </motion.div>

        <div className="collection-sidebar__footer">
          <motion.button
            className="collection-sidebar__new-btn purple-ripple"
            onClick={() => setShowNewCollectionModal(true)}
            whileHover={{ scale: 1.03, y: -2 }}
            whileTap={{ scale: 0.97 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <motion.div
              whileHover={{ rotate: 90 }}
              transition={{ duration: 0.3 }}
              style={{ display: 'flex' }}
            >
              <Icon icon={icons.add} size={18} />
            </motion.div>
            <span>New Collection</span>
          </motion.button>
        </div>
      </motion.aside>

      {/* Collapsed sidebar toggle button */}
      <AnimatePresence>
        {sidebarCollapsed && (
          <motion.button
            className="collection-sidebar__expand-btn"
            onClick={toggleSidebar}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            title="Expand sidebar"
          >
            <Icon icon={icons.chevronRight} size={20} />
          </motion.button>
        )}
      </AnimatePresence>
    </>
  );
};
