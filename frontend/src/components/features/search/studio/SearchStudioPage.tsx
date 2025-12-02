import React, { useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { QueryBuilder } from './QueryBuilder';
import { MethodControls } from './MethodControls';
import { SearchResultsList } from '../results/SearchResultsList';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/common/Icon';
import { icons } from '@/config/icons';
import { searchApi, type SearchRequest, type SearchResultItem, type SearchMethod, type SearchWeights, type BooleanClause } from '@/lib/api/search';
import { useLocalStorage } from '@/lib/hooks/useLocalStorage';
import { nanoid } from 'nanoid';

export const SearchStudioPage: React.FC = () => {
    const [searchParams, setSearchParams] = useSearchParams();

    // Search State
    const [query, setQuery] = useState(searchParams.get('q') || '');
    const [clauses, setClauses] = useState<BooleanClause[]>([]);
    const [method, setMethod] = useState<SearchMethod>('hybrid');
    const [weights, setWeights] = useState<SearchWeights>({ keyword: 30, semantic: 70 });

    // Results State
    const [results, setResults] = useState<SearchResultItem[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(0);

    // Selection State
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

    // Saved Searches
    const [savedSearches, setSavedSearches] = useLocalStorage<any[]>('saved-searches', []);

    const handleSearch = useCallback(async (isNewSearch = true) => {
        setIsLoading(true);
        try {
            const request: SearchRequest = {
                query,
                boolean_clauses: clauses.length > 0 ? clauses : undefined,
                method,
                weights: method === 'hybrid' ? weights : undefined,
                limit: 20,
                offset: isNewSearch ? 0 : (page + 1) * 20,
            };

            const response = await searchApi.search(request);

            if (isNewSearch) {
                setResults(response.items);
                setTotal(response.total);
                setPage(0);
            } else {
                setResults(prev => [...prev, ...response.items]);
                setPage(prev => prev + 1);
            }
        } catch (error) {
            console.error('Search failed:', error);
            // TODO: Toast
        } finally {
            setIsLoading(false);
        }
    }, [query, clauses, method, weights, page]);

    const handleSaveSearch = () => {
        const name = prompt('Enter a name for this search:');
        if (name) {
            const newSearch = {
                id: nanoid(),
                name,
                request: {
                    query,
                    boolean_clauses: clauses,
                    method,
                    weights,
                },
                createdAt: Date.now(),
            };
            setSavedSearches(prev => [newSearch, ...prev]);
        }
    };

    const loadSavedSearch = (saved: any) => {
        setQuery(saved.request.query);
        setClauses(saved.request.boolean_clauses || []);
        setMethod(saved.request.method || 'hybrid');
        if (saved.request.weights) setWeights(saved.request.weights);
    };

    const toggleSelection = (id: string) => {
        const newSet = new Set(selectedIds);
        if (newSet.has(id)) newSet.delete(id);
        else newSet.add(id);
        setSelectedIds(newSet);
    };

    const selectAll = () => {
        if (selectedIds.size === results.length) {
            setSelectedIds(new Set());
        } else {
            setSelectedIds(new Set(results.map(r => r.resource.id)));
        }
    };

    return (
        <div className="flex h-full bg-gray-50 dark:bg-gray-900">
            {/* Sidebar Controls */}
            <aside className="w-80 flex-shrink-0 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-y-auto p-4 space-y-6">
                <div className="flex items-center justify-between">
                    <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">Search Studio</h1>
                    <Button variant="ghost" size="sm" onClick={handleSaveSearch} title="Save Search">
                        <Icon icon={icons.save} size={18} />
                    </Button>
                </div>

                {/* Main Query */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Query</label>
                    <div className="relative">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch(true)}
                            className="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter search terms..."
                        />
                        <Icon icon={icons.search} size={16} className="absolute left-3 top-3 text-gray-400" />
                    </div>
                </div>

                {/* Method Controls */}
                <MethodControls
                    method={method}
                    onMethodChange={setMethod}
                    weights={weights}
                    onWeightsChange={setWeights}
                />

                {/* Query Builder */}
                <QueryBuilder
                    clauses={clauses}
                    onChange={setClauses}
                />

                <Button onClick={() => handleSearch(true)} className="w-full">
                    Run Search
                </Button>

                {/* Saved Searches List */}
                {savedSearches.length > 0 && (
                    <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                        <h3 className="text-sm font-medium text-gray-500 mb-3">Saved Searches</h3>
                        <div className="space-y-2">
                            {savedSearches.map((saved) => (
                                <div
                                    key={saved.id}
                                    className="flex items-center justify-between p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer group"
                                    onClick={() => loadSavedSearch(saved)}
                                >
                                    <span className="text-sm truncate">{saved.name}</span>
                                    <button
                                        className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setSavedSearches(prev => prev.filter(s => s.id !== saved.id));
                                        }}
                                    >
                                        <Icon icon={icons.close} size={14} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </aside>

            {/* Results Area */}
            <main className="flex-1 overflow-y-auto p-6">
                <SearchResultsList
                    results={results}
                    isLoading={isLoading}
                    hasMore={results.length < total}
                    onLoadMore={() => handleSearch(false)}
                    selectedIds={selectedIds}
                    onToggleSelection={toggleSelection}
                    onSelectAll={selectAll}
                    total={total}
                />
            </main>
        </div>
    );
};

export default SearchStudioPage;
