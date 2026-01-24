/**
 * ErrorBanner Component
 * 
 * Displays error messages with retry options for editor API failures.
 * Used across annotation, chunk, and quality features.
 * 
 * Accessibility features:
 * - ARIA labels for all buttons
 * - Screen reader announcements
 * - Keyboard navigation support
 * - Proper focus management
 */

import { AlertCircle, RefreshCw, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useEffect } from 'react';
import { announceError, announceWarning } from '@/lib/accessibility';

interface ErrorBannerProps {
  /**
   * Error message to display
   */
  message: string;
  
  /**
   * Optional title for the error
   */
  title?: string;
  
  /**
   * Whether to show a retry button
   */
  showRetry?: boolean;
  
  /**
   * Callback when retry button is clicked
   */
  onRetry?: () => void;
  
  /**
   * Whether to show a dismiss button
   */
  showDismiss?: boolean;
  
  /**
   * Callback when dismiss button is clicked
   */
  onDismiss?: () => void;
  
  /**
   * Whether the retry operation is in progress
   */
  isRetrying?: boolean;
  
  /**
   * Variant of the alert (error, warning, info)
   */
  variant?: 'error' | 'warning' | 'info';
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

export function ErrorBanner({
  message,
  title = 'Error',
  showRetry = true,
  onRetry,
  showDismiss = true,
  onDismiss,
  isRetrying = false,
  variant = 'error',
  className = '',
}: ErrorBannerProps) {
  const variantStyles = {
    error: 'border-red-500 bg-red-50 dark:bg-red-950/20',
    warning: 'border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20',
    info: 'border-blue-500 bg-blue-50 dark:bg-blue-950/20',
  };

  // Announce error to screen readers when component mounts
  useEffect(() => {
    if (variant === 'error') {
      announceError(`${title}: ${message}`);
    } else if (variant === 'warning') {
      announceWarning(`${title}: ${message}`);
    }
  }, [title, message, variant]);

  return (
    <Alert 
      className={`${variantStyles[variant]} ${className}`}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
    >
      <AlertCircle className="h-4 w-4" aria-hidden="true" />
      <AlertTitle className="flex items-center justify-between">
        <span>{title}</span>
        <div className="flex items-center gap-2">
          {showRetry && onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry}
              disabled={isRetrying}
              className="h-6 px-2"
              aria-label={`Retry ${title.toLowerCase()}`}
              aria-busy={isRetrying}
            >
              <RefreshCw 
                className={`h-3 w-3 mr-1 ${isRetrying ? 'animate-spin' : ''}`}
                aria-hidden="true"
              />
              {isRetrying ? 'Retrying...' : 'Retry'}
            </Button>
          )}
          {showDismiss && onDismiss && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
              className="h-6 w-6 p-0"
              aria-label={`Dismiss ${title.toLowerCase()}`}
            >
              <X className="h-3 w-3" aria-hidden="true" />
            </Button>
          )}
        </div>
      </AlertTitle>
      <AlertDescription className="text-sm">
        {message}
      </AlertDescription>
    </Alert>
  );
}

/**
 * Specialized error banner for annotation failures
 */
export function AnnotationErrorBanner({
  error,
  usingCachedData,
  onRetry,
  onDismiss,
  isRetrying,
}: {
  error: string;
  usingCachedData: boolean;
  onRetry: () => void;
  onDismiss: () => void;
  isRetrying: boolean;
}) {
  return (
    <ErrorBanner
      title={usingCachedData ? 'Using Cached Annotations' : 'Annotation Error'}
      message={error}
      variant={usingCachedData ? 'warning' : 'error'}
      showRetry={true}
      onRetry={onRetry}
      showDismiss={true}
      onDismiss={onDismiss}
      isRetrying={isRetrying}
      className="mb-4"
    />
  );
}

/**
 * Specialized error banner for chunk failures
 */
export function ChunkErrorBanner({
  error,
  usingFallback,
  onRetry,
  onDismiss,
  isRetrying,
}: {
  error: string;
  usingFallback: boolean;
  onRetry: () => void;
  onDismiss: () => void;
  isRetrying: boolean;
}) {
  return (
    <ErrorBanner
      title={usingFallback ? 'Using Line-Based Display' : 'Chunk Error'}
      message={error}
      variant={usingFallback ? 'warning' : 'error'}
      showRetry={true}
      onRetry={onRetry}
      showDismiss={true}
      onDismiss={onDismiss}
      isRetrying={isRetrying}
      className="mb-4"
    />
  );
}

/**
 * Specialized error banner for quality failures
 */
export function QualityErrorBanner({
  error,
  onRetry,
  onDismiss,
  isRetrying,
}: {
  error: string;
  onRetry: () => void;
  onDismiss: () => void;
  isRetrying: boolean;
}) {
  return (
    <ErrorBanner
      title="Quality Data Unavailable"
      message={`${error} Quality badges are hidden.`}
      variant="warning"
      showRetry={true}
      onRetry={onRetry}
      showDismiss={true}
      onDismiss={onDismiss}
      isRetrying={isRetrying}
      className="mb-4"
    />
  );
}
