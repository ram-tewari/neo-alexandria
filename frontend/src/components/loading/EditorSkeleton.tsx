/**
 * EditorSkeleton - Loading skeleton for Monaco editor
 */
import { Skeleton } from './Skeleton';

export function EditorSkeleton() {
  return (
    <div className="h-full w-full bg-[#1e1e1e] dark:bg-[#1e1e1e] p-4" role="status" aria-label="Loading editor">
      <div className="space-y-3">
        {/* Line numbers and code lines */}
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            {/* Line number */}
            <Skeleton className="w-8 h-4 bg-gray-700" animation="pulse" />
            {/* Code line with varying widths */}
            <Skeleton
              className="h-4 bg-gray-700"
              width={`${Math.random() * 40 + 40}%`}
              animation="pulse"
            />
          </div>
        ))}
      </div>
      <span className="sr-only">Loading editor content...</span>
    </div>
  );
}
