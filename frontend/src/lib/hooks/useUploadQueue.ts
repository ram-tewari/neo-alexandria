/**
 * Upload Queue Management Hook
 * Handles file and URL uploads with progress tracking, concurrent upload management, and status polling
 */

import { useState, useCallback, useRef } from 'react';
import { resourcesApi } from '../api/resources';
import { ResourceAccepted, IngestionStatus } from '../api/types';
import { useToast } from '../../contexts/ToastContext';

export type UploadStatus = 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
export type ProcessingStage = 'downloading' | 'extracting' | 'analyzing';

export interface UploadItem {
  id: string;
  file?: File;
  url?: string;
  status: UploadStatus;
  progress: number;
  stage?: ProcessingStage;
  error?: string;
  resourceId?: string;
  createdAt: number;
}

interface UseUploadQueueOptions {
  maxConcurrent?: number;
  pollInterval?: number; // milliseconds
  pollTimeout?: number; // milliseconds
  onUploadComplete?: (item: UploadItem) => void;
  onUploadError?: (item: UploadItem, error: string) => void;
}

const DEFAULT_MAX_CONCURRENT = 3;
const DEFAULT_POLL_INTERVAL = 5000; // 5 seconds
const DEFAULT_POLL_TIMEOUT = 300000; // 5 minutes (60 attempts * 5s)

/**
 * Generate unique upload item ID
 */
