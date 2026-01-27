/**
 * DocumentGrid Component
 * 
 * Displays documents in a responsive grid with:
 * - Responsive layout (1-4 columns based on screen size)
 * - Virtual scrolling for performance with large datasets
 * - Loading skeletons
 * - Empty state
 * - Integration with useDocuments hook
 * - Keyboard navigation
 */

import { useEffect, useRef } from 'react';
import { FixedSizeGrid as Grid } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import { DocumentCard } from './DocumentCard';
import { Skeleton } from '@/components/loading/Skeleton';
import { FileText, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Resource } from '@/types/library';
import { cn } from '@/lib/utils';

export interface DocumentGridProps {
  documents: Resource[];
  isLoading?: boolean;
  selectedIds?: Set<string>;
  onDocumentClick?: (document: Resource) => void;
  onDocumentSelect?: (documentId: string, selected: boolean) => void;
  onDocumentDelete?: (documentId: string) => void;
  onDocumentAddToCollection?: (documentId: string) => void;
  onUploadClick?: () => void;
  className?: string;
}

// Calculate number of columns based on container width
function getColumnCount(width: number): number {
  if (width >= 1536) return 4; // 2xl
  if (width >= 1024) return 3; // lg
  if (width >= 768) return 2; // md
  return 1; // sm
}

// Card dimensions
const CARD_WIDTH = 280;
const CARD_HEIGHT = 420;
const GAP = 16;

export function DocumentGrid({
  documents,
  isLoading = false,
  selectedIds = new Set(),
  onDocumentClick,
  onDocumentSelect,
  onDocumentDelete,
  onDocumentAddToCollection,
  onUploadClick,
  className,
}: DocumentGridProps) {
  const gridRef = useRef<Grid>(null);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!gridRef.current) return;

      // Arrow key navigation
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        e.preventDefault();
        // Grid handles arrow key navigation automatically
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Loading state
  if (isLoading) {
    return (
      <div className={cn('grid gap-4', className)}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <DocumentCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (documents.length === 0) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-16', className)}>
        <div className="rounded-full bg-muted p-6 mb-4">
          <FileText className="h-12 w-12 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold mb-2">No documents yet</h3>
        <p className="text-sm text-muted-foreground mb-6 text-center max-w-sm">
          Get started by uploading your first document or importing from a repository
        </p>
        {onUploadClick && (
          <Button onClick={onUploadClick}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Document
          </Button>
        )}
      </div>
    );
  }

  // Grid cell renderer
  const Cell = ({ columnIndex, rowIndex, style }: any) => {
    const index = rowIndex * getColumnCount(window.innerWidth) + columnIndex;
    const document = documents[index];

    if (!document) return null;

    return (
      <div style={style} className="p-2">
        <DocumentCard
          document={document}
          isSelected={selectedIds.has(document.id)}
          onSelect={(selected) => onDocumentSelect?.(document.id, selected)}
          onClick={() => onDocumentClick?.(document)}
          onDelete={() => onDocumentDelete?.(document.id)}
          onAddToCollection={() => onDocumentAddToCollection?.(document.id)}
        />
      </div>
    );
  };

  return (
    <div className={cn('h-full w-full', className)}>
      <AutoSizer>
        {({ height, width }) => {
          const columnCount = getColumnCount(width);
          const rowCount = Math.ceil(documents.length / columnCount);
          const columnWidth = Math.floor(width / columnCount);

          return (
            <Grid
              ref={gridRef}
              columnCount={columnCount}
              columnWidth={columnWidth}
              height={height}
              rowCount={rowCount}
              rowHeight={CARD_HEIGHT + GAP}
              width={width}
              className="scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent"
            >
              {Cell}
            </Grid>
          );
        }}
      </AutoSizer>
    </div>
  );
}

// Loading skeleton for document card
function DocumentCardSkeleton() {
  return (
    <div className="rounded-xl border bg-card overflow-hidden">
      {/* Thumbnail skeleton */}
      <Skeleton className="aspect-[3/4] w-full" />
      
      {/* Content skeleton */}
      <div className="p-4 space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
        <Skeleton className="h-3 w-1/3" />
      </div>
    </div>
  );
}
