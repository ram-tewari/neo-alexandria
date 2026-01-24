/**
 * API Loading Indicators
 * 
 * Provides loading indicators for API operations in the editor:
 * - Annotations loading
 * - Chunks loading
 * - Quality data loading
 * 
 * These indicators appear as subtle overlays or inline messages
 * to inform users that data is being fetched.
 * 
 * Requirements: 5.5 - Loading states for API operations
 */

import { Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

// ============================================================================
// Annotations Loading Indicator
// ============================================================================

export function AnnotationsLoadingIndicator() {
  return (
    <Alert className="border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-900">
      <Loader2 className="h-4 w-4 animate-spin text-blue-600 dark:text-blue-400" aria-hidden="true" />
      <AlertDescription className="text-sm text-blue-800 dark:text-blue-300">
        Loading annotations...
      </AlertDescription>
    </Alert>
  );
}

// ============================================================================
// Chunks Loading Indicator
// ============================================================================

export function ChunksLoadingIndicator() {
  return (
    <Alert className="border-purple-200 bg-purple-50 dark:bg-purple-950/20 dark:border-purple-900">
      <Loader2 className="h-4 w-4 animate-spin text-purple-600 dark:text-purple-400" aria-hidden="true" />
      <AlertDescription className="text-sm text-purple-800 dark:text-purple-300">
        Loading semantic chunks...
      </AlertDescription>
    </Alert>
  );
}

// ============================================================================
// Quality Data Loading Indicator
// ============================================================================

export function QualityLoadingIndicator() {
  return (
    <Alert className="border-green-200 bg-green-50 dark:bg-green-950/20 dark:border-green-900">
      <Loader2 className="h-4 w-4 animate-spin text-green-600 dark:text-green-400" aria-hidden="true" />
      <AlertDescription className="text-sm text-green-800 dark:text-green-300">
        Loading quality data...
      </AlertDescription>
    </Alert>
  );
}

// ============================================================================
// Combined Loading Indicator (for multiple operations)
// ============================================================================

export function CombinedLoadingIndicator({ 
  operations 
}: { 
  operations: Array<'annotations' | 'chunks' | 'quality'> 
}) {
  const operationLabels = {
    annotations: 'annotations',
    chunks: 'semantic chunks',
    quality: 'quality data',
  };

  const operationList = operations.map(op => operationLabels[op]).join(', ');

  return (
    <Alert className="border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-900">
      <Loader2 className="h-4 w-4 animate-spin text-blue-600 dark:text-blue-400" aria-hidden="true" />
      <AlertDescription className="text-sm text-blue-800 dark:text-blue-300">
        Loading {operationList}...
      </AlertDescription>
    </Alert>
  );
}

// ============================================================================
// Inline Loading Badge (for gutter/overlay)
// ============================================================================

export function InlineLoadingBadge({ 
  text = 'Loading...',
  variant = 'default' 
}: { 
  text?: string;
  variant?: 'default' | 'small';
}) {
  const sizeClass = variant === 'small' ? 'h-3 w-3' : 'h-4 w-4';
  const textClass = variant === 'small' ? 'text-xs' : 'text-sm';

  return (
    <div 
      className="inline-flex items-center gap-1.5 px-2 py-1 bg-muted/80 rounded-md"
      role="status"
      aria-live="polite"
      aria-label={text}
    >
      <Loader2 className={`${sizeClass} animate-spin text-muted-foreground`} aria-hidden="true" />
      <span className={`${textClass} text-muted-foreground font-medium`}>{text}</span>
      <span className="sr-only">{text}</span>
    </div>
  );
}

// ============================================================================
// Floating Loading Indicator (bottom-right corner)
// ============================================================================

export function FloatingLoadingIndicator({ 
  operations 
}: { 
  operations: Array<{ name: string; label: string }> 
}) {
  if (operations.length === 0) return null;

  return (
    <div 
      className="fixed bottom-4 right-4 z-50 bg-card border shadow-lg rounded-lg p-3 max-w-xs"
      role="status"
      aria-live="polite"
      aria-label="Loading operations in progress"
    >
      <div className="space-y-2">
        {operations.map((op) => (
          <div key={op.name} className="flex items-center gap-2 text-sm">
            <Loader2 className="h-3 w-3 animate-spin text-primary" aria-hidden="true" />
            <span className="text-muted-foreground">{op.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
