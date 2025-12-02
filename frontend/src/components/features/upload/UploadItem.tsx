/**
 * UploadItem Component
 * Displays individual upload progress with status icons and actions
 */

import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { UploadItem as UploadItemType } from '../../../lib/hooks/useUploadQueue';
import { Button } from '../../ui/Button/Button';
import { Card } from '../../ui/Card/Card';
import { announceUploadProgress } from '../../../lib/utils/announceToScreenReader';
import './UploadItem.css';

interface UploadItemProps {
  item: UploadItemType;
  onRetry?: (id: string) => void;
  onCancel?: (id: string) => void;
}

/**
 * Format bytes to human-readable size
 */
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Get status icon and color
 */
const getStatusDisplay = (status: UploadItemType['status']) => {
  switch (status) {
    case 'pending':
      return { icon: '⏳', label: 'Pending', color: 'var(--color-text-secondary)' };
    case 'uploading':
      return { icon: '⬆️', label: 'Uploading', color: 'var(--color-primary)' };
    case 'processing':
      return { icon: '⚙️', label: 'Processing', color: 'var(--color-primary)' };
    case 'completed':
      return { icon: '✅', label: 'Completed', color: 'var(--color-success)' };
    case 'failed':
      return { icon: '❌', label: 'Failed', color: 'var(--color-error)' };
    default:
      return { icon: '❓', label: 'Unknown', color: 'var(--color-text-secondary)' };
  }
};

/**
 * Get stage label
 */
const getStageLabel = (stage?: UploadItemType['stage']): string => {
  switch (stage) {
    case 'downloading':
      return 'Downloading content';
    case 'extracting':
      return 'Extracting metadata';
    case 'analyzing':
      return 'Analyzing content';
    default:
      return '';
  }
};

export const UploadItem: React.FC<UploadItemProps> = ({ item, onRetry, onCancel }) => {
  const statusDisplay = getStatusDisplay(item.status);
  const isURL = !!item.url;
  const fileName = item.file?.name || item.url || 'Unknown';
  const fileSize = item.file?.size;
  const showProgress = item.status === 'uploading' || item.status === 'processing';
  const stageLabel = getStageLabel(item.stage);
  const previousProgressRef = useRef(item.progress);

  // Announce progress changes to screen readers (throttled)
  useEffect(() => {
    const progressDiff = Math.abs(item.progress - previousProgressRef.current);
    
    // Only announce every 25% progress or on completion
    if (showProgress && (progressDiff >= 25 || item.progress === 100)) {
      announceUploadProgress(fileName, item.progress, stageLabel);
      previousProgressRef.current = item.progress;
    }
  }, [item.progress, fileName, stageLabel, showProgress]);

  return (
    <Card className="upload-item">
      <div className="upload-item__content">
        {/* Screen reader status announcement */}
        <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
          {fileName}: {statusDisplay.label}
          {showProgress && ` ${item.progress}% complete`}
          {stageLabel && ` - ${stageLabel}`}
        </div>

        {/* Status Icon */}
        <div 
          className="upload-item__icon"
          style={{ color: statusDisplay.color }}
          aria-hidden="true"
        >
          {statusDisplay.icon}
        </div>

        {/* File Info */}
        <div className="upload-item__info">
          <div className="upload-item__header">
            <div className="upload-item__filename-wrapper">
              {isURL && (
                <span className="upload-item__type-badge" title="URL Resource">
                  🔗
                </span>
              )}
              <span className="upload-item__filename" title={fileName}>
                {fileName}
              </span>
            </div>
            {fileSize && (
              <span className="upload-item__filesize">
                {formatBytes(fileSize)}
              </span>
            )}
          </div>

          {/* Progress Bar */}
          {showProgress && (
            <div className="upload-item__progress-container">
              <div className="upload-item__progress-bar">
                <motion.div
                  className="upload-item__progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${item.progress}%` }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                />
              </div>
              <span className="upload-item__progress-text">
                {item.progress}%
              </span>
            </div>
          )}

          {/* Stage Label */}
          {stageLabel && (
            <div className="upload-item__stage">
              {stageLabel}
            </div>
          )}

          {/* Error Message */}
          {item.status === 'failed' && item.error && (
            <div className="upload-item__error" role="alert">
              <strong>Error:</strong> {item.error}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="upload-item__actions">
          {item.status === 'failed' && onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onRetry(item.id)}
              aria-label="Retry upload"
            >
              Retry
            </Button>
          )}
          {item.status !== 'completed' && onCancel && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onCancel(item.id)}
              aria-label="Cancel upload"
            >
              Cancel
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default UploadItem;
