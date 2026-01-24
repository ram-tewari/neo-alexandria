/**
 * Loading Skeleton Components
 * 
 * Provides loading states and skeletons for various editor components:
 * - Monaco Editor loading skeleton
 * - Hover card loading skeleton (already exists in HoverCardProvider)
 * - API operation loading indicators
 * - Panel loading skeletons
 * 
 * Requirements: 5.5 - Loading states for better UX
 */

import { Skeleton } from '@/components/ui/skeleton';
import { Loader2 } from 'lucide-react';

// ============================================================================
// Monaco Editor Loading Skeleton
// ============================================================================

export function MonacoEditorSkeleton() {
  return (
    <div 
      className="flex flex-col h-full bg-background p-4 space-y-2"
      role="status"
      aria-live="polite"
      aria-label="Loading code editor"
    >
      {/* Editor header skeleton */}
      <div className="flex items-center gap-2 mb-4">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-24" />
        <div className="flex-1" />
        <Skeleton className="h-8 w-8 rounded" />
        <Skeleton className="h-8 w-8 rounded" />
      </div>

      {/* Line numbers and code skeleton */}
      <div className="flex-1 space-y-2">
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            {/* Line number */}
            <Skeleton className="h-4 w-8" />
            {/* Code line with varying widths */}
            <Skeleton 
              className="h-4" 
              style={{ width: `${Math.random() * 40 + 60}%` }} 
            />
          </div>
        ))}
      </div>

      {/* Loading message */}
      <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm">
        <div className="flex items-center gap-3 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
          <span className="text-sm font-medium">Loading code editor...</span>
        </div>
      </div>

      <span className="sr-only">Loading code editor, please wait...</span>
    </div>
  );
}

// ============================================================================
// Annotation Panel Loading Skeleton
// ============================================================================

export function AnnotationPanelSkeleton() {
  return (
    <div 
      className="space-y-4 p-4"
      role="status"
      aria-live="polite"
      aria-label="Loading annotations"
    >
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-8 w-8 rounded" />
      </div>

      {/* Search bar skeleton */}
      <Skeleton className="h-10 w-full rounded-md" />

      {/* Annotation list skeleton */}
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="space-y-2 p-3 border rounded-md">
            <div className="flex items-center gap-2">
              <Skeleton className="h-3 w-3 rounded-full" />
              <Skeleton className="h-4 w-24" />
            </div>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <div className="flex gap-2 mt-2">
              <Skeleton className="h-5 w-16 rounded-full" />
              <Skeleton className="h-5 w-20 rounded-full" />
            </div>
          </div>
        ))}
      </div>

      <span className="sr-only">Loading annotations, please wait...</span>
    </div>
  );
}

// ============================================================================
// Chunk Metadata Panel Loading Skeleton
// ============================================================================

export function ChunkMetadataSkeleton() {
  return (
    <div 
      className="space-y-4 p-4 border rounded-lg"
      role="status"
      aria-live="polite"
      aria-label="Loading chunk metadata"
    >
      {/* Title skeleton */}
      <Skeleton className="h-6 w-48" />

      {/* Metadata items */}
      <div className="space-y-3">
        <div className="space-y-1">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-4 w-full" />
        </div>
        <div className="space-y-1">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-4 w-32" />
        </div>
        <div className="space-y-1">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-4 w-24" />
        </div>
      </div>

      {/* Navigation buttons */}
      <div className="flex gap-2 pt-4">
        <Skeleton className="h-9 flex-1 rounded-md" />
        <Skeleton className="h-9 flex-1 rounded-md" />
      </div>

      <span className="sr-only">Loading chunk metadata, please wait...</span>
    </div>
  );
}

// ============================================================================
// Quality Badge Loading Indicator
// ============================================================================

export function QualityBadgeLoadingIndicator() {
  return (
    <div 
      className="flex items-center gap-2 text-xs text-muted-foreground p-2 bg-muted/50 rounded-md"
      role="status"
      aria-live="polite"
      aria-label="Loading quality data"
    >
      <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
      <span>Loading quality data...</span>
      <span className="sr-only">Loading quality data, please wait...</span>
    </div>
  );
}

// ============================================================================
// Inline Loading Spinner (for small operations)
// ============================================================================

export function InlineLoadingSpinner({ 
  text = 'Loading...',
  size = 'sm' 
}: { 
  text?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
}) {
  const sizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  return (
    <div 
      className="flex items-center gap-2 text-muted-foreground"
      role="status"
      aria-live="polite"
      aria-label={text}
    >
      <Loader2 className={`${sizeClasses[size]} animate-spin`} aria-hidden="true" />
      <span className="text-sm">{text}</span>
      <span className="sr-only">{text}</span>
    </div>
  );
}

// ============================================================================
// API Operation Loading Overlay
// ============================================================================

export function ApiOperationLoadingOverlay({ 
  operation = 'Loading',
  transparent = false 
}: { 
  operation?: string;
  transparent?: boolean;
}) {
  return (
    <div 
      className={`absolute inset-0 flex items-center justify-center ${
        transparent ? 'bg-background/50' : 'bg-background/80'
      } backdrop-blur-sm z-50`}
      role="status"
      aria-live="polite"
      aria-label={`${operation}...`}
    >
      <div className="flex flex-col items-center gap-3 p-6 bg-card border rounded-lg shadow-lg">
        <Loader2 className="h-8 w-8 animate-spin text-primary" aria-hidden="true" />
        <div className="text-center">
          <p className="text-sm font-medium text-foreground">{operation}...</p>
          <p className="text-xs text-muted-foreground mt-1">Please wait</p>
        </div>
      </div>
      <span className="sr-only">{operation}, please wait...</span>
    </div>
  );
}

// ============================================================================
// File Tree Loading Skeleton
// ============================================================================

export function FileTreeSkeleton() {
  return (
    <div 
      className="space-y-2 p-4"
      role="status"
      aria-live="polite"
      aria-label="Loading file tree"
    >
      {/* Root folder */}
      <div className="flex items-center gap-2">
        <Skeleton className="h-4 w-4" />
        <Skeleton className="h-4 w-32" />
      </div>

      {/* Nested items */}
      <div className="ml-4 space-y-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center gap-2" style={{ marginLeft: `${(i % 3) * 12}px` }}>
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-4" style={{ width: `${Math.random() * 80 + 80}px` }} />
          </div>
        ))}
      </div>

      <span className="sr-only">Loading file tree, please wait...</span>
    </div>
  );
}

// ============================================================================
// Generic Card Loading Skeleton
// ============================================================================

export function CardLoadingSkeleton({ 
  lines = 3,
  showHeader = true 
}: { 
  lines?: number;
  showHeader?: boolean;
}) {
  return (
    <div 
      className="space-y-3 p-4 border rounded-lg"
      role="status"
      aria-live="polite"
      aria-label="Loading content"
    >
      {showHeader && <Skeleton className="h-6 w-40" />}
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton 
            key={i} 
            className="h-4" 
            style={{ width: i === lines - 1 ? '60%' : '100%' }} 
          />
        ))}
      </div>
      <span className="sr-only">Loading content, please wait...</span>
    </div>
  );
}

// ============================================================================
// Button Loading State
// ============================================================================

export function ButtonLoadingSpinner({ size = 'sm' }: { size?: 'xs' | 'sm' | 'md' }) {
  const sizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
  };

  return (
    <Loader2 
      className={`${sizeClasses[size]} animate-spin`} 
      aria-hidden="true"
    />
  );
}
