// Neo Alexandria 2.0 Frontend - Search Page
// Advanced search with hybrid search and faceted filtering

import React, { useState, useCallback, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { HybridWeightSlider } from '@/components/search/HybridWeightSlider';
import { FacetPanel } from '@/components/search/FacetPanel';
import { SearchResults } from '@/components/search/SearchResults';
import { useSearchManager } from '@/hooks/useSearch';
import { 
  Search, 
  Filter, 
  SlidersHorizontal,
  Grid3x3,
  List as ListIcon,
  ChevronLeft,
  ChevronRight,
  SortAsc,
  SortDesc,
  X
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { formatNumber } from '@/utils/format';
import type { SearchQuery, SearchFilters } from '@/types/api';

type ViewMode = 'grid' | 'list';
type SortField = 'relevance' | 'updated_at' | 'created_at' | 'quality_score' | 'title';
type SortDirection = 'asc' | 'desc';

const SearchPage: React.FC = () => {
  // URL search params for shareable searches
  const [searchParams, setSearchParams] = useSearchParams();
  
  // View state
  const [viewMode, setViewMode] = useState<ViewMode>(
    (searchParams.get('view') as ViewMode) || 'list'
  );
  const [showFilters, setShowFilters] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Search state
  const [searchText, setSearchText] = useState(searchParams.get('q') || '');
  const [hybridWeight, setHybridWeight] = useState(
    Number(searchParams.get('hybrid_weight')) || 0.5
  );
  const [filters, setFilters] = useState<SearchFilters>({
    classification_code: searchParams.getAll('classification_code'),
    type: searchParams.getAll('type'),
    language: searchParams.getAll('language'),
    read_status: searchParams.getAll('read_status') as any[],
    min_quality: searchParams.get('min_quality') ? Number(searchParams.get('min_quality')) : undefined,
    subject_any: searchParams.getAll('subject_any'),
  });
  
  // Sorting state
  const [sortField, setSortField] = useState<SortField>(
    (searchParams.get('sort_by') as SortField) || 'relevance'
  );
  const [sortDirection, setSortDirection] = useState<SortDirection>(
    (searchParams.get('sort_dir') as SortDirection) || 'desc'
  );
  
  // Pagination state
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);
  const itemsPerPage = 25;

  // Build search query
  const searchQuery: SearchQuery = {
    text: searchText || undefined,
    filters: Object.keys(filters).length > 0 ? filters : undefined,
    hybrid_weight: hybridWeight,
    sort_by: sortField,
    sort_dir: sortDirection,
    limit: itemsPerPage,
    offset: (page - 1) * itemsPerPage,
  };

  // Use search hook with debouncing
  const { 
    data, 
    isLoading, 
    isDebouncing, 
    error 
  } = useSearchManager(300);

  // Perform search when query changes
  const performSearch = useCallback(() => {
    // Update URL params
    const params = new URLSearchParams();
    
    if (searchText) params.set('q', searchText);
    if (hybridWeight !== 0.5) params.set('hybrid_weight', hybridWeight.toString());
    if (viewMode !== 'list') params.set('view', viewMode);
    if (sortField !== 'relevance') params.set('sort_by', sortField);
    if (sortDirection !== 'desc') params.set('sort_dir', sortDirection);
    if (page !== 1) params.set('page', page.toString());
    
    filters.classification_code?.forEach(code => params.append('classification_code', code));
    filters.type?.forEach(type => params.append('type', type));
    filters.language?.forEach(lang => params.append('language', lang));
    filters.read_status?.forEach(status => params.append('read_status', status));
    filters.subject_any?.forEach(subject => params.append('subject_any', subject));
    if (filters.min_quality) params.set('min_quality', filters.min_quality.toString());
    
    setSearchParams(params);
  }, [searchText, hybridWeight, viewMode, sortField, sortDirection, page, filters, setSearchParams]);

  // Handle search submission
  const handleSearch = useCallback((e?: React.FormEvent) => {
    e?.preventDefault();
    setPage(1); // Reset to first page on new search
    performSearch();
  }, [performSearch]);

  // Handle filter changes
  const handleFiltersChange = useCallback((newFilters: SearchFilters) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page on filter change
  }, []);

  // Handle hybrid weight change with debounce
  const handleHybridWeightChange = useCallback((weight: number) => {
    setHybridWeight(weight);
    setPage(1); // Reset to first page on weight change
  }, []);

  // Handle sorting
  const handleSort = useCallback((field: SortField) => {
    if (field === sortField) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection(field === 'relevance' ? 'desc' : 'desc');
    }
    setPage(1); // Reset to first page on sort change
  }, [sortField]);

  // Handle pagination
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Clear search
  const handleClearSearch = useCallback(() => {
    setSearchText('');
    setFilters({});
    setHybridWeight(0.5);
    setSortField('relevance');
    setSortDirection('desc');
    setPage(1);
    setSearchParams(new URLSearchParams());
  }, [setSearchParams]);

  // Update URL when params change
  useEffect(() => {
    if (searchText || Object.keys(filters).length > 0) {
      performSearch();
    }
  }, [searchText, hybridWeight, filters, sortField, sortDirection, page]);

  const results = data?.items || [];
  const totalResults = data?.total || 0;
  const totalPages = Math.ceil(totalResults / itemsPerPage);
  const hasActiveSearch = searchText || Object.keys(filters).length > 0;

  return (
    <div className="min-h-screen bg-charcoal-grey-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-3xl font-bold text-charcoal-grey-50 mb-2">Advanced Search</h1>
          <p className="text-charcoal-grey-400">
            Search your knowledge library with hybrid keyword and semantic search
          </p>
        </motion.div>

        {/* Search Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card variant="glass" className="mb-6">
            <CardContent className="p-6">
              <form onSubmit={handleSearch}>
                {/* Main Search Input */}
                <div className="flex gap-3 mb-4">
                  <div className="flex-1">
                    <Input
                      placeholder="Search for resources..."
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                      leftIcon={<Search className="w-4 h-4" />}
                      className="w-full text-base"
                      rightIcon={
                        searchText ? (
                          <button
                            type="button"
                            onClick={() => setSearchText('')}
                            className="hover:text-charcoal-grey-300"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        ) : undefined
                      }
                    />
                  </div>
                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    icon={<Search className="w-4 h-4" />}
                    loading={isLoading || isDebouncing}
                  >
                    Search
                  </Button>
                </div>

                {/* Advanced Options Toggle */}
                <div className="flex items-center justify-between">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    icon={<SlidersHorizontal className="w-4 h-4" />}
                  >
                    {showAdvanced ? 'Hide' : 'Show'} Advanced Options
                  </Button>

                  {hasActiveSearch && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={handleClearSearch}
                      className="text-accent-blue-400 hover:text-accent-blue-300"
                    >
                      Clear All
                    </Button>
                  )}
                </div>

                {/* Advanced Options Panel */}
                <AnimatePresence>
                  {showAdvanced && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="pt-6 mt-6 border-t border-charcoal-grey-700">
                        <HybridWeightSlider
                          value={hybridWeight}
                          onChange={handleHybridWeightChange}
                        />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        {/* Controls Bar */}
        {hasActiveSearch && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6"
          >
            <Card variant="glass">
              <CardContent className="p-4">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  {/* View Controls */}
                  <div className="flex items-center space-x-3">
                    <Button
                      variant={showFilters ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setShowFilters(!showFilters)}
                      icon={<Filter className="w-4 h-4" />}
                    >
                      {showFilters ? 'Hide' : 'Show'} Filters
                    </Button>
                    
                    <div className="flex items-center bg-charcoal-grey-800 rounded-lg p-1">
                      <Button
                        variant={viewMode === 'grid' ? 'primary' : 'ghost'}
                        size="sm"
                        onClick={() => setViewMode('grid')}
                        icon={<Grid3x3 className="w-4 h-4" />}
                        className="rounded-r-none"
                      />
                      <Button
                        variant={viewMode === 'list' ? 'primary' : 'ghost'}
                        size="sm"
                        onClick={() => setViewMode('list')}
                        icon={<ListIcon className="w-4 h-4" />}
                        className="rounded-l-none"
                      />
                    </div>
                  </div>

                  {/* Sort Controls */}
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-charcoal-grey-400 whitespace-nowrap">Sort by:</span>
                    <div className="flex flex-wrap gap-1">
                      {[
                        { field: 'relevance' as SortField, label: 'Relevance' },
                        { field: 'updated_at' as SortField, label: 'Updated' },
                        { field: 'created_at' as SortField, label: 'Created' },
                        { field: 'quality_score' as SortField, label: 'Quality' },
                        { field: 'title' as SortField, label: 'Title' },
                      ].map(({ field, label }) => (
                        <Button
                          key={field}
                          variant={sortField === field ? 'primary' : 'ghost'}
                          size="sm"
                          onClick={() => handleSort(field)}
                          icon={
                            sortField === field ? (
                              sortDirection === 'asc' ? (
                                <SortAsc className="w-3 h-3" />
                              ) : (
                                <SortDesc className="w-3 h-3" />
                              )
                            ) : undefined
                          }
                        >
                          {label}
                        </Button>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Main Content Area */}
        {hasActiveSearch ? (
          <div className="flex gap-6">
            {/* Facet Panel */}
            <AnimatePresence>
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, x: -20, width: 0 }}
                  animate={{ opacity: 1, x: 0, width: 320 }}
                  exit={{ opacity: 0, x: -20, width: 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex-shrink-0"
                >
                  <FacetPanel
                    facets={data?.facets}
                    filters={filters}
                    onFiltersChange={handleFiltersChange}
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Search Results */}
            <div className="flex-1 min-w-0">
              <SearchResults
                results={results}
                total={totalResults}
                isLoading={isLoading || isDebouncing}
                viewMode={viewMode}
                snippets={data?.snippets}
              />

              {/* Pagination Controls */}
              {totalPages > 1 && !isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-8 flex items-center justify-between"
                >
                  <div className="text-sm text-charcoal-grey-400">
                    Showing {(page - 1) * itemsPerPage + 1} to {Math.min(page * itemsPerPage, totalResults)} of {formatNumber(totalResults)} results
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(page - 1)}
                      disabled={page === 1}
                      icon={<ChevronLeft className="w-4 h-4" />}
                    >
                      Previous
                    </Button>
                    
                    <div className="flex items-center space-x-1">
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        let pageNum;
                        if (totalPages <= 5) {
                          pageNum = i + 1;
                        } else if (page <= 3) {
                          pageNum = i + 1;
                        } else if (page >= totalPages - 2) {
                          pageNum = totalPages - 4 + i;
                        } else {
                          pageNum = page - 2 + i;
                        }
                        
                        return (
                          <Button
                            key={pageNum}
                            variant={page === pageNum ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => handlePageChange(pageNum)}
                          >
                            {pageNum}
                          </Button>
                        );
                      })}
                    </div>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(page + 1)}
                      disabled={page === totalPages}
                      icon={<ChevronRight className="w-4 h-4" />}
                    >
                      Next
                    </Button>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        ) : (
          <EmptySearchState />
        )}
      </div>
    </div>
  );
};

// Empty state component
const EmptySearchState: React.FC = () => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3 }}
  >
    <Card variant="glass">
      <CardContent className="text-center py-16">
        <Search className="w-20 h-20 mx-auto mb-4 text-accent-blue-500" />
        <h3 className="text-2xl font-medium text-charcoal-grey-50 mb-2">
          Start Your Search
        </h3>
        <p className="text-charcoal-grey-400 max-w-md mx-auto mb-6">
          Enter keywords or phrases to search your knowledge library. Use the hybrid weight slider to balance between exact keyword matching and semantic understanding.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center text-sm text-charcoal-grey-500">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-neutral-blue-500 rounded-full" />
            <span>Keyword search for exact matches</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-accent-blue-500 rounded-full" />
            <span>Semantic search for meaning</span>
          </div>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

export { SearchPage };
