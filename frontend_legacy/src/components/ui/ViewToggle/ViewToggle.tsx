/**
 * ViewToggle component
 * Switches between grid and table views
 */

import React from 'react';
import { motion } from 'framer-motion';
import { scalePress } from '../../../lib/utils/animations';

export type ViewMode = 'grid' | 'table';

export interface ViewToggleProps {
  /** Current view mode */
  value: ViewMode;
  /** Callback when view mode changes */
  onChange: (view: ViewMode) => void;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Toggle between grid and table views
 */
export const ViewToggle: React.FC<ViewToggleProps> = ({
  value,
  onChange,
  className = '',
}) => {
  return (
    <div className={`inline-flex rounded-lg bg-gray-200 dark:bg-gray-800 p-1 ${className}`} role="group">
      <motion.button
        onClick={() => onChange('grid')}
        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors duration-150 ${
          value === 'grid'
            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
        }`}
        aria-label="Grid view"
        aria-pressed={value === 'grid'}
        {...scalePress}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
          />
        </svg>
      </motion.button>
      
      <motion.button
        onClick={() => onChange('table')}
        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors duration-150 ${
          value === 'table'
            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
        }`}
        aria-label="Table view"
        aria-pressed={value === 'table'}
        {...scalePress}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 10h16M4 14h16M4 18h16"
          />
        </svg>
      </motion.button>
    </div>
  );
};
