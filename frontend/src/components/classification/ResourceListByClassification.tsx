// Neo Alexandria 2.0 Frontend - Resource List By Classification Component
// Displays resources filtered by selected classification with grid/list view and pagination

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useResources } from '@/hooks/useApi';
import { ResourceCard } from '@/components/resources/ResourceCard';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner, LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { Grid, List, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/cn';
import type { Resource } from '@/types/api';

interface ResourceListByClassificationProps {
  classificationCode: string;
  onResourcesLoaded?: (count: number) => void;
}

const ResourceListByClassification: React.FC<ResourceListByClassificationProps> = ({
  classificationCode,
  onResourcesLoaded,
}) => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [page, setPage] = useState(0);
  const itemsPerPage = 12;

  // Fetch resources filtered by classification
  const { data, isLoading, error } = useResources({
    classification_code: classificationCode,
    limit: itemsPerPage,
    offset: page * itemsPerPage,
    sort_by: 'updated_at',
    sort_dir: 'desc',
  });

  // Notify parent of resource count
  React.useEffect(() => {
    if (data?.total !== undefined && onResourcesLoaded) {
      onResourcesLoaded(data.total);
    }
  }, [data?.total, onResourcesLoaded]);

  const totalPages = data?.total ? Math.ceil(data.total / itemsPerPage) : 0;

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <LoadingSkeleton lines={1} className="w-48" />
          <LoadingSkeleton lines={1} className="w-32" />
        </div>
        <div className={cn(
          'grid gap-4',
          viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'
        )}>
          {Array.from({ length: 6 }).map((_, i) => (
            <LoadingSkeleton key={i} lines={8} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-2">Error loading resources</p>
        <p className="text-charcoal-grey-400 text-sm">
          {error instanceof Error ? error.message : 'An unexpected error occurred'}
        </p>
      </div>
    );
  }

  if (!data?.items || data.items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-charcoal-grey-400">
          No resources found for this classification
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with view toggle and count */}
      <div className="flex items-center justify-between">
        <div className="text-charcoal-grey-300">
          <span className="font-medium">{data.total}</span> resource{data.total !== 1 ? 's' : ''} found
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center space-x-2">
          <Button
            variant={viewMode === 'grid' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('grid')}
            icon={<Grid />}
            aria-label="Grid view"
          />
          <Button
            variant={viewMode === 'list' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('list')}
            icon={<List />}
            aria-label="List view"
          />
        </div>
      </div>

      {/* Resource Grid/List */}
      <motion.div
        key={viewMode}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.2 }}
        className={cn(
          'grid gap-4',
          viewMode === 'grid' 
            ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
            : 'grid-cols-1'
        )}
      >
        {data.items.map((resource: Resource) => (
          <motion.div
            key={resource.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ResourceCard
              resource={resource}
              viewMode={viewMode}
            />
          </motion.div>
        ))}
      </motion.div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2 pt-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            icon={<ChevronLeft />}
          >
            Previous
          </Button>

          <div className="flex items-center space-x-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum: number;
              if (totalPages <= 5) {
                pageNum = i;
              } else if (page < 3) {
                pageNum = i;
              } else if (page > totalPages - 4) {
                pageNum = totalPages - 5 + i;
              } else {
                pageNum = page - 2 + i;
              }

              return (
                <Button
                  key={pageNum}
                  variant={page === pageNum ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setPage(pageNum)}
                >
                  {pageNum + 1}
                </Button>
              );
            })}
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            icon={<ChevronRight />}
            iconPosition="right"
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
};

export { ResourceListByClassification };
