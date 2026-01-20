/**
 * LibraryPanel component
 * Main panel for displaying resources with view toggle, infinite scroll, and loading states
 */

import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ViewToggle, type ViewMode } from '../../ui/ViewToggle';
import { ResourceGrid } from '../ResourceGrid';
import { ResourceTable } from '../ResourceTable';
import { SkeletonCard } from '../../ui/Skeleton';
import { Button } from '../../ui/Button';
import { useLocalStorage } from '../../../lib/hooks/useLocalStorage';
import { useInfiniteResources, useInfiniteScroll } from '../../../lib/hooks';
import { slideUp } from '../../../lib/utils/animations';
import type { Resource, ResourceRead, ResourceListParams } from '../../../lib/api/types';
import type { Density } from '../../ui/DensityToggle';

interface LibraryPanelProps {
  /** Optional filters to apply to the resource list */
  filters?: Omit<ResourceListParams, 'limit' | 'offset'>;
  /** Callback when a resource is clicked */
  onResourceClick?: (resource: Resource | ResourceRead) => void;
  /** Whether batch mode is active */
  batchMode?: boolean;
  /** Set of selected resource IDs */
  selectedIds?: Set<string>;
  /** Callback when selection changes */
  onToggleSelection?: (id: string, index?: number) => void;
  /** View density setting */
  density?: Density;
}

/**
 * Library panel with view toggle, infinite scroll, and resource display
 */
export const LibraryPanel: React.FC<LibraryPanelProps> = ({
  filters,
  onResourceClick,
  batchMode = false,
  selectedIds = new Set(),
  onToggleSelection,
  density = 'comfortable',
}) => {
  const [viewMode, setViewMode] = useLocalStorage<ViewMode>('library-view-mode', 'grid');

  // Use infinite scroll hook for data fetching
  const {
    resources,
    total,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteResources({
    ...filters,
    pageSize: 20,
  });

  // Set up infinite scroll sentinel
  const sentinelRef = useInfiniteScroll({
    onIntersect: fetchNextPage,
    enabled: hasNextPage && !isFetchingNextPage,
    threshold: 0.8,
  });

  // Initial loading state
  if (isLoading) {
    return (
      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Library</h2>
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Library</h2>
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            Failed to load resources
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
          <Button
            variant="primary"
            onClick={() => window.location.reload()}
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Library
          {total > 0 && (
            <span className="ml-2 text-base font-normal text-gray-600 dark:text-gray-400">
              ({total} {total === 1 ? 'resource' : 'resources'})
            </span>
          )}
        </h2>
        <ViewToggle value={viewMode} onChange={setViewMode} />
      </div>
      
      <AnimatePresence mode="wait">
        {viewMode === 'grid' ? (
          <motion.div
            key="grid"
            {...slideUp}
          >
            <ResourceGrid 
              resources={resources} 
              onResourceClick={onResourceClick}
              batchMode={batchMode}
              selectedIds={selectedIds}
              onToggleSelection={onToggleSelection}
              density={density}
            />
            
            {/* Sentinel element for infinite scroll */}
            <div ref={sentinelRef} className="h-20" data-testid="scroll-sentinel" />
            
            {/* Loading indicator for next page */}
            {isFetchingNextPage && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <SkeletonCard key={`loading-${i}`} />
                ))}
              </div>
            )}
            
            {/* End of list indicator */}
            {!hasNextPage && resources.length > 0 && (
              <div className="text-center py-8 text-sm text-gray-600 dark:text-gray-400">
                You've reached the end of the list
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="table"
            {...slideUp}
          >
            <ResourceTable 
              resources={resources} 
              onResourceClick={onResourceClick} 
            />
            
            {/* Sentinel element for infinite scroll */}
            <div ref={sentinelRef} className="h-20" data-testid="scroll-sentinel" />
            
            {/* Loading indicator for next page */}
            {isFetchingNextPage && (
              <div className="py-4 text-center text-sm text-gray-600 dark:text-gray-400">
                Loading more resources...
              </div>
            )}
            
            {/* End of list indicator */}
            {!hasNextPage && resources.length > 0 && (
              <div className="text-center py-8 text-sm text-gray-600 dark:text-gray-400">
                You've reached the end of the list
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
