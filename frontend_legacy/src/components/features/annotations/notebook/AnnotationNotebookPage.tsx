import React, { useState, useEffect, useMemo } from 'react';
import { Button } from '../../../ui/Button/Button';
import { AnnotationCard } from './AnnotationCard';
import { AnnotationFilters } from './AnnotationFilters';
import { AnnotationsExportModal } from './AnnotationsExportModal';
import { useAllAnnotations, useSearchAnnotations } from '../../../../lib/hooks/useAnnotations';
import type { AnnotationSearchFilters, AnnotationGrouping } from '../../../../types/annotations';
import './AnnotationNotebookPage.css';

/**
 * AnnotationNotebookPage - Global page to browse and manage all annotations
 * 
 * Features:
 * - Chronological feed of annotation cards
 * - Filtering by resource, tag, color, date
 * - Full-text search with debounce
 * - Grouping toggle (chronological/resource/tag)
 * - Export to Markdown/JSON
 */
export const AnnotationNotebookPage: React.FC = () => {
    const [filters, setFilters] = useState<AnnotationSearchFilters>({});
    const [searchQuery, setSearchQuery] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const [grouping, setGrouping] = useState<AnnotationGrouping>('chronological');
    const [showExportModal, setShowExportModal] = useState(false);

    // Debounce search query
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchQuery);
        }, 300);

        return () => clearTimeout(timer);
    }, [searchQuery]);

    // Fetch annotations
    const { data: annotationsData, isLoading } = useAllAnnotations(filters);
    const { data: searchData, isLoading: isSearching } = useSearchAnnotations(
        debouncedSearch,
        filters,
        debouncedSearch.length > 0
    );

    // Use search results if searching, otherwise use filtered results
    const annotations = useMemo(() => {
        if (debouncedSearch && searchData) {
            return searchData.results.map(r => r.annotation);
        }
        return annotationsData?.items || [];
    }, [debouncedSearch, searchData, annotationsData]);

    // Group annotations
    const groupedAnnotations = useMemo(() => {
        if (grouping === 'chronological') {
            return { 'All Annotations': annotations };
        }

        if (grouping === 'resource') {
            const groups: Record<string, typeof annotations> = {};
            annotations.forEach(ann => {
                const key = ann.resourceId;
                if (!groups[key]) groups[key] = [];
                groups[key].push(ann);
            });
            return groups;
        }

        if (grouping === 'tag') {
            const groups: Record<string, typeof annotations> = {};
            annotations.forEach(ann => {
                if (ann.tags.length === 0) {
                    if (!groups['Untagged']) groups['Untagged'] = [];
                    groups['Untagged'].push(ann);
                } else {
                    ann.tags.forEach(tag => {
                        if (!groups[tag.name]) groups[tag.name] = [];
                        groups[tag.name].push(ann);
                    });
                }
            });
            return groups;
        }

        return { 'All Annotations': annotations };
    }, [annotations, grouping]);

    const totalCount = annotations.length;
    const isLoadingState = isLoading || isSearching;

    return (
        <div className="annotation-notebook-page">
            <div className="annotation-notebook-container">
                {/* Header */}
                <div className="annotation-notebook-header">
                    <h1 className="annotation-notebook-title">Annotation Notebook</h1>
                    <div className="annotation-notebook-actions">
                        <Button onClick={() => setShowExportModal(true)}>
                            Export
                        </Button>
                    </div>
                </div>

                {/* Search */}
                <div className="annotation-notebook-search">
                    <div className="annotation-notebook-search-wrapper">
                        <svg
                            className="annotation-notebook-search-icon"
                            width="20"
                            height="20"
                            viewBox="0 0 20 20"
                            fill="none"
                        >
                            <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" />
                            <path d="M13 13l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                        </svg>
                        <input
                            type="text"
                            className="annotation-notebook-search-input"
                            placeholder="Search annotations..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                </div>

                {/* Filters */}
                <AnnotationFilters
                    filters={filters}
                    onFiltersChange={setFilters}
                    resultCount={totalCount}
                />

                {/* Controls */}
                <div className="annotation-notebook-controls">
                    <div className="annotation-notebook-grouping">
                        <button
                            className={`annotation-notebook-grouping-option ${grouping === 'chronological' ? 'active' : ''
                                }`}
                            onClick={() => setGrouping('chronological')}
                        >
                            Chronological
                        </button>
                        <button
                            className={`annotation-notebook-grouping-option ${grouping === 'resource' ? 'active' : ''
                                }`}
                            onClick={() => setGrouping('resource')}
                        >
                            By Resource
                        </button>
                        <button
                            className={`annotation-notebook-grouping-option ${grouping === 'tag' ? 'active' : ''
                                }`}
                            onClick={() => setGrouping('tag')}
                        >
                            By Tag
                        </button>
                    </div>
                </div>

                {/* Feed */}
                <div className="annotation-notebook-feed">
                    {isLoadingState ? (
                        <div className="annotation-notebook-loading">
                            {[...Array(3)].map((_, i) => (
                                <div key={i} className="annotation-notebook-skeleton" />
                            ))}
                        </div>
                    ) : totalCount === 0 ? (
                        <div className="annotation-notebook-empty">
                            <svg
                                className="annotation-notebook-empty-icon"
                                viewBox="0 0 80 80"
                                fill="none"
                            >
                                <path
                                    d="M20 16h40a8 8 0 018 8v40a8 8 0 01-8 8H20a8 8 0 01-8-8V24a8 8 0 018-8z"
                                    stroke="currentColor"
                                    strokeWidth="3"
                                />
                                <path
                                    d="M28 32h24M28 44h24M28 56h16"
                                    stroke="currentColor"
                                    strokeWidth="3"
                                    strokeLinecap="round"
                                />
                            </svg>
                            <h2 className="annotation-notebook-empty-title">No annotations yet</h2>
                            <p className="annotation-notebook-empty-text">
                                {debouncedSearch || Object.keys(filters).length > 0
                                    ? 'Try adjusting your filters or search query'
                                    : 'Start annotating resources to build your knowledge base'}
                            </p>
                        </div>
                    ) : (
                        Object.entries(groupedAnnotations).map(([groupName, groupAnnotations]) => (
                            <div key={groupName} className="annotation-notebook-group">
                                {grouping !== 'chronological' && (
                                    <h2 className="annotation-notebook-group-header">{groupName}</h2>
                                )}
                                {groupAnnotations.map((annotation) => (
                                    <AnnotationCard
                                        key={annotation.id}
                                        annotation={annotation}
                                        resourceTitle={`Resource ${annotation.resourceId.substring(0, 8)}...`}
                                    />
                                ))}
                            </div>
                        ))
                    )}
                </div>

                {/* Export Modal */}
                {showExportModal && (
                    <AnnotationsExportModal
                        filters={filters}
                        onClose={() => setShowExportModal(false)}
                    />
                )}
            </div>
        </div>
    );
};
