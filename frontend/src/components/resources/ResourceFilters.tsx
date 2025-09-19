// Neo Alexandria 2.0 Frontend - Resource Filters Component
// Advanced filtering panel for the library dashboard

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Card, CardContent } from '@/components/ui/Card';
import { useClassificationTree } from '@/hooks/useApi';
import { useLibraryFilters, useAppStore } from '@/store';
import { X, Calendar, Star, BookOpen, Filter } from 'lucide-react';
import { cn } from '@/utils/cn';
import { formatClassificationCode } from '@/utils/format';
import type { ResourceQueryParams } from '@/types/api';

interface FilterSectionProps {
  title: string;
  children: React.ReactNode;
  collapsible?: boolean;
  defaultOpen?: boolean;
}

const FilterSection: React.FC<FilterSectionProps> = ({
  title,
  children,
  collapsible = true,
  defaultOpen = true,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-secondary-200 rounded-lg">
      <button
        onClick={() => collapsible && setIsOpen(!isOpen)}
        className={cn(
          'w-full px-4 py-3 text-left text-sm font-medium text-secondary-900 bg-secondary-50',
          'hover:bg-secondary-100 transition-colors',
          'rounded-t-lg',
          !isOpen && 'rounded-b-lg'
        )}
        disabled={!collapsible}
      >
        <div className="flex items-center justify-between">
          {title}
          {collapsible && (
            <span className={cn('transition-transform', isOpen && 'rotate-180')}>
              ▼
            </span>
          )}
        </div>
      </button>
      
      {isOpen && (
        <div className="p-4 border-t border-secondary-200">
          {children}
        </div>
      )}
    </div>
  );
};

