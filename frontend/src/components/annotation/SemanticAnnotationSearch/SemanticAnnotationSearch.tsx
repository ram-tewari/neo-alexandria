import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Sparkles, TrendingUp } from 'lucide-react';
import { useSemanticSearch, useConceptClusters } from '@/hooks/useAnnotations';
import { Annotation } from '@/types/annotation';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { formatDistanceToNow } from 'date-fns';

interface SemanticAnnotationSearchProps {
  onAnnotationClick?: (annotation: Annotation) => void;
}

export const SemanticAnnotationSearch: React.FC<SemanticAnnotationSearchProps> = ({
  onAnnotationClick,
}) => {
  const [query, setQuery] = useState('');
  const [searchEnabled, setSearchEnabled] = useState(false);
  const { data: searchResults = [], isLoading: searchLoading } = useSemanticSearch(query, searchEnabled);
  const { data: clusters = [], isLoading: clustersLoading } = useConceptClusters();
  const prefersReducedMotion = useReducedMotion();

  const handleSearch = () => {
    if (query.trim()) {
      setSearchEnabled(true);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Semantic Search
          </h2>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Find annotations by conceptual similarity
        </p>

        {/* Search Input */}
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Search by concept or meaning..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={!query.trim() || searchLoading}
            className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            Search
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {/* Search Results */}
        {searchEnabled && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Search Results
            </h3>

            {searchLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg" />
                  </div>
                ))}
              </div>
            ) : searchResults.length > 0 ? (
              <div className="space-y-4">
                {searchResults.map((result, index) => (
                  <motion.div
                    key={result.annotation.id}
                    initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => onAnnotationClick?.(result.annotation)}
                    className="bg-white dark:bg-gray-800 rounded-lg border-l-4 p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                    style={{ borderLeftColor: result.annotation.color }}
                  >
                    {/* Similarity Badge */}
                    <div className="flex items-center justify-between mb-2">
                      <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full">
                        {Math.round(result.similarity * 100)}% similar
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {formatDistanceToNow(new Date(result.annotation.createdAt), { addSuffix: true })}
                      </span>
                    </div>

                    {/* Annotation Text */}
                    <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                      "{result.annotation.text}"
                    </p>

                    {/* Note */}
                    {result.annotation.note && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 italic mb-2">
                        {result.annotation.note}
                      </p>
                    )}

                    {/* Tags */}
                    {result.annotation.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {result.annotation.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Related Annotations */}
                    {result.relatedAnnotations.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                        <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                          Related annotations:
                        </p>
                        <div className="space-y-2">
                          {result.relatedAnnotations.slice(0, 2).map((related) => (
                            <div
                              key={related.annotation.id}
                              className="text-xs text-gray-600 dark:text-gray-400 pl-3 border-l-2 border-gray-300 dark:border-gray-600"
                            >
                              <span className="font-medium">
                                {Math.round(related.similarity * 100)}%
                              </span>
                              {' - '}
                              {related.annotation.text.slice(0, 60)}...
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-400">
                  No similar annotations found
                </p>
              </div>
            )}
          </div>
        )}

        {/* Concept Clusters */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Concept Clusters
            </h3>
          </div>

          {clustersLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded-lg" />
                </div>
              ))}
            </div>
          ) : clusters.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {clusters.map((cluster, index) => (
                <motion.div
                  key={cluster.id}
                  initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white dark:bg-gray-800 rounded-lg border-2 p-4 shadow-sm hover:shadow-md transition-shadow"
                  style={{ borderColor: cluster.color }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-900 dark:text-white">
                      {cluster.label}
                    </h4>
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                      {cluster.annotations.length} annotations
                    </span>
                  </div>

                  <div className="space-y-2">
                    {cluster.annotations.slice(0, 3).map((annotation) => (
                      <div
                        key={annotation.id}
                        onClick={() => onAnnotationClick?.(annotation)}
                        className="text-sm text-gray-600 dark:text-gray-400 p-2 bg-gray-50 dark:bg-gray-700/50 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                      >
                        {annotation.text.slice(0, 80)}
                        {annotation.text.length > 80 && '...'}
                      </div>
                    ))}
                    {cluster.annotations.length > 3 && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                        +{cluster.annotations.length - 3} more
                      </p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">
                No concept clusters available yet
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
