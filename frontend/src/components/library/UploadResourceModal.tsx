// Neo Alexandria 2.0 Frontend - Upload Resource Modal
// Modal for ingesting new resources from URLs with status polling

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Link as LinkIcon, 
  Upload, 
  CheckCircle, 
  XCircle, 
  Loader2,
  AlertCircle
} from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useCreateResource } from '@/hooks/useApi';
import { apiService } from '@/services/api';
import { useAppStore } from '@/store';
import { cn } from '@/utils/cn';
import type { ResourceStatus } from '@/types/api';

interface UploadResourceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const UploadResourceModal: React.FC<UploadResourceModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [urlError, setUrlError] = useState('');
  const [ingestionStatus, setIngestionStatus] = useState<ResourceStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  
  const createResource = useCreateResource();
  const addNotification = useAppStore(state => state.addNotification);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setUrl('');
      setTitle('');
      setUrlError('');
      setIngestionStatus(null);
      setIsPolling(false);
    }
  }, [isOpen]);

  // Validate URL
  const validateUrl = (urlString: string): boolean => {
    if (!urlString.trim()) {
      setUrlError('URL is required');
      return false;
    }
    
    try {
      new URL(urlString);
      setUrlError('');
      return true;
    } catch {
      setUrlError('Please enter a valid URL');
      return false;
    }
  };

  // Poll for ingestion status
  const pollStatus = async (resourceId: string) => {
    setIsPolling(true);
    let attempts = 0;
    const maxAttempts = 30;
    const interval = 2000; // 2 seconds

    const poll = async () => {
      try {
        const status = await apiService.getResourceStatus(resourceId);
        setIngestionStatus(status);

        if (status.ingestion_status === 'completed') {
          setIsPolling(false);
          addNotification({
            type: 'success',
            title: 'Resource Added',
            message: 'Resource has been successfully processed',
          });
          
          // Close modal after a short delay
          setTimeout(() => {
            onClose();
          }, 2000);
          return;
        }

        if (status.ingestion_status === 'failed') {
          setIsPolling(false);
          addNotification({
            type: 'error',
            title: 'Processing Failed',
            message: status.ingestion_error || 'Unknown error occurred',
          });
          return;
        }

        // Continue polling if still pending
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, interval);
        } else {
          setIsPolling(false);
          addNotification({
            type: 'warning',
            title: 'Processing Timeout',
            message: 'Resource is still processing. Check back later.',
          });
        }
      } catch (error) {
        setIsPolling(false);
        addNotification({
          type: 'error',
          title: 'Status Check Failed',
          message: 'Failed to check resource status',
        });
      }
    };

    poll();
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateUrl(url)) {
      return;
    }

    try {
      const response = await createResource.mutateAsync({
        url: url.trim(),
        title: title.trim() || undefined,
      });

      // Start polling for status
      setIngestionStatus({
        id: response.id,
        ingestion_status: 'pending',
      });
      
      pollStatus(response.id);
    } catch (error) {
      // Error handled by mutation
    }
  };

  // Handle URL input change
  const handleUrlChange = (value: string) => {
    setUrl(value);
    if (urlError) {
      setUrlError('');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Add Resource"
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        <div>
          <label className="block text-sm font-medium text-charcoal-grey-200 mb-2">
            Resource URL *
          </label>
          <Input
            type="url"
            value={url}
            onChange={(e) => handleUrlChange(e.target.value)}
            placeholder="https://example.com/article"
            leftIcon={<LinkIcon className="w-4 h-4" />}
            disabled={isPolling || ingestionStatus?.ingestion_status === 'completed'}
            className={cn(urlError && 'border-red-500')}
          />
          {urlError && (
            <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {urlError}
            </p>
          )}
        </div>

        {/* Title Input (Optional) */}
        <div>
          <label className="block text-sm font-medium text-charcoal-grey-200 mb-2">
            Title (Optional)
          </label>
          <Input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Leave empty to auto-extract from URL"
            disabled={isPolling || ingestionStatus?.ingestion_status === 'completed'}
          />
          <p className="text-xs text-charcoal-grey-400 mt-1">
            If not provided, the title will be extracted automatically
          </p>
        </div>

        {/* Ingestion Status Display */}
        <AnimatePresence>
          {ingestionStatus && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <IngestionStatusDisplay status={ingestionStatus} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-4 border-t border-charcoal-grey-700">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isPolling}
          >
            {ingestionStatus?.ingestion_status === 'completed' ? 'Close' : 'Cancel'}
          </Button>
          
          {!ingestionStatus && (
            <Button
              type="submit"
              variant="primary"
              loading={createResource.isPending}
              disabled={createResource.isPending}
              icon={<Upload className="w-4 h-4" />}
            >
              Add Resource
            </Button>
          )}
        </div>
      </form>
    </Modal>
  );
};

// Ingestion Status Display Component
interface IngestionStatusDisplayProps {
  status: ResourceStatus;
}

const IngestionStatusDisplay: React.FC<IngestionStatusDisplayProps> = ({ status }) => {
  const getStatusConfig = () => {
    switch (status.ingestion_status) {
      case 'pending':
        return {
          icon: <Loader2 className="w-6 h-6 animate-spin text-accent-blue-500" />,
          title: 'Processing...',
          message: 'Your resource is being ingested and processed',
          bgColor: 'bg-accent-blue-500/10',
          borderColor: 'border-accent-blue-500/30',
        };
      case 'completed':
        return {
          icon: <CheckCircle className="w-6 h-6 text-green-500" />,
          title: 'Success!',
          message: 'Resource has been successfully added to your library',
          bgColor: 'bg-green-500/10',
          borderColor: 'border-green-500/30',
        };
      case 'failed':
        return {
          icon: <XCircle className="w-6 h-6 text-red-500" />,
          title: 'Processing Failed',
          message: status.ingestion_error || 'An error occurred during processing',
          bgColor: 'bg-red-500/10',
          borderColor: 'border-red-500/30',
        };
      default:
        return {
          icon: <Loader2 className="w-6 h-6 animate-spin text-charcoal-grey-400" />,
          title: 'Processing...',
          message: 'Please wait',
          bgColor: 'bg-charcoal-grey-700/50',
          borderColor: 'border-charcoal-grey-600',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={cn(
      'rounded-lg border p-4',
      config.bgColor,
      config.borderColor
    )}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {config.icon}
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-charcoal-grey-50 mb-1">
            {config.title}
          </h4>
          <p className="text-sm text-charcoal-grey-300">
            {config.message}
          </p>
          
          {/* Progress Indicator for Pending Status */}
          {status.ingestion_status === 'pending' && (
            <div className="mt-3">
              <div className="w-full bg-charcoal-grey-700 rounded-full h-2 overflow-hidden">
                <motion.div
                  className="h-full bg-accent-blue-500"
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{
                    duration: 30,
                    ease: 'linear',
                  }}
                />
              </div>
              <p className="text-xs text-charcoal-grey-400 mt-2">
                This may take a few moments...
              </p>
            </div>
          )}
          
          {/* Timestamps */}
          {status.ingestion_started_at && (
            <p className="text-xs text-charcoal-grey-400 mt-2">
              Started: {new Date(status.ingestion_started_at).toLocaleString()}
            </p>
          )}
          {status.ingestion_completed_at && (
            <p className="text-xs text-charcoal-grey-400 mt-1">
              Completed: {new Date(status.ingestion_completed_at).toLocaleString()}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
