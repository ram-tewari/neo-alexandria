import React, { useState } from 'react';
import { Upload as UploadIcon, Filter, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useResources } from '@/hooks/useResources';
import { ResourceList } from '@/components/resource/ResourceList';
import { UploadZone } from '@/components/resource/UploadZone';
import { ResourceFilters } from '@/types/resource';

export const Library: React.FC = () => {
  const [showUpload, setShowUpload] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<ResourceFilters>({});
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useResources(filters);

  const resources = data?.pages.flatMap((page) => page.items) ?? [];

  const handleResourceClick = (id: string) => {
    // Navigate to resource detail page
    window.location.href = `/resources/${id}`;
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Library
            </h1>
            <p className="mt-1 text-gray-600 dark:text-gray-400">
              {resources.length} resources
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
                ${
                  showFilters
                    ? 'bg-primary-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                }
              `}
              aria-label="Toggle filters"
              aria-pressed={showFilters}
            >
              <Filter className="w-4 h-4" />
              Filters
            </button>

            <button
              onClick={() => setShowUpload(!showUpload)}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              aria-label="Upload resources"
            >
              <UploadIcon className="w-4 h-4" />
              Upload
            </button>
          </div>
        </div>

        {/* Upload Zone */}
        <AnimatePresence>
          {showUpload && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8"
            >
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Upload Resources
                  </h2>
                  <button
                    onClick={() => setShowUpload(false)}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    aria-label="Close upload"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <UploadZone />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Filters Sidebar */}
        <div className="flex gap-8">
          <AnimatePresence>
            {showFilters && (
              <motion.aside
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="w-64 flex-shrink-0"
              >
                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 shadow-sm sticky top-8">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Filters
                  </h2>

                  {/* Type Filter */}
                  <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-gray-200 mb-3">
                      Type
                    </h3>
                    <div className="space-y-2">
                      {['pdf', 'url', 'arxiv'].map((type) => (
                        <label
                          key={type}
                          className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:text-gray-900 dark:hover:text-white transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={filters.type?.includes(type as any) ?? false}
                            onChange={(e) => {
                              const newTypes = e.target.checked
                                ? [...(filters.type ?? []), type as any]
                                : (filters.type ?? []).filter((t) => t !== type);
                              setFilters({ ...filters, type: newTypes });
                            }}
                            className="w-4 h-4 text-primary-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-primary-500"
                          />
                          {type.toUpperCase()}
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Quality Filter */}
                  <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-gray-200 mb-3">
                      Quality Score
                    </h3>
                    <div className="space-y-2">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={filters.qualityMin ?? 0}
                        onChange={(e) =>
                          setFilters({
                            ...filters,
                            qualityMin: parseInt(e.target.value),
                          })
                        }
                        className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary-600"
                        aria-label="Minimum quality score"
                      />
                      <div className="flex justify-between text-xs text-gray-700 dark:text-gray-300 font-medium">
                        <span>{filters.qualityMin ?? 0}</span>
                        <span>100</span>
                      </div>
                    </div>
                  </div>

                  {/* Clear Filters */}
                  <button
                    onClick={() => setFilters({})}
                    className="w-full px-4 py-2 text-sm font-medium text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors border border-gray-200 dark:border-gray-600"
                  >
                    Clear All Filters
                  </button>
                </div>
              </motion.aside>
            )}
          </AnimatePresence>

          {/* Resource List */}
          <div className="flex-1">
            <ResourceList
              resources={resources}
              onLoadMore={() => fetchNextPage()}
              hasMore={hasNextPage ?? false}
              isLoading={isLoading || isFetchingNextPage}
              selectedIds={selectedIds}
              onSelectionChange={setSelectedIds}
              onResourceClick={handleResourceClick}
            />
          </div>
        </div>

        {/* Floating Action Bar (when items selected) */}
        <AnimatePresence>
          {selectedIds.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50"
            >
              <div className="bg-gray-900 dark:bg-gray-800 text-white rounded-lg shadow-2xl px-6 py-4 flex items-center gap-4">
                <span className="font-medium">
                  {selectedIds.length} selected
                </span>
                <div className="flex items-center gap-2">
                  <button
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-md transition-colors text-sm font-medium"
                    onClick={() => {
                      // Handle batch delete
                      setSelectedIds([]);
                    }}
                  >
                    Delete
                  </button>
                  <button
                    className="px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-md transition-colors text-sm font-medium"
                    onClick={() => {
                      // Handle add to collection
                      setSelectedIds([]);
                    }}
                  >
                    Add to Collection
                  </button>
                  <button
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors text-sm font-medium"
                    onClick={() => setSelectedIds([])}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
