/**
 * EmptyState component for when no resources match filters
 * 
 * Displays a friendly message with an illustration when:
 * - No resources match the current filters
 * - The library is empty
 * 
 * Provides a "Clear Filters" action to help users recover
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '../../ui/Button/Button';
import type { ResourceFilters } from '../../../lib/hooks/useResourceFilters';

interface EmptyStateProps {
  /** Current filter state */
  filters: ResourceFilters;
  /** Callback to clear all filters */
  onClearFilters: () => void;
  /** Optional custom message */
  message?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Empty state component with illustration and clear filters action
 */
export const EmptyState: React.FC<EmptyStateProps> = ({
  filters,
  onClearFilters,
  message,
  className = '',
}) => {
  const hasActiveFilters = Object.keys(filters).length > 0;

  const defaultMessage = hasActiveFilters
    ? 'No resources match your current filters'
    : 'No resources in your library yet';

  const actionMessage = hasActiveFilters
    ? 'Try adjusting your filters or clear them to see all resources.'
    : 'Start by uploading your first resource or adding content from a URL.';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex flex-col items-center justify-center py-16 px-4 text-center ${className}`}
      role="status"
      aria-live="polite"
    >
      {/* Illustration */}
      <div className="mb-6">
        <svg
          className="w-32 h-32 text-gray-300 dark:text-gray-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          {hasActiveFilters ? (
            // Filter icon for filtered empty state
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            />
          ) : (
            // Empty folder icon for no resources
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
            />
          )}
        </svg>
      </div>

      {/* Message */}
      <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
        {message || defaultMessage}
      </h3>

      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6 max-w-md">
        {actionMessage}
      </p>

      {/* Actions */}
      <div className="flex gap-3">
        {hasActiveFilters && (
          <Button
            variant="primary"
            onClick={onClearFilters}
            aria-label="Clear all filters"
          >
            Clear Filters
          </Button>
        )}
        {!hasActiveFilters && (
          <>
            <Button
              variant="primary"
              onClick={() => window.location.href = '/upload'}
            >
              Upload Resource
            </Button>
            <Button
              variant="secondary"
              onClick={() => window.location.href = '/library'}
            >
              Browse Library
            </Button>
          </>
        )}
      </div>

      {/* Additional help text */}
      {hasActiveFilters && (
        <p className="text-xs text-gray-500 dark:text-gray-500 mt-6">
          Active filters: {Object.keys(filters).length}
        </p>
      )}
    </motion.div>
  );
};

/**
 * Compact empty state for smaller spaces
 */
export const CompactEmptyState: React.FC<{
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}> = ({ message, action }) => {
  return (
    <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        {message}
      </p>
      {action && (
        <Button
          variant="secondary"
          size="sm"
          onClick={action.onClick}
        >
          {action.label}
        </Button>
      )}
    </div>
  );
};
