import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Info, ArrowUp } from 'lucide-react';
import { SearchResult, SortOption } from '@/types/search';
import { ResourceCard } from '@/components/resource/ResourceCard';
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';
import { SkeletonList } from '@/components/common/Skeleton';

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
  sortBy: SortOption;
  onSortChange: (sort: SortOption) => void;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  query,
  onLoadMore,
  hasMore,
  isLoading,
  sortBy,
  onSortChange,
}) => {
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [showScrollTop, setShowScrollTop] = useState(false);

  const loadMoreRef = useInfiniteScroll({
    onLoadMore,
    hasMore,
    isLoading,
    threshold: 0.8,
  });

  React.useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 500);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleExpanded = (id: string) => {
    setExpandedResults((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const highlightKeywords = (text: string, keywords: string[]) => {
    if (!keywords.length) return text;

    const regex = new RegExp(`(${keywords.join('|')})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, index) =>
      keywords.some((kw) => kw.toLowerCase() === part.toLowerCase()) ? (
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-800 px-0.5 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (results.length === 0 && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-24 h-24 mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
          <Info className="w-12 h-12 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          No results found
        </h3>
        <p className="text-gray-600 dark:text-gray-400 max-w-md">
          Try adjusting your search query or filters to find what you're looking for.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Sort Controls */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {results.length} results for "{query}"
        </p>

        <select
          value={sortBy}
          onChange={(e) => onSortChange(e.target.value as SortOption)}
          className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          aria-label="Sort results"
        >
          <option value="relevance">Most Relevant</option>
          <option value="recent">Most Recent</option>
          <option value="quality">Highest Quality</option>
          <option value="title">Title (A-Z)</option>
        </select>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {results.map((result) => (
          <motion.div
            key={result.resource.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            {/* Resource Card */}
            <div className="p-4">
              <div className="flex items-start gap-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {highlightKeywords(result.resource.title, query.split(' '))}
                  </h3>

                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {result.resource.authors.join(', ')}
                  </p>

                  <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3">
                    {highlightKeywords(result.resource.abstract, query.split(' '))}
                  </p>

                  {/* Highlights */}
                  {result.highlights.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {result.highlights.slice(0, 2).map((highlight, index) => (
                        <div
                          key={index}
                          className="p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded border-l-2 border-yellow-400"
                        >
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                            {highlight.field}
                          </p>
                          <p className="text-sm text-gray-700 dark:text-gray-300">
                            ...{highlightKeywords(highlight.text, query.split(' '))}...
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Score Badge */}
                <div className="flex-shrink-0 text-center">
                  <div className="px-3 py-1 bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded-full text-sm font-semibold">
                    {Math.round(result.score * 100)}%
                  </div>
                  <button
                    onClick={() => toggleExpanded(result.resource.id)}
                    className="mt-2 text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1"
                    aria-label="Show relevance explanation"
                    aria-expanded={expandedResults.has(result.resource.id)}
                  >
                    <Info className="w-3 h-3" />
                    Why?
                  </button>
                </div>
              </div>
            </div>

            {/* Relevance Explanation */}
            <AnimatePresence>
              {expandedResults.has(result.resource.id) && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50"
                >
                  <div className="p-4 space-y-3">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                      Relevance Breakdown
                    </h4>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Keyword Match
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-500"
                              style={{ width: `${result.explanation.keywordScore * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">
                            {Math.round(result.explanation.keywordScore * 100)}%
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Semantic Similarity
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-green-500"
                              style={{ width: `${result.explanation.semanticScore * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">
                            {Math.round(result.explanation.semanticScore * 100)}%
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Sparse Embedding
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-purple-500"
                              style={{ width: `${result.explanation.sparseScore * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">
                            {Math.round(result.explanation.sparseScore * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>

                    {result.explanation.factors.length > 0 && (
                      <div className="pt-2">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Contributing Factors:
                        </p>
                        <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                          {result.explanation.factors.map((factor, index) => (
                            <li key={index}>• {factor}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>

      {/* Loading State */}
      {isLoading && <SkeletonList count={3} />}

      {/* Infinite Scroll Trigger */}
      {hasMore && <div ref={loadMoreRef} className="h-10" />}

      {/* Scroll to Top Button */}
      <AnimatePresence>
        {showScrollTop && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={scrollToTop}
            className="fixed bottom-8 right-8 p-3 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-lg transition-colors z-50"
            aria-label="Scroll to top"
          >
            <ArrowUp className="w-5 h-5" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
};
