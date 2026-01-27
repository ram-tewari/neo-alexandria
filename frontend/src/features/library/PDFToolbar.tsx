import { useCallback, useEffect } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize,
  Download,
  Printer,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { usePDFViewer } from '@/lib/hooks/usePDFViewer';

interface PDFToolbarProps {
  resourceUrl?: string;
  resourceTitle?: string;
  className?: string;
}

const ZOOM_LEVELS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];

export function PDFToolbar({
  resourceUrl,
  resourceTitle = 'document',
  className = '',
}: PDFToolbarProps) {
  const {
    currentPage,
    totalPages,
    zoom,
    setCurrentPage,
    setZoom,
    nextPage,
    prevPage,
    canGoNext,
    canGoPrev,
  } = usePDFViewer();

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Prevent shortcuts when typing in input fields
      if (e.target instanceof HTMLInputElement) return;

      switch (e.key) {
        case 'ArrowLeft':
          if (canGoPrev) prevPage();
          break;
        case 'ArrowRight':
          if (canGoNext) nextPage();
          break;
        case '+':
        case '=':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            handleZoomIn();
          }
          break;
        case '-':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            handleZoomOut();
          }
          break;
        case '0':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            setZoom(1.0);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [canGoNext, canGoPrev, nextPage, prevPage, setZoom]);

  const handlePageChange = useCallback(
    (value: string) => {
      const page = parseInt(value, 10);
      if (!isNaN(page) && page >= 1 && page <= totalPages) {
        setCurrentPage(page);
      }
    },
    [totalPages, setCurrentPage]
  );

  const handleZoomChange = useCallback(
    (value: string) => {
      const zoomValue = parseFloat(value);
      if (!isNaN(zoomValue)) {
        setZoom(zoomValue);
      }
    },
    [setZoom]
  );

  const handleZoomIn = useCallback(() => {
    const currentIndex = ZOOM_LEVELS.findIndex((level) => level >= zoom);
    const nextIndex = Math.min(currentIndex + 1, ZOOM_LEVELS.length - 1);
    setZoom(ZOOM_LEVELS[nextIndex]);
  }, [zoom, setZoom]);

  const handleZoomOut = useCallback(() => {
    const currentIndex = ZOOM_LEVELS.findIndex((level) => level >= zoom);
    const prevIndex = Math.max(currentIndex - 1, 0);
    setZoom(ZOOM_LEVELS[prevIndex]);
  }, [zoom, setZoom]);

  const handleFitWidth = useCallback(() => {
    // Fit to width (approximate)
    setZoom(1.0);
  }, [setZoom]);

  const handleDownload = useCallback(() => {
    if (resourceUrl) {
      const link = document.createElement('a');
      link.href = resourceUrl;
      link.download = `${resourceTitle}.pdf`;
      link.click();
    }
  }, [resourceUrl, resourceTitle]);

  const handlePrint = useCallback(() => {
    if (resourceUrl) {
      window.open(resourceUrl, '_blank');
    }
  }, [resourceUrl]);

  return (
    <div
      className={`flex items-center gap-2 p-2 border-b bg-background ${className}`}
    >
      {/* Page Navigation */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={prevPage}
          disabled={!canGoPrev}
          title="Previous page (←)"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <div className="flex items-center gap-1">
          <Input
            type="number"
            value={currentPage}
            onChange={(e) => handlePageChange(e.target.value)}
            className="w-16 text-center"
            min={1}
            max={totalPages}
          />
          <span className="text-sm text-muted-foreground">
            / {totalPages}
          </span>
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={nextPage}
          disabled={!canGoNext}
          title="Next page (→)"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      <div className="h-6 w-px bg-border" />

      {/* Zoom Controls */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleZoomOut}
          disabled={zoom <= ZOOM_LEVELS[0]}
          title="Zoom out (Ctrl+-)"
        >
          <ZoomOut className="h-4 w-4" />
        </Button>

        <Select value={zoom.toString()} onValueChange={handleZoomChange}>
          <SelectTrigger className="w-24">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ZOOM_LEVELS.map((level) => (
              <SelectItem key={level} value={level.toString()}>
                {Math.round(level * 100)}%
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button
          variant="ghost"
          size="icon"
          onClick={handleZoomIn}
          disabled={zoom >= ZOOM_LEVELS[ZOOM_LEVELS.length - 1]}
          title="Zoom in (Ctrl++)"
        >
          <ZoomIn className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={handleFitWidth}
          title="Fit to width"
        >
          <Maximize className="h-4 w-4" />
        </Button>
      </div>

      <div className="h-6 w-px bg-border" />

      {/* Actions */}
      <div className="flex items-center gap-1 ml-auto">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleDownload}
          disabled={!resourceUrl}
          title="Download PDF"
        >
          <Download className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={handlePrint}
          disabled={!resourceUrl}
          title="Print PDF"
        >
          <Printer className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
