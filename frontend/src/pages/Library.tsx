// Neo Alexandria 2.0 Frontend - Library Dashboard Page
// Main library view with resource listing, filtering, and management

import React, { useState, useMemo } from 'react';
import { useResources } from '@/hooks/useApi';
import { 
  useSelectedResources,
} from '@/store';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingSkeleton } from '@/components/ui/LoadingSpinner';
import { ResourceCard } from '@/components/resources/ResourceCard';
import { ResourceFilters } from '@/components/resources/ResourceFilters';
import { ResourceBulkActions } from '@/components/resources/ResourceBulkActions';
import { 
  Search, 
  Filter, 
  SortAsc, 
  SortDesc, 
  Grid, 
  List,
  Plus,
  BookOpen,
  Sparkles
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { formatNumber } from '@/utils/format';
import type { ResourceQueryParams } from '@/types/api';

type ViewMode = 'grid' | 'list';
type SortField = 'updated_at' | 'created_at' | 'quality_score' | 'title';
type SortDirection = 'asc' | 'desc';

const Library: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>('updated_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Store state
  const selectedResources = useSelectedResources();

  // Build query parameters
  const queryParams: ResourceQueryParams = useMemo(() => ({
    q: searchQuery || undefined,
    sort_by: sortField,
    sort_dir: sortDirection,
    limit: 25,
    offset: 0,
  }), [searchQuery, sortField, sortDirection]);

  // Fetch resources
  const { data, refetch, isRefetching, isLoading, error } = useResources(queryParams);

  // Use data directly from the API call instead of store
  const resources = data?.items || [];
  const totalResources = data?.total || 0;

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  // Handle sorting
  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Handle pagination
  const handleLoadMore = () => {
    // For now, we'll implement simple pagination by refetching with more data
    // In a real implementation, you'd want to append to existing results
    refetch();
  };

  const hasMoreResources = data ? resources.length < data.total : false;

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Library</h1>
          <p className="text-secondary-600 mt-1">
            {totalResources > 0 
              ? `${formatNumber(totalResources)} resource${totalResources === 1 ? '' : 's'} in your collection`
              : 'Start building your knowledge library'
            }
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            icon={<Filter className="w-4 h-4" />}
          >
            Filters
          </Button>
          
          <div className="flex items-center bg-secondary-100 rounded-lg p-1">
            <Button
              variant={viewMode === 'grid' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
              icon={<Grid className="w-4 h-4" />}
            />
            <Button
              variant={viewMode === 'list' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              icon={<List className="w-4 h-4" />}
            />
          </div>
        </div>
      </div>

      {/* Search and Sort */}
      <Card variant="glass">
        <CardContent className="p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <Input
                placeholder="Search your library..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
              />
            </div>

            {/* Sort Options */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-secondary-600 whitespace-nowrap">Sort by:</span>
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

      {/* Filters Panel */}
      {showFilters && (
        <Card variant="glass">
          <CardHeader>
            <h3 className="text-lg font-medium">Filters</h3>
          </CardHeader>
          <CardContent>
            <ResourceFilters />
          </CardContent>
        </Card>
      )}

      {/* Bulk Actions */}
      {selectedResources.length > 0 && (
        <ResourceBulkActions selectedCount={selectedResources.length} />
      )}

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
        <EmptyLibraryState onAddResource={() => window.location.href = '/add'} />
      ) : (
        <>
          {/* Resource Grid/List */}
          <div className={cn(
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          )}>
            {resources.map((resource) => (
              <ResourceCard
                key={resource.id}
                resource={resource}
                viewMode={viewMode}
                selected={selectedResources.includes(resource.id)}
              />
            ))}
          </div>

          {/* Load More */}
          {hasMoreResources && (
            <div className="text-center pt-6">
              <Button
                variant="glass"
                onClick={handleLoadMore}
                loading={isRefetching}
                disabled={isRefetching}
              >
                Load More Resources
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

// Empty state component
interface EmptyLibraryStateProps {
  onAddResource: () => void;
}

const EmptyLibraryState: React.FC<EmptyLibraryStateProps> = ({ onAddResource }) => (
  <Card>
    <CardContent className="text-center py-12">
      <div className="text-secondary-400 mb-4">
        <BookOpen className="w-16 h-16 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">
          Your library is empty
        </h3>
        <p className="text-secondary-600 max-w-sm mx-auto mb-6">
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
);

export { Library };
