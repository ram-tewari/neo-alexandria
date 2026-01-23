/**
 * ReferenceDetailsPanel Component
 * 
 * Modal dialog displaying full citation details for a reference.
 * Provides a "View in Library" button for references with PDF links.
 * 
 * Features:
 * - Full citation display
 * - Author list
 * - URL and external links
 * - Library integration (Phase 3)
 * - Smooth modal animations
 * 
 * Requirements: 6.4, 6.5
 */

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ExternalLink, BookOpen, Copy, Check } from 'lucide-react';
import type { Reference } from './types';
import { useState } from 'react';

// ============================================================================
// Types
// ============================================================================

export interface ReferenceDetailsPanelProps {
  reference: Reference | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onViewInLibrary?: (pdfId: string) => void;
}

// ============================================================================
// Component
// ============================================================================

export function ReferenceDetailsPanel({
  reference,
  open,
  onOpenChange,
  onViewInLibrary,
}: ReferenceDetailsPanelProps) {
  const [copied, setCopied] = useState(false);

  // Handle copy citation
  const handleCopyCitation = () => {
    if (!reference?.citation) return;
    
    navigator.clipboard.writeText(reference.citation);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Handle view in library
  const handleViewInLibrary = () => {
    if (!reference?.pdf_id || !onViewInLibrary) return;
    onViewInLibrary(reference.pdf_id);
  };

  // Handle open external link
  const handleOpenExternal = () => {
    if (!reference?.url) return;
    window.open(reference.url, '_blank', 'noopener,noreferrer');
  };

  if (!reference) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">
            {reference.title}
          </DialogTitle>
          <DialogDescription>
            {reference.reference_type.charAt(0).toUpperCase() + reference.reference_type.slice(1)} Reference
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Authors */}
          {reference.authors && reference.authors.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-2">Authors</h3>
              <p className="text-sm">{reference.authors.join(', ')}</p>
            </div>
          )}

          {/* Citation */}
          {reference.citation && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-muted-foreground">Citation</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopyCitation}
                  className="h-8 px-2"
                >
                  {copied ? (
                    <>
                      <Check className="h-4 w-4 mr-1" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4 mr-1" />
                      Copy
                    </>
                  )}
                </Button>
              </div>
              <p className="text-sm bg-muted p-3 rounded-md font-mono">
                {reference.citation}
              </p>
            </div>
          )}

          {/* URL */}
          {reference.url && (
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-2">URL</h3>
              <a
                href={reference.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline break-all"
              >
                {reference.url}
              </a>
            </div>
          )}

          {/* Line Number */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Referenced at</h3>
            <p className="text-sm">Line {reference.line_number}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-4 border-t">
          {reference.pdf_id && onViewInLibrary && (
            <Button
              onClick={handleViewInLibrary}
              className="flex-1"
            >
              <BookOpen className="h-4 w-4 mr-2" />
              View in Library
            </Button>
          )}
          
          {reference.url && (
            <Button
              onClick={handleOpenExternal}
              variant={reference.pdf_id ? 'outline' : 'default'}
              className="flex-1"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Open External Link
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
