import React, { useState } from 'react';
import { Button } from '../../../ui/Button/Button';
import { SemanticResultCard } from './SemanticResultCard';
import { AnnotationClustersView } from './AnnotationClustersView';
import { useSemanticSearch } from '../../../../lib/hooks/useAnnotations';
import type { AnnotationSearchFilters } from '../../../../types/annotations';
import './SemanticAnnotationSearchPanel.css';

interface SemanticAnnotationSearchPanelProps {
    filters?: AnnotationSearchFilters;
}

/**
 * SemanticAnnotationSearchPanel - Semantic search interface for annotations
 * 
 * Features:
 * - Query input for free-text semantic search
 * - Optional filters (tag, resource)
 * - Results section with similarity scores
 * - Cluster visualization
 * - Fallback message if semantic endpoint unavailable
 */
export const SemanticAnnotationSearchPanel: React.FC<SemanticAnnotationSearchPanelProps> = ({
    filters,
}) => {
    const [query, setQuery] = useState('');
    const [activeQuery, setActiveQuery] = useState('');

    const { data, isLoading, error } = useSemanticSearch(
        activeQuery,
        filters,
        activeQuery.length > 0
    );

    const handleSearch = () => {
        setActiveQuery(query);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    // Show fallback if endpoint is unavailable
    if (error) {
        return (
            <div className="semantic-search-panel">
                <div className="semantic-search-fallback">
                    <svg className="semantic-search-fallback-icon" viewBox="0 0 48 48" fill="none">
                        <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2" />
                        <path d="M24 16v12M24 32v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                    <p className="semantic-search-fallback-text">
                        Semantic search is currently unavailable
                    </p>
                    <p className="semantic-search-fallback-hint">
                        Please use the full-text search above or try again later
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="semantic-search-panel">
            <div className="semantic-search-header">
                <svg className="semantic-search-icon" viewBox="0 0 24 24" fill="none">
                    <path
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                    <path
                        d="M10 7v6l4 2"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                </svg>
                <h2 className="semantic-search-title">Semantic Search</h2>
            </div>

            <div className="semantic-search-input-wrapper">
                <input
                    type="text"
                    className="semantic-search-input"
                    placeholder="Search by meaning and context..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <Button
                    className="semantic-search-button"
                    onClick={handleSearch}
                    disabled={isLoading || query.length === 0}
                >
                    {isLoading ? 'Searching...' : 'Search'}
                </Button>
            </div>

            {data && (
                <div className="semantic-search-results">
                    {/* Clusters */}
                    {data.clusters && data.clusters.length > 0 && (
                        <AnnotationClustersView clusters={data.clusters} />
                    )}

                    {/* Results */}
                    {data.results.map((result) => (
                        <SemanticResultCard key={result.annotation.id} result={result} />
                    ))}
                </div>
            )}
        </div>
    );
};
