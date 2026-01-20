/**
 * HybridScoreBadge Component
 * Displays composite search score with detailed breakdown on hover
 */

import { Sparkles, Search, BarChart3 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { ScoreBreakdown } from '../types';

interface HybridScoreBadgeProps {
  score: number;
  breakdown?: ScoreBreakdown;
}

export function HybridScoreBadge({ score, breakdown }: HybridScoreBadgeProps) {
  const percentage = Math.round(score * 100);
  
  // Color coding based on score
  const getColorClass = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300';
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300';
    return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
  };

  const formatScore = (value?: number) => {
    if (value === undefined) return 'N/A';
    return `${Math.round(value * 100)}%`;
  };

  const getProgressWidth = (value?: number) => {
    if (value === undefined) return '0%';
    return `${Math.round(value * 100)}%`;
  };

  return (
    <div className="group relative inline-block">
      <Badge className={getColorClass(score)}>
        {percentage}%
      </Badge>
      
      {/* Hover Card Tooltip */}
      {breakdown && (
        <div className="absolute left-0 top-full mt-2 w-64 p-4 bg-popover border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
          <div className="space-y-3">
            <h4 className="text-sm font-semibold mb-2">Score Breakdown</h4>
            
            {/* Semantic Score */}
            {breakdown.semantic_score !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1">
                    <Sparkles className="h-3 w-3" />
                    <span>Semantic Match</span>
                  </div>
                  <span className="font-semibold">{formatScore(breakdown.semantic_score)}</span>
                </div>
                <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-purple-500 transition-all duration-300"
                    style={{ width: getProgressWidth(breakdown.semantic_score) }}
                  />
                </div>
              </div>
            )}
            
            {/* Keyword Score */}
            {breakdown.keyword_score !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1">
                    <Search className="h-3 w-3" />
                    <span>Keyword Match</span>
                  </div>
                  <span className="font-semibold">{formatScore(breakdown.keyword_score)}</span>
                </div>
                <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: getProgressWidth(breakdown.keyword_score) }}
                  />
                </div>
              </div>
            )}
            
            {/* Composite Score */}
            <div className="space-y-1 pt-2 border-t">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1">
                  <BarChart3 className="h-3 w-3" />
                  <span className="font-semibold">Composite Score</span>
                </div>
                <span className="font-bold">{percentage}%</span>
              </div>
              <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