const generateId = (): string => {
  return `upload-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Hook for managing upload queue
 */
export const useUploadQueue = (options: UseUploadQueueOptions = {}) => {
  const {
    maxConcurrent = DEFAULT_MAX_CONCURRENT,
    pollInterval = DEFAULT_POLL_INTERVAL,
    pollTimeout = DEFAULT_POLL_TIMEOUT,
    onUploadComplete,
    onUploadError,
  } = options;

  const [queue, setQueue] = useState<UploadItem[]>([]);
  const activeUploadsRef = useRef<Set<string>>(new Set());
  const abortControllersRef = useRef<Map<string, AbortController>>(new Map());
  const pollTimersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());
  const { showToast } = useToast();

  /**
   * Update an item in the queue
   */
  const updateItem = useCallback((id: string, updates: Partial<UploadItem>) => {
    setQueue(prev =>
      prev.map(item => (item.id === id ? { ...item, ...updates } : item))
    );
  }, []);

  /**
   * Remove an item from the queue
   */
  const removeItem = useCallback((id: string) => {
    setQueue(prev => prev.filter(item => item.id !== id));
    activeUploadsRef.current.delete(id);
    
    // Clean up abort controller
    const controller = abortControllersRef.current.get(id);
    if (controller) {
      controller.abort();
      abortControllersRef.current.delete(id);
    }

    // Clean up poll timer
    const timer = pollTimersRef.current.get(id);
    if (timer) {
      clearTimeout(timer);
      pollTimersRef.current.delete(id);
    }
  }, []);

  /**
   * Map ingestion status to processing stage
   */
  const getStageFromStatus = (status: IngestionStatus): ProcessingStage | undefined => {
    switch (status) {
      case 'pending':
        return 'downloading';
      case 'processing':
        return 'extracting';
      default:
        return undefined;
    }
  };

  /**
   * Poll resource status until completion or timeout
   */
  const pollStatus = useCallback(async (itemId: string, resourceId: string) => {
    const startTime = Date.now();
    let attempts = 0;
    const maxAttempts = Math.floor(pollTimeout / pollInterval);

    const poll = async () => {
      attempts++;
      const elapsed = Date.now() - startTime;

      // Check timeout
      if (elapsed >= pollTimeout || attempts >= maxAttempts) {
        updateItem(itemId, {
          status: 'failed',
          error: 'Processing timeout - please check resource status manually',
        });
        
        showToast({
          variant: 'error',
          message: 'Upload processing timed out',
        });
        
        pollTimersRef.current.delete(itemId);
        return;
      }

      try {
        const status = await resourcesApi.getStatus(resourceId);

        if (status.ingestion_status === 'completed') {
          // Success!
          updateItem(itemId, {
            status: 'completed',
            progress: 100,
            stage: undefined,
          });

          showToast({
            variant: 'success',
            message: 'Resource uploaded successfully',
          });

          pollTimersRef.current.delete(itemId);

          // Callback for completion
          const item = queue.find(i => i.id === itemId);
          if (item && onUploadComplete) {
            onUploadComplete({ ...item, status: 'completed' });
          }

        } else if (status.ingestion_status === 'failed') {
          // Failed
          const errorMessage = status.ingestion_error || 'Processing failed';
          
          updateItem(itemId, {
            status: 'failed',
            error: errorMessage,
          });

          showToast({
            variant: 'error',
            message: `Upload failed: ${errorMessage}`,
          });

          pollTimersRef.current.delete(itemId);

          // Callback for error
          const item = queue.find(i => i.id === itemId);
          if (item && onUploadError) {
            onUploadError(item, errorMessage);
          }

        } else {
          // Still processing - update stage and continue polling
          const stage = getStageFromStatus(status.ingestion_status);
          updateItem(itemId, { stage });

          // Schedule next poll
          const timer = setTimeout(poll, pollInterval);
          pollTimersRef.current.set(itemId, timer);
        }

      } catch (error: any) {
        // Network error or API error - retry
        console.error('Status poll error:', error);
        
        // Schedule retry
        const timer = setTimeout(poll, pollInterval);
        pollTimersRef.current.set(itemId, timer);
      }
    };

    // Start polling
    const timer = setTimeout(poll, pollInterval);
    pollTimersRef.current.set(itemId, timer);
  }, [pollInterval, pollTimeout, updateItem, showToast, queue, onUploadComplete, onUploadError]);

  /**
   * Start upload for an item
   */
  const startUpload = useCallback(async (item: UploadItem) => {
    // Check if already uploading
    if (activeUploadsRef.current.has(item.id)) {
      return;
    }

    // Add to active uploads
    activeUploadsRef.current.add(item.id);

    // Create abort controller for this upload
    const abortController = new AbortController();
    abortControllersRef.current.set(item.id, abortController);

    try {
      // Update status to uploading
      updateItem(item.id, { status: 'uploading', progress: 0, error: undefined });

      // Prepare request data
      const requestData: any = {};
      if (item.file) {
        requestData.file = item.file;
      } else if (item.url) {
        requestData.url = item.url;
      }

      // Upload with progress tracking
      const response: ResourceAccepted = await resourcesApi.create(requestData, {
        onUploadProgress: (progressEvent: ProgressEvent) => {
          if (progressEvent.lengthComputable) {
            const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
            updateItem(item.id, { progress });
          }
        },
      });

      // Upload complete, now processing
      updateItem(item.id, {
        status: 'processing',
        progress: 100,
        resourceId: response.id,
        stage: 'downloading',
      });

      // Start polling for status
      pollStatus(item.id, response.id);

    } catch (error: any) {
      const errorMessage = error.message || 'Upload failed';
      
      updateItem(item.id, {
        status: 'failed',
        error: errorMessage,
      });

      // Callback for upload error
      if (onUploadError) {
        onUploadError(item, errorMessage);
      }
    } finally {
      // Remove from active uploads
      activeUploadsRef.current.delete(item.id);
      abortControllersRef.current.delete(item.id);
      
      // Process next item in queue
      processQueue();
    }
  }, [updateItem, pollStatus]);

  /**
   * Process queue - start uploads up to max concurrent limit
   */
  const processQueue = useCallback(() => {
    setQueue(currentQueue => {
      const pendingItems = currentQueue.filter(item => item.status === 'pending');
      const availableSlots = maxConcurrent - activeUploadsRef.current.size;

      if (availableSlots > 0 && pendingItems.length > 0) {
        const itemsToStart = pendingItems.slice(0, availableSlots);
        itemsToStart.forEach(item => {
          // Start upload asynchronously
          startUpload(item);
        });
      }

      return currentQueue;
    });
  }, [maxConcurrent, startUpload]);

  /**
   * Add files to the upload queue
   */
  const addFiles = useCallback((files: File[]) => {
    const newItems: UploadItem[] = files.map(file => ({
      id: generateId(),
      file,
      status: 'pending',
      progress: 0,
      createdAt: Date.now(),
    }));

    setQueue(prev => [...prev, ...newItems]);

    // Trigger queue processing
    setTimeout(processQueue, 0);
  }, [processQueue]);

  /**
   * Add URL to the upload queue
   */
  const addURL = useCallback((url: string) => {
    const item: UploadItem = {
      id: generateId(),
      url,
      status: 'pending',
      progress: 0,
      createdAt: Date.now(),
    };

    setQueue(prev => [...prev, item]);

    // Trigger queue processing
    setTimeout(processQueue, 0);
  }, [processQueue]);

  /**
   * Retry a failed upload
   */
  const retryUpload = useCallback((id: string) => {
    const item = queue.find(i => i.id === id);
    if (item && item.status === 'failed') {
      updateItem(id, {
        status: 'pending',
        progress: 0,
        error: undefined,
        resourceId: undefined,
      });
      
      // Trigger queue processing
      setTimeout(processQueue, 0);
    }
  }, [queue, updateItem, processQueue]);

  /**
   * Cancel an upload
   */
  const cancelUpload = useCallback((id: string) => {
    const controller = abortControllersRef.current.get(id);
    if (controller) {
      controller.abort();
    }
    removeItem(id);
  }, [removeItem]);

  /**
   * Clear completed uploads
   */
  const clearCompleted = useCallback(() => {
    setQueue(prev => prev.filter(item => item.status !== 'completed'));
  }, []);

  /**
   * Clear all uploads
   */
  const clearAll = useCallback(() => {
    // Abort all active uploads
    abortControllersRef.current.forEach(controller => controller.abort());
    abortControllersRef.current.clear();
    
    // Clear all poll timers
    pollTimersRef.current.forEach(timer => clearTimeout(timer));
    pollTimersRef.current.clear();
    
    activeUploadsRef.current.clear();
    setQueue([]);
  }, []);

  return {
    queue,
    addFiles,
    addURL,
    retryUpload,
    cancelUpload,
    clearCompleted,
    clearAll,
    activeCount: activeUploadsRef.current.size,
  };
};

export default useUploadQueue;
