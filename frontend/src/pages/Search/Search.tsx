import React, { useState } from 'react';
import { SearchBar } from '@/components/search/SearchBar';
import { SearchResults } from '@/components/search/SearchResults';
import { useSearch } from '@/hooks/useSearch';
import { SearchQuery, QuickFilter, SortOption } from '@/types/search';

const defaultQuery: SearchQuery = {
  text: '',
  filters: [],
  weights: {
    keyword: 0.4,
    semantic: 0.4,
    sparse: 0.2,
  },
  method: 'hybrid',
};

const quickFilters: QuickFilter[] = [
  {
    id: 'this-week',
    label: 'This Week',
    filter: { field: 'date', operator: '>=', value: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) },
  },
  {
    id: 'high-quality',
    label: 'High Quality',
    filter: { field: 'quality', operator: '>=', value: 80 },
  },
];

export const Search: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [query, setQuery] = useState<SearchQuery>(defaultQuery);
  const [sortBy, setSortBy] = useState<SortOption>('relevance');

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useSearch(query);

  const results = data?.pages.flatMap((page) => page.items) ?? [];

  const handleSearch = (text: string) => {
    setQuery({ ...query, text });
  };

  const handleQuickFilter = (filter: QuickFilter) => {
    setQuery({
      ...query,
      filters: [...query.filters, filter.filter],
    });
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Search
        </h1>

        <SearchBar
          value={searchText}
          onChange={setSearchText}
          onSubmit={handleSearch}
          quickFilters={quickFilters}
          onQuickFilterClick={handleQuickFilter}
        />

        {query.text && (
          <div className="mt-8">
            <SearchResults
              results={results}
              query={query.text}
              onLoadMore={() => fetchNextPage()}
              hasMore={hasNextPage ?? false}
              isLoading={isLoading || isFetchingNextPage}
              sortBy={sortBy}
              onSortChange={setSortBy}
            />
          </div>
        )}
      </div>
    </div>
  );
};