const ResourceFilters: React.FC = () => {
  const filters = useLibraryFilters();
  const setFilters = useAppStore(state => state.setLibraryFilters);
  const { data: classificationData } = useClassificationTree();

  const [localFilters, setLocalFilters] = useState<Partial<ResourceQueryParams>>(filters);

  const updateFilter = (key: keyof ResourceQueryParams, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
  };

  const applyFilters = () => {
    setFilters({ ...filters, ...localFilters, offset: 0 }); // Reset offset when applying filters
  };

  const clearFilters = () => {
    const clearedFilters = {
      limit: filters.limit,
      offset: 0,
      sort_by: filters.sort_by,
      sort_dir: filters.sort_dir,
    };
    setLocalFilters(clearedFilters);
    setFilters(clearedFilters);
  };

  const removeFilter = (key: keyof ResourceQueryParams) => {
    const newFilters = { ...localFilters };
    delete newFilters[key];
    setLocalFilters(newFilters);
    setFilters({ ...filters, ...newFilters });
  };

  const hasActiveFilters = Object.keys(localFilters).some(key => 
    !['limit', 'offset', 'sort_by', 'sort_dir'].includes(key) && localFilters[key as keyof ResourceQueryParams]
  );

  return (
    <div className="space-y-4">
      {/* Active Filters */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-secondary-600">Active filters:</span>
          
          {localFilters.classification_code && (
            <Badge variant="info" className="flex items-center gap-1">
              Classification: {localFilters.classification_code}
              <button
                onClick={() => removeFilter('classification_code')}
                className="ml-1 hover:bg-blue-200 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}

          {localFilters.type && (
            <Badge variant="info" className="flex items-center gap-1">
              Type: {localFilters.type}
              <button
                onClick={() => removeFilter('type')}
                className="ml-1 hover:bg-blue-200 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}

          {localFilters.language && (
            <Badge variant="info" className="flex items-center gap-1">
              Language: {localFilters.language}
              <button
                onClick={() => removeFilter('language')}
                className="ml-1 hover:bg-blue-200 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}

          {localFilters.read_status && (
            <Badge variant="info" className="flex items-center gap-1">
              Status: {localFilters.read_status}
              <button
                onClick={() => removeFilter('read_status')}
                className="ml-1 hover:bg-blue-200 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}

          {localFilters.min_quality && (
            <Badge variant="info" className="flex items-center gap-1">
              Min Quality: {Math.round(localFilters.min_quality * 100)}%
              <button
                onClick={() => removeFilter('min_quality')}
                className="ml-1 hover:bg-blue-200 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="text-secondary-600 hover:text-secondary-900"
          >
            Clear all
          </Button>
        </div>
      )}

      {/* Filter Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Classification */}
        <FilterSection title="Classification">
          <div className="space-y-2">
            {classificationData?.tree && classificationData.tree.length > 0 ? (
              <div className="grid grid-cols-2 gap-2">
                {classificationData.tree.map((category) => (
                  <button
                    key={category.code}
                    onClick={() => updateFilter('classification_code', category.code)}
                    className={cn(
                      'text-left p-2 rounded border text-xs',
                      localFilters.classification_code === category.code
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-secondary-200 hover:border-secondary-300 text-secondary-700'
                    )}
                  >
                    <div className="font-medium">{category.code}</div>
                    <div className="text-xs text-secondary-500 truncate">{category.name}</div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-sm text-secondary-500 italic">
                {classificationData ? 'No classification categories available' : 'Loading classification tree...'}
              </div>
            )}
          </div>
        </FilterSection>

        {/* Content Type */}
        <FilterSection title="Content Type">
          <div className="grid grid-cols-2 gap-2">
            {[
              { value: 'article', label: 'Article' },
              { value: 'book', label: 'Book' },
              { value: 'video', label: 'Video' },
              { value: 'podcast', label: 'Podcast' },
              { value: 'paper', label: 'Paper' },
              { value: 'tutorial', label: 'Tutorial' },
            ].map(({ value, label }) => (
              <button
                key={value}
                onClick={() => updateFilter('type', value)}
                className={cn(
                  'text-left p-2 rounded border text-sm',
                  localFilters.type === value
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-secondary-200 hover:border-secondary-300 text-secondary-700'
                )}
              >
                {label}
              </button>
            ))}
          </div>
        </FilterSection>

        {/* Read Status */}
        <FilterSection title="Read Status">
          <div className="grid grid-cols-2 gap-2">
            {[
              { value: 'unread', label: 'Unread', icon: <BookOpen className="w-4 h-4" /> },
              { value: 'in_progress', label: 'In Progress', icon: <BookOpen className="w-4 h-4" /> },
              { value: 'completed', label: 'Completed', icon: <BookOpen className="w-4 h-4" /> },
              { value: 'archived', label: 'Archived', icon: <BookOpen className="w-4 h-4" /> },
            ].map(({ value, label, icon }) => (
              <button
                key={value}
                onClick={() => updateFilter('read_status', value)}
                className={cn(
                  'flex items-center space-x-2 text-left p-2 rounded border text-sm',
                  localFilters.read_status === value
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-secondary-200 hover:border-secondary-300 text-secondary-700'
                )}
              >
                {icon}
                <span>{label}</span>
              </button>
            ))}
          </div>
        </FilterSection>

        {/* Quality Score */}
        <FilterSection title="Quality Score">
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-secondary-700 mb-1">
                Minimum Quality: {localFilters.min_quality ? Math.round(localFilters.min_quality * 100) : 0}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={localFilters.min_quality || 0}
                onChange={(e) => updateFilter('min_quality', parseFloat(e.target.value))}
                className="w-full h-2 bg-secondary-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
            
            <div className="grid grid-cols-3 gap-2 text-xs">
              {[
                { value: 0.8, label: 'High (80%+)', color: 'text-green-600' },
                { value: 0.6, label: 'Medium (60%+)', color: 'text-yellow-600' },
                { value: 0.4, label: 'Low (40%+)', color: 'text-orange-600' },
              ].map(({ value, label, color }) => (
                <button
                  key={value}
                  onClick={() => updateFilter('min_quality', value)}
                  className={cn(
                    'p-1 rounded text-center border',
                    color,
                    localFilters.min_quality === value
                      ? 'border-current bg-current/10'
                      : 'border-secondary-200 hover:border-current'
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </FilterSection>

        {/* Language */}
        <FilterSection title="Language">
          <div className="grid grid-cols-3 gap-2">
            {[
              { value: 'en', label: 'English' },
              { value: 'es', label: 'Spanish' },
              { value: 'fr', label: 'French' },
              { value: 'de', label: 'German' },
              { value: 'it', label: 'Italian' },
              { value: 'pt', label: 'Portuguese' },
            ].map(({ value, label }) => (
              <button
                key={value}
                onClick={() => updateFilter('language', value)}
                className={cn(
                  'text-left p-2 rounded border text-sm',
                  localFilters.language === value
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-secondary-200 hover:border-secondary-300 text-secondary-700'
                )}
              >
                {label}
              </button>
            ))}
          </div>
        </FilterSection>

        {/* Date Filters */}
        <FilterSection title="Date Range">
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-secondary-700 mb-1">
                Created After
              </label>
              <Input
                type="date"
                value={localFilters.created_from?.split('T')[0] || ''}
                onChange={(e) => updateFilter('created_from', e.target.value ? `${e.target.value}T00:00:00Z` : undefined)}
                leftIcon={<Calendar className="w-4 h-4" />}
              />
            </div>
            
            <div>
              <label className="block text-sm text-secondary-700 mb-1">
                Created Before
              </label>
              <Input
                type="date"
                value={localFilters.created_to?.split('T')[0] || ''}
                onChange={(e) => updateFilter('created_to', e.target.value ? `${e.target.value}T23:59:59Z` : undefined)}
                leftIcon={<Calendar className="w-4 h-4" />}
              />
            </div>
          </div>
        </FilterSection>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-secondary-200">
        <Button
          variant="outline"
          onClick={clearFilters}
          disabled={!hasActiveFilters}
        >
          Clear Filters
        </Button>
        
        <Button
          variant="primary"
          onClick={applyFilters}
          icon={<Filter className="w-4 h-4" />}
        >
          Apply Filters
        </Button>
      </div>
    </div>
  );
};

export { ResourceFilters };
