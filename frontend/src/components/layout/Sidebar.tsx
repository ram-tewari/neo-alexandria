/**
 * Sidebar Component
 * Collapsible side navigation with sorting controls
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, ArrowUp, ArrowDown } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import './Sidebar.css';

export interface SidebarItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href: string;
  badge?: number;
}

export interface SortOption {
  id: string;
  label: string;
  direction: 'asc' | 'desc';
}

export interface SidebarProps {
  items: SidebarItem[];
  defaultCollapsed?: boolean;
  sortOptions?: SortOption[];
  onSort?: (option: SortOption) => void;
}

export function Sidebar({
  items,
  defaultCollapsed = false,
  sortOptions = [],
  onSort,
}: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const [activeSort, setActiveSort] = useState<string | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const { theme } = useTheme();

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleSort = (option: SortOption) => {
    setActiveSort(option.id);
    onSort?.(option);
  };

  // Keyboard shortcut: Ctrl+X
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'x') {
        e.preventDefault();
        toggleCollapse();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCollapsed]);

  return (
    <motion.aside
      className={`sidebar ${isCollapsed ? 'sidebar--collapsed' : ''}`}
      initial={false}
      animate={{
        width: isCollapsed ? '80px' : '240px',
      }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
    >
      {/* Collapse Arrow Toggle */}
      <button
        onClick={toggleCollapse}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="sidebar__toggle-arrow"
        aria-label={isCollapsed ? 'Expand sidebar (Ctrl+X)' : 'Collapse sidebar (Ctrl+X)'}
        aria-expanded={!isCollapsed}
        type="button"
      >
        <motion.div
          animate={{ rotate: isCollapsed ? 180 : 0 }}
          transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        >
          <ChevronLeft size={16} aria-hidden="true" />
        </motion.div>
        
        {/* Tooltip */}
        {showTooltip && (
          <motion.div
            className="sidebar__tooltip"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.2 }}
          >
            <kbd className="sidebar__kbd">Ctrl</kbd>
            <span>+</span>
            <kbd className="sidebar__kbd">X</kbd>
          </motion.div>
        )}
      </button>

      {/* Navigation Items */}
      <nav className="sidebar__nav">
        <ul className="sidebar__nav-list">
          {items.map((item) => (
            <li key={item.id} className="sidebar__nav-item">
              <a href={item.href} className="sidebar__nav-link">
                <span className="sidebar__nav-icon">{item.icon}</span>
                {!isCollapsed && (
                  <motion.span
                    className="sidebar__nav-label"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {item.label}
                  </motion.span>
                )}
                {!isCollapsed && item.badge !== undefined && (
                  <span className="sidebar__nav-badge">{item.badge}</span>
                )}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Sort Controls */}
      {sortOptions.length > 0 && !isCollapsed && (
        <div className="sidebar__sort">
          <h3 className="sidebar__sort-title">Sort</h3>
          <div className="sidebar__sort-options">
            {sortOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => handleSort(option)}
                className={`sidebar__sort-btn ${
                  activeSort === option.id ? 'sidebar__sort-btn--active' : ''
                }`}
                aria-label={`Sort by ${option.label} ${option.direction === 'asc' ? 'ascending' : 'descending'}`}
                type="button"
              >
                <span>{option.label}</span>
                <motion.div
                  animate={{
                    rotate: option.direction === 'desc' ? 180 : 0,
                  }}
                  transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
                >
                  {option.direction === 'asc' ? (
                    <ArrowUp size={16} aria-hidden="true" />
                  ) : (
                    <ArrowDown size={16} aria-hidden="true" />
                  )}
                </motion.div>
              </button>
            ))}
          </div>
        </div>
      )}
    </motion.aside>
  );
}
