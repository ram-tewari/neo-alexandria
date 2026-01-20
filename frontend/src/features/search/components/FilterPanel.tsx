/**
 * FilterPanel Component
 * Sidebar with quality and search method filters
 */

import { SlidersHorizontal } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { SearchFilters, SearchMethod } from '../types';

interface FilterPanelProps {
  filters: SearchFilters;
  method: SearchMethod;
  onFilterChange: (key: keyof SearchFilters, value: any) => void;
  onMethodChange: (method: SearchMethod) => void;
  isMobile?: boolean;
}

export function FilterPanel({
  filters,
  method,
  onFilterChange,
  onMethodChange,
  isMobile = false,
}: FilterPanelProps) {
  const qualityValue = Math.round((filters.min_quality || 0) * 100);

  const handleQualityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    onFilterChange('min_quality', value / 100);
  };

  return (
    <div className={`space-y-6 ${isMobile ? 'p-4' : 'p-6'}`}>
      <div className="flex items-center gap-2">
        <SlidersHorizontal className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Filters</h2>
      </div>

      {/* Search Method */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Search Method</Label>
        <Tabs value={method} onValueChange={(v) => onMethodChange(v as SearchMethod)}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="hybrid">Hybrid</TabsTrigger>
            <TabsTrigger value="semantic">Semantic</TabsTrigger>
          </TabsList>
        </Tabs>
        <p className="text-xs text-muted-foreground">
          {method === 'hybrid'
            ? 'Combines keyword and semantic search'
            : 'AI-powered meaning-based search'}
        </p>
      </div>

      {/* Quality Score Filter */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label htmlFor="quality-slider" className="text-sm font-medium">
            Min Quality
          </Label>
          <span className="text-sm font-semibold text-primary">
            {qualityValue}%
          </span>
        </div>
        <input
          id="quality-slider"
          type="range"
          min="0"
          max="100"
          step="5"
          value={qualityValue}
          onChange={handleQualityChange}
          className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
          aria-label={`Minimum quality score: ${qualityValue}%`}
        />
        <p className="text-xs text-muted-foreground">
          Filter results by quality score
        </p>
      </div>
    </div>
  );
}
