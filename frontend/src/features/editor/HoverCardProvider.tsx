/**
 * HoverCardProvider Component
 * 
 * Provides contextual hover cards with symbol information from the backend.
 * Implements debounced hover detection (300ms) and fetches symbol information
 * from the backend API using static analysis.
 * 
 * Performance optimizations:
 * - Memoized with React.memo to prevent unnecessary re-renders
 * - Callbacks memoized with useCallback
 * - Debounced hover events (300ms) via useHoverInfo hook
 * - 30-minute cache for hover responses
 * 
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
 */

import { useEffect, useState, useCallback, useRef, memo } from 'react';
import * as monaco from 'monaco-editor';
import { HoverCard, HoverCardContent, HoverCardTrigger } from '@/components/ui/hover-card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { ExternalLink, AlertCircle, RefreshCw } from 'lucide-react';
import { useHoverInfo } from '@/lib/hooks/useEditorData';
import type { HoverParams } from '@/types/api';

interface HoverCardProviderProps {
  editor: monaco.editor.IStandaloneCodeEditor | null;
  resourceId: string;
  filePath: string;
  onSymbolClick?: (symbol: string, file: string, line: number, column: number) => void;
}

const HOVER_DEBOUNCE_MS = 300;

const HoverCardProviderComponent = ({
  editor,
  resourceId,
  filePath,
  onSymbolClick,
}: HoverCardProviderProps) => {
  const [hoverParams, setHoverParams] = useState<HoverParams | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  
  const currentPositionRef = useRef<{ line: number; column: number } | null>(null);

  // Use the debounced hover info hook
  const { data: hoverInfo, isLoading, error, refetch } = useHoverInfo(
    hoverParams,
    HOVER_DEBOUNCE_MS
  );

  /**
   * Handle hover event
   */
  const handleHover = useCallback(
    (e: monaco.editor.IEditorMouseEvent) => {
      // Only handle hover over text
      if (e.target.type !== monaco.editor.MouseTargetType.CONTENT_TEXT) {
        setIsOpen(false);
        setHoverParams(null);
        currentPositionRef.current = null;
        return;
      }

      const pos = e.target.position;
      if (!pos) {
        setIsOpen(false);
        setHoverParams(null);
        currentPositionRef.current = null;
        return;
      }

      // Don't refetch if same position
      if (
        currentPositionRef.current &&
        currentPositionRef.current.line === pos.lineNumber &&
        currentPositionRef.current.column === pos.column
      ) {
        return;
      }

      currentPositionRef.current = { line: pos.lineNumber, column: pos.column };

      // Set hover params (debouncing happens in the hook)
      setHoverParams({
        resource_id: resourceId,
        file_path: filePath,
        line: pos.lineNumber,
        column: pos.column,
      });
      setIsOpen(true);
    },
    [resourceId, filePath]
  );

  /**
   * Handle retry for failed hover fetch
   */
  const handleRetry = useCallback(() => {
    refetch();
  }, [refetch]);

  /**
   * Handle symbol click navigation
   */
  const handleSymbolClick = useCallback(
    (file: string, line: number, column: number) => {
      if (hoverInfo?.symbol_name) {
        setIsOpen(false);
        onSymbolClick?.(hoverInfo.symbol_name, file, line, column);
      }
    },
    [hoverInfo, onSymbolClick]
  );

  /**
   * Set up Monaco hover listener
   */
  useEffect(() => {
    if (!editor) return;

    const disposable = editor.onMouseMove(handleHover);

    return () => {
      disposable.dispose();
    };
  }, [editor, handleHover]);

  /**
   * Close hover card when editor loses focus
   */
  useEffect(() => {
    if (!editor) return;

    const disposable = editor.onDidBlurEditorText(() => {
      setIsOpen(false);
      setHoverParams(null);
      currentPositionRef.current = null;
    });

    return () => {
      disposable.dispose();
    };
  }, [editor]);

  // Don't render if no hover params or closed
  if (!isOpen || !hoverParams) {
    return null;
  }

  return (
    <HoverCard open={isOpen} onOpenChange={setIsOpen}>
      <HoverCardTrigger asChild>
        <div className="absolute" style={{ pointerEvents: 'none' }} />
      </HoverCardTrigger>
      <HoverCardContent 
        className="w-96 p-4"
        side="top"
        align="start"
        role="dialog"
        aria-label="Symbol information"
        aria-describedby="hover-card-content"
        style={{
          animation: 'fadeInScale 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
          transformOrigin: 'bottom left',
        }}
      >
        {isLoading ? (
          <div className="space-y-3" role="status" aria-label="Loading symbol information">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <span className="sr-only">Loading symbol information...</span>
          </div>
        ) : error ? (
          <div className="space-y-3" id="hover-card-content">
            <Alert variant="destructive" className="py-2" role="alert">
              <AlertCircle className="h-4 w-4" aria-hidden="true" />
              <AlertDescription className="text-xs">
                Unable to load hover information. {error.message}
              </AlertDescription>
            </Alert>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetry}
              className="w-full"
              aria-label="Retry loading symbol information"
            >
              <RefreshCw className="h-3 w-3 mr-2" aria-hidden="true" />
              Retry
            </Button>
          </div>
        ) : !hoverInfo || !hoverInfo.symbol_name ? (
          <div className="text-sm text-muted-foreground" id="hover-card-content">
            No symbol information available
          </div>
        ) : (
          <div className="space-y-3" id="hover-card-content">
            {/* Symbol name and type */}
            <div className="space-y-1">
              <div className="font-semibold text-sm text-foreground">
                {hoverInfo.symbol_name}
              </div>
              {hoverInfo.symbol_type && (
                <div className="text-xs text-muted-foreground">
                  {hoverInfo.symbol_type}
                </div>
              )}
            </div>

            {/* Documentation */}
            {hoverInfo.documentation && (
              <div className="text-sm text-muted-foreground">
                {hoverInfo.documentation}
              </div>
            )}

            {/* Definition location */}
            {hoverInfo.definition_location && (
              <button
                onClick={() =>
                  handleSymbolClick(
                    hoverInfo.definition_location!.file_path,
                    hoverInfo.definition_location!.line,
                    hoverInfo.definition_location!.column
                  )
                }
                className="flex items-center gap-2 w-full text-left text-xs p-2 rounded hover:bg-accent transition-colors focus-visible:outline-2 focus-visible:outline-primary"
                aria-label={`Go to definition at line ${hoverInfo.definition_location.line}`}
              >
                <ExternalLink className="h-3 w-3 text-muted-foreground" aria-hidden="true" />
                <div className="flex-1">
                  <div className="font-medium">Go to definition</div>
                  <div className="text-muted-foreground">
                    Line {hoverInfo.definition_location.line}, Column {hoverInfo.definition_location.column}
                  </div>
                </div>
              </button>
            )}

            {/* Related chunks */}
            {hoverInfo.related_chunks.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-medium text-muted-foreground">
                  Related Code
                </div>
                <div className="space-y-1" role="list" aria-label="Related code chunks">
                  {hoverInfo.related_chunks.map((chunk, index) => (
                    <div
                      key={index}
                      className="text-xs p-2 rounded bg-muted"
                      role="listitem"
                    >
                      <div className="font-medium mb-1">
                        Similarity: {(chunk.similarity_score * 100).toFixed(0)}%
                      </div>
                      <div className="text-muted-foreground line-clamp-2">
                        {chunk.preview}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Context lines */}
            {hoverInfo.context_lines.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-medium text-muted-foreground">
                  Context
                </div>
                <pre className="text-xs p-2 rounded bg-muted overflow-x-auto">
                  <code>{hoverInfo.context_lines.join('\n')}</code>
                </pre>
              </div>
            )}
          </div>
        )}
      </HoverCardContent>
    </HoverCard>
  );
}

// Memoize the component to prevent unnecessary re-renders
export const HoverCardProvider = memo(HoverCardProviderComponent, (prevProps, nextProps) => {
  // Custom comparison function for better memoization
  return (
    prevProps.editor === nextProps.editor &&
    prevProps.resourceId === nextProps.resourceId &&
    prevProps.filePath === nextProps.filePath &&
    prevProps.onSymbolClick === nextProps.onSymbolClick
  );
});

HoverCardProvider.displayName = 'HoverCardProvider';
