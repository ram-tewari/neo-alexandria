import { useState, useCallback, useEffect } from 'react';
import { Highlighter, Palette, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { usePDFViewer } from '@/lib/hooks/usePDFViewer';
import { cn } from '@/lib/utils';

interface PDFHighlighterProps {
  resourceId: string;
  onSaveHighlight?: (highlight: Highlight) => Promise<void>;
  onDeleteHighlight?: (highlightId: string) => Promise<void>;
  className?: string;
}

export interface Highlight {
  id: string;
  resourceId: string;
  pageNumber: number;
  text: string;
  color: string;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  createdAt: string;
}

const HIGHLIGHT_COLORS = [
  { name: 'Yellow', value: '#fef08a', class: 'bg-yellow-200' },
  { name: 'Green', value: '#bbf7d0', class: 'bg-green-200' },
  { name: 'Blue', value: '#bfdbfe', class: 'bg-blue-200' },
  { name: 'Pink', value: '#fbcfe8', class: 'bg-pink-200' },
  { name: 'Purple', value: '#e9d5ff', class: 'bg-purple-200' },
];

export function PDFHighlighter({
  resourceId,
  onSaveHighlight,
  onDeleteHighlight,
  className = '',
}: PDFHighlighterProps) {
  const [selectedColor, setSelectedColor] = useState(HIGHLIGHT_COLORS[0].value);
  const [isHighlighting, setIsHighlighting] = useState(false);
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const [selectionPosition, setSelectionPosition] = useState<{
    x: number;
    y: number;
  } | null>(null);

  const { highlights, addHighlight, removeHighlight, currentPage } =
    usePDFViewer();

  // Handle text selection
  useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        setSelectedText(null);
        setSelectionPosition(null);
        return;
      }

      const text = selection.toString().trim();
      if (text.length === 0) {
        setSelectedText(null);
        setSelectionPosition(null);
        return;
      }

      // Get selection position
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      setSelectedText(text);
      setSelectionPosition({
        x: rect.left + rect.width / 2,
        y: rect.top - 10,
      });
    };

    document.addEventListener('selectionchange', handleSelectionChange);
    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
    };
  }, []);

  const handleHighlight = useCallback(async () => {
    if (!selectedText || !selectionPosition) return;

    const selection = window.getSelection();
    if (!selection) return;

    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    const highlight: Highlight = {
      id: `highlight-${Date.now()}`,
      resourceId,
      pageNumber: currentPage,
      text: selectedText,
      color: selectedColor,
      position: {
        x: rect.left,
        y: rect.top,
        width: rect.width,
        height: rect.height,
      },
      createdAt: new Date().toISOString(),
    };

    // Add to local state
    addHighlight(highlight);

    // Save to backend
    if (onSaveHighlight) {
      try {
        await onSaveHighlight(highlight);
      } catch (error) {
        console.error('Failed to save highlight:', error);
        // Optionally remove from local state on error
        removeHighlight(highlight.id);
      }
    }

    // Clear selection
    selection.removeAllRanges();
    setSelectedText(null);
    setSelectionPosition(null);
  }, [
    selectedText,
    selectionPosition,
    resourceId,
    currentPage,
    selectedColor,
    addHighlight,
    removeHighlight,
    onSaveHighlight,
  ]);

  const handleDeleteHighlight = useCallback(
    async (highlightId: string) => {
      // Remove from local state
      removeHighlight(highlightId);

      // Delete from backend
      if (onDeleteHighlight) {
        try {
          await onDeleteHighlight(highlightId);
        } catch (error) {
          console.error('Failed to delete highlight:', error);
          // Optionally restore highlight on error
        }
      }
    },
    [removeHighlight, onDeleteHighlight]
  );

  const currentPageHighlights = highlights.filter(
    (h) => h.pageNumber === currentPage
  );

  return (
    <div className={cn('pdf-highlighter', className)}>
      {/* Toolbar */}
      <div className="flex items-center gap-2 p-2 border-b bg-background">
        <Button
          variant={isHighlighting ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setIsHighlighting(!isHighlighting)}
          title="Toggle highlighting mode"
        >
          <Highlighter className="h-4 w-4 mr-2" />
          Highlight
        </Button>

        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="sm" title="Choose highlight color">
              <Palette className="h-4 w-4 mr-2" />
              <div
                className="w-4 h-4 rounded border"
                style={{ backgroundColor: selectedColor }}
              />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-2">
            <div className="flex gap-2">
              {HIGHLIGHT_COLORS.map((color) => (
                <button
                  key={color.value}
                  className={cn(
                    'w-8 h-8 rounded border-2 transition-all',
                    color.class,
                    selectedColor === color.value
                      ? 'border-primary scale-110'
                      : 'border-transparent hover:scale-105'
                  )}
                  onClick={() => setSelectedColor(color.value)}
                  title={color.name}
                />
              ))}
            </div>
          </PopoverContent>
        </Popover>

        {currentPageHighlights.length > 0 && (
          <span className="text-sm text-muted-foreground ml-auto">
            {currentPageHighlights.length} highlight
            {currentPageHighlights.length !== 1 ? 's' : ''} on this page
          </span>
        )}
      </div>

      {/* Selection popup */}
      {selectedText && selectionPosition && isHighlighting && (
        <div
          className="fixed z-50 bg-popover border rounded-md shadow-md p-2"
          style={{
            left: selectionPosition.x,
            top: selectionPosition.y,
            transform: 'translate(-50%, -100%)',
          }}
        >
          <Button size="sm" onClick={handleHighlight}>
            <Highlighter className="h-4 w-4 mr-2" />
            Highlight
          </Button>
        </div>
      )}

      {/* Highlight overlays */}
      <div className="highlight-overlays">
        {currentPageHighlights.map((highlight) => (
          <div
            key={highlight.id}
            className="absolute group cursor-pointer"
            style={{
              left: highlight.position.x,
              top: highlight.position.y,
              width: highlight.position.width,
              height: highlight.position.height,
              backgroundColor: highlight.color,
              opacity: 0.4,
              pointerEvents: 'auto',
            }}
            title={highlight.text}
          >
            <Button
              variant="destructive"
              size="icon"
              className="absolute -top-2 -right-2 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={() => handleDeleteHighlight(highlight.id)}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
