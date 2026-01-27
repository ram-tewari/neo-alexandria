/**
 * DocumentCard Component
 * 
 * Displays a single document in the library grid with:
 * - Thumbnail preview
 * - Title, authors, and publication date
 * - Quality score badge
 * - Quick actions (open, delete, add to collection)
 * - Selection checkbox for batch operations
 * - Hover effects and animations
 */

import { useState } from 'react';
import { FileText, Trash2, FolderPlus, MoreVertical } from 'lucide-react';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Checkbox } from '@/components/ui/checkbox';
import type { Resource } from '@/types/library';
import { cn } from '@/lib/utils';

export interface DocumentCardProps {
  document: Resource;
  isSelected?: boolean;
  onSelect?: (selected: boolean) => void;
  onClick?: () => void;
  onDelete?: () => void;
  onAddToCollection?: () => void;
  className?: string;
}

export function DocumentCard({
  document,
  isSelected = false,
  onSelect,
  onClick,
  onDelete,
  onAddToCollection,
  className,
}: DocumentCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  // Format date
  const formattedDate = document.publication_date
    ? new Date(document.publication_date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : document.created_at
    ? new Date(document.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : 'Unknown date';

  // Format authors
  const authors = document.authors?.join(', ') || document.creator || 'Unknown author';
  const truncatedAuthors = authors.length > 50 ? `${authors.slice(0, 50)}...` : authors;

  // Quality score badge variant
  const getQualityVariant = (score?: number) => {
    if (!score) return 'secondary';
    if (score >= 0.8) return 'default';
    if (score >= 0.6) return 'secondary';
    return 'outline';
  };

  // Quality score color
  const getQualityColor = (score?: number) => {
    if (!score) return 'text-muted-foreground';
    if (score >= 0.8) return 'text-green-600 dark:text-green-400';
    if (score >= 0.6) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  // Handle card click (but not when clicking actions)
  const handleCardClick = (e: React.MouseEvent) => {
    // Don't trigger if clicking on interactive elements
    const target = e.target as HTMLElement;
    if (
      target.closest('button') ||
      target.closest('[role="checkbox"]') ||
      target.closest('[role="menuitem"]')
    ) {
      return;
    }
    onClick?.();
  };

  return (
    <Card
      className={cn(
        'group relative overflow-hidden transition-all duration-200',
        'hover:shadow-lg hover:scale-[1.02]',
        isSelected && 'ring-2 ring-primary',
        onClick && 'cursor-pointer',
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCardClick}
    >
      {/* Selection Checkbox */}
      {onSelect && (
        <div className="absolute top-3 left-3 z-10">
          <Checkbox
            checked={isSelected}
            onCheckedChange={onSelect}
            className="bg-background/80 backdrop-blur-sm"
            aria-label={`Select ${document.title}`}
          />
        </div>
      )}

      {/* Quick Actions Menu */}
      <div className="absolute top-3 right-3 z-10">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                'h-8 w-8 bg-background/80 backdrop-blur-sm',
                'opacity-0 group-hover:opacity-100 transition-opacity',
                isHovered && 'opacity-100'
              )}
              aria-label="Document actions"
            >
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {onAddToCollection && (
              <DropdownMenuItem onClick={onAddToCollection}>
                <FolderPlus className="mr-2 h-4 w-4" />
                Add to Collection
              </DropdownMenuItem>
            )}
            {onDelete && (
              <DropdownMenuItem
                onClick={onDelete}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Thumbnail */}
      <div className="relative aspect-[3/4] overflow-hidden bg-muted">
        {document.thumbnail_url ? (
          <img
            src={document.thumbnail_url}
            alt={document.title}
            className="h-full w-full object-cover transition-transform duration-200 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <FileText className="h-16 w-16 text-muted-foreground/50" />
          </div>
        )}

        {/* Quality Score Badge */}
        {document.quality_score !== undefined && (
          <div className="absolute bottom-2 right-2">
            <Badge
              variant={getQualityVariant(document.quality_score)}
              className={cn('font-mono text-xs', getQualityColor(document.quality_score))}
            >
              {(document.quality_score * 100).toFixed(0)}%
            </Badge>
          </div>
        )}

        {/* Document Type Badge */}
        {document.content_type && (
          <div className="absolute top-2 left-2">
            <Badge variant="secondary" className="text-xs uppercase">
              {document.content_type}
            </Badge>
          </div>
        )}
      </div>

      {/* Content */}
      <CardContent className="p-4">
        {/* Title */}
        <h3
          className="mb-2 line-clamp-2 text-sm font-semibold leading-tight"
          title={document.title}
        >
          {document.title}
        </h3>

        {/* Authors */}
        <p className="mb-1 text-xs text-muted-foreground" title={authors}>
          {truncatedAuthors}
        </p>

        {/* Date */}
        <p className="text-xs text-muted-foreground">{formattedDate}</p>
      </CardContent>

      {/* Footer with Quick Actions */}
      <CardFooter
        className={cn(
          'border-t p-2 transition-opacity',
          'opacity-0 group-hover:opacity-100',
          isHovered && 'opacity-100'
        )}
      >
        <div className="flex w-full gap-1">
          {onClick && (
            <Button
              variant="ghost"
              size="sm"
              className="flex-1 text-xs"
              onClick={(e) => {
                e.stopPropagation();
                onClick();
              }}
            >
              Open
            </Button>
          )}
          {onAddToCollection && (
            <Button
              variant="ghost"
              size="sm"
              className="flex-1 text-xs"
              onClick={(e) => {
                e.stopPropagation();
                onAddToCollection();
              }}
            >
              <FolderPlus className="mr-1 h-3 w-3" />
              Add
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
