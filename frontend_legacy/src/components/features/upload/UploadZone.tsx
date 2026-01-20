/**
 * UploadZone Component
 * Drag-and-drop file upload area with validation
 */

import React, { useCallback, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { useToast } from '../../../contexts/ToastContext';
import { Button } from '../../ui/Button/Button';
import './UploadZone.css';

interface UploadZoneProps {
  onFilesAdded: (files: File[]) => void;
  accept?: string;
  maxSize?: number; // bytes
  maxFiles?: number;
  disabled?: boolean;
}

const DEFAULT_ACCEPT = '.pdf,.epub,.txt,.doc,.docx';
const DEFAULT_MAX_SIZE = 50 * 1024 * 1024; // 50MB
const DEFAULT_MAX_FILES = 10;

export const UploadZone: React.FC<UploadZoneProps> = ({
  onFilesAdded,
  accept = DEFAULT_ACCEPT,
  maxSize = DEFAULT_MAX_SIZE,
  maxFiles = DEFAULT_MAX_FILES,
  disabled = false,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { showToast } = useToast();

  /**
   * Validate file type and size
   */
  const validateFile = useCallback((file: File): { valid: boolean; error?: string } => {
    // Check file size
    if (file.size > maxSize) {
      return {
        valid: false,
        error: `${file.name} exceeds ${Math.round(maxSize / 1024 / 1024)}MB limit`,
      };
    }

    // Check file type if accept is specified
    if (accept) {
      const acceptedTypes = accept.split(',').map(t => t.trim());
      const fileExtension = `.${file.name.split('.').pop()?.toLowerCase()}`;
      const isAccepted = acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return fileExtension === type;
        }
        // Handle MIME types
        return file.type === type || file.type.startsWith(type.replace('/*', ''));
      });

      if (!isAccepted) {
        return {
          valid: false,
          error: `${file.name} is not a supported file type`,
        };
      }
    }

    return { valid: true };
  }, [accept, maxSize]);

  /**
   * Process and validate files
   */
  const processFiles = useCallback((files: FileList | File[]) => {
    const fileArray = Array.from(files);

    // Check max files limit
    if (fileArray.length > maxFiles) {
      showToast({
        variant: 'error',
        message: `Maximum ${maxFiles} files allowed at once`,
      });
      return;
    }

    // Validate each file
    const validFiles: File[] = [];
    const errors: string[] = [];

    fileArray.forEach(file => {
      const validation = validateFile(file);
      if (validation.valid) {
        validFiles.push(file);
      } else if (validation.error) {
        errors.push(validation.error);
      }
    });

    // Show errors
    if (errors.length > 0) {
      errors.forEach(error => {
        showToast({
          variant: 'error',
          message: error,
        });
      });
    }

    // Add valid files
    if (validFiles.length > 0) {
      onFilesAdded(validFiles);
    }
  }, [maxFiles, validateFile, onFilesAdded, showToast]);

  /**
   * Handle drag over
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  /**
   * Handle drag leave
   */
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  /**
   * Handle drop
   */
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFiles(files);
    }
  }, [disabled, processFiles]);

  /**
   * Handle file input change
   */
  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
    // Reset input value to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [processFiles]);

  /**
   * Trigger file input click
   */
  const handleBrowseClick = useCallback(() => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, [disabled]);

  /**
   * Handle keyboard activation
   */
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
      e.preventDefault();
      handleBrowseClick();
    }
  }, [disabled, handleBrowseClick]);

  const formatMaxSize = () => {
    const mb = maxSize / 1024 / 1024;
    return mb >= 1 ? `${Math.round(mb)}MB` : `${Math.round(maxSize / 1024)}KB`;
  };

  const getAcceptedFormats = () => {
    return accept
      .split(',')
      .map(t => t.trim().replace('.', '').toUpperCase())
      .join(', ');
  };

  return (
    <motion.div
      className={`upload-zone ${isDragging ? 'upload-zone--dragging' : ''} ${disabled ? 'upload-zone--disabled' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleBrowseClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="Upload files"
      aria-disabled={disabled}
      animate={{
        borderColor: isDragging ? 'var(--color-primary)' : 'var(--color-border)',
        backgroundColor: isDragging ? 'var(--color-primary-light)' : 'transparent',
      }}
      transition={{ duration: 0.2 }}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={accept}
        onChange={handleFileInputChange}
        className="upload-zone__input"
        aria-hidden="true"
        tabIndex={-1}
        disabled={disabled}
      />

      <div className="upload-zone__content">
        <div className="upload-zone__icon" aria-hidden="true">
          📁
        </div>
        
        <h3 className="upload-zone__title">
          {isDragging ? 'Drop files here' : 'Drop files here or click to browse'}
        </h3>
        
        <p className="upload-zone__description">
          Supports {getAcceptedFormats()} up to {formatMaxSize()}
        </p>
        
        {!isDragging && (
          <Button
            variant="primary"
            size="md"
            onClick={(e) => {
              e.stopPropagation();
              handleBrowseClick();
            }}
            disabled={disabled}
            className="upload-zone__button"
          >
            Browse Files
          </Button>
        )}
      </div>
    </motion.div>
  );
};

export default UploadZone;
