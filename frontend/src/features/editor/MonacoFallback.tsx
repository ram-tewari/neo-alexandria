/**
 * Monaco Fallback Component
 * 
 * Fallback text viewer displayed when Monaco Editor fails to load.
 * Provides basic code viewing with error message and retry functionality.
 * 
 * Requirements: 10.1 - Error Handling and Fallbacks
 */

import { useState } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import type { CodeFile } from './types';

// ============================================================================
// Types
// ============================================================================

export interface MonacoFallbackProps {
  file: CodeFile;
  error?: Error | string;
  onRetry?: () => void;
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function MonacoFallback({
  file,
  error,
  onRetry,
  className = '',
}: MonacoFallbackProps) {
  const [isRetrying, setIsRetrying] = useState(false);

  // ==========================================================================
  // Handlers
  // ==========================================================================

  const handleRetry = async () => {
    if (!onRetry) return;
    
    setIsRetrying(true);
    try {
      await onRetry();
    } catch (error) {
      // Silently handle retry errors - the parent component
      // will handle error state management
      console.error('Retry failed:', error);
    } finally {
      // Reset after a short delay to allow for UI feedback
      setTimeout(() => setIsRetrying(false), 500);
    }
  };

  // ==========================================================================
  // Error Message
  // ==========================================================================

  const errorMessage = error instanceof Error ? error.message : error || 'Failed to load Monaco Editor';

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div 
      className={`monaco-fallback flex flex-col h-full ${className}`}
      data-testid="monaco-fallback"
    >
      {/* Error Alert */}
      <Alert variant="destructive" className="m-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Editor Failed to Load</AlertTitle>
        <AlertDescription className="flex items-center justify-between">
          <span>{errorMessage}</span>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetry}
              disabled={isRetrying}
              className="ml-4"
            >
              {isRetrying ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Retrying...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Retry
                </>
              )}
            </Button>
          )}
        </AlertDescription>
      </Alert>

      {/* Fallback Text Viewer */}
      <div className="flex-1 overflow-auto px-4 pb-4">
        <div className="border rounded-md bg-muted/50">
          <div className="border-b bg-muted px-4 py-2 text-sm font-medium">
            {file.name}
            <span className="ml-2 text-muted-foreground">
              ({file.language} • {file.lines} lines)
            </span>
          </div>
          <pre className="p-4 overflow-auto text-sm font-mono">
            <code className="block whitespace-pre">{file.content}</code>
          </pre>
        </div>
      </div>

      {/* Info Message */}
      <div className="px-4 pb-4 text-sm text-muted-foreground">
        <p>
          Displaying file in fallback mode. Some features like syntax highlighting,
          annotations, and quality badges are unavailable.
        </p>
      </div>
    </div>
  );
}
