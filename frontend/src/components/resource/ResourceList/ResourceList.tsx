import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Grid, List, Rows, Loader2 } from 'lucide-react';
import { Resource, ViewMode, DensityMode } from '@/types/resource';
import { ResourceCard } from '../ResourceCard';
import { SkeletonCard, SkeletonList } from '@/components/common/Skeleton';
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface ResourceListProps {
  resources: Resource[];
  view?: ViewMode;
  density?: DensityMode;
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
  selectedIds?: string[];
  onSelectionChange?: (ids: string[]) => void;
  onResourceClick?: (id: string) => void;
}

export const ResourceList: React.FC<ResourceListProps> = ({
  resources,
  view = 'card',
  density = 'comfortable',
  onLoadMore,
  hasMore,
  isLoading,
  selectedIds = [],
  onSelectionChange,
  onResourceClick,
}) => {
  const [localView, setLocalView] = useState<ViewMode>(view);
  const loadMoreRef = useInfiniteScroll({
    onLoadMore,
    hasMore,
    isLoading,
    threshold: 0.8,
  });
  const prefersReducedMotion = useReducedMotion();

  const handleSelect = (id: string) => {
    if (!onSelectionChange) return;

    const newSelection = selectedIds.includes(id)
      ? selectedIds.filter((selectedId) => selectedId !== id)
      : [...selectedIds, id];

    onSelectionChange(newSelection);
  };

  const handleSelectAll = () => {
    if (!onSelectionChange) return;

    if (selectedIds.length === resources.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(resources.map((r) => r.id));
    }
  };

  const getGridClasses = () => {
    if (localView !== 'card') return '';

    const densityMap = {
      comfortable: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
      compact: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4',
      spacious: 'grid-cols-1 md:grid-cols-2 gap-8',
    };

    return `grid ${densityMap[density]}`;
  };

  const getListClasses = () => {
    if (localView === 'card') return '';

    const densityMap = {
      comfortable: 'space-y-4',
      compact: 'space-y-2',
      spacious: 'space-y-6',
    };

    return densityMap[density];
  };

  if (resources.length === 0 && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-24 h-24 mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
          <List className="w-12 h-12 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          No resources found
        </h3>
        <p className="text-gray-600 dark:text-gray-400 max-w-md">
          Try adjusting your filters or upload some documents to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* View Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {onSelectionChange && resources.length > 0 && (
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                checked={selectedIds.length === resources.length && resources.length > 0}
                onChange={handleSelectAll}
                className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
                aria-label="Select all resources"
              />
              {selectedIds.length > 0 && (
                <span className="font-medium">
                  {selectedIds.length} selected
                </span>
              )}
            </label>
          )}
        </div>

        <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setLocalView('card')}
            className={`p-2 rounded transition-colors ${
              localView === 'card'
                ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
            aria-label="Card view"
            aria-pressed={localView === 'card'}
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setLocalView('list')}
            className={`p-2 rounded transition-colors ${
              localView === 'list'
                ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
            aria-label="List view"
            aria-pressed={localView === 'list'}
          >
            <List className="w-4 h-4" />
          </button>
          <button
            onClick={() => setLocalView('compact')}
            className={`p-2 rounded transition-colors ${
              localView === 'compact'
                ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
            aria-label="Compact view"
            aria-pressed={localView === 'compact'}
          >
            <Rows className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Resources Grid/List */}
      <motion.div
        layout={!prefersReducedMotion}
        className={localView === 'card' ? getGridClasses() : getListClasses()}
      >
        <AnimatePresence mode="popLayout">
          {resources.map((resource) => (
            <ResourceCard
              key={resource.id}
              resource={resource}
              view={localView}
              isSelected={selectedIds.includes(resource.id)}
              onSelect={onSelectionChange ? handleSelect : undefined}
              onClick={onResourceClick}
            />
          ))}
        </AnimatePresence>
      </motion.div>

      {/* Loading State */}
      {isLoading && (
        <div className={localView === 'card' ? getGridClasses() : getListClasses()}>
          {localView === 'card' ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <SkeletonList count={3} />
          )}
        </div>
      )}

      {/* Infinite Scroll Trigger */}
      {hasMore && (
        <div
          ref={loadMoreRef}
          className="flex items-center justify-center py-8"
        >
          <Loader2 className="w-6 h-6 text-primary-600 animate-spin" aria-label="Loading more resources" />
        </div>
      )}

      {/* End of List */}
      {!hasMore && resources.length > 0 && (
        <div className="text-center py-8 text-sm text-gray-500 dark:text-gray-400">
          You've reached the end of the list
        </div>
      )}
    </div>
  );
};
