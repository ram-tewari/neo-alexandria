/**
 * UploadQueue Component
 * Displays the queue of uploads with progress summary
 */

import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadItem as UploadItemType } from '../../../lib/hooks/useUploadQueue';
import UploadItem from './UploadItem';
import { Button } from '../../ui/Button/Button';
import './UploadQueue.css';

interface UploadQueueProps {
  queue: UploadItemType[];
  onRetry?: (id: string) => void;
  onCancel?: (id: string) => void;
  onClearCompleted?: () => void;
  className?: string;
}

export const UploadQueue: React.FC<UploadQueueProps> = ({
  queue,
  onRetry,
  onCancel,
  onClearCompleted,
  className = '',
}) => {
  // Calculate statistics
  const stats = useMemo(() => {
    const total = queue.length;
    const completed = queue.filter(item => item.status === 'completed').length;
    const failed = queue.filter(item => item.status === 'failed').length;
    const inProgress = queue.filter(
      item => item.status === 'uploading' || item.status === 'processing'
    ).length;
    const pending = queue.filter(item => item.status === 'pending').length;
    
    const completionPercentage = total > 0 ? Math.round((completed / total) * 100) : 0;

    return {
      total,
      completed,
      failed,
      inProgress,
      pending,
      completionPercentage,
    };
  }, [queue]);

  if (queue.length === 0) {
    return null;
  }

  return (
    <div className={`upload-queue ${className}`}>
      {/* Header with Summary */}
      <div className="upload-queue__header">
        <div className="upload-queue__title-section">
          <h3 className="upload-queue__title">
            Upload Queue
          </h3>
          <div className="upload-queue__stats">
            <span className="upload-queue__stat">
              {stats.completed}/{stats.total} complete
            </span>
            {stats.inProgress > 0 && (
              <span className="upload-queue__stat upload-queue__stat--active">
                {stats.inProgress} in progress
              </span>
            )}
            {stats.failed > 0 && (
              <span className="upload-queue__stat upload-queue__stat--error">
                {stats.failed} failed
              </span>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="upload-queue__progress">
          <div className="upload-queue__progress-bar">
            <motion.div
              className="upload-queue__progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${stats.completionPercentage}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          <span className="upload-queue__progress-text">
            {stats.completionPercentage}%
          </span>
        </div>

        {/* Actions */}
        {stats.completed > 0 && onClearCompleted && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearCompleted}
            className="upload-queue__clear-button"
          >
            Clear Completed
          </Button>
        )}
      </div>

      {/* Queue Items */}
      <div className="upload-queue__items">
        <AnimatePresence mode="popLayout">
          {queue.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              layout
            >
              <UploadItem
                item={item}
                onRetry={onRetry}
                onCancel={onCancel}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Empty State for All Completed */}
      {stats.total > 0 && stats.completed === stats.total && (
        <motion.div
          className="upload-queue__success"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="upload-queue__success-icon">🎉</div>
          <p className="upload-queue__success-text">
            All uploads completed successfully!
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default UploadQueue;
