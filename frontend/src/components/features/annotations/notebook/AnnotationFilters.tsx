import React from 'react';
import type { AnnotationSearchFilters, AnnotationColor } from '../../../../types/annotations';
import './AnnotationFilters.css';

interface AnnotationFiltersProps {
    filters: AnnotationSearchFilters;
    onFiltersChange: (filters: AnnotationSearchFilters) => void;
    resultCount?: number;
}

const COLORS: AnnotationColor[] = ['yellow', 'green', 'blue', 'pink', 'orange'];

/**
 * AnnotationFilters - Filter bar for annotation notebook
 * 
 * Features:
 * - Resource selector
 * - Tag input
 * - Color filter (color swatches)
 * - Date range picker
 * - Clear all filters button
 * - Result count display
 */
export const AnnotationFilters: React.FC<AnnotationFiltersProps> = ({
    filters,
    onFiltersChange,
    resultCount,
}) => {
    const handleResourceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onFiltersChange({ ...filters, resourceId: e.target.value || undefined });
    };

    const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const tags = e.target.value
            .split(',')
            .map(t => t.trim())
            .filter(t => t.length > 0);
        onFiltersChange({ ...filters, tags: tags.length > 0 ? tags : undefined });
    };

    const handleColorToggle = (color: AnnotationColor) => {
        onFiltersChange({
            ...filters,
            color: filters.color === color ? undefined : color,
        });
    };

    const handleDateFromChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onFiltersChange({ ...filters, dateFrom: e.target.value || undefined });
    };

    const handleDateToChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onFiltersChange({ ...filters, dateTo: e.target.value || undefined });
    };

    const handleClearFilters = () => {
        onFiltersChange({});
    };

    const hasActiveFilters = Boolean(
        filters.resourceId ||
        filters.tags?.length ||
        filters.color ||
        filters.dateFrom ||
        filters.dateTo
    );

    return (
        <div className="annotation-filters">
            <div className="annotation-filters-row">
                <div className="annotation-filter-group">
                    <label className="annotation-filter-label" htmlFor="filter-resource">
                        Resource
                    </label>
                    <input
                        id="filter-resource"
                        type="text"
                        className="annotation-filter-input"
                        placeholder="Filter by resource ID..."
                        value={filters.resourceId || ''}
                        onChange={handleResourceChange}
                    />
                </div>

                <div className="annotation-filter-group">
                    <label className="annotation-filter-label" htmlFor="filter-tags">
                        Tags
                    </label>
                    <input
                        id="filter-tags"
                        type="text"
                        className="annotation-filter-input"
                        placeholder="Enter tags (comma-separated)..."
                        value={filters.tags?.join(', ') || ''}
                        onChange={handleTagsChange}
                    />
                </div>
            </div>

            <div className="annotation-filters-row">
                <div className="annotation-filter-group">
                    <label className="annotation-filter-label">Color</label>
                    <div className="annotation-color-filters">
                        {COLORS.map((color) => (
                            <button
                                key={color}
                                className={`annotation-color-filter color-${color} ${filters.color === color ? 'active' : ''
                                    }`}
                                onClick={() => handleColorToggle(color)}
                                aria-label={`Filter by ${color}`}
                                aria-pressed={filters.color === color}
                            />
                        ))}
                    </div>
                </div>

                <div className="annotation-filter-group">
                    <label className="annotation-filter-label" htmlFor="filter-date-from">
                        Date From
                    </label>
                    <input
                        id="filter-date-from"
                        type="date"
                        className="annotation-filter-input"
                        value={filters.dateFrom || ''}
                        onChange={handleDateFromChange}
                    />
                </div>

                <div className="annotation-filter-group">
                    <label className="annotation-filter-label" htmlFor="filter-date-to">
                        Date To
                    </label>
                    <input
                        id="filter-date-to"
                        type="date"
                        className="annotation-filter-input"
                        value={filters.dateTo || ''}
                        onChange={handleDateToChange}
                    />
                </div>
            </div>

            <div className="annotation-filters-actions">
                <button
                    className="annotation-filters-clear"
                    onClick={handleClearFilters}
                    disabled={!hasActiveFilters}
                >
                    Clear Filters
                </button>
                {resultCount !== undefined && (
                    <span className="annotation-filters-count">
                        {resultCount} {resultCount === 1 ? 'annotation' : 'annotations'}
                    </span>
                )}
            </div>
        </div>
    );
};
