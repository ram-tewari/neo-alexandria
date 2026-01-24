/**
 * AnnotationPanel Component
 * 
 * Sidebar panel for managing annotations with:
 * - List view of all annotations
 * - Create/edit/delete functionality
 * - Search and filtering
 * - Loading states and skeletons
 * - Smooth slide animations
 * 
 * Requirements: 4.1, 4.4, 4.6, 4.7, 8.3
 */

import { useState, useMemo } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Search, Plus, Edit2, Trash2, X } from 'lucide-react';
import { useAnnotationStore } from '@/stores/annotation';
import { AnnotationPanelSkeleton } from './components/LoadingSkeletons';
import { motion, AnimatePresence } from 'framer-motion';
import type { Annotation, AnnotationCreate, AnnotationUpdate } from './types';

// ============================================================================
// Types
// ============================================================================

export interface AnnotationPanelProps {
  resourceId: string;
  annotations: Annotation[];
  onAnnotationSelect?: (id: string) => void;
}

// ============================================================================
// Component
// ============================================================================

export function AnnotationPanel({
  resourceId,
  annotations,
  onAnnotationSelect,
}: AnnotationPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingAnnotation, setEditingAnnotation] = useState<Annotation | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const {
    isLoading,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
  } = useAnnotationStore();

  // Filter annotations based on search query
  const filteredAnnotations = useMemo(() => {
    if (!searchQuery) return annotations;

    const query = searchQuery.toLowerCase();
    return annotations.filter(
      (annotation) =>
        annotation.highlighted_text.toLowerCase().includes(query) ||
        annotation.note?.toLowerCase().includes(query) ||
        annotation.tags?.some((tag) => tag.toLowerCase().includes(query))
    );
  }, [annotations, searchQuery]);

  // Handle annotation creation
  const handleCreate = async (data: AnnotationCreate) => {
    try {
      await createAnnotation(resourceId, data);
      setIsCreating(false);
    } catch (error) {
      console.error('Failed to create annotation:', error);
    }
  };

  // Handle annotation update
  const handleUpdate = async (id: string, data: AnnotationUpdate) => {
    try {
      await updateAnnotation(id, data);
      setEditingAnnotation(null);
    } catch (error) {
      console.error('Failed to update annotation:', error);
    }
  };

  // Handle annotation deletion
  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this annotation?')) return;

    try {
      await deleteAnnotation(id);
    } catch (error) {
      console.error('Failed to delete annotation:', error);
    }
  };

  return (
    <>
      {/* Trigger Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(true)}
        className="gap-2"
        aria-label="Open annotations panel"
      >
        <Plus className="h-4 w-4" aria-hidden="true" />
        Annotations ({annotations.length})
      </Button>

      {/* Panel Sheet */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetContent side="right" className="w-96 p-0">
          <SheetHeader className="p-4 border-b">
            <SheetTitle>Annotations</SheetTitle>
          </SheetHeader>

          {/* Loading State */}
          {isLoading && annotations.length === 0 ? (
            <AnnotationPanelSkeleton />
          ) : (
            <div className="flex flex-col h-full">
              {/* Search Bar */}
              <div className="p-4 border-b">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <Input
                    placeholder="Search annotations..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                    aria-label="Search annotations"
                  />
                </div>
              </div>

              {/* Annotation List */}
              <ScrollArea className="flex-1">
                <div className="p-4 space-y-3">
                  {filteredAnnotations.length === 0 ? (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className="text-center text-sm text-muted-foreground py-8"
                    >
                      {searchQuery ? 'No annotations found' : 'No annotations yet'}
                    </motion.div>
                  ) : (
                    <AnimatePresence mode="popLayout">
                      {filteredAnnotations.map((annotation, index) => (
                        <motion.div
                          key={annotation.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: 20 }}
                          transition={{
                            duration: 0.3,
                            delay: index * 0.05,
                            ease: [0.4, 0, 0.2, 1],
                          }}
                          layout
                        >
                          <AnnotationCard
                            annotation={annotation}
                            onSelect={() => onAnnotationSelect?.(annotation.id)}
                            onEdit={() => setEditingAnnotation(annotation)}
                            onDelete={() => handleDelete(annotation.id)}
                          />
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  )}
                </div>
              </ScrollArea>

              {/* Create Button */}
              <div className="p-4 border-t">
                <Button
                  onClick={() => setIsCreating(true)}
                  className="w-full gap-2"
                  aria-label="Create new annotation"
                >
                  <Plus className="h-4 w-4" aria-hidden="true" />
                  New Annotation
                </Button>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>

      {/* Create/Edit Dialog would go here */}
      {/* For now, this is a placeholder - full implementation in task 8.2 */}
    </>
  );
}

// ============================================================================
// Annotation Card Component
// ============================================================================

function AnnotationCard({
  annotation,
  onSelect,
  onEdit,
  onDelete,
}: {
  annotation: Annotation;
  onSelect: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <motion.div
      className="p-3 border rounded-lg hover:bg-accent/50 transition-colors cursor-pointer group"
      onClick={onSelect}
      role="button"
      tabIndex={0}
      aria-label={`Annotation: ${annotation.highlighted_text}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect();
        }
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
    >
      {/* Color indicator and text */}
      <div className="flex items-start gap-2 mb-2">
        <div
          className="h-3 w-3 rounded-full mt-1 flex-shrink-0"
          style={{ backgroundColor: annotation.color }}
          aria-hidden="true"
        />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium line-clamp-2">
            {annotation.highlighted_text}
          </p>
        </div>
      </div>

      {/* Note */}
      {annotation.note && (
        <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
          {annotation.note}
        </p>
      )}

      {/* Tags */}
      {annotation.tags && annotation.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {annotation.tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
      )}

      {/* Actions */}
      <motion.div
        className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity"
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
        transition={{ duration: 0.2 }}
      >
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onEdit();
          }}
          className="h-7 px-2"
          aria-label="Edit annotation"
        >
          <Edit2 className="h-3 w-3" aria-hidden="true" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="h-7 px-2 text-destructive hover:text-destructive"
          aria-label="Delete annotation"
        >
          <Trash2 className="h-3 w-3" aria-hidden="true" />
        </Button>
      </motion.div>
    </motion.div>
  );
}
