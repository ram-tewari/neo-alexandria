/**
 * BatchToolbar component
 * Floating toolbar for batch operations on selected resources
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../../ui/Button';
import { useToast } from '../../../contexts/ToastContext';
import { resourcesApi } from '../../../lib/api/resources';
import type { ResourceUpdate } from '../../../lib/api/types';
import { announceBatchSelection } from '../../../lib/utils/announceToScreenReader';

export interface BatchToolbarProps {
  /** Number of selected resources */
  selectedCount: number;
  /** Array of selected resource IDs */
  selectedIds: string[];
  /** Callback to clear selection */
  onClear: () => void;
  /** Optional callback after successful batch operation */
  onSuccess?: () => void;
}

/**
 * Floating toolbar with batch action buttons
 * Appears at bottom of screen when resources are selected
 * 
 * @example
 * ```tsx
 * <BatchToolbar
 *   selectedCount={5}
 *   selectedIds={['id1', 'id2', 'id3', 'id4', 'id5']}
 *   onClear={() => clearSelection()}
 * />
 * ```
 */
export const BatchToolbar: React.FC<BatchToolbarProps> = ({
  selectedCount,
  selectedIds,
  onClear,
  onSuccess,
}) => {
  const { showToast } = useToast();
  const [isUpdating, setIsUpdating] = useState(false);

  // Announce selection changes to screen readers
  useEffect(() => {
    if (selectedCount > 0) {
      announceBatchSelection(selectedCount);
    }
  }, [selectedCount]);

  /**
   * Handle batch update operation
   */
  const handleBatchUpdate = async (updates: ResourceUpdate, actionName: string) => {
    setIsUpdating(true);
    try {
      await resourcesApi.batchUpdate(selectedIds, updates);
      showToast({
        variant: 'success',
        message: `${actionName} applied to ${selectedCount} resource${selectedCount > 1 ? 's' : ''}`,
      });
      onClear();
      onSuccess?.();
    } catch (error) {
      showToast({
        variant: 'error',
        message: `Failed to ${actionName.toLowerCase()}: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    } finally {
      setIsUpdating(false);
    }
  };

  /**
   * Handle "Add to Collection" action
   * Note: This is a placeholder - actual collection selection UI would be needed
   */
  const handleAddToCollection = () => {
    showToast({
      variant: 'info',
      message: 'Collection selection UI coming soon',
    });
  };

  /**
   * Handle "Change Status" action
   * Note: This is a placeholder - actual status selection UI would be needed
   */
  const handleChangeStatus = () => {
    showToast({
      variant: 'info',
      message: 'Status selection UI coming soon',
    });
  };

  /**
   * Handle "Update Tags" action
   * Note: This is a placeholder - actual tag editor UI would be needed
   */
  const handleUpdateTags = () => {
    showToast({
      variant: 'info',
      message: 'Tag editor UI coming soon',
    });
  };

  return (
    <AnimatePresence>
      {selectedCount > 0 && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
          role="toolbar"
          aria-label="Batch actions toolbar"
        >
          <div className="bg-white dark:bg-gray-800 shadow-2xl rounded-lg border border-gray-200 dark:border-gray-700 p-4 flex items-center gap-4">
            {/* Screen reader announcement region */}
            <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
              {selectedCount} {selectedCount === 1 ? 'item' : 'items'} selected
            </div>
            {/* Selection count */}
            <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-md">
              <svg
                className="w-5 h-5 text-blue-600 dark:text-blue-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
              <span className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                {selectedCount} selected
              </span>
            </div>

            {/* Divider */}
            <div className="h-8 w-px bg-gray-200 dark:bg-gray-700" />

            {/* Action buttons */}
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={handleAddToCollection}
                disabled={isUpdating}
              >
                Add to Collection
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={handleChangeStatus}
                disabled={isUpdating}
              >
                Change Status
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={handleUpdateTags}
                disabled={isUpdating}
              >
                Update Tags
              </Button>
            </div>

            {/* Divider */}
            <div className="h-8 w-px bg-gray-200 dark:bg-gray-700" />

            {/* Clear button */}
            <Button
              size="sm"
              variant="ghost"
              onClick={onClear}
              disabled={isUpdating}
              aria-label="Clear selection"
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
        </motion.div>
      )}
    </AnimatePresence>
  );
};
