/**
 * RepositoryHeader Component
 * 
 * Displays repository information and actions in the header area.
 * Shows repository name, description, stats, and status.
 */

import { GitBranch, Star, FileCode, Activity } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { Repository } from '@/stores/repository';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface RepositoryHeaderProps {
  repository: Repository;
}

// ============================================================================
// Component
// ============================================================================

export function RepositoryHeader({ repository }: RepositoryHeaderProps) {
  const statusColors = {
    ready: 'bg-green-500',
    indexing: 'bg-yellow-500',
    error: 'bg-red-500',
  };

  const statusLabels = {
    ready: 'Ready',
    indexing: 'Indexing',
    error: 'Error',
  };

  return (
    <div className="border-b bg-card px-6 py-4">
      <div className="flex items-start justify-between">
        {/* Repository Info */}
        <div className="space-y-2">
          {/* Name and Status */}
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">{repository.name}</h1>
            <div className="flex items-center gap-2">
              <div
                className={cn(
                  'h-2 w-2 rounded-full',
                  statusColors[repository.status]
                )}
              />
              <span className="text-sm text-muted-foreground">
                {statusLabels[repository.status]}
              </span>
            </div>
          </div>

          {/* Description */}
          {repository.description && (
            <p className="text-sm text-muted-foreground max-w-2xl">
              {repository.description}
            </p>
          )}

          {/* Metadata */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            {/* Source */}
            <div className="flex items-center gap-1.5">
              <GitBranch className="h-4 w-4" />
              <span className="capitalize">{repository.source}</span>
            </div>

            {/* Language */}
            {repository.language && (
              <Badge variant="secondary" className="font-normal">
                {repository.language}
              </Badge>
            )}

            {/* Stars */}
            {repository.stars !== undefined && (
              <div className="flex items-center gap-1.5">
                <Star className="h-4 w-4" />
                <span>{repository.stars.toLocaleString()}</span>
              </div>
            )}

            {/* Stats */}
            {repository.stats && (
              <>
                <div className="flex items-center gap-1.5">
                  <FileCode className="h-4 w-4" />
                  <span>{repository.stats.files.toLocaleString()} files</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Activity className="h-4 w-4" />
                  <span>{repository.stats.lines.toLocaleString()} lines</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Actions (placeholder for future) */}
        <div className="flex items-center gap-2">
          {/* TODO: Add actions like refresh, settings, etc. */}
        </div>
      </div>
    </div>
  );
}
