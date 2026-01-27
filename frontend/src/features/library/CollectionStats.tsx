/**
 * CollectionStats Component
 * 
 * Displays statistics and visualizations for a collection.
 * Shows document counts, type breakdown, quality metrics, and top tags.
 * 
 * Features:
 * - Total document count
 * - Document type breakdown with visual bars
 * - Average quality score with progress bar
 * - Date range (created/updated)
 * - Top tags with counts
 * - Color-coded type indicators
 * - Loading skeleton variant
 * 
 * @example
 * ```tsx
 * <CollectionStats collection={myCollection} />
 * ```
 */

import { BarChart3, FileText, Calendar, Tag } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/loading/Skeleton';
import type { Collection } from '@/types/library';

/**
 * Props for the CollectionStats component
 */
interface CollectionStatsProps {
  /** Collection to display statistics for */
  collection: Collection;
  /** Optional CSS class name for styling */
  className?: string;
}
export function CollectionStats({
  collection,
  className = '',
}: CollectionStatsProps) {
  // Mock data - in real app, fetch from API
  const stats = {
    total_documents: collection.resource_count,
    document_types: [
      { type: 'PDF', count: Math.floor(collection.resource_count * 0.6) },
      { type: 'Code', count: Math.floor(collection.resource_count * 0.3) },
      { type: 'Markdown', count: Math.floor(collection.resource_count * 0.1) },
    ],
    avg_quality_score: 0.85,
    date_range: {
      earliest: collection.created_at,
      latest: collection.updated_at,
    },
    top_tags: collection.tags?.slice(0, 5).map((tag) => ({ tag, count: Math.floor(Math.random() * 10) + 1 })) || [],
  };

  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return 'bg-red-500';
      case 'code':
        return 'bg-blue-500';
      case 'markdown':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className={`collection-stats flex flex-col h-full ${className}`}>
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold">Statistics</h3>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6">
          {/* Total Documents */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Total Documents</span>
            </div>
            <p className="text-2xl font-bold">{stats.total_documents}</p>
          </div>

          {/* Document Types */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Document Types</span>
            </div>
            <div className="space-y-2">
              {stats.document_types.map((item) => (
                <div key={item.type}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span>{item.type}</span>
                    <span className="text-muted-foreground">{item.count}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getTypeColor(item.type)}`}
                      style={{ width: `${(item.count / stats.total_documents) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Average Quality */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Average Quality</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500"
                  style={{ width: `${stats.avg_quality_score * 100}%` }}
                />
              </div>
              <span className="text-sm font-medium">{(stats.avg_quality_score * 100).toFixed(0)}%</span>
            </div>
          </div>

          {/* Date Range */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Date Range</span>
            </div>
            <div className="text-sm text-muted-foreground">
              <p>Created: {new Date(stats.date_range.earliest).toLocaleDateString()}</p>
              <p>Updated: {new Date(stats.date_range.latest).toLocaleDateString()}</p>
            </div>
          </div>

          {/* Top Tags */}
          {stats.top_tags.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Tag className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Top Tags</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {stats.top_tags.map((item) => (
                  <Badge key={item.tag} variant="secondary">
                    {item.tag} ({item.count})
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

/**
 * Loading skeleton for CollectionStats
 */
export function CollectionStatsSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`collection-stats flex flex-col h-full ${className}`}>
      <div className="p-4 border-b">
        <Skeleton className="h-6 w-32" />
      </div>
      <div className="p-4 space-y-6">
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    </div>
  );
}
