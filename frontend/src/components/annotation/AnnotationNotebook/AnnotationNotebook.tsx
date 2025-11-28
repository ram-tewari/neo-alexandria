import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Download, Calendar, Tag as TagIcon, FileText } from 'lucide-react';
import { Annotation, AnnotationFilters, HIGHLIGHT_COLORS } from '@/types/annotation';
import { useAllAnnotations, useExportAnnotations } from '@/hooks/useAnnotations';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { formatDistanceToNow } from 'date-fns';

interface AnnotationNotebookProps {
  onAnnotationClick?: (annotation: Annotation) => void;
}

export const AnnotationNotebook: React.FC<AnnotationNotebookProps> = ({
  onAnnotationClick,
}) => {
  const [filters, setFilters] = useState<AnnotationFilters>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [groupBy, setGroupBy] = useState<'chronological' | 'resource' | 'tag'>('chronological');
  const [showFilters, setShowFilters] = useState(false);
  
  const { data: annotations = [], isLoading } = useAllAnnotations(filters);
  const exportAnnotations = useExportAnnotations();
  const prefersReducedMotion = useReducedMotion();

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setFilters(prev => ({ ...prev, searchQuery: query || undefined }));
  };

  const handleColorFilter = (color: string) => {
    setFilters(prev => {
      const colors = prev.colors || [];
      const newColors = colors.includes(color)
        ? colors.filter(c => c !== color)
        : [...colors, color];
      return { ...prev, colors: newColors.length > 0 ? newColors : undefined };
    });
  };

  const handleExport = (format: 'markdown' | 'json') => {
    exportAnnotations.mutate({ format, filters });
  };

  const groupAnnotations = () => {
    if (groupBy === 'chronological') {
      return [{ key: 'all', label: 'All Annotations', annotations }];
    }

    if (groupBy === 'resource') {
      const grouped = annotations.reduce((acc, annotation) => {
        const key = annotation.resourceId;
        if (!acc[key]) {
          acc[key] = [];
        }
        acc[key].push(annotation);
        return acc;
      }, {} as Record<string, Annotation[]>);

      return Object.entries(grouped).map(([key, anns]) => ({
        key,
        label: `Resource ${key.slice(0, 8)}`,
        annotations: anns,
      }));
    }

    if (groupBy === 'tag') {
      const grouped = annotations.reduce((acc, annotation) => {
        annotation.tags.forEach(tag => {
          if (!acc[tag]) {
            acc[tag] = [];
          }
          acc[tag].push(annotation);
        });
        if (annotation.tags.length === 0) {
          if (!acc['untagged']) {
            acc['untagged'] = [];
          }
          acc['untagged'].push(annotation);
        }
        return acc;
      }, {} as Record<string, Annotation[]>);

      return Object.entries(grouped).map(([key, anns]) => ({
        key,
        label: key === 'untagged' ? 'Untagged' : key,
        annotations: anns,
      }));
    }

    return [];
  };

  const groupedAnnotations = groupAnnotations();

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Annotation Notebook
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {annotations.length} annotations
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleExport('markdown')}
              disabled={exportAnnotations.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="space-y-3">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Search annotations..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                showFilters
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              <Filter className="w-4 h-4" />
            </button>
          </div>

          {showFilters && (
            <motion.div
              initial={prefersReducedMotion ? {} : { opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-3"
            >
              {/* Color Filters */}
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                  Colors
                </label>
                <div className="flex flex-wrap gap-2">
                  {HIGHLIGHT_COLORS.map((color) => (
                    <button
                      key={color.value}
                      onClick={() => handleColorFilter(color.value)}
                      className={`w-8 h-8 rounded border-2 transition-all ${
                        filters.colors?.includes(color.value)
                          ? 'border-primary-600 ring-2 ring-primary-200 dark:ring-primary-800'
                          : 'border-gray-300 dark:border-gray-600'
                      }`}
                      style={{ backgroundColor: color.value }}
                      aria-label={`Filter by ${color.name}`}
                    />
                  ))}
                </div>
              </div>

              {/* Group By */}
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                  Group By
                </label>
                <div className="flex gap-2">
                  {(['chronological', 'resource', 'tag'] as const).map((option) => (
                    <button
                      key={option}
                      onClick={() => setGroupBy(option)}
                      className={`px-3 py-1 text-sm rounded transition-colors ${
                        groupBy === option
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                      }`}
                    >
                      {option === 'chronological' && <Calendar className="w-4 h-4 inline mr-1" />}
                      {option === 'resource' && <FileText className="w-4 h-4 inline mr-1" />}
                      {option === 'tag' && <TagIcon className="w-4 h-4 inline mr-1" />}
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Annotations List */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            {groupedAnnotations.map((group) => (
              <div key={group.key}>
                {groupBy !== 'chronological' && (
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    {group.label}
                  </h3>
                )}

                <div className="space-y-3">
                  {group.annotations.map((annotation, index) => (
                    <motion.div
                      key={annotation.id}
                      initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => onAnnotationClick?.(annotation)}
                      className="bg-white dark:bg-gray-800 rounded-lg border-l-4 p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                      style={{ borderLeftColor: annotation.color }}
                    >
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
                      </div>

                      {/* Selected Text */}
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                        "{annotation.text}"
                      </p>

                      {/* Note */}
                      {annotation.note && (
                        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                          <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                            {annotation.note}
                          </p>
                        </div>
                      )}

                      {/* Source Preview */}
                      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        Resource: {annotation.resourceId.slice(0, 8)}...
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            ))}

            {annotations.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
                  <FileText className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  No annotations yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Start highlighting and taking notes on your resources.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
