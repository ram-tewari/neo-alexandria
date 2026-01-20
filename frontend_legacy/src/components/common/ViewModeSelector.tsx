/**
 * View Mode Selector Component
 * 
 * Toggle buttons for switching between Grid, List, Headlines, and Masonry views
 */

import { motion } from 'framer-motion';
import { Icon } from './Icon';
import { icons } from '@/config/icons';
import type { ViewMode } from '@/types/api';
import './ViewModeSelector.css';

interface ViewModeSelectorProps {
  currentMode: ViewMode;
  onChange: (mode: ViewMode) => void;
}

const viewModes: { mode: ViewMode; icon: any; label: string }[] = [
  { mode: 'grid', icon: icons.grid, label: 'Grid' },
  { mode: 'list', icon: icons.list, label: 'List' },
  { mode: 'headlines', icon: icons.columns, label: 'Headlines' },
  { mode: 'masonry', icon: icons.masonry, label: 'Masonry' },
];

export const ViewModeSelector = ({ currentMode, onChange }: ViewModeSelectorProps) => {
  return (
    <div className="view-mode-selector">
      {viewModes.map(({ mode, icon, label }) => (
        <motion.button
          key={mode}
          className={`view-mode-btn ${currentMode === mode ? 'active' : ''}`}
          onClick={() => onChange(mode)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          title={label}
        >
          <Icon icon={icon} size={18} />
          <span className="view-mode-label">{label}</span>
          
          {currentMode === mode && (
            <motion.div
              className="view-mode-indicator"
              layoutId="activeViewMode"
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            />
          )}
        </motion.button>
      ))}
    </div>
  );
};
