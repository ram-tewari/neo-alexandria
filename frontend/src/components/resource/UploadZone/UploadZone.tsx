import React, { useState, useRef, DragEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Link, FileText, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { useUploadFile, useUploadUrl, useUploadStatus } from '@/hooks/useResources';
import { UploadProgress } from '@/types/resource';

interface UploadZoneProps {
  onFilesSelected?: (files: File[]) => void;
  onUrlSubmit?: (url: string) => void;
  accept?: string;
  maxFiles?: number;
  maxSize?: number; // in MB
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onFilesSelected,
  onUrlSubmit,
  accept = '.pdf',
  maxFiles = 10,
  maxSize = 50,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [url, setUrl] = useState('');
  const [uploadQueue, setUploadQueue] = useState<UploadProgress[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadFileMutation = useUploadFile();
  const uploadUrlMutation = useUploadUrl();

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const handleFiles = (files: File[]) => {
    // Validate files
    const validFiles = files.filter((file) => {
      if (maxSize && file.size > maxSize * 1024 * 1024) {
        return false;
      }
      return true;
    });

    if (validFiles.length > maxFiles) {
      validFiles.splice(maxFiles);
    }

    // Create upload queue items
    const queueItems: UploadProgress[] = validFiles.map((file) => ({
      id: Math.random().toString(36).substring(7),
      filename: file.name,
      progress: 0,
      stage: 'uploading',
    }));

    setUploadQueue((prev) => [...prev, ...queueItems]);

    // Upload files
    validFiles.forEach((file, index) => {
      uploadFileMutation.mutate(file, {
        onSuccess: (data) => {
          updateQueueItem(queueItems[index].id, {
            stage: 'complete',
            progress: 100,
          });
        },
        onError: () => {
          updateQueueItem(queueItems[index].id, {
            stage: 'error',
            error: 'Upload failed',
          });
        },
      });
    });

    onFilesSelected?.(validFiles);
  };

  const handleUrlSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic URL validation
    try {
      new URL(url);
    } catch {
      return;
    }

    const queueItem: UploadProgress = {
      id: Math.random().toString(36).substring(7),
      filename: url,
      progress: 0,
      stage: 'uploading',
    };

    setUploadQueue((prev) => [...prev, queueItem]);

    uploadUrlMutation.mutate(url, {
      onSuccess: () => {
        updateQueueItem(queueItem.id, {
          stage: 'complete',
          progress: 100,
        });
        setUrl('');
        setShowUrlInput(false);
      },
      onError: () => {
        updateQueueItem(queueItem.id, {
          stage: 'error',
          error: 'Failed to process URL',
        });
      },
    });

    onUrlSubmit?.(url);
  };

  const updateQueueItem = (
    id: string,
    updates: Partial<UploadProgress>
  ) => {
    setUploadQueue((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...updates } : item))
    );
  };

  const removeQueueItem = (id: string) => {
    setUploadQueue((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${
            isDragging
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 scale-105'
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
          }
        `}
        animate={isDragging ? { scale: 1.02 } : { scale: 1 }}
        role="button"
        aria-label="Upload files"
        tabIndex={0}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple
          onChange={handleFileSelect}
          className="hidden"
          aria-hidden="true"
        />

        <Upload
          className={`w-12 h-12 mx-auto mb-4 ${
            isDragging ? 'text-primary-600' : 'text-gray-400'
          }`}
          aria-hidden="true"
        />

        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Drop files here or click to browse
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Supports PDF files up to {maxSize}MB
        </p>

        <div className="mt-4">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setShowUrlInput(true);
            }}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-700 dark:text-primary-300 hover:text-primary-800 dark:hover:text-primary-200"
          >
            <Link className="w-4 h-4" />
            Or add from URL
          </button>
        </div>
      </motion.div>

      {/* URL Input */}
      <AnimatePresence>
        {showUrlInput && (
          <motion.form
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            onSubmit={handleUrlSubmit}
            className="flex gap-2"
          >
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/paper.pdf"
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              aria-label="Enter URL"
            />
            <button
              type="submit"
              disabled={!url}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 text-white rounded-md transition-colors"
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => {
                setShowUrlInput(false);
                setUrl('');
              }}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-md transition-colors"
            >
              Cancel
            </button>
          </motion.form>
        )}
      </AnimatePresence>

      {/* Upload Queue */}
      <AnimatePresence>
        {uploadQueue.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-2"
          >
            {uploadQueue.map((item) => (
              <UploadQueueItem
                key={item.id}
                item={item}
                onRemove={() => removeQueueItem(item.id)}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

interface UploadQueueItemProps {
  item: UploadProgress;
  onRemove: () => void;
}

const UploadQueueItem: React.FC<UploadQueueItemProps> = ({ item, onRemove }) => {
  const getIcon = () => {
    switch (item.stage) {
      case 'complete':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />;
    }
  };

  const getStageLabel = () => {
    switch (item.stage) {
      case 'uploading':
        return 'Uploading...';
      case 'extracting':
        return 'Extracting text...';
      case 'analyzing':
        return 'Analyzing...';
      case 'complete':
        return 'Complete';
      case 'error':
        return item.error || 'Error';
      default:
        return '';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      <FileText className="w-5 h-5 text-gray-400 flex-shrink-0" />
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
          {item.filename}
        </p>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          {getStageLabel()}
        </p>
        
        {item.stage !== 'complete' && item.stage !== 'error' && (
          <div className="mt-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${item.progress}%` }}
              className="bg-primary-600 h-1 rounded-full"
            />
          </div>
        )}
      </div>

      <div className="flex-shrink-0">{getIcon()}</div>

      {(item.stage === 'complete' || item.stage === 'error') && (
        <button
          onClick={onRemove}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          aria-label="Remove"
        >
          <XCircle className="w-5 h-5" />
        </button>
      )}
    </motion.div>
  );
};
