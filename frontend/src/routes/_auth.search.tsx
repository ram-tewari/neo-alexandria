/**
 * Search Route
 * Main search interface with filters, results, and recommendations
 */

import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useEffect } from 'react';
import { Search as SearchIcon } from 'lucide-react';
import { z } from 'zod';
import { useSearch } from '@/features/search/hooks/useSearch';
import { SearchInput } from '@/features/search/components/SearchInput';
import { FilterPanel } from '@/features/search/components/FilterPanel';
import { SearchResultItem } from '@/features/search/components/SearchResultItem';
import { RecommendationsWidget } from '@/features/recommendations/components/RecommendationsWidget';
import { Card } from '@/components/ui/card';

const searchSchema = z.object({
  q: z.string().optional(),
  quality: z.string().optional(),
  method: z.enum(['hybrid', 'semantic']).optional(),
});

export const Route = createFileRoute('/_auth/search')({
  component: SearchPage,
  validateSearch: searchSchema,
});

function SearchPage() {
  const navigate = useNavigate();
  const searchParams = Route.useSearch();
  const {
    query,
    filters,
    method,
    results,
    isLoading,
    error,
    setQuery,
    setFilter,
    setMethod,
    clearFilters,
  } = useSearch();

  // Initialize from URL params
  useEffect(() => {
    if (searchParams.q) {
      setQuery(searchParams.q);
    }
    if (searchParams.quality) {
      const quality = parseFloat(searchParams.quality);
      if (!isNaN(quality) && quality >= 0 && quality <= 1) {
        setFilter('min_quality', quality);
      }
    }
    if (searchParams.method) {
      setMethod(searchParams.method);
    }
  }, []);

  // Update URL when search state changes
  useEffect(() => {
    const params: { q?: string; quality?: string; method?: 'hybrid' | 'semantic' } = {};
    if (query) params.q = query;
    if (filters.min_quality && filters.min_quality > 0) {
      params.quality = filters.min_quality.toString();
    }
    if (method === 'semantic') params.method = method;

    navigate({
      to: '/search',
      search: params,
      replace: true,
    }).catch(() => {
      // Ignore navigation errors
    });
  }, [query, filters.min_quality, method, navigate]);

  const handleClearSearch = () => {
    setQuery('');
    clearFilters();
  };

  const handleResultClick = (id: number) => {
    navigate({ to: '/resources', search: { id: id.toString() } });
  };

  const handleRecommendationClick = (id: string) => {
    navigate({ to: '/resources', search: { id } });
  };

  return (
    <div className="flex h-full">
      {/* Desktop Sidebar - Filters */}
      <aside className="hidden md:block w-72 border-r bg-background overflow-y-auto">
        <div className="sticky top-0">
          <FilterPanel
            filters={filters}
            method={method}
            onFilterChange={setFilter}
            onMethodChange={setMethod}
          />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-6 space-y-6">
          {/* Search Input */}
          <div className="sticky top-0 z-10 bg-background pb-4 border-b">
            <SearchInput
              value={query}
              onChange={setQuery}
              onClear={handleClearSearch}
              isLoading={isLoading}
            />
          </div>

          {/* Error State */}
          {error && (
            <Card className="p-6 border-destructive">
              <div className="flex items-center gap-2 text-destructive">
                <SearchIcon className="h-5 w-5" />
                <p className="font-semibold">Search Error</p>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {error.message}
              </p>
            </Card>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Card key={i} className="p-4 space-y-3 animate-pulse">
                  <div className="h-6 bg-secondary rounded w-3/4" />
                  <div className="space-y-2">
                    <div className="h-4 bg-secondary rounded" />
                    <div className="h-4 bg-secondary rounded w-5/6" />
                  </div>
                  <div className="flex gap-2">
                    <div className="h-5 bg-secondary rounded w-20" />
                    <div className="h-5 bg-secondary rounded w-24" />
                    <div className="h-5 bg-secondary rounded w-16" />
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Results */}
          {!isLoading && query && results && results.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Found {results.length} result{results.length !== 1 ? 's' : ''}
                </p>
                {(filters.min_quality && filters.min_quality > 0) || method !== 'hybrid' ? (
                  <button
                    onClick={clearFilters}
                    className="text-sm text-primary hover:underline"
                  >
                    Clear filters
                  </button>
                ) : null}
              </div>
              {results.map((result) => (
                <SearchResultItem
                  key={result.id}
                  result={result}
                  onClick={handleResultClick}
                />
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && query && results && results.length === 0 && (
            <Card className="p-12 text-center">
              <SearchIcon className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="text-lg font-semibold mb-2">No results found</h3>
              <p className="text-sm text-muted-foreground mb-4">
                No results found for "{query}"
              </p>
              {(filters.min_quality && filters.min_quality > 0) || method !== 'hybrid' ? (
                <button
                  onClick={clearFilters}
                  className="text-sm text-primary hover:underline"
                >
                  Try clearing filters
                </button>
              ) : (
                <p className="text-xs text-muted-foreground">
                  Try different keywords or adjust your filters
                </p>
              )}
            </Card>
          )}

          {/* Recommendations (when no query) */}
          {!query && !isLoading && (
            <RecommendationsWidget onRecommendationClick={handleRecommendationClick} />
          )}
        </div>
      </main>
    </div>
  );
}
