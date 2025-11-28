import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Edit2, Trash2, ChevronDown, ChevronUp } from 'lucide-react';
import { Annotation } from '@/types/annotation';
import { useUpdateAnnotation, useDeleteAnnotation } from '@/hooks/useAnnotations';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { formatDistanceToNow } from 'date-fns';

interface AnnotationSidebarProps {
  annotations: Annotation[];
  scrollPosition: number;
  onAnnotationClick: (id: string) => void;
  onAnnotationEdit: (id: string, updates: Partial<Annotation>) => void;
  onAnnotationDelete: (id: string) => void;
}

export const AnnotationSidebar: React.FC<AnnotationSidebarProps> = ({
  annotations,
  scrollPosition,
  onAnnotationClick,
  onAnnotationEdit,
  onAnnotationDelete,
}) => {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editNote, setEditNote] = useState('');
  const updateAnnotation = useUpdateAnnotation();
  const deleteAnnotation = useDeleteAnnotation();
  const prefersReducedMotion = useReducedMotion();

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  };

  const startEdit = (annotation: Annotation) => {
    setEditingId(annotation.id);
    setEditNote(annotation.note || '');
  };

  const saveEdit = (annotation: Annotation) => {
    if (editNote.trim() !== annotation.note) {
      updateAnnotation.mutate({
        id: annotation.id,
        updates: { note: editNote.trim() },
      });
      onAnnotationEdit(annotation.id, { note: editNote.trim() });
    }
    setEditingId(null);
  };

  const handleDelete = (annotation: Annotation) => {
    if (window.confirm('Delete this annotation?')) {
      deleteAnnotation.mutate({
        id: annotation.id,
        resourceId: annotation.resourceId,
      });
      onAnnotationDelete(annotation.id);
    }
  };

  // Sort annotations by position
  const sortedAnnotations = [...annotations].sort((a, b) => a.position.start - b.position.start);

  return (
    <div className="h-full overflow-y-auto bg-gray-50 dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700">
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Annotations ({annotations.length})
        </h3>

        <div className="space-y-3">
          {sortedAnnotations.map((annotation, index) => {
            const isExpanded = expandedIds.has(annotation.id);
            const isEditing = editingId === annotation.id;

            return (
              <motion.div
                key={annotation.id}
                initial={prefersReducedMotion ? {} : { opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white dark:bg-gray-800 rounded-lg border-l-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                style={{ borderLeftColor: annotation.color }}
                onClick={() => onAnnotationClick(annotation.id)}
              >
                <div className="p-3">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                          {annotation.type === 'highlight' ? 'Highlight' : annotation.type === 'note' ? 'Note' : 'Tag'}
                        </span>
                        <span className="text-xs text-gray-400 dark:text-gray-500">
                          {formatDistanceToNow(new Date(annotation.createdAt), { addSuffix: true })}
                        </span>
                      </div>
                      
                      {/* Tags */}
                      {annotation.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2">
                          {annotation.tags.map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-0.5 text-xs bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          startEdit(annotation);
                        }}
                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                        aria-label="Edit annotation"
                      >
                        <Edit2 className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(annotation);
                        }}
                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                        aria-label="Delete annotation"
                      >
                        <Trash2 className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleExpand(annotation.id);
                        }}
                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                        aria-label={isExpanded ? 'Collapse' : 'Expand'}
                      >
                        {isExpanded ? (
                          <ChevronUp className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                        ) : (
                          <ChevronDown className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Selected Text */}
                  <p className={`text-sm text-gray-700 dark:text-gray-300 ${isExpanded ? '' : 'line-clamp-2'}`}>
                    "{annotation.text}"
                  </p>

                  {/* Note */}
                  {(annotation.note || isEditing) && (
                    <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                      {isEditing ? (
                        <div className="space-y-2">
                          <textarea
                            value={editNote}
                            onChange={(e) => setEditNote(e.target.value)}
                            onClick={(e) => e.stopPropagation()}
                            className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                            rows={3}
                            placeholder="Add a note..."
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                saveEdit(annotation);
                              }}
                              className="px-3 py-1 text-xs bg-primary-600 hover:bg-primary-700 text-white rounded transition-colors"
                            >
                              Save
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setEditingId(null);
                              }}
                              className="px-3 py-1 text-xs bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                          {annotation.note}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}

          {annotations.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">
                No annotations yet. Select text to create one.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
