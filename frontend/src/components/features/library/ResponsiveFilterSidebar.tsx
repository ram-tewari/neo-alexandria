/**
 * ResponsiveFilterSidebar component
 * 
 * Provides responsive behavior for the filter sidebar:
 * - Desktop (≥768px): Fixed sidebar on the left
 * - Mobile (<768px): Collapsible drawer with overlay
 * 
 * Features:
 * - Smooth transitions between states
 * - Keyboard accessible (Escape to close)
 * - Focus trap when drawer is open
 * - Backdrop click to close
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FilterSidebar, type FilterFacets } from './FilterSidebar';
import { Button } from '../../ui/Button/Button';
import type { ResourceFilters } from '../../../lib/hooks/useResourceFilters';
import { useFocusTrap } from '../../../lib/hooks/useFocusTrap';

interface ResponsiveFilterSidebarProps {
  /** Current filter state */
  filters: ResourceFilters;
  /** Callback when filters change */
  onChange: (filters: ResourceFilters) => void;
  /** Optional facet counts */
  facets?: FilterFacets;
  /** Whether the mobile drawer is open */
  isOpen?: boolean;
  /** Callback when drawer open state changes */
  onOpenChange?: (open: boolean) => void;
}

/**
 * Responsive filter sidebar with mobile drawer support
 */
export const ResponsiveFilterSidebar: React.FC<ResponsiveFilterSidebarProps> = ({
  filters,
  onChange,
  facets,
  isOpen = false,
  onOpenChange,
}) => {
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(isOpen);
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile viewport
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Sync with external open state
  useEffect(() => {
    setIsMobileDrawerOpen(isOpen);
  }, [isOpen]);

  // Handle drawer state changes
  const handleOpenChange = (open: boolean) => {
    setIsMobileDrawerOpen(open);
    onOpenChange?.(open);
  };

  // Close drawer on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isMobileDrawerOpen) {
        handleOpenChange(false);
      }
    };

    if (isMobile && isMobileDrawerOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isMobile, isMobileDrawerOpen]);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (isMobile && isMobileDrawerOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [isMobile, isMobileDrawerOpen]);

  // Desktop: Fixed sidebar
  if (!isMobile) {
    return (
      <FilterSidebar
        filters={filters}
        onChange={onChange}
        facets={facets}
        className="h-full"
      />
    );
  }

  // Mobile: Drawer with backdrop
  return (
    <>
      <AnimatePresence>
        {isMobileDrawerOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => handleOpenChange(false)}
              aria-hidden="true"
            />

            {/* Drawer */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed left-0 top-0 bottom-0 z-50 w-80 max-w-[85vw]"
            >
              <MobileDrawerContent
                filters={filters}
                onChange={onChange}
                facets={facets}
                onClose={() => handleOpenChange(false)}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

/**
 * Mobile drawer content with close button
 */
interface MobileDrawerContentProps {
  filters: ResourceFilters;
  onChange: (filters: ResourceFilters) => void;
  facets?: FilterFacets;
  onClose: () => void;
}

const MobileDrawerContent: React.FC<MobileDrawerContentProps> = ({
  filters,
  onChange,
  facets,
  onClose,
}) => {
  const drawerRef = React.useRef<HTMLDivElement>(null);
  useFocusTrap(drawerRef, true);

  return (
    <div
      ref={drawerRef}
      className="h-full flex flex-col bg-white dark:bg-gray-800 shadow-xl"
      role="dialog"
      aria-modal="true"
      aria-label="Filter sidebar"
    >
      {/* Header with close button */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Filters
        </h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          aria-label="Close filters"
          className="!p-2"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </Button>
      </div>

      {/* Filter content */}
      <div className="flex-1 overflow-auto">
        <FilterSidebar
          filters={filters}
          onChange={onChange}
          facets={facets}
          className="border-0"
        />
      </div>

      {/* Footer with apply button */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <Button
          variant="primary"
          onClick={onClose}
          className="w-full"
        >
          Apply Filters
        </Button>
      </div>
    </div>
  );
};

/**
 * Filter button for mobile header
 */
interface FilterButtonProps {
  /** Number of active filters */
  activeCount?: number;
  /** Click handler */
  onClick: () => void;
  /** Additional CSS classes */
  className?: string;
}

export const FilterButton: React.FC<FilterButtonProps> = ({
  activeCount = 0,
  onClick,
  className = '',
}) => {
  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={onClick}
      className={`relative ${className}`}
      aria-label={`Open filters${activeCount > 0 ? ` (${activeCount} active)` : ''}`}
    >
      {/* Filter icon */}
      <svg
        className="w-5 h-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
        />
      </svg>

      {/* Active filter badge */}
      {activeCount > 0 && (
        <span className="absolute -top-1 -right-1 flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-blue-600 rounded-full">
          {activeCount}
        </span>
      )}
    </Button>
  );
};
