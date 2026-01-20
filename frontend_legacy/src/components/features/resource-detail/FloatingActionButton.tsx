import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ResourceRead } from '../../../lib/api/types';
import './FloatingActionButton.css';

interface FloatingActionButtonProps {
  resource: ResourceRead;
}

/**
 * FloatingActionButton - Floating action button that appears on scroll
 * 
 * Features:
 * - Shows when scrolled past 200px
 * - Animated scale transition
 * - Fixed position at bottom-right
 * - Opens resource in viewer/external link
 */
export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({ resource }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.scrollY > 200;
      setIsVisible(scrolled);
    };

    // Check initial scroll position
    handleScroll();

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleClick = () => {
    // If resource has a URL, open it in a new tab
    if (resource.url) {
      window.open(resource.url, '_blank', 'noopener,noreferrer');
    } else {
      // Otherwise, scroll to content tab
      const contentTab = document.getElementById('tab-content');
      contentTab?.click();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.button
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{
            type: 'spring',
            stiffness: 260,
            damping: 20,
          }}
          onClick={handleClick}
          className="floating-action-button"
          aria-label={resource.url ? 'Open resource in new tab' : 'View content'}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            {resource.url ? (
              // External link icon
              <path
                d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5zM5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"
                fill="currentColor"
              />
            ) : (
              // Document icon
              <path
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                fill="currentColor"
              />
            )}
          </svg>
          <span className="fab-label">
            {resource.url ? 'Open' : 'View'}
          </span>
        </motion.button>
      )}
    </AnimatePresence>
  );
};
