/**
 * DocumentUpload Component
 * 
 * File upload interface with:
 * - Drag-and-drop support
 * - File type validation
 * - File size validation (max 50MB)
 * - Multi-file upload
 * - Upload progress indicators
 * - Success/error notifications
 */

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

export interface UploadFile {
  file: File;
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export interface DocumentUploadProps {
  onUpload: (files: File[]) => Promise<void>;
  maxSize?: number; // in bytes
  acceptedTypes?: string[];
  multiple?: boolean;
  className?: string;
}

const DEFAULT_MAX_SIZE = 50 * 1024 * 1024; // 50MB
const DEFAULT_ACCEPTED_TYPES = [
  'application/pdf',
  'text/html',
  'text/plain',
  'text/markdown',
];

export function DocumentUpload({
  onUpload,
  maxSize = DEFAULT_MAX_SIZE,
  acceptedTypes = DEFAULT_ACCEPTED_TYPES,
  multiple = true,
  className,
}: DocumentUploadProps) {
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[], rejectedFiles: any[]) => {
      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const newRejected = rejectedFiles.map((rejected) => ({
          file: rejected.file,
          id: `${rejected.file.name}-${Date.now()}`,
          progress: 0,
          status: 'error' as const,
          error: rejected.errors[0]?.message || 'File rejected',
        }));
        setUploadFiles((prev) => [...prev, ...newRejected]);
        return;
      }

      // Add accepted files to upload queue
      const newFiles = acceptedFiles.map((file) => ({
        file,
        id: `${file.name}-${Date.now()}`,
        progress: 0,
        status: 'pending' as const,
      }));

      setUploadFiles((prev) => [...prev, ...newFiles]);

      // Start upload
      try {
        await onUpload(acceptedFiles);
        
        // Mark as success
        setUploadFiles((prev) =>
          prev.map((f) =>
            newFiles.find((nf) => nf.id === f.id)
              ? { ...f, status: 'success', progress: 100 }
              : f
          )
        );
      } catch (error) {
        // Mark as error
        setUploadFiles((prev) =>
          prev.map((f) =>
            newFiles.find((nf) => nf.id === f.id)
              ? {
                  ...f,
                  status: 'error',
                  error: error instanceof Error ? error.message : 'Upload failed',
                }
              : f
          )
        );
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxSize,
    multiple,
  });

  const removeFile = (id: string) => {
    setUploadFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const clearCompleted = () => {
    setUploadFiles((prev) => prev.filter((f) => f.status === 'uploading' || f.status === 'pending'));
  };

  const hasCompleted = uploadFiles.some((f) => f.status === 'success' || f.status === 'error');

  return (
    <div className={cn('space-y-4', className)}>
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50'
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
        {isDragActive ? (
          <p className="text-sm font-medium">Drop files here...</p>
        ) : (
          <>
            <p className="text-sm font-medium mb-1">
              Drag & drop files here, or click to select
            </p>
            <p className="text-xs text-muted-foreground">
              PDF, HTML, TXT, MD • Max {Math.round(maxSize / 1024 / 1024)}MB per file
            </p>
          </>
        )}
      </div>

      {/* Upload queue */}
      {uploadFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">
              {uploadFiles.length} {uploadFiles.length === 1 ? 'file' : 'files'}
            </h4>
            {hasCompleted && (
              <Button variant="ghost" size="sm" onClick={clearCompleted}>
                Clear completed
              </Button>
            )}
          </div>

          <div className="space-y-2">
            {uploadFiles.map((uploadFile) => (
              <UploadFileItem
                key={uploadFile.id}
                uploadFile={uploadFile}
                onRemove={() => removeFile(uploadFile.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface UploadFileItemProps {
  uploadFile: UploadFile;
  onRemove: () => void;
}

function UploadFileItem({ uploadFile, onRemove }: UploadFileItemProps) {
  const { file, progress, status, error } = uploadFile;

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      default:
        return <FileText className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-destructive';
      default:
        return 'text-muted-foreground';
    }
  };

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border bg-card">
      {getStatusIcon()}
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <p className="text-sm font-medium truncate">{file.name}</p>
          <span className="text-xs text-muted-foreground whitespace-nowrap">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </span>
        </div>

        {status === 'uploading' && (
          <Progress value={progress} className="h-1" />
        )}

        {status === 'error' && error && (
          <p className="text-xs text-destructive">{error}</p>
        )}

        {status === 'success' && (
          <p className="text-xs text-green-600">Upload complete</p>
        )}
      </div>

      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 shrink-0"
        onClick={onRemove}
        aria-label={`Remove ${file.name}`}
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}
