/**
 * Filter Bar Component
 * 
 * Search input with filters for quality, date, type, and tags
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from './Icon';
import { icons } from '@/config/icons';
import type { ReadStatus } from '@/types/resource';
import './FilterBar.css';

interface FilterBarProps {
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
  filters?: {
    read_status?: ReadStatus;
    quality_min?: number;
    quality_max?: number;
    tags?: string[];
  };
  onFiltersChange?: (filters: any) => void;
  onClearFilters?: () => void;
}

export const FilterBar = ({
  searchQuery = '',
  onSearchChange,
  filters = {},
  onFiltersChange,
  onClearFilters,
}: FilterBarProps) => {
  const [showFilters, setShowFilters] = useState(false);
  const [localSearch, setLocalSearch] = useState(searchQuery);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLocalSearch(value);
    
    // Debounce search
    const timeoutId = setTimeout(() => {
      onSearchChange?.(value);
    }, 300);
    
    return () => clearTimeout(timeoutId);
  };

  const handleFilterChange = (key: string, value: any) => {
    onFiltersChange?.({ ...filters, [key]: value });
  };

  const activeFilterCount = Object.keys(filters).filter(
    key => filters[key as keyof typeof filters] !== undefined
  ).length;

  return (
    <div className="filter-bar">
      <div className="filter-bar__main">
        <div className="filter-bar__search">
          <Icon icon={icons.search} size={18} />
          <input
            type="text"
            placeholder="Search resources..."
            value={localSearch}
            onChange={handleSearchChange}
            className="filter-bar__input"
          />
          {localSearch && (
            <button
              onClick={() => {
                setLocalSearch('');
                onSearchChange?.('');
              }}
              className="filter-bar__clear-search"
            >
              <Icon icon={icons.close} size={16} />
            </button>
          )}
        </div>

        <div className="filter-bar__actions">
          <button
            className={`filter-bar__toggle ${showFilters ? 'active' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            <Icon icon={icons.filter} size={18} />
            <span>Filters</span>
            {activeFilterCount > 0 && (
              <span className="filter-bar__badge">{activeFilterCount}</span>
            )}
          </button>

          {activeFilterCount > 0 && (
            <button
              className="filter-bar__clear"
              onClick={onClearFilters}
            >
              Clear all
            </button>
          )}
        </div>
      </div>

      <AnimatePresence>
        {showFilters && (
          <motion.div
            className="filter-bar__panel"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="filter-bar__grid">
              {/* Read Status Filter */}
              <div className="filter-group">
                <label className="filter-label">Status</label>
                <select
                  value={filters.read_status || ''}
                  onChange={(e) => handleFilterChange('read_status', e.target.value || undefined)}
                  className="filter-select"
                >
                  <option value="">All</option>
                  <option value="unread">Unread</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              {/* Quality Filter */}
              <div className="filter-group">
                <label className="filter-label">
                  Quality Score: {filters.quality_min || 0}% - {filters.quality_max || 100}%
                </label>
                <div className="filter-range">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={filters.quality_min || 0}
                    onChange={(e) => handleFilterChange('quality_min', Number(e.target.value) / 100)}
                    className="filter-slider"
                  />
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={filters.quality_max || 100}
                    onChange={(e) => handleFilterChange('quality_max', Number(e.target.value) / 100)}
                    className="filter-slider"
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Active Filters Chips */}
      {activeFilterCount > 0 && (
        <div className="filter-bar__chips">
          {filters.read_status && (
            <div className="filter-chip">
              <span>Status: {filters.read_status}</span>
              <button onClick={() => handleFilterChange('read_status', undefined)}>
                <Icon icon={icons.close} size={12} />
              </button>
            </div>
          )}
          {(filters.quality_min !== undefined || filters.quality_max !== undefined) && (
            <div className="filter-chip">
              <span>
                Quality: {((filters.quality_min || 0) * 100).toFixed(0)}% - {((filters.quality_max || 1) * 100).toFixed(0)}%
              </span>
              <button onClick={() => {
                handleFilterChange('quality_min', undefined);
                handleFilterChange('quality_max', undefined);
              }}>
                <Icon icon={icons.close} size={12} />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
