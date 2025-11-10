// Neo Alexandria 2.0 Frontend - Content Viewer Component
// Displays resource content with annotation support

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import type { Resource } from '@/types/api';
import {
  Highlighter,
  MessageSquare,
  Trash2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface ContentViewerProps {
  resource: Resource;
}

interface Annotation {
  id: string;
  text: string;
  note: string;
  color: string;
  createdAt: string;
  startOffset: number;
  endOffset: number;
}

// Annotation colors
const ANNOTATION_COLORS = [
  { value: 'yellow', label: 'Yellow', class: 'bg-yellow-300/30 border-yellow-400' },
  { value: 'green', label: 'Green', class: 'bg-green-300/30 border-green-400' },
  { value: 'blue', label: 'Blue', class: 'bg-blue-300/30 border-blue-400' },
  { value: 'pink', label: 'Pink', class: 'bg-pink-300/30 border-pink-400' },
];

export const ContentViewer: React.FC<ContentViewerProps> = ({ resource }) => {
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [selectedText, setSelectedText] = useState<string>('');
  const [showAnnotationForm, setShowAnnotationForm] = useState(false);
  const [annotationNote, setAnnotationNote] = useState('');
  const [annotationColor, setAnnotationColor] = useState('yellow');
  const [isAnnotationMode, setIsAnnotationMode] = useState(false);
  const [expandedSubjects, setExpandedSubjects] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  // Load annotations from localStorage on mount
  useEffect(() => {
    const storageKey = `annotations_${resource.id}`;
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      try {
        setAnnotations(JSON.parse(stored));
      } catch (error) {
        console.error('Failed to load annotations:', error);
      }
    }
  }, [resource.id]);

  // Save annotations to localStorage whenever they change
  useEffect(() => {
    const storageKey = `annotations_${resource.id}`;
    localStorage.setItem(storageKey, JSON.stringify(annotations));
  }, [annotations, resource.id]);

  // Handle text selection
  const handleTextSelection = () => {
    if (!isAnnotationMode) return;

    const selection = window.getSelection();
    if (selection && selection.toString().trim().length > 0) {
      setSelectedText(selection.toString().trim());
      setShowAnnotationForm(true);
    }
  };

  // Create annotation
  const handleCreateAnnotation = () => {
    if (!selectedText) return;

    const newAnnotation: Annotation = {
      id: `annotation_${Date.now()}`,
      text: selectedText,
      note: annotationNote,
      color: annotationColor,
      createdAt: new Date().toISOString(),
      startOffset: 0, // Simplified - in production would track actual position
      endOffset: 0,
    };

    setAnnotations([...annotations, newAnnotation]);
    setSelectedText('');
    setAnnotationNote('');
    setShowAnnotationForm(false);
    
    // Clear selection
    window.getSelection()?.removeAllRanges();
  };

  // Delete annotation
  const handleDeleteAnnotation = (id: string) => {
    setAnnotations(annotations.filter(a => a.id !== id));
  };

  // Cancel annotation
  const handleCancelAnnotation = () => {
    setSelectedText('');
    setAnnotationNote('');
    setShowAnnotationForm(false);
    window.getSelection()?.removeAllRanges();
  };

  // Get color class for annotation
  const getColorClass = (color: string): string => {
    return ANNOTATION_COLORS.find(c => c.value === color)?.class || ANNOTATION_COLORS[0].class;
  };

  return (
    <Card className="bg-charcoal-grey-800 border-charcoal-grey-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-charcoal-grey-50">Content</h2>
          
          {/* Annotation Toolbar */}
          <div className="flex items-center gap-2">
            <Button
              variant={isAnnotationMode ? 'primary' : 'outline'}
              size="sm"
              icon={<Highlighter />}
              onClick={() => setIsAnnotationMode(!isAnnotationMode)}
            >
              {isAnnotationMode ? 'Annotating' : 'Annotate'}
            </Button>
            
            {annotations.length > 0 && (
              <Badge variant="info" size="md">
                {annotations.length} {annotations.length === 1 ? 'note' : 'notes'}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Annotation Mode Notice */}
        {isAnnotationMode && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-accent-blue-500/10 border border-accent-blue-500/30 rounded-lg p-3"
          >
            <div className="flex items-start gap-2">
              <MessageSquare className="w-4 h-4 text-accent-blue-400 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-accent-blue-300">
                Select text below to create an annotation. Click "Annotate" again to exit annotation mode.
              </div>
            </div>
          </motion.div>
        )}

        {/* Annotation Form */}
        {showAnnotationForm && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-charcoal-grey-700 border border-charcoal-grey-600 rounded-lg p-4 space-y-3"
          >
            <div>
              <div className="text-sm font-medium text-charcoal-grey-50 mb-2">Selected Text</div>
              <div className="text-sm text-charcoal-grey-300 bg-charcoal-grey-800 rounded p-2 italic">
                "{selectedText}"
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-charcoal-grey-50 mb-2 block">
                Add Note (optional)
              </label>
              <textarea
                value={annotationNote}
                onChange={(e) => setAnnotationNote(e.target.value)}
                placeholder="Add your thoughts or comments..."
                className="w-full px-3 py-2 bg-charcoal-grey-800 border border-charcoal-grey-600 rounded-lg text-charcoal-grey-50 placeholder-charcoal-grey-400 focus:outline-none focus:ring-2 focus:ring-accent-blue-500 resize-none"
                rows={3}
              />
            </div>

            <div>
              <label className="text-sm font-medium text-charcoal-grey-50 mb-2 block">
                Highlight Color
              </label>
              <div className="flex gap-2">
                {ANNOTATION_COLORS.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => setAnnotationColor(color.value)}
                    className={`w-10 h-10 rounded-lg border-2 transition-all ${
                      annotationColor === color.value
                        ? 'border-white scale-110'
                        : 'border-transparent hover:scale-105'
                    } ${color.class}`}
                    title={color.label}
                  />
                ))}
              </div>
            </div>

            <div className="flex gap-2 justify-end pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancelAnnotation}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleCreateAnnotation}
              >
                Save Annotation
              </Button>
            </div>
          </motion.div>
        )}

        {/* Main Content */}
        <div
          ref={contentRef}
          onMouseUp={handleTextSelection}
          className={`prose prose-invert max-w-none ${
            isAnnotationMode ? 'select-text cursor-text' : ''
          }`}
        >
          {/* Description */}
          {resource.description && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-charcoal-grey-50 mb-3">Description</h3>
              <p className="text-charcoal-grey-300 leading-relaxed whitespace-pre-wrap">
                {resource.description}
              </p>
            </div>
          )}

          {/* Subjects */}
          {resource.subject && resource.subject.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-charcoal-grey-50">Subjects</h3>
                {resource.subject.length > 5 && (
                  <button
                    onClick={() => setExpandedSubjects(!expandedSubjects)}
                    className="text-sm text-accent-blue-400 hover:text-accent-blue-300 flex items-center gap-1"
                  >
                    {expandedSubjects ? (
                      <>
                        Show Less <ChevronUp className="w-4 h-4" />
                      </>
                    ) : (
                      <>
                        Show All ({resource.subject.length}) <ChevronDown className="w-4 h-4" />
                      </>
                    )}
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                {(expandedSubjects ? resource.subject : resource.subject.slice(0, 5)).map((subject, index) => (
                  <Badge key={index} variant="outline" size="md">
                    {subject}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Type and Format */}
          {(resource.type || resource.format) && (
            <div className="grid grid-cols-2 gap-4 mb-6">
              {resource.type && (
                <div>
                  <div className="text-sm text-charcoal-grey-400 mb-1">Type</div>
                  <div className="text-charcoal-grey-50">{resource.type}</div>
                </div>
              )}
              {resource.format && (
                <div>
                  <div className="text-sm text-charcoal-grey-400 mb-1">Format</div>
                  <div className="text-charcoal-grey-50">{resource.format}</div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Annotations List */}
        {annotations.length > 0 && (
          <div className="pt-6 border-t border-charcoal-grey-700">
            <h3 className="text-lg font-medium text-charcoal-grey-50 mb-4">Your Annotations</h3>
            <div className="space-y-3">
              {annotations.map((annotation) => (
                <motion.div
                  key={annotation.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`rounded-lg border-l-4 p-3 ${getColorClass(annotation.color)}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-charcoal-grey-50 font-medium mb-1 italic">
                        "{annotation.text}"
                      </div>
                      {annotation.note && (
                        <div className="text-sm text-charcoal-grey-300 mb-2">
                          {annotation.note}
                        </div>
                      )}
                      <div className="text-xs text-charcoal-grey-400">
                        {new Date(annotation.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<Trash2 />}
                      onClick={() => handleDeleteAnnotation(annotation.id)}
                      className="flex-shrink-0"
                    />
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
