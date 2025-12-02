/**
 * FilterSidebar component for faceted filtering
 * 
 * Provides a sidebar with multiple filter sections including:
 * - Classification filter
 * - Quality range filter
 * - Resource type filter
 * - Language filter
 * - Read status filter
 * 
 * Features:
 * - Displays result counts for each facet option
 * - Optimistic UI updates
 * - Clear all filters button
 */

import React, { useEffect, useRef } from 'react';
import { Button } from '../../ui/Button/Button';
import { useResourceFilters, type ResourceFilters } from '../../../lib/hooks/useResourceFilters';
import type { ReadStatus } from '../../../lib/api/types';
import { announceFilterChange } from '../../../lib/utils/announceToScreenReader';

interface FilterSidebarProps {
  /** Current filter state */
  filters: ResourceFilters;
  /** Callback when filters change */
  onChange: (filters: ResourceFilters) => void;
  /** Optional facet counts for each filter option */
  facets?: FilterFacets;
  /** Additional CSS classes */
  className?: string;
}

export interface FilterFacets {
  classifications?: FilterFacet[];
  types?: FilterFacet[];
  languages?: FilterFacet[];
  readStatuses?: FilterFacet[];
}

export interface FilterFacet {
  label: string;
  value: string;
  count: number;
}

/**
 * Main filter sidebar component
 */
export const FilterSidebar: React.FC<FilterSidebarProps> = ({
  filters,
  onChange,
  facets,
  className = '',
}) => {
  const previousFiltersRef = useRef<ResourceFilters>(filters);

  // Announce filter changes to screen readers
  useEffect(() => {
    const prevFilters = previousFiltersRef.current;
    const changedKeys = Object.keys(filters).filter(
      key => filters[key as keyof ResourceFilters] !== prevFilters[key as keyof ResourceFilters]
    );

    if (changedKeys.length > 0) {
      changedKeys.forEach(key => {
        const value = filters[key as keyof ResourceFilters];
        if (value !== undefined) {
          const filterName = key.replace(/_/g, ' ');
          announceFilterChange(filterName, String(value));
        }
      });
    }

    previousFiltersRef.current = filters;
  }, [filters]);

  const handleFilterChange = (key: keyof ResourceFilters, value: any) => {
    // Toggle behavior: if same value is clicked, clear it
    const newValue = filters[key] === value ? undefined : value;
    onChange({ ...filters, [key]: newValue });
  };

  const handleQualityChange = (min?: number, max?: number) => {
    onChange({
      ...filters,
      min_quality: min,
      max_quality: max,
    });
  };

  const handleClearAll = () => {
    onChange({});
  };

  const hasActiveFilters = Object.keys(filters).length > 0;

  return (
    <aside
      className={`w-64 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-auto ${className}`}
      role="complementary"
      aria-label="Resource filters"
    >
      {/* Screen reader announcement region */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true" />
      
      <div className="p-4 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Filters
          </h2>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearAll}
              aria-label="Clear all filters"
            >
              Clear All
            </Button>
          )}
        </div>

        {/* Classification Filter */}
        {facets?.classifications && facets.classifications.length > 0 && (
          <FilterSection title="Classification">
            {facets.classifications.map((facet) => (
              <FilterOption
                key={facet.value}
                label={facet.label}
                count={facet.count}
                checked={filters.classification_code === facet.value}
                onChange={() => handleFilterChange('classification_code', facet.value)}
              />
            ))}
          </FilterSection>
        )}

        {/* Quality Range Filter */}
        <FilterSection title="Quality Score">
          <QualityRangeFilter
            minQuality={filters.min_quality}
            maxQuality={filters.max_quality}
            onChange={handleQualityChange}
          />
        </FilterSection>

        {/* Resource Type Filter */}
        {facets?.types && facets.types.length > 0 && (
          <FilterSection title="Type">
            {facets.types.map((facet) => (
              <FilterOption
                key={facet.value}
                label={facet.label}
                count={facet.count}
                checked={filters.type === facet.value}
                onChange={() => handleFilterChange('type', facet.value)}
              />
            ))}
          </FilterSection>
        )}

        {/* Language Filter */}
        {facets?.languages && facets.languages.length > 0 && (
          <FilterSection title="Language">
            {facets.languages.map((facet) => (
              <FilterOption
                key={facet.value}
                label={facet.label}
                count={facet.count}
                checked={filters.language === facet.value}
                onChange={() => handleFilterChange('language', facet.value)}
              />
            ))}
          </FilterSection>
        )}

        {/* Read Status Filter */}
        <FilterSection title="Read Status">
          {READ_STATUS_OPTIONS.map((option) => (
            <FilterOption
              key={option.value}
              label={option.label}
              checked={filters.read_status === option.value}
              onChange={() => handleFilterChange('read_status', option.value)}
            />
          ))}
        </FilterSection>
      </div>
    </aside>
  );
};

/**
 * Filter section component for grouping related filters
 */
interface FilterSectionProps {
  title: string;
  children: React.ReactNode;
}

export const FilterSection: React.FC<FilterSectionProps> = ({ title, children }) => {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {title}
      </h3>
      <div className="space-y-1">
        {children}
      </div>
    </div>
  );
};

/**
 * Individual filter option with checkbox
 */
interface FilterOptionProps {
  label: string;
  count?: number;
  checked: boolean;
  onChange: () => void;
}

export const FilterOption: React.FC<FilterOptionProps> = ({
  label,
  count,
  checked,
  onChange,
}) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Allow Enter or Space to toggle checkbox
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onChange();
    }
  };

  return (
    <label 
      className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition-colors"
      onKeyDown={handleKeyDown}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-0 dark:border-gray-600 dark:bg-gray-700"
        aria-label={count !== undefined ? `${label} (${count} results)` : label}
      />
      <span className="flex-1 text-sm text-gray-700 dark:text-gray-300">
        {label}
      </span>
      {count !== undefined && (
        <span className="text-xs text-gray-500 dark:text-gray-400" aria-hidden="true">
          ({count})
        </span>
      )}
    </label>
  );
};

/**
 * Quality range filter with min/max sliders
 */
interface QualityRangeFilterProps {
  minQuality?: number;
  maxQuality?: number;
  onChange: (min?: number, max?: number) => void;
}

export const QualityRangeFilter: React.FC<QualityRangeFilterProps> = ({
  minQuality = 0,
  maxQuality = 1,
  onChange,
}) => {
  const handleMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    onChange(value, maxQuality);
  };

  const handleMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    onChange(minQuality, value);
  };

  const handleReset = () => {
    onChange(undefined, undefined);
  };

  const isFiltered = minQuality > 0 || maxQuality < 1;

  return (
    <div className="space-y-3">
      {/* Min Quality Slider */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
          <span>Minimum</span>
          <span className="font-medium">{Math.round(minQuality * 100)}%</span>
        </div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={minQuality}
          onChange={handleMinChange}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 accent-blue-600"
          aria-label="Minimum quality score"
        />
      </div>

      {/* Max Quality Slider */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
          <span>Maximum</span>
          <span className="font-medium">{Math.round(maxQuality * 100)}%</span>
        </div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={maxQuality}
          onChange={handleMaxChange}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 accent-blue-600"
          aria-label="Maximum quality score"
        />
      </div>

      {/* Reset Button */}
      {isFiltered && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleReset}
          className="w-full text-xs"
        >
          Reset Range
        </Button>
      )}
    </div>
  );
};

/**
 * Read status options
 */
const READ_STATUS_OPTIONS: Array<{ label: string; value: ReadStatus }> = [
  { label: 'Unread', value: 'unread' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Archived', value: 'archived' },
];
