/**
 * ChunkMetadataPanel Component
 * 
 * Displays metadata for the selected semantic chunk including:
 * - Function/class name
 * - Line range
 * - Language
 * - Chunk size
 * - Related chunks (via graph)
 * 
 * Features:
 * - Metadata display
 * - Navigation to related chunks
 * - Expand/collapse animation
 * 
 * Requirements: 2.4
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronUp, Code2, FileCode, ArrowRight } from 'lucide-react';
import type { SemanticChunk } from './types';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// Types
// ============================================================================

export interface ChunkMetadataPanelProps {
  chunk: SemanticChunk | null;
  onNavigateToChunk?: (chunkId: string) => void;
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

export function ChunkMetadataPanel({
  chunk,
  onNavigateToChunk,
  className = '',
}: ChunkMetadataPanelProps) {
  const [expanded, setExpanded] = useState(true);

  if (!chunk) {
    return (
      <Card className={`${className} opacity-50`} role="region" aria-label="Chunk metadata">
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground">
            No Chunk Selected
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Click on a chunk boundary to view its metadata
          </p>
        </CardContent>
      </Card>
    );
  }

  const metadata = chunk.chunk_metadata;
  const chunkName = metadata.function_name || metadata.class_name || 'Unknown';
  const lineRange = `${metadata.start_line}-${metadata.end_line}`;
  const lineCount = metadata.end_line - metadata.start_line + 1;

  return (
    <Card className={className} role="region" aria-label="Chunk metadata">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Code2 className="h-4 w-4" aria-hidden="true" />
            Chunk Metadata
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
            className="h-6 w-6 p-0"
            aria-label={expanded ? 'Collapse chunk metadata' : 'Expand chunk metadata'}
            aria-expanded={expanded}
          >
            {expanded ? (
              <ChevronUp className="h-4 w-4" aria-hidden="true" />
            ) : (
              <ChevronDown className="h-4 w-4" aria-hidden="true" />
            )}
          </Button>
        </div>
      </CardHeader>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{
              height: { duration: 0.3, ease: 'easeInOut' },
              opacity: { duration: 0.2, ease: 'easeInOut' },
            }}
            style={{ overflow: 'hidden' }}
            role="region"
            aria-label="Chunk details"
          >
            <CardContent className="space-y-4">
              {/* Chunk Name */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-1">
                  {metadata.function_name ? 'Function' : metadata.class_name ? 'Class' : 'Name'}
                </h4>
                <p className="text-sm font-mono" aria-label={`Chunk name: ${chunkName}`}>
                  {chunkName}
                </p>
              </div>

              {/* Line Range */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-1">Line Range</h4>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="font-mono" aria-label={`Lines ${lineRange}`}>
                    {lineRange}
                  </Badge>
                  <span className="text-xs text-muted-foreground" aria-label={`${lineCount} lines`}>
                    ({lineCount} {lineCount === 1 ? 'line' : 'lines'})
                  </span>
                </div>
              </div>

              {/* Language */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-1">Language</h4>
                <Badge variant="secondary" className="flex items-center gap-1 w-fit" aria-label={`Language: ${metadata.language}`}>
                  <FileCode className="h-3 w-3" aria-hidden="true" />
                  {metadata.language}
                </Badge>
              </div>

              {/* Chunk Index */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-1">Chunk Index</h4>
                <p className="text-sm" aria-label={`Chunk index: ${chunk.chunk_index}`}>
                  {chunk.chunk_index}
                </p>
              </div>

              {/* Content Preview */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-1">Content Preview</h4>
                <div 
                  className="bg-muted p-2 rounded-md max-h-32 overflow-y-auto"
                  role="region"
                  aria-label="Code preview"
                >
                  <pre className="text-xs font-mono whitespace-pre-wrap break-words">
                    {chunk.content.slice(0, 200)}
                    {chunk.content.length > 200 && '...'}
                  </pre>
                </div>
              </div>

              {/* Related Chunks (Placeholder for Phase 3) */}
              {onNavigateToChunk && (
                <div>
                  <h4 className="text-xs font-medium text-muted-foreground mb-2">Related Chunks</h4>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground italic">
                      Graph-based chunk relationships will be available in Phase 3
                    </p>
                    {/* Placeholder for future related chunks */}
                    {/* <Button
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start text-xs h-8"
                      onClick={() => onNavigateToChunk('related-chunk-id')}
                      aria-label="Navigate to related function"
                    >
                      <ArrowRight className="h-3 w-3 mr-2" aria-hidden="true" />
                      Related Function Name
                    </Button> */}
                  </div>
                </div>
              )}
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}
