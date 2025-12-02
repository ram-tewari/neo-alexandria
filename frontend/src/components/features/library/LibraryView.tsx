/**
 * LibraryView component with integrated filter sidebar
 * 
 * This is an enhanced version of the library view that includes:
 * - Responsive filter sidebar
 * - Empty state handling
 * - Filter button for mobile
 * - Batch selection mode
 * - Integration with existing LibraryPanel
 */

import React, { useState, useEffect, useRef } from 'react';
import { LibraryPanel } from '../LibraryPanel';
import { ResponsiveFilterSidebar, FilterButton } from './ResponsiveFilterSidebar';
import { EmptyState } from './EmptyState';
import { BatchToolbar } from './BatchToolbar';
import { Button } from '../../ui/Button';
import { DensityToggle } from '../../ui/DensityToggle';
import { useResourceFilters, useActiveFilterCount, useBatchSelection, useLocalStorage } from '../../../lib/hooks';
import { useInfiniteResources } from '../../../lib/hooks';
import type { FilterFacets } from './FilterSidebar';
import type { Density } from '../../ui/DensityToggle';

interface LibraryViewProps {
  /** Optional callback when a resource is clicked */
  onResourceClick?: (resource: any) => void;
  /** Optional facet data for filters */
  facets?: FilterFacets;
}

/**
 * Complete library view with filters and resource display
 */
export const LibraryView: React.FC<LibraryViewProps> = ({
  onResourceClick,
  facets,
}) => {
  const [filters, setFilters] = useResourceFilters();
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);
  const [batchMode, setBatchMode] = useState(false);
  const [density, setDensity] = useLocalStorage<Density>('view-density', 'comfortable');
  const activeFilterCount = useActiveFilterCount(filters);
  const lastClickedIndexRef = useRef<number>(-1);
  const isShiftPressedRef = useRef<boolean>(false);

  // Batch selection state
  const { selectedIds, toggleSelection, selectAll, clearSelection } = useBatchSelection();

  // Fetch resources with current filters
  const {
    resources,
    total,
    isLoading,
    error,
  } = useInfiniteResources({
    ...filters,
    pageSize: 20,
  });

  // Show empty state when no resources match filters
  const showEmptyState = !isLoading && !error && resources.length === 0;
  
  // Show error state when there's an error
  const showErrorState = !isLoading && error;

  // Handle batch mode toggle
  const handleBatchModeToggle = () => {
    if (batchMode) {
      // Exiting batch mode - clear selection
      clearSelection();
    }
    setBatchMode(!batchMode);
  };

  // Keyboard shortcuts for batch selection
  useEffect(() => {
    if (!batchMode) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Track Shift key state
      if (e.key === 'Shift') {
        isShiftPressedRef.current = true;
      }

      // Cmd/Ctrl + A: Select all visible resources
      if ((e.metaKey || e.ctrlKey) && e.key === 'a') {
        e.preventDefault();
        const allIds = resources.map(r => r.id);
        selectAll(allIds);
      }

      // Escape: Clear selection
      if (e.key === 'Escape') {
        e.preventDefault();
        clearSelection();
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      // Track Shift key state
      if (e.key === 'Shift') {
        isShiftPressedRef.current = false;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [batchMode, resources, selectAll, clearSelection]);

  // Enhanced toggle selection with Shift+Click support for range selection
  const handleToggleSelection = (id: string, index?: number) => {
    // If Shift is held and we have a previous click, select range
    if (isShiftPressedRef.current && index !== undefined && lastClickedIndexRef.current !== -1) {
      const start = Math.min(lastClickedIndexRef.current, index);
      const end = Math.max(lastClickedIndexRef.current, index);
      const rangeIds = resources.slice(start, end + 1).map(r => r.id);
      
      // Add all IDs in range to selection
      rangeIds.forEach(rangeId => {
        if (!selectedIds.has(rangeId)) {
          toggleSelection(rangeId);
        }
      });
    } else {
      // Normal toggle
      toggleSelection(id);
    }

    // Update last clicked index
    if (index !== undefined) {
      lastClickedIndexRef.current = index;
    }
  };

  return (
    <div className="flex h-full">
      {/* Desktop: Fixed sidebar, Mobile: Drawer */}
      <ResponsiveFilterSidebar
        filters={filters}
        onChange={setFilters}
        facets={facets}
        isOpen={isMobileFilterOpen}
        onOpenChange={setIsMobileFilterOpen}
      />

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header with filter button, density toggle, and batch mode toggle */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between gap-4">
          <div className="md:hidden">
            <FilterButton
              activeCount={activeFilterCount}
              onClick={() => setIsMobileFilterOpen(true)}
            />
          </div>
          <div className="flex-1" />
          <DensityToggle value={density} onChange={setDensity} />
          <Button
            variant={batchMode ? 'primary' : 'secondary'}
            size="sm"
            onClick={handleBatchModeToggle}
            aria-pressed={batchMode}
          >
            {batchMode ? 'Exit Batch Mode' : 'Batch Select'}
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {showErrorState ? (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center max-w-md">
                <div className="text-4xl mb-4">⚠️</div>
                <h3 className="text-lg font-semibold mb-2">Failed to Load Resources</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {error instanceof Error ? error.message : 'An error occurred while loading resources'}
                </p>
                <Button
                  variant="primary"
                  onClick={() => window.location.reload()}
                >
                  Retry
                </Button>
              </div>
            </div>
          ) : showEmptyState ? (
            <EmptyState
              filters={filters}
              onClearFilters={() => setFilters({})}
            />
          ) : (
            <LibraryPanel
              filters={filters}
              onResourceClick={onResourceClick}
              batchMode={batchMode}
              selectedIds={selectedIds}
              onToggleSelection={handleToggleSelection}
              density={density}
            />
          )}
        </div>
      </div>

      {/* Batch toolbar - appears when items are selected */}
      {batchMode && (
        <BatchToolbar
          selectedCount={selectedIds.size}
          selectedIds={Array.from(selectedIds)}
          onClear={clearSelection}
        />
      )}
    </div>
  );
};

/**
 * Example usage with mock facets
 * 
 * @example
 * ```tsx
 * const mockFacets: FilterFacets = {
 *   classifications: [
 *     { label: 'Computer Science', value: 'cs', count: 42 },
 *     { label: 'Mathematics', value: 'math', count: 28 },
 *   ],
 *   types: [
 *     { label: 'Article', value: 'article', count: 35 },
 *     { label: 'Book', value: 'book', count: 15 },
 *   ],
 *   languages: [
 *     { label: 'English', value: 'en', count: 50 },
 *     { label: 'Spanish', value: 'es', count: 10 },
 *   ],
 * };
 * 
 * <LibraryView facets={mockFacets} />
 * ```
 */
