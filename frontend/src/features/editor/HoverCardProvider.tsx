/**
 * HoverCardProvider Component
 * 
 * Provides contextual hover cards with Node2Vec summaries and graph connections.
 * Implements debounced hover detection (300ms) and fetches symbol information
 * from the backend when available, falling back to Monaco IntelliSense.
 * 
 * Performance optimizations:
 * - Memoized with React.memo to prevent unnecessary re-renders
 * - Callbacks memoized with useCallback
 * - Debounced hover events (300ms)
 * 
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 7.4, 10.6
 */

import { useEffect, useState, useCallback, useRef, memo } from 'react';
import * as monaco from 'monaco-editor';
import { HoverCard, HoverCardContent, HoverCardTrigger } from '@/components/ui/hover-card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { ExternalLink, AlertCircle, RefreshCw } from 'lucide-react';
import { HoverCardData, Position } from './types';
import { editorApi } from '@/lib/api/editor';

interface HoverCardProviderProps {
  editor: monaco.editor.IStandaloneCodeEditor | null;
  resourceId: string;
  onSymbolClick?: (symbol: string, file: string) => void;
}

const HOVER_DEBOUNCE_MS = 300;

const HoverCardProviderComponent = ({
  editor,
  resourceId,
  onSymbolClick,
}: HoverCardProviderProps) => {
  const [hoverData, setHoverData] = useState<HoverCardData | null>(null);
  const [position, setPosition] = useState<Position | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const currentSymbolRef = useRef<string | null>(null);

  /**
   * Detect symbol under cursor using Monaco's language service
   */
  const detectSymbol = useCallback(
    async (pos: monaco.Position): Promise<string | null> => {
      if (!editor) return null;

      const model = editor.getModel();
      if (!model) return null;

      // Get word at position
      const wordAtPosition = model.getWordAtPosition(pos);
      if (!wordAtPosition) return null;

      return wordAtPosition.word;
    },
    [editor]
  );

  /**
   * Fetch Node2Vec summary from backend
   */
  const fetchNode2VecSummary = useCallback(
    async (symbol: string): Promise<HoverCardData> => {
      try {
        const response = await editorApi.getNode2VecSummary(resourceId, symbol);
        return {
          symbol,
          summary: response.summary,
          connections: response.connections || [],
          loading: false,
        };
      } catch (error) {
        console.error('Failed to fetch Node2Vec summary:', error);
        throw error;
      }
    },
    [resourceId]
  );

  /**
   * Get fallback information from Monaco IntelliSense
   */
  const getFallbackInfo = useCallback(
    async (symbol: string, pos: monaco.Position): Promise<HoverCardData> => {
      if (!editor) {
        return {
          symbol,
          summary: `Symbol: ${symbol}`,
          connections: [],
          loading: false,
        };
      }

      const model = editor.getModel();
      if (!model) {
        return {
          symbol,
          summary: `Symbol: ${symbol}`,
          connections: [],
          loading: false,
        };
      }

      try {
        // Get hover information from Monaco
        const hovers = await monaco.languages.getHoverProvider(model.getLanguageId())
          ? await monaco.languages.getHover(model, pos)
          : null;

        if (hovers && hovers.contents.length > 0) {
          const content = hovers.contents[0];
          const summary = typeof content === 'string' 
            ? content 
            : 'value' in content 
              ? content.value 
              : `Symbol: ${symbol}`;

          return {
            symbol,
            summary,
            connections: [],
            loading: false,
          };
        }
      } catch (error) {
        console.error('Failed to get Monaco hover info:', error);
      }

      return {
        symbol,
        summary: `Symbol: ${symbol}`,
        connections: [],
        loading: false,
      };
    },
    [editor]
  );

  /**
   * Handle hover event with debouncing
   */
  const handleHover = useCallback(
    async (e: monaco.editor.IEditorMouseEvent) => {
      // Clear existing timeout
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
        hoverTimeoutRef.current = null;
      }

      // Only handle hover over text
      if (e.target.type !== monaco.editor.MouseTargetType.CONTENT_TEXT) {
        setIsOpen(false);
        setHoverData(null);
        currentSymbolRef.current = null;
        return;
      }

      const pos = e.target.position;
      if (!pos) {
        setIsOpen(false);
        setHoverData(null);
        currentSymbolRef.current = null;
        return;
      }

      // Debounce hover detection
      hoverTimeoutRef.current = setTimeout(async () => {
        const symbol = await detectSymbol(pos);
        
        if (!symbol) {
          setIsOpen(false);
          setHoverData(null);
          currentSymbolRef.current = null;
          return;
        }

        // Don't refetch if same symbol
        if (symbol === currentSymbolRef.current) {
          return;
        }

        currentSymbolRef.current = symbol;
        setPosition({ line: pos.lineNumber, column: pos.column });

        // Show loading state
        setHoverData({
          symbol,
          summary: '',
          connections: [],
          loading: true,
        });
        setIsOpen(true);

        // Try to fetch Node2Vec summary
        try {
          const data = await fetchNode2VecSummary(symbol);
          setHoverData(data);
        } catch (error) {
          // Fall back to Monaco IntelliSense
          const fallbackData = await getFallbackInfo(symbol, pos);
          setHoverData({
            ...fallbackData,
            error: 'Unable to load Node2Vec summary. Showing basic information.',
          });
        }
      }, HOVER_DEBOUNCE_MS);
    },
    [detectSymbol, fetchNode2VecSummary, getFallbackInfo]
  );

  /**
   * Handle retry for failed Node2Vec fetch
   */
  const handleRetry = useCallback(async () => {
    if (!hoverData || !position || !editor) return;

    const model = editor.getModel();
    if (!model) return;

    const pos = new monaco.Position(position.line, position.column);

    setHoverData({
      ...hoverData,
      loading: true,
      error: undefined,
    });

    try {
      const data = await fetchNode2VecSummary(hoverData.symbol);
      setHoverData(data);
    } catch (error) {
      const fallbackData = await getFallbackInfo(hoverData.symbol, pos);
      setHoverData({
        ...fallbackData,
        error: 'Unable to load Node2Vec summary. Showing basic information.',
      });
    }
  }, [hoverData, position, editor, fetchNode2VecSummary, getFallbackInfo]);

  /**
   * Handle symbol click navigation
   */
  const handleSymbolClick = useCallback(
    (symbol: string, file: string) => {
      setIsOpen(false);
      onSymbolClick?.(symbol, file);
    },
    [onSymbolClick]
  );

  /**
   * Set up Monaco hover listener
   */
  useEffect(() => {
    if (!editor) return;

    const disposable = editor.onMouseMove(handleHover);

    return () => {
      disposable.dispose();
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, [editor, handleHover]);

  /**
   * Close hover card when editor loses focus
   */
  useEffect(() => {
    if (!editor) return;

    const disposable = editor.onDidBlurEditorText(() => {
      setIsOpen(false);
      setHoverData(null);
      currentSymbolRef.current = null;
    });

    return () => {
      disposable.dispose();
    };
  }, [editor]);

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
        {hoverData.loading ? (
          <div className="space-y-3" role="status" aria-label="Loading symbol information">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <span className="sr-only">Loading symbol information...</span>
          </div>
        ) : (
          <div className="space-y-3" id="hover-card-content">
            {/* Symbol name */}
            <div className="font-semibold text-sm text-foreground">
              {hoverData.symbol}
            </div>

            {/* Error message */}
            {hoverData.error && (
              <Alert variant="destructive" className="py-2" role="alert">
                <AlertCircle className="h-4 w-4" aria-hidden="true" />
                <AlertDescription className="text-xs">
                  {hoverData.error}
                </AlertDescription>
              </Alert>
            )}

            {/* Summary */}
            {hoverData.summary && (
              <div className="text-sm text-muted-foreground">
                {hoverData.summary}
              </div>
            )}

            {/* Connections */}
            {hoverData.connections.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-medium text-muted-foreground">
                  Related Symbols
                </div>
                <div className="space-y-1" role="list" aria-label="Related symbols">
                  {hoverData.connections.map((connection, index) => (
                    <button
                      key={index}
                      onClick={() => handleSymbolClick(connection.name, connection.file)}
                      className="flex items-center gap-2 w-full text-left text-xs p-2 rounded hover:bg-accent transition-colors focus-visible:outline-2 focus-visible:outline-primary"
                      aria-label={`Navigate to ${connection.name} in ${connection.file}`}
                      role="listitem"
                    >
                      <ExternalLink className="h-3 w-3 text-muted-foreground" aria-hidden="true" />
                      <div className="flex-1">
                        <div className="font-medium">{connection.name}</div>
                        <div className="text-muted-foreground">
                          {connection.relationship} • {connection.file}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Retry button for errors */}
            {hoverData.error && (
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
            )}
          </div>
        )}
      </HoverCardContent>
    </HoverCard>
  );
}

// Memoize the component to prevent unnecessary re-renders
// Requirements: 7.2 - React optimization
export const HoverCardProvider = memo(HoverCardProviderComponent, (prevProps, nextProps) => {
  // Custom comparison function for better memoization
  return (
    prevProps.editor === nextProps.editor &&
    prevProps.resourceId === nextProps.resourceId &&
    prevProps.onSymbolClick === nextProps.onSymbolClick
  );
});

HoverCardProvider.displayName = 'HoverCardProvider';
