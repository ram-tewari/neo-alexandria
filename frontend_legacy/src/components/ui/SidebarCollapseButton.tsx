import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useSidebar } from './sidebar';
import './SidebarCollapseButton.css';

interface SidebarCollapseButtonProps {
  showKeyboardHint?: boolean;
}

export function SidebarCollapseButton({ showKeyboardHint = true }: SidebarCollapseButtonProps) {
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === 'collapsed';

  return (
    <div className="sidebar-collapse-wrapper">
      <motion.button
        className="sidebar-collapse-button"
        onClick={toggleSidebar}
        aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <motion.div
          className="collapse-arrow"
          animate={{
            x: isCollapsed ? [0, 1.5, 0] : [0, -1.5, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          {isCollapsed ? (
            <ChevronRight size={14} />
          ) : (
            <ChevronLeft size={14} />
          )}
        </motion.div>

        {showKeyboardHint && (
          <motion.div
            className="keyboard-hint"
            initial={{ opacity: 0, y: 5 }}
            whileHover={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <kbd>Ctrl</kbd>
            <span>+</span>
            <kbd>B</kbd>
          </motion.div>
        )}
      </motion.button>
    </div>
  );
}
