// Neo Alexandria 2.0 Frontend - Faceted Search Sidebar
// Collapsible filter sidebar with classification, type, language, quality, and subject filters

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, X } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useSubjectSuggestions } from '@/hooks/useApi';
import { cn } from '@/utils/cn';
import type { SearchFilters, Facets } from '@/types/api';

interface FacetedSearchSidebarProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  facets?: Facets;
}

export const FacetedSearchSidebar: React.FC<FacetedSearchSidebarProps> = ({
  filters,
  onFiltersChange,
  facets,
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['classification', 'type', 'language', 'read_status', 'quality'])
  );
  const [subjectQuery, setSubjectQuery] = useState('');
  const { data: subjectSuggestions } = useSubjectSuggestions(subjectQuery);

  const toggleSection = useCallback((section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  }, []);

  const handleCheckboxChange = useCallback((
    filterKey: keyof SearchFilters,
    value: string,
    checked: boolean
  ) => {
    const currentValues = (filters[filterKey] as string[]) || [];
    const newValues = checked
      ? [...currentValues, value]
      : currentValues.filter(v => v !== value);
    
    onFiltersChange({
      ...filters,
      [filterKey]: newValues.length > 0 ? newValues : undefined,
    });
  }, [filters, onFiltersChange]);

  const handleQualityChange = useCallback((value: number) => {
    onFiltersChange({
      ...filters,
      min_quality: value > 0 ? value : undefined,
    });
  }, [filters, onFiltersChange]);

  const handleSubjectAdd = useCallback((subject: string) => {
    const currentSubjects = filters.subject_any || [];
    if (!currentSubjects.includes(subject)) {
      onFiltersChange({
        ...filters,
        subject_any: [...currentSubjects, subject],
      });
    }
    setSubjectQuery('');
  }, [filters, onFiltersChange]);

  const handleSubjectRemove = useCallback((subject: string) => {
    const currentSubjects = filters.subject_any || [];
    onFiltersChange({
      ...filters,
      subject_any: currentSubjects.filter(s => s !== subject),
    });
  }, [filters, onFiltersChange]);

  const clearAllFilters = useCallback(() => {
    onFiltersChange({});
  }, [onFiltersChange]);

  const hasActiveFilters = Object.values(filters).some(v => 
    Array.isArray(v) ? v.length > 0 : v !== undefined
  );

  return (
    <Card variant="glass" className="sticky top-20">
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-charcoal-grey-50">Filters</h3>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAllFilters}
              className="text-accent-blue-400 hover:text-accent-blue-300"
            >
              Clear All
            </Button>
          )}
        </div>

        <div className="space-y-4">
          {/* Classification Filter */}
          <FilterSection
            title="Classification"
            isExpanded={expandedSections.has('classification')}
            onToggle={() => toggleSection('classification')}
            count={filters.classification_code?.length}
          >
            <div className="space-y-2">
              {facets?.classification_code?.slice(0, 10).map(({ key, count }) => (
                <CheckboxFilter
                  key={key}
                  label={key}
                  count={count}
                  checked={filters.classification_code?.includes(key) || false}
                  onChange={(checked) => handleCheckboxChange('classification_code', key, checked)}
                />
              ))}
            </div>
          </FilterSection>

          {/* Type Filter */}
          <FilterSection
            title="Resource Type"
            isExpanded={expandedSections.has('type')}
            onToggle={() => toggleSection('type')}
            count={filters.type?.length}
          >
            <div className="space-y-2">
              {facets?.type?.map(({ key, count }) => (
                <CheckboxFilter
                  key={key}
                  label={key || 'Unknown'}
                  count={count}
                  checked={filters.type?.includes(key) || false}
                  onChange={(checked) => handleCheckboxChange('type', key, checked)}
                />
              ))}
            </div>
          </FilterSection>

          {/* Language Filter */}
          <FilterSection
            title="Language"
            isExpanded={expandedSections.has('language')}
            onToggle={() => toggleSection('language')}
            count={filters.language?.length}
          >
            <div className="space-y-2">
              {facets?.language?.map(({ key, count }) => (
                <CheckboxFilter
                  key={key}
                  label={key || 'Unknown'}
                  count={count}
                  checked={filters.language?.includes(key) || false}
                  onChange={(checked) => handleCheckboxChange('language', key, checked)}
                />
              ))}
            </div>
          </FilterSection>

          {/* Read Status Filter */}
          <FilterSection
            title="Read Status"
            isExpanded={expandedSections.has('read_status')}
            onToggle={() => toggleSection('read_status')}
            count={filters.read_status?.length}
          >
            <div className="space-y-2">
              {facets?.read_status?.map(({ key, count }) => (
                <CheckboxFilter
                  key={key}
                  label={formatReadStatus(key)}
                  count={count}
                  checked={filters.read_status?.includes(key as any) || false}
                  onChange={(checked) => handleCheckboxChange('read_status', key, checked)}
                />
              ))}
            </div>
          </FilterSection>

          {/* Quality Score Filter */}
          <FilterSection
            title="Quality Score"
            isExpanded={expandedSections.has('quality')}
            onToggle={() => toggleSection('quality')}
            count={filters.min_quality ? 1 : undefined}
          >
            <div className="space-y-3">
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={filters.min_quality || 0}
                onChange={(e) => handleQualityChange(Number(e.target.value))}
                className="w-full h-2 bg-charcoal-grey-700 rounded-lg appearance-none cursor-pointer accent-accent-blue-500"
              />
              <div className="flex items-center justify-between text-sm">
                <span className="text-charcoal-grey-400">Min: {filters.min_quality || 0}%</span>
                <span className="text-charcoal-grey-400">Max: 100%</span>
              </div>
            </div>
          </FilterSection>

          {/* Subject Filter with Autocomplete */}
          <FilterSection
            title="Subjects"
            isExpanded={expandedSections.has('subjects')}
            onToggle={() => toggleSection('subjects')}
            count={filters.subject_any?.length}
          >
            <div className="space-y-3">
              {/* Selected Subjects */}
              {filters.subject_any && filters.subject_any.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {filters.subject_any.map(subject => (
                    <span
                      key={subject}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-accent-blue-500/20 text-accent-blue-300 rounded text-sm"
                    >
                      {subject}
                      <button
                        onClick={() => handleSubjectRemove(subject)}
                        className="hover:text-accent-blue-100"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {/* Subject Input with Autocomplete */}
              <div className="relative">
                <Input
                  placeholder="Search subjects..."
                  value={subjectQuery}
                  onChange={(e) => setSubjectQuery(e.target.value)}
                  className="w-full"
                />
                
                {/* Suggestions Dropdown */}
                {subjectQuery && subjectSuggestions && subjectSuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-charcoal-grey-800 border border-charcoal-grey-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    {subjectSuggestions.map(suggestion => (
                      <button
                        key={suggestion}
                        onClick={() => handleSubjectAdd(suggestion)}
                        className="w-full px-3 py-2 text-left text-sm text-charcoal-grey-200 hover:bg-charcoal-grey-700 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </FilterSection>
        </div>
      </CardContent>
    </Card>
  );
};

// Filter Section Component
interface FilterSectionProps {
  title: string;
  isExpanded: boolean;
  onToggle: () => void;
  count?: number;
  children: React.ReactNode;
}

const FilterSection: React.FC<FilterSectionProps> = ({
  title,
  isExpanded,
  onToggle,
  count,
  children,
}) => {
  return (
    <div className="border-b border-charcoal-grey-700 pb-4 last:border-b-0">
      <button
        onClick={onToggle}
        className="flex items-center justify-between w-full text-left mb-3 group"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-charcoal-grey-200 group-hover:text-charcoal-grey-50 transition-colors">
            {title}
          </span>
          {count !== undefined && count > 0 && (
            <span className="px-2 py-0.5 bg-accent-blue-500/20 text-accent-blue-300 rounded-full text-xs">
              {count}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-charcoal-grey-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-charcoal-grey-400" />
        )}
      </button>
      
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Checkbox Filter Component
interface CheckboxFilterProps {
  label: string;
  count: number;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

const CheckboxFilter: React.FC<CheckboxFilterProps> = ({
  label,
  count,
  checked,
  onChange,
}) => {
  return (
    <label className="flex items-center justify-between cursor-pointer group">
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="w-4 h-4 text-accent-blue-500 bg-charcoal-grey-700 border-charcoal-grey-600 rounded focus:ring-accent-blue-500 focus:ring-2"
        />
        <span className={cn(
          'text-sm transition-colors',
          checked ? 'text-charcoal-grey-50 font-medium' : 'text-charcoal-grey-300 group-hover:text-charcoal-grey-100'
        )}>
          {label}
        </span>
      </div>
      <span className="text-xs text-charcoal-grey-500">
        {count}
      </span>
    </label>
  );
};

// Helper function
function formatReadStatus(status: string): string {
  const statusMap: Record<string, string> = {
    'unread': 'Unread',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'archived': 'Archived',
  };
  return statusMap[status] || status;
}
