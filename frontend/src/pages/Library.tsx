// Neo Alexandria 2.0 Frontend - Library Dashboard Page
// Main library view with resource listing, filtering, and management

import React, { useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSearchParams } from 'react-router-dom';
import { useResources } from '@/hooks/useApi';
import { useAppStore } from '@/store';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { ResourceCard } from '@/components/resources/ResourceCard';
import { FacetedSearchSidebar } from '@/components/library/FacetedSearchSidebar';
import { ResourceGrid } from '@/components/library/ResourceGrid';
import { ResourceList } from '@/components/library/ResourceList';
import { BulkActionBar } from '@/components/library/BulkActionBar';
import { UploadResourceModal } from '@/components/library/UploadResourceModal';
import { 
  Search, 
  Filter, 
  SortAsc, 
  SortDesc, 
  Grid3x3,
  List as ListIcon,
  Plus,
  BookOpen,
  Sparkles,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { formatNumber } from '@/utils/format';
import type { ResourceQueryParams, SearchFilters } from '@/types/api';

type ViewMode = 'grid' | 'list';
type SortField = 'updated_at' | 'created_at' | 'quality_score' | 'title';
type SortDirection = 'asc' | 'desc';

const Library: React.FC = () => {
  // URL search params for shareable filters
  const [searchParams, setSearchParams] = useSearchParams();
  
  // View state
  const [viewMode, setViewMode] = useState<ViewMode>(
    (searchParams.get('view') as ViewMode) || 'grid'
  );
  const [showFilters, setShowFilters] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [filters, setFilters] = useState<SearchFilters>({
    classification_code: searchParams.getAll('classification_code'),
    type: searchParams.getAll('type'),
    language: searchParams.getAll('language'),
    read_status: searchParams.getAll('read_status') as any[],
    min_quality: searchParams.get('min_quality') ? Number(searchParams.get('min_quality')) : undefined,
  });
  
  // Sorting state
  const [sortField, setSortField] = useState<SortField>(
    (searchParams.get('sort_by') as SortField) || 'updated_at'
  );
  const [sortDirection, setSortDirection] = useState<SortDirection>(
    (searchParams.get('sort_dir') as SortDirection) || 'desc'
  );
  
  // Pagination state
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);
  const itemsPerPage = 24;

  // Store state
  const selectedResources = useAppStore(state => state.selectedResources);
  const clearSelection = useAppStore(state => state.clearSelection);

  // Build query parameters
  const queryParams: ResourceQueryParams = useMemo(() => ({
    q: searchQuery || undefined,
    sort_by: sortField,
    sort_dir: sortDirection,
    limit: itemsPerPage,
    offset: (page - 1) * itemsPerPage,
    ...filters,
  }), [searchQuery, sortField, sortDirection, page, filters]);

  // Fetch resources
  const { data, refetch, isRefetching, isLoading, error } = useResources(queryParams);

  // Use data directly from the API call
  const resources = data?.items || [];
  const totalResources = data?.total || 0;
  const totalPages = Math.ceil(totalResources / itemsPerPage);

  // Update URL params when filters change
  const updateUrlParams = useCallback(() => {
    const params = new URLSearchParams();
    
    if (searchQuery) params.set('q', searchQuery);
    if (viewMode !== 'grid') params.set('view', viewMode);
    if (sortField !== 'updated_at') params.set('sort_by', sortField);
    if (sortDirection !== 'desc') params.set('sort_dir', sortDirection);
    if (page !== 1) params.set('page', page.toString());
    
    filters.classification_code?.forEach(code => params.append('classification_code', code));
    filters.type?.forEach(type => params.append('type', type));
    filters.language?.forEach(lang => params.append('language', lang));
    filters.read_status?.forEach(status => params.append('read_status', status));
    if (filters.min_quality) params.set('min_quality', filters.min_quality.toString());
    
    setSearchParams(params);
  }, [searchQuery, viewMode, sortField, sortDirection, page, filters, setSearchParams]);

  // Handle search
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    setPage(1); // Reset to first page on new search
  }, []);

  // Handle sorting
  const handleSort = useCallback((field: SortField) => {
    if (field === sortField) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
    setPage(1); // Reset to first page on sort change
  }, [sortField]);

  // Handle view mode change
  const handleViewModeChange = useCallback((mode: ViewMode) => {
    setViewMode(mode);
  }, []);

  // Handle filter changes
  const handleFiltersChange = useCallback((newFilters: SearchFilters) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page on filter change
  }, []);

  // Handle pagination
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Update URL when params change
  React.useEffect(() => {
    updateUrlParams();
  }, [updateUrlParams]);

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <BookOpen className="w-12 h-12 mx-auto mb-2" />
          <h3 className="text-lg font-medium">Error Loading Library</h3>
          <p className="text-sm text-secondary-600 mt-1">{error?.message || 'An error occurred'}</p>
        </div>
        <Button onClick={() => refetch()}>Try Again</Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-charcoal-grey-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6"
        >
          <div>
            <h1 className="text-3xl font-bold text-charcoal-grey-50">Library</h1>
            <p className="text-charcoal-grey-400 mt-1">
              {totalResources > 0 
                ? `${formatNumber(totalResources)} resource${totalResources === 1 ? '' : 's'} in your collection`
                : 'Start building your knowledge library'
              }
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button
              variant="primary"
              size="md"
              onClick={() => setShowUploadModal(true)}
              icon={<Plus className="w-4 h-4" />}
            >
              Add Resource
            </Button>
            
            <Button
              variant={showFilters ? 'primary' : 'outline'}
              size="md"
              onClick={() => setShowFilters(!showFilters)}
              icon={<Filter className="w-4 h-4" />}
            >
              {showFilters ? 'Hide' : 'Show'} Filters
            </Button>
            
            <div className="flex items-center bg-charcoal-grey-800 rounded-lg p-1">
              <Button
                variant={viewMode === 'grid' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => handleViewModeChange('grid')}
                icon={<Grid3x3 className="w-4 h-4" />}
                className="rounded-r-none"
              />
              <Button
                variant={viewMode === 'list' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => handleViewModeChange('list')}
                icon={<ListIcon className="w-4 h-4" />}
                className="rounded-l-none"
              />
            </div>
          </div>
        </motion.div>

        {/* Search and Sort Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card variant="glass" className="mb-6">
            <CardContent className="p-4">
              <div className="flex flex-col lg:flex-row gap-4">
                {/* Search */}
                <div className="flex-1">
                  <Input
                    placeholder="Search your library..."
                    value={searchQuery}
                    onChange={(e) => handleSearch(e.target.value)}
                    leftIcon={<Search className="w-4 h-4" />}
                    className="w-full"
                  />
                </div>

                {/* Sort Options */}
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-charcoal-grey-400 whitespace-nowrap">Sort by:</span>
                  <div className="flex space-x-1">
                    {[
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

        {/* Main Content Area */}
        <div className="flex gap-6">
          {/* Filters Sidebar */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, x: -20, width: 0 }}
                animate={{ opacity: 1, x: 0, width: 320 }}
                exit={{ opacity: 0, x: -20, width: 0 }}
                transition={{ duration: 0.2 }}
                className="flex-shrink-0"
              >
                <FacetedSearchSidebar
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                  facets={data?.facets}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Resources Content */}
          <div className="flex-1 min-w-0">
            {/* Bulk Actions Bar */}
            <AnimatePresence>
              {selectedResources.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="mb-4"
                >
                  <BulkActionBar
                    selectedCount={selectedResources.length}
                    onClearSelection={clearSelection}
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Content */}
            {isLoading && resources.length === 0 ? (
              <div className="space-y-4">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} variant="glass">
                    <CardContent className="p-4">
                      <LoadingSkeleton lines={3} />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : resources.length === 0 ? (
              <EmptyLibraryState onAddResource={() => setShowUploadModal(true)} />
            ) : (
              <>
                {/* Resource Grid/List */}
                {viewMode === 'grid' ? (
                  <ResourceGrid
                    resources={resources}
                    selectedResources={selectedResources}
                    isLoading={isRefetching}
                  />
                ) : (
                  <ResourceList
                    resources={resources}
                    selectedResources={selectedResources}
                    isLoading={isRefetching}
                  />
                )}

                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-8 flex items-center justify-between"
                  >
                    <div className="text-sm text-charcoal-grey-400">
                      Showing {(page - 1) * itemsPerPage + 1} to {Math.min(page * itemsPerPage, totalResources)} of {totalResources} resources
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
              </>
            )}
          </div>
        </div>
      </div>

      {/* Upload Resource Modal */}
      <UploadResourceModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
      />
    </div>
  );
};

// Empty state component
interface EmptyLibraryStateProps {
  onAddResource: () => void;
}

const EmptyLibraryState: React.FC<EmptyLibraryStateProps> = ({ onAddResource }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3 }}
  >
    <Card variant="glass">
      <CardContent className="text-center py-16">
        <div className="text-charcoal-grey-400 mb-4">
          <BookOpen className="w-20 h-20 mx-auto mb-4 text-accent-blue-500" />
          <h3 className="text-2xl font-medium text-charcoal-grey-50 mb-2">
            Your library is empty
          </h3>
          <p className="text-charcoal-grey-400 max-w-sm mx-auto mb-8">
            Start building your personal knowledge library by adding your first resource.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button 
            variant="primary" 
            onClick={onAddResource}
            icon={<Plus className="w-4 h-4" />}
          >
            Add Your First Resource
          </Button>
          <Button 
            variant="outline" 
            onClick={() => window.location.href = '/recommendations'}
            icon={<Sparkles className="w-4 h-4" />}
          >
            Get Recommendations
          </Button>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

export { Library };
