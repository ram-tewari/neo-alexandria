/**
 * SearchResultItem Component
 * Display individual search result with metadata
 */

import { BookOpen, FileText, Globe, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { HybridScoreBadge } from './HybridScoreBadge';
import type { SearchResult } from '../types';

interface SearchResultItemProps {
  result: SearchResult;
  onClick: (id: number) => void;
}

const RESOURCE_TYPE_CONFIG = {
  article: { icon: FileText, color: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' },
  paper: { icon: FileText, color: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300' },
  book: { icon: BookOpen, color: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' },
  website: { icon: Globe, color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300' },
  default: { icon: FileText, color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300' },
};

export function SearchResultItem({ result, onClick }: SearchResultItemProps) {
  const typeConfig = RESOURCE_TYPE_CONFIG[result.resource_type as keyof typeof RESOURCE_TYPE_CONFIG] || RESOURCE_TYPE_CONFIG.default;
  const Icon = typeConfig.icon;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <Card
      className="p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onClick(result.id)}
    >
      <div className="space-y-3">
        {/* Title */}
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold line-clamp-2 flex-1">
            {result.title}
          </h3>
          {result.url && (
            <ExternalLink className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-1" />
          )}
        </div>

        {/* Description */}
        <p className="text-sm text-muted-foreground line-clamp-2">
          {result.description}
        </p>

        {/* Metadata Footer */}
        <div className="flex items-center gap-2 flex-wrap text-xs">
          {/* Resource Type Badge */}
          <Badge variant="secondary" className={typeConfig.color}>
            <Icon className="h-3 w-3 mr-1" />
            {result.resource_type}
          </Badge>

          {/* Quality Score */}
          {result.quality_score !== undefined && (
            <Badge variant="outline">
              Quality: {Math.round(result.quality_score * 100)}%
            </Badge>
          )}

          {/* Search Score with Breakdown */}
          <HybridScoreBadge score={result.score} breakdown={result.scores_breakdown} />

          {/* Date */}
          <span className="text-muted-foreground ml-auto">
            {formatDate(result.created_at)}
          </span>
        </div>

        {/* Tags */}
        {result.tags && result.tags.length > 0 && (
          <div className="flex items-center gap-1 flex-wrap">
            {result.tags.slice(0, 5).map((tag, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
            {result.tags.length > 5 && (
              <span className="text-xs text-muted-foreground">
                +{result.tags.length - 5} more
              </span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
