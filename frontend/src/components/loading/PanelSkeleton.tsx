/**
 * PanelSkeleton - Loading skeleton for side panels
 */
import { Skeleton } from './Skeleton';

export interface PanelSkeletonProps {
  lines?: number;
  showHeader?: boolean;
}

export function PanelSkeleton({ lines = 5, showHeader = true }: PanelSkeletonProps) {
  return (
    <div className="p-4 space-y-4" role="status" aria-label="Loading panel">
      {showHeader && (
        <div className="space-y-2">
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      )}
      <div className="space-y-3">
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton key={i} className="h-4" width={`${Math.random() * 30 + 60}%`} />
        ))}
      </div>
      <span className="sr-only">Loading panel content...</span>
    </div>
  );
}

/**
 * AnnotationPanelSkeleton - Skeleton for annotation panel
 */
export function AnnotationPanelSkeleton() {
  return (
    <div className="p-4 space-y-4" role="status" aria-label="Loading annotations">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="border rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-16" />
          </div>
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-4/5" />
          <div className="flex gap-2 mt-2">
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-20 rounded-full" />
          </div>
        </div>
      ))}
      <span className="sr-only">Loading annotations...</span>
    </div>
  );
}

/**
 * ChunkPanelSkeleton - Skeleton for chunk metadata panel
 */
export function ChunkPanelSkeleton() {
  return (
    <div className="p-4 space-y-4" role="status" aria-label="Loading chunk metadata">
      <div className="space-y-2">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-full" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <div className="flex gap-2">
          <Skeleton className="h-6 w-20 rounded-full" />
          <Skeleton className="h-6 w-24 rounded-full" />
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
      </div>
      <span className="sr-only">Loading chunk metadata...</span>
    </div>
  );
}
