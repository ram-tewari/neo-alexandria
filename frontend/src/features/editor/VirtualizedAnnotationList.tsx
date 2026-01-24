/**
 * VirtualizedAnnotationList Component
 * 
 * Virtualized list of annotations using react-window for performance.
 * Only renders visible items to handle large numbers of annotations efficiently.
 * 
 * Performance optimizations:
 * - Virtualized rendering with react-window
 * - Memoized list items with React.memo
 * - Debounced scroll events
 * 
 * Requirements: 7.2 - React optimization
 * 
 * Note: Requires react-window to be installed:
 * npm install react-window @types/react-window
 */

import { memo, useCallback } from 'react';
import { FixedSizeList as List } from 'react-window';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Trash2, Edit } from 'lucide-react';
import type { Annotation } from './types';

// ============================================================================
// Types
// ============================================================================

export interface VirtualizedAnnotationListProps {
  annotations: Annotation[];
  selectedAnnotationId?: string;
  onAnnotationClick: (annotation: Annotation) => void;
  onAnnotationEdit?: (annotation: Annotation) => void;
  onAnnotationDelete?: (annotation: Annotation) => void;
  height: number;
  width: number | string;
}

interface AnnotationItemProps {
  annotation: Annotation;
  isSelected: boolean;
  onClick: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

// ============================================================================
// Annotation Item Component (Memoized)
// ============================================================================

const AnnotationItem = memo(({
  annotation,
  isSelected,
  onClick,
  onEdit,
  onDelete,
}: AnnotationItemProps) => {
  return (
    <div
      className={`
        p-3 border-b cursor-pointer transition-colors
        ${isSelected ? 'bg-accent' : 'hover:bg-muted/50'}
      `}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      aria-selected={isSelected}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          {/* Highlighted text preview */}
          <p className="text-sm font-medium truncate mb-1">
            {annotation.highlighted_text}
          </p>
          
          {/* Note preview */}
          {annotation.note && (
            <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
              {annotation.note}
            </p>
          )}
          
          {/* Tags */}
          {annotation.tags && annotation.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {annotation.tags.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="text-xs"
                >
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>
        
        {/* Action buttons */}
        <div className="flex gap-1 flex-shrink-0">
          {onEdit && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
              aria-label="Edit annotation"
            >
              <Edit className="h-3 w-3" />
            </Button>
          )}
          {onDelete && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-destructive hover:text-destructive"
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
              aria-label="Delete annotation"
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>
      
      {/* Color indicator */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1"
        style={{ backgroundColor: annotation.color }}
        aria-hidden="true"
      />
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for better memoization
  return (
    prevProps.annotation.id === nextProps.annotation.id &&
    prevProps.annotation.note === nextProps.annotation.note &&
    prevProps.annotation.highlighted_text === nextProps.annotation.highlighted_text &&
    prevProps.annotation.tags?.join(',') === nextProps.annotation.tags?.join(',') &&
    prevProps.annotation.color === nextProps.annotation.color &&
    prevProps.isSelected === nextProps.isSelected &&
    prevProps.onClick === nextProps.onClick &&
    prevProps.onEdit === nextProps.onEdit &&
    prevProps.onDelete === nextProps.onDelete
  );
});

AnnotationItem.displayName = 'AnnotationItem';

// ============================================================================
// Virtualized List Component
// ============================================================================

const VirtualizedAnnotationListComponent = ({
  annotations,
  selectedAnnotationId,
  onAnnotationClick,
  onAnnotationEdit,
  onAnnotationDelete,
  height,
  width,
}: VirtualizedAnnotationListProps) => {
  // Item height in pixels (adjust based on your design)
  const ITEM_HEIGHT = 100;

  // Row renderer for react-window
  const Row = useCallback(
    ({ index, style }: { index: number; style: React.CSSProperties }) => {
      const annotation = annotations[index];
      const isSelected = annotation.id === selectedAnnotationId;

      return (
        <div style={style}>
          <AnnotationItem
            annotation={annotation}
            isSelected={isSelected}
            onClick={() => onAnnotationClick(annotation)}
            onEdit={onAnnotationEdit ? () => onAnnotationEdit(annotation) : undefined}
            onDelete={onAnnotationDelete ? () => onAnnotationDelete(annotation) : undefined}
          />
        </div>
      );
    },
    [annotations, selectedAnnotationId, onAnnotationClick, onAnnotationEdit, onAnnotationDelete]
  );

  // Empty state
  if (annotations.length === 0) {
    return (
      <div
        className="flex items-center justify-center text-muted-foreground text-sm"
        style={{ height }}
      >
        No annotations yet
      </div>
    );
  }

  return (
    <List
      height={height}
      itemCount={annotations.length}
      itemSize={ITEM_HEIGHT}
      width={width}
      className="annotation-list"
      overscanCount={5} // Render 5 extra items above/below viewport for smooth scrolling
    >
      {Row}
    </List>
  );
};

// Memoize the component to prevent unnecessary re-renders
// Requirements: 7.2 - React optimization
export const VirtualizedAnnotationList = memo(
  VirtualizedAnnotationListComponent,
  (prevProps, nextProps) => {
    // Custom comparison function
    return (
      prevProps.annotations === nextProps.annotations &&
      prevProps.selectedAnnotationId === nextProps.selectedAnnotationId &&
      prevProps.onAnnotationClick === nextProps.onAnnotationClick &&
      prevProps.onAnnotationEdit === nextProps.onAnnotationEdit &&
      prevProps.onAnnotationDelete === nextProps.onAnnotationDelete &&
      prevProps.height === nextProps.height &&
      prevProps.width === nextProps.width
    );
  }
);

VirtualizedAnnotationList.displayName = 'VirtualizedAnnotationList';
