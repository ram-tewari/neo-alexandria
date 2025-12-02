import React, { useRef, useEffect } from 'react';
import { SearchResultCard } from './SearchResultCard';
import type { SearchResultItem } from '@/lib/api/search';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/common/Icon';
import { icons } from '@/config/icons';

interface SearchResultsListProps {
    results: SearchResultItem[];
    isLoading: boolean;
    hasMore: boolean;
    onLoadMore: () => void;
    selectedIds: Set<string>;
    onToggleSelection: (id: string) => void;
    onSelectAll: () => void;
    total: number;
    onSortChange?: (sort: string) => void; // New prop
}

export const SearchResultsList: React.FC<SearchResultsListProps> = ({
    results,
    isLoading,
    hasMore,
    onLoadMore,
    selectedIds,
    onToggleSelection,
    onSelectAll,
    total,
    onSortChange,
}) => {
    const observerTarget = useRef<HTMLDivElement>(null);

    // Infinite Scroll Observer
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && hasMore && !isLoading) {
                    onLoadMore();
                }
            },
            { threshold: 0.5 }
        );

        if (observerTarget.current) {
            observer.observe(observerTarget.current);
        }

        return () => observer.disconnect();
    }, [hasMore, isLoading, onLoadMore]);

    if (results.length === 0 && !isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                <Icon icon={icons.search} size={48} className="mb-4 opacity-20" />
                <p className="text-lg font-medium">No results found</p>
                <p className="text-sm">Try adjusting your query or filters</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Toolbar */}
            <div className="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-700">
                <div className="text-sm text-gray-500">
                    Found {total} results
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" onClick={onSelectAll}>
                        Select All
                    </Button>

                    {/* Sort Controls */}
                    <select
                        className="text-sm border-gray-200 dark:border-gray-700 rounded-md bg-transparent"
                        onChange={(e) => onSortChange?.(e.target.value)}
                    >
                        <option value="relevance">Relevance</option>
                        <option value="date_desc">Newest</option>
                        <option value="date_asc">Oldest</option>
                        <option value="quality">Quality</option>
                    </select>
                </div>
            </div>

            {/* List */}
            <div className="space-y-4">
                {results.map((item) => (
                    <SearchResultCard
                        key={item.resource.id}
                        item={item}
                        selected={selectedIds.has(item.resource.id)}
                        onSelect={() => onToggleSelection(item.resource.id)}
                    />
                ))}
            </div>

            {/* Loading State & Sentinel */}
            <div ref={observerTarget} className="py-8 flex justify-center">
                {isLoading && (
                    <div className="flex items-center gap-2 text-gray-500">
                        <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                        <span>Loading more...</span>
                    </div>
                )}
            </div>
        </div>
    );
};
