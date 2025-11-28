import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Highlighter, MessageSquare, Tag, X } from 'lucide-react';
import { TextSelection, HIGHLIGHT_COLORS } from '@/types/annotation';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface AnnotationToolbarProps {
  selection: TextSelection;
  onHighlight: (color: string) => void;
  onNote: () => void;
  onTag: (tags: string[]) => void;
  onClose: () => void;
  position: { x: number; y: number };
}

export const AnnotationToolbar: React.FC<AnnotationToolbarProps> = ({
  selection,
  onHighlight,
  onNote,
  onTag,
  onClose,
  position,
}) => {
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [showTagInput, setShowTagInput] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const toolbarRef = useRef<HTMLDivElement>(null);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (toolbarRef.current && !toolbarRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const handleColorSelect = (color: string) => {
    onHighlight(color);
    setShowColorPicker(false);
  };

  const handleAddTag = () => {
    if (tagInput.trim()) {
      const newTags = [...tags, tagInput.trim()];
      setTags(newTags);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter(t => t !== tag));
  };

  const handleSubmitTags = () => {
    if (tags.length > 0) {
      onTag(tags);
      setShowTagInput(false);
      setTags([]);
    }
  };

  return (
    <motion.div
      ref={toolbarRef}
      initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.95, y: -10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: -10 }}
      transition={{ duration: 0.15 }}
      style={{
        position: 'fixed',
        left: position.x,
        top: position.y - 60,
        zIndex: 1000,
      }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-2"
    >
      <div className="flex items-center gap-1">
        {/* Highlight Button */}
        <div className="relative">
          <button
            onClick={() => setShowColorPicker(!showColorPicker)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            aria-label="Highlight"
            title="Highlight"
          >
            <Highlighter className="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <AnimatePresence>
            {showColorPicker && (
              <motion.div
                initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-2"
              >
                <div className="grid grid-cols-4 gap-1">
                  {HIGHLIGHT_COLORS.map((color) => (
                    <button
                      key={color.value}
                      onClick={() => handleColorSelect(color.value)}
                      className="w-8 h-8 rounded border-2 border-gray-300 dark:border-gray-600 hover:border-gray-500 dark:hover:border-gray-400 transition-colors"
                      style={{ backgroundColor: color.value }}
                      aria-label={`Highlight ${color.name}`}
                      title={color.name}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Note Button */}
        <button
          onClick={onNote}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          aria-label="Add note"
          title="Add note"
        >
          <MessageSquare className="w-4 h-4 text-gray-700 dark:text-gray-300" />
        </button>

        {/* Tag Button */}
        <div className="relative">
          <button
            onClick={() => setShowTagInput(!showTagInput)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            aria-label="Add tags"
            title="Add tags"
          >
            <Tag className="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <AnimatePresence>
            {showTagInput && (
              <motion.div
                initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-3 w-64"
              >
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                      placeholder="Add tag..."
                      className="flex-1 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      autoFocus
                    />
                    <button
                      onClick={handleAddTag}
                      className="px-3 py-1 text-sm bg-primary-600 hover:bg-primary-700 text-white rounded transition-colors"
                    >
                      Add
                    </button>
                  </div>

                  {tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 rounded"
                        >
                          {tag}
                          <button
                            onClick={() => handleRemoveTag(tag)}
                            className="hover:text-primary-900 dark:hover:text-primary-100"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}

                  {tags.length > 0 && (
                    <button
                      onClick={handleSubmitTags}
                      className="w-full px-3 py-1 text-sm bg-primary-600 hover:bg-primary-700 text-white rounded transition-colors"
                    >
                      Apply Tags
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Close Button */}
        <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          aria-label="Close"
        >
          <X className="w-4 h-4 text-gray-700 dark:text-gray-300" />
        </button>
      </div>

      {/* Selection Preview */}
      <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
          "{selection.text}"
        </p>
      </div>
    </motion.div>
  );
};
