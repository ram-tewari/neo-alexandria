/**
 * DocumentFilters Component
 * 
 * Filter controls for document library:
 * - Type filter (PDF, HTML, Code, Text)
 * - Quality score range slider
 * - Date range picker
 * - Sort dropdown
 * - Search input
 * - Clear filters button
 */

import { useState, useEffect } from 'react';
import { Search, X, SlidersHorizontal } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';

export interface DocumentFiltersState {
  search: string;
  type?: 'pdf' | 'html' | 'code' | 'text';
  qualityMin: number;
  qualityMax: number;
  sortBy: 'date' | 'title' | 'quality';
  sortOrder: 'asc' | 'desc';
}

export interface DocumentFiltersProps {
  filters: DocumentFiltersState;
  onFiltersChange: (filters: DocumentFiltersState) => void;
  className?: string;
}

const DEFAULT_FILTERS: DocumentFiltersState = {
  search: '',
  type: undefined,
  qualityMin: 0,
  qualityMax: 100,
  sortBy: 'date',
  sortOrder: 'desc',
};

export function DocumentFilters({
  filters,
  onFiltersChange,
  className,
}: DocumentFiltersProps) {
  const [localSearch, setLocalSearch] = useState(filters.search);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localSearch !== filters.search) {
        onFiltersChange({ ...filters, search: localSearch });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [localSearch]);

  const hasActiveFilters =
    filters.search ||
    filters.type ||
    filters.qualityMin > 0 ||
    filters.qualityMax < 100 ||
    filters.sortBy !== 'date' ||
    filters.sortOrder !== 'desc';

  const clearFilters = () => {
    setLocalSearch('');
    onFiltersChange(DEFAULT_FILTERS);
  };

  const activeFilterCount = [
    filters.search,
    filters.type,
    filters.qualityMin > 0 || filters.qualityMax < 100,
  ].filter(Boolean).length;

  return (
    <div className={cn('flex flex-col gap-4', className)}>
      {/* Search and Quick Actions */}
      <div className="flex gap-2">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search documents..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            className="pl-9 pr-9"
          />
          {localSearch && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
              onClick={() => setLocalSearch('')}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Advanced Filters Popover */}
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" className="relative">
              <SlidersHorizontal className="mr-2 h-4 w-4" />
              Filters
              {activeFilterCount > 0 && (
                <Badge
                  variant="default"
                  className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                >
                  {activeFilterCount}
                </Badge>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80" align="end">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Filters</h4>
                {hasActiveFilters && (
                  <Button variant="ghost" size="sm" onClick={clearFilters}>
                    Clear all
                  </Button>
                )}
              </div>

              {/* Type Filter */}
              <div className="space-y-2">
                <Label>Document Type</Label>
                <Select
                  value={filters.type || 'all'}
                  onValueChange={(value) =>
                    onFiltersChange({
                      ...filters,
                      type: value === 'all' ? undefined : (value as any),
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All types</SelectItem>
                    <SelectItem value="pdf">PDF</SelectItem>
                    <SelectItem value="html">HTML</SelectItem>
                    <SelectItem value="code">Code</SelectItem>
                    <SelectItem value="text">Text</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Quality Range */}
              <div className="space-y-2">
                <Label>
                  Quality Score: {filters.qualityMin}% - {filters.qualityMax}%
                </Label>
                <Slider
                  min={0}
                  max={100}
                  step={5}
                  value={[filters.qualityMin, filters.qualityMax]}
                  onValueChange={([min, max]) =>
                    onFiltersChange({ ...filters, qualityMin: min, qualityMax: max })
                  }
                  className="py-4"
                />
              </div>
            </div>
          </PopoverContent>
        </Popover>

        {/* Sort */}
        <Select
          value={`${filters.sortBy}-${filters.sortOrder}`}
          onValueChange={(value) => {
            const [sortBy, sortOrder] = value.split('-') as [
              DocumentFiltersState['sortBy'],
              DocumentFiltersState['sortOrder']
            ];
            onFiltersChange({ ...filters, sortBy, sortOrder });
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="date-desc">Newest first</SelectItem>
            <SelectItem value="date-asc">Oldest first</SelectItem>
            <SelectItem value="title-asc">Title A-Z</SelectItem>
            <SelectItem value="title-desc">Title Z-A</SelectItem>
            <SelectItem value="quality-desc">Highest quality</SelectItem>
            <SelectItem value="quality-asc">Lowest quality</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Active Filters */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2">
          {filters.search && (
            <Badge variant="secondary" className="gap-1">
              Search: {filters.search}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => {
                  setLocalSearch('');
                  onFiltersChange({ ...filters, search: '' });
                }}
              />
            </Badge>
          )}
          {filters.type && (
            <Badge variant="secondary" className="gap-1">
              Type: {filters.type.toUpperCase()}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => onFiltersChange({ ...filters, type: undefined })}
              />
            </Badge>
          )}
          {(filters.qualityMin > 0 || filters.qualityMax < 100) && (
            <Badge variant="secondary" className="gap-1">
              Quality: {filters.qualityMin}%-{filters.qualityMax}%
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() =>
                  onFiltersChange({ ...filters, qualityMin: 0, qualityMax: 100 })
                }
              />
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}
